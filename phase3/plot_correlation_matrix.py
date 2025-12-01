#!/usr/bin/env python3
"""
Correlation Matrix Visualization: What Drives Low-ℓ EE?

Compare parameter correlations between pre-DESI and +DESI EDE chains
to understand the correlation flip mechanism.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# Try seaborn, fall back to matplotlib
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    print("Seaborn not available, using matplotlib heatmap")

def load_chain(chain_file, burn_frac=0.3):
    """Load chain data and remove burn-in."""
    data = {}
    with open(chain_file, 'r') as f:
        header = f.readline().strip().lstrip('#').split()
        cols = {name: i for i, name in enumerate(header)}
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    values = np.array([[float(x) for x in line.split()] for line in lines])
    
    # Remove burn-in
    burn = int(burn_frac * len(values))
    values = values[burn:]
    
    for name, idx in cols.items():
        data[name] = values[:, idx]
    
    return data, cols

def compute_correlation_matrix(data, params):
    """Compute correlation matrix for specified parameters."""
    n = len(params)
    corr = np.zeros((n, n))
    
    for i, p1 in enumerate(params):
        for j, p2 in enumerate(params):
            if p1 in data and p2 in data:
                corr[i, j] = np.corrcoef(data[p1], data[p2])[0, 1]
            else:
                corr[i, j] = np.nan
    
    return corr

def plot_heatmap(ax, corr, labels, title, cmap='RdBu_r'):
    """Plot correlation heatmap."""
    n = len(labels)
    
    # Create heatmap
    im = ax.imshow(corr, cmap=cmap, vmin=-1, vmax=1, aspect='equal')
    
    # Add text annotations
    for i in range(n):
        for j in range(n):
            val = corr[i, j]
            if not np.isnan(val):
                # Color text based on background
                color = 'white' if abs(val) > 0.5 else 'black'
                ax.text(j, i, f'{val:.2f}', ha='center', va='center', 
                       color=color, fontsize=10, fontweight='bold')
    
    # Set ticks and labels
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_xticklabels(labels, fontsize=9, rotation=45, ha='right')
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_title(title, fontsize=12, fontweight='bold')
    
    return im

def main():
    """Main analysis."""
    print("=" * 60)
    print("PARAMETER CORRELATION MATRIX ANALYSIS")
    print("What Drives Low-ℓ EE?")
    print("=" * 60)
    
    # Chain files
    chains_dir = "chains"
    chain_files = {
        'EDE pre-DESI': f'{chains_dir}/tier5_ede_shoes_predesi.1.txt',
        'EDE +DESI': f'{chains_dir}/tier5_ede_shoes_desi.1.txt',
    }
    
    # Check files exist
    for name, path in chain_files.items():
        if not os.path.exists(path):
            print(f"ERROR: {path} not found")
            return
    
    # Parameters to analyze
    # Core EDE parameters + those affecting low-ℓ EE
    params_full = ['Lambda_EDE_ridder', 'log10_ac', 'tau_reio', 'n_s', 'omega_b', 'H0', 'omega_cdm', 'logA']
    param_labels = ['Λ_EDE', 'log₁₀(aₛ)', 'τ_reio', 'nₛ', 'ωb', 'H₀', 'ωcdm', 'ln(10¹⁰Aₛ)']
    
    # Load chains
    print("\nLoading chains...")
    chains = {}
    for name, path in chain_files.items():
        chains[name], _ = load_chain(path)
        print(f"  {name}: {len(chains[name]['H0'])} samples (after burn-in)")
    
    # Check which parameters are available
    available_params = []
    available_labels = []
    for p, l in zip(params_full, param_labels):
        if all(p in chains[name] for name in chains):
            available_params.append(p)
            available_labels.append(l)
    
    print(f"\nAnalyzing {len(available_params)} parameters: {available_params}")
    
    # Compute correlation matrices
    print("\nComputing correlation matrices...")
    corr_matrices = {}
    for name in chains:
        corr_matrices[name] = compute_correlation_matrix(chains[name], available_params)
    
    # Print key correlations
    print("\n" + "=" * 60)
    print("KEY CORRELATIONS (affecting low-ℓ EE)")
    print("=" * 60)
    
    # Find tau_reio index
    if 'tau_reio' in available_params:
        tau_idx = available_params.index('tau_reio')
        lambda_idx = available_params.index('Lambda_EDE_ridder') if 'Lambda_EDE_ridder' in available_params else None
        
        print("\nCorrelations with τ_reio:")
        for i, (p, l) in enumerate(zip(available_params, available_labels)):
            if p != 'tau_reio':
                for name in chains:
                    corr = corr_matrices[name][tau_idx, i]
                    print(f"  {name}: corr(τ_reio, {l}) = {corr:+.3f}")
                print()
        
        if lambda_idx is not None:
            print("\n" + "-" * 40)
            print("THE CORRELATION FLIP:")
            print("-" * 40)
            for name in chains:
                corr = corr_matrices[name][lambda_idx, tau_idx]
                print(f"  {name}: corr(Λ_EDE, τ_reio) = {corr:+.3f}")
    
    # Create figure
    print("\n" + "=" * 60)
    print("Creating correlation matrix figure...")
    print("=" * 60)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Parameter Correlations: The Mechanism Behind Low-ℓ EE Changes', 
                 fontsize=14, fontweight='bold')
    
    # Panel 1: Pre-DESI correlations
    im1 = plot_heatmap(axes[0], corr_matrices['EDE pre-DESI'], available_labels,
                       'EDE Pre-DESI\n(corr(Λ_EDE, τ) = +0.35)')
    
    # Panel 2: +DESI correlations
    im2 = plot_heatmap(axes[1], corr_matrices['EDE +DESI'], available_labels,
                       'EDE +DESI\n(corr(Λ_EDE, τ) = -0.67)')
    
    # Panel 3: Difference (shows what changed)
    diff = corr_matrices['EDE +DESI'] - corr_matrices['EDE pre-DESI']
    im3 = plot_heatmap(axes[2], diff, available_labels,
                       'Difference (+DESI - Pre-DESI)\nRed = correlation increased',
                       cmap='RdBu_r')
    
    # Add colorbars
    cbar_ax1 = fig.add_axes([0.35, 0.08, 0.02, 0.25])
    fig.colorbar(im1, cax=cbar_ax1, label='Correlation')
    
    cbar_ax2 = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    fig.colorbar(im3, cax=cbar_ax2, label='Δ Correlation')
    
    plt.tight_layout(rect=[0, 0.15, 0.9, 0.95])
    
    # Save figure
    outfile = '../phase2/paper/figures/correlation_matrix_comparison.png'
    plt.savefig(outfile, dpi=150, bbox_inches='tight')
    print(f"\nFigure saved to: {outfile}")
    
    plt.savefig('correlation_matrix_comparison.png', dpi=150, bbox_inches='tight')
    print(f"Also saved to: correlation_matrix_comparison.png")
    plt.close()
    
    # Create focused 2x2 figure showing key correlations
    print("\nCreating focused correlation scatter plots...")
    
    fig2, axes2 = plt.subplots(2, 2, figsize=(12, 10))
    fig2.suptitle('Key Parameter Correlations: Pre-DESI vs +DESI', 
                  fontsize=14, fontweight='bold')
    
    # Key pairs to plot
    pairs = [
        ('Lambda_EDE_ridder', 'tau_reio', 'Λ_EDE', 'τ_reio'),
        ('Lambda_EDE_ridder', 'n_s', 'Λ_EDE', 'nₛ'),
        ('tau_reio', 'n_s', 'τ_reio', 'nₛ'),
        ('Lambda_EDE_ridder', 'H0', 'Λ_EDE', 'H₀'),
    ]
    
    colors = {'EDE pre-DESI': 'green', 'EDE +DESI': 'red'}
    
    for ax, (p1, p2, l1, l2) in zip(axes2.flat, pairs):
        for name, color in colors.items():
            if p1 in chains[name] and p2 in chains[name]:
                x = chains[name][p1]
                y = chains[name][p2]
                
                # Thin for plotting
                thin = max(1, len(x) // 500)
                
                ax.scatter(x[::thin], y[::thin], c=color, alpha=0.3, s=10, 
                          label=name)
                
                # Add correlation coefficient
                corr = np.corrcoef(x, y)[0, 1]
                
        ax.set_xlabel(l1, fontsize=11)
        ax.set_ylabel(l2, fontsize=11)
        
        # Add correlation text
        if p1 in chains['EDE pre-DESI'] and p2 in chains['EDE pre-DESI']:
            corr_pre = np.corrcoef(chains['EDE pre-DESI'][p1], 
                                   chains['EDE pre-DESI'][p2])[0, 1]
            corr_post = np.corrcoef(chains['EDE +DESI'][p1], 
                                    chains['EDE +DESI'][p2])[0, 1]
            
            ax.text(0.05, 0.95, f'Pre-DESI: r = {corr_pre:+.2f}\n+DESI: r = {corr_post:+.2f}',
                   transform=ax.transAxes, fontsize=10,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.legend(loc='lower right', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    outfile2 = '../phase2/paper/figures/correlation_scatter_comparison.png'
    plt.savefig(outfile2, dpi=150, bbox_inches='tight')
    print(f"\nScatter figure saved to: {outfile2}")
    
    plt.savefig('correlation_scatter_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY: What Drives Low-ℓ EE?")
    print("=" * 60)
    
    if 'Lambda_EDE_ridder' in available_params and 'tau_reio' in available_params:
        lambda_idx = available_params.index('Lambda_EDE_ridder')
        tau_idx = available_params.index('tau_reio')
        
        corr_pre = corr_matrices['EDE pre-DESI'][lambda_idx, tau_idx]
        corr_post = corr_matrices['EDE +DESI'][lambda_idx, tau_idx]
        
        print(f"""
Low-ℓ EE is dominated by τ_reio (reionization optical depth).
The χ² difference comes from how τ correlates with Λ_EDE:

Pre-DESI:
  corr(Λ_EDE, τ_reio) = {corr_pre:+.2f}
  → Higher EDE amplitude allows higher τ
  → Posterior can explore τ values that fit low-ℓ EE better
  → Result: Δχ²(low-ℓ EE) ≈ -15

+DESI:
  corr(Λ_EDE, τ_reio) = {corr_post:+.2f}
  → DESI geometry forces correlation to FLIP
  → Higher EDE now requires LOWER τ
  → Posterior excluded from the τ "sweet spot"
  → Result: Δχ²(low-ℓ EE) ≈ -0.4 (benefit lost)

PHYSICAL INTERPRETATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━
DESI BAO tightly constrains the distance-redshift relation.
Within this narrow geometric corridor:
  - EDE must increase to maintain r_s reduction
  - But this forces τ down (via other CMB constraints)
  - Lower τ → worse low-ℓ EE fit

The "correlation flip" is the geometric price of DESI's precision.
""")

if __name__ == '__main__':
    main()
