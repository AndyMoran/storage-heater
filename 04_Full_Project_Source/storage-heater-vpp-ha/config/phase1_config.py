"""
Phase 1 configuration: every material constant named here, not buried in
notebook logic (PROJECT.md 5.6). Each entry states whether it is a fixed
convention, a cited external figure, or an untested placeholder pending
Phase 1's own data (PROJECT.md 9.5, Assumptions Ledger).

Nothing in this file has been calibrated against real data yet -- Phase 1
has not ingested any data as of file creation. These are METHODOLOGY.md's
own starting values (1.1-1.4), carried over verbatim and flagged.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaConfig:
    # Stage A (1.1): gap-tolerance for "contiguous half-hour steps" check.
    # Convention choice, not yet tested against real gap frequency in LCL.
    max_unexplained_gap_minutes: int = 60  # STATUS: convention, adjust after first look at real gaps


@dataclass(frozen=True)
class CoarseScreenConfig:
    # Stage A (1.2.1): cheap vectorized filter before per-household signature check.
    overnight_window_start_hour: int = 23
    overnight_window_end_hour: int = 7
    overnight_mean_kw_threshold: float = 1.5  # STATUS: METHODOLOGY.md example value, UNTESTED


@dataclass(frozen=True)
class SignatureConfig:
    # Stage A (1.2.2): rule-based charge-event detector.
    baseload_rolling_window_days: int = 7
    charge_band_low_kw: float = 1.8  # STATUS: METHODOLOGY.md example, roughly matches ONE typical storage-heater unit (common UK ratings 1.7-2.55kW)
    charge_band_high_kw: float | None = None  # DEPRECATED 2026-08-31: no longer enforced. See evidence_map.md -- a 2-bed property with ~5 heaters (common UK sizing) can draw 8.5-13kW simultaneously; a fixed 3.2kW cap assumed a single heater and excluded real multi-heater households (confirmed on MAC003218, 10-13kW block). Field kept, unused, for traceability of the change rather than silently deleted.
    max_relative_swing_in_run: float = 0.4  # NEW 2026-08-31: (max-min)/mean within a candidate charge run must be <= this. Added because dropping the band's upper cap (above) also silently removed the only steadiness check -- without it, ANY sustained elevated reading qualifies, spiky or not, and 42/42 coarse-screened households passed (a red flag, not a result). STATUS: untested threshold, chosen as "fairly steady" not derived from data.
    min_consecutive_halfhours: int = 3
    # A household qualifies as "likely storage-heater" if charge events occur
    # on a majority of nights across at least one full heating-season month.
    majority_night_fraction: float = 0.5
    min_qualifying_month_days: int = 28


@dataclass(frozen=True)
class OverchargeConfig:
    # Stage B (1.3): degree-day proxy for modelled "required" overnight kWh.
    # 15.5C is the UK HDD convention (METHODOLOGY.md 1.3), not yet tested
    # against whether it's the right base for THIS population.
    base_temp_c: float = 15.5  # STATUS: UK HDD convention, not yet Phase-1-derived
    heat_loss_a_constant: float = 1.0  # STATUS: PLACEHOLDER -- not yet fitted to any data. Do not use for a real finding.
    overcharge_margin_fraction: float = 0.15  # STATUS: PLACEHOLDER margin, UNTESTED


@dataclass(frozen=True)
class BoostDetectionConfig:
    # Stage B (1.3): second, distinct load signature, 16:00-20:00 window.
    boost_window_start_hour: int = 16
    boost_window_end_hour: int = 20
    # Deliberately left distinct from SignatureConfig's band -- boost pulses
    # are expected shorter/more irregular; exact band UNTESTED, first look
    # at real boost-window traces should set this, not this default.
    boost_min_kw: float = 0.5
    boost_max_kw: float = 3.0


SCHEMA = SchemaConfig()
COARSE_SCREEN = CoarseScreenConfig()
SIGNATURE = SignatureConfig()
OVERCHARGE = OverchargeConfig()
BOOST = BoostDetectionConfig()
