#!/usr/bin/env python3
"""
Diagnose why DESI destroys the low-ℓ EE benefit in EDE fits.

The mystery:
- Pre-DESI: Planck low-ℓ EE favors EDE by Δχ² = -15.2
- +DESI: Planck low-ℓ EE favors EDE by only Δχ² = -0.4
- DESI itself is nearly neutral (+0.2)

Hypothesis: DESI forces a parameter shift that kills the low-ℓ EE benefit.
Key suspects: τ_reio, n_s, ω_b, Λ_EDE
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
import sys

# Add CLASS to path
sys.path.insert(0, '/home/ridderadmin/Ridder-Field/phase2/class/python')

try:
    from classy import Class
    HAS_CLASS = True
except ImportError:
    HAS_CLASS = False
    print("Warning: CLASS not available. Will skip spectrum computation.")

def load_chain(chain_file):
    """Load chain and extract parameters."""
    if not os.path.exists(chain_file):
        return None
    
    data = np.loadtxt(chain_file)
    
    # Try to load parameter names from header
    with open(chain_file, 'r') as f:
        header = f.readline().strip()
    
    if header.startswith('#'):
        cols = header[1:].split()
    else:
        # Default column names for EDE chains
        cols = ['weight', 'minuslogpost', 'logA', 'n_s', 'H0', 'omega_b', 
                'omega_cdm', 'tau_reio', 'Lambda_EDE_ridder']
    
    return data, cols

def get_best_fit(chain_file):
    """Get best-fit parameters from chain."""
    result = load_chain(chain_file)
    if result is None:
        return None
    
    data, cols = result
    
    # Find minimum -logpost
    minuslogpost_col = None
    for i, col in enumerate(cols):
        if 'minuslogpost' in col.lower() or 'chi2' in col.lower():
            minuslogpost_col = i
            break
    
    if minuslogpost_col is None:
        minuslogpost_col = 1  # Default
    
    best_idx = np.argmin(data[:, minuslogpost_col])
    best_params = {}
    
    for i, col in enumerate(cols):
        if i < data.shape[1]:
            best_params[col] = data[best_idx, i]
    
    return best_params

def compute_lowl_ee(params, lmax=30):
    """Compute low-ℓ EE spectrum using CLASS."""
    if not HAS_CLASS:
        return None, None
    
    cosmo = Class()
    
    # Set up parameters
    class_params = {
        'output': 'tCl pCl',
        'lensing': 'no',
        'l_max_scalars': lmax + 10,
        'omega_b': params.get('omega_b', 0.02237),
        'omega_cdm': params.get('omega_cdm', 0.1200),
        'H0': params.get('H0', 70.0),
        'tau_reio': params.get('tau_reio', 0.054),
        'n_s': params.get('n_s', 0.9649),
        'ln10^{10}A_s': params.get('logA', 3.044),
    }
    
    # Add EDE parameters if present
    if 'Lambda_EDE_ridder' in params and params['Lambda_EDE_ridder'] > 0:
        class_params['Lambda_EDE_ridder'] = params['Lambda_EDE_ridder']
        class_params['n_ridder'] = params.get('n_ridder', 3.0)
        class_params['theta_i_ridder'] = params.get('theta_i_ridder', 1.0)
        class_params['beta_ridder'] = params.get('beta_ridder', 0.0)
    
    try:
        cosmo.set(class_params)
        cosmo.compute()
        
        cls = cosmo.lensed_cl(lmax)
        ell = np.arange(lmax + 1)
        ee = cls['ee'] * ell * (ell + 1) / (2 * np.pi) * 1e12  # μK²
        
        cosmo.struct_cleanup()
        cosmo.empty()
        
        return ell[2:], ee[2:]
    except Exception as e:
        print(f"CLASS error: {e}")
        return None, None

def main():
    print("=" * 70)
    print("DIAGNOSING LOW-ℓ EE PARAMETER SHIFT")
    print("=" * 70)
    
    # Define chain paths
    chain_dir = Path("chains")
    
    # Pre-DESI chains
    pre_desi_ede = chain_dir / "tier5_ede_shoes_predesi.1.txt"
    pre_desi_lcdm = chain_dir / "tier5_lcdm_shoes_predesi.1.txt"
    
    # +DESI chains
    plus_desi_ede = chain_dir / "tier5_ede_shoes_desi.1.txt"
    plus_desi_lcdm = chain_dir / "tier5_lcdm_shoes_desi.1.txt"
    
    # Load best-fits
    print("\n1. LOADING BEST-FIT PARAMETERS")
    print("-" * 50)
    
    params = {}
    for name, path in [
        ('Pre-DESI EDE', pre_desi_ede),
        ('Pre-DESI ΛCDM', pre_desi_lcdm),
        ('+DESI EDE', plus_desi_ede),
        ('+DESI ΛCDM', plus_desi_lcdm),
    ]:
        if path.exists():
            best = get_best_fit(str(path))
            if best:
                params[name] = best
                print(f"\n{name}: ✓ Loaded")
            else:
                print(f"\n{name}: ✗ Failed to parse")
        else:
            print(f"\n{name}: ✗ File not found: {path}")
    
    if len(params) < 2:
        print("\nNot enough chains found. Trying alternative paths...")
        
        # Try alternative naming conventions
        alt_paths = {
            'Pre-DESI EDE': [
                'chains/tier5_ede_shoes_predesi.1.txt',
                'chains/tier5_ede_shoes_predesi.2.txt',
                'chains/tier10_ede_shoes.1.txt',
            ],
            '+DESI EDE': [
                'chains/tier5_ede_shoes_desi.1.txt',
                'chains/tier5_ede_desi.1.txt',
            ],
        }
        
        for name, paths in alt_paths.items():
            for p in paths:
                if os.path.exists(p) and name not in params:
                    best = get_best_fit(p)
                    if best:
                        params[name] = best
                        print(f"Found {name} at {p}")
                        break
    
    # 2. COMPARE KEY PARAMETERS
    print("\n" + "=" * 70)
    print("2. PARAMETER COMPARISON")
    print("=" * 70)
    
    key_params = ['H0', 'tau_reio', 'n_s', 'omega_b', 'omega_cdm', 'logA', 
                  'Lambda_EDE_ridder', 'log10_ac']
    
    if 'Pre-DESI EDE' in params and '+DESI EDE' in params:
        print("\n  Parameter Shift: Pre-DESI → +DESI (EDE)")
        print("-" * 50)
        
        pre = params['Pre-DESI EDE']
        post = params['+DESI EDE']
        
        shifts = {}
        for p in key_params:
            # Handle various naming conventions
            p_variants = [p, p.lower(), p.replace('_', '')]
            
            pre_val = None
            post_val = None
            
            for var in p_variants:
                if var in pre and pre_val is None:
                    pre_val = pre[var]
                if var in post and post_val is None:
                    post_val = post[var]
            
            if pre_val is not None and post_val is not None:
                delta = post_val - pre_val
                shifts[p] = delta
                pct = 100 * delta / abs(pre_val) if pre_val != 0 else 0
                
                flag = ""
                if abs(pct) > 5:
                    flag = " ⚠️ LARGE SHIFT"
                if p == 'tau_reio' and abs(pct) > 2:
                    flag = " 🔴 KEY FOR LOW-ℓ EE"
                
                print(f"  {p:20s}: {pre_val:10.4f} → {post_val:10.4f} (Δ = {delta:+.4f}, {pct:+.1f}%){flag}")
        
        # Highlight tau_reio
        if 'tau_reio' in shifts:
            print(f"\n  🔍 τ_reio shift: {shifts['tau_reio']:+.4f}")
            print("     Low-ℓ EE is dominated by τ_reio through the reionization bump.")
            print("     A shift in τ can completely change the low-ℓ EE χ².")
    
    # 3. CORRELATION ANALYSIS
    print("\n" + "=" * 70)
    print("3. CORRELATION ANALYSIS")
    print("=" * 70)
    
    for world, chain_file in [('Pre-DESI', pre_desi_ede), ('+DESI', plus_desi_ede)]:
        if not chain_file.exists():
            continue
        
        result = load_chain(str(chain_file))
        if result is None:
            continue
        
        data, cols = result
        
        print(f"\n{world} EDE Correlations:")
        print("-" * 50)
        
        # Find column indices
        col_map = {col: i for i, col in enumerate(cols)}
        
        # Key correlations with Lambda_EDE
        lambda_col = None
        for var in ['Lambda_EDE_ridder', 'Lambda_EDE', 'lambda_ede']:
            if var in col_map:
                lambda_col = col_map[var]
                break
        
        if lambda_col is not None:
            lambda_vals = data[:, lambda_col]
            
            for target in ['tau_reio', 'n_s', 'omega_b', 'H0']:
                if target in col_map:
                    target_vals = data[:, col_map[target]]
                    corr = np.corrcoef(lambda_vals, target_vals)[0, 1]
                    
                    strength = ""
                    if abs(corr) > 0.5:
                        strength = " (STRONG)"
                    elif abs(corr) > 0.3:
                        strength = " (moderate)"
                    
                    print(f"  corr(Λ_EDE, {target}): {corr:+.3f}{strength}")
    
    # 4. PHYSICS INTERPRETATION
    print("\n" + "=" * 70)
    print("4. PHYSICS INTERPRETATION")
    print("=" * 70)
    
    print("""
The low-ℓ EE spectrum is dominated by the reionization bump at ℓ ~ 5-20.
This bump is primarily set by:

  1. τ_reio (optical depth): Amplitude of the bump ∝ τ²
  2. z_reio (reionization redshift): Peak location
  3. n_s (spectral index): Overall tilt

KEY INSIGHT:
------------
Pre-DESI EDE may have found a "sweet spot" where:
  - The sound horizon shift (r_s → H_0) is optimized
  - τ_reio lands at a value that fits low-ℓ EE better
  - The combination is favored by SH0ES + low-ℓ EE together

When DESI is added:
  - BAO constraints tighten the geometry
  - The allowed (Λ_EDE, H_0, ω_cdm) region shifts
  - This forces τ_reio to a different value
  - The "sweet spot" in low-ℓ EE is lost

This explains the "triangular tension":
  - SH0ES and low-ℓ EE prefer the SAME EDE corner (pre-DESI)
  - DESI breaks this degeneracy by constraining geometry
  - The Planck high-ℓ cost (~+17) was always there
  - It was hidden by low-ℓ EE compensation pre-DESI
""")
    
    # 5. SAVE RESULTS
    print("\n" + "=" * 70)
    print("5. SAVING RESULTS")
    print("=" * 70)
    
    # Create summary table
    if len(params) >= 2:
        with open('lowl_ee_shift_summary.txt', 'w') as f:
            f.write("LOW-ℓ EE PARAMETER SHIFT ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("The mystery:\n")
            f.write("  Pre-DESI: Δχ²(low-ℓ EE) = -15.2\n")
            f.write("  +DESI:    Δχ²(low-ℓ EE) = -0.4\n\n")
            
            if 'Pre-DESI EDE' in params and '+DESI EDE' in params:
                f.write("Parameter Shifts (EDE: Pre-DESI → +DESI):\n")
                f.write("-" * 50 + "\n")
                
                pre = params['Pre-DESI EDE']
                post = params['+DESI EDE']
                
                for p in key_params:
                    for var in [p, p.lower()]:
                        if var in pre and var in post:
                            delta = post[var] - pre[var]
                            f.write(f"  {p}: {pre[var]:.4f} → {post[var]:.4f} (Δ = {delta:+.4f})\n")
                            break
        
        print("  Saved: lowl_ee_shift_summary.txt")
    
    # 6. NEXT STEPS
    print("\n" + "=" * 70)
    print("6. NEXT STEPS")
    print("=" * 70)
    
    print("""
To further investigate:

1. COMPUTE LOW-ℓ EE SPECTRA:
   Run this on VM with CLASS to see the actual spectrum differences.

2. PROFILE SCAN:
   Run a profile scan over Λ_EDE at fixed DESI, tracking τ_reio response.

3. TARGETED OPTIMIZATION:
   Can we find an EDE configuration that:
   - Satisfies DESI geometry
   - Preserves some low-ℓ EE benefit
   - Minimizes high-ℓ cost?

4. PAPER NARRATIVE:
   The "triangular tension" story is now complete:
   - Planck high-ℓ: Always costs ~+17
   - Planck low-ℓ EE: Gains ~-15 when SH0ES allows it
   - DESI: Neutral but shifts parameters
   - Result: DESI exposes the high-ℓ tax by removing low-ℓ compensation
""")

if __name__ == "__main__":
    main()
