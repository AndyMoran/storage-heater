"""
Stage 1: full-population household features from LCL_2013.csv, Jan + July
only, needed to run the S_night detector (evidence_map.md, 2026-08-31,
'Seasonal check' and 'S_night built out as the primary Stage A detector').

Reimplements the documented method (the original session's notebook was
never exported to src/, per evidence_map.md 2026-09-02) rather than
literally reusing src/signature_detector.py, which the log itself says was
abandoned in favour of this approach.

Deliberately pure-Python/NumPy for the CSV scan, not Polars: this device
has 2 vCPU / 3.8GB RAM, and a plain single-pass line scan restricted to
Jan+July rows (skipping the date-parse entirely for the other 10 months via
a cheap string-prefix check before touching the 4443-value row) keeps
memory flat regardless of file size, which a wide-format melt of the full
77M-cell file would not.

Night convention throughout this whole pipeline (matches
config/phase1_config.py's CoarseScreenConfig and src/signature_detector.py
exactly): a period-ending half-hourly reading with hour>=23 or hour<7 is
"overnight". LCL's timestamps are period-ending (confirmed directly: first
row is 2013-01-01 00:30, last is 2014-01-01 00:00), so hour==7 (the
06:30-07:00 reading) is correctly excluded, same as the existing modules.
"""
import csv
import time
import numpy as np

CSV_PATH = "../../LCL_2013.csv"
OUT_PATH = "data/intermediate/phase1_household_features_raw.csv"

t0 = time.time()

with open(CSV_PATH, newline="") as f:
    header_line = f.readline()
    households = header_line.rstrip("\n").split(",")[1:]
    n_hh = len(households)
    print(f"[{time.time()-t0:.1f}s] households: {n_hh}", flush=True)

    # accumulators, indexed by household position
    jan_night_sum = np.zeros(n_hh)
    jan_total_sum = np.zeros(n_hh)
    jan_night_n = np.zeros(n_hh, dtype=np.int64)
    jan_total_n = np.zeros(n_hh, dtype=np.int64)
    jan_max_overnight_kw = np.full(n_hh, -np.inf)

    jul_night_sum = np.zeros(n_hh)
    jul_total_sum = np.zeros(n_hh)
    jul_night_n = np.zeros(n_hh, dtype=np.int64)
    jul_total_n = np.zeros(n_hh, dtype=np.int64)

    n_rows_seen = 0
    n_rows_used = 0
    for line in f:
        n_rows_seen += 1
        # cheap prefix check on the raw line before splitting the
        # 4443-value row at all -- this is what makes the full-year scan
        # fast: the other 10 months never get split() or float()'d.
        is_jan = line[:8] == "2013-01-"
        is_jul = line[:8] == "2013-07-"
        if not (is_jan or is_jul):
            continue
        n_rows_used += 1
        hour = int(line[11:13])
        overnight = hour >= 23 or hour < 7

        parts = line.rstrip("\n").split(",")
        vals = np.empty(n_hh, dtype=np.float64)
        for i, p in enumerate(parts[1:]):
            s = p.strip()
            vals[i] = float(s) if s else np.nan

        valid = ~np.isnan(vals)

        if is_jan:
            jan_total_sum[valid] += vals[valid]
            jan_total_n += valid
            if overnight:
                jan_night_sum[valid] += vals[valid]
                jan_night_n += valid
                kw = vals * 2.0  # kWh/half-hour -> avg kW
                higher = valid & (kw > jan_max_overnight_kw)
                jan_max_overnight_kw[higher] = kw[higher]
        else:  # July
            jul_total_sum[valid] += vals[valid]
            jul_total_n += valid
            if overnight:
                jul_night_sum[valid] += vals[valid]
                jul_night_n += valid

        if n_rows_used % 500 == 0:
            print(f"[{time.time()-t0:.1f}s] rows used so far: {n_rows_used} (seen {n_rows_seen})", flush=True)

print(f"[{time.time()-t0:.1f}s] scan complete. rows seen={n_rows_seen}, rows used (Jan+Jul)={n_rows_used}", flush=True)

# Expected slot counts: Jan=31 days x48=1488, Jul=31 days x48=1488
JAN_EXPECTED = 31 * 48
JUL_EXPECTED = 31 * 48

with open(OUT_PATH, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow([
        "LCLid", "jan_total_n", "jan_night_n", "jan_total_kwh", "jan_night_kwh",
        "jan_max_overnight_kw", "jul_total_n", "jul_night_n", "jul_total_kwh", "jul_night_kwh",
    ])
    for i, hh in enumerate(households):
        w.writerow([
            hh, int(jan_total_n[i]), int(jan_night_n[i]),
            float(jan_total_sum[i]), float(jan_night_sum[i]),
            float(jan_max_overnight_kw[i]) if jan_max_overnight_kw[i] != -np.inf else "",
            int(jul_total_n[i]), int(jul_night_n[i]),
            float(jul_total_sum[i]), float(jul_night_sum[i]),
        ])

print(f"[{time.time()-t0:.1f}s] wrote {OUT_PATH}", flush=True)
print("STAGE1 DONE", flush=True)
