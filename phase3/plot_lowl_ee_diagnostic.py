#!/usr/bin/env python3
"""
Plot the low-ℓ EE diagnostic: Why does DESI destroy the benefit?

KEY FINDING: DESI flips the Λ_EDE-τ_reio correlation!
  Pre-DESI: corr(Λ_EDE, τ) = +0.35 (higher Λ → higher τ → HELPS low-ℓ EE)
  +DESI:    corr(Λ_EDE, τ) = -0.67 (higher Λ → LOWER τ → HURTS low-ℓ EE)
"""

import numpy as np
import matplotlib.pyplot as plt
import os

def load_chain(chain_file):
    """Load chain data."""
    if not os.path.exists(chain_file):
        return None, None
    
    data = np.loadtxt(chain_file)
    
    with open(chain_file, 'r') as f:
        header = f.readline().strip()
    
    if header.startswith('#'):
        cols = header[1:].split()
    else:
        cols = []
    
    return data, cols

def main():
    # Chain paths
    chains = {
        'Pre-DESI EDE': 'chains/tier5_ede_shoes_predesi.1.txt',
        '+DESI EDE': 'chains/tier5_ede_shoes_desi.1.txt',
    }
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Colors
    colors = {
        'Pre-DESI EDE': '#2E86AB',  # Blue
        '+DESI EDE': '#E94F37',      # Red
    }
    
    for name, chain_file in chains.items():
        data, cols = load_chain(chain_file)
        if data is None:
            print(f"Could not load {name}")
            continue
        
        # Find column indices
        col_map = {col: i for i, col in enumerate(cols)}
        
        # Get relevant columns
        lambda_col = col_map.get('Lambda_EDE_ridder')
        tau_col = col_map.get('tau_reio')
        ns_col = col_map.get('n_s')
        h0_col = col_map.get('H0')
        
        if lambda_col is None or tau_col is None:
            print(f"Missing columns for {name}")
            continue
        
        lambda_vals = data[:, lambda_col]
        tau_vals = data[:, tau_col]
        ns_vals = data[:, ns_col] if ns_col else None
        h0_vals = data[:, h0_col] if h0_col else None
        
        # Subsample for plotting
        n_plot = min(2000, len(lambda_vals))
        idx = np.random.choice(len(lambda_vals), n_plot, replace=False)
        
        # Plot 1: Λ_EDE vs τ_reio
        ax = axes[0, 0]
        ax.scatter(lambda_vals[idx], tau_vals[idx], alpha=0.3, s=5, 
                   c=colors[name], label=name)
        
        # Add best-fit line
        z = np.polyfit(lambda_vals, tau_vals, 1)
        p = np.poly1d(z)
        x_line = np.linspace(lambda_vals.min(), lambda_vals.max(), 100)
        ax.plot(x_line, p(x_line), '-', c=colors[name], lw=2)
        
        corr = np.corrcoef(lambda_vals, tau_vals)[0, 1]
        ax.text(0.05, 0.95 if 'Pre' in name else 0.85, 
                f'{name}: r = {corr:+.2f}',
                transform=ax.transAxes, fontsize=10, 
                color=colors[name], fontweight='bold')
        
        # Plot 2: Λ_EDE vs n_s
        if ns_vals is not None:
            ax = axes[0, 1]
            ax.scatter(lambda_vals[idx], ns_vals[idx], alpha=0.3, s=5,
                       c=colors[name], label=name)
            
            z = np.polyfit(lambda_vals, ns_vals, 1)
            p = np.poly1d(z)
            ax.plot(x_line, p(x_line), '-', c=colors[name], lw=2)
            
            corr = np.corrcoef(lambda_vals, ns_vals)[0, 1]
            ax.text(0.05, 0.95 if 'Pre' in name else 0.85,
                    f'{name}: r = {corr:+.2f}',
                    transform=ax.transAxes, fontsize=10,
                    color=colors[name], fontweight='bold')
        
        # Plot 3: τ_reio vs n_s  
        if ns_vals is not None:
            ax = axes[1, 0]
            ax.scatter(tau_vals[idx], ns_vals[idx], alpha=0.3, s=5,
                       c=colors[name], label=name)
            
            corr = np.corrcoef(tau_vals, ns_vals)[0, 1]
            ax.text(0.05, 0.95 if 'Pre' in name else 0.85,
                    f'{name}: r = {corr:+.2f}',
                    transform=ax.transAxes, fontsize=10,
                    color=colors[name], fontweight='bold')
        
        # Plot 4: H0 vs τ_reio
        if h0_vals is not None:
            ax = axes[1, 1]
            ax.scatter(h0_vals[idx], tau_vals[idx], alpha=0.3, s=5,
                       c=colors[name], label=name)
            
            corr = np.corrcoef(h0_vals, tau_vals)[0, 1]
            ax.text(0.05, 0.95 if 'Pre' in name else 0.85,
                    f'{name}: r = {corr:+.2f}',
                    transform=ax.transAxes, fontsize=10,
                    color=colors[name], fontweight='bold')
    
    # Labels
    axes[0, 0].set_xlabel(r'$\Lambda_{\rm EDE}$ [eV]', fontsize=12)
    axes[0, 0].set_ylabel(r'$\tau_{\rm reio}$', fontsize=12)
    axes[0, 0].set_title('THE CORRELATION FLIP\n' + 
                         r'Pre-DESI: $\Lambda\uparrow \Rightarrow \tau\uparrow$ (helps low-$\ell$ EE)' + '\n' +
                         r'+DESI: $\Lambda\uparrow \Rightarrow \tau\downarrow$ (hurts low-$\ell$ EE)',
                         fontsize=10)
    axes[0, 0].legend(loc='lower right')
    
    axes[0, 1].set_xlabel(r'$\Lambda_{\rm EDE}$ [eV]', fontsize=12)
    axes[0, 1].set_ylabel(r'$n_s$', fontsize=12)
    axes[0, 1].set_title(r'$\Lambda_{\rm EDE}$ vs $n_s$', fontsize=11)
    
    axes[1, 0].set_xlabel(r'$\tau_{\rm reio}$', fontsize=12)
    axes[1, 0].set_ylabel(r'$n_s$', fontsize=12)
    axes[1, 0].set_title(r'$\tau_{\rm reio}$ vs $n_s$', fontsize=11)
    
    axes[1, 1].set_xlabel(r'$H_0$ [km/s/Mpc]', fontsize=12)
    axes[1, 1].set_ylabel(r'$\tau_{\rm reio}$', fontsize=12)
    axes[1, 1].set_title(r'$H_0$ vs $\tau_{\rm reio}$', fontsize=11)
    
    plt.suptitle('Why DESI Destroys the Low-ℓ EE Benefit\n' +
                 'The Λ_EDE-τ correlation flips from +0.35 to -0.67',
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig('lowl_ee_correlation_flip.png', dpi=150, bbox_inches='tight')
    print("Saved: lowl_ee_correlation_flip.png")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY: THE CORRELATION FLIP MECHANISM")
    print("=" * 60)
    print("""
Why does DESI destroy the Δχ² = -15 low-ℓ EE benefit?

1. BEFORE DESI (Pre-DESI SH0ES World):
   - Λ_EDE and τ_reio are positively correlated (+0.35)
   - Higher EDE → Higher τ → Better low-ℓ EE fit
   - SH0ES and low-ℓ EE BOTH favor the same corner
   - Net: Δχ²(low-ℓ EE) = -15.2

2. AFTER DESI (+DESI SH0ES World):
   - DESI tightens geometric constraints
   - Λ_EDE forced higher (0.60 → 0.79) to satisfy BAO
   - But now Λ_EDE and τ_reio are NEGATIVELY correlated (-0.67)!
   - Higher EDE → LOWER τ → Worse low-ℓ EE fit
   - Net: Δχ²(low-ℓ EE) = -0.4 (almost zero)

3. THE PHYSICS:
   - τ_reio controls the reionization bump amplitude (∝ τ²)
   - Pre-DESI: The model finds τ ≈ 0.060 which fits the bump well
   - +DESI: Geometry forces τ ≈ 0.059 (lower) which fits worse
   - This 1.5% shift in τ corresponds to ~3% in low-ℓ EE amplitude

4. CONCLUSION:
   - The "DESI tax" is NOT from DESI data (Δχ² = +0.2, neutral)
   - It's from DESI INDIRECTLY changing the parameter correlations
   - This removes the low-ℓ EE compensation that hid the high-ℓ cost
   - The +17 high-ℓ cost was ALWAYS there; it's now exposed
""")

if __name__ == "__main__":
    main()
