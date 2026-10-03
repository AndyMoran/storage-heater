"""
Phase 2.3 nudge copy config (METHODOLOGY.md 2.3).

Templates live here as data, not scattered as inline strings through
src/nudge_generator.py, per the explicit instruction.

Register: plain, short, second person (PROJECT.md Part 8 Section 20 --
tenant-facing SMS/app copy is its own register, distinct from every other
document in this project). Tested for reading level in
src/nudge_generator.py's self-test, not just eyeballed.

Humidity/comfort line: resolved 2026-09-02 (evidence_map.md) after
checking the original claim ("18C feels like 21C") against ISO 7730
directly -- it would require a physically impossible 100-percentage-point
RH swing to support, and an independent SET/ET*-model source reached the
same "small effect" conclusion by a different route. NO degree-equivalence
number is used below. The mould/dampness claim is kept (well-supported,
multiple sources) but is NOT attributed to ASHRAE 55, which explicitly
disclaims mould coverage.
"""

# Dial 1 (mildest) -> Dial 6 (coldest). Six levels, matching the real physical dial numbering
# (1-6) confirmed 2026-09-02 against a real housing association's Dimplex heater tenant guide --
# was five (a round-number guess, not checked against a real product) before this.
CHARGE_LEVEL_TEMPLATES: dict[int, str] = {
    1: "Tonight's mild. Turn your heater's input dial right down to 1.",
    2: "A mild night ahead. Set your heater's input dial to 2.",
    3: "A cool night. Set your heater's input dial to 3.",
    4: "Getting colder. Set your heater's input dial to 4.",
    5: "A cold night ahead. Set your heater's input dial to 5.",
    6: "A very cold night. Set your heater's input dial to 6, the top setting.",
}

OUTPUT_DIAL_REMINDER = (
    "Before bed, turn your output dial right down too, to its lowest number. "
    "This saves tonight's heat for tomorrow."
)

# Supplementary tip, shown at most a few times a month (see src/nudge_generator.py),
# never mixed into the core charge-level instruction.
HUMIDITY_TIP = (
    "Tip: keeping the air less damp stops that clammy feeling and helps "
    "prevent mould. You shouldn't need the heating past 20C once the air's drier."
)

# Known, explicit gap (not silently resolved): the Target Charge Index this
# copy is driven by calibrates the overcharge-avoiding half only. There is
# no validated exhaustion-avoiding floor (Phase 1's exhaustion test was a
# negative result) -- so this copy cannot and does not claim to prevent
# running out of heat by afternoon, only to avoid paying for heat that
# isn't needed.
EXHAUSTION_DISCLAIMER_NOTE = (
    "This helps you avoid paying for heat you don't need on mild nights. "
    "It can't yet tell you if you'll run low on heat later in the day."
)
