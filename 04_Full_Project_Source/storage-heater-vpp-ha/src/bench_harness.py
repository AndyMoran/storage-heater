"""
Phase 3.1 bench-test harness: runs src/control_logic.py against REAL time
(not simulated timestamps) on a loop, logs every decision, and drives an
actual relay through a pluggable "driver" function.

This is deliberately hardware-agnostic at the core. Plug in a driver
function for whatever's actually driving the LED/relay (Shelly HTTP API,
GPIO on a Pi/ESP32, etc.) -- see set_relay_stub() below for the interface
to implement.

Logs match METHODOLOGY.md 3.3's ask to "log relay state, dummy-load power,
and sensor readings throughout" -- power isn't loggable from pure software
(that's a real bench measurement), but relay state, setpoint, and the full
decision reason are, and are written to a CSV every poll.
"""

from __future__ import annotations

import csv
import datetime as dt
import time
import sys
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, "config")
from control_logic import compute_control_state, ControlState

LOG_PATH = Path("data/intermediate/phase3_bench_log.csv")
POLL_INTERVAL_SEC = 30  # how often to re-evaluate the control logic. Lower for a fast bench demo (e.g. 5s), higher for a real multi-hour soak test.


def set_relay_stub(state: bool) -> None:
    """
    REPLACE THIS FUNCTION with real hardware control.

    This stub only prints -- it does not drive anything. Wire in your
    actual relay/LED driver here.

    Shelly Pro 1PM (recommended -- see evidence_map.md, 2026-09-02, for
    why: same device the eventual real install will use, confirmed real
    specs, local network operation, no cloud/hub dependency). It is a
    Gen2+ device using JSON-RPC over HTTP, NOT the older Gen1 "legacy"
    /relay/0?turn= format (that applies to the older plain "Shelly1/1PM",
    a different product -- checked directly against Shelly's own API docs
    before writing this, not assumed):

        import requests
        SHELLY_IP = "192.168.1.xx"  # set to your device's actual local IP
        def set_relay(state: bool) -> None:
            requests.get(f"http://{SHELLY_IP}/rpc/Switch.Set", params={"id": 0, "on": str(state).lower()})

    To also pull REAL measured power (the Pro 1PM's built-in metering
    satisfies METHODOLOGY.md 3.3's "log... dummy-load power" requirement
    directly from the hardware, no separate meter needed):

        def read_relay_power_watts() -> float:
            r = requests.get(f"http://{SHELLY_IP}/rpc/Switch.GetStatus", params={"id": 0})
            return r.json().get("apower", 0.0)  # apower = active power in watts

    Raspberry Pi GPIO (RPi.GPIO or gpiozero) -- fine for a quick logic
    demo, but a different hardware/integration path than the eventual
    mains-relay install, so bench-testing on it doesn't validate as much:
        from gpiozero import LED
        led = LED(17)  # BCM pin 17
        def set_relay(state: bool) -> None:
            led.on() if state else led.off()
    """
    print(f"      [STUB -- no hardware wired in yet] would set relay: {'ON' if state else 'OFF'}")


def read_rh_sensor_stub() -> float | None:
    """
    REPLACE THIS FUNCTION with a real sensor read.
    Returns None to simulate a sensor dropout (tests the fail-safe path
    for real, not just in the unit tests).
    """
    return 55.0  # fixed dummy value until a real RH sensor is wired in


def get_target_charge_index_stub(now: dt.datetime) -> int | None:
    """
    REPLACE THIS FUNCTION once the Phase 2 forecast pipeline is wired to
    run live. For the bench test, hard-code whichever scenario you're
    demonstrating (see run_bench_demo below for the four scenarios).
    """
    return 5  # defaults to "coldest night" -- override per-scenario in run_bench_demo


def run_control_loop(
    duration_sec: int,
    poll_interval_sec: int = POLL_INTERVAL_SEC,
    relay_driver=set_relay_stub,
    rh_reader=read_rh_sensor_stub,
    index_getter=get_target_charge_index_stub,
    override_requested_at: dt.datetime | None = None,
    log_path: Path = LOG_PATH,
):
    """Runs the real, tested control_logic against real wall-clock time, logging every decision."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    is_new_file = not log_path.exists()
    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        if is_new_file:
            writer.writerow(["timestamp", "relay_state", "target_setpoint_c", "override_active", "reason"])

        start = time.monotonic()
        last_relay_state = None
        while time.monotonic() - start < duration_sec:
            now = dt.datetime.now()
            state: ControlState = compute_control_state(
                now=now,
                target_charge_index=index_getter(now),
                measured_rh_pct=rh_reader(),
                manual_override_requested_at=override_requested_at,
            )
            relay_driver(state.relay_state)
            writer.writerow([now.isoformat(), state.relay_state, state.target_setpoint_c, state.override_active, state.reason])
            f.flush()

            if state.relay_state != last_relay_state:
                print(f"  {now.strftime('%H:%M:%S')}  relay -> {'ON ' if state.relay_state else 'OFF'}  "
                      f"setpoint={state.target_setpoint_c}C  {state.reason}")
                last_relay_state = state.relay_state

            time.sleep(poll_interval_sec)

    print(f"\nLog written to {log_path}")


if __name__ == "__main__":
    print(__doc__)
    print("This is the harness, not a live run -- see run_bench_demo.py for the four")
    print("scenario demos, or call run_control_loop() directly once real drivers are wired in.")
