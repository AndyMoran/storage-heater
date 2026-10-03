import pandas as pd
import numpy as np

df = pd.read_parquet('/home/claude/phase1_household_nights.parquet')
df['night_date'] = pd.to_datetime(df['night_date'])
winter = df[df['night_date'].dt.month.isin([11,12,1,2])].copy()

GRID_CARBON = 0.14395
GAS_CARBON  = 0.18231
ELEC_PRICE  = 0.2632
GAS_PRICE   = 0.0797
BOILER_EFF  = 0.825

SINK_TEMPS_C = {'A35_radiator_modern': 35.0, 'A45_radiator_typical_UK': 45.0}

# --- Commodity/manufacturer-rule-of-thumb COP curve ---
# Anchor points: (deltaT_K, cooling_COP), taken from a hobbyist's extraction of a real
# high-performance single-stage module's datasheet curves (deavid, "Water cooling with
# Peltier, worth it?", 2019) — the only source found this session with multiple COP-vs-dT
# points rather than a single generic band. Treated as log-linear between/beyond anchors.
# NOTE: this is a *better-than-cheapest* module's datasheet curve, not a bargain TEC1-12706
# clone — if anything, optimistic for genuine bottom-tier commodity chips, which independent
# manufacturer FAQs (TE Technology, Sheetak) describe only with a generic COP 0.3-0.8 band
# for single-stage devices without a published dT-resolved curve.
anchor_dt = np.array([0.0, 20.0, 40.0])
anchor_cop_cool = np.array([5.5, 1.4, 0.25])
log_anchor_cop = np.log(anchor_cop_cool)

def commodity_cop_cooling(delta_t_k):
    delta_t_k = np.asarray(delta_t_k, dtype=float)
    # log-linear interpolation inside [0,40], log-linear EXTRAPOLATION beyond using
    # the last segment's slope (holding the curve's observed decay rate, not flat)
    slope_last = (log_anchor_cop[-1] - log_anchor_cop[-2]) / (anchor_dt[-1] - anchor_dt[-2])
    log_cop = np.interp(delta_t_k, anchor_dt, log_anchor_cop)
    beyond = delta_t_k > anchor_dt[-1]
    log_cop = np.where(beyond, log_anchor_cop[-1] + slope_last * (delta_t_k - anchor_dt[-1]), log_cop)
    return np.exp(log_cop)

def commodity_cop_heating(delta_t_k):
    # Qh = Qc + Pin, same device same operating point -> COP_heat = COP_cool + 1
    return commodity_cop_cooling(delta_t_k) + 1.0

results_rows = []
for label, t_sink in SINK_TEMPS_C.items():
    dt = t_sink - winter['mean_temp_c'].values
    cop_cool = commodity_cop_cooling(dt)
    cop_heat = commodity_cop_heating(dt)
    elec_in = winter['night_kwh'].values / cop_heat
    winter[f'dt__{label}'] = dt
    winter[f'cop_cool__{label}'] = cop_cool
    winter[f'cop_heat__{label}'] = cop_heat
    winter[f'elec_kwh__{label}'] = elec_in

per_hh = winter.groupby('LCLid').agg(
    heat_demand_kwh=('night_kwh', 'sum'),
    **{f'elec_kwh__{label}': (f'elec_kwh__{label}', 'sum') for label in SINK_TEMPS_C},
    **{f'dt__{label}': (f'dt__{label}', 'mean') for label in SINK_TEMPS_C},
    **{f'cop_cool__{label}': (f'cop_cool__{label}', 'mean') for label in SINK_TEMPS_C},
)

summary = per_hh.mean()
heat_demand = summary['heat_demand_kwh']
print(f"Mean winter heat demand per household: {heat_demand:.1f} kWh\n")

for label in SINK_TEMPS_C:
    elec = summary[f'elec_kwh__{label}']
    seasonal_cop_heat = heat_demand / elec
    seasonal_cop_cool_implied = seasonal_cop_heat - 1
    cost = elec * ELEC_PRICE
    carbon = elec * GRID_CARBON
    print(f"{label}: mean ΔT={summary[f'dt__{label}']:.1f}K | "
          f"seasonal cooling-mode COP (anchor curve, mean) ~{summary[f'cop_cool__{label}']:.2f} | "
          f"seasonal HEATING COP (demand-weighted) = {seasonal_cop_heat:.2f} | "
          f"elec_in={elec:.1f} kWh | cost=£{cost:.2f} | carbon={carbon:.1f} kg")

# Comparators, reused unchanged
gas_input = heat_demand / BOILER_EFF
print(f"\nGas boiler: cost=£{gas_input*GAS_PRICE:.2f}, carbon={gas_input*GAS_CARBON:.1f} kg")
storage_cost = heat_demand * ELEC_PRICE
storage_carbon = heat_demand * GRID_CARBON
print(f"Resistive storage heater: cost=£{storage_cost:.2f}, carbon={storage_carbon:.1f} kg")
for scop, name in [(2.78, 'ASHP conservative'), (3.83, 'ASHP best-practice'), (3.25, 'GSHP')]:
    elec = heat_demand / scop
    print(f"{name} (SCOP {scop}): cost=£{elec*ELEC_PRICE:.2f}, carbon={elec*GRID_CARBON:.1f} kg")

per_hh.to_csv('per_household_results_commodity.csv')
