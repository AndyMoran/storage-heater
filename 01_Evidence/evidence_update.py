import datetime

entry = '''
## 2026-09-07 — Insulation stress-test assumption corrected: the Jan-2026 consultation is superseded by the confirmed April-2026 policy

Andy asked to bake the 2030 insulation deadline into the next article, on the reasoning that it's "closing rapidly" and will materially affect storage-heater usage. Checked the underlying policy directly rather than reusing the 2026-09-02 stress-test's assumption, since that entry cited a January 2026 consultation *response* -- and government has since published a further, later document.

**What changed.** The January 2026 document assumed a single fabric-first route to EPC C. The government's confirmed policy (final response, April 2026, per CIH and National Housing Federation) drops fabric-first entirely: social landlords must hit EPC C by 1 April 2030 against **any one of three metrics, landlord's choice** -- Fabric Performance, Smart Readiness, or Heating System -- with a second metric required by 2039. A £10,000 spend exemption applies per metric; if the standard can't be reached within that spend, compliance defers (to 2040 for the first metric).

**This breaks the 2026-09-02 stress-test's core assumption, not just its footnote.** That entry modelled "35-50% demand reduction by 2030" as if every social home gets fabric-improved. Under the confirmed three-metric policy, a landlord can satisfy 2030 compliance with zero fabric work at all, via Smart Readiness or Heating System instead. The 35-50%/EPC-F-to-C figures are no longer a safe population-wide assumption -- they're now conditional on "for the subset of stock where a landlord actually chooses the fabric route."

**Checked whether the fabric route is even affordable for this specific segment of stock, rather than assuming landlords freely choose between the three metrics.** Storage-heater properties are disproportionately older, off-gas-grid stock, which correlates with solid-wall (not cavity-wall) construction. Real-world cost data (EPC Advisor, property118, EPCGuide, all checked directly): cavity wall insulation is cheap and highly cost-effective (GBP350-500), but solid wall insulation runs GBP5,000-15,000 (up to GBP22,000 for external solid-wall treatment) -- on its own, often exceeding the entire GBP10,000 spend cap before any other fabric measure (windows, roof, floor) is added. property118's own analysis: a Victorian solid-wall E-rated property "could easily exceed the £10,000 cost cap." This is a real, sourced reason to expect the Fabric Performance route to be financially unworkable for a material share of exactly the housing stock this project studies -- not a hypothetical.

**Net effect on the project's own numbers: the opposite direction from what "insulation is coming" might suggest.** Rather than assuming widespread fabric improvement shrinks the overcharge/gas-gap problem by 2030 (the 2026-09-02 framing), the more defensible read is: many solid-wall storage-heater properties will likely reach 2030 via the Heating System or Smart Readiness metric instead of fabric, meaning the UNinsulated £927/£691/£378 baseline (not the 35-50%-reduced scenario) remains the realistic case for a material share of this stock through 2030 and possibly to 2040 under a deferred exemption.

**Checked, not assumed: whether a nudge app or relay retrofit could itself count toward the "Smart Readiness" metric -- a materially stronger business case than tenant savings or VPP revenue alone.** Fetched the actual government consultation document (SRS_MEES_Consultation, gov.uk) rather than inferring from secondary sources. Finding: the technical definition of "Smart Readiness" is explicitly **not yet finalised** -- it awaits a separate, still-open Home Energy Model (HEM) consultation. The document's own illustrative modelling "assumed a smart metric would require installation of Photovoltaic (PV) Solar for the purposes of cost analysis" -- solar PV, batteries, and smart-tariff-enabling smart meters are the only measures named as *potentially* qualifying. **No mention anywhere of smart heating controls, storage-heater dial management, or demand-response/load-shifting heating technology as a named qualifying measure.** This means the "hardware retrofit could be a landlord's funded legal-compliance route" idea from the 2026-09-06 conversation is a genuinely open, plausible-but-unconfirmed possibility -- not a finding, and should not be stated as one until the HEM consultation defines the metric's actual technical content.

**Revised insulation-scenario numbers, kept from 2026-09-02 (unchanged maths, since insulation still scales gas/unmanaged/optimised proportionally, per that entry's own reasoning) but now explicitly labelled conditional on the fabric route being chosen and affordable:**
- Gas-to-optimised-storage gap (currently GBP313/year): -> GBP203/year at 35% fabric-driven demand reduction -> GBP156/year at 50%.
- Unmanaged-to-optimised gap, i.e. NightDial/relay's addressable ceiling (currently GBP236/year): -> GBP153/year at 35% -> GBP118/year at 50%.
- These now come with an explicit caveat the 2026-09-02 entry did not carry: they apply only where a landlord actually chooses and can afford the Fabric Performance route, which real-world cost data suggests will be a minority of solid-wall, off-gas-grid, storage-heater properties specifically.

**Sources checked directly this session:** CIH ("CIH welcomes confirmation of Minimum Energy Efficiency Standards in the social rented sector"), National Housing Federation MEES policy page, Elmhurst Energy's summary of the confirmed three-metric/2030/2039 structure, the government's own SRS MEES consultation PDF (gov.uk) for the Smart Readiness definition status, and three independent real-world EPC-upgrade-cost sources (EPC Advisor, property118, EPCGuide) for the solid-wall cost-cap check.

**Output:** this entry. No code/data files changed -- this corrects a policy assumption feeding the article draft, not a model output.
'''

with open("evidence_map.md", "a") as f:
    f.write(entry)

print("Appended", len(entry), "chars")
