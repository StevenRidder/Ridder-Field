#!/usr/bin/env python3
"""Create publication-quality geometric ceiling figure for Nature/PRL."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import os

# Final data from fixed-H0 chains (all at 1000 samples)
h0_values = np.array([68.5, 69, 69.5, 70, 70.5, 71, 71.5, 72, 72.5, 73, 73.5])
delta_chi2 = np.array([7.0, 2.2, 14.1, 14.5, 22.5, 33.7, 69.0, 91.0, 132.4, 139.6, 184.2])

# Smooth interpolation
h0_smooth = np.linspace(68.0, 74.0, 300)
spline = UnivariateSpline(h0_values, delta_chi2, s=50)
delta_smooth = spline(h0_smooth)
delta_smooth = np.maximum(delta_smooth, 0)  # No negative values

# Create figure with Nature-style formatting
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 10,
    'figure.dpi': 150,
})

fig, ax = plt.subplots(figsize=(10, 6.5))

# Background shading for rejection regions
ax.axhspan(0, 4, alpha=0.15, color='green', zorder=0, label='Comfortable (< 2σ)')
ax.axhspan(4, 9, alpha=0.12, color='yellow', zorder=0, label='Tension (2-3σ)')
ax.axhspan(9, 25, alpha=0.10, color='orange', zorder=0, label='Strong tension (3-5σ)')
ax.axhspan(25, 250, alpha=0.08, color='red', zorder=0, label='Rejected (> 5σ)')

# Plot smooth curve
ax.plot(h0_smooth, delta_smooth, 'k-', lw=2.5, zorder=5)

# Plot data points with error-bar style markers
ax.scatter(h0_values, delta_chi2, s=180, c='navy', edgecolor='white', 
           linewidth=2, zorder=10, marker='o')

# Significance thresholds
for sigma_val, chi2_val, label in [(2, 4, '2σ'), (3, 9, '3σ'), (5, 25, '5σ'), (10, 100, '10σ')]:
    ax.axhline(chi2_val, color='gray', ls='--', alpha=0.5, lw=1, zorder=1)
    ax.text(74.05, chi2_val, label, fontsize=9, va='center', color='gray', ha='left')

# External measurements with bands
# SH0ES: 73.04 ± 1.04
ax.axvspan(73.04-1.04, 73.04+1.04, alpha=0.25, color='crimson', zorder=2)
ax.axvline(73.04, color='crimson', ls='-', lw=2, alpha=0.8, zorder=3)

# JWST/TRGB: 69.8 ± 1.7  
ax.axvspan(69.8-1.7, 69.8+1.7, alpha=0.20, color='dodgerblue', zorder=2)
ax.axvline(69.8, color='dodgerblue', ls='-', lw=2, alpha=0.8, zorder=3)

# Planck ΛCDM: 67.36 ± 0.54
ax.axvspan(67.36-0.54, 67.36+0.54, alpha=0.25, color='purple', zorder=2)

# Mark the optimum
ax.scatter([69.0], [2.2], s=350, c='limegreen', edgecolor='darkgreen', 
           linewidth=3, zorder=15, marker='*')

# Annotations
ax.annotate('EDE Optimum\n$H_0 = 69.0$\n$\\Delta\\chi^2 = +2.2$', 
            xy=(69.0, 2.2), xytext=(67.3, 35),
            arrowprops=dict(arrowstyle='->', lw=2, color='darkgreen', 
                          connectionstyle='arc3,rad=0.2'),
            fontsize=11, ha='center', weight='bold', color='darkgreen',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                     edgecolor='darkgreen', lw=2, alpha=0.95))

ax.annotate('Geometric Ceiling\n$H_0 \\approx 70$\n$\\Delta\\chi^2 > 14$', 
            xy=(70.0, 14.5), xytext=(71.5, 55),
            arrowprops=dict(arrowstyle='->', lw=2, color='darkorange',
                          connectionstyle='arc3,rad=-0.2'),
            fontsize=11, ha='center', weight='bold', color='darkorange',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                     edgecolor='darkorange', lw=2, alpha=0.95))

ax.annotate('SH0ES\n$73.0 \\pm 1.0$\n12σ rejected', 
            xy=(73.04, 148), xytext=(72.0, 180),
            arrowprops=dict(arrowstyle='->', lw=2, color='crimson'),
            fontsize=10, ha='center', weight='bold', color='crimson',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                     edgecolor='crimson', lw=1.5, alpha=0.95))

ax.annotate('JWST/TRGB\n$69.8 \\pm 1.7$', 
            xy=(69.8, 14.5), xytext=(68.0, 75),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='dodgerblue',
                          connectionstyle='arc3,rad=0.3'),
            fontsize=10, ha='center', color='dodgerblue',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                     edgecolor='dodgerblue', lw=1.5, alpha=0.95))

# Labels
ax.set_xlabel('$H_0$ [km s$^{-1}$ Mpc$^{-1}$]', fontsize=15, weight='bold')
ax.set_ylabel('$\\Delta\\chi^2$ relative to $\\Lambda$CDM', fontsize=15, weight='bold')
ax.set_title('The Geometric Ceiling on $H_0$', fontsize=18, weight='bold', pad=15)

ax.set_xlim(67, 74.5)
ax.set_ylim(-5, 210)

# Custom legend
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='navy', 
           markersize=10, markeredgecolor='white', markeredgewidth=1.5,
           label='Fixed-$H_0$ MCMC chains'),
    Line2D([0], [0], marker='*', color='w', markerfacecolor='limegreen',
           markersize=15, markeredgecolor='darkgreen', markeredgewidth=2,
           label='EDE optimum ($H_0 = 69.0$)'),
    Patch(facecolor='crimson', alpha=0.3, label='SH0ES (12σ rejected)'),
    Patch(facecolor='dodgerblue', alpha=0.25, label='JWST/TRGB (at ceiling)'),
    Patch(facecolor='purple', alpha=0.3, label='Planck $\\Lambda$CDM'),
]
ax.legend(handles=legend_elements, loc='upper left', framealpha=0.95, 
          edgecolor='gray', fontsize=10)

ax.grid(alpha=0.3, zorder=0, ls=':')

plt.tight_layout()

# Save
plt.savefig('geometric_ceiling_final.pdf', dpi=300, bbox_inches='tight')
plt.savefig('geometric_ceiling_final.png', dpi=300, bbox_inches='tight')
print("✅ Saved: geometric_ceiling_final.pdf and .png")

# Also save a simpler version for talks
fig2, ax2 = plt.subplots(figsize=(8, 5))
ax2.plot(h0_smooth, delta_smooth, 'k-', lw=3)
ax2.scatter(h0_values, delta_chi2, s=120, c='red', edgecolor='black', lw=1.5, zorder=10)
ax2.axhline(9, color='orange', ls='--', lw=2, label='3σ threshold')
ax2.axhline(25, color='red', ls='--', lw=2, label='5σ threshold')
ax2.axvline(73.04, color='blue', ls=':', lw=2, label='SH0ES')
ax2.axvline(69.8, color='green', ls=':', lw=2, label='JWST/TRGB')
ax2.set_xlabel('$H_0$ [km/s/Mpc]', fontsize=14)
ax2.set_ylabel('$\\Delta\\chi^2$', fontsize=14)
ax2.set_xlim(68, 74)
ax2.set_ylim(-5, 200)
ax2.legend(loc='upper left')
ax2.set_title('Geometric Ceiling: $H_0$ Cannot Exceed 70', fontsize=14, weight='bold')
plt.tight_layout()
plt.savefig('geometric_ceiling_simple.png', dpi=200, bbox_inches='tight')
print("✅ Saved: geometric_ceiling_simple.png")

plt.show()
