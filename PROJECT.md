# PROJECT.md: storage-heater-vpp-ha

**Status:** Scoping — Phase 1 not yet started
**Purpose:** Define the research logic, verification discipline, and communication guardrails for a four-stage-becomes-five-stage project: proving that unmanaged electric storage heating wastes money and comfort, testing whether behavioural nudges close that gap cheaply, bench-testing a low-cost hardware retrofit that closes it automatically, and building the financial case (and then the implementation path) for a Housing Association to turn that retrofit fleet into a revenue-generating Virtual Power Plant (VPP) asset — under the universal engineering constitution below, the same constitution developed for `thermal-counterfactual-gb` and reused for `negawatt-bridge-medai` and `ofgem-curate-response`, reused here again as a matter of discipline, not copied for convenience.
**Core Philosophy:** *Physical reality and auditable math always trump software illusions. We do not build analytical black boxes. We build transparent, reproducible, and physically grounded frameworks. A finding that says "no" is as complete as one that says "yes." A claim from anywhere other than a primary source — including this project's own earlier drafts — is not a fact until it has been checked against one.*

---

# Part 1 — Project Definition & Scoping

## 1. The Project Definition Template

Every project must begin by explicitly defining its scope, avoiding the trap of solving every problem at once.

1. **The Core Thesis:** A single, punchy sentence defining the gap between theory and physical reality.
2. **The Empirical Deliverability Question:** Do not ask if a concept exists in theory. Ask if the physical assets can *actually deliver* the required service when real-world constraints, consumer behaviour, and hardware limits are applied.
3. **The Boundary of the Model:** Explicitly state what the model *does not* do.

---

# Part 2 — Research Philosophy

## 2. The Golden Heuristics

Non-negotiable rules for all modelling, simulation, and analytical work.

### 2.1 Physics Before Economics
Physical feasibility and system need must be established before economic conclusions are drawn. Do not jump directly to NPV, revenue sufficiency, or market design before establishing the physical and technological logic.
*Always begin with: What is constrained? Where? Which direction is power flowing? Can the asset physically perform the action?*

### 2.2 The 'Sledgehammer' Test (Simple Before Complex)
Use the simplest credible method that answers the question. Before implementing advanced algorithms, ask: *"Can a simple, auditable, rule-based or multiplicative model answer the core question?"* If yes, the simple model must be used. Complexity is only justified if it solves a specific, documented gap that the simple model cannot address.

### 2.3 The Physics/Derating Separation (No Double-Counting)
Internal physical constraints must be modeled directly within the core simulation ($P_{simulated}$). Post-hoc derating multipliers ($\eta$) are strictly reserved for external network, operational, or behavioral frictions.

### 2.4 The Anti-Correlation Stress Test
Any flexibility, reliability, or risk model must include a "worst-case correlation" scenario. If a model only tests average conditions, it is over-promising and will fail in the real world.

### 2.5 Time Flows Forwards (Zero Look-Ahead Bias)
No variable, feature, or model input may use information unavailable at the decision timestamp. Strict temporal train/test splits are mandatory.

### 2.6 Mechanism Before Model
Every model result must be attached to a physical or economic mechanism. Use the project loop: *Model result → discomfort → mechanism → sensitivity → policy lever → caveat*.

### 2.7 Ambiguity Is Informative
Treat uncertainty as a signal that understanding is incomplete. Do not force interpretations before sufficient evidence exists.

### 2.8 A Null Result Is a Deliverable
A model that honestly finds "this doesn't work," "the effect is smaller than the claim," or "the answer is a shrug" has done its job. Do not keep adjusting scope, assumptions, or framing after a run until the answer looks better — a null or unfavourable result is reported with the same confidence, the same traceability, and the same visibility as a favourable one.

### 2.9 The Efficiency Paradox Clause
Any model that projects a future load and freezes it as a static number for the modelling horizon must explicitly flag two countervailing, exogenous risks: the engineering deflation of that load and the behavioural inflation of that load. Do not build a multi-year technology-forecasting model to resolve which risk dominates — flag both, bound them qualitatively, and move on.

### 2.10 Verify the Verifier
A claim arriving via external feedback, a search engine's synthesized answer, another analyst's review, or this project's own earlier draft is not a source — it is a lead. Before it is used, it must be traced to and confirmed against its own primary document, not accepted because it sounds specific, cites a real-sounding name, or agrees with what was already believed. Where a new claim contradicts something already sourced in this project, the contradiction is resolved by re-checking the primary source directly, not by preferring whichever version arrived most recently or most confidently.

---

# Part 3 — Analytical Design

## 3. The Universal 6-Stage Pipeline

### Stage A: Empirical Ground Truth
Build the empirical event log or raw data foundation. Preserve empirical correlation between variables. Do not use synthetic data before building the empirical register.

### Stage B: Temporal & Distributional Analysis
Characterise the data by time, season, duration, and severity.

### Stage C: Physical / Synthetic Asset Modelling
Model the physical assets. Do not treat different seasonal services as equivalent. Explicitly model hardware/fabric differences where relevant to the physical outcome.

### Stage D: Dispatch & Scenario Modelling
Run multiple scenarios on the same synthetic fleet/population so differences are attributable to dispatch/policy rules rather than portfolio composition.
1. **Baseline/Naive**
2. **Theoretical Ceiling**
3. **The Realistic Hybrid (Central Case)**
4. **The Anti-Correlation Stress Test**

### Stage E: Value Gap & Derating Framework
$$P_{effective} = P_{simulated} \times (\eta_{thermal} \times \eta_{phase} \times \eta_{comms} \times \eta_{primacy})$$
*Never double-count internal physics here.*

### Stage F: Monte Carlo & Uncertainty Propagation
Simple vectorized Monte Carlo (e.g., NumPy) is the primary uncertainty framework. Always calculate and report **P10, P50, and P90**, not just point estimates.

## Analytical Principles: Feynman Approaches

1. *"You must not fool yourself — and you are the easiest person to fool."* Every assumption documented, every number traceable, invite adversarial review.
2. *"What I cannot create, I do not understand."* Build the physical model from first principles rather than citing a headline number.
3. *"Knowing the name of something is not the same as knowing something."* Decompose "flexibility" into its physical mechanisms.
4. *"Reality must take precedence over public relations."* The physics doesn't care about the pitch deck.
5. *"I would rather have questions that can't be answered than answers that can't be questioned."* State what remains unknown at every stage.
6. *"Explain it simply."* If it can't be explained to a housing officer or tenant in one breath, it isn't understood well enough to model.
7. *"Shut up and calculate."* Run the numbers rather than hand-wave.
8. **Map vs. territory.** The model is a map. Never confuse it with reality.

---

# Part 4 — Engineering & Programming Discipline

## 4. The Modern Stack & Environment Rules
- **Environment Management:** `uv` strictly enforced.
- **Dataframes:** Polars strictly enforced over Pandas.
- **Math/Simulation:** NumPy (vectorized), SciPy (distributions).
- **Visualization:** Matplotlib (publication-ready).

### 4.1 Environment Locking & Isolation
Notebooks execute via the project-specific virtual environment. Cross-project kernel usage prohibited. First cell verifies the active Python executable path.

### 4.2 The Parquet Handoff Rule
Notebooks must not pass massive dataframes in memory across stages. Minimum 4 modular notebooks. Each saves output to `data/intermediate/*.parquet`; the next reads from it.

### 4.3 Polars Quirks & Gotchas
- No `.item()` needed — aggregations return native Python floats.
- `.with_columns()` evaluates in parallel — cannot reference an alias created in the same block.

## 5. NASA/JPL-Inspired Coding Standards
*Make wrong results hard to produce silently.*

1. **Small Functions, Clear Contracts.** No hidden global state.
2. **Assertions Protect Physics.** e.g. `assert 0 <= soc <= 1`, `assert relay_rating_a > 0`.
3. **Fail Loudly.** No silent failures, no broad `except: pass`.
4. **Schema Before Analysis.** Explicit schema (column, type, unit, allowed range) for every intermediate dataset.
5. **Deterministic Baseline Before Randomness.** Run one transparent, deterministic example before Monte Carlo.
6. **Configuration, Not Magic Numbers.** Material assumptions live in named config, not buried in logic.
7. **Warnings Are Evidence.** Do not suppress globally.

---

# Part 5 — Communication, Traceability, & Reporting

## 6. The Traceability Mandate
Every headline metric must be reproducible via a documented, row-by-row traceability table. If a reviewer cannot reproduce your headline number in a spreadsheet in under 60 seconds, the model is a black box and is rejected.

## 7. Translate to Physical Units
Every headline percentage must be accompanied by its physical kW, kWh, or £ equivalent for the target scale.

## 8. Writing Principles: Strunk & White, Zinsser, and the Human Voice

### 8.1 Strunk & White
Omit needless words. Active voice. Positive form. Definite, specific, concrete language — "3.5%" not "approximately 3-4%". Do not overstate. Be clear.

### 8.2 Zinsser
Clarity is the foundation. Cut clutter. Write for the reader. Use active verbs. Be yourself. Simplify.

### 8.3 Modelling Prose — The Standard Pattern
Every major claim needs: **Number. Unit. Denominator. Mechanism. Scope boundary. Caveat.**

## 9. Visual Design Principles: Tufte's Standards
Maximize data-ink ratio. No chartjunk, no pie charts, no 3D, no decorative dashboards. Show the denominator. Direct-label, don't force legend eye-travel. Use small multiples for scenario comparison. y-axis starts at zero unless justified and marked. Show P10/P90 uncertainty when it affects the decision.

## 10. The README Standard
Every repository README.md includes: Core Thesis (one sentence), Traceability Table, explicit No-Double-Counting documentation, a "Limitations & Future Work" section, and at least one Tufte-compliant figure.

## 11. External Communication
Tuesday/Wednesday 8:00–9:30am UK. Link in first comment. One Tufte-compliant chart attached. Confident but humble tone, pre-empt expert critiques. Pivot to "lessons learned" framing if a technical post doesn't land.

---

# Part 6 — Forbidden Shortcuts & Known Risks

## 12. Forbidden Shortcuts
Do not: use synthetic data before the empirical register exists; double-count derating on top of physics already modeled; reach for MCMC/GANs/MILP when simple Monte Carlo or rule-based logic answers the question; treat non-equivalent seasonal/state services as equivalent; condition on post-event outcomes; hide material assumptions inside notebook cells; claim locational or tenure-specific value without an event-level or tenure-level counterfactual.

## 13. Known Risks & Mitigations
Generic risk categories: public data may not reveal the finest-grained constraint (mitigate by reporting each data granularity separately, never blended); behavioural/comfort constraints may dominate technical capacity (mitigate by modelling the comfort floor explicitly and running the Anti-Correlation Stress Test); synthetic population assumptions may overstate coordinated response (mitigate with explicit derating and P10/P50/P90 reporting).

---

# Part 7 — The Final Discipline

Do not let the model become clever before the mechanism becomes clear.

**Project order:** Physics → Event Register → Mechanism → Scenario Model → Sensitivity → Monte Carlo → Policy Lever → Caveat

**The Final Project Loop:** Model result → discomfort → mechanism → sensitivity → policy lever → caveat

---

# Part 8 — Document & Advocacy-Response Discipline

*(Carried forward from `ofgem-curate-response`, where it was written after that project's own retrospective. Parts 1–7 above were written for physical/simulation modelling; this Part covers a different failure surface — verifying externally-supplied claims and producing text or messaging that reaches a real audience, which this project needs for Phase 2's tenant-facing nudges and Phase 4/5's HA-facing financial and roadmap material.)*

## 14. External Feedback Triage (a specific case of 2.10)

Sort every unsolicited claim, "gap list," or AI-generated critique into exactly one of four buckets before acting on any of it: (1) confirmed against a primary source — usable, cite the primary source itself; (2) real but outside this project's stated scope — note it, don't act on it; (3) contradicts something already verified — re-check the primary source directly, the newest or most confident version does not win by default; (4) rests on an unverified premise or an unnamed "analysts say" authority claim — flag as unconfirmed, leave out.

## 15. Neutral-Prompt-Then-Verify

When checking a specific factual claim via search or fetch, never phrase the check in a way that states the fact being checked. Ask neutrally, and re-run with a second independently-phrased neutral prompt before treating the finding as load-bearing.

## 16. Multi-Source Corroboration for Secondary Figures

A quantitative claim that isn't itself from a primary source needs at least two independent, credible secondary sources agreeing before it's used. A claim found in only one lower-quality aggregator is excluded outright.

## 17. Document/Code-Editing Discipline

Never hand-type or transcribe a snippet that must match a source file exactly — extract it programmatically and verify uniqueness before using it to find-and-replace. Automated validation catches malformed structure, not misplaced content — the real check is rendering/running and inspecting the actual output. Never overwrite a working or frozen file; every edit round produces a new version, the previous one stays on disk.

## 18. The Running Decision Log

Keep one file (`evidence_map.md`) that every verification pass, every accepted or rejected external claim, and every material decision gets appended to as it happens. This is what makes a project resumable and a retrospective possible.

## 19. Dataset- and Snapshot-Conflation Caution

Before combining or comparing two figures, check: same snapshot date? same methodology or scope? same underlying universe? Where they aren't the same, say so explicitly rather than silently blending — and prefer the more conservative figure when one is available.

## 20. Voice by Document Type

Decide the register before drafting: a formal submission uses collective "we"; a personal-capacity letter uses first-person "I" with a signature block; tenant-facing SMS/app copy needs its own plain, short, second-person register (see Part 9's Phase 2 spec); an HA board pitch deck needs a fourth, more formal-but-persuasive register again. Mixing registers within one document reads as a drafting error.

## 21. Read the Receiving Body's Own Rules Before Drafting

Before writing anything for an external audience — a funder's application form, a regulator's submission portal, an HA board's own reporting template — extract its exact requirements first (format, word limits, required structure, any numbering/labelling scheme) rather than assuming a generic format will do.

## 22. Tool-Boundary Discipline

Know which tools operate on the actual project files and which operate on an unrelated store (a personal-memory system, a scratch workspace, a different repository). Check the result lands where intended, not just that the call succeeded.

---

# Part 9 — storage-heater-vpp-ha: Project Specification

## 9.1 Project Definition

**Core Thesis:** Electric storage heaters, run unmanaged, waste money for tenants twice over — by overcharging on mild nights and by running out of stored heat mid-afternoon, forcing a switch to expensive peak-rate resistive boost — and that same waste, once measured and closed with a cheap relay retrofit, converts a Housing Association's heating stock into a fleet of controllable, aggregatable load that can be scheduled alongside a battery asset to earn wholesale, balancing, and network-flexibility revenue.

**The Empirical Deliverability Question:** Not "could a smarter storage heater save money in theory" (obviously yes) but: does UK open smart-meter data actually show the specific overcharge/afternoon-exhaustion pattern this thesis depends on, at what magnitude, and for what share of Economy-7-type profiles — and if a hardware retrofit closes that gap, does the resulting fleet-level flexibility clear the bar (in £, in reliability, in tenant comfort) that makes a Housing Association's investment committee say yes, once every revenue stream is checked against its own real market rules rather than assumed.

**The Boundary of the Model:** This project does not attempt to redesign or replace storage heaters, does not model heat pump conversion (a different, larger capital intervention, explicitly out of scope), does not assume any specific HA's existing stock composition or transformer headroom without asking, and does not treat Phase 4's revenue-stack figures as real until each stream has been checked against its own current market-access rules (Section 9.6).

## 9.2 What This Project Is / Is Not

**Is:** An evidence-first sequence — prove the problem with open data, test the cheapest possible fix (behaviour), bench-test the next-cheapest fix (a retrofit relay), then build and pressure-test the financial case for scaling that fix into a VPP asset, ending in a concrete implementation path for a real HA board.

**Is not:** A pitch for a specific vendor's hardware, a heat-pump or fabric-retrofit business case, or a claim that VPP revenue alone pays for the whole programme — Phase 4 must show its arithmetic, including the case where it doesn't clear the bar (2.8: a null result is a deliverable).

## 9.3 Evidence Base & Source Repository

Primary data/technical sources identified and lightly verified as real and current (31 Aug 2026) before this spec was written — none yet pulled or analysed, per 2.10 this is a lead list, not yet an evidence base:

- **Low Carbon London (LCL) smart meter dataset** — ~5,500 London households, half-hourly, via the London Datastore / UK Data Service (originally an Ofgem Low Carbon Networks Fund trial, Imperial College London analysis). **Important correction to the original outline: this dataset does not arrive pre-tagged "Economy 7" or "has a storage heater."** It is anonymised half-hourly consumption plus household metadata (ACORN demographic group, some dynamic time-of-use trial participation). The Economy-7/storage-heater population must be *identified* via the NILM signature itself (originally listed as a separate "filter" step in Milestone 1 — it is actually the same operation as Milestone 2, not a prior step). Dataset period is 2011–2013, which is fine for the *timing/behaviour* finding (a storage heater's physical charge/discharge behaviour hasn't changed) but not for *current £* costs, which must be reprojected onto today's Economy 7 and Octopus Agile rates, not the trial-era prices in the raw data.
- **Low Carbon Networks Fund (LCNF), wider programme** — a real, historic (2010–2015) Ofgem-administered DNO innovation fund; LCL was one of its projects. Other LCNF/Network Innovation Allowance trials exist but data release practices vary project to project — a specific trial with usable storage-heater-relevant data has not yet been identified; treat "LCNF datasets" as a research lead for Stage A, not a confirmed second source.
- **Open-Meteo** — confirmed real, free, open-source weather API with both historical and forecast endpoints, no key required for non-commercial use. Suitable for the Phase 2 forecast engine.
- **Octopus Agile** — confirmed real, live half-hourly dynamic tariff with a public API and full historical price archive (also mirrored by third-party trackers). Suitable for Phase 2's tariff-compliance simulation and for reprojecting LCL-era costs onto current pricing.
- **Shelly Pro 1PM** — confirmed real, current product: DIN-rail-mountable, Wi-Fi/LAN/Bluetooth, 16A rated, integrated power metering. A credible bench-test relay candidate. (Sonoff's equivalent DIN-rail metered relay should be confirmed the same way before being named as an alternative.)
- **NESO Balancing Mechanism, small aggregated assets** — confirmed real and *currently in motion*: NESO has an active work item allowing aggregated small-scale (sub-1MW-class) assets into the Balancing Mechanism, including a specific "Trial of Small Aggregated Assets BMU" and a rule change reported as opening up to 300MW of flexible-asset capacity. This is genuinely useful grounding for Phase 4/5's BM revenue assumption and should be cited directly (primary NESO documents, not the trade-press summary) once Phase 4 begins.
- **DNO/local flexibility markets** — confirmed real and active (e.g. Piclo- and Electron-run local flexibility tenders that DNOs use for constraint management). Relevant to the "DNO Local Substation Constraint Payments" revenue stream, but access, clearing prices, and whether a 2.5MW fleet would actually be dispatched depend on the specific DNO licence area and substation — cannot be assumed nationally, must be checked per HA site once a candidate estate is chosen.

**Not yet checked, flagged for Phase 3/5:** BS 7671 (UK wiring regulations) compliance detail for a relay retrofit's exact installation method and the claimed ~20-minute per-flat install time; the psychrometric/comfort claim that lower relative humidity allows a lower setpoint at equivalent perceived warmth (a real physiological effect, but the specific "18.5°C at <50% RH feels like 21°C" figure in the original outline is illustrative language, not yet grounded in a specific psychrometric/thermal-comfort standard — see Assumptions Ledger).

## 9.4 Phase Mapping

| Phase | Proves | Primary Pipeline Stages (§3) |
|---|---|---|
| 1. Prove the Gap | Unmanaged storage heating has a measurable, quantifiable £-and-comfort cost, from real half-hourly data | A, B |
| 2. Behavioural Nudge | A cheap, hardware-free intervention (SMS/app) captures some of that saving, at a modelled compliance rate | A (weather), C (thermal model), D, F |
| 3. Hardware Bench-Test | A sub-£100/property relay retrofit can enforce the saving automatically and safely, on the bench, before any live install | C (physical asset), engineering discipline (§4–5) |
| 4. VPP Financial Model | A fleet of retrofitted properties, paired with a battery asset, can earn enough real (not assumed) revenue to justify the CapEx to an HA board | C, D, E, F |
| 5. HA Implementation Roadmap | The financial case in Phase 4 converts into a concrete, risk-assessed path an actual HA investment board can approve and a delivery team can execute | Communication & Governance (Part 8), not the modelling pipeline |

## 9.5 Assumptions Ledger

Every material assumption behind the original outline, stated so it can be tested rather than inherited:

1. A material share of LCL (or an equivalent) household profiles are on Economy 7 / run storage heaters — **untested**, first job of Stage A.
2. The 2–3kW continuous overnight square-wave signature is distinctive enough to disaggregate via a simple rule-based/NILM method without a labelled training set — **plausible given storage heaters' near-binary charge profile, but untested**; per 2.2 (Sledgehammer Test), try simple thresholding/edge-detection before reaching for a trained NILM model.
3. "25–40% more than modelled" (Phase 1 deliverable claim) is Andy's illustrative estimate, not yet derived from data — Phase 1's actual finding may be smaller, larger, or absent for some sub-population; report whatever the data shows (2.8).
4. Compliance rates of 10/30/50% for SMS nudges (Phase 2) are illustrative scenario bounds, not measured — label them as such until a pilot exists.
5. £80–£140/year nudge saving and the £50–£100 hardware BOM (Phases 2–3) are order-of-magnitude placeholders pending the actual bench-test and tariff simulation.
6. The 500-home CapEx (~£75k relays + £1.2–1.5M BESS) and £125k–£175k/year revenue figures (Phase 4) are illustrative, not modelled — Phase 4's actual job is to build the model that replaces these with derived numbers, including the P10/P50/P90 range (§3, Stage F) and the possibility that the answer is "doesn't clear the bar at this scale."
7. Local DNO flexibility and NESO BM access are assumed available to the modelled fleet — **must be checked against the specific DNO licence area and substation of whatever HA estate is eventually used as the worked example**, not assumed nationally portable.
8. The psychrometric comfort claim (lower RH allows a lower setpoint at equal perceived warmth) needs a cited physiological/psychrometric basis before it appears in any tenant-facing copy (Part 8, §20 voice discipline — a wrong comfort claim in tenant messaging is a credibility and possibly a safety issue, not just a modelling error).

## 9.6 Response Plan & Definition of Done, by Phase

**Phase 1 — done when:** the NILM disaggregation is applied to a real dataset, a documented, reproducible overcharge/afternoon-exhaustion pattern is either found or not found, and — whichever it is — the finding is written up with the same rigour either way (2.8), reprojected onto current tariffs for the £ figure.

**Phase 2 — done when:** the forecast engine and nudge-copy logic exist as working code (not just example message text), the financial-impact model runs the three compliance-rate scenarios against real Octopus Agile historical prices (not assumed prices), and the comfort/humidity messaging is either grounded in a cited standard or dropped.

**Phase 3 — done when:** the bench rig (relay + dummy load + sensor) runs the dual control logic (off-peak windowing + comfort cutoff + manual override) end-to-end on the desk, and a real (not assumed) installation-time and BOM-cost estimate exists, ideally sense-checked with a qualified electrician rather than inferred from a DIN-rail spec sheet alone.

**Phase 4 — done when:** a bottom-up financial model exists with every revenue stream checked against its own real, current market-access rules (9.3) for a specific candidate HA estate, producing IRR/NPV/payback with P10/P50/P90 bounds — including honest reporting if the central case doesn't clear a reasonable investment bar.

**Phase 5 — done when:** Phase 4's financial case is translated into a staged implementation roadmap (pilot scale → scale-up gates → governance sign-offs → procurement route → risk register) fit to sit in front of an actual HA investment board, in the register Part 8 §20 specifies for that audience.

## 9.7 Governance Note

Same as `ofgem-curate-response`: findings and figures in this project are independent, evidence-based work, not commissioned by or presented on behalf of any HA, vendor, or DNO unless and until a specific partner engagement is agreed — that framing should be stated explicitly in any external-facing Phase 2/4/5 material.

## 9.8 Open Questions Not Yet Resolved

1. Which specific LCL (or equivalent) sub-population is actually on Economy 7 / has storage heating — not resolvable without running the disaggregation itself.
2. Whether a second, more recent dataset (post-2020) exists anywhere with comparable half-hourly granularity, to cross-check that LCL's decade-old behavioural pattern still holds under today's usage patterns and (much higher) unit prices.
3. Which real HA estate, if any, becomes the Phase 4/5 worked example — without one, Phase 4's DNO/BM access checks (9.3) can only be generic, not site-specific.
4. Whether Sonoff's DIN-rail metered relay range is a genuine second bench-test candidate alongside Shelly Pro 1PM, or was named from general familiarity rather than a checked spec — verify before Phase 3 procurement.

## 9.9 Pre-Mortem — Cheapest Checks First

1. **The NILM signature turns out not to be cleanly separable from other loads** (e.g. an immersion heater or EV charger on the same panel produces a similar overnight square wave). *Cheapest check:* visually inspect a handful of raw half-hourly traces before writing any disaggregation code — Andy's own instinct in the outline (simple thresholding on a 2–3kW overnight step) is itself the Sledgehammer Test; if it fails visually on real traces, that is Stage A's first real finding, not a coding problem to solve around.
2. **LCL's 2011–2013 data no longer reflects how storage heaters are actually used** (many original storage heaters have since been replaced with modern "high heat retention" units with electronic controls, which may not show the same overcharge failure mode). *Cheapest check:* research current storage heater stock composition (how much of the UK/HA stock is legacy dumb units vs. modern HHR units) before assuming Phase 1's finding generalises to a present-day HA estate.
3. **Phase 4's revenue stack double-counts** — e.g. assuming a battery can simultaneously chase wholesale arbitrage, BM dispatch, and DNO constraint payments at the same half-hour without checking whether those services are mutually exclusive under current market rules. *Mitigation:* explicit stacking-conflict check as part of Stage D scenario design, not assumed away.
4. **The whole case is smaller than the outline assumes** — e.g. the CapEx for a compliant BESS at this scale is higher, or NESO/DNO access for a fleet this size is thinner, than the illustrative figures suggest. *Mitigation:* per 2.8, report it plainly if so — a smaller, honestly-bounded business case is more useful to an HA board than an inflated one that doesn't survive due diligence.

## 9.10 References

London Datastore, *SmartMeter Energy Consumption Data in London Households* (Low Carbon London project) — [data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households](https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households/). UK Data Service, *Low Carbon London project: Data from the Dynamic Time-of-Use Electricity Pricing Trial, 2013* — user guide at [doc.ukdataservice.ac.uk/doc/7857](http://doc.ukdataservice.ac.uk/doc/7857/mrdoc/pdf/7857_userguide.pdf). Ofgem, *Low Carbon Networks Fund* programme page — [ofgem.gov.uk/electricity/distribution-networks/network-innovation/low-carbon-networks-fund](https://www.ofgem.gov.uk/electricity/distribution-networks/network-innovation/low-carbon-networks-fund/second-tier-projects). Open-Meteo, API documentation (historical and forecast) — [open-meteo.com](https://open-meteo.com/). Octopus Energy, *Agile Octopus* tariff and API guide — [octopus.energy/smart/agile](https://octopus.energy/smart/agile/); community API guide at [guylipman.com/octopus/api_guide.html](https://www.guylipman.com/octopus/api_guide.html). Shelly, *Shelly Pro 1PM* product specification — [shelly.com/products/shelly-pro-1pm](https://us.shelly.com/products/shelly-pro-1pm). NESO, *Trial of Small Aggregated Assets BMU in the Balancing Mechanism* — [neso.energy/document/346171/download](https://www.neso.energy/document/346171/download); NESO, *Increasing flexibility from small-scale assets (<1MW)* — [neso.energy/document/303336/download](https://www.neso.energy/document/303336/download); NESO news, *ESO to make change allowing up to 300MW of flexible assets into the Balancing Mechanism* — [neso.energy/news/eso-make-change-allowing-300mw-flexible-assets-balancing-mechanism](https://www.neso.energy/news/eso-make-change-allowing-300mw-flexible-assets-balancing-mechanism).
