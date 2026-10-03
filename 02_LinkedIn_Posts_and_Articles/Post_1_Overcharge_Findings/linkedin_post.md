I spent the last while pulling apart a real UK smart-meter dataset to check something I kept hearing asserted but never seen actually measured: do electric storage heaters really waste as much money as everyone assumes?

Short answer: yes — but not for the reason I expected.

Using half-hourly data from 4,443 London households (2013, but reprojected onto today's real prices), I identified genuine storage-heater households by their load signature, then quantified exactly how much of their overnight charging was unjustified by that night's actual weather.

The number: 12.2% of all overnight charging was pure excess. £117 wasted per household, per year, at current tariffs. Real money, doing nothing but sitting in a hot brick nobody needed.

This isn't a niche problem, either. Roughly 1.7 million UK homes still run on electric storage heating, and an estimated 136,500 of those are in housing associations specifically, still on old-style manual dial controls. A real fuel poverty charity — National Energy Action, no stake in my project — says outdated storage heaters are trapping hundreds of thousands of social housing tenants in fuel poverty right now.

Here's the part I didn't expect: I tested whether simply switching an unmanaged heater onto a smart dynamic tariff (Octopus Agile) would help. It doesn't. It makes things slightly worse — because a heater that doesn't respond to price signals just sits exposed to the expensive peaks while missing all the cheap troughs. The saving was never in the tariff. It's entirely in the timing.

And "storage heaters cost more than gas" turned out to be exactly true, not just repeated folklore. Real prices, same two-bed flat: gas costs £378 a year. An unmanaged storage heater costs £927. Even fully optimised — zero waste, perfectly timed charging — it still costs £691. That's £313 more than gas, forever, no matter how well it's managed. The gap is structural, not behavioural.

Which raises the obvious question: what's the rational response to paying £313 more a year than you need to? Turn the heating down. There's real peer-reviewed evidence this actually happens — households on prepayment meters self-disconnect *more* during cold spells, not less, and over a third of one recent survey now describe their home as cold and damp as a direct result. That's the actual mechanism behind the mould risk housing associations are now legally required to act on under Awaab's Law. Not a guess — a measured pattern, sitting underneath a cost gap I can now put a real number on.

None of this is a new idea — "make storage heaters smarter" isn't exactly an unclaimed insight. What I think might be useful is the rigour: real data, real prices, honest negative results included, not just a plausible-sounding pitch.

I've now built and tested (in software) the actual control logic for a low-cost retrofit. Next step is a physical bench test — relay, LED, real electrician sign-off before anything touches a real heater.

If you work in social housing, energy data, or embedded/IoT and this is remotely interesting to you, I'd love to talk. I'll need the help.
