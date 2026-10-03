"""
Stage 2: full-year night_kwh per confirmed household (seasonal + year_round
only -- the 2 flagged households are excluded from here on, same as the
documented method), joined against real daily temperature to compute
heat_loss_proxy v1 (src/overcharge_test.py's exact formula:
max(0, 15.5 - mean_temp_c), no scaling constant).

Second pass over the full CSV, but restricted to only the ~40 confirmed
household columns this time (not all 4443) -- light enough to keep in
memory for the whole year.

Night convention: hour>=23 or hour<7 (period-ending timestamps), same as
Stage 1 and src/signature_detector.py. night_date = the calendar date the
night STARTS on (23:00 reading's own date); a night's kWh is the sum of
that household's half-hourly readings across the whole 23:00-07:00 window.
"""
import csv
import time
import datetime as dt

CSV_PATH = "../../LCL_2013.csv"
REGISTER_PATH = "data/intermediate/phase1_confirmed_households.csv"
WEATHER_PATH = "data/raw_weather/london_weather_2013.csv"
OUT_PATH = "data/intermediate/phase1_household_nights_raw.csv"

BASE_TEMP_C = 15.5

t0 = time.time()

# --- load confirmed households + weather ---
register = {}
with open(REGISTER_PATH) as f:
    for row in csv.DictReader(f):
        register[row["LCLid"]] = row["heating_type"]

confirmed_ids = set(lclid for lclid, ht in register.items() if ht in ("seasonal", "year_round"))
print(f"Confirmed households (seasonal+year_round) to aggregate: {len(confirmed_ids)}", flush=True)

weather = {}
with open(WEATHER_PATH) as f:
    for row in csv.DictReader(f):
        weather[row["date"]] = float(row["temp_c_mean"])
print(f"Weather days loaded: {len(weather)}", flush=True)

# --- second pass: only confirmed household columns ---
with open(CSV_PATH, newline="") as f:
    header_line = f.readline()
    all_households = header_line.rstrip("\n").split(",")[1:]
    col_idx = {hh: i for i, hh in enumerate(all_households) if hh in confirmed_ids}
    missing = confirmed_ids - set(col_idx.keys())
    if missing:
        print(f"WARNING: {len(missing)} confirmed households not found in CSV header: {missing}", flush=True)
    idx_list = sorted(col_idx.values())
    idx_to_lclid = {i: hh for hh, i in col_idx.items()}
    print(f"Column indices resolved: {len(idx_list)}", flush=True)

    # night_kwh[lclid][night_date_str] = running sum
    # night_n[lclid][night_date_str] = count of half-hourly readings actually
    # summed -- used below to drop incomplete nights (both the two boundary
    # nights this file structurally can't complete -- 2012-12-31, which is
    # missing its own 23:00-24:00 half of the window since the file starts
    # 2013-01-01 00:30, and 2013-12-31, which is missing 00:30-06:30 of
    # 2014-01-01 since the file ends there -- and any household-night with
    # too much missing data to trust the sum).
    NIGHT_EXPECTED_SLOTS = 16  # 23:00-07:00 = 8 hours = 16 half-hours
    NIGHT_MIN_VALID_SLOTS = 14  # allow up to 2 missing half-hours, no more
    night_kwh = {hh: {} for hh in col_idx}
    night_valid_n = {hh: {} for hh in col_idx}
    # global (household-independent) count of half-hourly SLOTS this file
    # actually contains for a given night -- all households share one
    # timestamp grid, so this alone identifies the two structurally
    # incomplete boundary nights (2012-12-31, 2013-12-31) regardless of any
    # household's own missing-data pattern.
    night_slot_count = {}

    n_rows = 0
    for line in f:
        n_rows += 1
        hour = int(line[11:13])
        overnight = hour >= 23 or hour < 7
        if not overnight:
            continue
        date_str = line[:10]
        d = dt.date(int(date_str[0:4]), int(date_str[5:7]), int(date_str[8:10]))
        night_date = d if hour >= 23 else (d - dt.timedelta(days=1))
        night_date_str = night_date.isoformat()
        night_slot_count[night_date_str] = night_slot_count.get(night_date_str, 0) + 1

        parts = line.rstrip("\n").split(",")
        for i in idx_list:
            s = parts[1 + i].strip()
            hh = idx_to_lclid[i]
            if not s:
                continue
            night_valid_n[hh][night_date_str] = night_valid_n[hh].get(night_date_str, 0) + 1
            night_kwh[hh][night_date_str] = night_kwh[hh].get(night_date_str, 0.0) + float(s)

        if n_rows % 4000 == 0:
            print(f"[{time.time()-t0:.1f}s] rows processed: {n_rows}", flush=True)

print(f"[{time.time()-t0:.1f}s] full scan complete, rows={n_rows}", flush=True)

# --- write nightly rows joined with weather + heat_loss_proxy v1 ---
n_written = 0
n_no_weather = 0
n_incomplete_night_window = 0  # boundary nights this file structurally can't complete
n_too_much_missing = 0         # household-specific missing-data gaps
with open(OUT_PATH, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["LCLid", "night_date", "night_kwh", "mean_temp_c", "heat_loss_proxy", "heating_type"])
    for hh, nights in night_kwh.items():
        heating_type = register[hh]
        for night_date_str, kwh in sorted(nights.items()):
            if night_slot_count.get(night_date_str, 0) < NIGHT_EXPECTED_SLOTS:
                n_incomplete_night_window += 1
                continue
            if night_valid_n[hh].get(night_date_str, 0) < NIGHT_MIN_VALID_SLOTS:
                n_too_much_missing += 1
                continue
            temp_c = weather.get(night_date_str)
            if temp_c is None:
                n_no_weather += 1
                continue
            heat_loss_proxy = max(0.0, BASE_TEMP_C - temp_c)
            w.writerow([hh, night_date_str, round(kwh, 6), temp_c, round(heat_loss_proxy, 6), heating_type])
            n_written += 1

print(f"[{time.time()-t0:.1f}s] wrote {n_written} household-nights to {OUT_PATH}", flush=True)
print(f"  skipped -- structurally incomplete night window (file boundary): {n_incomplete_night_window}", flush=True)
print(f"  skipped -- too much missing data for this household this night: {n_too_much_missing}", flush=True)
print(f"  skipped -- no matching weather day: {n_no_weather}", flush=True)
print("STAGE2 DONE", flush=True)
