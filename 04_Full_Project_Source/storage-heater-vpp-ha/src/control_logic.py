"""
Phase 3.2: Control logic (METHODOLOGY.md 3.2).

Two interacting rules, per the spec's own pseudocode:
1. Relay (charging) state: off-peak window, modulated by tonight's Target
   Charge Index -- ported directly from Phase 2's real calibration table
   (data/intermediate/phase2_index_calibration.parquet band midpoints),
   not a reinvented fraction scheme -- plus a time-limited manual override.
2. Comfort cutoff: humidity-driven setpoint reduction, using the corrected,
   conservatively-grounded REDUCED_SETPOINT_C from config (see
   config/phase3_control_config.py for the full ISO 7730 derivation).

Every constant lives in config/phase3_control_config.py, none hard-coded
here, so the bench test can sweep them (PROJECT.md 5.6).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import polars as pl

import sys
sys.path.insert(0, "config")
from phase3_control_config import (
    OFF_PEAK_START, OFF_PEAK_END, MANUAL_OVERRIDE_DURATION_MIN,
    RH_THRESHOLD_PCT, NORMAL_SETPOINT_C, REDUCED_SETPOINT_C,
    FAILSAFE_CHARGE_FRACTION, FAILSAFE_SETPOINT_C,
)

_CALIBRATION_PATH = "data/intermediate/phase2_index_calibration.parquet"
_calibration_cache: pl.DataFrame | None = None


def _load_calibration() -> pl.DataFrame:
    global _calibration_cache
    if _calibration_cache is None:
        _calibration_cache = pl.read_parquet(_CALIBRATION_PATH).with_columns(
            ((pl.col("relative_charge_low") + pl.col("relative_charge_high")) / 2).alias("band_midpoint")
        )
    return _calibration_cache


def charge_fraction_for_index(target_charge_index: int | None, calibration: pl.DataFrame | None = None) -> tuple[float, str]:
    """Returns (fraction of off-peak window to charge, reason string). None index -> fail-safe."""
    if target_charge_index is None:
        return FAILSAFE_CHARGE_FRACTION, "forecast/index unavailable -> fail-safe: charge as if coldest night"
    calib = calibration if calibration is not None else _load_calibration()
    row = calib.filter(pl.col("band") == target_charge_index)
    if row.height == 0:
        return FAILSAFE_CHARGE_FRACTION, f"index {target_charge_index} out of range -> fail-safe: charge as if coldest night"
    frac = row["band_midpoint"][0]
    return frac, f"Index {target_charge_index} -> {frac:.0%} of off-peak window (Phase 2 calibration band midpoint)"


@dataclass
class ControlState:
    timestamp: dt.datetime
    relay_state: bool
    target_setpoint_c: float
    override_active: bool
    reason: str


def _window_bounds(now: dt.datetime) -> tuple[dt.datetime, dt.datetime]:
    """Off-peak window for the night containing `now` (handles the midnight-crossing window)."""
    start = dt.datetime.combine(now.date(), OFF_PEAK_START)
    end = dt.datetime.combine(now.date(), OFF_PEAK_END)
    if OFF_PEAK_END <= OFF_PEAK_START:  # window crosses midnight -- not the case with current 00:00-05:00 default, handled for robustness
        end += dt.timedelta(days=1)
    return start, end


def compute_control_state(
    now: dt.datetime,
    target_charge_index: int | None,
    measured_rh_pct: float | None,
    manual_override_requested_at: dt.datetime | None,
    calibration: pl.DataFrame | None = None,
) -> ControlState:
    """
    Pure function: same inputs always produce the same ControlState
    (PROJECT.md 5.5, deterministic baseline before randomness).
    """
    reasons = []

    # --- Manual override check (time-limited) ---
    override_active = False
    if manual_override_requested_at is not None:
        elapsed_min = (now - manual_override_requested_at).total_seconds() / 60.0
        if 0 <= elapsed_min < MANUAL_OVERRIDE_DURATION_MIN:
            override_active = True
            reasons.append(f"manual override active ({elapsed_min:.0f}/{MANUAL_OVERRIDE_DURATION_MIN} min elapsed)")
        elif elapsed_min >= MANUAL_OVERRIDE_DURATION_MIN:
            reasons.append(f"manual override lapsed ({elapsed_min:.0f} min elapsed, limit {MANUAL_OVERRIDE_DURATION_MIN})")

    # --- Relay state ---
    window_start, window_end = _window_bounds(now)
    in_window = window_start <= now < window_end

    if in_window:
        frac, frac_reason = charge_fraction_for_index(target_charge_index, calibration)
        window_len = (window_end - window_start).total_seconds()
        on_duration = frac * window_len
        elapsed_in_window = (now - window_start).total_seconds()
        relay_state = elapsed_in_window < on_duration
        reasons.append(f"in off-peak window; {frac_reason}; relay {'ON' if relay_state else 'OFF (charge target reached)'}")
    elif override_active:
        relay_state = True
        reasons.append("outside off-peak window; relay ON via active manual override")
    else:
        relay_state = False
        reasons.append("outside off-peak window; no active override; relay OFF")

    # --- Comfort cutoff (independent of relay state, per spec: "overlays, does not replace") ---
    if measured_rh_pct is None:
        target_setpoint = FAILSAFE_SETPOINT_C
        reasons.append("RH sensor unavailable -> fail-safe: normal setpoint")
    elif override_active:
        target_setpoint = NORMAL_SETPOINT_C
        reasons.append("manual override active -> normal setpoint (comfort cutoff does not apply during tenant-requested boost)")
    elif measured_rh_pct < RH_THRESHOLD_PCT:
        target_setpoint = REDUCED_SETPOINT_C
        reasons.append(f"measured RH {measured_rh_pct:.0f}% < {RH_THRESHOLD_PCT:.0f}% threshold -> reduced setpoint {REDUCED_SETPOINT_C}C")
    else:
        target_setpoint = NORMAL_SETPOINT_C
        reasons.append(f"measured RH {measured_rh_pct:.0f}% >= {RH_THRESHOLD_PCT:.0f}% threshold -> normal setpoint")

    return ControlState(
        timestamp=now, relay_state=relay_state, target_setpoint_c=target_setpoint,
        override_active=override_active, reason=" | ".join(reasons),
    )
