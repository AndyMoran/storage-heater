Last post I showed the hidden cost: unmanaged storage heaters waste 12.2% of their overnight charge, £117 a year burned into a hot brick that didn't need to be hot. This post is about the fix — and about what fixing it does and doesn't actually achieve.

The original plan was hardware: bolt a relay onto every storage heater — a Shelly Pro 1PM or similar, £50–100 in parts, professionally installed, enforcing the charging window automatically. Still a real idea, still worth building. But it needs an electrician, a BS 7671 sign-off, a bench test, and a housing association willing to fund a retrofit fleet before anyone benefits.

So I built and shipped the software version first: NightDial. It's live now, and it's genuinely calibrated, not a mock-up. I ran the calibration against 42 confirmed storage‑heater households and 13,102 real household‑nights from the same smart‑meter dataset behind the last post. Each evening, NightDial fetches the local forecast for a tenant's postcode and gives one nudge: what to set the dial to tonight.

→ Mildest nights: turn it right down — saves ~90% vs. leaving it on max
→ A typical cold night: still worth ~48%
→ The coldest nights: the top setting is correct — nothing to save, and it says so

Last post's £117 was a population average. Run the same test per household, in £: £40 to £495 a year, median £104, top 10% above £190. It's one HTML file. No app store, no account, no hardware, no electrician.

Here's the honest ceiling, though. Even a household that gets everything right — full compliance, worst starting overcharge — lands around £691/year for a well-run storage heater. Gas costs £378. That's still £313/year more, every year, no matter how well the heater is managed. Nothing here closes that gap, because it isn't a waste problem — it's the physics of resistive electric heat against gas. A relay wouldn't close it either. Only a technology that gets more heat per kWh does that, and the only thing that does is a heat pump.

So I want to be plain about what NightDial actually is: a bridge, not a destination. Heat pumps are the real fix for warm homes in this housing stock, and I think that increasingly clearly the more of this project I do. But heat pump grants exclude social housing, and these flats mostly have no wet system to convert onto — that's blocked for now, not solved. NightDial exists to make the wait less punishing: real, measured money back for a tenant today, at zero cost, while the actual fix stays stuck behind funding.

It's a research prototype — not for real tenant use yet — with one permanent caveat on the page itself: the calibration data is from 2013, before the 2021+ energy crisis and Awaab's Law's excess-cold rules. If anything, that makes today's real waste larger than what's calibrated here.

Try it: andymoran.github.io/nightdial. If you work for a housing association or local authority, I'd value ten minutes of feedback.
