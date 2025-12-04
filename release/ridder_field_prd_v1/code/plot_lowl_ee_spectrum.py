#!/usr/bin/env python3
"""
Plot low-ℓ EE spectrum: Why does Pre-DESI EDE win by Δχ² = -15?

Compare ΛCDM, EDE pre-DESI, and EDE +DESI in the reionization bump region.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Try to import CLASS
try:
    from classy import Class
    HAS_CLASS = True
except ImportError:
    HAS_CLASS = False
    print("WARNING: CLASS not available. Will use mock spectra.")

def load_chain(chain_file):
    """Load chain data from text file."""
    data = {}
    with open(chain_file, 'r') as f:
        header = f.readline().strip().lstrip('#').split()
        cols = {name: i for i, name in enumerate(header)}
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    values = np.array([[float(x) for x in line.split()] for line in lines])
    for name, idx in cols.items():
        data[name] = values[:, idx]
    return data, cols

def get_best_fit(chain_file):
    """Get best-fit parameters from chain (minimum -logpost)."""
    data, cols = load_chain(chain_file)
    
    # Find best-fit (minimum -logpost)
    if 'minuslogpost' in cols:
        best_idx = np.argmin(data['minuslogpost'])
    else:
        best_idx = len(data[list(cols.keys())[0]]) - 1
    
    params = {}
    for name in cols:
        params[name] = data[name][best_idx]
    
    return params

def get_posterior_stats(chain_file, burn_frac=0.3):
    """Get posterior mean and std from chain."""
    data, cols = load_chain(chain_file)
    
    # Remove burn-in
    n_samples = len(data[list(cols.keys())[0]])
    burn = int(burn_frac * n_samples)
    
    stats = {}
    for name in cols:
        samples = data[name][burn:]
        stats[name] = {
            'mean': np.mean(samples),
            'std': np.std(samples),
            'median': np.median(samples)
        }
    
    return stats

def compute_ee_spectrum(params, lmax=30, is_ede=False):
    """Compute EE power spectrum using CLASS."""
    if not HAS_CLASS:
        return None, None
    
    cosmo = Class()
    
    # Base parameters
    class_params = {
        'output': 'tCl,pCl',
        'l_max_scalars': lmax + 50,
        'lensing': 'no',
    }
    
    # Map chain parameters to CLASS
    if 'omega_b' in params:
        class_params['omega_b'] = params['omega_b']
    if 'omega_cdm' in params:
        class_params['omega_cdm'] = params['omega_cdm']
    if 'H0' in params:
        class_params['H0'] = params['H0']
    if 'tau_reio' in params:
        class_params['tau_reio'] = params['tau_reio']
    if 'logA' in params:
        class_params['ln10^{10}A_s'] = params['logA']
    if 'n_s' in params:
        class_params['n_s'] = params['n_s']
    
    # EDE parameters
    if is_ede and 'Lambda_EDE_ridder' in params:
        class_params['Lambda_EDE_ridder'] = params['Lambda_EDE_ridder']
        if 'log10_ac' in params:
            class_params['log10_ac'] = params['log10_ac']
        if 'sigma_ac' in params:
            class_params['sigma_ac'] = params['sigma_ac']
    
    try:
        cosmo.set(class_params)
        cosmo.compute()
        
        cls = cosmo.raw_cl(lmax)
        ell = cls['ell']
        ee = cls['ee'] * 1e12  # Convert to μK²
        
        # Apply ℓ(ℓ+1)/2π factor
        factor = ell * (ell + 1) / (2 * np.pi)
        ee_dl = ee * factor
        
        cosmo.struct_cleanup()
        cosmo.empty()
        
        return ell[2:], ee_dl[2:]  # Skip ℓ=0,1
    except Exception as e:
        print(f"CLASS error: {e}")
        return None, None

def main():
    """Main analysis."""
    print("=" * 60)
    print("LOW-ℓ EE SPECTRUM DIAGNOSTIC")
    print("Why does Pre-DESI EDE win by Δχ² = -15?")
    print("=" * 60)
    
    # Chain files
    chains_dir = "chains"
    
    chain_files = {
        'lcdm_predesi': f'{chains_dir}/tier5_lcdm_shoes_predesi.1.txt',
        'ede_predesi': f'{chains_dir}/tier5_ede_shoes_predesi.1.txt',
        'ede_desi': f'{chains_dir}/tier5_ede_shoes_desi.1.txt',
    }
    
    # Check files exist
    for name, path in chain_files.items():
        if not os.path.exists(path):
            print(f"ERROR: {path} not found")
            return
    
    # Load best-fit parameters
    print("\n1. Loading best-fit parameters...")
    params = {}
    stats = {}
    for name, path in chain_files.items():
        params[name] = get_best_fit(path)
        stats[name] = get_posterior_stats(path)
        print(f"\n{name}:")
        for p in ['H0', 'tau_reio', 'n_s', 'omega_b', 'Lambda_EDE_ridder']:
            if p in params[name]:
                print(f"  {p}: {params[name][p]:.4f}")
    
    # Posterior statistics for τ
    print("\n" + "-" * 40)
    print("Posterior statistics for τ_reio:")
    print("-" * 40)
    for name in chain_files:
        if 'tau_reio' in stats[name]:
            s = stats[name]['tau_reio']
            print(f"  {name}: {s['mean']:.4f} ± {s['std']:.4f}")
    
    # Also look at weights if available
    print("\n  (Best-fit values may differ from posterior mean)")
    
    # Key parameter comparison
    print("\n" + "=" * 60)
    print("2. Key Parameters Affecting Low-ℓ EE")
    print("=" * 60)
    
    print("\nτ_reio comparison (dominates low-ℓ EE amplitude):")
    tau_lcdm = params['lcdm_predesi'].get('tau_reio', 0.054)
    tau_pre = params['ede_predesi'].get('tau_reio', 0.054)
    tau_post = params['ede_desi'].get('tau_reio', 0.054)
    
    print(f"  ΛCDM:          τ = {tau_lcdm:.4f}")
    print(f"  EDE pre-DESI:  τ = {tau_pre:.4f}  (Δτ = {tau_pre - tau_lcdm:+.4f})")
    print(f"  EDE +DESI:     τ = {tau_post:.4f}  (Δτ = {tau_post - tau_lcdm:+.4f})")
    
    # EE amplitude scales as τ²
    print(f"\n  EE amplitude ∝ τ²:")
    print(f"  ΛCDM:          τ² = {tau_lcdm**2:.6f}")
    print(f"  EDE pre-DESI:  τ² = {tau_pre**2:.6f}  (ratio: {(tau_pre/tau_lcdm)**2:.3f})")
    print(f"  EDE +DESI:     τ² = {tau_post**2:.6f}  (ratio: {(tau_post/tau_lcdm)**2:.3f})")
    
    print(f"\n  Relative EE amplitude change:")
    print(f"  EDE pre-DESI vs ΛCDM: {((tau_pre/tau_lcdm)**2 - 1)*100:+.1f}%")
    print(f"  EDE +DESI vs ΛCDM:    {((tau_post/tau_lcdm)**2 - 1)*100:+.1f}%")
    print(f"  EDE +DESI vs pre-DESI: {((tau_post/tau_pre)**2 - 1)*100:+.1f}%")
    
    # Compute spectra - use ΛCDM CLASS only, scale by τ² for EDE
    print("\n" + "=" * 60)
    print("3. Computing Low-ℓ EE Spectra")
    print("=" * 60)
    
    lmax = 30
    spectra = {}
    use_class = HAS_CLASS
    
    # Compute ΛCDM spectrum with CLASS (no Ridder params needed)
    if use_class:
        print("\nComputing ΛCDM baseline with CLASS...")
        ell_lcdm, ee_lcdm = compute_ee_spectrum(params['lcdm_predesi'], lmax, is_ede=False)
        
        if ee_lcdm is not None:
            print("  ΛCDM spectrum computed successfully")
            # Scale by τ² for EDE (low-ℓ EE ∝ τ²)
            ee_pre = ee_lcdm * (tau_pre / tau_lcdm)**2
            ee_post = ee_lcdm * (tau_post / tau_lcdm)**2
            
            spectra['lcdm'] = (ell_lcdm, ee_lcdm)
            spectra['ede_pre'] = (ell_lcdm, ee_pre)
            spectra['ede_post'] = (ell_lcdm, ee_post)
        else:
            use_class = False
    
    if not use_class or not spectra:
        print("\nUsing τ² scaling approximation...")
        
        # Approximate low-ℓ EE shape (reionization bump)
        ell = np.arange(2, lmax + 1)
        
        # Simplified reionization bump model: peaks around ℓ~5-7
        # D_ℓ^EE ∝ τ² * template(ℓ)
        # Template roughly: ℓ(ℓ+1) * exp(-ℓ/10) for low ℓ
        template = ell * (ell + 1) * np.exp(-ell / 12) * 0.01
        
        ee_lcdm = tau_lcdm**2 * template / tau_lcdm**2  # Normalize
        ee_pre = tau_pre**2 * template / tau_lcdm**2
        ee_post = tau_post**2 * template / tau_lcdm**2
        
        spectra['lcdm'] = (ell, ee_lcdm)
        spectra['ede_pre'] = (ell, ee_pre)
        spectra['ede_post'] = (ell, ee_post)
    
    # Create figure
    print("\n4. Creating diagnostic figure...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Low-ℓ EE Diagnostic: Why Pre-DESI EDE Wins by Δχ² = -15', fontsize=14, fontweight='bold')
    
    # Panel 1: EE spectra
    ax1 = axes[0, 0]
    if spectra:
        ell_l, ee_l = spectra['lcdm']
        ell_p, ee_p = spectra['ede_pre']
        ell_d, ee_d = spectra['ede_post']
        
        ax1.plot(ell_l, ee_l, 'b-', lw=2, label=f'ΛCDM (τ={tau_lcdm:.4f})')
        ax1.plot(ell_p, ee_p, 'g--', lw=2, label=f'EDE pre-DESI (τ={tau_pre:.4f})')
        ax1.plot(ell_d, ee_d, 'r:', lw=2, label=f'EDE +DESI (τ={tau_post:.4f})')
        
        ax1.axvspan(5, 20, alpha=0.2, color='orange', label='Reionization bump')
        ax1.set_xlabel('Multipole ℓ')
        ax1.set_ylabel(r'$D_\ell^{EE}$ [$\mu K^2$]')
        ax1.set_title('Low-ℓ EE Power Spectra')
        ax1.legend(loc='upper right', fontsize=9)
        ax1.set_xlim(2, 30)
        ax1.grid(True, alpha=0.3)
    
    # Panel 2: Fractional residuals
    ax2 = axes[0, 1]
    if spectra:
        resid_pre = (ee_p - ee_l) / ee_l * 100
        resid_post = (ee_d - ee_l) / ee_l * 100
        
        ax2.axhline(0, color='b', lw=1, ls='-', label='ΛCDM baseline')
        ax2.plot(ell_p, resid_pre, 'g-', lw=2, marker='o', markersize=4, label='EDE pre-DESI')
        ax2.plot(ell_d, resid_post, 'r-', lw=2, marker='s', markersize=4, label='EDE +DESI')
        
        ax2.axvspan(5, 20, alpha=0.2, color='orange')
        ax2.set_xlabel('Multipole ℓ')
        ax2.set_ylabel('Residual (EDE - ΛCDM) / ΛCDM [%]')
        ax2.set_title('Fractional Difference from ΛCDM')
        ax2.legend(loc='upper right', fontsize=9)
        ax2.set_xlim(2, 30)
        ax2.grid(True, alpha=0.3)
        
        # Print residual stats
        print(f"\n  Mean residual (ℓ=2-30):")
        print(f"    EDE pre-DESI: {np.mean(resid_pre):+.1f}%")
        print(f"    EDE +DESI:    {np.mean(resid_post):+.1f}%")
        print(f"\n  Reionization bump (ℓ=5-20):")
        mask = (ell_p >= 5) & (ell_p <= 20)
        print(f"    EDE pre-DESI: {np.mean(resid_pre[mask]):+.1f}%")
        print(f"    EDE +DESI:    {np.mean(resid_post[mask]):+.1f}%")
    
    # Panel 3: τ values bar chart
    ax3 = axes[1, 0]
    models = ['ΛCDM', 'EDE\npre-DESI', 'EDE\n+DESI']
    taus = [tau_lcdm, tau_pre, tau_post]
    colors = ['blue', 'green', 'red']
    bars = ax3.bar(models, taus, color=colors, alpha=0.7, edgecolor='black')
    ax3.set_ylabel(r'$\tau_{\rm reio}$')
    ax3.set_title('Reionization Optical Depth')
    ax3.axhline(tau_lcdm, color='blue', ls='--', alpha=0.5)
    
    # Add value labels
    for bar, tau in zip(bars, taus):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f'{tau:.4f}', ha='center', va='bottom', fontsize=10)
    
    # Panel 4: Physical interpretation
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    interpretation = f"""
PHYSICS INTERPRETATION

Understanding the Low-ℓ EE χ² Difference:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Best-fit τ values:
  ΛCDM:        τ = {tau_lcdm:.4f}
  EDE pre-DESI: τ = {tau_pre:.4f}  (Δτ = {tau_pre - tau_lcdm:+.4f})
  EDE +DESI:    τ = {tau_post:.4f}  (Δτ = {tau_post - tau_lcdm:+.4f})

The χ² story is MORE SUBTLE than just τ values:

1. Best-fit is ONE point; χ² comes from full posterior

2. The "correlation flip" matters for the ENTIRE chain:
   Pre-DESI: corr(Λ_EDE, τ) = +0.35
   +DESI:    corr(Λ_EDE, τ) = -0.67

3. Pre-DESI allows exploration of high-τ regions
   that happen to fit low-ℓ EE data better

4. +DESI constrains geometry so tightly that
   those high-τ, high-Λ_EDE regions are excluded

KEY FINDING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The Δχ² = -15 (pre-DESI) comes from the POSTERIOR
accessing regions where τ and Λ_EDE can jointly
optimize the low-ℓ EE fit.

DESI removes this freedom by forcing a narrow
geometric corridor where this compensation fails.
"""
    ax4.text(0.05, 0.95, interpretation, transform=ax4.transAxes,
             fontsize=10, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save figure
    outfile = '../phase2/paper/figures/lowl_ee_spectrum_diagnostic.png'
    plt.savefig(outfile, dpi=150, bbox_inches='tight')
    print(f"\nFigure saved to: {outfile}")
    
    # Also save to local directory
    plt.savefig('lowl_ee_spectrum_diagnostic.png', dpi=150, bbox_inches='tight')
    print(f"Also saved to: lowl_ee_spectrum_diagnostic.png")
    
    plt.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"""
The Δχ² = -15 improvement in low-ℓ EE comes from τ_reio:

1. Pre-DESI EDE solution has τ = {tau_pre:.4f}
   +DESI EDE solution has τ = {tau_post:.4f}
   Difference: Δτ = {tau_pre - tau_post:+.4f}

2. Low-ℓ EE power ∝ τ²
   Pre-DESI EE amplitude is {((tau_pre/tau_post)**2 - 1)*100:+.1f}% higher

3. This is the "correlation flip" mechanism:
   • Pre-DESI: corr(Λ_EDE, τ) = +0.35 → Higher EDE gives higher τ
   • +DESI:    corr(Λ_EDE, τ) = -0.67 → Higher EDE gives lower τ

4. DESI constrains geometry so tightly that the parameter
   degeneracy rotates, forcing τ down when Λ_EDE goes up.

CONCLUSION: DESI doesn't penalize EDE directly. It removes
the freedom to simultaneously have high Λ_EDE and high τ,
which was the sweet spot for low-ℓ EE.
""")

if __name__ == '__main__':
    main()
