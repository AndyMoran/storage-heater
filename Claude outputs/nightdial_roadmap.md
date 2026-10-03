---
title: NightDial → Hardware → VPP: a staged roadmap
description: How the storage-heater project moves from a free nudge app to a fleet-scale flexibility asset, and what each stage needs to prove before the next one is worth funding.
---

# NightDial → Hardware → VPP: a staged roadmap

## The shape of the argument

Every stage exists to answer one question the previous stage couldn't: does this actually work, for this population, at this cost, and is anyone going to pay for the next step. Nothing here is scoped as a leap of faith — each stage produces the specific evidence the next stage needs to be a rational investment rather than an assumption.

## Stage 1 — NightDial, live (done)

**What it is.** A free, single-file web app. Fetches a live forecast for a tenant's postcode, gives one nightly nudge — what to set the dial to — calibrated against real 2013 smart-meter data from 42 confirmed storage-heater households (13,102 household-nights). No install, no account, no hardware, no cost to the tenant or the landlord.

**What it's already shown.** The real, measured overcharge this population is capable of eliminating: average £110–117/household/year at full compliance, with real households ranging from £40 to £495/year depending on how badly they were overcharging to start with. This is the ceiling software nudging can reach for — not a guess, the actual distribution in the data.

**What it hasn't shown yet.** Real tenant compliance. The 10/30/50% figures used everywhere in this project's financial modelling are explicitly illustrative bounds, not measured — nobody has actually watched a real tenant use NightDial for a winter yet.

## Stage 2 — NightDial trial (next, and the most important unlock in the whole roadmap)

**What changes.** The same free app, plus a lightweight, opt-in way to find out whether the nudge was actually followed — nothing invasive: a one-tap "did you turn it down last night?" check-in, or (better, if a participating household has a smart meter) a real overnight-kWh comparison against what the app recommended. Needs a small group of real households, ideally through a willing housing association, over at least one real winter.

**What it produces.** The one number every later stage depends on and doesn't currently have: a *measured* compliance rate, replacing the illustrative 10/30/50% bounds with something real. That single number determines whether software alone gets most of the way to the £110–117 average, or whether it's closer to the illustrative 10% floor (£9–10/household/year) — and therefore whether Stage 3's investment case is strong or essential.

**Why this has to come before hardware, not alongside it.** PROJECT.md's own Phase 4 rule is explicit: revenue and savings figures aren't real until checked against actual data, not modelled assumptions. A trial costs nothing but a bit of coordination with an HA; a relay retrofit costs real capital. Measuring compliance first is the cheap way to find out whether the expensive step is justified — not a delay, the de-risking step itself.

## Stage 3 — Hardware retrofit (relay), informed by Stage 2's real number

**What it is.** Already spec'd and partly bench-tested in software: `control_logic.py` and `config/phase3_control_config.py` implement the same real, quantile-calibrated Target Charge Index (Index 1 charges 8.8% of the off-peak window, Index 5 charges 86.3% — genuine empirical figures, not round ones) as a relay-driven control loop, with fail-safe behaviour (forecast dropout → standard charging, never under-provision) already unit-tested (7/7 bench scenarios). The recommended device, checked against real current specs rather than assumed, is the Shelly Pro 1PM — 16A DIN-rail relay, built-in power metering, local JSON-RPC API (`/rpc/Switch.Set`, `/rpc/Switch.GetStatus`), no cloud dependency required.

**What's still owed before a real install, honestly listed, not glossed over:** the physical bench run (LED dummy load first, per the project's own safety-first design), electrician sign-off against BS 7671 (this project cannot self-certify that), a real installation-time and BOM-cost estimate sense-checked by a qualified electrician rather than inferred from a spec sheet, and — from Stage 2 — the actual compliance number that tells you how much value the relay adds over the free software alone.

**The case for it, sharpened by this month's policy findings.** A relay guarantees the saving regardless of tenant behaviour — worth more the lower Stage 2's measured compliance turns out to be, and worth more the longer heat pumps stay capex-blocked for this stock (Boiler Upgrade Scheme still excludes social housing after its April 2026 refresh; storage-heater flats have no existing wet system to convert onto). And as of the January 2026 Home Energy Model consultation, storage heaters and "smart heating controls and demand management systems" are explicitly named as qualifying technology under the incoming EPC Smart Readiness metric — meaning this relay isn't just a savings device, it's a plausible, evidence-backed route for a housing association to meet its 2030 MEES deadline under the metric it's most likely to actually afford (£10,000 spend cap per metric; solid-wall/EWI fabric work often exceeds that for exactly the flats this population lives in, per the wall-type discussion already logged — genuinely uncertain, not a settled cost case either way).

## Stage 4 — VPP via API: aggregating the fleet

**The mechanism.** Each relay is already, by construction, a controllable, metered, remotely-addressable load (that's what the local JSON-RPC API gives you for free — Stage 3 doesn't need new hardware for this, just a fleet-management layer talking to devices already capable of it). A thin dispatch service sits above the fleet: it ingests each relay's real-time state and consumption (`Switch.GetStatus`) and issues `Switch.Set` commands to entire groups of devices, on top of — never instead of — the tenant-comfort baseline the Target Charge Index already guarantees. The control logic that decides "how much can this specific relay's charge window flex right now without under-heating that tenant" is the same comfort-cutoff logic already built and tested in Stage 3; the VPP layer's job is just deciding *when* to ask a relay to flex, based on an external signal.

**Where the external signals come from, checked against real access rules rather than assumed generically available (PROJECT.md §9.3 — checked, not a lead list any more once a real candidate estate exists):**
- NESO's Balancing Mechanism now has an active work item for aggregated small-scale assets — a specific "Trial of Small Aggregated Assets BMU" reportedly opening up to 300MW of flexible capacity. Real and in motion, not proposed.
- DNO/local flexibility markets (Piclo- and Electron-run tenders) for constraint management — real and active, but access, clearing prices, and whether a given fleet would actually be dispatched depend on the specific DNO licence area and substation of whatever estate is used, not assumable nationally.

**What this stage still owes, stated plainly per this project's own discipline rather than presented as solved:** a bottom-up financial model with every revenue stream checked against its own current market-access rules for a specific candidate HA estate, producing a real IRR/NPV/payback range (P10/P50/P90) — including honest reporting if the central case doesn't clear an investment bar. That's Phase 4's job, and it hasn't been done yet; Stage 4 here describes the mechanism, not a proven revenue number.

## The dependency chain, in one line each

Stage 1 exists now, at zero cost, and is useful to the wider storage-heater community regardless of what happens next. Stage 2 turns an assumption (compliance rate) into a measured fact, cheaply. Stage 3 is justified in proportion to how low that measured number turns out to be, and is strengthened independently by the emerging MEES/Smart Readiness case. Stage 4 turns Stage 3's already-metered, already-networked hardware into a fleet asset, but only once a real financial model — not this roadmap — says the numbers clear the bar.
