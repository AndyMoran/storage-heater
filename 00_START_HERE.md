# AutoMagic — Project Collection

Everything from the storage-heater-vpp-ha project in one place. Four folders, in the order you'd probably want to look at them.

---

## 01_Evidence

- **`evidence_map.md`** — the master log. Every finding, every dead end, every checked assumption, every bug caught before it shipped, in chronological order. If you ever need to answer "where did this number actually come from," this is where.
- **`Phase1_Data_Report.docx`** — the formal write-up: the core overcharge finding (12.2% waste, £117/household/year), the honest negative result on afternoon exhaustion, the £ reprojection onto current tariffs, insulation/gas/heat-pump comparisons, and the under-heating/Awaab's Law risk case. Opens in Word or OnlyOffice.

## 02_LinkedIn_Posts_and_Articles

Three post-and-article pairs, in the order they were written — each one builds on the last, so reading in order tells the real story of how the findings developed.

- **Post 1 — Overcharge Findings.** The headline result: real UK smart-meter data shows storage heaters overcharging, quantified, and the counter-intuitive twist that a "dumb" heater on a smart tariff costs *more*, not less.
- **Post 2 — Policy Stress Test.** Checking whether the project's own premise survives contact with 2030 insulation policy, solar/battery economics, and heat pumps. Includes two comparison charts. Honest finding: insulation roughly halves the savings opportunity, but doesn't eliminate it.
- **Post 3 — Warm Homes Plan.** Does the government's newly-announced £442/year saving make this project redundant? No — it's a price cut, not a usage fix, and the two are additive. Also covers real market sizing: ~136,500 housing association homes still on old-style manual storage heaters.
- **Post 4 — Rational Point Heating.** The sharpest finding yet: a plug-in radiator and electric blanket is genuinely the *cheapest* heating option on the whole comparison table — cheaper than gas, cheaper than the optimised smart system. Explains why "just turn the heating down" is a rational tenant decision, not carelessness, and why that same rational decision is exactly what creates a landlord's liability under Awaab's Law.

Each folder has the LinkedIn post (short) and the longer article (with chart placement notes where relevant) side by side.

## 03_Prototype

- **`automagic_demo.html`** — open this directly in any browser, including on an Android phone. A working demo of the tenant-facing app concept: two dials (Input, matching the real 1–6 numbering found on actual storage heaters; Output, shown as general guidance since it isn't forecast-driven), real nudge messages, and all 365 days of 2013 replayed through the actual analysis pipeline — not placeholder content. Use the arrows or the slider to step through the year.

## 04_Full_Project_Source

- **`storage-heater-vpp-ha.zip`** — the complete technical project: all source code (`src/`), configuration (`config/`), the original spec documents (`README.md`, `PROJECT.md`, `METHODOLOGY.md`), and this same evidence log and comms folder in their original working locations. This is what you'd hand to a developer, or unzip yourself to keep working with the actual code (self-tests included — most modules run standalone and print their own pass/fail results).

---

*Everything here traces back to real, checked sources — real smart-meter data, real current tariffs, real government policy documents, real product specifications. Where something is an assumption rather than a checked fact, it's flagged as one in `evidence_map.md`.*
