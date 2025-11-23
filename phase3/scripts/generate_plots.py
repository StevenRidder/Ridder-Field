#!/usr/bin/env python3
"""
Generate publication-quality plots for Tier 3 and Tier 4 MCMC results.
Uses GetDist to create corner plots, trace plots, and 1D distributions.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from getdist import MCSamples, plots

# Set publication-quality plot style
plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.figsize': (10, 8),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def load_chain(chain_prefix, params=None, labels=None, burn_in=0.3):
    """
    Load MCMC chain using GetDist.
    
    Args:
        chain_prefix: Path prefix to chain files (without .1.txt)
        params: List of parameter names to extract
        labels: Dictionary mapping parameter names to LaTeX labels
        burn_in: Fraction of samples to discard as burn-in (default 0.3)
    
    Returns:
        MCSamples object
    """
    try:
        samples = MCSamples(chain_prefix, settings={'ignore_rows': burn_in})
        if params:
            samples = samples.getParams()
        return samples
    except Exception as e:
        print(f"Error loading chain {chain_prefix}: {e}")
        return None

def plot_tier3_comparison(ridder_chains, lcdm_chains, output_dir):
    """
    Generate comparison plots for Tier 3 (Ridder vs ΛCDM).
    """
    print("\n=== Generating Tier 3 Plots ===")
    
    # Parameters to plot
    params_ridder = ['H0', 'omega_b', 'omega_cdm', 'n_s', 'tau_reio', 'theta_i_ridder', 'beta_ridder']
    params_lcdm = ['H0', 'omega_b', 'omega_cdm', 'n_s', 'tau_reio']
    
    # Load Ridder chains
    ridder_samples_list = []
    for i, chain in enumerate(ridder_chains):
        samples = load_chain(chain, burn_in=0.3)
        if samples:
            ridder_samples_list.append(samples)
            print(f"  Loaded Ridder chain {i+1}: {samples.samples.shape[0]} samples")
    
    # Load ΛCDM chains
    lcdm_samples_list = []
    for i, chain in enumerate(lcdm_chains):
        samples = load_chain(chain, burn_in=0.3)
        if samples:
            lcdm_samples_list.append(samples)
            print(f"  Loaded ΛCDM chain {i+1}: {samples.samples.shape[0]} samples")
    
    if not ridder_samples_list and not lcdm_samples_list:
        print("  ERROR: No chains loaded successfully!")
        return
    
    # Combine chains
    if ridder_samples_list:
        ridder_combined = MCSamples.concatenate(ridder_samples_list)
        print(f"  Combined Ridder: {ridder_combined.samples.shape[0]} samples")
    else:
        ridder_combined = None
    
    if lcdm_samples_list:
        lcdm_combined = MCSamples.concatenate(lcdm_samples_list)
        print(f"  Combined ΛCDM: {lcdm_combined.samples.shape[0]} samples")
    else:
        lcdm_combined = None
    
    # 1. Triangle plot for Ridder field
    if ridder_combined:
        print("  Creating Ridder triangle plot...")
        g = plots.get_subplot_plotter()
        g.triangle_plot([ridder_combined], params_ridder, filled=True,
                       title_limit=1, legend_labels=['Ridder Field'])
        plt.savefig(os.path.join(output_dir, 'tier3_ridder_triangle.png'))
        plt.close()
    
    # 2. Comparison plot: H0, omega_cdm, n_s
    if ridder_combined and lcdm_combined:
        print("  Creating comparison plot...")
        g = plots.get_subplot_plotter()
        g.triangle_plot([ridder_combined, lcdm_combined], 
                       ['H0', 'omega_cdm', 'n_s'],
                       filled=True, legend_labels=['Ridder', 'ΛCDM'])
        plt.savefig(os.path.join(output_dir, 'tier3_comparison.png'))
        plt.close()
    
    # 3. 1D distributions for key parameters
    if ridder_combined:
        print("  Creating 1D distributions...")
        g = plots.get_single_plotter()
        g.plot_1d([ridder_combined], 'H0', title_limit=1)
        plt.savefig(os.path.join(output_dir, 'tier3_ridder_H0_dist.png'))
        plt.close()
        
        g.plot_1d([ridder_combined], 'theta_i_ridder', title_limit=1)
        plt.savefig(os.path.join(output_dir, 'tier3_ridder_theta_dist.png'))
        plt.close()
        
        g.plot_1d([ridder_combined], 'beta_ridder', title_limit=1)
        plt.savefig(os.path.join(output_dir, 'tier3_ridder_beta_dist.png'))
        plt.close()
    
    # 4. Trace plots to check convergence
    if ridder_samples_list:
        print("  Creating trace plots...")
        fig, axes = plt.subplots(3, 1, figsize=(12, 8))
        
        for i, samples in enumerate(ridder_samples_list):
            chain_data = samples.samples
            axes[0].plot(chain_data[:, samples.index['H0']], alpha=0.7, label=f'Chain {i+1}')
            axes[1].plot(chain_data[:, samples.index['theta_i_ridder']], alpha=0.7)
            axes[2].plot(chain_data[:, samples.index['beta_ridder']], alpha=0.7)
        
        axes[0].set_ylabel('H₀ [km/s/Mpc]')
        axes[1].set_ylabel('θᵢ')
        axes[2].set_ylabel('β')
        axes[2].set_xlabel('Sample')
        axes[0].legend()
        axes[0].set_title('Tier 3 Ridder Field: Trace Plots')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'tier3_ridder_traces.png'))
        plt.close()
    
    print("  Tier 3 plots complete!")

def plot_tier4(ridder_chains, output_dir):
    """
    Generate plots for Tier 4 (Ridder with full data).
    """
    print("\n=== Generating Tier 4 Plots ===")
    
    params = ['H0', 'omega_b', 'omega_cdm', 'n_s', 'tau_reio', 'theta_i_ridder', 'beta_ridder']
    
    # Load chains
    samples_list = []
    for i, chain in enumerate(ridder_chains):
        samples = load_chain(chain, burn_in=0.3)
        if samples:
            samples_list.append(samples)
            print(f"  Loaded Tier 4 chain {i+1}: {samples.samples.shape[0]} samples")
    
    if not samples_list:
        print("  ERROR: No Tier 4 chains loaded!")
        return
    
    # Combine chains
    combined = MCSamples.concatenate(samples_list)
    print(f"  Combined Tier 4: {combined.samples.shape[0]} samples")
    
    # 1. Triangle plot
    print("  Creating triangle plot...")
    g = plots.get_subplot_plotter()
    g.triangle_plot([combined], params, filled=True,
                   title_limit=1, legend_labels=['Ridder (Full Data)'])
    plt.savefig(os.path.join(output_dir, 'tier4_ridder_triangle.png'))
    plt.close()
    
    # 2. 1D distributions
    print("  Creating 1D distributions...")
    g = plots.get_single_plotter()
    g.plot_1d([combined], 'H0', title_limit=1)
    plt.savefig(os.path.join(output_dir, 'tier4_H0_dist.png'))
    plt.close()
    
    g.plot_1d([combined], 'theta_i_ridder', title_limit=1)
    plt.savefig(os.path.join(output_dir, 'tier4_theta_dist.png'))
    plt.close()
    
    g.plot_1d([combined], 'beta_ridder', title_limit=1)
    plt.savefig(os.path.join(output_dir, 'tier4_beta_dist.png'))
    plt.close()
    
    # 3. Trace plots
    print("  Creating trace plots...")
    fig, axes = plt.subplots(3, 1, figsize=(12, 8))
    
    for i, samples in enumerate(samples_list):
        chain_data = samples.samples
        axes[0].plot(chain_data[:, samples.index['H0']], alpha=0.7, label=f'Chain {i+1}')
        axes[1].plot(chain_data[:, samples.index['theta_i_ridder']], alpha=0.7)
        axes[2].plot(chain_data[:, samples.index['beta_ridder']], alpha=0.7)
    
    axes[0].set_ylabel('H₀ [km/s/Mpc]')
    axes[1].set_ylabel('θᵢ')
    axes[2].set_ylabel('β')
    axes[2].set_xlabel('Sample')
    axes[0].legend()
    axes[0].set_title('Tier 4 Ridder Field: Trace Plots')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'tier4_traces.png'))
    plt.close()
    
    print("  Tier 4 plots complete!")

def print_statistics(samples, name):
    """
    Print summary statistics for key parameters.
    """
    print(f"\n=== {name} Statistics ===")
    
    params_to_print = ['H0', 'omega_b', 'omega_cdm', 'n_s', 'tau_reio']
    if 'theta_i_ridder' in samples.paramNames.list():
        params_to_print.extend(['theta_i_ridder', 'beta_ridder'])
    
    for param in params_to_print:
        if param in samples.paramNames.list():
            mean = samples.mean(param)
            std = samples.std(param)
            limits = samples.confidence(param, 0.68)
            print(f"  {param:20s}: {mean:8.4f} ± {std:7.4f}  [{limits[0]:8.4f}, {limits[1]:8.4f}]")

def main():
    # Set up paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(base_dir, 'results')
    plots_dir = os.path.join(results_dir, 'plots')
    
    os.makedirs(plots_dir, exist_ok=True)
    
    # Tier 3 chains
    tier3_ridder = [
        os.path.join(results_dir, 'tier3_chains', f'ridder_tier3_prod_chain{i}')
        for i in range(1, 5)
    ]
    tier3_lcdm = [
        os.path.join(results_dir, 'tier3_chains', f'lcdm_tier3_prod_chain{i}')
        for i in range(1, 3)
    ]
    
    # Tier 4 chains
    tier4_ridder = [
        os.path.join(results_dir, 'tier4_chains', f'ridder_tier4_prod_chain{i}')
        for i in range(1, 5)
    ]
    
    # Generate plots
    plot_tier3_comparison(tier3_ridder, tier3_lcdm, plots_dir)
    plot_tier4(tier4_ridder, plots_dir)
    
    # Print statistics
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    
    # Load and print Tier 3 stats
    tier3_ridder_samples = []
    for chain in tier3_ridder:
        s = load_chain(chain, burn_in=0.3)
        if s:
            tier3_ridder_samples.append(s)
    
    if tier3_ridder_samples:
        tier3_ridder_combined = MCSamples.concatenate(tier3_ridder_samples)
        print_statistics(tier3_ridder_combined, "Tier 3 Ridder Field")
    
    tier3_lcdm_samples = []
    for chain in tier3_lcdm:
        s = load_chain(chain, burn_in=0.3)
        if s:
            tier3_lcdm_samples.append(s)
    
    if tier3_lcdm_samples:
        tier3_lcdm_combined = MCSamples.concatenate(tier3_lcdm_samples)
        print_statistics(tier3_lcdm_combined, "Tier 3 ΛCDM")
    
    # Load and print Tier 4 stats
    tier4_samples = []
    for chain in tier4_ridder:
        s = load_chain(chain, burn_in=0.3)
        if s:
            tier4_samples.append(s)
    
    if tier4_samples:
        tier4_combined = MCSamples.concatenate(tier4_samples)
        print_statistics(tier4_combined, "Tier 4 Ridder Field")
    
    print(f"\n✅ All plots saved to: {plots_dir}")
    print("="*70)

if __name__ == '__main__':
    main()

