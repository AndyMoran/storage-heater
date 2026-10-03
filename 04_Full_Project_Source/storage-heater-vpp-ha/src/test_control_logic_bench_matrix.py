"""
Unit tests for src/control_logic.py against METHODOLOGY.md §3.3's bench
test matrix -- run in software BEFORE any hardware exists, per the user's
explicit request. These are the same four scenarios the physical bench
rig will need to reproduce with a real relay/sensor once built; passing
here first is the point, not a replacement for the real bench run.
"""

import datetime as dt
import sys
sys.path.insert(0, "src")
sys.path.insert(0, "config")
from control_logic import compute_control_state, charge_fraction_for_index, _load_calibration
from phase3_control_config import (
    OFF_PEAK_START, OFF_PEAK_END, MANUAL_OVERRIDE_DURATION_MIN,
    NORMAL_SETPOINT_C, REDUCED_SETPOINT_C, RH_THRESHOLD_PCT,
)

TODAY = dt.date(2026, 1, 15)


def t(hour, minute=0):
    return dt.datetime.combine(TODAY, dt.time(hour, minute))


def run_test(name, fn):
    try:
        fn()
        print(f"  [PASS] {name}")
        return True
    except AssertionError as e:
        print(f"  [FAIL] {name}: {e}")
        return False


# === Scenario 1: simulated cold night -- verify full off-peak charge ===
def test_1_cold_night_full_charge():
    calib = _load_calibration()
    frac, _ = charge_fraction_for_index(5, calib)
    on_duration_min = frac * ((dt.datetime.combine(TODAY, OFF_PEAK_END) - dt.datetime.combine(TODAY, OFF_PEAK_START)).total_seconds() / 60)
    print(f"      (Index 5 charges for {frac:.1%} of the window = {on_duration_min:.0f} of 300 min --")
    print(f"       a real empirical quantile-band midpoint, not a fudged 100%)")

    # Well within the charging duration for the coldest band -> relay ON
    state = compute_control_state(t(2, 0), target_charge_index=5, measured_rh_pct=55.0, manual_override_requested_at=None)
    assert state.relay_state is True, f"expected ON at 02:00 for coldest index, got {state.relay_state}. Reason: {state.reason}"

    # Near the very start -> also ON
    state2 = compute_control_state(t(0, 5), target_charge_index=5, measured_rh_pct=55.0, manual_override_requested_at=None)
    assert state2.relay_state is True, f"expected ON at 00:05 for coldest index, got {state2.relay_state}"


# === Scenario 2: simulated mild night -- verify reduced/no charge ===
def test_2_mild_night_reduced_charge():
    calib = _load_calibration()
    frac, _ = charge_fraction_for_index(1, calib)
    print(f"      (Index 1 charges for only {frac:.1%} of the window)")

    # Briefly ON right at window start (band 1's small nonzero fraction)
    state_start = compute_control_state(t(0, 5), target_charge_index=1, measured_rh_pct=55.0, manual_override_requested_at=None)
    assert state_start.relay_state is True, f"expected brief ON at 00:05 even for mildest index, got OFF. Reason: {state_start.reason}"

    # But OFF well before the window ends -- this is the "reduced" behaviour
    state_later = compute_control_state(t(2, 0), target_charge_index=1, measured_rh_pct=55.0, manual_override_requested_at=None)
    assert state_later.relay_state is False, f"expected OFF at 02:00 for mildest index (charge target already met), got ON. Reason: {state_later.reason}"


# === Scenario 3: manual override mid-afternoon -- engages and lapses correctly ===
def test_3_manual_override():
    # Requested 15 min ago, well within the 30 min limit -> engaged
    state_active = compute_control_state(
        t(15, 0), target_charge_index=2, measured_rh_pct=55.0,
        manual_override_requested_at=t(14, 45),
    )
    assert state_active.override_active is True, f"expected override active, got inactive. Reason: {state_active.reason}"
    assert state_active.relay_state is True, f"expected relay ON during active override, got OFF. Reason: {state_active.reason}"

    # Requested 60 min ago, past the 30 min limit -> lapsed
    state_lapsed = compute_control_state(
        t(15, 0), target_charge_index=2, measured_rh_pct=55.0,
        manual_override_requested_at=t(14, 0),
    )
    assert state_lapsed.override_active is False, f"expected override lapsed, got still active. Reason: {state_lapsed.reason}"
    assert state_lapsed.relay_state is False, f"expected relay OFF after override lapses (outside window too), got ON. Reason: {state_lapsed.reason}"

    # Exactly at the boundary (30 min elapsed) -> should have just lapsed (>= limit, not <)
    state_boundary = compute_control_state(
        t(15, 0), target_charge_index=2, measured_rh_pct=55.0,
        manual_override_requested_at=t(14, 30),
    )
    assert state_boundary.override_active is False, f"expected override lapsed exactly at the {MANUAL_OVERRIDE_DURATION_MIN}min boundary"


# === Scenario 4: sensor dropout -- fails SAFE, not silent/off ===
def test_4a_forecast_dropout_failsafe():
    # No index available at all (forecast/index system down) during off-peak window
    state = compute_control_state(t(4, 45), target_charge_index=None, measured_rh_pct=55.0, manual_override_requested_at=None)
    assert state.relay_state is True, (
        f"CRITICAL: forecast dropout must fail toward standard charging, not 'heater off'. "
        f"Got relay_state={state.relay_state}. Reason: {state.reason}"
    )
    assert "fail-safe" in state.reason, "fail-safe path should be visible in the audit reason, not silent"


def test_4b_rh_sensor_dropout_failsafe():
    # RH sensor unavailable -> must default to NORMAL setpoint, never the reduced one
    state = compute_control_state(t(2, 0), target_charge_index=3, measured_rh_pct=None, manual_override_requested_at=None)
    assert state.target_setpoint_c == NORMAL_SETPOINT_C, (
        f"CRITICAL: RH sensor dropout must default to normal setpoint ({NORMAL_SETPOINT_C}C), "
        f"never the reduced one. Got {state.target_setpoint_c}C. Reason: {state.reason}"
    )
    assert "fail-safe" in state.reason


# === Supplementary: comfort cutoff logic itself, not one of the 4 named
# scenarios but core to the spec and worth testing directly ===
def test_comfort_cutoff_direct():
    dry = compute_control_state(t(2, 0), target_charge_index=3, measured_rh_pct=40.0, manual_override_requested_at=None)
    assert dry.target_setpoint_c == REDUCED_SETPOINT_C, f"expected reduced setpoint at 40% RH, got {dry.target_setpoint_c}"

    humid = compute_control_state(t(2, 0), target_charge_index=3, measured_rh_pct=60.0, manual_override_requested_at=None)
    assert humid.target_setpoint_c == NORMAL_SETPOINT_C, f"expected normal setpoint at 60% RH, got {humid.target_setpoint_c}"

    # Override active should suppress the comfort cutoff even if RH is low -- tenant-requested
    # boost should not be undermined by a setpoint reduction they didn't ask for.
    dry_but_overridden = compute_control_state(
        t(15, 0), target_charge_index=3, measured_rh_pct=40.0, manual_override_requested_at=t(14, 45),
    )
    assert dry_but_overridden.target_setpoint_c == NORMAL_SETPOINT_C, (
        f"expected normal setpoint during active override even at low RH, got {dry_but_overridden.target_setpoint_c}"
    )


def test_determinism():
    args = dict(now=t(2, 0), target_charge_index=3, measured_rh_pct=45.0, manual_override_requested_at=None)
    s1 = compute_control_state(**args)
    s2 = compute_control_state(**args)
    assert s1.relay_state == s2.relay_state and s1.target_setpoint_c == s2.target_setpoint_c, \
        "same inputs must always produce the same control state"


if __name__ == "__main__":
    print("=== METHODOLOGY.md 3.3 bench test matrix (software simulation) ===\n")
    tests = [
        ("Scenario 1: cold night -> full off-peak charge", test_1_cold_night_full_charge),
        ("Scenario 2: mild night -> reduced/no charge", test_2_mild_night_reduced_charge),
        ("Scenario 3: manual override engages and lapses", test_3_manual_override),
        ("Scenario 4a: forecast dropout fails SAFE (charges, doesn't skip)", test_4a_forecast_dropout_failsafe),
        ("Scenario 4b: RH sensor dropout fails SAFE (normal setpoint)", test_4b_rh_sensor_dropout_failsafe),
        ("Supplementary: comfort cutoff logic", test_comfort_cutoff_direct),
        ("Supplementary: determinism", test_determinism),
    ]
    results = [run_test(name, fn) for name, fn in tests]
    print()
    n_pass = sum(results)
    print(f"{n_pass}/{len(results)} tests passed.")
    if n_pass < len(results):
        sys.exit(1)
    print("\nAll four required bench scenarios (METHODOLOGY.md 3.3) pass in software.")
    print("This is NOT a substitute for the real bench run once hardware exists --")
    print("it's the check that should happen before committing to hardware, which is exactly what was asked for.")
