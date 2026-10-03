Heat pumps beat gas on carbon by four to one. Storage heaters beat it too — by less, and getting that second number right took catching two mistakes of my own along the way. Here's the full case, including the parts where I was wrong first.

*A note before you read on: the headline numbers here already went out in an earlier post. This piece is for anyone who wants to see the actual working behind them — including the two real mistakes I made and caught along the way — not just the conclusion.*

**The headline**

Across the 40 real households I've been using throughout this project, average heat demand comes to about 4,720 kWh a year. Three ways to deliver it, checked against real 2025 grid carbon data rather than a spec sheet or a single average:

Gas costs 958 kg of CO2 a year, using the real efficiency-adjusted carbon intensity of gas heat (203 gCO2 per kWh delivered, a 90%-efficient boiler).

Storage heating, as people actually run it, costs 678 kg — a real 29% saving against gas. Run it perfectly, charged to exact need with none of the overcharge this project's software has spent months eliminating, and it drops to 621 kg.

A heat pump at real field performance — not a manufacturer's number, but the median from DESNZ's 428-household Electrification of Heat trial (SCOP 2.78) — costs 223 kg. Under a quarter of gas, and two-thirds of even storage heating's best case.

[CHART 1: chart1_carbon_comparison.png — the three-way carbon comparison with error bars]

That gap is decisive enough that I don't think there's a serious carbon argument for storage heating over a heat pump in this housing stock. But I want to spend the rest of this piece on how I got the storage-heating number, because the process mattered more than I expected, and because I think the mistakes are more useful to show than to quietly fix and move on from.

**How you actually check a claim like this**

The lazy version of this comparison uses one number for grid carbon intensity — the UK's annual average, currently around 124 gCO2/kWh — and multiplies it out. That's not good enough for a real answer, for one reason: storage heaters draw electricity overnight, on a fixed schedule, and grid carbon intensity swings hard from night to night depending mostly on wind. A calm, cold night can run two to three times dirtier than a windy one. If you want to know what storage heating actually costs in carbon, you need to know how much of its real electricity draw lands on the dirty nights versus the clean ones — not just the average night.

So the first version of this analysis took the 23 coldest, stillest real nights of last winter — deliberately picked to find the worst case, using real half-hourly data from the National Grid ESO Carbon Intensity API — and checked how often storage heating's carbon intensity on those nights individually exceeded gas's. The answer was 35% of the time. That's a real number, but it's a worst-case sample, not a full-year answer, and I said so at the time.

Getting the full-year, demand-weighted answer meant matching every real household-night in the dataset (14,558 of them, across a full year of 2013 smart-meter data) to the real grid carbon intensity for a similar night today — not by fitting a regression and extrapolating it (which I tried first, and which produced an obviously wrong answer once I checked its calibration range against the real data), but by building an empirical lookup table from a properly sampled set of real nights spanning the full range of temperatures that actually carry the fleet's heat demand.

That's when the mistakes showed up — and both are worth walking through, because "I checked my own work and found a real problem" is a more useful thing to publish than a clean number that happens to be wrong.

**Mistake one: an hour in the wrong direction**

The Carbon Intensity API takes timestamps in UTC. I asked it for "23:00 to 07:00" using a fixed clock that never adjusts for daylight saving — which meant that for every sample night that fell inside British Summer Time, I was actually pulling data for 00:00 to 08:00 local time, an hour later than intended. I checked the size of the error directly: on a calm night it barely moved the number (about 1%), but on a night with a sharp carbon swing around dawn, it was off by nearly 9%. Fourteen of the 31 new sample nights fell inside BST. I refetched all fourteen with the correct window.

**Mistake two: a confound hiding in plain sight**

The second one was more interesting, and I only found it because the corrected chart looked wrong. Plotting carbon intensity by temperature band, the coldest band (-4 to 0°C) came out *cleaner* than the band next to it (0 to 4°C) — backwards from what you'd expect, since colder nights should if anything draw more gas generation, not less.

[CHART 2: chart2_volatility.png — carbon intensity by temperature band against the gas benchmark]

The cause turned out to be a leftover from the first, worst-case sample. Those original 23 nights were picked to be cold *and* still — low wind was part of the selection criterion, not an accident of which nights happened to be cold. They cluster heavily in the 0-4°C band, and because wind — not temperature — is what actually drives grid carbon intensity (more wind means more of the grid's power comes from turbines instead of gas), that band ended up carrying an artificially low average wind speed compared to its neighbours. The dirty-looking cold band wasn't a real property of the weather. It was a selection bias from an earlier, different question, quietly riding along into a new one.

The fix was to stop pooling the two samples. The bin lookup now uses only the second set of 31 nights, which were deliberately sampled with a fair mix of low, medium, and high wind at every temperature — an unconfounded design. The original 23 stay in the analysis, but honestly labelled as what they are: a real worst-case reference (that 35% figure still stands, on its own terms), not part of the average.

That correction moved the headline numbers by more than either the timezone fix or the original bin-width tightening had — storage heating's real advantage over gas turned out to be larger than my first corrected pass suggested, not smaller, and the volatility risk I'd flagged throughout the project turned out to be mostly an artifact of how I'd built the sample, not a property of the grid. Both directions of correction happened in the same afternoon, on the same dataset. I think that's a feature of doing this properly, not a sign it was done badly the first time.

**Carbon and cost don't agree, and that matters**

Here's the part that keeps this from being a simple "heat pumps win" story. At today's Ofgem price cap (7.97p/kWh gas, 26.32p/kWh electricity, Oct-Dec 2026), the same real households' running costs look like this:

[CHART 3: chart3_running_cost.png — running cost by technology and tariff]

Gas costs £418 a year. Storage heating costs £964 unmanaged, or £719 even fully optimised — still meaningfully more than gas, which is the structural problem this whole project exists to work around. A heat pump at the same real field performance costs £470 a year on an ordinary electricity tariff — it loses to gas, for every single household in the dataset. Put the identical hardware on a heat-pump-specific tariff (Economy 7, or Octopus's purpose-built Cosy), and the same heat pump costs £302 — it now beats gas outright, for every household.

Same box. Same SCOP. Same house. The only thing that changed is which tariff it's billed on. That's not a footnote — it's the whole running-cost story. A heat pump is not "cheap" or "expensive" as a category; it's cheap on the right tariff and expensive on the wrong one, and right now most households aren't automatically on the right one.

**What this actually points to**

Put the carbon and cost pictures together and the shape of the problem gets clearer, not muddier. On carbon, heat pumps and even reasonably-run storage heating already beat gas today, decisively in the heat pump's case. On cost, a heat pump only clears that same bar with the right tariff sitting underneath it — the hardware was never the obstacle, the billing structure was.

None of the real barriers standing between here and a heat-pump-heated version of this housing stock are technical. They're a UK electricity-to-gas price ratio that loads a disproportionate share of network and policy cost onto electricity rather than gas; a heat pump installer workforce roughly a ninth the size it needs to be by 2028; a funding scheme (the Boiler Upgrade Scheme) that still excludes social housing outright after its most recent refresh; and a set of tenure and building barriers — freeholder consent, cylinder space, communal heating systems — that hit this specific housing stock harder than most. Every one of those is a policy choice, which means every one of them is also a thing that could be changed. I've written the full case for what that actually means in the policy piece that followed this one.
