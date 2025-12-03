#!/usr/bin/env python3
"""
Visualize Tier 3 MCMC Results (Planck + SH0ES H0 Prior)
========================================================
Creates trace plots, corner plots, and parameter summaries for Tier 3 chains.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

def load_chain(chain_file):
    """Load a Cobaya chain file."""
    try:
        data = np.loadtxt(chain_file)
        print(f"Loaded {chain_file}: {data.shape[0]} samples")
        return data
    except Exception as e:
        print(f"Error loading {chain_file}: {e}")
        return None

def plot_traces(chains, param_indices, param_names, output_file="tier3_traces.png"):
    """Plot trace plots for key parameters."""
    n_params = len(param_indices)
    n_chains = len(chains)
    
    fig, axes = plt.subplots(n_params, 1, figsize=(12, 3*n_params))
    if n_params == 1:
        axes = [axes]
    
    colors = ['blue', 'red', 'green', 'orange']
    
    for i, (param_idx, param_name) in enumerate(zip(param_indices, param_names)):
        ax = axes[i]
        for chain_idx, chain in enumerate(chains):
            if chain is not None:
                samples = chain[:, param_idx]
                ax.plot(samples, alpha=0.7, color=colors[chain_idx % len(colors)], 
                       label=f'Chain {chain_idx+1}')
        
        ax.set_ylabel(param_name, fontsize=12)
        ax.set_xlabel('Sample', fontsize=10)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved trace plot to {output_file}")
    plt.close()

def plot_corner(chains, param_indices, param_names, output_file="tier3_corner.png"):
    """Plot corner plot (2D parameter space)."""
    all_samples = []
    for chain in chains:
        if chain is not None:
            all_samples.append(chain[:, param_indices])
    
    if not all_samples:
        print("No valid chains to plot")
        return
    
    combined = np.vstack(all_samples)
    n_params = len(param_indices)
    
    fig, axes = plt.subplots(n_params, n_params, figsize=(12, 12))
    
    for i in range(n_params):
        for j in range(n_params):
            ax = axes[i, j]
            
            if i == j:
                # Diagonal: 1D histogram
                ax.hist(combined[:, i], bins=30, alpha=0.7, color='steelblue', edgecolor='black')
                ax.set_ylabel('Count', fontsize=8)
                if i == n_params - 1:
                    ax.set_xlabel(param_names[i], fontsize=10)
            elif i > j:
                # Lower triangle: 2D scatter
                ax.scatter(combined[:, j], combined[:, i], alpha=0.3, s=1, color='steelblue')
                if j == 0:
                    ax.set_ylabel(param_names[i], fontsize=10)
                if i == n_params - 1:
                    ax.set_xlabel(param_names[j], fontsize=10)
            else:
                # Upper triangle: hide
                ax.axis('off')
            
            ax.tick_params(labelsize=8)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved corner plot to {output_file}")
    plt.close()

def print_summary(chains, param_indices, param_names, tier_name="TIER 3"):
    """Print parameter summary statistics."""
    print("\n" + "="*70)
    print(f"{tier_name} PARAMETER SUMMARY")
    print("="*70)
    
    all_samples = []
    for chain in chains:
        if chain is not None:
            all_samples.append(chain[:, param_indices])
    
    if not all_samples:
        print("No valid chains")
        return
    
    combined = np.vstack(all_samples)
    
    for i, param_name in enumerate(param_names):
        samples = combined[:, i]
        mean = np.mean(samples)
        std = np.std(samples)
        median = np.median(samples)
        q16, q84 = np.percentile(samples, [16, 84])
        
        print(f"{param_name:20s}: {mean:8.4f} ± {std:8.4f}")
        print(f"{'':20s}  Median: {median:8.4f}  [{q16:8.4f}, {q84:8.4f}]")
    
    # Chi2 summary
    chi2_idx = -1
    all_chi2 = []
    for chain in chains:
        if chain is not None:
            all_chi2.append(chain[:, chi2_idx])
    
    if all_chi2:
        combined_chi2 = np.concatenate(all_chi2)
        best_chi2 = np.min(combined_chi2)
        mean_chi2 = np.mean(combined_chi2)
        print(f"\n{'Chi2 (best)':20s}: {best_chi2:8.2f}")
        print(f"{'Chi2 (mean)':20s}: {mean_chi2:8.2f}")
    
    print("="*70 + "\n")

def main():
    """Main visualization routine."""
    chain_dir = "/home/<VM_USER>/Ridder-Field/phase3"
    chain_files = [
        f"{chain_dir}/tier3_chain1_work/chains/ridder_tier3_planck_bao_sh0es.1.txt",
        f"{chain_dir}/tier3_chain2_work/chains/ridder_tier3_planck_bao_sh0es.1.txt",
        f"{chain_dir}/tier3_chain3_work/chains/ridder_tier3_planck_bao_sh0es.1.txt",
        f"{chain_dir}/tier3_chain4_work/chains/ridder_tier3_planck_bao_sh0es.1.txt",
    ]
    
    if len(sys.argv) > 1:
        chain_files = sys.argv[1:]
    
    # Load chains
    chains = []
    for cf in chain_files:
        chain = load_chain(cf)
        chains.append(chain)
    
    # Parameter indices (0-indexed)
    param_indices = [4, 6, 8, 9]  # H0, omega_cdm, theta_i_ridder, beta_ridder
    param_names = ['H0', 'omega_cdm', 'theta_i_ridder', 'beta_ridder']
    
    # Generate plots
    output_dir = os.path.dirname(chain_files[0]) if os.path.exists(os.path.dirname(chain_files[0])) else "."
    
    plot_traces(chains, param_indices, param_names, 
                output_file=f"{output_dir}/tier3_traces.png")
    
    plot_corner(chains, param_indices, param_names,
                output_file=f"{output_dir}/tier3_corner.png")
    
    # Print summary
    print_summary(chains, param_indices, param_names, tier_name="TIER 3 (Planck + SH0ES)")
    
    print(f"\nPlots saved to {output_dir}/")
    print("  - tier3_traces.png")
    print("  - tier3_corner.png")

if __name__ == "__main__":
    main()

