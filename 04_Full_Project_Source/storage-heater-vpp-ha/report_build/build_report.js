const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, ImageRun, AlignmentType, BorderStyle, PageBreak, Header, Footer,
  PageNumber, NumberFormat
} = require("docx");
const fs = require("fs");

const PAGE_W = 12240, PAGE_H = 15840; // US letter not needed; A4 default is fine, leave default

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 160 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 120 } });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 160 } });
}
function pBold(text) {
  return new Paragraph({ children: [new TextRun({ text, bold: true })], spacing: { after: 160 } });
}
function bullet(text) {
  return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 80 } });
}
function caption(text) {
  return new Paragraph({
    children: [new TextRun({ text, italics: true, size: 18, color: "555555" })],
    spacing: { after: 320 }, alignment: AlignmentType.CENTER,
  });
}

function imageParagraph(path, widthPx, aspectRatio) {
  const width = widthPx;
  const height = Math.round(widthPx / aspectRatio);
  return new Paragraph({
    children: [new ImageRun({ data: fs.readFileSync(path), transformation: { width, height }, type: "png" })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 80 },
  });
}

function statTable(rows) {
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: [4500, 4500],
    rows: rows.map(([label, value], i) => new TableRow({
      children: [
        new TableCell({
          width: { size: 4500, type: WidthType.DXA },
          shading: i === 0 ? { type: ShadingType.CLEAR, fill: "2B5D8C" } : undefined,
          children: [new Paragraph({ children: [new TextRun({ text: label, bold: i === 0, color: i === 0 ? "FFFFFF" : "000000" })] })],
        }),
        new TableCell({
          width: { size: 4500, type: WidthType.DXA },
          shading: i === 0 ? { type: ShadingType.CLEAR, fill: "2B5D8C" } : undefined,
          children: [new Paragraph({ children: [new TextRun({ text: value, bold: i === 0, color: i === 0 ? "FFFFFF" : "000000" })] })],
        }),
      ],
    })),
  });
}

function statTable3(rows) {
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: [3600, 2700, 2700],
    rows: rows.map((cells, i) => new TableRow({
      children: cells.map((text, ci) => new TableCell({
        width: { size: ci === 0 ? 3600 : 2700, type: WidthType.DXA },
        shading: i === 0 ? { type: ShadingType.CLEAR, fill: "2B5D8C" } : undefined,
        children: [new Paragraph({ children: [new TextRun({ text, bold: i === 0, color: i === 0 ? "FFFFFF" : "000000" })] })],
      })),
    })),
  });
}

const doc = new Document({
  sections: [{
    properties: {},
    headers: {
      default: new Header({ children: [new Paragraph({
        children: [new TextRun({ text: "storage-heater-vpp-ha — Phase 1 Data Report", size: 16, color: "888888" })],
        alignment: AlignmentType.RIGHT,
      })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        children: [new TextRun({ text: "Page ", size: 16, color: "888888" }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "888888" })],
        alignment: AlignmentType.CENTER,
      })] }),
    },
    children: [
      // TITLE
      new Paragraph({
        children: [new TextRun({ text: "Proving the Gap", bold: true, size: 56, color: "2B5D8C" })],
        spacing: { after: 80 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Phase 1 Data Report — Storage-Heater Overcharge in Open UK Smart-Meter Data", size: 28, color: "444444" })],
        spacing: { after: 60 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "storage-heater-vpp-ha  ·  1 September 2026", size: 22, color: "888888", italics: true })],
        spacing: { after: 500 },
      }),

      h2("Executive Summary"),
      p("Using a full year (2013) of half-hourly smart-meter data from 4,443 London households, this analysis identifies genuine electric storage-heater households by their load signature and quantifies how much of their overnight charging is unjustified by that day's weather. The core finding:"),
      statTable([
        ["Headline finding", ""],
        ["Confirmed storage-heater households", "43 of 4,443 sampled (≈1.0%)"],
        ["Excess (\"overcharged\") energy, whole year", "25,638 kWh — 12.2% of all night-time charging"],
        ["Cost of that waste, current (2026) prices", "£117 per household per year (Economy 7)"],
        ["Cost if simply switched to Octopus Agile", "£126 per household per year — worse, not better"],
      ]),
      new Paragraph({ text: "", spacing: { after: 200 } }),
      p("The Agile result is not a disappointing finding — it is a precise one. It demonstrates that the value in this problem is not in the tariff, but in timing: a household that charges the same way regardless of price captures none of Agile's cheap overnight troughs and is fully exposed to its peaks. That is exactly the opportunity Phase 2 (the behavioural nudge engine) is designed to capture, not something Phase 1 should claim credit for."),
      p("Even fully optimized, electric storage heating remains £313/year more expensive than gas for equivalent heating demand (Section 5) — a persistent, structural gap that creates a direct, quantifiable incentive for under-heating, with corresponding damp and mould risk under Awaab's Law (Section 6). No evidence of active heater abandonment was found in this 2013 dataset, but that dataset predates the price pressure that would be expected to trigger it — a caveat this report states explicitly rather than leaving implicit."),

      h2("The Whole Thesis, in One Figure"),
      imageParagraph("fig1_combined.png", 620, 1.333),
      caption("Top: a confirmed \"seasonal\" household (MAC004954), December 2013. Dashed line is this household's own fitted temperature response, scaled to the same shape as the actual trace so heights are directly comparable — labels show actual vs. modelled-required kWh per night. Most nights track closely; a minority diverge, consistent with the 25.9% of seasonal-household nights flagged as overcharged.\nBottom: a confirmed \"year-round\" household (MAC004863), July 2013 — charging 27–40kWh most nights despite outdoor temperatures of 14–22°C, well above the 15.5°C threshold where any heating need exists at all."),

      new Paragraph({ children: [new PageBreak()] }),

      h1("1. Data & Population"),
      h2("1.1 Source"),
      p("Low Carbon London (LCL) smart-meter trial data, refactored release (Tindemans, 2023, 4TU.ResearchData, DOI 10.4121/fbbe775b-48d8-469f-a39b-b64488bfd6fd). 4,443 London households on standard (non-dynamic-pricing) tariffs, half-hourly readings, full calendar year 2013. Integrity verified byte-for-byte against the published MD5 checksum before use."),

      h2("1.2 Identifying storage-heater households"),
      p("A cheap first-pass filter (overnight demand exceeding daytime demand) identified 42 candidate households. Direct visual inspection of a 15-household sample showed this filter alone was not clean — roughly 40% of flagged households did not show a genuine storage-heater signature."),
      p("The working detector — the share of each household's January energy used overnight (\"S_night\") — was calibrated against the full population of 4,443 households, not tuned to match the small visual sample. The distribution below shows why: the overwhelming majority of households cluster around S_night ≈ 0.20 (ordinary background load), with a small, distinctly separated population above 0.65."),
      imageParagraph("s_night_full_population_histogram.png", 620, 2.8),
      caption("S_night distribution across all 4,380 households with sufficient January data. Left: linear scale. Right: log scale, revealing the sparse tail past the natural gap at S_night ≈ 0.65–0.70 — the basis for the confirmation threshold, chosen from where the population itself goes quiet, not fitted to match prior expectations."),
      p("This threshold, applied independently, recovered the same 6 households flagged as visually ambiguous in the earlier sample and retained all 9 flagged as visually clean — agreement that was not engineered, since the threshold came from the population distribution alone."),

      h2("1.3 Final population"),
      statTable([
        ["Category", "Households"],
        ["Confirmed — seasonal (temperature-responsive)", "37"],
        ["Confirmed — year-round (no temperature response)", "4"],
        ["Flagged for data-quality review (not classified)", "2"],
        ["Total confirmed", "43"],
      ]),

      new Paragraph({ children: [new PageBreak()] }),

      h1("2. Quantifying the Overcharge"),
      h2("2.1 Method"),
      p("For each seasonal household, a household-specific model was fitted: night charge (kWh) as a linear function of that day's heat-loss proxy (max(0, 15.5°C − mean daily temperature)). A single population-wide relationship was tested and rejected — households showed materially different slopes, consistent with different numbers of heaters per property (a typical two-bedroom UK property running around five heaters, per domain guidance, plausibly explaining aggregate overnight draws up to 10–13kW seen in the data). A night is flagged \"overcharged\" where actual charge exceeds that household's own fitted line by more than 25%."),
      p("For year-round households — which show no measurable temperature response — a simpler, stricter test applies: any night above 15.5°C has no legitimate heating justification at all, so charge above a small baseline on those nights is overcharge by construction."),

      h2("2.2 Validation"),
      p("Before treating flagged nights as a finding, they were plotted directly against the fitted line and against temperature to confirm the flags land where physically expected — not just computed and trusted."),
      imageParagraph("overcharge_test_validation.png", 620, 2.364),
      caption("Left: seasonal household (MAC004954, R²=0.84) — flagged nights (red) cluster above the fitted response, concentrated at the mild end. Right: year-round household (MAC004863) — flagged nights cluster past the 15.5°C threshold. Fit quality across all 37 seasonal households: median R²=0.70 (range 0.14–0.86); the lowest-R² households' individual flags are less trustworthy and are named explicitly in the underlying evidence log."),

      h2("2.3 Result"),
      statTable([
        ["Metric", "Value"],
        ["Total night-time charge, all confirmed households, 2013", "209,950 kWh"],
        ["Total excess (\"overcharged\") energy", "25,638 kWh (12.2% of all night charging)"],
        ["Seasonal households: nights flagged overcharged", "3,492 / 13,467 (25.9%)"],
        ["Year-round households: mild nights flagged overcharged", "306 / 312 (98%, n=4 households — small sample)"],
      ]),

      h1("3. Afternoon Exhaustion — A Negative Result"),
      p("METHODOLOGY.md specified a second test: whether stored heat runs out on cold days, evidenced by a distinct \"boost\" heating signature in the 16:00–20:00 window that tracks cold snaps. This was built and tested properly, including a full recalibration of the assumed heat-release rate once the first estimate (2.0kW) produced physically implausible results (median exhaustion by noon)."),
      p("Even after recalibration to a design-intent-derived rate (1.0kW, from cold-night charge levels), the cross-tabulation ran backwards: nights where the model predicted exhaustion by 20:00 showed a lower boost rate (50.0%) than nights it predicted were not exhausted (64.1%). The most likely explanation is confounding, not a coding error: 16:00–20:00 is when ordinary household activity — cooking, lighting, occupancy — rises for every household on a cold day, regardless of heating system, and a whole-house aggregate meter cannot separate that from genuine heater-exhaustion behaviour."),
      p("This is reported as a genuine limitation of this data and method, not glossed over — per the methodology's own instruction that a mechanism which \"shows up randomly... shouldn't claim one.\""),

      h1("4. Reprojecting Onto Current Prices"),
      p("The LCL data is priced at 2011–2013 trial rates; the finding above is reprojected onto current tariffs, sourced and cited rather than assumed."),
      h2("4.1 Static tariff: Economy 7"),
      p("Ecotricity's published domestic tariff sheet, effective 1 April 2026, London region, Direct Debit: day rate 28.09p/kWh, night rate 18.73p/kWh."),
      h2("4.2 Dynamic tariff: Octopus Agile"),
      p("Real half-hourly prices for London (tariff E-1R-AGILE-24-10-01-C), sampled across a representative winter week (12–19 Jan 2026) and summer week (24–31 Aug 2026) via the public Octopus API. Overnight (23:00–07:00) mean: 17.76p/kWh in winter, 24.0p/kWh in summer — winter Agile is genuinely cheaper than flat Economy 7's night rate; summer Agile is pricier."),

      h2("4.3 Result"),
      statTable3([
        ["", "Static Economy 7", "Octopus Agile (unmanaged)"],
        ["All night-time charging (41 households/yr)", "£39,324  (£959/hh)", "£41,085  (£1,002/hh)"],
        ["Excess/waste specifically (41 households/yr)", "£4,802  (£117/hh)", "£5,150  (£126/hh)"],
      ]),
      new Paragraph({ text: "", spacing: { after: 120 } }),
      p("Note: the table above compares tariffs while holding the charging pattern fixed at what actually happened in 2013 — i.e. a household that does not respond to price signals. Agile costs more here because an unmanaged, all-hours overnight block captures none of Agile's cheap troughs while remaining fully exposed to its peaks. This is the gap Phase 2 exists to close, not a Phase 1 finding about which tariff is better in general."),

      h2("4.4 What's Current Here, and What Isn't"),
      p("Worth stating explicitly rather than leaving for the reader to infer: the PRICES in this section are current — sourced from live 2026 tariff sheets and real 2026 half-hourly market data. The ENERGY QUANTITIES those prices are applied to are not current — they come from measured 2013 household behaviour, in 2013 weather. A kilowatt-hour doesn't inflate, so no adjustment is missing from the arithmetic itself; but \"2013 usage, 2026 prices\" is a specific, stated combination, not the same claim as \"2026 usage, 2026 prices,\" and the two should not be conflated when this figure is quoted elsewhere."),
      p("That distinction matters here for two separate reasons, both pointing the same direction. First, behaviourally: today's substantially higher energy prices may already be pushing some households toward the under-heating and self-rationing discussed in Section 6 — a real effect this project has no way to measure from 2013 data, since the acute price pressure driving it did not yet exist. If so, the true 2026 waste could run lower than 2013's figure, precisely because tenants are already coping (at a real cost to their comfort and health) rather than because the underlying equipment problem has improved. Second, meteorologically: Section 2.4's multi-year weather check (Phase 2 of this project) found that 2013 was colder than every one of the six most recent comparison years — 2020–2025 produced excess-kWh figures of 16,958–20,222 under the same fitted household models, while 2013's actual figure was 22,249, above the top of that range. This is independent of any behavioural question; it means 2013 was simply a harsher winter than a typical recent one."),
      pBold("Both effects point toward the same conclusion: the £117/household figure is a real, measured 2013 result, not a stale one — but it is more defensible read as an upper bound on a typical current year than as a typical-year estimate itself, for two independent reasons rather than one."),

      h1("5. Storage Heating vs. Gas: The Structural Cost Gap"),
      p("A tenant's real alternative to electric storage heating is usually gas central heating, not a different electricity tariff. This section compares them directly, for a typical two-bedroom social-housing flat, at current (2026) prices — checking the assumptions behind the comparison rather than taking them as given."),
      h2("5.1 Assumptions"),
      bullet("Annual space-heating demand: 4,500 kWh/year — an illustrative figure for a small, moderately insulated flat, not independently verified against this project's own data (which measures electricity, not heat delivered) and should be treated as a working assumption, not a sourced fact."),
      bullet("Gas: 7.15p/kWh — Ecotricity's published London Standard Direct Debit rate (the same tariff sheet used for the Economy 7 figures elsewhere in this report, kept consistent rather than mixing suppliers or tariff tiers)."),
      bullet("Boiler seasonal efficiency: 85% (a standard assumption for a modern condensing boiler) — delivered gas cost 8.41p/kWh."),
      bullet("Economy 7: day 28.09p/kWh, night 18.73p/kWh (Ecotricity, as sourced in Section 4)."),
      bullet("Night/day split for storage heating: 80/20 — drawn from this project's own S_night findings for genuine storage-heater households (typically 0.70–0.90), not an external assumption."),
      bullet("\"Optimized\" dynamic-tariff rate: 17.49p/kWh — computed directly from the real winter Octopus Agile data already sourced in Section 4 (the cheapest 16 half-hours per day, representing what a smart controller could actually achieve), not assumed."),

      h2("5.2 Result"),
      statTable3([
        ["Scenario", "Annual cost", "vs. gas"],
        ["Gas (delivered heat, 85% boiler efficiency)", "£379", "—"],
        ["Economy 7, as actually used today (incl. the 12.2% overcharge)", "£927", "+£549"],
        ["Economy 7, if the overcharge alone were eliminated", "£814", "+£435"],
        ["Fully optimized (Agile timing + overcharge eliminated)", "£691", "+£313"],
      ]),
      new Paragraph({ text: "", spacing: { after: 120 } }),
      p("The £236/year gap between the unmanaged and fully-optimized rows is Phase 2's real, defensible opportunity — genuine and substantial. But it does not close the gap to gas. Even in the best case this project can model — every overcharged kWh eliminated, every charge perfectly timed to the cheapest available price — electric storage heating remains £313/year more expensive than gas for the same heating demand. That gap is structural: it exists regardless of tenant behaviour, and no amount of load-shifting removes it on its own."),

      h1("6. Under-Heating and Fuel Surrender Risk"),
      p("A persistent cost disadvantage of this size creates a direct, foreseeable incentive for tenants to under-heat: switching storage heaters off entirely, or substituting cheap point-heating (a plug-in fan or oil-filled radiator run next to where someone sits) for whole-room heating. Under-heating a property raises relative humidity and condensation risk, which is the documented pathway to damp and mould — the specific hazard Awaab's Law (Social Housing (Regulation) Act 2023) requires social landlords to investigate and remediate within fixed statutory timeframes. This section tests whether that behaviour is visible in the data, and is explicit throughout about what was and wasn't found."),

      h2("6.1 A direct test — and a genuine negative result"),
      p("A specific, falsifiable signature was tested: a household showing strong storage-heater engagement (S_night) in November, collapsing to background level (S_night < 0.20) by January or February despite colder weather — consistent with a tenant receiving a high bill and switching the heaters off at the wall. Monthly S_night was computed for all 41 confirmed households across November 2013 – February 2014. Not one showed this pattern. S_night stayed remarkably stable across the whole heating season for nearly every household — most varied by less than 0.05 between the mildest and coldest months."),
      p("A second, related signature — a resistive point-heater substitution pulse in the 17:00–21:00 window, appearing where overnight charging has dropped — was not tested. It is conditioned on an abandoned-household subset that Signature A's null result means does not exist here, and running it against the general population would reproduce a confound already identified in Section 3 (ordinary evening activity rising for every household on a cold day, regardless of heating system)."),

      h2("6.2 The caveat this session cannot analyse around"),
      pBold("This dataset is from 2013 — a materially different price environment from today, and the null result above should not be read as evidence that fuel surrender does not happen."),
      p("2013 Economy 7 rates were substantially lower in real terms than current prices, and the acute cost-of-living and energy-price pressure that has driven widespread, documented fuel poverty since the 2021–2023 energy crisis was not present at the same intensity when this data was recorded. A behaviour driven primarily by bill shock may simply not have been triggered as often, or as severely, in this dataset's period as it is today. The absence of the pattern in 2013 is informative about 2013; it is not informative about today's risk, and should not be cited as reassurance either way."),

      h2("6.3 The stronger evidence: a structural incentive, independent of any one household's behaviour"),
      p("What Section 5 establishes does not depend on catching any specific household in the act of surrendering. It shows that a persistent, quantified, current-priced cost disadvantage exists for electric storage heating relative to gas — £313/year even under this project's best-case optimized scenario — for every household on this tariff type, regardless of whether that specific household's own meter shows a visible drop-off. That is a more defensible basis for a housing-association risk assessment than a behavioural detector result from a single, lower-price historical year: it demonstrates the incentive is real and structural, not that any particular tenant has yet acted on it."),
      p("The practical implication for Awaab's Law compliance: a property on unmanaged Economy 7 storage heating carries an elevated, quantifiable risk of under-heating-driven damp and mould relative to an equivalent gas-heated property, independent of any specific tenant's currently observed behaviour. This is a property-level risk factor worth flagging proactively, not something that requires waiting for a complaint or a visible meter anomaly to justify attention."),

      new Paragraph({ children: [new PageBreak()] }),

      h1("7. Limitations"),
      bullet("The overcharge test flags deviation from each household's own fitted pattern, not a claim about the true physical heat requirement of any specific property."),
      bullet("The year-round group is 4 households — real, and validated, but too small to generalise a population-wide rate from."),
      bullet("No labelled ground-truth dataset for genuine storage heaters was found this session (UK-DALE contains none; the Household Electricity Survey's raw appliance data sits behind UK Data Service registration, not pursued here) — the detection method is validated against the population's own distribution and direct visual inspection, not an independent labelled set."),
      bullet("The afternoon-exhaustion mechanism (Section 3) is an open, unresolved question, not a confirmed finding either way."),
      bullet("The Agile comparison uses two representative weeks, not a full year of historical prices, due to a tool-side limitation encountered when attempting to fetch a longer series."),
      bullet("The gas-vs-electric cost comparison (Section 5) rests on an illustrative, unsourced heating-demand figure (4,500 kWh/year) — the £-gap direction and rough magnitude are meaningful, the exact figure is not a precise claim."),
      bullet("The under-heating null result (Section 6.1) is specific to 2013 and its lower-price environment — it does not generalise to whether fuel surrender happens today, and should not be cited as if it does."),
      bullet("All £ figures in this report use 2013 measured energy quantities priced at current (2026) rates — see Section 4.4 for why that is more defensible read as an upper-bound estimate than a typical-current-year one."),

      h1("Next"),
      p("This completes Phase 1 (METHODOLOGY.md §1.1–1.4). The output register (data/intermediate/phase1_household_nights.parquet) is the input Phase 2's nudge-engine and compliance simulation reads from, per the project's sequencing rule that each phase's output contract is the next phase's required input."),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Phase1_Data_Report.docx", buf);
  console.log("written");
});
