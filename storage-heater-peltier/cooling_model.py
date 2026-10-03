import numpy as np

GRID_CARBON = 0.14395
ELEC_PRICE  = 0.2632

# Generic UK cooling demand assumption, from FES 2024 primary workbook figures
# (confirmed directly, cited in project's uk_cooling_demand_grid_peak_load.md):
# 2.7 kW average unit rating, 191 running hours/year
AC_UNIT_KW = 2.7
RUN_HOURS = 191
cooling_output_kwh = AC_UNIT_KW * RUN_HOURS
print(f"Generic annual cooling output assumption: {cooling_output_kwh:.1f} kWh/year/household")

# Conventional split AC/air-to-air heat pump cooling COP (industry-typical, NOT independently
# primary-verified this session -- flagged as such in the writeup)
CONV_AC_COP = 3.2

# Peltier cooling: COP_cooling = COP_heating - 1 (ideal reversible relation), same Carnot-fraction logic
def carnot_cop_cooling(t_h_c, t_c_c):
    t_h = t_h_c + 273.15
    t_c = t_c_c + 273.15
    dt = t_h - t_c
    return t_c / max(dt, 0.5)

# Representative UK summer cooling condition: room/sink at 24C (desired indoor temp output target
# for the exhaust side... careful with direction), outdoor/source at 30C (hot summer day, heat
# rejected TO outside, so "hot side" = outside 30C, "cold side" = indoor 24C)
T_HOT_OUTSIDE = 30.0
T_COLD_INSIDE = 24.0
dT_cooling = T_HOT_OUTSIDE - T_COLD_INSIDE  # 6K -- cooling lift is much smaller than winter heating lift

carnot_cool = carnot_cop_cooling(T_HOT_OUTSIDE, T_COLD_INSIDE)
for frac_label, frac in [('single_stage_ZT1_10pct', 0.10), ('optimised_26pct', 0.26)]:
    cop_cool = frac * carnot_cool
    elec_in = cooling_output_kwh / cop_cool
    cost = elec_in * ELEC_PRICE
    carbon = elec_in * GRID_CARBON
    print(f"Peltier cooling {frac_label}: dT={dT_cooling}K, Carnot={carnot_cool:.2f}, COP={cop_cool:.2f}, "
          f"elec={elec_in:.1f} kWh, cost=£{cost:.2f}, carbon={carbon:.1f} kg")

conv_elec = cooling_output_kwh / CONV_AC_COP
print(f"\nConventional split AC (COP {CONV_AC_COP}): elec={conv_elec:.1f} kWh, "
      f"cost=£{conv_elec*ELEC_PRICE:.2f}, carbon={conv_elec*GRID_CARBON:.1f} kg")
