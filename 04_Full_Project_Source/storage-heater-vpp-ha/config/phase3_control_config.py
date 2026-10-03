"""
Phase 3.2 control logic config (METHODOLOGY.md 3.2). All constants named
here so the bench test can sweep them (PROJECT.md 5.6), none hard-coded
in src/control_logic.py.
"""

import datetime as dt

# --- Charging window ---
# METHODOLOGY.md 3.2's own stated default (00:00-05:00), used as given.
# NOTE: this is narrower than Phase 1/2's overnight analysis window
# (23:00-07:00). Not silently reconciled here -- flagged in evidence_map.md
# as a real inconsistency between the Phase 1/2 analysis window and the
# Phase 3 spec's own default, worth resolving before a live install, not
# something this code should paper over by picking one silently.
OFF_PEAK_START = dt.time(0, 0)
OFF_PEAK_END = dt.time(5, 0)

# --- Manual override ---
MANUAL_OVERRIDE_DURATION_MIN = 30

# --- Comfort cutoff (humidity-driven setpoint reduction) ---
RH_THRESHOLD_PCT = 50.0
NORMAL_SETPOINT_C = 21.0

# REDUCED_SETPOINT_C: corrected 2026-09-02 from the original placeholder
# (18.5C, a 2.5C reduction) which was explicitly marked "pending Phase 2
# psychrometric grounding" in METHODOLOGY.md's own pseudocode.
#
# Grounding: ISO 7730 (2005 and 2025 editions) -- "a 10% higher relative
# humidity and a 0.3C higher operative temperature are perceived as being
# warmer in equal measure." A realistic, achievable dehumidification swing
# that crosses this control's own 50% RH threshold (e.g. a damp ~65-70%
# baseline brought down to ~45-50%, a ~20 percentage-point swing) supports
# (20/10)*0.3 = 0.6C. Set conservatively BELOW that computed figure, not at
# or above it, per this project's own stated caution about erring toward
# not under-heating a vulnerable tenant (METHODOLOGY.md 2.3, PROJECT.md
# 2.10) -- see evidence_map.md, 2026-09-02, for the full derivation.
REDUCED_SETPOINT_C = 20.5

# --- Fail-safe defaults (METHODOLOGY.md 3.3 test 4: sensor dropout must
# fail toward safety -- normal setpoint and standard charging -- never
# toward "heater off" or an under-heated setpoint) ---
FAILSAFE_CHARGE_FRACTION = 1.0   # missing forecast -> charge as if coldest (Index 5), not skip charging
FAILSAFE_SETPOINT_C = NORMAL_SETPOINT_C  # missing RH reading -> normal setpoint, never reduced
