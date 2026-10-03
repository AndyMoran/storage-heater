# storage-heater-vpp-ha

**Core Thesis:** Unmanaged electric storage heating wastes tenant money twice over — overcharging on mild nights and running out of stored heat by mid-afternoon — and closing that gap with a cheap relay retrofit turns a Housing Association's heating stock into a fleet of controllable load that, paired with a battery asset, can earn real wholesale, balancing, and network-flexibility revenue.

This is a five-phase, evidence-first project: prove the problem with open UK smart-meter data, test the cheapest fix (a behavioural nudge) before the more expensive one (hardware), bench-test the hardware fix before proposing any live install, build the financial case for scaling it into a VPP asset, and only then turn that case into an implementation roadmap a real HA investment board could act on. See `PROJECT.md` for the full constitution and phase-by-phase specification, `METHODOLOGY.md` for the technical method behind each phase, and (once Phase 1 starts) `evidence_map.md` for claim-by-claim traceability, following the same discipline used in `ofgem-curate-response`.

## Status

Scoping complete. Phase 1 (data proof) not yet started — no data has been pulled, no code has been written. This README, `PROJECT.md`, and `METHODOLOGY.md` are the pre-registration of method and assumptions, written before the analysis, so the analysis can be checked against a plan made in advance rather than a story fitted afterward.

## The Five Phases

| Phase | Objective | Deliverable |
|---|---|---|
| 1. Prove the Gap | Quantify the real £-and-comfort cost of unmanaged storage heating from open smart-meter data | A data report: overcharge and afternoon-exhaustion patterns, quantified, reprojected onto current tariffs |
| 2. Behavioural Nudge | Test whether SMS/app guidance alone captures some of that saving, before any hardware | A working forecast-and-nudge engine plus a compliance-scenario savings model against real dynamic-tariff prices |
| 3. Hardware Bench-Test | Design and bench-test a sub-£100/property relay retrofit that automates the fix | A working desk-bench prototype, tested control logic, and a real (electrician-checked) BOM and install-time estimate |
| 4. VPP Financial Model | Build the bottom-up financial case for scaling the retrofit into a revenue-generating VPP asset | A 10-year financial model (IRR/NPV/payback, P10/P50/P90) with every revenue stream checked against its own current market-access rules |
| 5. HA Implementation Roadmap | Convert the financial case into a staged, governed path to an actual HA investment decision | A pilot-to-scale roadmap: gate criteria, procurement route, risk register, board-ready material |

Phase 5 was split out from the original four-phase outline specifically so Phase 4 stays focused on proving the financial case, and the separate, harder question of *how an HA actually implements it* gets its own deliverable rather than being folded in as an afterthought.

## Assumptions Not Yet Tested

Every headline figure in the original project outline — the 25–40% overcharge cost, the £80–£140/year nudge saving, the £50–£100 hardware BOM, the £1.2–1.5M BESS CapEx, the £125k–£175k/year revenue — is an illustrative placeholder, not yet a modelled result. `PROJECT.md` §9.5 lists each one explicitly, with the step in `METHODOLOGY.md` that will either confirm, replace, or drop it. Reporting a smaller or absent effect is a valid outcome of this project, not a failure of it (`PROJECT.md` §2.8).

## No-Double-Counting Note

Phase 4's revenue stack (wholesale arbitrage, NESO Balancing Mechanism dispatch, DNO local flexibility payments) is not assumed additive. The financial model must encode which service the asset is actually serving in any given half-hour and apply an explicit priority rule where two services would otherwise conflict — see `METHODOLOGY.md` §4.2.

## Limitations & Future Work

- The Low Carbon London dataset (the leading candidate for Phase 1) is not pre-tagged for Economy 7 tariffs or storage heating — identifying that sub-population is itself the first analytical task, not a filtering step that precedes it. See `PROJECT.md` §9.3.
- The dataset's own pricing is a decade out of date; behavioural/timing patterns from it should still hold, but every £ figure must be reprojected onto current tariffs before it's reported.
- No specific Housing Association estate has yet been identified as the Phase 4/5 worked example. Without one, DNO- and NESO-access assumptions can only be generic — see `PROJECT.md` §9.8.
- The psychrometric comfort claim in the original Phase 2 nudge copy ("lower humidity makes 18°C feel like 21°C") needs a cited basis before it reaches any tenant, or it needs softening to a qualitative claim. Flagged, not yet resolved.
- BS 7671 compliance detail and the ~20-minute install-time claim for Phase 3's hardware are illustrative until reviewed by a qualified electrician.

## Figures

None yet — Phase 1 has not produced any data to plot. The first figure this project should produce, once Phase 1 runs, is the raw half-hourly trace of a handful of confirmed storage-heater households against the modelled "required charge" line, since that single chart is the whole Phase 1 thesis made visible (Tufte standard, `PROJECT.md` §9).
