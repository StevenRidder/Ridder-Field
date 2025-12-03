#!/usr/bin/env python3
"""
plot_v3_calibration.py - Create calibration plots for V3 model

Generates:
1. H0 vs Lambda_tail calibration curve
2. Parameter space visualization
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)

# Calibration data from tail scans
tail_data = {
    # Coarse scan
    'coarse': {
        'Lambda_tail': [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
        'H0': [67.36, 67.36, 67.36, 67.51, 68.39, 80.73, 285.31, 1110.93],
    },
    # Fine scan
    'fine': {
        'Lambda_tail': [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
        'H0': [68.39, 69.33, 70.88, 73.19, 76.42, 80.73],
    }
}

# Target measurements
H0_Planck = 67.36
H0_Planck_err = 0.54
H0_TRGB = 69.8
H0_TRGB_err = 1.7
H0_SH0ES = 73.04
H0_SH0ES_err = 1.04

# Calibrated branches
Lambda_TRGB = 1.2
H0_TRGB_model = 69.23
Lambda_SH0ES = 1.6
H0_SH0ES_model = 73.10

# =============================================================================
# PLOT 1: H0 vs Lambda_tail Calibration Curve
# =============================================================================

fig, ax = plt.subplots(1, 1, figsize=(10, 7))

# Plot coarse scan (log scale)
coarse = tail_data['coarse']
ax.plot(coarse['Lambda_tail'], coarse['H0'], 'o-', color='steelblue', 
        alpha=0.5, markersize=6, linewidth=1.5, label='Coarse scan')

# Plot fine scan (linear region)
fine = tail_data['fine']
ax.plot(fine['Lambda_tail'], fine['H0'], 's-', color='darkblue', 
        markersize=8, linewidth=2, label='Fine scan', zorder=10)

# Observational targets (horizontal bands)
ax.axhspan(H0_Planck - H0_Planck_err, H0_Planck + H0_Planck_err, 
          color='gray', alpha=0.2, label=f'Planck: {H0_Planck:.2f}±{H0_Planck_err:.2f}')
ax.axhspan(H0_TRGB - H0_TRGB_err, H0_TRGB + H0_TRGB_err, 
          color='green', alpha=0.2, label=f'TRGB: {H0_TRGB:.1f}±{H0_TRGB_err:.1f}')
ax.axhspan(H0_SH0ES - H0_SH0ES_err, H0_SH0ES + H0_SH0ES_err, 
          color='red', alpha=0.2, label=f'SH0ES: {H0_SH0ES:.2f}±{H0_SH0ES_err:.2f}')

# Calibrated branches (vertical lines)
ax.axvline(Lambda_TRGB, color='green', linestyle='--', linewidth=2, 
          label=f'TRGB branch: Λ={Lambda_TRGB} meV')
ax.axvline(Lambda_SH0ES, color='red', linestyle='--', linewidth=2, 
          label=f'SH0ES branch: Λ={Lambda_SH0ES} meV')

# Mark calibrated points
ax.plot(Lambda_TRGB, H0_TRGB_model, 'o', color='darkgreen', 
       markersize=12, markeredgecolor='black', markeredgewidth=2, zorder=20,
       label=f'v3_trgb: H₀={H0_TRGB_model:.2f}')
ax.plot(Lambda_SH0ES, H0_SH0ES_model, 'o', color='darkred', 
       markersize=12, markeredgecolor='black', markeredgewidth=2, zorder=20,
       label=f'v3_shoes: H₀={H0_SH0ES_model:.2f}')

# Styling
ax.set_xlabel('Λ_tail [meV]', fontsize=14, fontweight='bold')
ax.set_ylabel('H₀ [km/s/Mpc]', fontsize=14, fontweight='bold')
ax.set_title('V3 Tail Calibration: H₀ vs Λ_tail', fontsize=16, fontweight='bold')
ax.set_xlim(0, 2.5)
ax.set_ylim(66, 85)
ax.grid(True, alpha=0.3)
ax.legend(loc='upper left', fontsize=10, framealpha=0.9)

# Add text annotations
ax.text(0.5, 82, 'Tail-only calibration\n(EDE disabled)', 
       fontsize=11, style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
ax.text(1.8, 68, 'Steep\nscaling!', fontsize=11, fontweight='bold', 
       color='darkred', ha='center')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'v3_H0_vs_Lambda_tail.png', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'v3_H0_vs_Lambda_tail.pdf', bbox_inches='tight')
print(f'✓ Saved: {OUTPUT_DIR / "v3_H0_vs_Lambda_tail.png"}')

# =============================================================================
# PLOT 2: Log-scale version to show full range
# =============================================================================

fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Left panel: Full range (log scale)
ax1.plot(coarse['Lambda_tail'], coarse['H0'], 'o-', color='steelblue', 
        markersize=8, linewidth=2)
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.axhline(H0_TRGB, color='green', linestyle='--', linewidth=2, alpha=0.7)
ax1.axhline(H0_SH0ES, color='red', linestyle='--', linewidth=2, alpha=0.7)
ax1.axhline(H0_Planck, color='gray', linestyle='--', linewidth=2, alpha=0.7)
ax1.set_xlabel('Λ_tail [meV]', fontsize=12, fontweight='bold')
ax1.set_ylabel('H₀ [km/s/Mpc]', fontsize=12, fontweight='bold')
ax1.set_title('Full Range (Log-Log)', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3, which='both')
ax1.set_xlim(0.01, 10)
ax1.set_ylim(60, 2000)

# Annotate targets
ax1.text(0.015, H0_Planck, 'Planck', fontsize=10, va='center')
ax1.text(0.015, H0_TRGB, 'TRGB', fontsize=10, va='center', color='green')
ax1.text(0.015, H0_SH0ES, 'SH0ES', fontsize=10, va='center', color='red')

# Right panel: Viable window (linear scale)
ax2.plot(fine['Lambda_tail'], fine['H0'], 's-', color='darkblue', 
        markersize=10, linewidth=2.5)
ax2.fill_between([1.0, 2.0], 66, 85, color='lightblue', alpha=0.3, 
                label='Viable window')
ax2.axhspan(H0_TRGB - H0_TRGB_err, H0_TRGB + H0_TRGB_err, 
           color='green', alpha=0.2)
ax2.axhspan(H0_SH0ES - H0_SH0ES_err, H0_SH0ES + H0_SH0ES_err, 
           color='red', alpha=0.2)

# Mark calibrated points
ax2.plot(Lambda_TRGB, H0_TRGB_model, 'o', color='darkgreen', 
        markersize=14, markeredgecolor='black', markeredgewidth=2, zorder=20)
ax2.plot(Lambda_SH0ES, H0_SH0ES_model, 'o', color='darkred', 
        markersize=14, markeredgecolor='black', markeredgewidth=2, zorder=20)

# Add error bars
ax2.errorbar([Lambda_TRGB], [H0_TRGB], yerr=H0_TRGB_err, 
            fmt='none', ecolor='green', capsize=5, capthick=2, alpha=0.7)
ax2.errorbar([Lambda_SH0ES], [H0_SH0ES], yerr=H0_SH0ES_err, 
            fmt='none', ecolor='red', capsize=5, capthick=2, alpha=0.7)

ax2.set_xlabel('Λ_tail [meV]', fontsize=12, fontweight='bold')
ax2.set_ylabel('H₀ [km/s/Mpc]', fontsize=12, fontweight='bold')
ax2.set_title('Viable Window (Linear)', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0.9, 2.1)
ax2.set_ylim(66, 82)
ax2.legend(loc='upper left', fontsize=10)

# Add annotations
ax2.annotate(f'TRGB: {H0_TRGB_model:.2f}', xy=(Lambda_TRGB, H0_TRGB_model), 
            xytext=(Lambda_TRGB-0.15, H0_TRGB_model-3), fontsize=10,
            arrowprops=dict(arrowstyle='->', color='darkgreen', lw=1.5))
ax2.annotate(f'SH0ES: {H0_SH0ES_model:.2f}', xy=(Lambda_SH0ES, H0_SH0ES_model), 
            xytext=(Lambda_SH0ES+0.15, H0_SH0ES_model+3), fontsize=10,
            arrowprops=dict(arrowstyle='->', color='darkred', lw=1.5))

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'v3_calibration_full.png', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'v3_calibration_full.pdf', bbox_inches='tight')
print(f'✓ Saved: {OUTPUT_DIR / "v3_calibration_full.png"}')

# =============================================================================
# PLOT 3: Parameter Space (Lambda_tail vs f_EDE)
# =============================================================================

fig3, ax = plt.subplots(1, 1, figsize=(10, 8))

# Branches
branches = [
    {'name': 'ΛCDM', 'Lambda': 0.0, 'f_EDE': 0.0, 'H0': 67.36, 
     'color': 'gray', 'marker': 's', 'size': 200},
    {'name': 'TRGB', 'Lambda': 1.2, 'f_EDE': 0.083, 'H0': 69.23, 
     'color': 'green', 'marker': 'o', 'size': 300},
    {'name': 'SH0ES', 'Lambda': 1.6, 'f_EDE': 0.171, 'H0': 73.10, 
     'color': 'red', 'marker': 'o', 'size': 300},
]

for branch in branches:
    ax.scatter(branch['Lambda'], branch['f_EDE'], 
              s=branch['size'], c=branch['color'], marker=branch['marker'],
              edgecolors='black', linewidths=2, zorder=10, alpha=0.8,
              label=f"{branch['name']}: H₀={branch['H0']:.2f}")

# Constraint regions
ax.axhspan(0.0, 0.15, color='lightgreen', alpha=0.2, label='Typical EDE bound')
ax.axhspan(0.15, 0.20, color='yellow', alpha=0.2, label='Marginal EDE')
ax.axhspan(0.20, 0.30, color='red', alpha=0.1, label='Excluded (Model 1.0)')

# Viable tail range
ax.axvspan(1.0, 2.0, color='lightblue', alpha=0.2, label='Viable Λ_tail')

# Arrows showing evolution
ax.arrow(0.0, 0.0, 1.1, 0.075, head_width=0.01, head_length=0.1, 
        fc='green', ec='green', alpha=0.5, linewidth=2)
ax.arrow(1.2, 0.083, 0.35, 0.08, head_width=0.01, head_length=0.1, 
        fc='red', ec='red', alpha=0.5, linewidth=2)

ax.text(0.5, 0.04, 'TRGB path', fontsize=11, color='green', fontweight='bold')
ax.text(1.3, 0.15, 'SH0ES path', fontsize=11, color='red', fontweight='bold')

ax.set_xlabel('Λ_tail [meV]', fontsize=14, fontweight='bold')
ax.set_ylabel('f_EDE', fontsize=14, fontweight='bold')
ax.set_title('V3 Parameter Space: Λ_tail vs f_EDE', fontsize=16, fontweight='bold')
ax.set_xlim(-0.2, 2.5)
ax.set_ylim(-0.02, 0.25)
ax.grid(True, alpha=0.3)
ax.legend(loc='upper left', fontsize=10, framealpha=0.9)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'v3_parameter_space.png', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'v3_parameter_space.pdf', bbox_inches='tight')
print(f'✓ Saved: {OUTPUT_DIR / "v3_parameter_space.png"}')

print()
print('=' * 70)
print('All calibration plots created successfully!')
print('=' * 70)
print(f'\nPlots saved to: {OUTPUT_DIR}')
print('\nGenerated files:')
print('  1. v3_H0_vs_Lambda_tail.png/pdf - Main calibration curve')
print('  2. v3_calibration_full.png/pdf - Full range + viable window')
print('  3. v3_parameter_space.png/pdf - Lambda_tail vs f_EDE')

plt.show()

