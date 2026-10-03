import numpy as np
GRID_CARBON=0.14395; ELEC_PRICE=0.2632; AC_UNIT_KW=2.7; RUN_HOURS=191
cooling_output_kwh = AC_UNIT_KW*RUN_HOURS

def carnot_cop_cooling(dt_k, t_cold_c=24.0):
    t_c = t_cold_c+273.15
    return t_c/max(dt_k,0.5)

# Commodity/manufacturer rule-of-thumb curve (see commodity_model.py for provenance)
anchor_dt = np.array([0.0, 20.0, 40.0])
anchor_cop_cool = np.array([5.5, 1.4, 0.25])
log_anchor = np.log(anchor_cop_cool)

def commodity_cop_cooling(dt):
    dt = np.asarray(dt, dtype=float)
    slope_last = (log_anchor[-1]-log_anchor[-2])/(anchor_dt[-1]-anchor_dt[-2])
    logcop = np.interp(dt, anchor_dt, log_anchor)
    beyond = dt > anchor_dt[-1]
    logcop = np.where(beyond, log_anchor[-1] + slope_last*(dt-anchor_dt[-1]), logcop)
    return np.exp(logcop)

print("dT(K)  Carnot_cool  single(10%)  optimised(26%)  commodity(anchor curve)")
for dt in [3,6,9,12,15]:
    cc = carnot_cop_cooling(dt)
    comm = commodity_cop_cooling(dt)
    elec = cooling_output_kwh/comm
    print(f"{dt:5.0f}  {cc:10.2f}  {0.10*cc:11.2f}  {0.26*cc:14.2f}  {comm:10.2f}   "
          f"(elec={elec:.1f}kWh cost=£{elec*ELEC_PRICE:.2f} carbon={elec*GRID_CARBON:.1f}kg)")

conv_elec = cooling_output_kwh/3.2
print(f"\nConventional AC (COP 3.2): elec={conv_elec:.1f}kWh cost=£{conv_elec*ELEC_PRICE:.2f} carbon={conv_elec*GRID_CARBON:.1f}kg")
