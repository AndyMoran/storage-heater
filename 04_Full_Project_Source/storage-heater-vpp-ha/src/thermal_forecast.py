"""
Phase 2.1: Thermal forecast engine (METHODOLOGY.md 2.1).

Computes a daily heat-loss proxy using the SAME degree-day formula as
Phase 1 (src/overcharge_test.py, BASE_TEMP_C = 15.5), plus a wind-chill
adjustment term, per the explicit instruction that this must reuse Phase
1's formula rather than invent a fresh one (PROJECT.md 2.6, Mechanism
Before Model) -- so the Target Charge Index (2.2) is calibrated against
what Phase 1 actually showed happened, not a new assumption.

Wind chill: the JAG/TI (2001) formula, the standard used by the UK Met
Office, Environment Canada and the US National Weather Service (checked
directly, not assumed -- see evidence_map.md). Metric form:

    WC = 13.12 + 0.6215*T - 11.37*V^0.16 + 0.3965*T*V^0.16

T in degrees C, V in km/h. Valid ONLY for T <= 10C and V >= 4.8 km/h --
outside that range the formula is not validated and is not applied; the
raw temperature is used unadjusted instead of extrapolating a formula
past where it's been checked.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

BASE_TEMP_C = 15.5  # identical to Phase 1's overcharge_test.py -- not re-derived, reused deliberately
WIND_CHILL_MAX_TEMP_C = 10.0
WIND_CHILL_MIN_WIND_KMH = 4.8


def wind_chill_temp_c(temp_c: float, wind_speed_kmh: float) -> float:
    """
    JAG/TI wind chill in degrees C. Returns temp_c unadjusted outside the
    formula's validated range (T > 10C or wind < 4.8 km/h) rather than
    applying it somewhere it hasn't been checked to hold.
    """
    if temp_c > WIND_CHILL_MAX_TEMP_C or wind_speed_kmh < WIND_CHILL_MIN_WIND_KMH:
        return temp_c
    v16 = wind_speed_kmh ** 0.16
    return 13.12 + 0.6215 * temp_c - 11.37 * v16 + 0.3965 * temp_c * v16


def heat_loss_proxy_v2(temp_c: float, wind_speed_kmh: float, base_temp_c: float = BASE_TEMP_C) -> float:
    """
    Phase 1's exact structure -- max(0, base_temp - T) -- with the wind-
    chill-adjusted temperature substituted for raw temperature. The
    per-household calibration (slope/intercept) stays a Stage-2.2 concern,
    same as Phase 1 kept it a per-household fit rather than a single
    population constant; this function returns the physical proxy only.
    """
    effective_temp = wind_chill_temp_c(temp_c, wind_speed_kmh)
    return max(0.0, base_temp_c - effective_temp)


if __name__ == "__main__":
    # Self-test 1: hand-computed wind chill check.
    # T=-5C, V=30km/h: v16 = 30**0.16
    v16 = 30 ** 0.16
    expected = 13.12 + 0.6215 * (-5) - 11.37 * v16 + 0.3965 * (-5) * v16
    got = wind_chill_temp_c(-5, 30)
    assert abs(got - expected) < 1e-9, f"wind chill formula mismatch: {got} vs {expected}"
    assert -13.5 < got < -12.5, f"sanity check failed: expected roughly -13.0C, got {got:.2f}C"
    print(f"wind_chill_temp_c(-5, 30) = {got:.2f}C (hand-computed check: {expected:.2f}C)")

    # Self-test 2: formula must NOT apply outside its validated range.
    assert wind_chill_temp_c(15.0, 40) == 15.0, "should not adjust when temp > 10C"
    assert wind_chill_temp_c(-2.0, 2.0) == -2.0, "should not adjust when wind < 4.8 km/h"
    print("out-of-range guard: PASS (raw temp returned unadjusted when formula isn't validated)")

    # Self-test 3: heat_loss_proxy_v2 matches Phase 1's structure when wind chill doesn't apply.
    from math import isclose
    hl_calm = heat_loss_proxy_v2(5.0, 0.0)  # calm day -- no wind chill
    assert isclose(hl_calm, BASE_TEMP_C - 5.0), "with no wind, proxy should match Phase 1's plain formula"
    hl_windy = heat_loss_proxy_v2(5.0, 40.0)  # windy cold day -- wind chill should INCREASE the proxy
    assert hl_windy > hl_calm, "wind chill should increase the heat-loss proxy on a cold, windy day"
    print(f"heat_loss_proxy_v2(5C, calm) = {hl_calm:.2f}  |  heat_loss_proxy_v2(5C, 40km/h) = {hl_windy:.2f}")

    # Self-test 4: on a mild day, proxy stays 0 regardless of wind (matches Phase 1's floor at 0).
    assert heat_loss_proxy_v2(20.0, 50.0) == 0.0, "mild day should floor at 0 even with high wind"
    print("mild-day floor: PASS (proxy stays 0 above base_temp regardless of wind)")

    print("\nsrc/thermal_forecast.py self-test: ALL PASS")
