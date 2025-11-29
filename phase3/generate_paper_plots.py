#!/usr/bin/env python3
"""
Generate all publication plots for the Geometry-First Cosmology paper.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# Style settings for publication
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

# =============================================================================
# DATA
# =============================================================================

# Tier 10 SH0ES World Results
MODELS = {
    "ΛCDM": {"H0": 68.29, "H0_err": 0.38, "S8": 0.825, "S8_err": 0.007, "chi2": 2823.0, "k": 6, "color": "#2ecc71", "marker": "o"},
    "w₀wₐCDM": {"H0": 69.17, "H0_err": 0.32, "S8": 0.828, "S8_err": 0.014, "chi2": 2819.7, "k": 8, "color": "#7f8c8d", "marker": "D"},
    "Geometric EDE": {"H0": 70.62, "H0_err": 0.48, "S8": 0.798, "S8_err": 0.010, "chi2": 2812.9, "k": 8, "color": "#e74c3c", "marker": "s"},
}

# Reference values
SHOES_H0 = 73.04
SHOES_H0_ERR = 1.04
TRGB_H0 = 69.8
TRGB_H0_ERR = 1.7
DES_S8 = 0.776
DES_S8_ERR = 0.017

REF_CHI2 = MODELS["ΛCDM"]["chi2"]

# =============================================================================
# PLOT 1: FOREST PLOT (H0 and Δχ²)
# =============================================================================

def plot_forest():
    """Create the forest plot showing H0 and Δχ² for all models."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    
    models = list(MODELS.keys())
    y_pos = np.arange(len(models))
    
    # Left panel: H0
    for i, (name, data) in enumerate(MODELS.items()):
        ax1.errorbar(data["H0"], i, xerr=data["H0_err"], 
                    fmt=data["marker"], color=data["color"], 
                    markersize=10, capsize=4, capthick=2, linewidth=2,
                    label=f'{name} (k={data["k"]})')
    
    # SH0ES band
    ax1.axvspan(SHOES_H0 - SHOES_H0_ERR, SHOES_H0 + SHOES_H0_ERR, 
                alpha=0.2, color='blue', label='SH0ES (1σ)')
    ax1.axvline(SHOES_H0, color='blue', linestyle='--', alpha=0.5)
    
    # TRGB band
    ax1.axvspan(TRGB_H0 - TRGB_H0_ERR, TRGB_H0 + TRGB_H0_ERR,
                alpha=0.15, color='purple', label='TRGB (1σ)')
    
    ax1.set_xlabel(r'$H_0$ [km s$^{-1}$ Mpc$^{-1}$]')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(models)
    ax1.set_xlim(66, 76)
    ax1.legend(loc='upper right', fontsize=8)
    ax1.set_title('Hubble Constant Constraints')
    ax1.grid(axis='x', alpha=0.3)
    
    # Right panel: Δχ²
    for i, (name, data) in enumerate(MODELS.items()):
        delta_chi2 = data["chi2"] - REF_CHI2
        ax2.barh(i, delta_chi2, color=data["color"], alpha=0.7, height=0.5)
        ax2.plot(delta_chi2, i, data["marker"], color=data["color"], markersize=10)
        
        # Add value label
        offset = 1 if delta_chi2 < 0 else -1
        ax2.text(delta_chi2 + offset, i, f'{delta_chi2:+.1f}', 
                va='center', ha='left' if delta_chi2 < 0 else 'right', fontsize=10)
    
    ax2.axvline(0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel(r'$\Delta\chi^2$ (vs ΛCDM)')
    ax2.set_xlim(-15, 5)
    ax2.set_title('Goodness of Fit')
    ax2.grid(axis='x', alpha=0.3)
    
    # Add annotation
    fig.text(0.5, -0.08, 
             'Geometric EDE achieves higher H₀ AND better χ² — a "triple win"',
             ha='center', fontsize=11, style='italic')
    
    plt.tight_layout()
    plt.savefig('paper_forest_plot.png', dpi=300, bbox_inches='tight')
    plt.savefig('paper_forest_plot.pdf', bbox_inches='tight')
    print("✓ Forest plot saved: paper_forest_plot.{png,pdf}")
    plt.close()

# =============================================================================
# PLOT 2: H0 vs Δχ² TRADE-OFF PLOT
# =============================================================================

def plot_h0_chi2_tradeoff():
    """Create the H0 vs Δχ² trade-off plot."""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    for name, data in MODELS.items():
        delta_chi2 = data["chi2"] - REF_CHI2
        ax.errorbar(data["H0"], delta_chi2, xerr=data["H0_err"],
                   fmt=data["marker"], color=data["color"],
                   markersize=12, capsize=4, capthick=2, linewidth=2,
                   label=f'{name}: H₀={data["H0"]:.1f}, S₈={data["S8"]:.3f}')
    
    # SH0ES band
    ax.axvspan(SHOES_H0 - SHOES_H0_ERR, SHOES_H0 + SHOES_H0_ERR,
               alpha=0.15, color='blue', label='SH0ES (1σ)')
    
    # ΛCDM reference line
    ax.axhline(0, color='gray', linestyle='--', alpha=0.7, label='ΛCDM baseline')
    
    # Annotate the key result
    ax.annotate('Geometric EDE:\nHigher H₀ + Better χ²',
               xy=(70.62, -10.1), xytext=(72, -7),
               fontsize=10, ha='left',
               arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
    
    ax.annotate('CPL:\nBetter χ², but\ntensions unresolved',
               xy=(69.17, -3.3), xytext=(66.5, -6),
               fontsize=9, ha='right',
               arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
    
    ax.set_xlabel(r'$H_0$ [km s$^{-1}$ Mpc$^{-1}$]', fontsize=12)
    ax.set_ylabel(r'$\Delta\chi^2$ (vs ΛCDM)', fontsize=12)
    ax.set_xlim(66, 76)
    ax.set_ylim(-15, 5)
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_title('Trade-off: Hubble Tension Resolution vs Fit Quality', fontsize=13)
    
    plt.tight_layout()
    plt.savefig('paper_h0_chi2_tradeoff.png', dpi=300, bbox_inches='tight')
    plt.savefig('paper_h0_chi2_tradeoff.pdf', bbox_inches='tight')
    print("✓ H0-χ² trade-off plot saved: paper_h0_chi2_tradeoff.{png,pdf}")
    plt.close()

# =============================================================================
# PLOT 3: H0 vs S8 PLANE
# =============================================================================

def plot_h0_s8_plane():
    """Create the H0 vs S8 plane showing tension resolution."""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    for name, data in MODELS.items():
        ax.errorbar(data["H0"], data["S8"], 
                   xerr=data["H0_err"], yerr=data["S8_err"],
                   fmt=data["marker"], color=data["color"],
                   markersize=12, capsize=4, capthick=2, linewidth=2,
                   label=f'{name}')
    
    # Target regions
    # SH0ES H0 band
    ax.axvspan(SHOES_H0 - SHOES_H0_ERR, SHOES_H0 + SHOES_H0_ERR,
               alpha=0.1, color='blue')
    ax.axvline(SHOES_H0, color='blue', linestyle='--', alpha=0.3, label='SH0ES H₀')
    
    # DES S8 band
    ax.axhspan(DES_S8 - DES_S8_ERR, DES_S8 + DES_S8_ERR,
               alpha=0.1, color='orange')
    ax.axhline(DES_S8, color='orange', linestyle='--', alpha=0.5, label='DES Y3 S₈')
    
    # Target region (where tensions are resolved)
    target_rect = plt.Rectangle((70, 0.76), 4, 0.04, 
                                  fill=True, alpha=0.1, color='green',
                                  label='Target region')
    ax.add_patch(target_rect)
    
    # Arrow showing the shift
    ax.annotate('', xy=(70.62, 0.798), xytext=(68.29, 0.825),
               arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.text(69.5, 0.815, 'EDE\nshift', fontsize=9, ha='center', color='red')
    
    ax.set_xlabel(r'$H_0$ [km s$^{-1}$ Mpc$^{-1}$]', fontsize=12)
    ax.set_ylabel(r'$S_8 = \sigma_8\sqrt{\Omega_m/0.3}$', fontsize=12)
    ax.set_xlim(66, 76)
    ax.set_ylim(0.74, 0.86)
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_title('Resolving Both Tensions Simultaneously', fontsize=13)
    
    plt.tight_layout()
    plt.savefig('paper_h0_s8_plane.png', dpi=300, bbox_inches='tight')
    plt.savefig('paper_h0_s8_plane.pdf', bbox_inches='tight')
    print("✓ H0-S8 plane plot saved: paper_h0_s8_plane.{png,pdf}")
    plt.close()

# =============================================================================
# PLOT 4: CROSS-WORLD COMPARISON
# =============================================================================

def plot_cross_world():
    """Show EDE performance across different H0 priors."""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    worlds = ["BASE\n(no H₀ prior)", "TRGB\n(H₀=69.8±1.7)", "SH0ES\n(H₀=73.04±1.04)"]
    ede_delta_chi2 = [-19.3, -15.7, -10.1]
    ede_h0 = [68.76, 70.03, 70.62]
    ede_s8 = [0.833, 0.810, 0.798]
    
    x = np.arange(len(worlds))
    width = 0.6
    
    bars = ax.bar(x, ede_delta_chi2, width, color='#e74c3c', alpha=0.8, 
                  label='Geometric EDE Δχ²')
    
    # Add value labels
    for i, (bar, h0, s8) in enumerate(zip(bars, ede_h0, ede_s8)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height - 1,
               f'Δχ² = {height:.1f}',
               ha='center', va='top', fontsize=11, fontweight='bold', color='white')
        ax.text(bar.get_x() + bar.get_width()/2., 1,
               f'H₀={h0:.1f}\nS₈={s8:.3f}',
               ha='center', va='bottom', fontsize=9)
    
    ax.axhline(0, color='black', linestyle='-', linewidth=1)
    ax.set_ylabel(r'$\Delta\chi^2$ (vs ΛCDM in same world)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(worlds, fontsize=11)
    ax.set_ylim(-25, 5)
    ax.set_title('Geometric EDE Beats ΛCDM in ALL Worlds', fontsize=14)
    ax.grid(axis='y', alpha=0.3)
    
    # Add interpretation
    ax.text(0.5, -0.15, 
           'EDE is preferred by CMB+BAO data alone (BASE world), independent of local H₀ priors',
           transform=ax.transAxes, ha='center', fontsize=10, style='italic')
    
    plt.tight_layout()
    plt.savefig('paper_cross_world.png', dpi=300, bbox_inches='tight')
    plt.savefig('paper_cross_world.pdf', bbox_inches='tight')
    print("✓ Cross-world comparison saved: paper_cross_world.{png,pdf}")
    plt.close()

# =============================================================================
# PLOT 5: AIC/BIC COMPARISON
# =============================================================================

def plot_aic_bic():
    """Create AIC/BIC comparison bar chart."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    models = ["ΛCDM\n(k=6)", "w₀wₐCDM\n(k=8)", "Geometric EDE\n(k=8)"]
    x = np.arange(len(models))
    width = 0.35
    
    # Compute AIC/BIC
    n_data = 2600
    ln_n = np.log(n_data)
    
    ref_chi2 = 2823.0
    ref_aic = ref_chi2 + 2 * 6
    ref_bic = ref_chi2 + 6 * ln_n
    
    delta_aic = [
        0.0,
        (2819.7 + 2*8) - ref_aic,
        (2812.9 + 2*8) - ref_aic
    ]
    delta_bic = [
        0.0,
        (2819.7 + 8*ln_n) - ref_bic,
        (2812.9 + 8*ln_n) - ref_bic
    ]
    
    bars1 = ax.bar(x - width/2, delta_aic, width, label='ΔAIC', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, delta_bic, width, label='ΔBIC', color='#e67e22', alpha=0.8)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height >= 0 else -1.5),
                   f'{height:+.1f}', ha='center', va='bottom' if height >= 0 else 'top', fontsize=9)
    
    ax.axhline(0, color='black', linestyle='-', linewidth=1)
    ax.axhspan(-6, 6, alpha=0.1, color='gray', label='|ΔBIC|<6: "Positive" evidence')
    
    ax.set_ylabel('Δ (relative to ΛCDM)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=10)
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(-10, 20)
    ax.set_title('Information Criteria: AIC Prefers EDE, BIC Neutral', fontsize=13)
    
    # Interpretation box
    textstr = 'ΔAIC = −6.1 → AIC prefers EDE\nΔBIC = +5.6 → "Positive" evidence (not strong)'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=9,
           verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    plt.savefig('paper_aic_bic.png', dpi=300, bbox_inches='tight')
    plt.savefig('paper_aic_bic.pdf', bbox_inches='tight')
    print("✓ AIC/BIC comparison saved: paper_aic_bic.{png,pdf}")
    plt.close()

# =============================================================================
# PLOT 6: TENSION SIGMA REDUCTION
# =============================================================================

def plot_tension_reduction():
    """Show tension reduction in sigma for each model."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    
    models = ["ΛCDM", "w₀wₐCDM", "Geometric EDE"]
    colors = ["#2ecc71", "#7f8c8d", "#e74c3c"]
    
    # H0 tension (vs SH0ES)
    h0_values = [68.29, 69.17, 70.62]
    h0_errs = [0.38, 0.32, 0.48]
    h0_tensions = []
    for h0, err in zip(h0_values, h0_errs):
        combined_err = np.sqrt(err**2 + SHOES_H0_ERR**2)
        tension = abs(SHOES_H0 - h0) / combined_err
        h0_tensions.append(tension)
    
    bars1 = ax1.bar(models, h0_tensions, color=colors, alpha=0.8)
    ax1.axhline(5, color='red', linestyle='--', alpha=0.7, label='5σ threshold')
    ax1.axhline(2, color='orange', linestyle='--', alpha=0.7, label='2σ threshold')
    ax1.set_ylabel('Tension (σ)', fontsize=12)
    ax1.set_title('H₀ Tension vs SH0ES', fontsize=13)
    ax1.legend()
    ax1.set_ylim(0, 6)
    
    for bar, tension in zip(bars1, h0_tensions):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                f'{tension:.1f}σ', ha='center', fontsize=11, fontweight='bold')
    
    # S8 tension (vs DES)
    s8_values = [0.825, 0.828, 0.798]
    s8_errs = [0.007, 0.014, 0.010]
    s8_tensions = []
    for s8, err in zip(s8_values, s8_errs):
        combined_err = np.sqrt(err**2 + DES_S8_ERR**2)
        tension = abs(DES_S8 - s8) / combined_err
        s8_tensions.append(tension)
    
    bars2 = ax2.bar(models, s8_tensions, color=colors, alpha=0.8)
    ax2.axhline(2, color='orange', linestyle='--', alpha=0.7, label='2σ threshold')
    ax2.set_ylabel('Tension (σ)', fontsize=12)
    ax2.set_title('S₈ Tension vs DES Y3', fontsize=13)
    ax2.legend()
    ax2.set_ylim(0, 4)
    
    for bar, tension in zip(bars2, s8_tensions):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                f'{tension:.1f}σ', ha='center', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('paper_tension_reduction.png', dpi=300, bbox_inches='tight')
    plt.savefig('paper_tension_reduction.pdf', bbox_inches='tight')
    print("✓ Tension reduction plot saved: paper_tension_reduction.{png,pdf}")
    plt.close()

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("GENERATING ALL PUBLICATION PLOTS")
    print("=" * 70)
    print()
    
    plot_forest()
    plot_h0_chi2_tradeoff()
    plot_h0_s8_plane()
    plot_cross_world()
    plot_aic_bic()
    plot_tension_reduction()
    
    print()
    print("=" * 70)
    print("ALL PLOTS GENERATED SUCCESSFULLY")
    print("=" * 70)
    print()
    print("Generated files:")
    print("  - paper_forest_plot.{png,pdf}")
    print("  - paper_h0_chi2_tradeoff.{png,pdf}")
    print("  - paper_h0_s8_plane.{png,pdf}")
    print("  - paper_cross_world.{png,pdf}")
    print("  - paper_aic_bic.{png,pdf}")
    print("  - paper_tension_reduction.{png,pdf}")

