"""
Phase 2.4: Compliance and financial-impact simulation (METHODOLOGY.md 2.4).

Scenario grid, not a full Monte Carlo, per the Sledgehammer Test: tenant
compliance rate (10/30/50%, illustrative bounds) x weather year x tariff.
Reports a range, not a single point estimate.

SCOPE, STATED UPFRONT (see evidence_map.md, 2026-09-02):
- "Multiple historical weather years" is satisfied with real weather data
  across several years, applying each CONFIRMED household's own fitted
  response (Phase 1/2.2 -- a property of the heating system, not the
  specific year) to that year's real degree-days. This tests weather-driven
  variance in the savings estimate. It is NOT a claim about how tenants
  would actually have behaved in a different year -- no behavioral data
  exists for any year but 2013.
- Agile prices remain the two representative weeks already sourced
  (winter/summer 2026), per the Sledgehammer Test's explicit tolerance for
  scenario-grid-level approximation over exhaustive real-price simulation.

Method per (compliance, year, tariff) cell:
  total_modelled_kwh(year) = sum over households of the household's own
    fitted line (intercept + slope * heat_loss_proxy) applied to that
    year's real daily heat-loss proxy, summed across the year.
  total_actual_kwh(year) = total_modelled_kwh(year) * (1 + household's own
    OBSERVED 2013 overcharge rate) -- the RATE of overcharging (a
    behavioural tendency) is assumed to transfer across years even though
    the weather differs; the absolute weather does not need to.
  savings(p, year, tariff) = p * (actual - modelled) * price(tariff, year)
"""

from __future__ import annotations

import polars as pl
import numpy as np
import sys
sys.path.insert(0, "src")
from thermal_forecast import heat_loss_proxy_v2

COMPLIANCE_RATES = [0.10, 0.30, 0.50]  # illustrative bounds, PROJECT.md 9.5 item 4


def compute_household_overcharge_rates(nights: pl.DataFrame) -> pl.DataFrame:
    """
    Per household: overcharge_rate = (sum of excess on FLAGGED nights only) / modelled_kwh_2013.

    NOT (actual - modelled) summed over ALL nights -- that was tried first
    and gave exactly zero for every household (evidence_map.md, 2026-09-02).
    This is a real mathematical property, not a bug: OLS regression with an
    intercept produces residuals that sum to exactly zero by construction,
    so a net-residual "overcharge rate" is guaranteed to be ~0 regardless
    of the real data. Phase 1's own overcharge figure was never a net
    annual residual -- it was specifically the sum of excess on nights
    flagged as overcharged (actual > modelled * 1.25), which is what this
    function now reproduces.
    """
    seasonal = nights.filter(pl.col("heating_type") == "seasonal")
    return (
        seasonal.group_by("LCLid")
        .agg(
            pl.col("night_kwh").sum().alias("actual_kwh_2013"),
            pl.col("modelled_required_kwh").sum().alias("modelled_kwh_2013"),
            pl.col("overcharge_magnitude_kwh").filter(pl.col("overcharge_flag")).sum().alias("flagged_excess_kwh_2013"),
        )
        .with_columns(
            (pl.col("flagged_excess_kwh_2013") / pl.col("modelled_kwh_2013")).alias("overcharge_rate")
        )
    )


def simulate_year(
    weather_year: pl.DataFrame,  # columns: date, mean_temp_c, mean_wind_kmh
    household_fits: pl.DataFrame,  # columns: LCLid, intercept, slope
    overcharge_rates: pl.DataFrame,  # columns: LCLid, overcharge_rate
) -> dict:
    """Returns total modelled kWh and total actual (unmanaged) kWh for one year, all households."""
    daily_proxy = np.array([
        heat_loss_proxy_v2(row["mean_temp_c"], row["mean_wind_kmh"])
        for row in weather_year.iter_rows(named=True)
    ])
    sum_proxy = daily_proxy.sum()

    fits = household_fits.join(overcharge_rates.select(["LCLid", "overcharge_rate"]), on="LCLid")
    total_modelled = 0.0
    total_actual = 0.0
    for row in fits.iter_rows(named=True):
        modelled_kwh = max(0.0, row["intercept"]) * len(daily_proxy) + row["slope"] * sum_proxy
        # guard: modelled charge can't be negative on any given day even if intercept is slightly off;
        # this aggregate approximation is a Sledgehammer-Test-level simplification, not a day-by-day clip.
        modelled_kwh = max(0.0, modelled_kwh)
        actual_kwh = modelled_kwh * (1 + max(0.0, row["overcharge_rate"]))
        total_modelled += modelled_kwh
        total_actual += actual_kwh
    return {"total_modelled_kwh": total_modelled, "total_actual_kwh": total_actual,
            "n_households": fits.height, "sum_heat_loss_proxy": sum_proxy}


if __name__ == "__main__":
    # --- VALIDATION: reproduce Phase 1's own already-proven 2013 numbers ---
    # before trusting this pipeline on any new weather year.
    nights = pl.read_parquet("data/intermediate/phase1_household_nights.parquet")
    fits_v2 = pl.read_parquet("data/intermediate/phase2_household_fits_windchill.parquet")
    wx_2013 = pl.read_parquet("data/intermediate/phase2_thermal_forecast_2013.parquet").select(
        ["date", "mean_temp_c", "mean_wind_kmh"]
    )
    overcharge_rates = compute_household_overcharge_rates(nights)

    result_2013 = simulate_year(wx_2013, fits_v2, overcharge_rates)
    print("=== Validation against Phase 1's known 2013 result ===")
    print(f"Simulated total modelled kWh (2013): {result_2013['total_modelled_kwh']:,.0f}")
    print(f"Simulated total actual kWh (2013):    {result_2013['total_actual_kwh']:,.0f}")
    print(f"Simulated excess kWh (2013):          {result_2013['total_actual_kwh'] - result_2013['total_modelled_kwh']:,.0f}")
    print()
    print("Phase 1's ACTUAL reported figure for seasonal households specifically:")
    print("  3,492/13,467 nights flagged, excess kWh = 22,249 (from the Phase 1 report)")
    pct_diff = (result_2013['total_actual_kwh'] - result_2013['total_modelled_kwh'] - 22249) / 22249 * 100
    print(f"  Simulated vs. reported difference: {pct_diff:+.1f}%")
    print("  (A small gap is expected: this simulation re-derives modelled_kwh from the")
    print("   wind-chill-refit v2 model built in 2.2, not the original v1 figures Phase 1")
    print("   reported -- see the 2026-09-02 refit entry in evidence_map.md.)")
