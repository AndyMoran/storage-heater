import pandas as pd
import numpy as np

df = pd.read_parquet('/home/claude/phase1_household_nights.parquet')
df['night_date'] = pd.to_datetime(df['night_date'])
winter = df[df['night_date'].dt.month.isin([11,12,1,2])].copy()

# Carbon / tariff constants (established elsewhere in this project, reused unchanged)
GRID_CARBON = 0.14395   # kgCO2e/kWh, consumed basis (DESNZ/Defra 2026)
GAS_CARBON  = 0.18231   # kgCO2e/kWh gross CV
ELEC_PRICE  = 0.2632    # GBP/kWh, Ofgem Oct-Dec 2026 cap, standard rate
GAS_PRICE   = 0.0797    # GBP/kWh
BOILER_EFF  = 0.825

# Sink temperatures to test (K), representing different heat-delivery architectures
SINK_TEMPS_C = {'A35_radiator_modern': 35.0, 'A45_radiator_typical_UK': 45.0}

def carnot_cop_heating(t_h_c, t_c_c):
    t_h = t_h_c + 273.15
    t_c = t_c_c + 273.15
    dt = t_h - t_c
    return np.where(dt > 0.5, t_h / np.maximum(dt, 0.5), np.nan)

def peltier_cop_heating(t_h_c, t_c_c, carnot_fraction):
    return carnot_fraction * carnot_cop_heating(t_h_c, t_c_c)

results = {}
for label, t_sink in SINK_TEMPS_C.items():
    for frac_label, frac in [('single_stage_ZT1_10pct', 0.10), ('optimised_26pct', 0.26)]:
        cop = peltier_cop_heating(t_sink, winter['mean_temp_c'].values, frac)
        cop = np.clip(cop, 0.3, 8.0)  # physical floor/ceiling guard
        elec_in = winter['night_kwh'].values / cop
        results[f'{label}__{frac_label}'] = {
            'mean_cop': np.nanmean(cop),
            'total_elec_kwh_mean_household': None,
        }
        winter[f'cop__{label}__{frac_label}'] = cop
        winter[f'elec_kwh__{label}__{frac_label}'] = elec_in

# Per-household winter totals
per_hh = winter.groupby('LCLid').agg(
    heat_demand_kwh=('night_kwh','sum'),
    **{f'elec_kwh__{label}__{frac_label}': (f'elec_kwh__{label}__{frac_label}','sum')
       for label in SINK_TEMPS_C for frac_label in ['single_stage_ZT1_10pct','optimised_26pct']}
)

summary = per_hh.mean()
print("Mean winter heat demand per household (kWh):", summary['heat_demand_kwh'])
for label in SINK_TEMPS_C:
    for frac_label in ['single_stage_ZT1_10pct','optimised_26pct']:
        col = f'elec_kwh__{label}__{frac_label}'
        elec = summary[col]
        seasonal_cop = summary['heat_demand_kwh'] / elec
        cost = elec * ELEC_PRICE
        carbon = elec * GRID_CARBON
        print(f"{label} / {frac_label}: elec_in={elec:.1f} kWh, seasonal_COP={seasonal_cop:.2f}, cost=£{cost:.2f}, carbon={carbon:.1f} kg")

# Comparators (established elsewhere in project, reused unchanged)
heat_demand = summary['heat_demand_kwh']
gas_input = heat_demand / BOILER_EFF
gas_cost = gas_input * GAS_PRICE
gas_carbon = gas_input * GAS_CARBON
print(f"\nGas boiler: input={gas_input:.1f} kWh, cost=£{gas_cost:.2f}, carbon={gas_carbon:.1f} kg")

storage_cost = heat_demand * ELEC_PRICE
storage_carbon = heat_demand * GRID_CARBON
print(f"Resistive storage heater: cost=£{storage_cost:.2f}, carbon={storage_carbon:.1f} kg")

for scop, name in [(2.78,'ASHP conservative'), (3.83,'ASHP best-practice'), (3.25,'GSHP')]:
    elec = heat_demand/scop
    print(f"{name} (SCOP {scop}): cost=£{elec*ELEC_PRICE:.2f}, carbon={elec*GRID_CARBON:.1f} kg")

per_hh.to_csv('per_household_results.csv')
