#!/usr/bin/env python3
"""
Generate H0 profile figure for the paper.
Shows chi2(H0) for EDE with convergence window bands.
"""
import numpy as np
import matplotlib.pyplot as plt
import os

# H0 profile data from check_h0_ceiling.py
h0_values = [68.5, 69, 69.5, 70, 70.5, 71, 71.5, 72, 72.5, 73, 73.5]
delta_chi2 = [7.0, 2.2, 14.1, 14.5, 22.5, 33.7, 69.0, 91.0, 132.4, 139.6, 184.2]

# Reference values
lcdm_chi2_at_68 = 0  # LCDM is the baseline
shoes_h0 = 73.04
shoes_h0_err = 1.04
trgb_h0 = 69.8
trgb_h0_err = 1.7

# Create figure
fig, ax = plt.subplots(figsize=(10, 7))

# Plot EDE profile
ax.plot(h0_values, delta_chi2, 'o-', color='#E63946', linewidth=2.5, 
        markersize=8, label=r'EDE ($\phi$CDM)', zorder=5)

# Add convergence window (69-71)
ax.axvspan(69, 71, alpha=0.15, color='green', label='Convergence window')

# Add H0 measurement bands
ax.axvspan(shoes_h0 - shoes_h0_err, shoes_h0 + shoes_h0_err, 
           alpha=0.2, color='blue', label=f'SH0ES (${shoes_h0:.1f} \\pm {shoes_h0_err:.2f}$)')
ax.axvspan(trgb_h0 - trgb_h0_err, trgb_h0 + trgb_h0_err, 
           alpha=0.2, color='orange', label=f'TRGB (${trgb_h0:.1f} \\pm {trgb_h0_err:.1f}$)')

# Add reference lines
ax.axhline(0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
ax.axhline(10, color='gray', linestyle=':', linewidth=1, alpha=0.5)
ax.axhline(50, color='gray', linestyle=':', linewidth=1, alpha=0.5)
ax.axhline(100, color='gray', linestyle=':', linewidth=1, alpha=0.5)

# Add LCDM point at H0=68.5 (its preferred value)
ax.scatter([68.5], [0], marker='s', s=100, color='#457B9D', 
           edgecolor='black', linewidth=1.5, zorder=6, label=r'$\Lambda$CDM baseline')

# Annotations
ax.annotate(r'$\Delta\chi^2 \approx 0$', xy=(68.7, 2), fontsize=10, color='gray')
ax.annotate(r'$\Delta\chi^2 = 10$', xy=(73.2, 12), fontsize=9, color='gray')
ax.annotate(r'$\Delta\chi^2 = 50$', xy=(73.2, 52), fontsize=9, color='gray')
ax.annotate(r'$\Delta\chi^2 = 100$', xy=(73.2, 102), fontsize=9, color='gray')

# Key values annotation
ax.annotate('$H_0 = 69$:\n$\\Delta\\chi^2 = +2.2$', 
            xy=(69, 2.2), xytext=(67.5, 40),
            arrowprops=dict(arrowstyle='->', color='black', lw=1),
            fontsize=10, ha='center')
ax.annotate('$H_0 = 70$:\n$\\Delta\\chi^2 = +14.5$', 
            xy=(70, 14.5), xytext=(70, 60),
            arrowprops=dict(arrowstyle='->', color='black', lw=1),
            fontsize=10, ha='center')
ax.annotate('$H_0 = 72$:\n$\\Delta\\chi^2 = +91$\n(catastrophic)', 
            xy=(72, 91), xytext=(71, 140),
            arrowprops=dict(arrowstyle='->', color='black', lw=1),
            fontsize=10, ha='center')

# Labels
ax.set_xlabel(r'$H_0$ [km s$^{-1}$ Mpc$^{-1}$]', fontsize=14)
ax.set_ylabel(r'$\Delta\chi^2$ relative to $\Lambda$CDM', fontsize=14)
ax.set_title(r'Geometric Ceiling: $\chi^2$ Profile for Fixed $H_0$', fontsize=14)

ax.set_xlim(68, 74)
ax.set_ylim(-10, 200)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('h0_profile_figure.png', dpi=300, bbox_inches='tight')
plt.savefig('h0_profile_figure.pdf', dpi=300, bbox_inches='tight')
print('Saved: h0_profile_figure.png and h0_profile_figure.pdf')

# Also save data as CSV for the paper
with open('h0_profile_data.csv', 'w') as f:
    f.write('H0,delta_chi2\n')
    for h, d in zip(h0_values, delta_chi2):
        f.write(f'{h},{d}\n')
print('Saved: h0_profile_data.csv')

