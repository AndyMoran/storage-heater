# Trying to prove my own project pointless (and what happened instead)

A few weeks ago I published the first real numbers from a project measuring how much money UK storage heaters waste, using actual smart-meter data rather than the usual guesswork. The response raised a fair challenge, and it's one I'd been quietly worried about myself: by the time any hardware retrofit like this could actually be deployed, won't UK housing policy have already solved the problem? Insulation is getting a hard regulatory deadline. Solar and batteries are getting cheap. Maybe the honest answer is that a smart controller for old storage heaters is solving yesterday's problem.

So I went and checked, the same way I checked everything else in this project: with real numbers, not vibes.

## The policy is real, and the clock is short

UK social housing has to reach EPC Band C by 1 April 2030. This isn't a proposal anymore — the government published its formal consultation response in January this year confirming it. Current social housing has no formal minimum efficiency standard at all; typical stock sits at what's effectively EPC F. That's a genuinely big jump, on a genuinely short clock.

## What insulation actually does to the numbers

Real, sourced figures suggest a move of this scale — several EPC bands, not one — cuts heating demand somewhere in the range of 35–50%. I ran that through the same model I'd already built and validated against real household data.

**[Chart 1 here: fig3_scenario_comparison.png — running costs across gas, point-heating, unmanaged storage, Agile, and the optimised "AutoMagic" system, shown both at today's insulation level and after a 2030-standard upgrade]**

The headline: my smart-control system currently saves roughly £236 a year over an unmanaged storage heater. Once a home is properly insulated, that shrinks to somewhere between £118 and £153. Genuinely halved, not a rounding error, but not zero either — because an unmanaged heater tends to overcharge by roughly the same *proportion* of what it delivers, insulated or not. If anything, an old heater sized for a leaky home becomes more oversized once the fabric improves, which cuts slightly the other way.

The honest conclusion: the size of the opportunity is real today and shrinks over the next four years. Anyone building a business case on today's number for a 2030 housing stock is overstating it.

## Solar and battery: real money, wrong season

The obvious next question was whether rooftop solar and a battery close the remaining gap. I'd assumed maybe. The real numbers say no, for a specific and slightly surprising reason: seasonal mismatch.

A typical UK 4kW solar array generates 3,400–4,200kWh across a whole year, and genuinely saves a household £600–1,300 annually once a battery is added — that's real and worth having. But nearly all of that generation happens spring through autumn. I checked what a system like that actually produces in December specifically: less, across the *entire month*, than one real household's *single night* of storage-heater charging in my dataset.

Solar and smart heating control aren't competing for the same money. They're solving two different problems that happen to live in different seasons. A household could reasonably benefit from both.

## The number I wasn't looking for

While checking all this I ran one more calculation almost as an afterthought, and it turned out to be the most important finding in this whole follow-up.

Storage heater usage isn't smooth across the year. In my dataset, 53% of an entire year's charging happens in just four winter months — nearly double the rate a smoothed monthly average would suggest. Translate that into money and an "average" £927 annual unmanaged-heater bill is actually closer to £123 a month for four consecutive months, not the £77 a simple annual-average calculation implies.

That gap is easy to miss if you only ever look at annual figures. It's not easy to miss if your income is fixed and doesn't adjust for winter. There's peer-reviewed research using real UK smart-meter data on prepayment customers showing something genuinely troubling: people self-disconnect *more* during cold snaps, not less, despite needing heat the most. Recent survey data goes further — over half of a prepayment sample have drastically cut their energy use recently, and more than a third now describe their home as cold and damp as a direct result.

That's not a hypothetical anymore. That's the actual mechanism connecting an unmanaged heating system to the exact damp-and-mould risk that Awaab's Law now makes housing associations legally responsible for identifying and fixing on a statutory clock. I'd stop short of calling this existential for any given landlord — that depends on scale and exposure I don't have visibility into — but it's a real, quantifiable, and currently under-examined compliance risk, not just an efficiency question.

**[Chart 2 here: fig4_full_comparison_with_heatpump.png — the full running-cost comparison across every scenario, including heat pump running costs]**

## And, since people asked: what about heat pumps?

I'd deliberately kept heat pumps out of scope until now — they're a different, bigger kind of intervention and I didn't want to give a shallow answer. Having actually checked:

Running costs look genuinely competitive — in the same range as gas, and better than every electric alternative, once you account for a heat pump's efficiency advantage (delivering roughly 3–4 units of heat per unit of electricity).

But the capital picture has two real complications that change the calculation for exactly this kind of property. First, the main government grant that makes heat pumps affordable for most homeowners — £7,500 off installation — explicitly excludes social housing. Second, and more fundamentally: these are storage-heater flats. Most never had a wet radiator system installed in the first place, because that's precisely why they have storage heaters. A heat pump conversion here isn't a boiler swap; it's installing an entire heating system from scratch — radiators, pipework, hot water cylinder, the lot.

Good running-cost case, real and unresolved capital-cost question. I'm not going to pretend otherwise.

## Where this actually leaves things

Not moot. But not the number I published a few weeks ago either, if you're thinking about 2030 rather than today. The honest pitch to a housing association is narrower and, I think, more useful than the first version: this closes a real gap that current policy doesn't address on its own, the size of that gap is time-limited, and the underlying cost pattern is doing real, measurable harm to exactly the tenants Awaab's Law was written to protect — right now, not hypothetically.

I'd rather publish that than a cleaner story that doesn't hold up to the first serious question someone asks.

Still building this in the open, still looking for people who know housing finance, embedded systems, or fuel poverty policy better than I do.
