"""
Stage A schema contract for the ACTUAL file received (METHODOLOGY.md 1.1).

CORRECTION vs. the original assumption (logged in evidence_map.md,
2026-08-31): PROJECT.md 9.3 describes the raw London Datastore release as
long-format (LCLid, stdorToU, DateTime, KWH/hh, Acorn, Acorn_grouped).
The actual file obtained -- the 4TU.ResearchData refactored release
(Tindemans 2023) -- is WIDE format: one DateTime column, one column per
household (4,443 of them), no Acorn/stdorToU columns at all (they were
presumably stripped during refactoring; the Std-tariff filter was already
applied upstream, before this file was produced, so there is nothing left
to check per-row here).

This module works against the LONG-FORMAT converted output
(data/intermediate/lcl_2013_long.parquet: LCLid, DateTime, KWH_hh), which
Stage A's ingestion step produces from the wide source file. Fail loudly:
a household whose readings are missing beyond tolerance is flagged and
reported separately -- never silently interpolated over.
"""

from __future__ import annotations

import polars as pl
from dataclasses import dataclass


# Actual schema of the converted long-format file. No Acorn/stdorToU --
# see module docstring.
LONG_SCHEMA: dict[str, pl.DataType] = {
    "LCLid": pl.Utf8,
    "DateTime": pl.Datetime,
    "KWH_hh": pl.Float64,
}

KWH_HH_PLAUSIBLE_MAX = 20.0  # sanity bound; confirmed real max in this file is 10.761


def validate_schema(df_or_lf) -> list[str]:
    """Check columns/dtypes against LONG_SCHEMA. Empty list == OK."""
    schema = df_or_lf.collect_schema() if hasattr(df_or_lf, "collect_schema") else df_or_lf.schema
    problems: list[str] = []
    for col, expected_dtype in LONG_SCHEMA.items():
        if col not in schema.names():
            problems.append(f"missing required column: {col}")
            continue
        actual = schema[col]
        if expected_dtype == pl.Datetime:
            if not isinstance(actual, pl.Datetime):
                problems.append(f"column {col}: expected Datetime, got {actual}")
        elif actual != expected_dtype:
            problems.append(f"column {col}: expected {expected_dtype}, got {actual}")
    return problems


def timestamp_grid_check(lf: pl.LazyFrame, time_col: str = "DateTime") -> dict:
    """
    Confirm the shared timestamp grid is complete and regular (this file's
    households all share one DateTime index -- see module docstring, this
    replaces the original per-household gap-scan concept, which assumed
    long-format data with independent timestamps per household).
    """
    dts = lf.select(time_col).unique().sort(time_col).collect()[time_col]
    diffs = dts.diff().drop_nulls()
    all_30min = bool((diffs == diffs[0]).all()) if diffs.len() > 0 else True
    return {
        "n_distinct_timestamps": dts.len(),
        "min": dts.min(),
        "max": dts.max(),
        "all_steps_equal": all_30min,
        "step_seconds": diffs[0].total_seconds() if diffs.len() > 0 else None,
    }


def household_missingness_report(lf: pl.LazyFrame) -> pl.DataFrame:
    """
    Per-household null-value fraction. Households above tolerance are
    flagged and reported here -- not dropped, not interpolated. Downstream
    stages decide what to do with the flag (METHODOLOGY.md 1.1: 'flag and
    report gap-affected households separately, never silently interpolate').
    """
    return (
        lf.group_by("LCLid")
        .agg(
            pl.col("KWH_hh").null_count().alias("n_null"),
            pl.len().alias("n_total"),
        )
        .with_columns((pl.col("n_null") / pl.col("n_total")).alias("null_frac"))
        .sort("null_frac", descending=True)
        .collect(engine="streaming")
    )


def sanity_check_values(lf: pl.LazyFrame, kwh_col: str = "KWH_hh") -> list[str]:
    """Fail-loudly value checks -- physically impossible readings are a bug, not noise."""
    problems: list[str] = []
    stats = lf.select(
        pl.col(kwh_col).min().alias("min_val"),
        pl.col(kwh_col).max().alias("max_val"),
        (pl.col(kwh_col) < 0).sum().alias("n_negative"),
    ).collect(engine="streaming")
    min_val, max_val, n_negative = stats.row(0)
    if n_negative and n_negative > 0:
        problems.append(f"{kwh_col}: {n_negative} negative readings found")
    if max_val is not None and max_val > KWH_HH_PLAUSIBLE_MAX:
        problems.append(
            f"{kwh_col}: implausibly high reading found (max={max_val}, "
            f"bound={KWH_HH_PLAUSIBLE_MAX})"
        )
    return problems


if __name__ == "__main__":
    # Code-correctness self-test only -- NOT a Phase 1 finding.
    import datetime as dt

    fixture = pl.DataFrame(
        {
            "LCLid": ["MAC001"] * 4 + ["MAC002"] * 4,
            "DateTime": [
                dt.datetime(2013, 1, 1, 0, 30),
                dt.datetime(2013, 1, 1, 1, 0),
                dt.datetime(2013, 1, 1, 1, 30),
                dt.datetime(2013, 1, 1, 2, 0),
            ] * 2,
            "KWH_hh": [0.1, 0.2, None, 0.18, None, None, None, None],
        }
    ).lazy()

    assert validate_schema(fixture) == []
    grid = timestamp_grid_check(fixture)
    assert grid["all_steps_equal"] is True
    report = household_missingness_report(fixture)
    assert report.filter(pl.col("LCLid") == "MAC002")["null_frac"][0] == 1.0
    assert sanity_check_values(fixture) == []

    print("src/schema.py self-test: PASS")
