#!/usr/bin/env python3
"""
Scientific Stress Test for Ridder Field Model
==============================================

Tests fundamental observational pillars BEFORE launching MCMC:
1. BBN Consistency (Y_He)
2. Background Evolution (r_s, H_0)
3. CMB Damping Tail (high-ℓ)
4. β-Coupling Linearity (structure suppression)

If any test fails, the model is NOT ready for Phase 3.
"""

import numpy as np
import sys
import os

# Try to import classy
try:
    from classy import Class
except ImportError:
    print("ERROR: classy Python wrapper not found.")
    print("Installing classy...")
    import subprocess
    result = subprocess.run(
        ["bash", "/Users/steveridder/Git/Ridder Field/phase3/install_deps.sh"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("Failed to install classy. Please run:")
        print("  cd /Users/steveridder/Git/Ridder\\ Field/phase3")
        print("  bash install_deps.sh")
        sys.exit(1)
    # Try again
    try:
        from classy import Class
    except ImportError:
        print("ERROR: classy installation failed.")
        sys.exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Baseline ΛCDM (Planck 2018 TT,TE,EE+lowE+lensing best fit)
params_lcdm = {
    'h': 0.6736,
    'omega_b': 0.02237,
    'omega_cdm': 0.1200,
    'A_s': 2.1e-9,
    'n_s': 0.9649,
    'tau_reio': 0.0544,
    'output': 'tCl,mPk',
    'P_k_max_1/Mpc': 1.0,
    'l_max_scalars': 3000,
    'YHe': 'BBN',  # Force consistent BBN calculation
    'gauge': 'newtonian'
}

# Ridder Model (Tuned Phase 2.5)
params_ridder = {
    'h': 0.6736,
    'omega_b': 0.02237,
    'omega_cdm': 0.1200,
    'A_s': 2.1e-9,
    'n_s': 0.9649,
    'tau_reio': 0.0544,
    
    # Ridder field parameters
    'has_ridder': 'yes',
    'Lambda_EDE_ridder': 1.0,      # eV
    'f_axion_ridder': 1.0e27,      # eV
    'theta_i_ridder': 2.5,         # radians
    'beta_ridder': 0.01,           # coupling strength
    'n_ridder': 3,                 # potential exponent
    
    # Output
    'output': 'tCl,mPk',
    'P_k_max_1/Mpc': 1.0,
    'l_max_scalars': 3000,
    'YHe': 'BBN',
    'gauge': 'newtonian'
}

# =============================================================================
# STRESS TEST FUNCTIONS
# =============================================================================

def run_audit():
    """Execute all four stress tests."""
    print("=" * 70)
    print("SCIENTIFIC STRESS TEST - RIDDER FIELD MODEL")
    print("=" * 70)
    print()
    
    results = {
        'bbn': None,
        'background': None,
        'damping': None,
        'coupling': None
    }
    
    # -------------------------------------------------------------------------
    # TEST 1: BBN CONSISTENCY
    # -------------------------------------------------------------------------
    print("[TEST 1] Big Bang Nucleosynthesis (Y_He)")
    print("-" * 70)
    
    try:
        # Run ΛCDM
        print("  Computing ΛCDM baseline...")
        cosmo_lcdm = Class()
        cosmo_lcdm.set(params_lcdm)
        cosmo_lcdm.compute()
        
        # Run Ridder
        print("  Computing Ridder model...")
        cosmo_ridder = Class()
        cosmo_ridder.set(params_ridder)
        cosmo_ridder.compute()
        
        # Extract Y_He
        yhe_lcdm = cosmo_lcdm.get_current_derived_parameters(['YHe'])['YHe']
        yhe_ridder = cosmo_ridder.get_current_derived_parameters(['YHe'])['YHe']
        diff_yhe = abs(yhe_ridder - yhe_lcdm) / yhe_lcdm * 100
        
        print(f"  ΛCDM:   Y_He = {yhe_lcdm:.6f}")
        print(f"  Ridder: Y_He = {yhe_ridder:.6f}")
        print(f"  Deviation: {diff_yhe:.3f}%")
        print()
        
        if diff_yhe < 0.5:
            print("  ✅ STATUS: PASS (Safe - BBN unaffected)")
            results['bbn'] = 'PASS'
        elif diff_yhe < 1.0:
            print("  ⚠️  STATUS: WARNING (Marginal - check BBN constraints)")
            results['bbn'] = 'WARNING'
        else:
            print("  ❌ STATUS: FAIL (Excluded by BBN observations)")
            results['bbn'] = 'FAIL'
        
        print()
        
        # ---------------------------------------------------------------------
        # TEST 2: BACKGROUND EVOLUTION
        # ---------------------------------------------------------------------
        print("[TEST 2] Expansion History (r_s, H_0)")
        print("-" * 70)
        
        # Extract sound horizon and H_0
        rs_lcdm = cosmo_lcdm.rs_drag()
        rs_ridder = cosmo_ridder.rs_drag()
        h0_lcdm = cosmo_lcdm.Hubble(0) * 299792.458  # Convert to km/s/Mpc
        h0_ridder = cosmo_ridder.Hubble(0) * 299792.458
        
        rs_reduction = (1 - rs_ridder / rs_lcdm) * 100
        h0_increase = (h0_ridder / h0_lcdm - 1) * 100
        
        print(f"  ΛCDM:   r_s = {rs_lcdm:.2f} Mpc, H_0 = {h0_lcdm:.2f} km/s/Mpc")
        print(f"  Ridder: r_s = {rs_ridder:.2f} Mpc, H_0 = {h0_ridder:.2f} km/s/Mpc")
        print(f"  r_s reduction: {rs_reduction:.2f}%")
        print(f"  H_0 increase:  {h0_increase:.2f}%")
        print()
        
        # Check if H_0 is in the target range (73-74 km/s/Mpc)
        if 72.5 < h0_ridder < 74.5:
            print(f"  ✅ STATUS: PASS (H_0 = {h0_ridder:.2f} resolves Hubble tension)")
            results['background'] = 'PASS'
        elif 71.0 < h0_ridder < 75.0:
            print(f"  ⚠️  STATUS: WARNING (H_0 = {h0_ridder:.2f} marginally resolves tension)")
            results['background'] = 'WARNING'
        else:
            print(f"  ❌ STATUS: FAIL (H_0 = {h0_ridder:.2f} does not resolve tension)")
            results['background'] = 'FAIL'
        
        print()
        
        # ---------------------------------------------------------------------
        # TEST 3: CMB DAMPING TAIL
        # ---------------------------------------------------------------------
        print("[TEST 3] CMB Damping Tail (high-ℓ)")
        print("-" * 70)
        
        # Get CMB spectra
        cl_lcdm = cosmo_lcdm.lensed_cl(3000)
        cl_ridder = cosmo_ridder.lensed_cl(3000)
        
        # Extract TT spectra (convert to D_ℓ = ℓ(ℓ+1)C_ℓ/2π in μK²)
        ell = np.arange(2, 3001)
        tt_lcdm = cl_lcdm['tt'][2:3001] * (ell * (ell + 1)) / (2 * np.pi) * (2.7255e6)**2
        tt_ridder = cl_ridder['tt'][2:3001] * (ell * (ell + 1)) / (2 * np.pi) * (2.7255e6)**2
        
        # Check ratios at key ℓ values
        ratio_1000 = tt_ridder[998] / tt_lcdm[998]  # Index 998 = ℓ=1000
        ratio_2000 = tt_ridder[1998] / tt_lcdm[1998]
        ratio_3000 = tt_ridder[2998] / tt_lcdm[2998]
        
        print(f"  Ratio @ ℓ=1000: {ratio_1000:.4f}")
        print(f"  Ratio @ ℓ=2000: {ratio_2000:.4f}")
        print(f"  Ratio @ ℓ=3000: {ratio_3000:.4f}")
        print()
        
        # Check if damping tail is consistent (within 10%)
        if 0.90 < ratio_3000 < 1.10:
            print("  ✅ STATUS: PASS (Damping tail consistent)")
            results['damping'] = 'PASS'
        elif 0.80 < ratio_3000 < 1.20:
            print("  ⚠️  STATUS: WARNING (Mild damping modification - may need n_s adjustment)")
            results['damping'] = 'WARNING'
        else:
            print("  ❌ STATUS: FAIL (Significant damping modification - Silk damping violated)")
            results['damping'] = 'FAIL'
        
        print()
        
        # Clean up for next test
        cosmo_lcdm.struct_cleanup()
        cosmo_lcdm.empty()
        cosmo_ridder.struct_cleanup()
        cosmo_ridder.empty()
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results['bbn'] = 'ERROR'
        results['background'] = 'ERROR'
        results['damping'] = 'ERROR'
    
    # -------------------------------------------------------------------------
    # TEST 4: β-COUPLING LINEARITY
    # -------------------------------------------------------------------------
    print("[TEST 4] β-Coupling Linearity (Structure Suppression)")
    print("-" * 70)
    
    try:
        betas = [0.0, 0.005, 0.01, 0.015, 0.02]
        pk_values = []
        
        print("  Running β sweep...")
        for beta in betas:
            p_sweep = params_ridder.copy()
            p_sweep['beta_ridder'] = beta
            
            cosmo = Class()
            cosmo.set(p_sweep)
            cosmo.compute()
            
            # Get P(k) at z=0, k=0.1 h/Mpc
            h = cosmo.h()
            pk = cosmo.pk(0.1 * h, 0.0)
            pk_values.append(pk)
            
            print(f"    β = {beta:.3f}: P(k=0.1) = {pk:.3e}")
            
            cosmo.struct_cleanup()
            cosmo.empty()
        
        print()
        
        # Check monotonicity (should decrease as β increases)
        pk_array = np.array(pk_values)
        diffs = np.diff(pk_array)
        is_monotonic = np.all(diffs < 0)
        
        # Check linearity (differences should be roughly constant)
        if len(diffs) > 1:
            diff_ratios = diffs[1:] / diffs[:-1]
            is_linear = np.all((0.5 < diff_ratios) & (diff_ratios < 2.0))
        else:
            is_linear = True
        
        print(f"  Monotonic suppression: {is_monotonic}")
        print(f"  Linear scaling:        {is_linear}")
        print()
        
        if is_monotonic and is_linear:
            print("  ✅ STATUS: PASS (Coupling behaves linearly)")
            results['coupling'] = 'PASS'
        elif is_monotonic:
            print("  ⚠️  STATUS: WARNING (Monotonic but nonlinear - check equations)")
            results['coupling'] = 'WARNING'
        else:
            print("  ❌ STATUS: FAIL (Non-monotonic - sign error or resonance in equations)")
            results['coupling'] = 'FAIL'
        
        print()
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results['coupling'] = 'ERROR'
    
    # -------------------------------------------------------------------------
    # FINAL VERDICT
    # -------------------------------------------------------------------------
    print("=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    print()
    
    all_pass = all(r == 'PASS' for r in results.values())
    any_fail = any(r == 'FAIL' or r == 'ERROR' for r in results.values())
    
    print("Test Results:")
    print(f"  [1] BBN Consistency:    {results['bbn']}")
    print(f"  [2] Background:         {results['background']}")
    print(f"  [3] Damping Tail:       {results['damping']}")
    print(f"  [4] Coupling Linearity: {results['coupling']}")
    print()
    
    if all_pass:
        print("✅ CLEARED FOR PHASE 3 MCMC")
        print()
        print("All fundamental observational pillars are respected.")
        print("The model is scientifically sound and ready for parameter estimation.")
        return 0
    elif any_fail:
        print("❌ NOT READY FOR PHASE 3")
        print()
        print("One or more tests FAILED. Fix the issues before launching MCMC.")
        print("See diagnostic messages above for specific problems.")
        return 1
    else:
        print("⚠️  PROCEED WITH CAUTION")
        print()
        print("Some tests show warnings. Review carefully before launching MCMC.")
        print("Consider documenting these deviations in the paper.")
        return 2

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    exit_code = run_audit()
    sys.exit(exit_code)

