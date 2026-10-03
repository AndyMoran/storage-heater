"""
Stage B: overcharge test (METHODOLOGY.md 1.3).

Design decision (evidence_map.md, 2026-09-01): a single population-wide
a_constant does not fit -- the temp-vs-charge sanity check showed clearly
different slopes across households (plausibly different heater counts per
property, consistent with the earlier "~5 heaters per 2-bed property"
finding). Each 'seasonal' household gets its own fitted response line:

    night_kwh ~ intercept + slope * heat_loss_proxy,   heat_loss_proxy = max(0, 15.5 - mean_temp_c)

A night is flagged "overcharged" if actual charge exceeds this household's
OWN fitted line by more than a margin -- i.e. more than how that specific
household typically responds to that specific temperature, not a
universal physical model. This is an auditable outlier test, not a claim
about the true thermal physics of any one property.

'year_round' households (no temperature response at all, confirmed
visually and via R_seasonal) get a different, simpler test: on any night
warmer than base_temp, there is no legitimate heat-loss justification for
ANY charge at all, so charge above a small baseline (assumed standby/
measurement floor) on a mild night is overcharge by construction.
"""

from __future__ import annotations

import polars as pl
import numpy as np
from dataclasses import dataclass


BASE_TEMP_C = 15.5
OVERCHARGE_MARGIN_FRACTION = 0.25  # flag where actual exceeds modelled by >25%. STATUS: untested threshold, first pass.
MILD_NIGHT_BASELINE_KWH = 2.0      # for year_round households: charge above this on a mild night counts as overcharge. STATUS: untested, chosen from the visual floor seen in seasonal households' mild-night baseline.


@dataclass
class HouseholdFit:
    lclid: str
    intercept: float
    slope: float
    r_squared: float
    n_nights: int


def fit_seasonal_household(nights: pl.DataFrame) -> HouseholdFit:
    """OLS fit of night_kwh ~ intercept + slope * heat_loss_proxy for one household."""
    x = nights['heat_loss_proxy'].to_numpy()
    y = nights['night_kwh'].to_numpy()
    lclid = nights['LCLid'][0]
    n = len(x)
    if n < 30:
        return HouseholdFit(lclid, np.nan, np.nan, np.nan, n)

    A = np.vstack([np.ones_like(x), x]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    intercept, slope = coef
    pred = intercept + slope * x
    ss_res = np.sum((y - pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return HouseholdFit(lclid, float(intercept), float(slope), float(r_sq), n)


if __name__ == "__main__":
    nightly = pl.read_parquet("data/intermediate/phase1_household_nights_raw.parquet")

    seasonal = nightly.filter(pl.col("heating_type") == "seasonal")
    fits = [fit_seasonal_household(seasonal.filter(pl.col("LCLid") == hh))
            for hh in seasonal["LCLid"].unique().sort().to_list()]
    fits_df = pl.DataFrame([{"LCLid": f.lclid, "intercept": f.intercept, "slope": f.slope,
                              "r_squared": f.r_squared, "n_nights": f.n_nights} for f in fits])
    fits_df.write_parquet("data/intermediate/phase1_household_fits.parquet")

    print("Fit quality across", fits_df.height, "seasonal households:")
    print(fits_df.select(["slope", "intercept", "r_squared"]).describe())
    print()
    print("Weakest fits (lowest R²):")
    print(fits_df.sort("r_squared").head(5))

    # --- Apply the overcharge test ---
    seasonal_with_fit = seasonal.join(fits_df.select(["LCLid", "intercept", "slope"]), on="LCLid")
    seasonal_flagged = seasonal_with_fit.with_columns(
        (pl.col("intercept") + pl.col("slope") * pl.col("heat_loss_proxy")).clip(lower_bound=0).alias("modelled_required_kwh")
    ).with_columns(
        (pl.col("night_kwh") > pl.col("modelled_required_kwh") * (1 + OVERCHARGE_MARGIN_FRACTION)).alias("overcharge_flag"),
        (pl.col("night_kwh") - pl.col("modelled_required_kwh")).alias("overcharge_magnitude_kwh"),
    )

    year_round = nightly.filter(pl.col("heating_type") == "year_round").with_columns(
        pl.lit(MILD_NIGHT_BASELINE_KWH).alias("modelled_required_kwh")
    ).with_columns(
        ((pl.col("mean_temp_c") > BASE_TEMP_C) & (pl.col("night_kwh") > MILD_NIGHT_BASELINE_KWH)).alias("overcharge_flag"),
        pl.when(pl.col("mean_temp_c") > BASE_TEMP_C)
          .then(pl.col("night_kwh") - MILD_NIGHT_BASELINE_KWH)
          .otherwise(None)
          .alias("overcharge_magnitude_kwh"),
    )

    combined_cols = ["LCLid", "night_date", "night_kwh", "mean_temp_c", "heat_loss_proxy",
                      "heating_type", "modelled_required_kwh", "overcharge_flag", "overcharge_magnitude_kwh"]
    final = pl.concat([seasonal_flagged.select(combined_cols), year_round.select(combined_cols)])
    final.write_parquet("data/intermediate/phase1_household_nights.parquet")

    print()
    print("=== Overcharge test results ===")
    print("Seasonal households: nights flagged overcharged:",
          seasonal_flagged.filter(pl.col("overcharge_flag")).height, "/", seasonal_flagged.height,
          f"({100*seasonal_flagged['overcharge_flag'].mean():.1f}%)")
    print("Year-round households (mild nights only, temp>15.5C): nights flagged overcharged:",
          year_round.filter(pl.col("overcharge_flag")).height, "/",
          year_round.filter(pl.col("mean_temp_c") > BASE_TEMP_C).height)
    print()
    print("Total excess kWh (seasonal, flagged nights only):", round(seasonal_flagged.filter(pl.col("overcharge_flag"))["overcharge_magnitude_kwh"].sum(), 1))
    print("Total excess kWh (year-round, mild nights only):", round(year_round.filter(pl.col("overcharge_flag"))["overcharge_magnitude_kwh"].sum(), 1))
