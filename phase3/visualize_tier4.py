#!/usr/bin/env python3
"""
Visualize Tier 4 MCMC Results
Tier 4: Planck + BAO + SNe (The Grand Slam Test)
"""

import numpy as np
import matplotlib.pyplot as plt
from getdist import MCSamples, plots
import sys

print("=" * 80)
print("TIER 4 VISUALIZATION: Planck + BAO + SNe")
print("=" * 80)
print()

# Chain file path
chain_file = "chains/ridder_tier4_test.1.txt"

try:
    # Read the chain file
    print(f"Loading chain file: {chain_file}")
    data = np.loadtxt(chain_file)
    print(f"✓ Loaded {len(data)} samples")
    print()
    
    # Column indices (from header)
    # weight, minuslogpost, logA, n_s, H0, omega_b, omega_cdm, tau_reio, 
    # theta_i_ridder, beta_ridder, A_s, chi2__BAO, chi2__CMB, chi2__SN, 
    # minuslogprior, minuslogprior__0, chi2, ...
    
    weight_col = 0
    logA_col = 2
    n_s_col = 3
    H0_col = 4
    omega_b_col = 5
    omega_cdm_col = 6
    tau_reio_col = 7
    theta_i_col = 8
    beta_col = 9
    chi2_col = 16
    chi2_CMB_col = 12
    chi2_BAO_col = 11
    chi2_SN_col = 13
    
    # Extract parameters
    weights = data[:, weight_col]
    logA = data[:, logA_col]
    n_s = data[:, n_s_col]
    H0 = data[:, H0_col]
    omega_b = data[:, omega_b_col]
    omega_cdm = data[:, omega_cdm_col]
    tau_reio = data[:, tau_reio_col]
    theta_i = data[:, theta_i_col]
    beta = data[:, beta_col]
    chi2_total = data[:, chi2_col]
    chi2_CMB = data[:, chi2_CMB_col]
    chi2_BAO = data[:, chi2_BAO_col]
    chi2_SN = data[:, chi2_SN_col]
    
    # Calculate A_s from logA
    A_s = 1e-10 * np.exp(logA)
    
    print("Parameter Statistics:")
    print("-" * 80)
    print(f"H0:       {H0.mean():.2f} ± {H0.std():.2f} km/s/Mpc  (range: {H0.min():.2f} - {H0.max():.2f})")
    print(f"theta_i:  {theta_i.mean():.3f} ± {theta_i.std():.3f}  (range: {theta_i.min():.3f} - {theta_i.max():.3f})")
    print(f"beta:     {beta.mean():.4f} ± {beta.std():.4f}  (range: {beta.min():.4f} - {beta.max():.4f})")
    print(f"omega_b:  {omega_b.mean():.5f} ± {omega_b.std():.5f}")
    print(f"omega_cdm:{omega_cdm.mean():.4f} ± {omega_cdm.std():.4f}")
    print(f"n_s:      {n_s.mean():.4f} ± {n_s.std():.4f}")
    print(f"tau_reio: {tau_reio.mean():.4f} ± {tau_reio.std():.4f}")
    print()
    print(f"chi2 (total): {chi2_total.mean():.1f} ± {chi2_total.std():.1f}  (best: {chi2_total.min():.1f})")
    print(f"chi2 (CMB):   {chi2_CMB.mean():.1f} ± {chi2_CMB.std():.1f}")
    print(f"chi2 (BAO):   {chi2_BAO.mean():.1f} ± {chi2_BAO.std():.1f}")
    print(f"chi2 (SNe):   {chi2_SN.mean():.1f} ± {chi2_SN.std():.1f}")
    print("-" * 80)
    print()
    
    # ========================================================================
    # FIGURE 1: Trace Plots
    # ========================================================================
    print("Creating trace plots...")
    
    fig, axes = plt.subplots(4, 2, figsize=(14, 12))
    fig.suptitle('Tier 4 MCMC Trace Plots (Planck + BAO + SNe)', fontsize=16, fontweight='bold')
    
    samples = np.arange(len(H0))
    
    # H0
    axes[0, 0].plot(samples, H0, 'b-', alpha=0.6, linewidth=0.5)
    axes[0, 0].axhline(73.04, color='r', linestyle='--', label='SH0ES (73.04)', linewidth=2)
    axes[0, 0].axhline(67.4, color='orange', linestyle='--', label='Planck (67.4)', linewidth=2)
    axes[0, 0].set_ylabel('H₀ [km/s/Mpc]', fontsize=12)
    axes[0, 0].legend(fontsize=9)
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_ylim(65, 76)
    
    # theta_i
    axes[0, 1].plot(samples, theta_i, 'g-', alpha=0.6, linewidth=0.5)
    axes[0, 1].axhline(2.0, color='purple', linestyle='--', label='Ridder Valley', linewidth=2)
    axes[0, 1].set_ylabel('θᵢ', fontsize=12)
    axes[0, 1].legend(fontsize=9)
    axes[0, 1].grid(True, alpha=0.3)
    
    # beta
    axes[1, 0].plot(samples, beta, 'r-', alpha=0.6, linewidth=0.5)
    axes[1, 0].axhline(0.0, color='k', linestyle='--', label='No coupling', linewidth=2)
    axes[1, 0].set_ylabel('β (coupling)', fontsize=12)
    axes[1, 0].legend(fontsize=9)
    axes[1, 0].grid(True, alpha=0.3)
    
    # omega_cdm
    axes[1, 1].plot(samples, omega_cdm, 'purple', alpha=0.6, linewidth=0.5)
    axes[1, 1].set_ylabel('Ωc h²', fontsize=12)
    axes[1, 1].grid(True, alpha=0.3)
    
    # n_s
    axes[2, 0].plot(samples, n_s, 'orange', alpha=0.6, linewidth=0.5)
    axes[2, 0].set_ylabel('nₛ', fontsize=12)
    axes[2, 0].grid(True, alpha=0.3)
    
    # tau_reio
    axes[2, 1].plot(samples, tau_reio, 'brown', alpha=0.6, linewidth=0.5)
    axes[2, 1].set_ylabel('τ', fontsize=12)
    axes[2, 1].grid(True, alpha=0.3)
    
    # chi2 total
    axes[3, 0].plot(samples, chi2_total, 'k-', alpha=0.6, linewidth=0.5)
    axes[3, 0].set_ylabel('χ² (total)', fontsize=12)
    axes[3, 0].set_xlabel('Sample Number', fontsize=12)
    axes[3, 0].grid(True, alpha=0.3)
    
    # chi2 components
    axes[3, 1].plot(samples, chi2_CMB, 'b-', alpha=0.5, linewidth=0.5, label='CMB')
    axes[3, 1].plot(samples, chi2_BAO, 'g-', alpha=0.5, linewidth=0.5, label='BAO')
    axes[3, 1].plot(samples, chi2_SN/100, 'r-', alpha=0.5, linewidth=0.5, label='SNe/100')
    axes[3, 1].set_ylabel('χ² (components)', fontsize=12)
    axes[3, 1].set_xlabel('Sample Number', fontsize=12)
    axes[3, 1].legend(fontsize=9)
    axes[3, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('tier4_traces.png', dpi=150, bbox_inches='tight')
    print("✓ Saved tier4_traces.png")
    
    # ========================================================================
    # FIGURE 2: Corner Plot using GetDist
    # ========================================================================
    print("Creating corner plot...")
    
    # Prepare data for GetDist
    # GetDist expects: samples array, weights, names, labels
    samples_array = np.column_stack([H0, omega_b, omega_cdm, n_s, tau_reio, theta_i, beta])
    
    names = ['H0', 'omega_b', 'omega_cdm', 'n_s', 'tau_reio', 'theta_i', 'beta']
    labels = ['H_0', r'\Omega_b h^2', r'\Omega_c h^2', 'n_s', r'\tau', r'\theta_i', r'\beta']
    
    # Create MCSamples object
    mc_samples = MCSamples(
        samples=samples_array,
        weights=weights,
        names=names,
        labels=labels,
        label='Tier 4: Planck+BAO+SNe'
    )
    
    # Create corner plot
    g = plots.get_subplot_plotter()
    g.settings.num_plot_contours = 2
    g.settings.axes_fontsize = 11
    g.settings.lab_fontsize = 13
    g.settings.legend_fontsize = 11
    
    g.triangle_plot(
        [mc_samples],
        filled=True,
        title_limit=1,
        contour_colors=['darkblue'],
        line_args={'lw': 2, 'color': 'darkblue'}
    )
    
    plt.savefig('tier4_corner.png', dpi=150, bbox_inches='tight')
    print("✓ Saved tier4_corner.png")
    
    # ========================================================================
    # FIGURE 3: H0 vs theta_i vs beta (3D view)
    # ========================================================================
    print("Creating parameter correlation plots...")
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Tier 4 Parameter Correlations', fontsize=16, fontweight='bold')
    
    # H0 vs theta_i
    scatter = axes[0, 0].scatter(theta_i, H0, c=beta, cmap='viridis', alpha=0.6, s=10)
    axes[0, 0].axhline(73.04, color='r', linestyle='--', alpha=0.5, label='SH0ES')
    axes[0, 0].axhline(67.4, color='orange', linestyle='--', alpha=0.5, label='Planck')
    axes[0, 0].set_xlabel('θᵢ', fontsize=12)
    axes[0, 0].set_ylabel('H₀ [km/s/Mpc]', fontsize=12)
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=axes[0, 0])
    cbar.set_label('β', fontsize=10)
    
    # H0 vs beta
    scatter = axes[0, 1].scatter(beta, H0, c=theta_i, cmap='plasma', alpha=0.6, s=10)
    axes[0, 1].axhline(73.04, color='r', linestyle='--', alpha=0.5, label='SH0ES')
    axes[0, 1].axhline(67.4, color='orange', linestyle='--', alpha=0.5, label='Planck')
    axes[0, 1].set_xlabel('β (coupling)', fontsize=12)
    axes[0, 1].set_ylabel('H₀ [km/s/Mpc]', fontsize=12)
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=axes[0, 1])
    cbar.set_label('θᵢ', fontsize=10)
    
    # theta_i vs beta
    scatter = axes[1, 0].scatter(theta_i, beta, c=chi2_total, cmap='coolwarm', alpha=0.6, s=10)
    axes[1, 0].set_xlabel('θᵢ', fontsize=12)
    axes[1, 0].set_ylabel('β (coupling)', fontsize=12)
    axes[1, 0].grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=axes[1, 0])
    cbar.set_label('χ²', fontsize=10)
    
    # chi2 vs H0
    axes[1, 1].scatter(H0, chi2_total, c='blue', alpha=0.4, s=10)
    axes[1, 1].axvline(73.04, color='r', linestyle='--', alpha=0.5, label='SH0ES')
    axes[1, 1].axvline(67.4, color='orange', linestyle='--', alpha=0.5, label='Planck')
    axes[1, 1].set_xlabel('H₀ [km/s/Mpc]', fontsize=12)
    axes[1, 1].set_ylabel('χ² (total)', fontsize=12)
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('tier4_correlations.png', dpi=150, bbox_inches='tight')
    print("✓ Saved tier4_correlations.png")
    
    # ========================================================================
    # FIGURE 4: 1D Marginalized Distributions
    # ========================================================================
    print("Creating 1D distributions...")
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle('Tier 4 Marginalized Parameter Distributions', fontsize=16, fontweight='bold')
    
    # H0
    axes[0, 0].hist(H0, bins=50, weights=weights, color='blue', alpha=0.7, edgecolor='black')
    axes[0, 0].axvline(H0.mean(), color='darkblue', linestyle='-', linewidth=2, label=f'Mean: {H0.mean():.2f}')
    axes[0, 0].axvline(73.04, color='r', linestyle='--', linewidth=2, label='SH0ES: 73.04')
    axes[0, 0].axvline(67.4, color='orange', linestyle='--', linewidth=2, label='Planck: 67.4')
    axes[0, 0].set_xlabel('H₀ [km/s/Mpc]', fontsize=12)
    axes[0, 0].set_ylabel('Samples', fontsize=12)
    axes[0, 0].legend(fontsize=9)
    axes[0, 0].grid(True, alpha=0.3)
    
    # theta_i
    axes[0, 1].hist(theta_i, bins=50, weights=weights, color='green', alpha=0.7, edgecolor='black')
    axes[0, 1].axvline(theta_i.mean(), color='darkgreen', linestyle='-', linewidth=2, label=f'Mean: {theta_i.mean():.3f}')
    axes[0, 1].axvline(2.0, color='purple', linestyle='--', linewidth=2, label='Ridder Valley: 2.0')
    axes[0, 1].set_xlabel('θᵢ', fontsize=12)
    axes[0, 1].set_ylabel('Samples', fontsize=12)
    axes[0, 1].legend(fontsize=9)
    axes[0, 1].grid(True, alpha=0.3)
    
    # beta
    axes[0, 2].hist(beta, bins=50, weights=weights, color='red', alpha=0.7, edgecolor='black')
    axes[0, 2].axvline(beta.mean(), color='darkred', linestyle='-', linewidth=2, label=f'Mean: {beta.mean():.4f}')
    axes[0, 2].axvline(0.0, color='black', linestyle='--', linewidth=2, label='No coupling: 0')
    axes[0, 2].set_xlabel('β (coupling)', fontsize=12)
    axes[0, 2].set_ylabel('Samples', fontsize=12)
    axes[0, 2].legend(fontsize=9)
    axes[0, 2].grid(True, alpha=0.3)
    
    # omega_cdm
    axes[1, 0].hist(omega_cdm, bins=50, weights=weights, color='purple', alpha=0.7, edgecolor='black')
    axes[1, 0].axvline(omega_cdm.mean(), color='indigo', linestyle='-', linewidth=2, label=f'Mean: {omega_cdm.mean():.4f}')
    axes[1, 0].set_xlabel('Ωc h²', fontsize=12)
    axes[1, 0].set_ylabel('Samples', fontsize=12)
    axes[1, 0].legend(fontsize=9)
    axes[1, 0].grid(True, alpha=0.3)
    
    # n_s
    axes[1, 1].hist(n_s, bins=50, weights=weights, color='orange', alpha=0.7, edgecolor='black')
    axes[1, 1].axvline(n_s.mean(), color='darkorange', linestyle='-', linewidth=2, label=f'Mean: {n_s.mean():.4f}')
    axes[1, 1].set_xlabel('nₛ', fontsize=12)
    axes[1, 1].set_ylabel('Samples', fontsize=12)
    axes[1, 1].legend(fontsize=9)
    axes[1, 1].grid(True, alpha=0.3)
    
    # chi2
    axes[1, 2].hist(chi2_total, bins=50, weights=weights, color='gray', alpha=0.7, edgecolor='black')
    axes[1, 2].axvline(chi2_total.mean(), color='black', linestyle='-', linewidth=2, label=f'Mean: {chi2_total.mean():.1f}')
    axes[1, 2].axvline(chi2_total.min(), color='green', linestyle='--', linewidth=2, label=f'Best: {chi2_total.min():.1f}')
    axes[1, 2].set_xlabel('χ² (total)', fontsize=12)
    axes[1, 2].set_ylabel('Samples', fontsize=12)
    axes[1, 2].legend(fontsize=9)
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('tier4_distributions.png', dpi=150, bbox_inches='tight')
    print("✓ Saved tier4_distributions.png")
    
    print()
    print("=" * 80)
    print("VISUALIZATION COMPLETE!")
    print("=" * 80)
    print()
    print("Generated files:")
    print("  - tier4_traces.png        : MCMC trace plots")
    print("  - tier4_corner.png        : Corner plot (all parameters)")
    print("  - tier4_correlations.png  : Parameter correlation plots")
    print("  - tier4_distributions.png : 1D marginalized distributions")
    print()
    
except FileNotFoundError:
    print(f"ERROR: Chain file not found: {chain_file}")
    print("Make sure you're running this from the phase3 directory.")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

