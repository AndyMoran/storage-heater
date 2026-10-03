# What a real UK smart-meter dataset actually says about storage heaters

Everyone who's ever lived with an electric storage heater has a story about it: the bedroom that's an oven at 7am and stone cold by 4pm, the bill that never quite matches how warm the house felt. It's one of those problems everybody agrees is real and nobody has actually measured. So I decided to measure it.

## The question

Not "could a smarter storage heater save money" — obviously yes, in theory almost anything can. The actual question was narrower and harder: does real, open UK smart-meter data show a genuine, quantifiable overcharge-and-afternoon-exhaustion pattern, at what scale, and for what share of the population — or is the whole premise weaker than the received wisdom assumes?

## Finding the households

I worked from the Low Carbon London dataset — half-hourly electricity readings from 4,443 London households across 2013, one of the few open, genuinely granular UK smart-meter datasets that exists. The dataset doesn't tell you which households have storage heaters. You have to find them from the shape of their own electricity use.

My first attempts at this were, honestly, wrong. A simple "big block of power overnight" rule sounded reasonable and completely failed — it couldn't reliably separate real storage heaters from ordinary noisy household consumption. What actually worked, after several dead ends, was a different signal entirely: what *share* of a household's whole day's electricity gets used overnight. Real heater households cluster hard around 70–90%. Everyone else sits around 20%. It's not a subtle difference once you're looking at the right thing — the gap in the data is enormous and it doesn't need a fitted threshold, it just needs eyes.

That gave me 43 households I could say, with real confidence, are genuinely storage-heater homes. About 1% of the sample.

## What they actually waste

For each of those households, I built a model of their own individual relationship between outdoor temperature and how much they charge overnight — not a generic assumption, their own real fitted behaviour. Then I checked every single night of the year against it: did they charge more than that night's weather justified?

**12.2% of all overnight charging was excess.** Not needed for warmth. Just cost, sitting in a hot ceramic brick that nobody asked for. Reprojected onto today's real Economy 7 rates, that's **£117 wasted per household per year** — and that's the conservative half of the picture, since a genuine negative result on the *other* half (whether heat runs out and forces expensive afternoon top-ups) didn't hold up under testing, and I reported that honestly rather than force a tidier story.

## The twist I didn't expect

The obvious next move seemed to be: put these households on a smart, time-of-use tariff instead. Cheaper wholesale prices overnight, more expensive at peak — surely that alone helps?

It doesn't. Tested against real half-hourly Octopus Agile price data, a *dumb* heater — one that charges the same way regardless of what electricity actually costs at that moment — comes out slightly **worse off** on a dynamic tariff than on a flat one. It's fully exposed to the tariff's expensive peaks and captures none of its cheap troughs, because it was never designed to respond to a price signal in the first place.

The saving was never in switching tariffs. It's entirely in timing the charge intelligently — which is a genuinely different, harder problem, and the actual reason a smart controller is worth building at all.

## This isn't a niche problem

Before going further, it's worth being clear about scale — it's easy to assume storage heaters are a dwindling curiosity. They're not.

Roughly 1.7 million homes across the UK are still heated by electric storage heaters. The English Housing Survey's own data shows about a quarter of those have some form of automatic charge control — meaning roughly three-quarters, an estimated 1.26 million homes nationally, are still running the old manual dial system this project studies. Narrow that to housing associations specifically, and the English Housing Survey puts storage-heated homes in that tenure at 182,000–187,000, with an estimated 136,500 of those still on old-style manual dials.

That's not a rounding error, and it's not just my own read on it. National Energy Action — a fuel poverty charity with no stake in whether this project succeeds — states plainly that outdated, inefficient electric storage heaters are trapping hundreds of thousands of social housing tenants in fuel poverty right now.

## The number that matters more than the headline

"Storage heaters cost more than gas" is one of those things everyone repeats and nobody quite measures. So I built the comparison properly — real current (2026) prices, a typical two-bedroom social housing flat, not an anecdote.

| Heating method | Annual cost |
|---|---|
| Gas central heating | £378 |
| Storage heater, unmanaged (today's typical behaviour) | £927 |
| Storage heater, overcharge eliminated | £814 |
| Storage heater, fully optimised (smart timing + no overcharge) | £691 |

Here's the finding that actually changed how I think about the whole problem. I built the best case this data can support — overcharge eliminated completely, every charge timed to the cheapest possible half-hours. Electric storage heating *still* costs **£313 a year more than gas**, for the same amount of heat delivered.

That gap doesn't shrink with better behaviour. It's structural — a function of the underlying economics of resistive electric heat versus gas, not something a smarter controller can engineer away. And if you spend any time around social housing, that number should make you uneasy in a specific way: it's a direct, quantifiable, ever-present incentive for a tenant to under-heat their home. Not because they're careless — because the arithmetic genuinely doesn't favour running the heating properly, even for someone doing everything a smart system could ask of them.

## The rational response — and what it actually costs

If you're paying £313 a year more than your gas-heated neighbour no matter how carefully you manage the heater, there's a rational response available: use less heat than you need. Turn the dial down. Let the room run cold.

That's not a hypothetical, and it's not just my own inference. A study using real GB smart-meter data on prepayment customers found something genuinely troubling: households self-disconnect *more* during cold spells, not less — precisely when they need heat most and can least afford to keep paying for it. Separately, recent survey data on prepayment customers found over half have drastically cut their energy use recently, and more than a third now describe their home as cold and damp as a direct result.

That's the actual mechanism connecting an unmanaged heating system's cost to the specific harm — damp and mould — that Awaab's Law now makes social landlords legally responsible for identifying and fixing on a statutory clock. Not a chain of assumptions. A measured, documented pattern, sitting underneath a cost gap this project can now put a real number on.

I went looking for that exact behaviour — tenants visibly cutting their heaters off mid-winter — directly in my own 2013 dataset, and found no trace of it. But 2013 predates the price shocks of the last few years by a wide margin, so a single quiet historical year was never going to be the right place to catch it. The structural cost gap above, and the independent national evidence, are the more honest, more durable findings — neither depends on catching any one tenant in the act, and neither goes stale the way a single year's behavioural snapshot would.

## What's actually built

This isn't just an analysis anymore. Working from the real calibration the data produced, I've built:

- A forecast engine that turns tomorrow's weather into a physically grounded prediction of how much charge a given household should actually need
- A six-level "charge target" index, calibrated directly from the real empirical distribution in the data and matched to the actual 1–6 dial numbering found on real storage heaters — not a demo number, and not guessed at either (an early version assumed five levels until I checked a real housing association's own tenant guide)
- Tenant-facing messaging, checked line by line against actual thermal-comfort science rather than plausible-sounding claims (an early draft overstated a humidity/comfort effect by roughly 3–5x against the real ISO 7730 standard — worth catching before it reaches anyone)
- The actual control logic for a hardware retrofit — off-peak charging, a tenant override, a humidity-linked comfort adjustment — unit-tested against every required safety scenario in software, including the one that matters most: if a sensor drops out, the system fails toward keeping someone warm, never toward silently switching off

## What's next

A physical bench test: a real smart relay, a low-power LED standing in for the heater, before anything touches mains current or a real appliance. Only after that succeeds, and only with a qualified electrician's sign-off, does this go anywhere near an actual heater installation.

I want to be honest about the idea itself: "make storage heaters smarter" is not a novel insight. Plenty of people have proposed roughly this. What I think is more useful, and rarer, is doing the actual homework underneath it — real data, real current prices, a real market-sizing exercise, independent evidence for the human cost, and a negative result reported as plainly as a positive one.

I'll need real help to take this further — hardware, embedded control, and eventually a housing association willing to be the first real test case. If any of that is your world, I'd like to talk.
