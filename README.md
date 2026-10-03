# Storage Heater Peltier Assessment

A generic, vendor-independent techno-economic feasibility assessment of Peltier
(thermoelectric) heating and cooling, applied to the same 40-household real
smart-meter demand dataset used elsewhere in the storage-heater VPP project.

This is a physics-and-published-data feasibility check, not a product review:
no commodity or near-market manufacturer offering anything comparable to
TCS/Hummingbird's packaged thermoelectric heating/cooling product was found
anywhere, including China, at the time of writing (October 2026). The
technology looks *possible* on the physics; there is no verified product to
test it against.

## Contents

- `generic_peltier_techno_economic_assessment.md` — the full write-up: physics
  model, heating results, cooling results, capital cost evidence gap,
  synthesis, and a verification log (every figure tagged confirmed directly /
  triangulated / modelled-not-verified).
- `chart_heating_comparison.png`, `chart_cooling_sensitivity.png` — the two
  charts referenced from the write-up.
- `model.py` — the core heating physics model (single-stage 10% Carnot and
  "optimised" 26% Carnot scenarios) applied to the 40-household winter demand.
- `commodity_model.py` — the manufacturer-rule-of-thumb heating scenario,
  built from published TE Technology / Sheetak COP bands and a hobbyist-
  extracted real module datasheet curve, converted via COP_heat = COP_cool + 1.
- `cooling_model.py`, `cooling_sensitivity.py` — the cooling-side COP model
  and its sensitivity to temperature lift (ΔT).
- `make_charts.py` — regenerates both PNG charts from the modelled figures.

## Data dependency

The scripts expect `phase1_household_nights.parquet` (the 40-household winter
demand dataset used throughout the wider storage-heater project) to be
present alongside them to re-run from scratch. That file is **not** included
in this repo — it stays local, alongside the raw `LCL_2013.csv` source data,
per the project's convention of keeping large/raw data out of version
control (see `.gitignore`).

## Status

First-pass assessment, October 2026. Deliberately left with an open,
documented methodological limitation (see Section 6 of the write-up,
"Known limitation... heating-COP formula") rather than pushed further —
the write-up explains why that's the right place to stop.
