"""
Stage A, second pass: signature confirmation (METHODOLOGY.md 1.2.2).

Runs ONLY against the coarse-screen-flagged households (42 of them) -- the
coarse screen's job was to cut the population before this more expensive
per-household check, per 1.2.1.

Method, per household:
1. Baseload proxy: for each of the 48 half-hour-of-day slots, a rolling
   7-day trailing minimum (captures fridge/freezer/standby cycling, which
   repeats at a much shorter period than a storage heater's charge block).
2. Residual = raw kW - baseload proxy at that slot.
3. A half-hour is a "charge slot" if the residual falls within the
   configured band (default 1.8-3.2kW).
4. A night (23:00 of day D to 07:00 of day D+1) is a "charge night" if it
   contains a run of >= min_consecutive_halfhours charge slots.
5. A household is "likely storage-heater" if charge nights occur on a
   majority of nights within at least one calendar month with sufficient
   data (>= min_qualifying_month_days).

Deliberately implemented in NumPy over per-household arrays rather than
forced into Polars window expressions: with only 42 households (after the
coarse screen), a per-household loop is simpler to audit line-by-line than
equivalent group-window Polars code, and PROJECT.md 2.2 (Sledgehammer
Test) asks for the simplest credible method, not the most vectorized one.
Polars is used only for I/O and the initial per-household extraction.
"""

from __future__ import annotations

import numpy as np
import polars as pl
from dataclasses import dataclass
import sys
sys.path.insert(0, str(__file__.rsplit('/', 2)[0]) + '/config')
from phase1_config import SIGNATURE


@dataclass
class HouseholdSignatureResult:
    lclid: str
    n_nights_total: int
    n_nights_charge: int
    overall_charge_night_frac: float
    best_month: str | None
    best_month_frac: float
    best_month_n_days: int
    qualifies: bool


def _baseload_proxy(kw: np.ndarray, day_idx: np.ndarray, slot_idx: np.ndarray,
                     n_days: int, n_slots: int = 48, window_days: int = 7) -> np.ndarray:
    """
    ORIGINAL implementation, per METHODOLOGY.md 1.2.2's literal text:
    per-time-of-day-slot rolling 7-day trailing minimum.

    KEPT for reference but NOT USED (see evidence_map.md, 2026-08-31,
    'Signature-confirmation detector: a real limitation surfaced while
    self-testing' and the follow-up diagnostic entry). Confirmed on real
    data (MAC004863) to fail exactly as predicted: households that charge
    at a near-constant level every night make the same-slot trailing
    minimum converge to the charge level itself, erasing the residual.
    Superseded by _baseload_proxy_daytime below.
    """
    grid = np.full((n_days, n_slots), np.nan)
    grid[day_idx, slot_idx] = kw

    baseload_grid = np.full_like(grid, np.nan)
    for s in range(n_slots):
        col = grid[:, s]
        for d in range(n_days):
            lo = max(0, d - window_days + 1)
            window = col[lo:d + 1]
            valid = window[~np.isnan(window)]
            if valid.size > 0:
                baseload_grid[d, s] = valid.min()

    return baseload_grid[day_idx, slot_idx]


def _baseload_proxy_daytime(kw: np.ndarray, day_idx: np.ndarray, slot_idx: np.ndarray,
                             hour: np.ndarray, n_days: int, window_days: int = 7,
                             ref_hour_start: int = 10, ref_hour_end: int = 16) -> np.ndarray:
    """
    REVISED baseload proxy (deviation from METHODOLOGY.md 1.2.2's literal
    per-slot approach, logged in evidence_map.md 2026-08-31).

    For each day, baseload = rolling 7-day trailing minimum of readings
    taken ONLY during a daytime reference window (default 10:00-16:00),
    broadcast as a single per-day value across that night's slots.

    This is structurally immune to the circularity that broke the original
    approach: the reference window (10:00-16:00) does not overlap the
    charge-detection window (23:00-07:00) or the boost-detection window
    (16:00-20:00, METHODOLOGY.md 1.3), so a household's own heater signal
    cannot contaminate its own baseline, regardless of how consistently it
    charges night to night. Still captures fridge/freezer/standby draw,
    which is present at all hours by definition.
    """
    daytime_mask = (hour >= ref_hour_start) & (hour < ref_hour_end)
    daily_min = np.full(n_days, np.nan)
    for d in range(n_days):
        vals = kw[daytime_mask & (day_idx == d)]
        if vals.size > 0:
            daily_min[d] = vals.min()

    daily_baseload = np.full(n_days, np.nan)
    for d in range(n_days):
        lo = max(0, d - window_days + 1)
        window = daily_min[lo:d + 1]
        valid = window[~np.isnan(window)]
        if valid.size > 0:
            daily_baseload[d] = valid.min()

    return daily_baseload[day_idx]


def analyze_household(df: pl.DataFrame) -> HouseholdSignatureResult:
    """df: one household's rows, columns LCLid, DateTime, KWH_hh (any order of rows)."""
    lclid = df["LCLid"][0]
    df = df.sort("DateTime").drop_nulls("KWH_hh")
    if df.height == 0:
        return HouseholdSignatureResult(lclid, 0, 0, 0.0, None, 0.0, 0, False)

    dt = df["DateTime"].to_numpy()
    kw = (df["KWH_hh"].to_numpy()) * 2.0  # kWh per half-hour -> avg kW

    dt_pd = df["DateTime"]
    hour = df["DateTime"].dt.hour().to_numpy()
    date = df["DateTime"].dt.date().to_numpy()
    unique_dates = np.unique(date)
    date_to_idx = {d: i for i, d in enumerate(unique_dates)}
    day_idx = np.array([date_to_idx[d] for d in date])
    slot_idx = (hour * 2 + (df["DateTime"].dt.minute().to_numpy() // 30)).astype(int)
    n_days = len(unique_dates)

    baseload = _baseload_proxy_daytime(kw, day_idx, slot_idx, hour, n_days,
                                        window_days=SIGNATURE.baseload_rolling_window_days)
    residual = kw - baseload
    # Lower-bound-only test as of 2026-08-31 (evidence_map.md): the original
    # band's upper cap assumed a single storage-heater unit's worth of load.
    # Real properties commonly run several units simultaneously (a 2-bed
    # property with ~5 heaters can draw 8.5-13kW off-peak), so an upper cap
    # systematically excluded genuine multi-heater households. No cap now;
    # sustained elevation above the lower bound is the signal.
    in_band = residual >= SIGNATURE.charge_band_low_kw

    # night_id: a reading at hour>=23 belongs to that calendar date's night;
    # a reading at hour<7 belongs to the PREVIOUS calendar date's night.
    is_overnight = (hour >= 23) | (hour < 7)
    night_date = np.where(hour >= 23, date, date - np.timedelta64(1, "D"))

    charge_nights = set()
    all_nights = set(night_date[is_overnight])

    for nd in all_nights:
        mask = is_overnight & (night_date == nd)
        if not mask.any():
            continue
        night_in_band = in_band[mask]
        night_residual = residual[mask]
        order = np.argsort(dt[mask])
        night_in_band = night_in_band[order]
        night_residual = night_residual[order]

        # longest run of consecutive in-band half-hours, but a run only
        # counts if it's also STEADY (max-min)/mean <= max_relative_swing --
        # this is what actually distinguishes a heater's charge plateau from
        # a sustained-but-noisy load once the upper magnitude cap is gone
        # (evidence_map.md, 2026-08-31).
        found_qualifying_run = False
        run_start = None
        for i, v in enumerate(night_in_band):
            if v and run_start is None:
                run_start = i
            if (not v or i == len(night_in_band) - 1) and run_start is not None:
                run_end = i if not v else i + 1
                run_len = run_end - run_start
                if run_len >= SIGNATURE.min_consecutive_halfhours:
                    run_vals = night_residual[run_start:run_end]
                    mean_v = run_vals.mean()
                    swing = (run_vals.max() - run_vals.min()) / mean_v if mean_v > 0 else np.inf
                    if swing <= SIGNATURE.max_relative_swing_in_run:
                        found_qualifying_run = True
                        break
                run_start = None
        if found_qualifying_run:
            charge_nights.add(nd)

    n_nights_total = len(all_nights)
    n_nights_charge = len(charge_nights)
    overall_frac = n_nights_charge / n_nights_total if n_nights_total else 0.0

    # per-month breakdown
    months: dict[str, list] = {}
    for nd in all_nights:
        key = str(nd)[:7]  # YYYY-MM
        months.setdefault(key, [0, 0])
        months[key][0] += 1
        if nd in charge_nights:
            months[key][1] += 1

    best_month, best_frac, best_n = None, 0.0, 0
    for m, (total, charged) in months.items():
        if total >= SIGNATURE.min_qualifying_month_days:
            frac = charged / total
            if frac > best_frac:
                best_month, best_frac, best_n = m, frac, total

    qualifies = best_frac >= SIGNATURE.majority_night_fraction

    return HouseholdSignatureResult(
        lclid, n_nights_total, n_nights_charge, overall_frac,
        best_month, best_frac, best_n, qualifies,
    )


if __name__ == "__main__":
    # Self-test: alternating charge/no-charge nights, so every 7-day trailing
    # window contains at least one "off" night -- this guarantees genuine
    # baseline contrast and isolates a code-correctness check from the
    # separate, real methodological question (tested against real data,
    # not this fixture) of what happens when charging is night-invariant.
    # NOTE: a fixture where EVERY night charges identically at a constant
    # level would make the rolling-minimum baseline equal the charge level
    # itself, producing a zero residual -- this is a property of the
    # baseload-subtraction method as specified in METHODOLOGY.md 1.2.2, not
    # a bug in this implementation. Flagged in evidence_map.md as a real
    # limitation to check against real data.
    import datetime as dt
    rows = []
    base = dt.datetime(2013, 1, 1, 0, 0)
    for day in range(30):  # >= min_qualifying_month_days (28) so the month check actually engages
        # Charges EVERY night at a near-constant level -- this is the exact
        # case that broke the original per-slot baseload proxy. The revised
        # daytime-window proxy must still detect it, since the daytime
        # readings (0.1 kW fridge floor) never touch the charge band.
        for slot in range(48):
            t = base + dt.timedelta(days=day, minutes=30 * slot)
            hour = t.hour
            if hour >= 23 or hour < 7:
                val = 1.2  # kWh/hh -> 2.4kW, inside 1.8-3.2 band, EVERY night
            else:
                val = 0.1  # fridge-level floor, all daytime hours
            rows.append((t, val))
    fixture = pl.DataFrame({
        "LCLid": ["TEST001"] * len(rows),
        "DateTime": [r[0] for r in rows],
        "KWH_hh": [r[1] for r in rows],
    })
    result = analyze_household(fixture)
    print(result)
    assert result.qualifies, "constant-every-night synthetic fixture should qualify (this is the exact case the daytime-window fix targets)"

    # Second self-test: sustained-but-NOISY overnight load (above the lower
    # bound, but swinging wildly) should NOT qualify -- this is what the
    # steadiness check (added 2026-08-31) is specifically for.
    rows2 = []
    rng = np.random.default_rng(42)
    for day in range(30):
        for slot in range(48):
            t = base + dt.timedelta(days=day, minutes=30 * slot)
            hour = t.hour
            if hour >= 23 or hour < 7:
                val = float(rng.uniform(0.3, 4.5))  # noisy, spans well above 1.8kW but wildly
            else:
                val = 0.1
            rows2.append((t, val))
    fixture2 = pl.DataFrame({
        "LCLid": ["TEST002"] * len(rows2),
        "DateTime": [r[0] for r in rows2],
        "KWH_hh": [r[1] for r in rows2],
    })
    result2 = analyze_household(fixture2)
    print(result2)
    assert not result2.qualifies, "noisy-but-elevated fixture should NOT qualify (steadiness check)"

    print("src/signature_detector.py self-test: PASS")
