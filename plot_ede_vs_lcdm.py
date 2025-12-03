#!/usr/bin/env python3
"""
Plot EDE vs. ΛCDM comparison:
1. H(z) evolution
2. Fractional energy densities (rho_i / rho_tot)
3. C_l spectrum comparison
"""

import numpy as np
import matplotlib.pyplot as plt
import sys

def plot_expansion_history(lcdm_bg, ede_bg, output_prefix):
    """Plot H(z) comparison."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Load data
    lcdm = np.loadtxt(lcdm_bg)
    ede = np.loadtxt(ede_bg)
    
    # Column 0: z, Column 3: H [1/Mpc]
    z_lcdm = lcdm[:, 0]
    H_lcdm = lcdm[:, 3] * 299792.458  # Convert to km/s/Mpc
    
    z_ede = ede[:, 0]
    H_ede = ede[:, 3] * 299792.458
    
    # Top panel: H(z)
    ax1.loglog(z_lcdm, H_lcdm, 'k-', label='ΛCDM', linewidth=2)
    ax1.loglog(z_ede, H_ede, 'r-', label='EDE (θ=0.75)', linewidth=2, alpha=0.8)
    ax1.set_ylabel('H(z) [km/s/Mpc]', fontsize=12)
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Expansion History: EDE vs. ΛCDM', fontsize=14, fontweight='bold')
    
    # Bottom panel: Fractional difference
    # Interpolate EDE onto ΛCDM redshift grid
    H_ede_interp = np.interp(z_lcdm, z_ede, H_ede)
    frac_diff = (H_ede_interp - H_lcdm) / H_lcdm * 100
    
    ax2.semilogx(z_lcdm, frac_diff, 'b-', linewidth=2)
    ax2.axhline(0, color='k', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Redshift z', fontsize=12)
    ax2.set_ylabel('ΔH/H [%]', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-10, 10)
    
    # Mark key epochs
    for z_mark, label in [(1100, 'recomb'), (3400, 'eq')]:
        ax2.axvline(z_mark, color='gray', linestyle=':', alpha=0.5)
        ax2.text(z_mark, ax2.get_ylim()[1]*0.9, label, 
                ha='center', fontsize=9, color='gray')
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}_expansion.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_prefix}_expansion.png")
    plt.close()

def plot_energy_densities(lcdm_bg, ede_bg, output_prefix):
    """Plot fractional energy densities."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
    
    # Load data
    lcdm = np.loadtxt(lcdm_bg)
    ede = np.loadtxt(ede_bg)
    
    z_lcdm = lcdm[:, 0]
    z_ede = ede[:, 0]
    
    # ΛCDM components (no Ridder field, so columns are different)
    # Column 8: rho_g, 9: rho_b, 10: rho_cdm, 11: rho_lambda, 13: rho_crit
    rho_g_lcdm = lcdm[:, 8]
    rho_b_lcdm = lcdm[:, 9]
    rho_cdm_lcdm = lcdm[:, 10]
    rho_lambda_lcdm = lcdm[:, 11]
    rho_crit_lcdm = lcdm[:, 13]
    
    # EDE components (has Ridder field)
    # Column 8: rho_g, 9: rho_b, 10: rho_cdm, 11: rho_lambda, 14: rho_ridder, 19: rho_tot
    rho_g_ede = ede[:, 8]
    rho_b_ede = ede[:, 9]
    rho_cdm_ede = ede[:, 10]
    rho_lambda_ede = ede[:, 11]
    rho_ridder_ede = ede[:, 14]
    rho_tot_ede = ede[:, 19]
    
    # ΛCDM fractional densities
    Omega_g_lcdm = rho_g_lcdm / rho_crit_lcdm
    Omega_m_lcdm = (rho_b_lcdm + rho_cdm_lcdm) / rho_crit_lcdm
    Omega_lambda_lcdm = rho_lambda_lcdm / rho_crit_lcdm
    
    # EDE fractional densities
    Omega_g_ede = rho_g_ede / rho_tot_ede
    Omega_m_ede = (rho_b_ede + rho_cdm_ede) / rho_tot_ede
    Omega_lambda_ede = rho_lambda_ede / rho_tot_ede
    Omega_ridder_ede = rho_ridder_ede / rho_tot_ede
    
    # Top panel: ΛCDM
    ax1.loglog(z_lcdm, Omega_g_lcdm, 'orange', label='Radiation', linewidth=2)
    ax1.loglog(z_lcdm, Omega_m_lcdm, 'blue', label='Matter', linewidth=2)
    ax1.loglog(z_lcdm, Omega_lambda_lcdm, 'purple', label='Λ', linewidth=2)
    ax1.set_ylabel('Ω_i(z)', fontsize=12)
    ax1.legend(fontsize=11, loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Energy Fractions: ΛCDM', fontsize=13, fontweight='bold')
    ax1.set_ylim(1e-4, 2)
    
    # Bottom panel: EDE
    ax2.loglog(z_ede, Omega_g_ede, 'orange', label='Radiation', linewidth=2)
    ax2.loglog(z_ede, Omega_m_ede, 'blue', label='Matter', linewidth=2)
    ax2.loglog(z_ede, Omega_lambda_ede, 'purple', label='Λ', linewidth=2)
    ax2.loglog(z_ede, Omega_ridder_ede, 'red', label='Ridder (EDE)', linewidth=2.5)
    ax2.set_xlabel('Redshift z', fontsize=12)
    ax2.set_ylabel('Ω_i(z)', fontsize=12)
    ax2.legend(fontsize=11, loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.set_title('Energy Fractions: EDE', fontsize=13, fontweight='bold')
    ax2.set_ylim(1e-4, 2)
    
    # Mark key epochs on both
    for ax in [ax1, ax2]:
        for z_mark, label in [(1100, 'recomb'), (3400, 'eq'), (691, 'EDE peak')]:
            ax.axvline(z_mark, color='gray', linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}_densities.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_prefix}_densities.png")
    plt.close()

def plot_ridder_zoom(ede_bg, output_prefix):
    """Zoom in on Ridder field evolution."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    ede = np.loadtxt(ede_bg)
    
    z_ede = ede[:, 0]
    rho_ridder_ede = ede[:, 14]
    rho_tot_ede = ede[:, 19]
    Omega_ridder = rho_ridder_ede / rho_tot_ede
    
    # Top: absolute density
    ax1.loglog(z_ede, rho_ridder_ede, 'r-', linewidth=2)
    ax1.set_ylabel('ρ_Ridder [Mpc⁻²]', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Ridder Field Evolution', fontsize=14, fontweight='bold')
    
    # Bottom: fractional contribution
    ax2.loglog(z_ede, Omega_ridder, 'r-', linewidth=2)
    ax2.axhline(0.063, color='k', linestyle='--', alpha=0.5, 
                label=f'f_peak ~ 0.063 (from Phase 2)')
    ax2.axvline(691, color='gray', linestyle=':', alpha=0.7, 
                label='z_peak ~ 691')
    ax2.set_xlabel('Redshift z', fontsize=12)
    ax2.set_ylabel('Ω_Ridder(z)', fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(1e-10, 0.5)
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}_ridder_evolution.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_prefix}_ridder_evolution.png")
    plt.close()

def plot_cl_comparison(lcdm_cl, ede_cl, output_prefix):
    """Plot C_l comparison."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Load data
    lcdm = np.loadtxt(lcdm_cl)
    ede = np.loadtxt(ede_cl)
    
    ell_lcdm = lcdm[:, 0]
    TT_lcdm = lcdm[:, 1]
    
    ell_ede = ede[:, 0]
    TT_ede = ede[:, 1]
    
    # Top panel: C_l spectra
    ax1.plot(ell_lcdm, TT_lcdm * 1e10, 'k-', label='ΛCDM', linewidth=2)
    ax1.plot(ell_ede, TT_ede * 1e10, 'r-', label='EDE (θ=0.75)', linewidth=2, alpha=0.8)
    ax1.set_ylabel('ℓ(ℓ+1)C_ℓ^TT/(2π) [×10⁻¹⁰]', fontsize=12)
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_title('CMB Temperature Power Spectrum', fontsize=14, fontweight='bold')
    ax1.set_xlim(2, 2500)
    
    # Bottom panel: Fractional difference
    TT_ede_interp = np.interp(ell_lcdm, ell_ede, TT_ede)
    frac_diff = (TT_ede_interp - TT_lcdm) / TT_lcdm * 100
    
    ax2.plot(ell_lcdm, frac_diff, 'b-', linewidth=2)
    ax2.axhline(0, color='k', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Multipole ℓ', fontsize=12)
    ax2.set_ylabel('ΔC_ℓ/C_ℓ [%]', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(2, 2500)
    ax2.set_ylim(-10, 10)
    
    # Mark acoustic peaks
    for ell_peak in [220, 540, 810]:
        ax2.axvline(ell_peak, color='gray', linestyle=':', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}_cl_comparison.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_prefix}_cl_comparison.png")
    plt.close()

def main():
    lcdm_bg = 'output/benchmark_vanilla_lcdm_00_background.dat'
    lcdm_cl = 'output/benchmark_vanilla_lcdm_00_cl.dat'
    ede_bg = 'output/benchmark_ede_theta075_00_background.dat'
    ede_cl = 'output/benchmark_ede_theta075_00_cl.dat'
    output_prefix = 'plots/phase3_comparison'
    
    import os
    os.makedirs('plots', exist_ok=True)
    
    print("Creating Phase 3 comparison plots...")
    print("=" * 60)
    
    plot_expansion_history(lcdm_bg, ede_bg, output_prefix)
    plot_energy_densities(lcdm_bg, ede_bg, output_prefix)
    plot_ridder_zoom(ede_bg, output_prefix)
    plot_cl_comparison(lcdm_cl, ede_cl, output_prefix)
    
    print("=" * 60)
    print("All plots created successfully!")

if __name__ == "__main__":
    main()

