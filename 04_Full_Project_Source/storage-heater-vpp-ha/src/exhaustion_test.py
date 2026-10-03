"""
Stage B: afternoon-exhaustion test (METHODOLOGY.md 1.3, second bullet).

Two parts:
1. Boost detection: a distinct load signature in 16:00-20:00, different
   band and shorter/more irregular than the overnight block.
2. A simple constant-rate decay model: predicted_runout_hours = night_kwh
   / assumed_release_rate_kw, giving a predicted clock time at which
   stored heat should be exhausted. Cross-tabulated against actual boost
   occurrence/timing and against the day's temperature.

Population check (evidence_map.md, 2026-09-01) before building this:
across all 37 seasonal households, mean peak and mean total energy in the
16:00-20:00 window are both substantially higher on cold days than mild
days (peak +47%, total +55%) -- real, directionally-sensible signal, at
odds with an earlier small (n=3 household, 2 day) visual look that
suggested the opposite. Built on the population check, not the anecdote.

release_rate_kw is a genuine physical unknown (no direct way to observe
stored heat from electricity data -- passive convective release draws no
further power) and is treated as an explicitly flagged, untested config
constant, not a calibrated figure.
"""

from __future__ import annotations

import polars as pl
from dataclasses import dataclass


BOOST_WINDOW_START_HOUR = 16
BOOST_WINDOW_END_HOUR = 20
BOOST_MIN_KW = 0.5
BOOST_MAX_KW = 3.0          # STATUS: METHODOLOGY.md-style illustrative band, UNTESTED -- unlike the overnight band, not yet checked against real boost-heater examples (none available; see evidence_map.md UK-DALE/HES findings)
BOOST_MIN_CONSECUTIVE_HALFHOURS = 1
BOOST_MAX_CONSECUTIVE_HALFHOURS = 4   # "shorter, more irregular" than the overnight block's run length

RELEASE_RATE_KW = 1.0        # STATUS: recalibrated 2026-09-01 (evidence_map.md) -- the original 2.0kW guess predicted median exhaustion by noon, contradicted storage heaters' basic design intent, and made the cross-tab run backwards. 1.0kW derived from cold-night (top quartile heat_loss_proxy) median charge (24.1 kWh) lasting a full 24h cycle -- a design-intent calibration, not a guess, but still a single population-wide constant rather than a per-household fit; treat accordingly.
CHARGE_END_HOUR = 7.0        # night charge ends ~07:00 per the overnight window definition already used throughout Stage A/B


def detect_boost(nightly_and_daily: pl.DataFrame) -> pl.DataFrame:
    """
    Input: raw long-format rows for confirmed seasonal households (LCLid, DateTime, KWH_hh).
    Returns one row per household-day with boost_flag, boost_kwh, first_boost_hour.
    """
    boost_window = (
        (pl.col("DateTime").dt.hour() >= BOOST_WINDOW_START_HOUR)
        & (pl.col("DateTime").dt.hour() < BOOST_WINDOW_END_HOUR)
    )
    in_band = (pl.col("KWH_hh") * 2 >= BOOST_MIN_KW) & (pl.col("KWH_hh") * 2 <= BOOST_MAX_KW)

    per_slot = (
        nightly_and_daily.filter(boost_window)
        .with_columns(pl.col("DateTime").dt.date().alias("date"), in_band.alias("in_band"))
    )

    results = []
    for (lclid, date), grp in per_slot.group_by(["LCLid", "date"]):
        grp = grp.sort("DateTime")
        vals = grp["in_band"].to_list()
        kws = (grp["KWH_hh"] * 2).to_list()
        hours = grp["DateTime"].dt.hour().to_list()
        minutes = grp["DateTime"].dt.minute().to_list()

        run_start = None
        found = False
        boost_kwh = 0.0
        first_hour = None
        for i, v in enumerate(vals):
            if v and run_start is None:
                run_start = i
            if (not v or i == len(vals) - 1) and run_start is not None:
                run_end = i if not v else i + 1
                run_len = run_end - run_start
                if BOOST_MIN_CONSECUTIVE_HALFHOURS <= run_len <= BOOST_MAX_CONSECUTIVE_HALFHOURS:
                    found = True
                    boost_kwh += sum(kws[run_start:run_end]) * 0.5
                    if first_hour is None:
                        first_hour = hours[run_start] + minutes[run_start] / 60.0
                run_start = None
        results.append({"LCLid": lclid, "date": date, "boost_flag": found,
                         "boost_kwh": boost_kwh, "first_boost_hour": first_hour})

    return pl.DataFrame(results)


if __name__ == "__main__":
    reg = pl.read_parquet("data/intermediate/phase1_confirmed_households.parquet")
    nights = pl.read_parquet("data/intermediate/phase1_household_nights.parquet")
    temp = pl.read_parquet("data/intermediate/london_temp_2013.parquet")
    seasonal_ids = reg.filter(pl.col("heating_type") == "seasonal")["LCLid"].to_list()

    lf = pl.scan_parquet("data/intermediate/lcl_2013_long.parquet").filter(pl.col("LCLid").is_in(seasonal_ids))
    raw = lf.filter(
        (pl.col("DateTime").dt.hour() >= BOOST_WINDOW_START_HOUR) & (pl.col("DateTime").dt.hour() < BOOST_WINDOW_END_HOUR)
    ).collect(engine="streaming")

    boost = detect_boost(raw)
    boost.write_parquet("data/intermediate/phase1_boost_detection.parquet")
    print("household-days with boost window data:", boost.height)
    print("boost flagged:", boost["boost_flag"].sum(), f"({100*boost['boost_flag'].mean():.1f}%)")

    nights_pred = nights.filter(pl.col("heating_type") == "seasonal").with_columns(
        (CHARGE_END_HOUR + pl.col("night_kwh") / RELEASE_RATE_KW).alias("predicted_runout_hour")
    ).with_columns(
        pl.when(pl.col("predicted_runout_hour") > 31).then(31.0).otherwise(pl.col("predicted_runout_hour")).alias("predicted_runout_hour")
    )

    print()
    print("predicted run-out hour distribution (24h clock, capped at 31=next-day 7am):")
    print(nights_pred["predicted_runout_hour"].describe())

    joined = boost.join(
        nights_pred.select(["LCLid", "night_date", "predicted_runout_hour", "mean_temp_c", "heat_loss_proxy"]),
        left_on=["LCLid", "date"], right_on=["LCLid", "night_date"], how="inner",
    )
    joined.write_parquet("data/intermediate/phase1_exhaustion_test.parquet")

    print()
    print("=== Cross-tabulation ===")
    predicted_exhausted_by_1620 = joined.filter(pl.col("predicted_runout_hour") <= 20)
    predicted_not_exhausted = joined.filter(pl.col("predicted_runout_hour") > 20)
    print("Model predicts EXHAUSTED by 20:00 -- boost rate:",
          f"{100*predicted_exhausted_by_1620['boost_flag'].mean():.1f}%", f"(n={predicted_exhausted_by_1620.height})")
    print("Model predicts NOT exhausted by 20:00 -- boost rate:",
          f"{100*predicted_not_exhausted['boost_flag'].mean():.1f}%", f"(n={predicted_not_exhausted.height})")
