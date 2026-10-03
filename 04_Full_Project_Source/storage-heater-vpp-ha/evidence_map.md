# evidence_map.md — storage-heater-vpp-ha

Running log of every verification pass, accepted/rejected external claim, and material decision, per PROJECT.md §18. Newest entries at the bottom.

---

## 2026-08-31 — Phase 1 kickoff: data source verification (PROJECT.md §2.10, Verify the Verifier)

**Claim being checked:** PROJECT.md §9.3 names the Low Carbon London (LCL) dataset as the primary source, citing `data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households`. Before writing any ingestion code, checked whether this project's sandboxed tooling can actually reach that data.

**Finding: it cannot, directly.** The execution environment's outbound network is allow-listed to package registries and GitHub only (pypi.org, npmjs.com, github.com, api.github.com, etc.). `data.london.gov.uk`, the UK Data Service (`ukdataservice.ac.uk`), and `data.4tu.nl` are not on that list. Confirmed by attempting a fetch — request is rejected at the network boundary, not by the destination.

**Leads checked (bucket 1–4 per §14 triage):**

1. `github.com/groupoasys/Data_Low_Carbon_London` — presents as a GitHub-hosted copy (168 CSVs, matching the real schema: `LCLid`, `stdorToU`, `DateTime`, `KWH/hh`, `Acorn`, `Acorn_grouped`). **Checked directly (partial clone, no blobs) rather than trusted from the search snippet.** The repo's own `Power_Networks_LCL/Readme.md` states the data was never actually uploaded ("impossible for me to upload the files... you can download it in the following link") and points back to `data.london.gov.uk`. **Bucket 4 — dead end, logged so it isn't re-tried.**
2. `github.com/JerryGreenough/...`, `github.com/building-energy/low-carbon-london-data` — both are analysis/methodology repos referencing the same `data.london.gov.uk` source, not data hosts. Not cloned (no indication either bundles the CSVs) — **not yet verified either way; leave as an untried lead if the primary route fails.**
3. `data.4tu.nl` (Tindemans, 2023, *Low Carbon London smart meter data (refactored)*, DOI 10.4121/fbbe775b-48d8-469f-a39b-b64488bfd6fd) — a real, citable, versioned secondary release: 4,443 households, Std-tariff only, 2013 only, single 137MB zip. **Credible bucket-1-if-reachable candidate** — properly attributed, filtered in a documented way (Std-only, which is actually closer to our target population than the raw file, since the ToU trial group's behaviour was deliberately perturbed by dynamic pricing). Not reachable from this sandbox (`data.4tu.nl` not allow-listed).
4. UK Data Service R script (`ukdataservice/smartmeter`) — pulls from `files.datapress.com`, also not allow-listed.

**Decision:** Do not fabricate or approximate this dataset. Per Golden Heuristic 2.8, a blocked input is reported as what it is, not worked around with a smaller, unstated substitute. Two real unblock paths exist (see next entry) and the choice belongs to the project owner, not to an assumption made here.

**What was NOT done as a result:** no disaggregation code, no NILM detector, no overcharge/exhaustion quantification. Per Forbidden Shortcuts (§12), none of that runs meaningfully — or at all — before Stage A's empirical register exists.

**What WAS done in the meantime (does not require real data):** project scaffold, `uv`-locked environment (Polars/NumPy/SciPy/Matplotlib per §4), `config/phase1_config.py` with every Methodology §1.1–1.4 constant named and flagged with its assumption status, `src/schema.py` (schema validation + gap detection + value sanity checks), self-tested against a small fabricated fixture that is explicitly labelled as a code-correctness check and never treated as, or mixed with, a Phase 1 finding.

---

## 2026-08-31 — Why is UK data on a Dutch repository? (user question, checked rather than assumed)

**Claim being checked:** the 4TU.ResearchData release (DOI 10.4121/fbbe775b-48d8-469f-a39b-b64488bfd6fd) is credible provenance for LCL data, despite sitting on a Netherlands-based repository.

**Checked:** Simon H. Tindemans's TU Delft research-portal profile. Confirmed:
- He is Associate Professor, Intelligent Electrical Power Grids group, TU Delft — 4TU.ResearchData is TU Delft's own institutional repository, which explains the host, independent of the data's UK origin (4TU is a general-purpose repository for the four Dutch technical universities; it is not restricted to Dutch-origin data).
- His TU Delft research-portal record lists a second, earlier deposit: **Schofield, J., Carmichael, R., Tindemans, S. H., Bilton, M., Woolf, M. & Strbac, G. — UK Data Service, 14 Jan 2016** — i.e. Tindemans appears as a named contributor on an *earlier, UK-hosted* LCL-related data release, alongside the Imperial College London / UK Power Networks team associated with the original trial. This is consistent with him having worked on the original project (plausibly at Imperial, before his current TU Delft post) rather than being an unconnected third party who picked up a public file and re-hosted it.

**Conclusion:** the Dutch host is an artifact of where the depositor now works, not a break in the chain of custody — he has a documented, findable connection to the original LCL data release, not just to the refactored copy. This is a stronger primary-adjacent source than an anonymous re-upload would be, and is treated as such (bucket 1, §14). Still: the refactored file's exact filtering logic should be re-read from the 4TU dataset page/documentation once obtained, not assumed from the search snippet already logged above.

---

## 2026-08-31 — Data acquired: integrity verified

User downloaded `LCL_2013_kWh_csv.zip` directly from the 4TU dataset page and uploaded it. Checked before treating it as ground truth (§2.10):

- **Size:** 137,223,875 bytes — exact match to the size logged from the 4TU page metadata above.
- **MD5:** `2a4bde340f2ee2a8aa9813debb9da363` — exact match to the MD5 logged from the 4TU page metadata above.

Both match exactly. This is confirmed to be the unaltered, cited release — not a corrupted transfer or a different/tampered file. Blocker from the first entry above is now cleared. Proceeding to Stage A (schema check against the actual file, since it is the *refactored* release and may not match `src/schema.py`'s `RAW_SCHEMA`, which was written against the original London Datastore column names).

---

## 2026-08-31 — Stage A: actual schema differs from PROJECT.md §9.3's description (as flagged in advance)

**Checked, not assumed** (§2.10): opened the real file rather than trusting PROJECT.md §9.3's description of the raw London Datastore layout.

**Finding:** the file is **wide format**, not the long format (`LCLid`, `stdorToU`, `DateTime`, `KWH/hh`, `Acorn`, `Acorn_grouped`) that PROJECT.md §9.3 describes for the raw London Datastore release. Actual structure: one `DateTime` column + 4,443 household columns (`MAC000002` … `MAC005567`), one row per half-hour timestamp, cell values are that household's kWh reading. **No `Acorn`, `Acorn_grouped`, or `stdorToU` columns exist in this file at all.** Household count (4,443) matches the 4TU page's stated figure exactly, confirming this is genuinely the Std-tariff-filtered refactor, not a different or corrupted release — but the tariff filter was applied *before* this file was produced, so there is no per-row field left to independently re-verify it from the file itself; that check would require the original London Datastore file, not this one.

**Consequence:** `src/schema.py`'s `RAW_SCHEMA` (written before this file arrived) was wrong for the actual artifact. Rewritten against the real structure. Also: "gap detection" as METHODOLOGY.md §1.1 describes it (missing timestamps *per household*) doesn't apply here — the timestamp grid is shared and complete (see next entry) — so the equivalent per-household integrity check here is missing-*value* fraction within an otherwise-complete grid, not missing-*row* detection. This is a real deviation from the written methodology's assumed data shape, logged rather than silently reinterpreted.

**Ingestion note:** the wide 560MB CSV could not be pivoted to long format in one pass on this machine (3.9GB RAM total, ~3.5GB free) — two attempts (whole-frame lazy transform, then a full-width streaming unpivot) both hit OOM. Resolved by batching: 23 batches of ~200 household columns each, relying on Polars' projection pushdown to only parse the needed columns per pass, each batch written to its own parquet part, then concatenated. Total time 46.6s. Output: `data/intermediate/lcl_2013_long.parquet` (136MB, 77,841,360 rows = 4,443 households × 17,520 half-hours, confirmed exact).

## 2026-08-31 — Stage A: timestamp grid and value sanity checks (real data)

- **Timestamp grid:** 17,520 distinct half-hour steps, 2013-01-01 00:30 → 2014-01-01 00:00, every step exactly 1,800 seconds apart. No gaps, no irregular steps. Matches the 4TU page's stated coverage exactly.
- **Values:** min 0.0, max 10.761 kWh/hh, zero negative readings. Comfortably inside `KWH_HH_PLAUSIBLE_MAX = 20.0`.
- **Missingness:** 3,696,925 / 77,841,360 cells null (4.75%). 409 households have >5% missing readings. **194 households are 100% null** (present as a column, zero real readings) — these are flagged, not dropped and not interpolated, per METHODOLOGY.md §1.1's explicit instruction. They will fall out of the coarse screen naturally (no data to compute an overnight mean from) but are recorded here so their exclusion is traceable rather than silent.

## 2026-08-31 — Coarse screen (METHODOLOGY.md 1.2.1)

Filter: overnight (23:00–07:00) mean kW > 1.5 AND overnight/daytime mean-kW ratio > 1.0. The absolute threshold is METHODOLOGY.md's own example value (§9.5 item 2, untested). The ratio cutoff of 1.0 is a decision made here, not specified in METHODOLOGY.md — chosen as the simplest, most auditable interpretation of "unusually high relative to the whole panel" (a household drawing more power overnight than during the day is itself unusual for ordinary consumption), rather than a population-percentile cutoff, which would make the threshold circular against the very population being screened. Logged as an assumption, not a derived result.

**Result: 42 of 4,411 households with any data pass the coarse screen (~1.0%).** Flagged, not yet interpreted — a low hit rate is consistent with either (a) low genuine storage-heater/Economy-7 prevalence in this sample (plausible: this is a Greater London sample, and London's housing stock leans gas-heated relative to the UK average, so a below-national-average storage-heater share would not be surprising) or (b) the coarse screen being too strict. The pre-mortem check (next entry) is the way to tell these apart, not further threshold-tuning.

## 2026-08-31 — Pre-mortem visual check (METHODOLOGY.md 1.2, done BEFORE writing any detector)

Plotted 15 of the 42 coarse-screen-flagged households (top 5, middle 5, bottom 5 by overnight-kW, to sample across the flagged range rather than just the strongest hits), half-hourly kW, 7–16 Jan 2013, with the 23:00–07:00 window shaded. Saved to `data/intermediate/premortem_traces.png`.

**Finding — genuinely mixed, and worth reporting honestly rather than rounding to "it works":**

- **Clean, textbook storage-heater square-wave signature** (steady plateau load confined almost entirely to the shaded overnight window, dropping to near-zero by day, repeating night after night): MAC003218, MAC005198, MAC004863, MAC005041, MAC005009, MAC004902, MAC000415, MAC005216, MAC004983 — 9 of 15. This is the pattern Andy's outline and METHODOLOGY.md §9.5 item 2 predicted, and it is visually unambiguous in these traces — the Sledgehammer Test's core premise holds for this subset.
- **Not a clean storage-heater signature** — spiky, irregular loads with no discrete on/off block (MAC000153, MAC000321, MAC004858), or a near-constant load with no day/night contrast at all (MAC003749, flat ~2kW around the clock — exactly the false-positive risk PROJECT.md §9.9 item 1 names: a load that isn't a storage heater but still trips an overnight-mean threshold, e.g. an immersion heater or continuously-running appliance), or ambiguous/noisy block shapes that don't cleanly separate from daytime activity (MAC005335, MAC001978): 6 of 15.

**Conclusion for next step:** the coarse screen is not clean on its own — roughly 40% of this sample would be false positives if the coarse screen alone were treated as "confirmed storage heater." This is exactly why METHODOLOGY.md §1.2.2's signature confirmation (baseload subtraction, charge-band check, majority-of-nights consistency) is a required second pass, not a formality — proceeding straight from coarse screen to Phase 1's headline finding would overstate prevalence. Not a null result (§2.8) — the pattern is real and strong where it appears — but confirms the two-pass design in the methodology is doing necessary work, and sets an expectation that the confirmed-household count after §1.2.2 will land below 42, not at 42.

---

## 2026-08-31 — Resolving Open Question 9.8.2: does a post-2020 comparable dataset exist?

PROJECT.md §9.8 item 2 flagged this as unresolved at spec-writing time. Checked now rather than left open indefinitely.

**Finding: yes, and it's better than LCL on almost every substantive axis — but effectively inaccessible for this project.** The Smart Energy Research Lab (SERL) Observatory dataset: 13,000+ GB-representative households (not just London), half-hourly electricity *and gas*, current through at least June 2024 (7th edition), and — critically for Phase 1's core problem — linked EPC (Energy Performance Certificate) data, which plausibly includes actual heating-system-type fields. If so, that would let Phase 1 skip disaggregation-by-load-shape entirely for an EPC-confirmed subsample. **Checked access terms directly rather than assuming "open data" from the description:** SERL granular data is UKDS Secure Lab only — "data accessed in this way cannot be downloaded," restricted to accredited UK researchers with Digital Economy Act Accredited Researcher status, institutional ethics approval, and Safe Researcher training. Not a realistic near-term path for this project. A lower-barrier aggregated statistical release (SERL Stats Report Volume 2, ~110k rows, simple end-user UKDS license, no accreditation) exists but is pre-aggregated, not household-level traces — usable only as an external prevalence benchmark, not as Phase 1's primary data.

**Other alternatives surfaced, not pursued further today:**
- **Full original LCL** (data.london.gov.uk, 5,567 households including the ToU trial group, ACORN-tagged, Nov 2011–Feb 2014) — same underlying trial as the file already in hand, openly downloadable in principle, but same network wall as before (not fetchable from this sandbox) and materially larger (~783MB zip / ~10GB unzipped) than what was practical to upload this session. Real upgrade if ACORN demographic slicing or the extra two months matter later; not pursued now since it wasn't necessary to unblock Phase 1's core method.
- **UK-DALE** (5 homes, appliance-level ground truth, 16kHz) — too small to be a primary source, but a good candidate for exactly the validation step METHODOLOGY.md §1.2 asks for ("cross-check a subsample against any household survey/appliance-ownership metadata, if available") — flagged for later, not fetched yet.
- **SSEN/UKPN DNO open data portals** (2023–2024, LV feeder/substation level) — wrong granularity for Phase 1 (aggregated across ≥5 meters, not per-household), but directly relevant to Phase 4/5's DNO headroom and local-flexibility checks (PROJECT.md §9.3) — noted for that phase, not this one.

**Decision:** proceed Phase 1 on the current 4TU file. It is the best dataset that is both real and actually obtainable at this project's current access level — not the best dataset that exists in principle.

## 2026-08-31 — Original London Datastore page fetched directly (user-provided URL, confirms and extends earlier lead)

User supplied `data.london.gov.uk/dataset/smartmeter-energy-consumption-data-in-london-households-vqm0d` — same underlying UK Power Networks dataset found earlier under a different URL slug (the site has since re-slugged; confirmed via matching title, author, household count, and description). Fetched directly rather than assumed identical.

**New facts confirmed from the primary page itself (supersede earlier ballpark figures):**
- Full CSV zip: 764.54 MB exactly (`LCL-FullData.zip`). Partitioned (168-file) zip: 758.86 MB exactly.
- Non-ToU ("Std") households' actual 2013 flat tariff: **14.228 pence/kWh**, stated directly — not an estimate.
- A separate `Tariffs.xlsx` (239.63 kB) ships with this release, containing the real 2013 dynamic-price (High/Low/Normal) schedule and timing — relevant to Phase 2's compliance simulation and to any Phase 1 cross-check of the trial's own pricing, not previously known to be a distinct file.
- License: CC BY 4.0, explicitly stated.
- Confirms the population split already logged: ~4,500 flat-rate + ~1,100 dynamic-price (ToU) trial households = 5,567 total, Nov 2011–Feb 2014.

**No change to Phase 1's standing result** — the coarse screen and pre-mortem check were already run against genuine Std-tariff households (4TU's filtering to non-ToU only, done upstream). The ToU trial group is a deliberately price-perturbed population and arguably less representative of *ordinary* storage-heater behaviour, which is what Phase 1 needs — so excluding it was a defensible modelling choice, not just a size-convenience one. Logged for future reference if a later phase wants the ToU group, the extra ~2 months, or the real tariff schedule.

## 2026-08-31 — Signature-confirmation detector (METHODOLOGY.md §1.2.2): a real limitation surfaced while self-testing

While writing the self-test for `src/signature_detector.py`, a synthetic fixture with an *identical, invariant charge level every single night* produced zero detected charge-events — not a code bug, but a property of the baseload-subtraction method itself: a rolling 7-day trailing minimum, evaluated at a household that charges the same amount every night without variation, equals the charge level itself, so the residual is zero and nothing looks like a signal.

**Why this matters and why it's flagged rather than quietly patched:** PROJECT.md's own thesis is that unmanaged storage heaters *overcharge on mild nights same as cold ones* — i.e. the failure mode this project is trying to prove is exactly the low-variability charging pattern this detection method would under-detect. This is a genuine tension between METHODOLOGY.md §1.2.2 as written and PROJECT.md's core thesis, not something to paper over. It is only a risk for households whose charging is *very* consistent night-to-night; households with any real night-to-night variation (weather-driven charge duration, meter noise, occasional non-charge nights) are unaffected, and the real data checked below does show that variation. Logged so that if the confirmed-household count looks suspiciously low, this is the first place to look, and so it's on record as a known edge case rather than a surprise found later.

Self-test rebuilt with an alternating charge/no-charge pattern (guarantees genuine baseline contrast within every 7-day window) rather than a constant one, specifically to isolate code-correctness from this separate methodological question. Passes.

## 2026-08-31 — Signature detector run on real data: confirms the predicted failure, v1 abandoned

Ran the detector exactly as METHODOLOGY.md §1.2.2 specifies (per-slot rolling 7-day trailing minimum) against the 42 coarse-screen-flagged households. Result: **only 1 of the 9 households visually rated "clean" in the pre-mortem check passed, while 2 of the 6 rated "not clean" passed** — close to inverted agreement with direct visual inspection, not noise. Diagnosed on MAC004863 (visually one of the cleanest signatures): plotted raw / baseload-proxy / residual side by side (`data/intermediate/diagnostic_MAC004863.png`). The baseload-proxy panel is visibly a near-exact copy of the household's own overnight charge block, not background noise — confirms the predicted failure mode exactly: this household charges at a near-constant ~4.8kW every night, so the same-slot 7-day trailing minimum converges to the charge level itself, leaving almost no residual.

**Fix implemented:** `_baseload_proxy_daytime` (new function in `src/signature_detector.py`) draws the baseline from a 10:00–16:00 daytime reference window instead of the same overnight slot being tested — structurally immune to contamination by the household's own heater signal, since that window doesn't overlap the charge-detection window (23:00–07:00) or the boost-detection window (16:00–20:00, METHODOLOGY.md §1.3). This is a deviation from METHODOLOGY.md §1.2.2's literal text, made because the literal version was tested against real data and demonstrably failed, not preferred on aesthetic grounds. `_baseload_proxy` (original) kept in the file for reference, not deleted, per §17 (never overwrite a working/frozen approach without keeping the prior version visible).

**Re-run with the fix:** 21/42 households now qualify (up from 7/42). Visual agreement improved but is still far from clean: 2/9 visually-clean pass, 3/6 visually-not-clean pass. Investigated the most surprising flip (MAC003218, passed under v1, visually clean, fails under v2) rather than accepting the number and moving on: `data/intermediate/diagnostic_MAC003218_v2.png` shows the v2 baseload proxy is behaving correctly (stays low, ~0.2–0.5kW, genuinely off the household's own signal) — but MAC003218's overnight charge block runs **10–13kW**, far above the 1.8–3.2kW charge band (METHODOLOGY.md's own illustrative example, flagged UNTESTED in `config/phase1_config.py` from the start). This isn't a baseline-estimation bug — it's a second, independent problem: **the fixed charge band is too narrow for the real range of overnight demand in this population.** Checked the distribution across all 42 coarse-screen-flagged households: overnight mean kW ranges from 1.51 to 9.38 (mean 2.26, median 1.93) — the band captures the bulk of the distribution but excludes real outliers on the high end, plausibly multi-heater households or larger systems, not obviously non-storage-heater loads.

**Not yet resolved — flagged for the next step rather than patched unilaterally a second time in the same pass (per §2.8: don't keep re-tuning until the answer looks right without stopping to think).** Two known, well-diagnosed problems now stand between the current 21/42 figure and a number worth reporting as Phase 1's finding: (1) the charge-band upper bound may need to be loosened, made per-household-adaptive, or dropped in favour of a lower-bound-only test; (2) visual agreement, even after the baseline fix, remains poor enough that the visual pre-mortem sample itself, the charge-band definition, or both need re-examination before either is treated as a check on the other.

## 2026-08-31 — Charge band fixed per user's domain knowledge; steadiness gap surfaces and is falsified

User's estimate: a typical UK 2-bed property runs ~5 storage heaters. Checked against real market data (Eco Experts, EDF, storageheaters.com, MPC Energy, MoneySavingExpert forum): common unit ratings run ~0.85-3.4kW, with 1.7kW/2.55kW/3.4kW being standard sizes. Five units at 1.7-2.55kW each puts simultaneous household draw at ~8.5-13kW — matches MAC003218's observed 10-13kW block almost exactly. Confirms the original 3.2kW upper cap assumed one heater, not a household.

**Fix:** dropped the upper bound entirely (`charge_band_high_kw` deprecated in `config/phase1_config.py`, kept for traceability, not deleted). Re-ran: **42/42 households now qualify — zero discrimination.** This is itself informative, not a result to accept: removing the cap also silently removed the only thing checking for a *steady* plateau, so any sustained elevated reading now passes regardless of shape.

**Attempted second fix:** added an explicit steadiness check — (max-min)/mean within a candidate charge run must be ≤ 0.4 (guessed threshold, flagged untested). Re-ran: 16/42 qualify, but agreement with the visual pre-mortem sample got *worse* (1/9 clean pass), and MAC003218 — independently confirmed via diagnostic plot to be a genuine, strong household signature — dropped to a 0.0 charge-night fraction.

**Falsified rather than accepted:** measured the actual relative swing within confirmed-good nights for MAC004863 and MAC003218 directly (not guessed): median 0.52 and 0.79 respectively, individual nights up to 1.11. The 0.4 threshold was wrong by a wide margin — real storage-heater charging is genuinely noisy within a night (plausibly from multiple heaters cycling independently), and the "steady rectangular block" read from the zoomed-out multi-day pre-mortem chart doesn't hold at half-hour resolution. This also means the 15-household visual pre-mortem sample is not a reliable calibration target at this resolution — three tuning rounds against it produced three different failure modes, which is the pattern §2.8 warns against, not genuine convergence.

**Decision point put to the user rather than continuing to guess a fourth threshold.** Chose: get a real validation set (UK-DALE) before refining further.

## 2026-08-31 — UK-DALE checked directly: does not contain what was needed

Before downloading anything, checked what UK-DALE's 5 houses actually contain, via the metadata repo `github.com/JackKelly/UK-DALE_metadata` (reachable directly, unlike the actual 3.5GB dataset which is hosted at UKERC EDC/CEDA, not on an allow-listed domain).

**Finding: none of the 5 UK-DALE houses has an Economy-7 storage heater.** Searched all five `buildingN.yaml` files for heater-related appliances:
- House 1: an "immersion heater" — but `meters: [0]` (unmetered) and explicitly documented as "never been used." Zero usable signal.
- House 2, House 4: no heater-type appliance at all.
- House 3: an `electric_heater` → type "electric space heater," genuinely separately metered (`meters: [3]`). The closest available analog, but a different appliance class from a storage heater — a plug-in space heater cycles on/off via its own thermostat through the day, not on an off-peak timer overnight — and covers only ~6 weeks (27 Feb–8 Apr 2013).
- House 5: no heater (a "network attached storage" device matched the keyword search, not relevant).

**This closes off the planned path, not just delays it.** Even the closest match (House 3) isn't the appliance type Phase 1 needs to validate against, and the underlying data file still isn't reachable from this sandbox regardless (UKERC EDC, not GitHub). Reported back to the user before spending effort fetching a partial file that wouldn't answer the original question.

## 2026-08-31 — Second lead checked: DECC/BEIS Household Electricity Survey (HES) — named explicitly in METHODOLOGY.md §1.2 as a validation candidate

Checked before giving up on finding real ground truth. HES (250 owner-occupied English homes, 2010-2011, appliance-level submetering at distribution-board and individual-appliance level, 10-min/2-min resolution) **does genuinely cover storage heaters** — an independent analysis of the HES data (ResearchGate, "What Can We Learn from the Household Electricity Survey?") reports a statistically significant summer/winter base-load difference specifically for "space heating (mostly night-time storage heaters)" (p=0.04). Unlike UK-DALE, this is a real match for the appliance type Phase 1 needs.

**Access reality, checked directly on the UKERC EDC listing page rather than assumed:** the freely-available portion (no registration) is aggregated statistical output — Excel-format summary reports and spreadsheet tools (`gov.uk/government/collections/household-electricity-survey`), not raw per-household appliance time series. Useful as an external plausibility benchmark for a prevalence figure (a related 2021 BEIS Energy Follow-Up Survey reports ~7% of English households using electric storage heaters or room heaters) but not for calibrating a detector against real load shapes. The raw appliance-level data that would actually help is UK Data Service Study 7874 — requires UKDS registration and project assignment. A real barrier, but a materially lighter one than SERL's Secure Lab/accreditation requirement; not pursued today, flagged as an actionable option if the user wants to take it further.

## 2026-08-31 — Seasonal check (user's idea) leads to the best discriminator found tonight

User's insight: storage heaters have a hard physical tell that a per-night residual test doesn't exploit — they should show a seasonal on/off pattern (temperature-driven), or in the "always left on" case, a flat high level across seasons that is itself the clearest possible illustration of PROJECT.md's overcharging thesis. Proposed a 3-feature matrix: (1) max overnight kW in January (physical floor), (2) January/July overnight-mean ratio ("R_seasonal", seasonal check), (3) night energy as a share of total January energy ("S_night", diurnal concentration).

**Checked computationally against the 42 coarse-screen-flagged households rather than accepted on the reasoning alone** (per this session's repeated lesson: physically-reasonable thresholds have not survived contact with real data tonight).

- **Feature 3 (S_night) is the strongest discriminator found in this entire session.** All 9 visually-clean households (pre-mortem sample): 0.71–0.85. All 6 visually-not-clean households: 0.36–0.45. Zero overlap. Cleaner separation than any version of the residual/steadiness detector produced.
- **Feature 2 (R_seasonal) as originally specified has a division bug and a conceptual gap.** MAC005263's ratio computed to ~3,041,278 — not an outlier signal, a `÷≈0` artifact: July sums to exactly 0.0 kWh across 1,488 valid readings, more likely a vacancy/meter-fault/dropout than genuine "off for summer" and needs flagging as a data-quality case, not fed through the ratio. Separately: MAC004863 (independently diagnostic-confirmed as a genuine strong signature earlier this session) has R_seasonal ≈ 1.03 — January 4.506kW, July 4.365kW, essentially no seasonal difference. A strict R_seasonal≥1.8 gate would have wrongly excluded it. This matches the user's own "leave it on at all times" observation exactly — treated as a real household sub-type (year-round chargers), not noise to threshold away.
- **Feature 1 (max overnight kW, Jan) adds no discrimination on this population** — all 42 already clear a 2.0kW floor, unsurprising since the coarse screen already selected for elevated overnight demand. Likely more useful applied to the full 4,411-household population before the coarse screen, not after.

**Revised design, replacing the residual/steadiness detector line of work:** S_night as the primary confirming signal (threshold to be set in the clear 0.45–0.71 gap, e.g. ~0.55–0.60), R_seasonal used to classify confirmed households into seasonal-responsive vs. year-round types rather than as a pass/fail gate, with an explicit floor on the denominator (or absolute-zero-month flag) before computing any ratio, and Feature 1 kept as a sanity floor rather than a discriminator.

## 2026-08-31 — S_night built out as the primary Stage A detector, run against the full population

**Full-population check, not just the 42.** Computed S_night (Jan) for all 4,443 households (4,380 with sufficient January data after excluding 4 zero-total-kWh data-quality cases). Population median S_night ≈ 0.20 (std 0.098) — ordinary households cluster tightly low, as expected. Rather than pick a threshold from the small 15-household visual sample, searched for the largest natural gap in the full distribution between 0.25 and 0.85: found at **S_night = 0.6551 → 0.6964**, a real, data-driven break, not a guess. `data/intermediate/s_night_full_population_histogram.png`.

**Cross-check against the visual pre-mortem sample (independent, not tuned to match it):** using threshold 0.68, **all 6 visually-not-clean households drop out, all 9 visually-clean households are retained** — a clean, non-circular validation, since the threshold came from the full population's own distribution, not from tuning against this 15-household sample.

**Cross-check against the original coarse screen:** only 26/42 overlap. 16 of the original 42 are dropped (and these are exactly the households that don't show real diurnal concentration — includes all 6 visually-messy cases). 19 new households are added — plausibly households with a real day/night split at a lower absolute power level than the original mean-based screen's 1.5kW floor could catch.

**A real failure caught before finalizing:** two households (MAC002771, MAC004735) had S_night ≈ 0.97–1.0 but January max overnight draw of only 0.42kW and 0.12kW respectively — near-vacant/negligible-consumption properties where a tiny, noisy total gets a skewed *ratio* with no real signal behind it. This is exactly the case Feature 1 (magnitude floor) was proposed to catch, and confirms it's a necessary companion to S_night, not a redundant check once S_night is applied to the *full* population rather than the pre-screened 42 (where the original coarse screen's own 1.5kW mean floor had already implicitly excluded this failure mode). Added a 2.0kW January-max floor; both households excluded.

**Final Stage A signature-confirmation register (`data/intermediate/phase1_confirmed_households.parquet`): 43 households.**
- 37 classified `seasonal` (R_seasonal ≥ 1.8 — genuine winter/summer swing)
- 4 classified `year_round` (includes MAC004863, independently diagnostic-confirmed earlier this session — matches the user's "leave it on at all times" observation exactly)
- 1 `data_quality_flag_zero_july` (genuinely zero July consumption — flagged for manual review, not classified either way)
- 1 `insufficient_july_data` (MAC003218 — confirmed dropped out of the panel before July, consistent with the earlier finding that its data only spans Jan–Apr)

This register is the Stage A deliverable and is what Stage B (quantifying the overcharge and afternoon-exhaustion gap, METHODOLOGY.md §1.3) should consume. It replaces the abandoned residual/steadiness detector line of work entirely — the seasonal approach, initiated from the user's own domain insight, produced a cleaner, more physically grounded, and independently-validated result than four rounds of tuning the per-night method ever did.

## 2026-08-31 — Stage B blocked on the same kind of issue as Stage A: weather data not fetchable from this sandbox

Read METHODOLOGY.md §1.3 directly before starting Stage B rather than working from memory of an earlier read. The overcharge test needs `mean_daily_temp` for London, 2013, at daily resolution, for the degree-day proxy (`heat_loss_proxy = max(0, base_temp - mean_daily_temp) * a_constant`). PROJECT.md §9.8 already vetted Open-Meteo as the source ("confirmed real, free, open-source weather API... no key required").

**Checked three paths, all blocked for different reasons, before asking the user to fetch anything:**
1. Open-Meteo's `/v1/archive` endpoint — confirmed the exact parameters from its own docs page, but a direct fetch returns `ROBOTS_DISALLOWED` — the site's robots.txt blocks automated tooling, not a human opening the URL in a browser.
2. UK Met Office free public archive (e.g. Heathrow station data) — confirmed by reading the actual file content: monthly resolution only (year, month, mean tmax, mean tmin), not daily. Insufficient for a per-night test.
3. GitHub-hosted ERA5 tooling — several repos exist, but all require a Copernicus CDS API key to actually pull data; nothing is a plain pre-downloaded file on an allow-listed host.

**Resolution:** same pattern as the LCL dataset itself — ask the user to fetch and upload, but far lighter this time (a single small CSV, 365 rows, no registration, no account). Exact URL handed to the user:
`https://archive-api.open-meteo.com/v1/archive?latitude=51.5074&longitude=-0.1278&start_date=2013-01-01&end_date=2013-12-31&daily=temperature_2m_mean&timezone=Europe%2FLondon&format=csv`

User uploaded `open-meteo-51_49N0_16W16m.csv` — 365 rows, London (51.49°N, -0.16°W, 16m elevation), daily mean temperature, 2013-01-01 to 2013-12-31, clean structure (3 metadata lines, then a header, then data). Confirmed usable directly. Sanity-checked against known history: coldest days land 16-17 Jan 2013 (-2.2°C, matches the documented January 2013 UK cold spell) and warmest in late July (23.8°C, consistent with the well-documented 2013 UK heatwave). Real data, not corrupted or mislabelled.

## 2026-09-01 — Stage B: overcharge test built and validated against real temperature data

**Sanity check before committing to a design.** Plotted night charge vs. heat-loss proxy for 4 confirmed households (3 seasonal, 1 year-round) before writing any calibration code. Result: clean hockey-stick shapes for the seasonal households (flat near-zero above 15.5°C, rising steadily below it — exactly METHODOLOGY.md's assumed functional form) and a flat cloud with zero temperature response for the year-round household (MAC004863) — a direct visual confirmation of the "leave it on at all times" pattern first identified via R_seasonal. Critically, the *slopes* differed substantially across the three seasonal households (highest ~2.9 kWh/degree-day, lowest ~1.1) — ruling out a single shared `a_constant` (`config/phase1_config.py`'s original placeholder) as too crude for a population with materially different heater counts per property.

**Design adopted:** each `seasonal` household gets its own OLS-fitted response line (`night_kwh ~ intercept + slope × heat_loss_proxy`, `src/overcharge_test.py`) across its full year of nights. A night is flagged overcharged where actual charge exceeds that household's *own* fitted line by more than 25% (untested margin, flagged as a first-pass choice). This is deliberately an outlier test relative to each household's own typical response, not a claim about the true physical heat requirement of any specific property — worth keeping that framing precise when this gets reported.

**Fit quality across the 37 seasonal households:** median R²=0.70, ranging from 0.14 (MAC005234 — weak, flag this household's overcharge results as less trustworthy) up to 0.86. Most fit well; a handful don't, and are named explicitly rather than silently included with equal confidence.

**`year_round` households (4 of them) get a different, simpler test:** on any night warmer than 15.5°C there is no legitimate heat-loss justification for material charge at all, so charge above a 2.0kWh baseline (untested, chosen from the visual mild-night floor of seasonal households) on a mild night counts as overcharge by construction. This test is deliberately silent on cold nights for this group — there's no way to tell from this method whether a non-responsive household's cold-night charge is "right," only that its mild-night charge clearly isn't needed.

**Results, visually validated (not just computed) before trusting:** plotted flagged nights directly on top of the raw scatter for both a seasonal example (MAC004954, R²=0.84) and the year-round example. Flags land exactly where expected — clustered above the fitted line, concentrated at the mild end for the seasonal case; clustered past 15.5°C for the year-round case. `data/intermediate/overcharge_test_validation.png`.

- **Seasonal households:** 3,492 / 13,467 household-nights (25.9%) flagged overcharged. Total excess: 22,249 kWh across the year across all 37 households on flagged nights.
- **Year-round households:** 306 / 312 mild nights (98%) flagged overcharged — but this is only 4 households, and shouldn't be generalised beyond this small sample without more data. Total excess: 3,389 kWh from mild-night charging alone.

**Output:** `data/intermediate/phase1_household_nights.parquet` — one row per confirmed household-night with charge, temperature, modelled requirement, overcharge flag/magnitude. This is half of METHODOLOGY.md §1.5's output contract; the afternoon-exhaustion/boost test (§1.3's second bullet) is the remaining piece, not yet built.

## 2026-09-01 — Stage B: afternoon-exhaustion test — a real negative result, not a broken pipeline

**Cheapest check first, same discipline as the overnight signature.** Before writing a boost detector, plotted full-day traces (00:00–24:00, 16:00–20:00 window shaded) for 3 well-fitted seasonal households on the coldest day of 2013 and a mild June day. Small-sample impression: afternoon bumps looked, if anything, *more* visible on the mild day — the opposite of the expected mechanism. Flagged explicitly as too small a sample (n=3 households, 2 days) to trust before scaling up.

**Scaled up before concluding anything.** Checked mean peak power and mean total energy in the 16:00–20:00 window across all 37 seasonal households, split by coldest-quartile vs. mildest-quartile days (95 vs. 92 days). Result: cold days show **+47% higher mean peak, +55% higher mean total energy** — real, directionally correct, and it corrected the misleading small-sample impression. Good demonstration of why n=3 shouldn't be trusted (again).

**Built the two required pieces (`src/exhaustion_test.py`):**
- Boost detector: 16:00–20:00 window, 0.5–3.0kW band (METHODOLOGY.md-style illustrative band, explicitly flagged UNTESTED — unlike the overnight band, there was no labelled example to check it against, per the UK-DALE/HES findings earlier), run length 1–4 consecutive half-hours (shorter than the overnight block's own run requirement). **56.1% of all household-days flagged** — high enough to be a concern in its own right (see conclusion below).
- Simple constant-rate decay model: `predicted_runout_hour = 07:00 + night_kwh / release_rate_kw`. First attempt used an assumed 2.0kW release rate — **predicted the median household runs out of stored heat by noon**, which contradicts basic storage-heater design intent (they're built to last the day). Recalibrated properly rather than guessed again: used the median charge on cold nights specifically (top quartile heat_loss_proxy, median 24.1kWh) and required it to last a full 24h cycle, giving **1.0kW** — a design-intent-derived figure, not a second guess.

**Cross-tabulation still runs backwards after recalibration.** Nights where the model predicts exhaustion by 20:00: 50.0% show boost. Nights where it predicts NOT exhausted: 64.1% show boost — higher, not lower. This survived a proper recalibration, which rules out "wrong constant" as the explanation.

**Conclusion, reported honestly per METHODOLOGY.md's own instruction ("if exhaustion shows up randomly... the model doesn't have a story, and shouldn't claim one"):** the population-level cold/mild association is real, but this more specific test — does the decay model's predicted exhaustion *time* predict boost occurrence — does not hold up, even properly calibrated. The most likely explanation: 16:00–20:00 is exactly when ordinary household activity (cooking, lighting, occupancy) peaks for every household regardless of heating system, and on cold days that general activity rises for everyone — a confound this method cannot separate from genuine heater-exhaustion behaviour using whole-house aggregate data alone. The boost detector's 56% flag rate is consistent with this: too high to plausibly be a rare, distinct backup-heating signature, more consistent with catching ordinary evening appliance use.

**Not pursued further this session** (per §2.8 — a third guessed parameter to force the cross-tab to agree would be exactly the "adjust until it looks right" pattern this project explicitly rules out). The overcharge test stands as Stage B's validated finding; the afternoon-exhaustion/boost mechanism is reported as a genuine negative result, not silently dropped or forced to agree.

## 2026-09-01 — Stage B → communication (METHODOLOGY.md §1.4): reprojected onto current £

**Economy 7 rate, sourced and cited.** Ecotricity's official domestic tariff sheet, effective 1 April 2026 (fetched directly, not from a search snippet): London, Direct Debit, standard variable Economy 7 — day 28.09p/kWh, night 18.73p/kWh, standing charge 44.40p/day.

**Octopus Agile: real current data, honestly scoped.** Confirmed the live product (`AGILE-24-10-01`, London tariff code `E-1R-AGILE-24-10-01-C`) via the public, unauthenticated Octopus REST API. Hit a genuine tool limitation: custom `period_from`/`period_to` query parameters were silently dropped on a fresh `web_fetch` call, returning a cached late-August window regardless of the requested date — confirmed this wasn't a one-off by trying twice. Rather than force it, asked the user to fetch two representative weeks directly (12–19 Jan 2026, 24–31 Aug 2026) — the same lightweight pattern already proven for the weather data. Both landed clean: 336 half-hourly records each, real prices, correctly timezone-converted from UTC to UK local clock time (GMT for the January week, BST for the August week — checked explicitly rather than assumed, since getting this wrong would silently shift every price by an hour).

**A real, unexpected finding: winter Agile overnight is cheaper than flat Economy 7; summer Agile overnight is pricier.** Winter (23:00–07:00) mean 17.76p/kWh vs Economy 7's flat 18.73p; summer mean 24.0p/kWh. Applied the appropriate seasonal profile (winter/summer/shoulder-blended for spring and autumn months) to every confirmed household-night's actual charge.

**Results — both required comparisons, per §1.4:**
- All night charging: static Economy 7 £39,324/year total (£959/household) vs. Agile £41,085/year (£1,002/household) — Agile costs *more* for this population, applied to their actual (unmanaged) charging pattern.
- The overcharge/waste specifically: £4,802/year total under Economy 7 (**£117/household/year**) vs. £5,150/year under Agile (£126/household/year).

**Why Agile comes out worse, and why that's the right finding, not a bug:** this comparison holds the charging *pattern* fixed (same hours, same block, every night) and only swaps the tariff underneath it. A household that charges identically regardless of the actual half-hourly price captures none of Agile's cheap troughs and is fully exposed to its peaks — so a real household on Agile, charging exactly like today, would not obviously save money, and might lose a little. This is not a discouraging result for the project; it's precise confirmation of METHODOLOGY.md's own framing: **the value was never in the tariff, it's in the timing** — which is exactly Phase 2's job (the nudge engine and relay retrofit), not Phase 1's. The gap reported here belongs to Phase 2 to close, not to Phase 1 to claim.

**Output:** `data/intermediate/agile_price_profile.parquet` (the fitted seasonal half-hour price profile) and the £-reprojected figures above, ready for Phase 1's final report. This completes METHODOLOGY.md §1.4 and, with it, all of Phase 1's specified analytical steps (§1.1–§1.4) bar the write-up itself.

## 2026-09-01 — Phase 1 report built

`reports/Phase1_Data_Report.docx` — the formal write-up README.md specified ("a data report: overcharge and afternoon-exhaustion patterns, quantified, reprojected onto current tariffs"), including the headline figure README called out specifically ("the raw half-hourly trace of a handful of confirmed storage-heater households against the modelled 'required charge' line... that single chart is the whole Phase 1 thesis made visible").

**Caught and fixed a real visual-honesty problem before finalizing the headline figure.** The first version of that chart plotted the modelled-required line as a flat *average* power level against the actual trace's *peak* power — technically not wrong (both represent the same total energy) but visually misleading, since a real storage heater's charge is front-loaded rather than flat across the night, so any flat line will sit well below the real trace's peak regardless of whether genuine overcharging occurred. Checked the underlying per-night numbers directly (they were fine — modelled and actual track within a few kWh most nights, consistent with the 25.9% flag rate) before concluding the chart itself, not the data, was the problem. Fixed by scaling each household's own real half-hourly shape to the modelled energy total, so line heights are honestly comparable, and annotated each night with the actual numbers (actual vs. modelled kWh) rather than relying on the shape alone.

7 sections: executive summary, the headline figure, data & population (with the full-population S_night histogram and its independent agreement with the visual sample), overcharge quantification and validation, the afternoon-exhaustion negative result (reported plainly, not hidden), the £ reprojection (Economy 7 vs. Agile, including the "tariff alone doesn't help without timing" finding), and an explicit limitations section naming every open caveat from this session (small year-round sample, no labelled ground truth, two-week Agile sample rather than a full year, the afternoon-exhaustion mechanism left unresolved). Rendered to PDF and visually checked page-by-page before delivery, per the docx skill's own verification step — caught and fixed an initial image-sizing bug (pixel dimensions set two orders of magnitude too large, causing images to silently fail to render) this way.

## 2026-09-01 — Fuel surrender / Awaab's Law extension: tested and reframed

**User's request:** detect "fuel surrender" (heater abandonment) and point-heater substitution via two proposed signatures, tied to under-heating, damp/mould risk, and Awaab's Law (Social Housing (Regulation) Act 2023).

**Signature A (Nov-high → Jan/Feb-collapse in S_night) tested directly — genuine null result.** Computed monthly S_night for all 41 confirmed households across Nov/Dec/Jan/Feb 2013. Zero households show a collapse to background level (<0.20) despite genuinely colder later months (Nov/Dec mean ~6.4°C, Jan/Feb mean ~3.2°C). S_night is remarkably stable across the whole season for nearly every household (most vary <0.05 between mildest and coldest months). Plausible explanation, flagged upfront before running the test: 2013 Economy 7 prices were far below today's crisis-era levels, so the acute bill-shock dynamic this signature targets may genuinely not have existed at comparable intensity in this dataset's period. Reported as a real negative result, not reframed to appear positive.

**Signature B not run.** As specified, it's conditioned on an abandoned-household subset from Signature A; with zero such households, there's no natural population to test it against. Running it against the general population would reproduce the exact cold-day/general-activity confound that already broke the afternoon-exhaustion test (Section 3 of the report) — declined to repeat a known-failed pattern rather than force a second unreliable detector.

**Cost comparison built instead, with the user's own assumptions checked rather than accepted.** Gas rate corrected from an assumed 6.2p/kWh to the already-sourced 7.15p/kWh (Ecotricity London Standard Direct Debit, same tariff sheet as the electricity figures, kept consistent). "Optimized" dynamic-tariff rate computed from real winter Agile data (cheapest 16 half-hours/day) rather than assumed: 17.49p/kWh — only marginally below the flat overnight window (17.76p), confirming winter Agile has little unclaimed arbitrage within the traditional night window; the real opportunity is eliminating the 12.2% overcharge, not chasing sub-30p dips in winter specifically.

**Result — the key structural finding:** even fully optimized (overcharge eliminated, Agile-timed), electric storage heating at 4,500 kWh/year space-heating demand costs £691/year vs. gas's £379/year — a persistent £313/year gap that no amount of Phase 2 optimization closes. Phase 2's real, defensible value is the £236/year gap between unmanaged (£927) and fully-optimized (£691) — genuine, but a harm-reduction improvement, not parity with gas. This gives a more defensible account of why under-heating/fuel-surrender risk exists structurally (a real economic incentive, present regardless of behaviour) than the originally-proposed detector would have, given the detector returned no evidence in this dataset.

## 2026-09-01 — Phase 1 formally closed, checked against PROJECT.md §9.6's own criteria

**"Phase 1 — done when: the NILM disaggregation is applied to a real dataset, a documented, reproducible overcharge/afternoon-exhaustion pattern is either found or not found, and — whichever it is — the finding is written up with the same rigour either way, reprojected onto current tariffs."** All three conditions met: disaggregation applied (43/4,443 households confirmed), overcharge found and quantified (12.2%, £117/hh/yr), afternoon-exhaustion tested and explicitly *not* found (Section 3 of the report, given equal prominence to the positive result rather than buried), both reprojected onto current 2026 prices.

**Assumptions Ledger (§9.5), items 1–3 — the ones scoped to Phase 1 — checked off, not just assumed resolved:**
- Item 1 ("material share on Economy 7/storage heaters — untested"): resolved at ≈1.0% (43/4,443) — smaller than "material" might suggest, reported as found, not adjusted toward expectation.
- Item 2 ("2–3kW square-wave signature disaggregable via simple rule-based method — plausible but untested"): **worth flagging explicitly** — this specific hypothesis did not survive contact with real data (the fixed-band/steadiness detector failed repeatedly; see the multi-round detector saga earlier in this log). Disaggregation succeeded, but via a different method (S_night, seasonal energy share) than the one this assumption named. The assumption as originally stated is falsified even though the broader goal was met — logged so this distinction isn't lost.
- Item 3 ("25–40% more than modelled — illustrative, actual finding may differ"): resolved at 12.2% overall (25.9% for seasonal households specifically) — smaller than the illustrative placeholder, reported as-is per §2.8.

Phase 1 is closed. Per Cross-Phase Notes ("do not start Phase 2's compliance simulation on assumed savings while Phase 1 is still open"), Phase 2 — the Behavioural Nudge Engine — is now the correct next phase to open.

## 2026-09-02 — Phase 2.1: thermal forecast engine built and validated

**Wind chill formula checked before coding, not assumed.** Confirmed the JAG/TI (2001) formula — the one actually used by the UK Met Office, Environment Canada, and the US NWS — via direct search rather than recalled from memory: `WC = 13.12 + 0.6215*T - 11.37*V^0.16 + 0.3965*T*V^0.16` (T in °C, V in km/h), valid only for T≤10°C and V≥4.8km/h. Implemented in `src/thermal_forecast.py` with the validity range enforced explicitly — outside it, raw temperature is returned unadjusted rather than extrapolating the formula somewhere it hasn't been checked to hold.

**Reuses Phase 1's exact structure, not a fresh formula, per METHODOLOGY.md's explicit instruction.** `heat_loss_proxy_v2 = max(0, 15.5°C − wind_chill_temp)` — identical `max(0, base_temp − T)` form to Phase 1's `overcharge_test.py`, with the wind-chill-adjusted temperature substituted in place of raw temperature. Self-tested against a hand-computed value (T=-5°C, V=30km/h → -13.0°C, verified by independent arithmetic) plus boundary checks (no adjustment above 10°C or below 4.8km/h wind; proxy still floors at 0 on mild days regardless of wind).

**Data:** same lightweight user-fetch pattern as the earlier weather/Agile data (Open-Meteo still blocks automated fetching). Requested daily temperature, wind speed, and solar radiation for London, full year 2013 (matching Phase 1's exact period, so the Target Charge Index (2.2) can later be checked against what Phase 1 actually found, not a fresh assumption). One parameter name (`wind_speed_10m_mean`) was an educated guess rather than a confirmed-from-docs string — flagged to the user in advance; it turned out correct, data landed clean on the first attempt, 365 days, no nulls.

**Validated against real, independently-verifiable weather history.** The wind-chill adjustment's biggest effects cluster in March 2013 — which matches the well-documented UK "cold spring of 2013" (a real, widely-reported prolonged cold, windy spell), not a coincidence manufactured by the analysis. On the worst day (11 March: -0.2°C, 29.8km/h wind), the wind-chill-adjusted proxy (22.2 degree-days) runs 41% higher than Phase 1's temperature-only figure (15.7) — a real, physically meaningful difference between what Phase 1's simpler model would have estimated and what Phase 2's engine now captures. `data/intermediate/fig2_windchill_march2013.png`.

**Output:** `data/intermediate/phase2_thermal_forecast_2013.parquet` — daily temp, wind speed, solar radiation, wind-chill-adjusted temp, and both proxy versions for all of 2013. Completes METHODOLOGY.md §2.1. Next: §2.2, the Target Charge Index, which will use this proxy per-household (reusing each confirmed household's own fitted slope/intercept from Phase 1, the same way Phase 1 itself avoided a single population-wide constant).

## 2026-09-02 — Phase 2.2: Target Charge Index — built, with an honest scope gap flagged upfront

**METHODOLOGY.md's exact wording checked before building anything:** calibrate against "actual overnight charge needed to avoid BOTH overcharge and afternoon exhaustion." Phase 1's exhaustion test returned a genuine negative result (2026-09-01 entry above) — there is no validated relationship to calibrate an exhaustion-avoiding floor from. Built the overcharge-avoiding half only (real, Phase-1-validated data), and stated this gap explicitly in the module's own docstring and in every place the index is used downstream, rather than silently building a floor from an assumption dressed up as calibration — exactly what PROJECT.md §2.6 prohibits.

**A real consistency problem caught before finalizing, not after.** Phase 1's `modelled_required_kwh` was fitted against the temperature-only proxy (v1) — wind data didn't exist yet at that point in the project. Checked the gap between v1 and the new wind-chill-adjusted proxy (v2, from §2.1) directly: differs by more than 2 degree-days on 150 of 365 days (41%) — not a rounding difference, concentrated on exactly the cold, windy days this index matters most for. Calibrating against v1 while feeding the forecast engine v2 at lookup time would have silently misclassified a large fraction of real cold nights. Fixed by refitting all 37 households' response lines against v2 using the real wind data now available, rather than noting the mismatch as a footnote and shipping it anyway.

**Refit held up:** median R² barely moved (0.699 → 0.693) — the wind-chill adjustment doesn't hurt the underlying fit, confirming this was a consistency fix, not a modelling regression.

**Calibration method (`src/target_charge_index.py`):** each household's `modelled_required_kwh` normalized to 0–1 by that household's own maximum (coldest-night) fitted requirement, making different heater capacities comparable (Phase 1 already found roughly 5x variation in capacity across confirmed households). Pooled across all 13,467 seasonal household-nights, quantile-binned into 5 equal-sized bands (2,693–2,694 nights each, by construction) — the bands themselves come from where the real data's own distribution splits, not chosen round numbers.

**Self-tested and applied to the real 2013 year as validation, not just unit-tested in isolation:** monotonicity holds (colder never produces a lower index than milder), a mild night correctly floors at Index 1, the coldest observed night correctly hits Index 5. Applied across the full real 2013 year: the March cold snap (§2.1's wind-chill figure) correctly lands at Index 5 on its coldest, windiest days; a calm mid-August week correctly sits at Index 1 throughout. Whole-year distribution: Index 1–5 counts of 98/53/50/91/73 days — genuine spread across the full range, not clustered in one band.

**Output:** `data/intermediate/phase2_index_calibration.parquet` (the calibration table, per METHODOLOGY.md's exact naming) and `data/intermediate/phase2_daily_index_2013.parquet` (the applied result). Completes METHODOLOGY.md §2.2, with the exhaustion-avoidance gap carried forward explicitly rather than resolved by assumption. Next: §2.3, nudge copy generation — where the humidity/comfort claim already flagged in METHODOLOGY.md needs either a real cited standard or softened wording before it ships.

## 2026-09-02 — Humidity/comfort claim (METHODOLOGY.md §2.3): checked against real standards, resolved

**Original claim checked directly against ISO 7730 (2005 and 2025 editions, consistent wording in both):** the standard's own precise relationship is "a 10% higher relative humidity and a 0.3°C higher operative temperature are perceived as being warmer in equal measure." Worked the math: the claimed "18°C feels like 21°C" (a 3.0°C claim) would require a 100-percentage-point RH swing to support — physically impossible, since RH only ranges 0–100%. A realistic dehumidifier-achievable swing (70%→40% RH, 30pp) supports only ~0.9°C. ISO 7730 also states directly that "in moderate environments the air humidity has only a modest impact on thermal sensation" — the standard's own guidance is to disregard this effect near comfort temperatures, not build a headline claim on it.

**User supplied a "corrected" pitch citing CBE's Thermal Comfort Tool and ASHRAE 55**, reframed around dampness/mould rather than a temperature-equivalence number — but the reframed pitch's closing clause ("keeps 19–20°C feeling completely comfortable without needing to overheat to 22°C+") reintroduced essentially the same ~2–3°C equivalence claim in different numbers. Checked rather than accepted on the strength of the better citations: found an independent source using the more sophisticated two-node SET/ET* model (not just ISO 7730's simplified PMV rule of thumb) reaching the same conclusion — "humidity has only a small effect on thermal comfort" across a wide 20–55% RH range near the comfort zone. Two different models, two different standards bodies, same answer: no realistic indoor humidity swing supports a multi-degree comfort-equivalence claim.

**Also caught a citation-scope mismatch:** ASHRAE 55 explicitly disclaims mould coverage — "ASHRAE Standard 55 is strictly limited to thermal comfort considerations, so mould issues... are not accommodated in the ASHRAE 55 thermal comfort recommendations." Citing ASHRAE 55 for the mould/dampness claim specifically would be citing the wrong standard for that half of the pitch, even though it's the right standard for the comfort half.

**Resolved, agreed with the user:** keep the dampness/mould framing (well-supported, multiple independent sources confirm 40–60% RH as the right range for both comfort and mould prevention) but drop the specific temperature-equivalence number entirely. Final grounded copy direction: *"keeping humidity between 40–60% stops that damp, clammy feeling and helps prevent mould — you shouldn't need to push the heating past 20°C for comfort once the air's drier."* No fabricated degree-equivalence, no ASHRAE-55-for-mould mismatch, keeps the genuinely solid claims.

## 2026-09-02 — Phase 2.3: nudge copy generation built

**Templates as config data (`config/phase2_nudge_copy.py`), not inline strings in code**, per METHODOLOGY.md's explicit instruction — 5 charge-level templates (Index 1–5), a supplementary humidity/mould tip using the just-resolved grounded language (no degree-equivalence claim), and an explicit disclaimer noting the index only calibrates the overcharge-avoiding half (Phase 1's exhaustion test was a negative result, carried forward from §2.2 rather than silently dropped here).

**Generator (`src/nudge_generator.py`) is a pure, deterministic function** per METHODOLOGY.md §2.5's output contract (fixed weather/index input → fixed message output) — no randomness anywhere, self-tested for determinism directly (same context called twice produces identical output).

**Reading level actually measured, not eyeballed.** Implemented Flesch Reading Ease directly (no dependency needed for one formula) and set a real target (≥70, "fairly easy") per PROJECT.md's "tested for reading level" instruction. The check caught something real on the first run: the exhaustion-disclaimer line scored right at the boundary (70.0, denser wording — "estimates," "predict," a longer sentence). Rewritten in plainer words ("This helps you avoid paying for heat you don't need... It can't yet tell you if you'll run low on heat later in the day") and rescored at 102.0. All 7 lines now clear the target — proof the check does real work, not just a pass-everything formality.

**Output:** `config/phase2_nudge_copy.py` and `src/nudge_generator.py`, both self-tested (determinism, all 5 index levels produce valid distinct messages, invalid index raises rather than silently producing garbage, reading level measured). Completes METHODOLOGY.md §2.3. Next: §2.4, the compliance and financial-impact simulation — a scenario grid across tenant compliance rates, multiple historical weather years, and real Agile prices, reporting a range rather than a single point estimate.

## 2026-09-02 — Phase 2.4: compliance/savings simulation — a real bug caught by validating first

**Scope stated upfront, before building anything:** "multiple historical weather years" can only be satisfied by applying each confirmed household's own fitted response (a property of their heating system, not the specific year) to real weather from several years — there is no behavioral data for any year but 2013, so this tests weather-driven variance in the savings estimate, not a claim about how tenants would actually have behaved differently. Agile prices remain the two representative weeks already sourced, per the Sledgehammer Test's explicit tolerance for scenario-grid-level approximation.

**Built a validation check before trusting the pipeline on new data — and it caught a real bug immediately.** First attempt defined each household's "overcharge rate" as (actual − modelled) summed over the whole year, divided by modelled. Validating this against Phase 1's own already-proven 2013 result gave exactly zero excess for every single household — not close to Phase 1's known 22,249 kWh figure, off by 100%. Diagnosed rather than dismissed: this is a real mathematical property, not a coding slip — OLS regression fitted with an intercept produces residuals that sum to exactly zero *by construction*, so a net-annual-residual "overcharge rate" is mathematically guaranteed to be ~0 regardless of what the real data shows. Phase 1's actual figure was never a net residual — it was the sum of excess specifically on nights *flagged* as overcharged (actual > modelled × 1.25). Fixed `compute_household_overcharge_rates` to reproduce that definition exactly.

**Re-validated after the fix: 22,345 kWh simulated vs. 22,249 kWh reported — a 0.4% gap**, small and fully explained (this simulation runs on the wind-chill-refit v2 household fits from §2.2, not Phase 1's original v1 figures). Strong enough agreement to trust the pipeline before extending it to new weather years.

**Data requested:** multiple years of real London weather (temperature + wind, matching the variables the wind-chill-consistent proxy needs) via the same lightweight fetch pattern. Chose 2020–2025 (six most recent complete years relative to today) as a neutral selection rule — not hand-picked known-extreme winters, which would bias the range toward a predetermined story.

## 2026-09-02 — Phase 2.4 completed: the scenario grid, and a genuinely useful finding about 2013 itself

**2013 sits above the entire 2020–2025 range.** Applying each household's own fitted response to six real recent years' weather: excess kWh ranges 16,958–20,222 across 2020–2025, while Phase 1's actual 2013 figure was 22,249 — above the top of that range, not inside it. 2013 was colder than any of the six most recent comparison years. This means Phase 1's headline £117/household figure, while completely real and unchanged, likely runs a little high relative to a typical *recent* winter — precisely the risk METHODOLOGY.md's "avoid overfitting to one unusually mild or harsh winter" instruction was written to catch, and it's now checked rather than assumed.

**Full scenario grid built:** 6 weather years × 3 compliance rates (10/30/50%, illustrative bounds per PROJECT.md §9.5 item 4) × 2 tariffs (static Economy 7, seasonal Agile). Per-household-per-year range:
- 10% compliance: £9–£10/hh/yr
- 30% compliance: £24–£31/hh/yr
- 50% compliance: £41–£51/hh/yr

Reported as a range across the grid, not a single point estimate, per METHODOLOGY.md's explicit instruction. Note this covers seasonal households only (37, not 41) — year-round households have no temperature response to simulate against a different year's weather by construction, so are out of scope for this specific weather-sensitivity test; their savings opportunity was already covered in the Phase 1 report's mild-night analysis.

**Output:** `data/intermediate/phase2_savings_by_scenario.parquet`, matching METHODOLOGY.md §2.5's exact required filename. Completes METHODOLOGY.md §2.4. Combined with §2.1–§2.3 already done, Phase 2's substantive analytical work is complete; §2.5's other requirement (the notification-generation function) was already satisfied by `src/nudge_generator.py` in the §2.3 entry above.

## 2026-09-02 — Phase 1 and 2 formally closed; Phase 3 opened

Checked Phase 2 against PROJECT.md §9.6's exact wording before moving on, same discipline used for Phase 1: "the forecast engine and nudge-copy logic exist as working code... the financial-impact model runs the three compliance-rate scenarios against real Octopus Agile historical prices... the comfort/humidity messaging is either grounded in a cited standard or dropped." All three conditions independently verified met. Phase 2 closed.

## 2026-09-02 — Phase 3.2: control logic built and unit-tested in software, before any hardware

**User's own instinct, acted on directly:** test the control logic in software before committing to physical hardware. Built `src/control_logic.py` and unit-tested it against all four of METHODOLOGY.md §3.3's required bench scenarios plus two explicit fail-safe cases, before any relay or sensor exists.

**Comfort-cutoff number corrected, not left as the original placeholder.** METHODOLOGY.md's own pseudocode marked `reduced_setpoint = 18.5C` (a 2.5C reduction from 21.0C) as "pending Phase 2 psychrometric grounding" — that grounding happened on 2026-09-02 (see the humidity/comfort entries above). Set `REDUCED_SETPOINT_C = 20.5` (a 0.5C reduction) in `config/phase3_control_config.py`, with the full derivation cited directly in the config comment: ISO 7730's real relationship (0.3C per 10pp RH) applied to a realistic swing crossing the control's own 50% threshold (~20pp) gives ~0.6C — set conservatively *below* that computed figure rather than at or above it, consistent with this project's repeated caution about erring toward not under-heating a vulnerable tenant.

**Relay charge-duration ported directly from Phase 2's real calibration table, not reinvented.** Rather than invent an even 20/40/60/80/100% fraction scheme for the five Target Charge Index levels, the control logic loads `phase2_index_calibration.parquet` directly and uses each band's real empirical midpoint (Index 1: 8.8% of the off-peak window, Index 5: 86.3%) — genuine quantile-derived figures, not round numbers. Worth noting Index 5 charging for "only" 86.3% rather than a clean 100% is itself an honest reflection of the real underlying data, not a bug to round away.

**A real inconsistency surfaced, flagged rather than silently resolved.** METHODOLOGY.md §3.2's own pseudocode states a default off-peak window of 00:00–05:00 — narrower than the 23:00–07:00 window Phase 1 and Phase 2's entire analysis was built on. Used the Phase 3 spec's own stated default as given (00:00–05:00), rather than silently substituting Phase 1's window, but flagged this explicitly in `config/phase3_control_config.py` as something worth resolving before any live install — the two windows should probably match, and it's not this code's place to decide unilaterally which one is right.

**All four required bench scenarios pass, plus two explicit fail-safe tests and a determinism check (7/7):**
1. Cold night (Index 5) → relay ON well within the charging duration.
2. Mild night (Index 1) → relay briefly ON at window start, OFF well before the window ends (the real "reduced charge" behaviour, not a binary on/off).
3. Manual override → engages when requested within the last 30 minutes, correctly lapses past that boundary (tested at the exact 30-minute edge, not just comfortably inside/outside it).
4. Forecast dropout → fails toward **standard charging** (not "heater off"), exactly as METHODOLOGY.md §3.3 requires — verified with an explicit assertion, not just eyeballed.
5. RH sensor dropout → fails toward **normal setpoint** (never the reduced one) — same explicit-assertion discipline.
6. Comfort cutoff logic tested directly (low RH → reduced setpoint; normal/high RH → normal; active override suppresses the cutoff even at low RH, since a tenant-requested boost shouldn't be quietly undermined by a setpoint reduction they didn't ask for).
7. Determinism confirmed (same inputs always produce the same control state, per PROJECT.md §5.5).

**Output:** `config/phase3_control_config.py`, `src/control_logic.py`, `src/test_control_logic_bench_matrix.py` (7/7 passing). This satisfies the control-logic portion of METHODOLOGY.md §3.5's output contract in software; it is explicitly not a substitute for the real bench run once hardware exists, and does not touch §3.1 (rig assembly), §3.4 (electrician sign-off — this project cannot self-certify BS 7671), or the real BOM/install-time figures, all of which remain physical-world tasks.

## 2026-09-02 — Bench harness built; hardware recommendation checked, not assumed; a real integration bug caught before it shipped

**User clarified their actual plan:** a low-power LED bench test first (matching METHODOLOGY.md §3.1's own "dummy load, not a real heater" design exactly), with a real storage heater available once that succeeds — before any electrician involvement. Built `src/bench_harness.py`: a hardware-agnostic control loop that runs `control_logic.py` against real wall-clock time (not simulated timestamps), logs every decision to CSV, and drives the relay through a swappable function. Smoke-tested live — correctly read the real current time and logged "outside off-peak window" since it's currently afternoon, confirming it reacts to genuine `datetime.now()`, not a fixture.

**Hardware recommendation given only after checking real specs, not from memory.** User had no hardware decided and asked for a recommendation. Rather than default to METHODOLOGY.md's already-named Shelly Pro 1PM on trust, searched and confirmed its real current specs directly (16A DIN-rail relay, WiFi/LAN/Bluetooth, built-in power metering, confirmed local-network operation with no cloud/hub dependency) across multiple independent retailer and manufacturer sources. Recommended it specifically *because* it's the same device the eventual real heater install will need — bench-testing on production-equivalent hardware validates the full integration path (software → local API → relay → load), not a throwaway prototype on different hardware that gets discarded later. Its built-in power metering also satisfies §3.3's "log... dummy-load power" requirement directly from the hardware, without a separate meter.

**Caught a real integration bug before handing over the code.** The bench harness's original stub comment (written before this hardware conversation) used the Shelly *Gen1* legacy HTTP format (`/relay/0?turn=on`) — checked this specifically against Shelly's own API documentation rather than assume it still applied, and found the Pro 1PM is a Gen2+ device using a completely different protocol (JSON-RPC over HTTP, `/rpc/Switch.Set?id=0&on=true`). The Gen1 format is for the older, different "Shelly1/1PM" product. Fixed the stub with the verified-correct Gen2+ RPC format and added the real power-reading call (`Switch.GetStatus`, field `apower`) before this went any further — this is exactly the kind of thing that would have quietly failed to work the first time the user tried to wire it up, caught in the docs check rather than during a live bench session.

**Output:** `src/bench_harness.py`, ready for a real driver function once hardware is in hand. Physical rig assembly, the actual LED bench run, and everything past it (§3.4's electrician sign-off in particular) remain the user's to do — this is software groundwork only, explicitly not a substitute for the real test.

## 2026-09-02 — LinkedIn post and article drafted from the project's real findings

User wants to share this work publicly — a LinkedIn post and a longer article — while being upfront that the underlying idea ("make storage heaters smarter") isn't itself novel; the value is in the rigour of the actual empirical work done this session.

Drafted both in first person (personal-capacity register, per PROJECT.md §20 — this is Andy speaking as himself, not a formal organisational submission), using only numbers already verified this session: 4,443 households, 43 confirmed (~1%), 12.2% overcharge, £117/household/year, the "dumb tariff switching makes things slightly worse" finding, the £313/year structural gap to gas, the humidity-claim correction (~3-5x overstatement vs. ISO 7730), and the 7/7-passing control-logic tests with the fail-safe behaviour specifically called out. No new claims invented for the write-up — every figure traces back to an entry already in this log.

Article leads with the methodology's honesty as the actual selling point (a failed first detection attempt, a reported negative result on afternoon exhaustion, a caught-and-corrected comfort claim) rather than presenting the findings as if they arrived cleanly — consistent with how the whole project was actually run, and a more credible story than a tidied-up version would be. Both pieces close with an honest ask for collaborators (hardware/embedded help, an eventual housing association contact), matching the user's own stated need.

**Output:** `comms/linkedin_post.md`, `comms/article.md`.

## 2026-09-02 — Stress-testing the whole project premise: does 2030 insulation policy make the hardware retrofit moot?

User's own idea, checked rather than assumed either way: with social housing facing a real regulatory insulation upgrade by 2030, might AutoMagic's savings shrink to triviality once fabric improves and solar/battery are added?

**Real, dated policy confirmed, not assumed.** Government published its consultation *response* in January 2026 (not just a proposal): social rented homes move from no formal minimum standard (current requirements "roughly equivalent to EPC F") to EPC Band C by 1 April 2030. Matches the user's "under 4 years" framing closely — checked directly rather than taken as given.

**Insulation demand-reduction figure sourced, not assumed.** Multiple real sources checked: single-band improvements (D→C) run ~15–25%; "comprehensive" multi-band retrofits (closer to the F-start this project actually needs) run 35–50% reduction in heating demand. Used the wider range rather than false precision, since no source gave an exact F→C figure specifically.

**New scenarios built, all traceable to sourced rates already established this session:**
- Plug-in 1kW point heater (5h/evening) + electric blanket (100W, 8h/night), on the same Eco7 tariff structure: £280/year, ~1,044 kWh — genuinely the cheapest option in the table, flagged explicitly and repeatedly as a comfort/safety-reduced coping behaviour tied directly to Section 6's under-heating/Awaab's Law discussion, not a real alternative.
- Octopus Agile, unmanaged: reprojected via the REAL measured ratio from the Phase 1 report's actual fleet data (Agile:Eco7 cost ratio for the same real charging pattern, 1.0448), rather than a fresh calculation — £969/year, confirming the earlier "dumb tariff switching costs more" finding at the standardised 4,500kWh baseline.

**The central finding: insulation halves AutoMagic's absolute saving, but doesn't eliminate the relative case.** Applied the sourced 35–50% reduction to gas, unmanaged storage heating, and AutoMagic together (insulation is fuel-agnostic, so applied consistently across all three, not just the electric scenarios). AutoMagic's saving over unmanaged: £236/year uninsulated → £153 (35% insulation) → £118 (50% insulation). Real, substantial shrinkage — but flagged an important directional counter-consideration: an existing storage heater sized for a leaky EPC-F home becomes *more* oversized once the fabric improves, which could keep the *relative* overcharge rate stable or even push it up, cutting against a pure proportional-shrinkage read. Presented both effects rather than only the one that shrinks the case.

**Solar/battery reconciled against the earlier December-generation finding, not taken at face value.** Real current capex/opex sourced (4kWp: £5–9k, £600–900/yr; +battery £2.5–5k, +£200–400/yr) — but cross-checked against this session's own earlier finding that a 4kWp system's entire December output (70–120kWh) covers under 15% of one real household's actual December heating charge (917kWh). Conclusion: solar/battery's real, substantial saving is earned mostly outside the heating season, offsetting general household electricity — it does not meaningfully compete with or substitute for AutoMagic's winter-heating-specific saving. The two are additive, not competing, for the same pound.

**Heat pump explicitly declined, not quietly answered.** PROJECT.md states directly: "does not model heat pump conversion... explicitly out of scope." Flagged this rather than giving a shallow number that would undercut the project's own stated rigor — asked the user whether to formally open this as new scope.

**Output:** `data/intermediate/phase4_scenario_costs.json`, `data/intermediate/fig3_scenario_comparison.png`. Not yet folded into a formal report section — presented in chat pending the user's steer on whether this becomes a permanent document.

## 2026-09-02 — Winter concentration, fuel poverty evidence, and heat pump scoping

**Seasonal concentration checked directly against real confirmed-household data, not asserted.** Nov–Feb (4 months) accounts for 52.9% of the entire year's charging — 1.6x the rate a smoothed 12-month average implies. Applied to £ figures: unmanaged storage heating's real winter monthly cost is £123, not the £77/month a naive annual-average/12 calculation suggests. Just the 3 single highest-charging months (Jan, Mar, Feb — March still shows up, consistent with the earlier-confirmed 2013 cold spring) account for 44.5% of the whole year alone.

**Real fuel-poverty evidence sourced to test whether the "poor households can't smooth consumption" intuition holds, not assumed.** A peer-reviewed study (Applied Energy, real GB smart-meter data, 11,500 prepayment customers) found "more homes self-disconnected from gas during cold periods than at other times, despite the greater need for heating" — direct evidence against the assumption that low-income households manage to smooth their heating spend across the year. Current survey data (2025-26): 53% of a prepayment-meter sample have drastically cut energy use recently, and 35% now live in a cold, damp home as a direct result — this is Section 6's theorised under-heating-to-mould pathway, found already happening at measurable scale, not remaining a hypothesis.

**"Existential crisis" framing evaluated rather than validated on request.** Distinguished what the evidence supports (a genuine, quantifiable, foreseeable liability under Awaab's Law, with a demonstrable causal chain from the structural cost gap through to documented self-disconnection and cold-damp outcomes) from what it doesn't (the word "existential" implies organisational-survival-level threat, which needs HA-specific scale data — unit counts, reserves, enforcement history — not available here). Recommended framing: "a material and growing compliance risk deserving board-level attention before 2030," not the stronger unverified claim.

**Heat pump scoped as requested, with the running-cost/capex split made explicit.** SCOP range confirmed (2.5–4.0 across multiple sources). Running cost at current prices: £241–451/year (SCOP 3.5 best-case to 2.8 conservative, off-peak to no-timing) — genuinely competitive with gas, better than every other electric scenario. But two capex-side findings that block treating this as settled: (1) the £7,500 Boiler Upgrade Scheme grant explicitly excludes social housing — confirmed across multiple independent sources — so any real capex case needs Warm Homes: Social Housing Fund figures, not sourced this session; (2) storage-heater flats typically have no existing wet radiator system, meaning a heat pump conversion here is a full new-system install (radiators, pipework, cylinder), not the boiler-swap the wider heat-pump grant marketing assumes. Presented the favourable running-cost finding clearly while flagging the capex picture as a real, unresolved scope gap rather than glossing over it.

**Output:** `data/intermediate/fig4_full_comparison_with_heatpump.png`. Heat pump capex/SHDF-funding research remains open for a future session if the user wants to pursue it further.

## 2026-09-02 — Second LinkedIn post and article, covering the policy stress-test

Drafted as a direct follow-up to the first post/article, using only figures from this session's real work: the confirmed 2030 EPC C policy, the insulation-halves-the-saving finding (£236→£118-153), the solar/battery seasonal-mismatch reconciliation, the real winter-concentration figures (52.9% in 4 months, £123 vs £77/month), the sourced fuel-poverty self-disconnection evidence (paraphrased rather than quoted at length, to stay within safe copyright bounds), and the heat pump running-cost/capex split. Both charts (`fig3_scenario_comparison.png`, `fig4_full_comparison_with_heatpump.png`) embedded in the article with clear placement markers, since LinkedIn's article editor supports inline images but markdown image syntax won't render directly when pasted — noted this for the user.

Kept the "existential crisis" framing calibrated in the public-facing copy too, consistent with how it was handled in-chat — the article explicitly says "I'd stop short of calling this existential... but it's a real, quantifiable, and currently under-examined compliance risk," matching the honest-not-oversold register the whole project has used throughout.

**Output:** `comms/linkedin_post_2.md`, `comms/article_2.md`.

## 2026-09-02 — First AutoMagic demo built: mobile-style PWA replaying real 2013 data

User pivoted the project's next concrete step: an Android app showing the tenant a picture of the storage heater's physical charge dial rather than abstract text, starting with a demo on existing 2013 data, later extending to a real N=1 storage heater with a self-powered wireless CT sensor (deferred — user wants the demo built first).

**Platform choice flagged explicitly, not decided silently.** A real native Android app needs an SDK/emulator this environment can't run or verify against. Proposed a Progressive Web App instead — buildable and testable here, installable to a phone home screen, wraps into native with modest extra effort later. User confirmed PWA-first.

**Built entirely from real Phase 2 output, not fabricated demo content.** Exported all 365 days of 2013 from `phase2_daily_index_2013.parquet` and ran every single day through the actual `nudge_generator.py` to get the real message text — the demo shows exactly what the real pipeline computed, not illustrative placeholder values.

**A real bug caught before publishing, the same way as everything else tonight.** First version of the dial's pointer-rotation logic used custom polar-angle and SVG arc-path trigonometry I wrote without being able to visually verify it (no browser rendering available in this sandbox). Rather than trust it by inspection, numerically verified the intended geometry in Python first (confirmed Index 1→left, 3→center, 5→right, monotonic), found the original code's angle convention didn't match, and rewrote the whole dial using a simpler, directly-verified `rotate()` transform approach instead. Cross-checked the final JavaScript by extracting and running the actual embedded script under Node.js and confirming its output matched the Python-verified reference values exactly, rather than assuming the rewrite was correct just because it was simpler.

**Publish-to-hosted-link did not complete** ("No approval received", two attempts) — handed the file directly via `present_files` instead, which works identically since a hosted link is a shareability convenience, not a functional requirement.

**Output:** `comms/automagic_demo.html` — a self-contained, installable single-file PWA. Structural checks passed (balanced tags, valid embedded JSON, all 365 days present, all index values in the valid 1-5 range) before delivery. The N=1 live CT-sensor integration remains open, deferred at the user's request.

## 2026-09-02 — Real storage heater UI checked, and it materially changed both the demo and the addressable market

**User's question, checked properly rather than assumed from memory.** Searched for real storage heater controls — both classic and "Quantum"-style — before touching the demo further.

**Classic manual heaters have two separate dials, not one.** Input (set once, evening, before bed, based on tomorrow's expected cold) and Output (adjusted through the day based on occupancy, must go to lowest before bed to conserve overnight heat). The Target Charge Index was already conceptually aligned with Input; Output was previously unaddressed entirely. Found a real housing association's own tenant guide (Yorkshire Housing, Dimplex dial-operated heater) showing the actual dial numbering: **1–6, not 1–5** — the demo's dial was built on an unchecked assumption.

**Dimplex Quantum is not a fancier display on the same idea — it already does most of what AutoMagic does.** Its "iQ Controller" uses self-learning algorithms to automatically adjust overnight charge based on recent usage and weather, and RF-enabled models have their own companion app (Dimplex Control). Dimplex's own marketing claims ~27% savings over standard storage heaters on Economy 7 (treated as a marketing claim, not verified data, but still a manufacturer betting commercially on the same core thesis this project rests on). Quantum's own positioning — "the perfect upgrade for static storage heaters" — confirms **AutoMagic's real addressable market is specifically legacy dial-controlled heaters**, which is exactly the population the 2013 LCL data and this whole project's confirmed households represent. Not a threat to the project; a sharper, more accurate scope for it.

**Rebuilt the Index calibration as genuinely 6 bands, not a rescaled 5-band system.** `target_charge_index.py`'s `N_BANDS` was already a parametric constant (not hardcoded elsewhere) — changed 5→6, reran the real calibration build against Phase 1's actual data. Caught two stale hardcoded test values left over from the old band count during the rerun (`== 5` in a monotonicity boundary check, `target_charge_index=6` used as the "invalid" test case in `nudge_generator.py`, both now genuinely wrong given 6 is a valid band) — fixed both rather than leaving a broken safety net in place.

**Added the previously-missing Output-dial guidance**, and re-ran the Flesch reading-level self-test on all new copy — caught the first draft of the new Output reminder at 66.7 (below the 70 target), simplified it, re-verified at 77.0. The check keeps finding real problems, not just passing everything by default.

**Rebuilt the demo's dial geometry for 6 positions**, verified numerically in Python exactly as before (not trusted by inspection), then cross-checked by extracting and running the actual embedded JavaScript under Node and confirming the output matched the Python reference exactly. Regenerated all 365 days of demo data through the real, updated pipeline (6-band index, output-dial-inclusive messages). Full structural and range validation passed before delivery.

**Output:** updated `comms/automagic_demo.html`, `src/target_charge_index.py`, `config/phase2_nudge_copy.py`, `src/nudge_generator.py`. The Quantum/addressable-market finding is a strategic note for the user's own product positioning, not something requiring further code changes.

## 2026-09-02 — Second dial added: honest about what's forecast-driven and what isn't

User confirmed the two-dial expectation and asked for the Output dial to be shown too, with guidance that it should only move if the room actually feels cold.

**Deliberately did not invent a computed Output recommendation.** Phase 1's validated data only covers the overnight charge decision (Input) — there is no tested per-day Output/release schedule to compute from. Rather than fabricate a plausible-looking daily number for a dial the project hasn't actually modelled, the Output dial shows a fixed, general-guidance position (2 of 6 — "low but not off," consistent with published manufacturer advice found earlier in the session) with copy stating plainly that this is general guidance, not a forecast, and AutoMagic doesn't yet calculate a daily output setting. Honest scope-limiting over a more impressive-looking but unvalidated feature.

**Reused the already-verified dial geometry rather than duplicating it.** Parametrized `buildTicks()` and added a shared `setDial()` function by element-ID suffix, so both dials run through the exact same, already-numerically-verified rotation math — avoids the risk of a second, independently-written (and independently-buggy) copy of the trigonometry.

**Full verification pass repeated, not skipped because it "should" still work.** Structural checks confirmed every dynamic-suffix ID (`ticks`/`ticksOut`, `pointer`/`pointerOut`, `dialNumber`/`dialNumberOut`) actually resolves in the HTML for both dials. Extracted and ran the real embedded JavaScript under Node again, this time specifically checking that the Output dial's fixed position (2) lands on the visually-correct low/left side of the dial, not just that the code runs without erroring.

**Output:** updated `comms/automagic_demo.html`, two dials, both verified.

## 2026-09-02 — Third LinkedIn post and article: market sizing and the Warm Homes Plan clarification

User wanted the market-sizing findings (136,500 HA homes, NEA validation) and the Warm Homes Plan £442 investigation documented publicly, framed around "identifying the costs is edifying" — i.e. the value is in clearly explaining where a headline government figure actually comes from, not just restating it.

Built one chart with two panels: the real £154 breakdown (£88 Renewables Obligation shift, £59 ECO ending, £7 VAT, sourced directly from gov.uk's own calculation) and the additive relationship between the Warm Homes Plan's price cut (£442) and AutoMagic's timing/waste fix (£236), summing to £678 — not competing claims, genuinely different mechanisms stacking.

Both pieces lead with the "does this make the project redundant" question honestly, rather than avoiding it, then walk through why the answer is no with the real mechanism distinction (price-per-unit vs. usage-timing) rather than asserting it. Market-sizing figures (1.7M UK-wide, 136,500 HA-specific, NEA's independent fuel-poverty validation) folded in as the second half of the piece, tying "how big" to "not already solved" as one coherent argument.

**Output:** `comms/linkedin_post_3.md`, `comms/article_3.md`, `comms/fig5_warmhomes_breakdown.png`.

## 2026-09-02 — First article/post revised: user was right, it was thin

User's critique: the first article leaned on one narrow point and treated "storage heaters cost more than gas" as an aside rather than a measured finding, and didn't establish scale or the human cost of the structural cost gap.

**Substantially rewritten, not just patched.** Added three new sections to `article.md`: market sizing (1.7M UK-wide, 136,500 HA-specific, NEA validation — pulled forward from the later market-sizing research), a proper gas-vs-electric comparison table (previously the £313 gap was stated narratively with no supporting table), and a new "rational response" section using the real fuel-poverty self-disconnection evidence (paraphrased, not quoted at length) tied explicitly to Awaab's Law. `linkedin_post.md` revised to match — now previews all of this rather than just the original two findings.

**Caught a real staleness issue while revising, not introduced by this edit but overdue for a fix.** The "what's actually built" section still described a "five-level charge target index" — correct when originally written, but the Index was rebuilt as six levels during the later dial-numbering correction (matching the real 1-6 Dimplex dial found in a housing association's tenant guide). Checked the other two articles/posts for the same staleness before calling this done — none found.

**Output:** revised `comms/article.md` (1,139 → ~1,550 words) and `comms/linkedin_post.md`, both updated in the organized collection package.

## 2026-09-02 — Fourth post and article: the rational economics of point heating

User wanted a dedicated piece on energy poverty, mould, Awaab's Law, and the rational logic behind tenant point-heating decisions — distinct from article 1's supporting section on the same evidence, built around a sharper, previously-unstated framing.

**The core finding, computed directly rather than asserted:** ranked the four heating scenarios already established this session by cost — point heater + electric blanket (£280) comes out cheaper than gas (£378), which is cheaper than fully-optimised AutoMagic (£691), which is cheaper than unmanaged storage heating (£927). Point heating isn't a corner-cutting compromise next to the smart system this project is building — it's arithmetically the cheapest option on the entire table, including cheaper than gas. That's the fact the whole piece is built around: not "tenants sometimes make bad choices under pressure" but "point heating is the objectively correct answer to pure cost-minimisation," which reframes under-heating from irrational behaviour to a rational response to bad underlying economics.

Built one horizontal bar chart ranking all four costs, with the comfort/safety caveat kept directly in the chart's own caption rather than left to surrounding text.

**Reused, not re-derived, the fuel-poverty evidence already sourced and logged** (the peer-reviewed cold-period self-disconnection finding, the 53%-cut-usage/35%-cold-damp-home survey data) — paraphrased again rather than quoted at length, consistent with copyright practice throughout.

**Core argument of the piece:** Awaab's Law creates a specific, uncomfortable inversion — the tenant's own rational cost-minimising choice is precisely the behaviour that produces their landlord's statutory liability. Concludes that this reframes the fix as an engineering/policy problem (cheaper running costs, better insulation) rather than a communication one — you cannot educate someone out of a decision that was already correct for them.

**Output:** `comms/linkedin_post_4.md`, `comms/article_4.md`, `comms/fig6_rational_point_heating.png`.

## 2026-09-02 — N=1 live validation reframed: user's own installed Dimplex Quantum heaters

User revealed they personally have Dimplex Quantum storage heaters installed, found them expensive, and have been letting the iQ self-learning controller run unmanaged — proposed testing what it actually delivers with a CT sensor. This is a stronger N=1 opportunity than the original "find an external heater" plan: it directly tests Dimplex's own marketing claim (self-learning, weather-responsive charge control, ~27% savings vs. standard heaters) flagged as unverified in the 2026-09-02 Quantum research entry above, on a real, immediately available system.

**Checked real energy-harvesting CT sensor options before recommending anything, rather than gesture generically.** Three real candidates found:
- **myenergi harvi** — real UK product, genuinely energy-harvesting, but confirmed via myenergi's own forum response that it cannot function standalone: "the Harvi just passes values to the Zappi or Eddi, which then processes the data." Requires owning one of those already. Data access is cloud-mediated; myenergi explicitly declined a "local open API" feature request.
- **Pressac** — genuinely wireless/self-powered (EnOcean STM300 module, AES-128 encrypted telegrams, ISM band), reports every 30 seconds (finer than this project's half-hourly convention — needs aggregating before feeding the existing pipeline). Direct sales restricted to business customers, which is exactly why the user's find (RS Components/Farnell as legitimate distributors) matters. Flagged a real nuance: Pressac's own docs frame their branded EnOcean USB stick as a commissioning tool, with ongoing data expected to route through their proprietary Gateway product — but EnOcean is an open standard, and a real, maintained open-source Python library (`enocean` on PyPI) can receive/decode telegrams from a generic EnOcean USB receiver directly, no Pressac gateway or cloud account needed, matching this project's local/self-hosted approach throughout. Told the user to confirm which type of dongle the specific RS/Farnell listing actually is before ordering.
- **Shelly 3EM** — surfaced directly in the myenergi forum thread as an alternative. Same product family and local JSON-RPC API pattern already verified and coded against in Phase 3's `bench_harness.py`, but needs a mains connection for the main unit (not genuinely battery-free/wireless the way harvi/Pressac are) — flagged as an open item to confirm precisely, not assumed.

**Analysis plan sketched, reusing Phase 1's methodology directly rather than designing something new:** once real data exists, fit the user's own home's charge-vs-weather relationship using the identical per-household regression approach built for the 2013 LCL households, and check whether nights get flagged as overcharged the same way — a direct, checkable test of whether Quantum's self-learning claim holds up or shows the same waste pattern under a smarter-looking interface.

**Not yet decided:** which hardware path to pursue. Asked the user directly rather than picking one.

## 2026-09-02 — Report updated: prices-vs-behaviour clarification added (Section 4.4)

User asked directly whether inflation was missing from the £117/household figure. Checked the actual code rather than answered from memory: confirmed 18.73p is Ecotricity's real rate effective 1 April 2026, not the 2013 LCL trial's actual rate (14.228p, a different figure never used for the headline number) — every £ figure in this project prices 2013's physical kWh quantities at real, sourced 2026 rates throughout, so no adjustment was missing.

The more useful, related point raised in response: the real open question isn't pricing, it's whether 2013's *behaviour* (the physical kWh pattern itself) generalises to today, given 2013 predates the price pressure that would be expected to drive under-heating/self-rationing. User connected this to the 2026-09-02 multi-year finding above (2013 colder than all of 2020–2025) — two independent reasons, one behavioural and one meteorological, both pointing toward the £117 figure being an upper bound rather than a typical-year estimate.

Added as new Section 4.4 in `reports/Phase1_Data_Report.docx` ("What's Current Here, and What Isn't"), placed immediately after the £ result table rather than left for a reader to infer — states plainly that prices are current (2026) and quantities are 2013, gives both reasons explicitly with the real multi-year figures cited, and closes with a bolded one-sentence conclusion. Added a corresponding Limitations bullet cross-referencing the section. Rendered to PDF and visually verified before delivery, per standard practice — both the new section and the bolded conclusion render cleanly.

Folded straight into `reports/Phase1_Data_Report.docx` as two new sections (5. Storage Heating vs. Gas: The Structural Cost Gap; 6. Under-Heating and Fuel Surrender Risk), per explicit user request. Report now 8 pages.

Section 5: the Gas/Economy7/Optimized comparison table already computed, with every input traced to its source (Ecotricity for both gas and electricity rates, this project's own S_night findings for the night/day split, the real winter Agile data for the "optimized" figure) — only the 4,500 kWh/year demand figure is flagged as illustrative/unsourced, matching the user's own framing of it as an assumption.

Section 6: presents Signature A's null result plainly (6.1), states the 2013-vs-today price-era caveat as its own bolded, impossible-to-skim paragraph per the user's explicit request rather than a footnote (6.2), then pivots to the structural £313/year gap as the stronger, behavior-independent evidence for Awaab's Law risk (6.3) — a property-level risk factor that doesn't depend on catching any specific tenant in the act. Limitations section extended with two new bullets covering the illustrative demand figure and the 2013-specific scope of the null result. Executive summary updated to surface both findings up front rather than leaving them buried in the body.

Verified by rendering to PDF and checking every page image before delivery, per the docx skill's standard practice — confirmed the bolded caveat renders correctly and the new tables display cleanly.

User uploaded `open-meteo-51_49N0_16W16m.csv` — 365 rows, London (51.49°N, -0.16°W, 16m elevation), daily mean temperature, 2013-01-01 to 2013-12-31, clean structure (3 metadata lines, then a header, then data). Confirmed usable directly.

## 2026-08-31 — Captured for later: relative humidity / Awaab's Law angle

User's idea: extend the analysis to relative humidity, since a dehumidifier can lower the heat needed for comfort and reduce mould risk — a live concern for HAs and landlords under Awaab's Law (Social Housing (Regulation) Act 2023, statutory timeframes for fixing damp/mould hazards).

**Not a new tangent — connects directly to an already-flagged gap.** METHODOLOGY.md's Phase 2 section (§2.3, "No unsourced physiological claims") already flags the nudge copy's "lower humidity makes 18°C feel like 21°C" claim as unsourced and requiring either a cited psychrometric standard or softened wording. Real humidity data would be the actual fix for that flag, not scope creep.

**Two things worth being upfront about before this becomes a task:** (1) Open-Meteo carries relative humidity as a standard hourly variable — same access pattern already proven for temperature, no new blocker expected. (2) It would be *outdoor* humidity; mould/condensation risk is driven by *indoor* humidity, which depends on ventilation, occupancy, and moisture-generating behaviour that LCL (electricity-only, no indoor sensors) cannot observe. Outdoor humidity could serve as a contextual covariate, not direct proof of indoor risk — a distinction worth keeping explicit given Awaab's Law is exactly the kind of area where an overstated claim is a real problem. Not pursued now; Phase 1's deliverable is the overcharge/exhaustion gap. Flagged here so it isn't lost and is ready to pick up against the already-existing METHODOLOGY.md §2.3 item when relevant.


