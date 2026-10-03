"""
Stage 1b: build the household register from Stage 1's Jan/July features,
reconstructing the method documented in evidence_map.md (2026-08-31,
'S_night built out as the primary Stage A detector, run against the full
population'). The original notebook that produced this wasn't preserved in
the source bundle (evidence_map.md, 2026-09-02), so this rebuilds it from
the method AND validates the result against the previously-logged numbers
rather than assuming a faithful match.

Method, in the documented order:
1. Restrict to households with "sufficient January data" (reconstructed
   rule, since the exact original threshold wasn't preserved: >=80% of the
   31*48=1488 expected January half-hourly slots present. Documented
   result to compare against: 4,380/4,443 households had "sufficient
   January data").
2. S_night = January overnight kWh / January total kWh.
3. Find the largest gap in the S_night distribution restricted to
   [0.25, 0.85] (avoids the dense low cluster and any degenerate ratios
   near 1.0) -- documented result: gap found at S_night ~0.655 -> ~0.696,
   threshold used = 0.68.
4. Primary gate: S_night > threshold AND jan_max_overnight_kw >= 2.0kW
   (Feature 1 floor, added specifically to exclude near-vacant properties
   whose tiny totals produce a skewed but high ratio).
5. Among gated households: zero-July-consumption -> data_quality flag;
   negligible July data -> insufficient_july_data flag; otherwise
   R_seasonal = (Jan overnight mean kW) / (Jul overnight mean kW) >= 1.8
   -> seasonal, else -> year_round.

Documented result to validate against: 43 households total
(37 seasonal, 4 year_round, 1 data_quality_flag_zero_july,
1 insufficient_july_data).
"""
import csv
import numpy as np

IN_PATH = "/home/claude/phase1_household_features_raw.csv"
OUT_PATH = "/home/claude/phase1_confirmed_households.csv"

JAN_EXPECTED_SLOTS = 31 * 48  # 1488
SUFFICIENT_JAN_FRACTION = 0.80
S_NIGHT_GAP_LOW = 0.25
S_NIGHT_GAP_HIGH = 0.85
JAN_MAX_OVERNIGHT_FLOOR_KW = 2.0
R_SEASONAL_THRESHOLD = 1.8
JUL_INSUFFICIENT_FRACTION = 0.10  # below this fraction of expected July slots -> "insufficient_july_data"

rows = []
with open(IN_PATH) as f:
    r = csv.DictReader(f)
    for row in r:
        rows.append(row)

print(f"Total households in Stage 1 output: {len(rows)}")

# --- Step 1: sufficient January data ---
sufficient = []
for row in rows:
    jan_total_n = int(row["jan_total_n"])
    if jan_total_n >= SUFFICIENT_JAN_FRACTION * JAN_EXPECTED_SLOTS:
        sufficient.append(row)

print(f"Households with sufficient January data (>= {SUFFICIENT_JAN_FRACTION:.0%} of {JAN_EXPECTED_SLOTS} slots): {len(sufficient)}")
print(f"(documented reference figure: 4,380)")

# --- Step 2: S_night, exclude zero-total-January (degenerate ratio) ---
zero_jan_total = 0
s_night_pop = []  # (LCLid, s_night, row)
for row in sufficient:
    jan_total_kwh = float(row["jan_total_kwh"])
    jan_night_kwh = float(row["jan_night_kwh"])
    if jan_total_kwh <= 0:
        zero_jan_total += 1
        continue
    s_night = jan_night_kwh / jan_total_kwh
    s_night_pop.append((row["LCLid"], s_night, row))

print(f"Excluded for zero January total kWh: {zero_jan_total}")
print(f"Population entering S_night gap search: {len(s_night_pop)}")

# --- Step 3: largest gap in S_night distribution within [0.25, 0.85] ---
s_vals = sorted(v for _, v, _ in s_night_pop)
in_range = [v for v in s_vals if S_NIGHT_GAP_LOW <= v <= S_NIGHT_GAP_HIGH]
best_gap = 0.0
best_lo, best_hi = None, None
for a, b in zip(in_range[:-1], in_range[1:]):
    gap = b - a
    if gap > best_gap:
        best_gap = gap
        best_lo, best_hi = a, b

threshold = (best_lo + best_hi) / 2 if best_lo is not None else 0.68
print(f"Largest natural gap in S_night distribution within [{S_NIGHT_GAP_LOW}, {S_NIGHT_GAP_HIGH}]: "
      f"{best_lo:.4f} -> {best_hi:.4f} (gap={best_gap:.4f})")
print(f"Threshold used (midpoint): {threshold:.4f}")
print(f"(documented reference: gap found at ~0.6551 -> ~0.6964, threshold used = 0.68)")

# --- Step 4: primary gate (S_night + Jan-max floor) ---
gated = []
for lclid, s_night, row in s_night_pop:
    jan_max_kw = float(row["jan_max_overnight_kw"]) if row["jan_max_overnight_kw"] != "" else 0.0
    if s_night > threshold and jan_max_kw >= JAN_MAX_OVERNIGHT_FLOOR_KW:
        gated.append((lclid, s_night, jan_max_kw, row))

print(f"\nHouseholds passing primary gate (S_night > {threshold:.4f} AND Jan-max-overnight-kW >= {JAN_MAX_OVERNIGHT_FLOOR_KW}): {len(gated)}")
print(f"(documented reference: 43)")

# --- Step 5: classify ---
JUL_EXPECTED_SLOTS = 31 * 48
register = []
n_seasonal = n_year_round = n_zero_july = n_insufficient_july = 0
for lclid, s_night, jan_max_kw, row in gated:
    jul_total_n = int(row["jul_total_n"])
    jul_total_kwh = float(row["jul_total_kwh"])
    jul_night_kwh = float(row["jul_night_kwh"])
    jul_night_n = int(row["jul_night_n"])
    jan_night_kwh = float(row["jan_night_kwh"])
    jan_night_n = int(row["jan_night_n"])

    if jul_total_n < JUL_INSUFFICIENT_FRACTION * JUL_EXPECTED_SLOTS:
        heating_type = "insufficient_july_data"
        r_seasonal = None
        n_insufficient_july += 1
    elif jul_total_kwh <= 0:
        heating_type = "data_quality_flag_zero_july"
        r_seasonal = None
        n_zero_july += 1
    else:
        jan_overnight_mean_kw = (jan_night_kwh / jan_night_n) * 2.0 if jan_night_n else 0.0
        jul_overnight_mean_kw = (jul_night_kwh / jul_night_n) * 2.0 if jul_night_n else 0.0
        r_seasonal = jan_overnight_mean_kw / jul_overnight_mean_kw if jul_overnight_mean_kw > 0 else float("inf")
        if r_seasonal >= R_SEASONAL_THRESHOLD:
            heating_type = "seasonal"
            n_seasonal += 1
        else:
            heating_type = "year_round"
            n_year_round += 1

    register.append({
        "LCLid": lclid,
        "s_night_jan": round(s_night, 4),
        "jan_max_overnight_kw": round(jan_max_kw, 3),
        "r_seasonal": round(r_seasonal, 4) if r_seasonal is not None and r_seasonal != float("inf") else "",
        "heating_type": heating_type,
    })

print(f"\n=== Final register ===")
print(f"  seasonal: {n_seasonal} (documented reference: 37)")
print(f"  year_round: {n_year_round} (documented reference: 4)")
print(f"  data_quality_flag_zero_july: {n_zero_july} (documented reference: 1)")
print(f"  insufficient_july_data: {n_insufficient_july} (documented reference: 1)")
print(f"  TOTAL: {len(register)} (documented reference: 43)")

with open(OUT_PATH, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["LCLid", "s_night_jan", "jan_max_overnight_kw", "r_seasonal", "heating_type"])
    w.writeheader()
    for r in register:
        w.writerow(r)

print(f"\nWrote {OUT_PATH}")
