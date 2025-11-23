#!/usr/bin/env python3
"""
Simple plotting script for Tier 3 and Tier 4 MCMC results.
Reads chain files directly and creates basic diagnostic plots.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

# Set plot style
plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def load_chain_simple(filename, burn_in_frac=0.3):
    """Load chain file and return data array."""
    data = np.loadtxt(filename)
    # Remove burn-in
    n_burn = int(len(data) * burn_in_frac)
    return data[n_burn:]

def get_column_names(filename):
    """Extract column names from header."""
    with open(filename, 'r') as f:
        header = f.readline()
    return header.strip('#').split()

def plot_traces(chains, param_indices, param_names, title, output_file):
    """Create trace plots for convergence checking."""
    fig, axes = plt.subplots(len(param_indices), 1, figsize=(12, 3*len(param_indices)))
    if len(param_indices) == 1:
        axes = [axes]
    
    for i, (idx, name) in enumerate(zip(param_indices, param_names)):
        for j, chain in enumerate(chains):
            axes[i].plot(chain[:, idx], alpha=0.7, label=f'Chain {j+1}')
        axes[i].set_ylabel(name)
        axes[i].legend(loc='upper right')
        if i == 0:
            axes[i].set_title(title)
        if i == len(param_indices) - 1:
            axes[i].set_xlabel('Sample')
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    print(f"  Saved: {output_file}")

def plot_distributions(chains, param_indices, param_names, labels, output_file):
    """Create 1D distribution plots."""
    n_params = len(param_indices)
    fig, axes = plt.subplots(1, n_params, figsize=(5*n_params, 4))
    if n_params == 1:
        axes = [axes]
    
    for i, (idx, name) in enumerate(zip(param_indices, param_names)):
        all_data = []
        for j, chain in enumerate(chains):
            data = chain[:, idx]
            all_data.extend(data)
            axes[i].hist(data, bins=30, alpha=0.3, label=f'Chain {j+1}', density=True)
        
        # Plot combined distribution
        all_data = np.array(all_data)
        mean = np.mean(all_data)
        std = np.std(all_data)
        median = np.median(all_data)
        
        axes[i].axvline(mean, color='r', linestyle='--', label=f'Mean: {mean:.3f}')
        axes[i].axvline(median, color='g', linestyle=':', label=f'Median: {median:.3f}')
        
        axes[i].set_xlabel(name)
        axes[i].set_ylabel('Density')
        axes[i].legend()
        axes[i].set_title(f'{name}\n{mean:.4f} ± {std:.4f}')
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    print(f"  Saved: {output_file}")

def plot_2d_contours(chains, param_pairs, param_names, title, output_file):
    """Create 2D contour plots."""
    n_pairs = len(param_pairs)
    fig, axes = plt.subplots(1, n_pairs, figsize=(6*n_pairs, 5))
    if n_pairs == 1:
        axes = [axes]
    
    for i, (idx1, idx2) in enumerate(param_pairs):
        for j, chain in enumerate(chains):
            x = chain[:, idx1]
            y = chain[:, idx2]
            axes[i].scatter(x, y, alpha=0.3, s=1, label=f'Chain {j+1}')
        
        axes[i].set_xlabel(param_names[i][0])
        axes[i].set_ylabel(param_names[i][1])
        axes[i].legend()
    
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    print(f"  Saved: {output_file}")

def print_statistics(chains, param_indices, param_names, title):
    """Print summary statistics."""
    print(f"\n=== {title} ===")
    for idx, name in zip(param_indices, param_names):
        all_data = []
        for chain in chains:
            all_data.extend(chain[:, idx])
        all_data = np.array(all_data)
        
        mean = np.mean(all_data)
        std = np.std(all_data)
        median = np.median(all_data)
        q16, q84 = np.percentile(all_data, [16, 84])
        
        print(f"  {name:20s}: {mean:8.4f} ± {std:7.4f}  [{q16:8.4f}, {q84:8.4f}]")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(base_dir, 'results')
    plots_dir = os.path.join(results_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    print("="*70)
    print("MCMC CHAIN ANALYSIS")
    print("="*70)
    
    # ===== TIER 3 ANALYSIS =====
    print("\n### TIER 3: Planck + BAO + SH0ES ###")
    
    # Load Tier 3 Ridder chains
    tier3_ridder_files = [
        os.path.join(results_dir, 'tier3_chains', f'ridder_tier3_prod_chain{i}.1.txt')
        for i in range(1, 5)
    ]
    
    tier3_ridder_chains = []
    for f in tier3_ridder_files:
        if os.path.exists(f):
            chain = load_chain_simple(f, burn_in_frac=0.3)
            tier3_ridder_chains.append(chain)
            print(f"  Loaded {os.path.basename(f)}: {len(chain)} samples (after burn-in)")
    
    # Get column names
    col_names = get_column_names(tier3_ridder_files[0])
    H0_idx = col_names.index('H0')
    theta_idx = col_names.index('theta_i_ridder')
    beta_idx = col_names.index('beta_ridder')
    omega_b_idx = col_names.index('omega_b')
    omega_cdm_idx = col_names.index('omega_cdm')
    n_s_idx = col_names.index('n_s')
    chi2_idx = col_names.index('chi2')
    
    # Tier 3 Ridder plots
    if tier3_ridder_chains:
        plot_traces(
            tier3_ridder_chains,
            [H0_idx, theta_idx, beta_idx],
            ['H₀ [km/s/Mpc]', 'θᵢ', 'β'],
            'Tier 3 Ridder Field: Convergence',
            os.path.join(plots_dir, 'tier3_ridder_traces.png')
        )
        
        plot_distributions(
            tier3_ridder_chains,
            [H0_idx, theta_idx, beta_idx, chi2_idx],
            ['H₀ [km/s/Mpc]', 'θᵢ', 'β', 'χ²'],
            ['Ridder'],
            os.path.join(plots_dir, 'tier3_ridder_distributions.png')
        )
        
        plot_2d_contours(
            tier3_ridder_chains,
            [(H0_idx, theta_idx), (H0_idx, beta_idx), (theta_idx, beta_idx)],
            [('H₀', 'θᵢ'), ('H₀', 'β'), ('θᵢ', 'β')],
            'Tier 3 Ridder: Parameter Correlations',
            os.path.join(plots_dir, 'tier3_ridder_contours.png')
        )
        
        print_statistics(
            tier3_ridder_chains,
            [H0_idx, omega_b_idx, omega_cdm_idx, n_s_idx, theta_idx, beta_idx, chi2_idx],
            ['H0', 'omega_b', 'omega_cdm', 'n_s', 'theta_i', 'beta', 'chi2'],
            'Tier 3 Ridder Field Statistics'
        )
    
    # Load Tier 3 ΛCDM chains
    tier3_lcdm_files = [
        os.path.join(results_dir, 'tier3_chains', f'lcdm_tier3_prod_chain{i}.1.txt')
        for i in range(1, 3)
    ]
    
    tier3_lcdm_chains = []
    for f in tier3_lcdm_files:
        if os.path.exists(f):
            chain = load_chain_simple(f, burn_in_frac=0.3)
            tier3_lcdm_chains.append(chain)
            print(f"  Loaded {os.path.basename(f)}: {len(chain)} samples (after burn-in)")
    
    if tier3_lcdm_chains:
        plot_traces(
            tier3_lcdm_chains,
            [H0_idx, omega_b_idx, omega_cdm_idx],
            ['H₀ [km/s/Mpc]', 'Ωb', 'Ωcdm'],
            'Tier 3 ΛCDM: Convergence',
            os.path.join(plots_dir, 'tier3_lcdm_traces.png')
        )
        
        plot_distributions(
            tier3_lcdm_chains,
            [H0_idx, omega_b_idx, omega_cdm_idx, chi2_idx],
            ['H₀ [km/s/Mpc]', 'Ωb', 'Ωcdm', 'χ²'],
            ['ΛCDM'],
            os.path.join(plots_dir, 'tier3_lcdm_distributions.png')
        )
        
        print_statistics(
            tier3_lcdm_chains,
            [H0_idx, omega_b_idx, omega_cdm_idx, n_s_idx, chi2_idx],
            ['H0', 'omega_b', 'omega_cdm', 'n_s', 'chi2'],
            'Tier 3 ΛCDM Statistics'
        )
    
    # ===== TIER 4 ANALYSIS =====
    print("\n### TIER 4: Planck + BAO + SH0ES + SN ###")
    
    tier4_files = [
        os.path.join(results_dir, 'tier4_chains', f'ridder_tier4_prod_chain{i}.1.txt')
        for i in range(1, 5)
    ]
    
    tier4_chains = []
    for f in tier4_files:
        if os.path.exists(f):
            chain = load_chain_simple(f, burn_in_frac=0.3)
            tier4_chains.append(chain)
            print(f"  Loaded {os.path.basename(f)}: {len(chain)} samples (after burn-in)")
    
    if tier4_chains:
        plot_traces(
            tier4_chains,
            [H0_idx, theta_idx, beta_idx],
            ['H₀ [km/s/Mpc]', 'θᵢ', 'β'],
            'Tier 4 Ridder Field: Convergence',
            os.path.join(plots_dir, 'tier4_traces.png')
        )
        
        plot_distributions(
            tier4_chains,
            [H0_idx, theta_idx, beta_idx, chi2_idx],
            ['H₀ [km/s/Mpc]', 'θᵢ', 'β', 'χ²'],
            ['Tier 4'],
            os.path.join(plots_dir, 'tier4_distributions.png')
        )
        
        plot_2d_contours(
            tier4_chains,
            [(H0_idx, theta_idx), (H0_idx, beta_idx), (theta_idx, beta_idx)],
            [('H₀', 'θᵢ'), ('H₀', 'β'), ('θᵢ', 'β')],
            'Tier 4 Ridder: Parameter Correlations',
            os.path.join(plots_dir, 'tier4_contours.png')
        )
        
        print_statistics(
            tier4_chains,
            [H0_idx, omega_b_idx, omega_cdm_idx, n_s_idx, theta_idx, beta_idx, chi2_idx],
            ['H0', 'omega_b', 'omega_cdm', 'n_s', 'theta_i', 'beta', 'chi2'],
            'Tier 4 Ridder Field Statistics'
        )
    
    print("\n" + "="*70)
    print(f"✅ All plots saved to: {plots_dir}")
    print("="*70)

if __name__ == '__main__':
    main()

