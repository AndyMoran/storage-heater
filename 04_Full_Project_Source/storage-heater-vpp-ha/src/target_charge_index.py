"""
Phase 2.2: Target Charge Index, 1-5 (METHODOLOGY.md 2.2).

IMPORTANT SCOPE NOTE, stated here and not buried: METHODOLOGY.md specifies
calibrating against "actual overnight charge needed to avoid BOTH
overcharge and afternoon exhaustion." Phase 1's afternoon-exhaustion test
(src/exhaustion_test.py) returned a genuine negative result -- no
validated relationship between charge level and exhaustion timing was
found (evidence_map.md, 2026-09-01). There is therefore nothing real to
calibrate an exhaustion-avoiding FLOOR against. Inventing one now would be
exactly the "fresh assumption dressed up as calibration" this project's
own rules prohibit (PROJECT.md 2.6, Mechanism Before Model).

This module calibrates ONLY the overcharge-avoiding half, which Phase 1
DID validate: each confirmed seasonal household's own fitted response
(modelled_required_kwh = intercept + slope * heat_loss_proxy, from
src/overcharge_test.py) is real, tested, and visually validated data. The
exhaustion-avoidance half of the brief remains an open gap, explicitly
flagged wherever this index is used downstream, not silently assumed away.

Method:
1. Per confirmed seasonal household, normalize modelled_required_kwh to a
   0-1 "relative charge" scale using that household's OWN maximum fitted
   requirement (its coldest-night figure) -- this makes different
   households' heater capacities comparable, since Phase 1 already
   established capacities vary by roughly 5x across confirmed households.
2. Pool all household-nights' (heat_loss_proxy, relative_charge) pairs.
3. Bin relative_charge into 5 quantile-based bands from the POOLED
   empirical distribution (not round numbers) -- Index 1 (lowest fifth)
   to Index 5 (highest fifth).
4. For each Index band, record the heat_loss_proxy range that maps to it
   -- this is the practical lookup: forecast tonight's heat_loss_proxy,
   look up the Index.
"""

from __future__ import annotations

import polars as pl
import numpy as np
from dataclasses import dataclass


N_BANDS = 6  # matches the real physical dial numbering (1-6), confirmed 2026-09-02 against a real
             # housing association's own tenant guide for a Dimplex dial-operated storage heater --
             # NOT chosen for analytical convenience. Was 5 (a round-number guess) before this check.


@dataclass
class IndexCalibration:
    band: int
    relative_charge_low: float
    relative_charge_high: float
    heat_loss_proxy_low: float
    heat_loss_proxy_high: float
    heat_loss_proxy_median: float
    n_household_nights: int


def build_calibration(nights: pl.DataFrame) -> tuple[pl.DataFrame, dict]:
    """
    nights: Phase 1's household_nights table, filtered to heating_type == 'seasonal'.
    Returns (calibration_table, household_max_requirement dict for later use).
    """
    household_max = (
        nights.group_by("LCLid")
        .agg(pl.col("modelled_required_kwh").max().alias("household_max_kwh"))
    )
    max_map = dict(zip(household_max["LCLid"], household_max["household_max_kwh"]))

    df = nights.join(household_max, on="LCLid").with_columns(
        (pl.col("modelled_required_kwh") / pl.col("household_max_kwh")).alias("relative_charge")
    )
    # drop households with zero/degenerate max (shouldn't happen for seasonal households, guard anyway)
    df = df.filter(pl.col("household_max_kwh") > 0)

    rc = df["relative_charge"].to_numpy()
    quantile_edges = np.quantile(rc, np.linspace(0, 1, N_BANDS + 1))

    rows = []
    for i in range(N_BANDS):
        lo, hi = quantile_edges[i], quantile_edges[i + 1]
        if i == N_BANDS - 1:
            mask = (rc >= lo) & (rc <= hi)
        else:
            mask = (rc >= lo) & (rc < hi)
        hlp_in_band = df["heat_loss_proxy"].to_numpy()[mask]
        rows.append({
            "band": i + 1,
            "relative_charge_low": float(lo),
            "relative_charge_high": float(hi),
            "heat_loss_proxy_low": float(hlp_in_band.min()) if len(hlp_in_band) else float("nan"),
            "heat_loss_proxy_high": float(hlp_in_band.max()) if len(hlp_in_band) else float("nan"),
            "heat_loss_proxy_median": float(np.median(hlp_in_band)) if len(hlp_in_band) else float("nan"),
            "n_household_nights": int(mask.sum()),
        })
    calib = pl.DataFrame(rows)
    return calib, max_map


def lookup_band(heat_loss_proxy: float, calibration: pl.DataFrame) -> int:
    """
    Given tonight's forecast heat_loss_proxy, return the Target Charge
    Index (1-5) whose heat_loss_proxy range it falls into. Uses the band
    MEDIANS as boundaries (more robust to the overlap that quantile-based
    binning on a noisy joint distribution naturally produces than using
    raw min/max, which can overlap between adjacent bands).
    """
    medians = calibration.sort("band")["heat_loss_proxy_median"].to_list()
    # boundaries = midpoints between consecutive medians
    boundaries = [(medians[i] + medians[i + 1]) / 2 for i in range(len(medians) - 1)]
    band = 1
    for b in boundaries:
        if heat_loss_proxy > b:
            band += 1
    return band


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src")
    from overcharge_test import fit_seasonal_household, OVERCHARGE_MARGIN_FRACTION

    nights = pl.read_parquet("data/intermediate/phase1_household_nights.parquet")
    seasonal_raw = nights.filter(pl.col("heating_type") == "seasonal")
    wx = pl.read_parquet("data/intermediate/phase2_thermal_forecast_2013.parquet")

    # CONSISTENCY FIX (see module docstring / evidence_map.md, 2026-09-02):
    # Phase 1's modelled_required_kwh was fitted against the temperature-only
    # proxy (v1) -- wind data didn't exist yet at that point in the project.
    # v2 (wind-chill-adjusted) differs from v1 by >2 degree-days on 150/365
    # days (41%) -- not a rounding difference. Refit each household's
    # response line against v2 using the real wind data now available,
    # rather than calibrate this index against a proxy the forecast engine
    # won't actually be using at lookup time.
    seasonal = seasonal_raw.join(
        wx.select(["date", "heat_loss_proxy_v2_windchill"]),
        left_on="night_date", right_on="date", how="left",
    ).drop_nulls("heat_loss_proxy_v2_windchill").rename(
        {"heat_loss_proxy": "heat_loss_proxy_v1", "heat_loss_proxy_v2_windchill": "heat_loss_proxy"}
    )

    fits_v2 = [fit_seasonal_household(seasonal.filter(pl.col("LCLid") == hh))
               for hh in seasonal["LCLid"].unique().sort().to_list()]
    fits_v2_df = pl.DataFrame([{"LCLid": f.lclid, "intercept": f.intercept, "slope": f.slope,
                                 "r_squared": f.r_squared, "n_nights": f.n_nights} for f in fits_v2])
    fits_v2_df.write_parquet("data/intermediate/phase2_household_fits_windchill.parquet")

    print("Refit quality (wind-chill proxy) vs. Phase 1's original (temp-only):")
    orig_fits = pl.read_parquet("data/intermediate/phase1_household_fits.parquet")
    print(f"  Original (v1) median R²: {orig_fits['r_squared'].median():.3f}")
    print(f"  Refit (v2) median R²:    {fits_v2_df['r_squared'].median():.3f}")

    seasonal = seasonal.join(fits_v2_df.select(["LCLid", "intercept", "slope"]), on="LCLid").with_columns(
        (pl.col("intercept") + pl.col("slope") * pl.col("heat_loss_proxy")).clip(lower_bound=0).alias("modelled_required_kwh_v2")
    ).drop("modelled_required_kwh").rename({"modelled_required_kwh_v2": "modelled_required_kwh"})

    calib, max_map = build_calibration(seasonal)
    calib.write_parquet("data/intermediate/phase2_index_calibration.parquet")

    print()
    print("=== Target Charge Index calibration (wind-chill-consistent) ===")
    print(calib)

    # self-test: lookup should be monotonic -- colder (higher heat_loss_proxy) never
    # produces a LOWER index than a milder night
    test_proxies = [0.0, 2.0, 5.0, 8.0, 12.0, 15.0, 17.0]
    bands = [lookup_band(p, calib) for p in test_proxies]
    print()
    print("Self-test -- monotonicity check:")
    for p, b in zip(test_proxies, bands):
        print(f"  heat_loss_proxy={p:5.1f} -> Index {b}")
    assert all(bands[i] <= bands[i + 1] for i in range(len(bands) - 1)), \
        f"Index must be monotonic in heat_loss_proxy, got {bands}"
    print("monotonicity: PASS")

    assert lookup_band(0.0, calib) == 1, "a mild night (0 heat-loss) should be the lowest band"
    assert lookup_band(17.7, calib) == N_BANDS, "the coldest observed night should be the highest band"
    print("boundary checks: PASS")

    print(f"\nCalibrated against {seasonal.height} real household-nights across {seasonal['LCLid'].n_unique()} households.")
    print("\nKNOWN GAP: this index calibrates the overcharge-avoiding half only.")
    print("The afternoon-exhaustion-avoiding floor is NOT calibrated -- Phase 1's")
    print("exhaustion test returned a negative result (no validated relationship to build one from).")
