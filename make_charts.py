import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'

# Palette (validated default, light mode)
BLUE='#2a78d6'; ORANGE='#eb6834'; AQUA='#1baf7a'; YELLOW='#eda100'
MAGENTA='#e87ba4'; GREEN='#008300'; VIOLET='#4a3aa7'; RED='#e34948'
TEXT='#0b0b0b'; TEXT2='#52514e'; SURFACE='#fcfcfb'

# --- Chart 1: Heating cost & carbon comparison ---
techs = ['Gas\nboiler', 'Resistive\nstorage heater', 'ASHP\n(SCOP 2.78)', 'ASHP\n(SCOP 3.83)',
         'GSHP\n(SPF 3.25)', 'Peltier\nsingle-stage*', 'Peltier\ncommodity*', 'Peltier\noptimised*']
cost = [252.21, 687.14, 247.17, 179.41, 211.43, 682.98, 438.55, 262.69]
carbon = [576.9, 375.8, 135.2, 98.1, 115.6, 373.5, 239.9, 143.7]
colors = [RED, ORANGE, AQUA, GREEN, VIOLET, MAGENTA, YELLOW, BLUE]

fig, axes = plt.subplots(1, 2, figsize=(14.5, 6.6), facecolor=SURFACE)

ax = axes[0]
bars = ax.bar(range(len(techs)), cost, color=colors, width=0.62)
ax.set_title('Winter running cost per household\n(one real winter, same 40-household demand)', color=TEXT, fontsize=11, loc='left')
ax.set_ylabel('£ / winter', color=TEXT2)
ax.set_xticks(range(len(techs))); ax.set_xticklabels(techs, fontsize=8, color=TEXT)
for b, v in zip(bars, cost):
    ax.text(b.get_x()+b.get_width()/2, v+12, f'£{v:.0f}', ha='center', fontsize=9, color=TEXT)
ax.set_facecolor(SURFACE)
for s in ['top','right']: ax.spines[s].set_visible(False)
ax.spines['left'].set_color(TEXT2); ax.spines['bottom'].set_color(TEXT2)
ax.tick_params(colors=TEXT2)
ax.set_ylim(0, 760)

ax = axes[1]
bars = ax.bar(range(len(techs)), carbon, color=colors, width=0.62)
ax.set_title('Winter operational carbon per household\n(kgCO2e, same basis)', color=TEXT, fontsize=11, loc='left')
ax.set_ylabel('kgCO2e / winter', color=TEXT2)
ax.set_xticks(range(len(techs))); ax.set_xticklabels(techs, fontsize=8, color=TEXT)
for b, v in zip(bars, carbon):
    ax.text(b.get_x()+b.get_width()/2, v+8, f'{v:.0f}', ha='center', fontsize=9, color=TEXT)
ax.set_facecolor(SURFACE)
for s in ['top','right']: ax.spines[s].set_visible(False)
ax.spines['left'].set_color(TEXT2); ax.spines['bottom'].set_color(TEXT2)
ax.tick_params(colors=TEXT2)
ax.set_ylim(0, 620)

fig.suptitle('Generic Peltier heat pump vs established comparators — heating', fontsize=13, color=TEXT, y=1.02)
fig.text(0.01, -0.09,
    '*Peltier figures: single-stage and optimised from a generic physics model (ZT≈1 = 10% of Carnot; optimised, via better\n'
    'material or control (not multi-staging) = 26% of Carnot, the fraction implied by TCS\'s claimed SCOP 2.9 but not independently\n'
    'confirmed for any real product); commodity rule-of-thumb from manufacturer-published COP curves (TE Technology, Sheetak,\n'
    'and a hobbyist-extracted datasheet curve), not a Carnot-fraction assumption. All at A35 sink, same 40-household winter\n'
    'demand and 2026 tariffs/carbon factors as other bars. Not a specific vendor\'s claimed performance.',
    fontsize=7.5, color=TEXT2)
plt.tight_layout(rect=[0,0.14,1,1])
plt.savefig('chart_heating_comparison.png', dpi=160, facecolor=SURFACE, bbox_inches='tight')
print("saved chart 1")

# --- Chart 2: Cooling COP sensitivity to ΔT ---
dts = np.array([3,6,9,12,15])
cop_single = 0.10 * (297.15/dts)
cop_optimised = 0.26 * (297.15/dts)
conv_ac = np.full_like(dts, 3.2, dtype=float)

# Commodity/manufacturer rule-of-thumb curve: log-linear interpolation/extrapolation
# anchored to a hobbyist-extracted real module datasheet (cooling COP 5.5/1.4/0.25 at dT 0/20/40K)
anchor_dt = np.array([0.0, 20.0, 40.0])
anchor_cop = np.array([5.5, 1.4, 0.25])
log_anchor = np.log(anchor_cop)
slope_last = (log_anchor[-1]-log_anchor[-2])/(anchor_dt[-1]-anchor_dt[-2])
log_cop_commodity = np.interp(dts, anchor_dt, log_anchor)
cop_commodity = np.exp(log_cop_commodity)

fig2, ax2 = plt.subplots(figsize=(8,5.5), facecolor=SURFACE)
ax2.plot(dts, cop_single, marker='o', color=MAGENTA, label='Peltier, single-stage (ZT≈1, 10% Carnot)', linewidth=2.2)
ax2.plot(dts, cop_commodity, marker='^', color=YELLOW, label='Peltier, commodity rule-of-thumb (manufacturer-published)', linewidth=2.2)
ax2.plot(dts, cop_optimised, marker='o', color=BLUE, label='Peltier, optimised (material/control, 26% Carnot)', linewidth=2.2)
ax2.plot(dts, conv_ac, marker='s', color=TEXT2, linestyle='--', label='Conventional split AC (typical COP ~3.2)', linewidth=2)
ax2.set_xlabel('Temperature lift, outside−inside (K)', color=TEXT2)
ax2.set_ylabel('Cooling COP', color=TEXT2)
ax2.set_title('Peltier cooling COP degrades fastest exactly on the hottest days', color=TEXT, fontsize=12, loc='left')
ax2.legend(fontsize=8.5, frameon=False)
ax2.set_facecolor(SURFACE)
for s in ['top','right']: ax2.spines[s].set_visible(False)
ax2.spines['left'].set_color(TEXT2); ax2.spines['bottom'].set_color(TEXT2)
ax2.tick_params(colors=TEXT2)
ax2.annotate('commodity curve crosses\nconventional AC around ΔT≈9K', xy=(9,2.97), xytext=(9.3,7.2),
             fontsize=8, color=TEXT2, arrowprops=dict(arrowstyle='-', color=TEXT2, lw=0.8))
ax2.annotate('...but falls behind\nat heatwave ΔT', xy=(13,3.4), fontsize=8, color=TEXT2)
plt.tight_layout()
plt.savefig('chart_cooling_sensitivity.png', dpi=160, facecolor=SURFACE, bbox_inches='tight')
print("saved chart 2")
