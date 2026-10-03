A few weeks ago I wrote that I don't think awareness campaigns fix fuel poverty. Tenants switching to point heating aren't confused — they've already done the maths, and £280 beat £927. I still believe that. But there's a narrower piece of the problem an app can actually help with, so I built one.

NightDial is for the roughly 1.26 million UK homes still on old dial-only storage heaters — no smart control, no timer, just a dial someone has to remember to turn down. Left on the top setting, they overcharge on a mild night exactly as much as a cold one. Every evening, NightDial fetches the local forecast and gives one nudge: what to set the dial to tonight, and a reminder to turn the output down before bed. Nothing to install, nothing sent anywhere except the coordinates needed for the forecast.

The dial recommendation isn't a guess. I ran the calibration against real household data — 42 confirmed storage-heater households, 13,102 real household-nights, from the Low Carbon London smart-meter dataset:

→ Index 1 (mildest nights): saves ~90% vs. leaving it on max
→ Index 4: ~48%
→ Index 6 (coldest nights): the top setting is the right call — nothing to save

One honest caveat, stated permanently on the page itself, not buried: that data is from 2013. It predates both the 2021+ energy-price crisis and Awaab's Law's excess-cold rules for social landlords. A 2013 household could afford to charge more freely than a lot of 2026 tenants can — so if anything, this likely understates the real risk, not overstates it.

Which is the other half of why I built this. NightDial only closes part of the gap between an unmanaged storage heater and a well-run one — it doesn't touch the much bigger gap between storage heating and point heating, and I'm not pretending otherwise. But keeping whole-home heating a viable, less painful option for more tenants is one small lever against the point-heating-into-damp-and-mould pathway Awaab's Law now makes a landlord's legal problem. Seen that way, it's as much a health and asset-protection tool as a tenant savings one.

It's a research prototype, live now: [andymoran.github.io/nightdial](https://andymoran.github.io/nightdial/)

If you work for a housing association or local authority, I'd genuinely value ten minutes of your feedback — what's confusing, what's missing, whether the framing is right for your tenants.
