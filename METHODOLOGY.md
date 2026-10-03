# METHODOLOGY.md: storage-heater-vpp-ha

Companion to `PROJECT.md` (the governing constitution and project spec). Where `PROJECT.md` says *what* each phase must prove and what "done" looks like, this document says *how* — the actual technical method for each phase, written before any code exists so the method can be reviewed and argued with before it's built. Every method below inherits `PROJECT.md`'s Golden Heuristics (§2), the Universal 6-Stage Pipeline (§3), and the coding standards (§4–5); this document doesn't repeat those, it applies them.

---

## Phase 1 — Proving the Gap (NILM Disaggregation)

### 1.1 Data ingestion and schema (Stage A)

Load the Low Carbon London half-hourly CSVs (`LCLid`, timestamp, `KWH/hh`) into Polars, one household at a time (streaming, not a single giant join — see `PROJECT.md` §4.2). Schema-check on load: timestamps are contiguous half-hour steps with no unexplained gaps larger than a defined tolerance (flag and report gap-affected households separately, never silently interpolate over a gap this large).

### 1.2 Identifying the Economy-7/storage-heater sub-population

**Correction to the original outline, logged in `PROJECT.md` §9.3:** there is no pre-existing "has storage heater" column. Identification *is* the disaggregation step, done in two passes:

1. **Coarse screen.** Flag households whose mean overnight (23:00–07:00) demand exceeds a threshold (e.g. 1.5kW average) *and* whose overnight-to-daytime demand ratio is unusually high relative to the whole panel — a cheap, vectorized filter to cut the household count before the more expensive per-household signature check.
2. **Signature confirmation.** For each flagged household, run a simple, auditable rule-based detector (Sledgehammer Test, `PROJECT.md` §2.2) before considering anything more elaborate:
   - Compute a rolling 7-day trailing minimum load curve per half-hour-of-day as a baseload proxy (captures fridge/freezer/standby, which cycles at a much shorter period than a storage heater's charge block).
   - Subtract the baseload proxy from the raw trace.
   - Flag a "charge event" where the residual holds within a defined band (e.g. 1.8–3.2kW, adjustable per §9.5's assumption that this band is plausible but untested) for at least 3 consecutive half-hour periods within the 23:00–07:00 window.
   - A household qualifies as "likely storage-heater" if charge events occur on a majority of nights across at least one full heating-season month.

**Pre-mortem check (do this before writing the detector):** manually plot 10–20 raw traces from the coarse screen and eyeball them first. If the charge-block pattern isn't visually obvious on real traces, that is Phase 1's first finding — report it, do not force a detector to find a pattern that isn't there (`PROJECT.md` §2.8).

**Validation, if available:** cross-check a subsample against any household survey/appliance-ownership metadata that ships alongside LCL or a comparable dataset (e.g. the DECC/BEIS Household Electricity Survey has some appliance-level ownership flags on a smaller sample) — even a small labelled subsample is enough to sanity-check the detector's false-positive rate. If no such subsample exists, say so explicitly rather than reporting an unvalidated detector as ground truth.

### 1.3 Quantifying the operational gap (Stage B)

For each confirmed household-night:

- **Overcharge test.** Compute the night's total charged kWh. Compute a modelled "required" kWh from that day's heat-loss, using a simple degree-day proxy: `heat_loss_proxy = max(0, base_temp - mean_daily_temp) * a_constant`, with `base_temp` set to the UK heating-degree-day convention (15.5°C) unless Phase 1's own data suggests a different empirical base — this constant is exactly the kind of thing that belongs in named config, not a magic number (`PROJECT.md` §5.6). Flag a night as "overcharged" where actual charge exceeds modelled requirement by a defined margin.
- **Afternoon exhaustion test.** Model stored heat as a simple first-order decay from the morning's charge level. Independently detect "boost" usage as a *second, distinct* load signature in the 16:00–20:00 window — different wattage band and shorter, more irregular pulses than the overnight block, consistent with a resistive boost heater rather than the storage unit itself. Cross-tabulate boost-usage nights against the decay model's predicted "run-out" time and against that day's temperature, to test whether exhaustion tracks cold snaps (mechanism) rather than showing up randomly (no mechanism → the model doesn't have a story, and shouldn't claim one).

### 1.4 Reprojecting onto current £ (Stage B → communication)

The LCL data is priced at 2011–2013 trial rates internally; do not report the headline £ finding in trial-era prices. Recompute using: (a) a current Economy 7 day/night rate pair (sourced from a current supplier tariff, cited) for the "as billed under a static tariff" comparison, and (b) current Octopus Agile half-hourly historical prices for the "what a smarter timing could have captured" comparison. Report both — the gap between them is Phase 2's opportunity, not Phase 1's finding.

### 1.5 Output contract

`data/intermediate/phase1_household_nights.parquet` — one row per confirmed household-night: date, household id, overnight charge kWh, modelled requirement kWh, overcharge flag and magnitude, boost-usage flag and kWh, mean daily temp, £ under current Economy 7, £ under current Agile actual prices. This is the single artifact Phase 2 reads from.

---

## Phase 2 — Behavioural Nudge Engine

### 2.1 Thermal forecast engine

Pull Open-Meteo historical-forecast data (temperature, wind speed, solar radiation) for the target region. Compute a daily heat-loss proxy using the same degree-day method as Phase 1 §1.3, plus a wind-chill adjustment term — this must use the *same* proxy formula as Phase 1, not a separately-invented one, so the Target Charge Index below is actually calibrated against what Phase 1 showed really happened, not a fresh assumption (`PROJECT.md` §2.6, Mechanism Before Model).

### 2.2 Target Charge Index (1–6)

Calibrate the six index bands from Phase 1's own empirical distribution of (heat-loss proxy → actual overnight charge needed to avoid both overcharge and afternoon exhaustion), not from round numbers chosen for a demo. Document the calibration table in `data/intermediate/phase2_index_calibration.parquet` so it's auditable against Phase 1's output.

> **Correction, 2026-09-02 (see `evidence_map.md`):** originally specified as 1–5 bands here. Corrected to 1–6 after the real physical dial numbering was confirmed against a real housing association's Dimplex heater tenant guide -- `control_logic.py` and `nudge_generator.py` were already built and shipped against the corrected 1–6 scale; this document had not been updated to match until now.

### 2.3 Nudge copy generation

Message templates are driven by the index value and the forecast, using a lookup table (config, not inline strings scattered through code). Two content rules:

- **No unsourced physiological claims.** The humidity/comfort nudge in the original outline ("humidity is high today; running your dehumidifier will make 18°C feel like 21°C") states a specific, quantified perceived-temperature effect. Before this ships in tenant-facing copy, either cite a specific psychrometric/thermal-comfort standard (e.g. an operative-temperature or apparent-temperature model) that supports a number of that magnitude, or soften the copy to a qualitative claim ("lower humidity can make the same temperature feel warmer") until it's grounded. This is a `PROJECT.md` §20 (voice) and §2.10 (verify the verifier) issue, not a copywriting nicety — a wrong comfort claim to a tenant is a credibility problem, and potentially a vulnerable-tenant welfare problem if it's wrong in the direction of encouraging someone to run their heating lower than is safe.
- **Plain, short, second person.** Tenant-facing copy is its own register (`PROJECT.md` §20) — shorter and plainer than any of this project's other written material, tested for reading level.

### 2.4 Compliance and financial-impact simulation

Not a full Monte Carlo — per the Sledgehammer Test, a scenario grid is enough: cross tenant compliance rate (10/30/50%, explicitly labelled as illustrative bounds per `PROJECT.md` §9.5 item 4) against multiple historical weather years (to avoid overfitting the saving estimate to one unusually mild or harsh winter) and real Octopus Agile historical half-hourly prices (never a flat assumed price). Report the resulting annual saving as a range across this grid, not a single point estimate — this is Stage F's P10/P50/P90 spirit implemented at the complexity level the question actually needs (§2.2).

### 2.5 Output contract

A working notification-generation function (testable with a fixed weather/index input → deterministic message output, per `PROJECT.md` §5.5 deterministic-baseline-before-randomness) plus `data/intermediate/phase2_savings_by_scenario.parquet`.

---

## Phase 3 — Hardware Bench-Test Protocol

### 3.1 Rig assembly

Relay (Shelly Pro 1PM or an equivalently-specified DIN-rail metered relay — confirm any named alternative, e.g. Sonoff, against its actual spec sheet before naming it, per `PROJECT.md` §9.8 item 4) switching a low-power dummy load (a lamp, not a real heater) from a standard plug — this rig never touches heater-rated current or a live consumer unit. A Zigbee/Wi-Fi temperature and relative-humidity sensor provides the environment input.

### 3.2 Control logic (ported directly from Phase 2's calibration, not reinvented)

Pseudocode for the three interacting rules:

```
if current_time in off_peak_window (config, default 00:00-05:00):
    relay_state = ON  # charge
elif manual_override_active:
    relay_state = ON  # tenant boost, time-limited (config, default 30 min)
else:
    relay_state = OFF

# Comfort cutoff overlays the above, does not replace it:
if measured_RH < rh_threshold (config, default 50%) and not manual_override_active:
    target_setpoint = reduced_setpoint  # e.g. 18.5C — pending Phase 2 psychrometric grounding
else:
    target_setpoint = normal_setpoint  # e.g. 21.0C
```

Every constant above is named config (`PROJECT.md` §5.6), not hard-coded, so the bench test can sweep them.

### 3.3 Bench test matrix

Before any live install is considered, script and run at least these scenarios on the bench, logging relay state, dummy-load power, and sensor readings throughout: (1) a simulated cold night — verify full off-peak charge; (2) a simulated mild night — verify reduced/no charge if the Phase 2 index says so; (3) a manual override request mid-afternoon — verify the timed bypass engages and lapses correctly; (4) a sensor dropout — verify the control logic fails safe (defaults to normal setpoint and standard off-peak charging, not to "heater off") rather than failing silently.

### 3.4 Safety and compliance

This project can produce a documented, testable prototype and an estimated installation method and time. It cannot self-certify BS 7671 compliance. Before Phase 3 is called done, get the proposed install method reviewed by a qualified electrician, and replace the illustrative "~20 minutes per flat" figure with their estimate or a logged range.

### 3.5 Output contract

Bench-test log data, the control-logic code (unit-tested against the matrix in §3.3), and a real (not assumed) per-property Bill of Materials and install-time estimate for Phase 4.

---

## Phase 4 — VPP Financial Model

### 4.1 Bottom-up CapEx

Relay/sensor cost × home count, using Phase 3's actual BOM (§3.5), not the original outline's illustrative £150/home. BESS installed cost (£/kWh and £/MW) benchmarked against a current, cited UK BESS cost source — do not carry the outline's £1.2–1.5M figure forward without one.

### 4.2 Revenue stack, modelled per stream, then checked for stacking conflicts

- **Wholesale/intraday arbitrage:** simulate against real historical half-hourly price spreads (the same Agile-style data used in Phase 2), applied to the battery's actual charge/discharge envelope net of the thermal load it's also serving.
- **NESO Balancing Mechanism:** model only after checking the specific current access rules for aggregated small assets (`PROJECT.md` §9.3's NESO references) against the modelled fleet's size and metering arrangement — this is a live, changing rule set, re-verify at the time Phase 4 actually starts rather than trusting this document's snapshot.
- **DNO local flexibility (constraint payments):** model using published local flexibility tender clearing prices (e.g. Piclo Flex auction history) for the DNO licence area of whatever candidate HA estate is chosen (`PROJECT.md` §9.8 item 3) — not a national average.
- **Stacking-conflict check:** explicitly encode that the asset can only follow one dispatch instruction per half-hour period; build a simple priority rule (e.g. firm DNO/BM commitments take precedence over opportunistic arbitrage) rather than assuming all three revenue streams are simultaneously additive.

### 4.3 Thermal load decoupling

Enforce in the scheduler, not just assume: space-heating charge is locked to off-peak grid power (never drawn from the battery), and the battery scheduler treats 16:00–20:00 as a protected discharge window, targeting ≥80% SoC entering it (config, sweep this in sensitivity testing rather than treating 80% as fixed).

### 4.4 Returns

Standard discounted cash flow over a stated horizon (10 years, matching the outline), Monte Carlo over price and dispatch-volume uncertainty (Stage F), reporting IRR/NPV/payback at P10/P50/P90 — and reporting plainly, per `PROJECT.md` §2.8, if the central case doesn't clear a reasonable hurdle rate for an HA investment committee. A smaller, honest case is more useful here than an inflated one.

### 4.5 Output contract

The financial model code and assumptions config, plus a results table suitable for direct inclusion in Phase 5's board material — every number in that table must trace back to a cell or function here (`PROJECT.md` §6, Traceability Mandate).

---

## Phase 5 — HA Implementation Roadmap

Not a modelling phase — a communication and governance phase, governed by Part 8 of `PROJECT.md` rather than the 6-stage pipeline.

### 5.1 Structure

Translate Phase 4's financial model into a staged path: a small pilot (illustratively 10–20 homes) with explicit go/no-go scale-gate criteria (e.g. measured savings within a defined tolerance of modelled, tenant satisfaction above a threshold, no safety incidents), followed by scale-up tranches, then business-as-usual operations and maintenance.

### 5.2 Governance and risk register

Cover explicitly, not implicitly: procurement route (framework agreement vs. direct tender), tenant consent and data protection (smart-meter data access is personal data — a GDPR basis is needed before any real tenant data is touched, not just open datasets), safety sign-off (BS 7671 certification per installed property, not just the bench-tested design), and financial risk allocation (does the HA carry BESS merchant-price risk directly, or route it through a third-party operator/ESCo model — state which, and why).

### 5.3 Deliverable register

Board-facing material for Phase 5 uses the HA-investment-board voice (`PROJECT.md` §20) — confident, numerate, decision-oriented, with the full model available as backup but not as the primary document a board member reads cold.

---

## Cross-Phase Notes

**On the Assumptions Ledger (`PROJECT.md` §9.5):** every numbered assumption there maps to a specific step above where it either gets tested or gets explicitly replaced with a real, sourced figure. Treat any number in the original outline that hasn't been replaced by the time a phase is marked done as a red flag, not a rounding convenience.

**On sequencing:** each phase's output contract is the next phase's required input. Do not start Phase 2's compliance simulation on assumed savings while Phase 1 is still open, and do not build Phase 4's revenue model on Phase 3's illustrative BOM once a real one exists.
