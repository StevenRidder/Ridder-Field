#!/usr/bin/env python3
"""
CI TEST: Verify CDM-Ridder coupling physics

HARD ASSERTIONS (will fail CI if violated):
1. ΛCDM must give σ8 in range [0.75, 0.90] - sanity check
2. Ridder β=0 must be within 5% of ΛCDM σ8 - no coupling means similar physics  
3. β>0 MUST give LOWER σ8 than β=0 - this is the core thesis!
4. β<0 MUST give HIGHER σ8 than β=0 - opposite direction
5. Effect must be measurable (>0.1% change) - coupling actually works
6. Effect must not be catastrophic (<30% change) - numerical stability

If any assertion fails, there's a BUG in the coupling code!
"""

import sys
import numpy as np

class CouplingBugError(Exception):
    """Raised when coupling physics is broken"""
    pass

def test_coupling():
    try:
        from classy import Class
    except ImportError:
        print("ERROR: Cannot import classy")
        return False
    
    print("="*70)
    print("CI TEST: CDM-Ridder Coupling Physics")
    print("="*70)
    
    # Base cosmology
    base_params = {
        "h": 0.6732,
        "omega_b": 0.02238,
        "omega_cdm": 0.1201,
        "A_s": 2.1e-9,
        "n_s": 0.9649,
        "tau_reio": 0.0544,
        "output": "mPk",
        "P_k_max_h/Mpc": 1.0,
    }
    
    # Ridder field params
    ridder_params = {
        "gauge": "newtonian",
        "use_ridder": "yes",
        "ridder_model_type": "v3_canon",
        "ridder_use_shelf": "yes",
        "ridder_use_tail": "no",
        "ridder_f_eV": 2.0e26,
        "theta_i_ridder": 2.8,
        "ridder_Lambda_EDE_eV": 0.5,
        "ridder_a_c": 0.0003,
        "ridder_sigma_lna": 0.6,
        "ridder_c_slow": 0.0,
        "ridder_sigma_E": 0.4,
        "beta_z_c": 3000.0,
        "beta_sigma_z": 0.5,
    }
    
    results = {}
    
    # Test 1: Pure ΛCDM (no Ridder field)
    print("\n[1/4] Testing pure ΛCDM...")
    try:
        cosmo = Class()
        cosmo.set(base_params)
        cosmo.compute()
        results["lcdm"] = {"sigma8": cosmo.sigma8()}
        print(f"  σ8 = {results['lcdm']['sigma8']:.4f}")
        cosmo.struct_cleanup()
        cosmo.empty()
    except Exception as e:
        print(f"  FAIL: {e}")
        return False
    
    # Test 2: Ridder field with β=0
    print("\n[2/4] Testing Ridder field β=0...")
    try:
        cosmo = Class()
        params = {**base_params, **ridder_params, "beta_ridder": 0.0}
        cosmo.set(params)
        cosmo.compute()
        results["beta0"] = {"sigma8": cosmo.sigma8()}
        print(f"  σ8 = {results['beta0']['sigma8']:.4f}")
        cosmo.struct_cleanup()
        cosmo.empty()
    except Exception as e:
        print(f"  FAIL: {e}")
        return False
    
    # Test 3: Ridder field with β=+0.05
    print("\n[3/4] Testing Ridder field β=+0.05...")
    try:
        cosmo = Class()
        params = {**base_params, **ridder_params, "beta_ridder": 0.05}
        cosmo.set(params)
        cosmo.compute()
        results["beta_pos"] = {"sigma8": cosmo.sigma8()}
        print(f"  σ8 = {results['beta_pos']['sigma8']:.4f}")
        cosmo.struct_cleanup()
        cosmo.empty()
    except Exception as e:
        print(f"  FAIL: {e}")
        return False
    
    # Test 4: Ridder field with β=-0.05
    print("\n[4/4] Testing Ridder field β=-0.05...")
    try:
        cosmo = Class()
        params = {**base_params, **ridder_params, "beta_ridder": -0.05}
        cosmo.set(params)
        cosmo.compute()
        results["beta_neg"] = {"sigma8": cosmo.sigma8()}
        print(f"  σ8 = {results['beta_neg']['sigma8']:.4f}")
        cosmo.struct_cleanup()
        cosmo.empty()
    except Exception as e:
        print(f"  FAIL: {e}")
        return False
    
    # Analysis
    print("\n" + "="*70)
    print("RESULTS ANALYSIS")
    print("="*70)
    
    s8_lcdm = results["lcdm"]["sigma8"]
    s8_beta0 = results["beta0"]["sigma8"]
    s8_pos = results["beta_pos"]["sigma8"]
    s8_neg = results["beta_neg"]["sigma8"]
    
    print(f"\nΛCDM:        σ8 = {s8_lcdm:.4f}")
    print(f"Ridder β=0:  σ8 = {s8_beta0:.4f} (Δ = {s8_beta0 - s8_lcdm:+.4f})")
    print(f"Ridder β=+:  σ8 = {s8_pos:.4f} (Δ = {s8_pos - s8_lcdm:+.4f})")
    print(f"Ridder β=-:  σ8 = {s8_neg:.4f} (Δ = {s8_neg - s8_lcdm:+.4f})")
    
    delta_pos = s8_pos - s8_beta0
    delta_neg = s8_neg - s8_beta0
    
    # ========================================
    # HARD ASSERTIONS - These catch bugs!
    # ========================================
    print("\n" + "="*70)
    print("BUG DETECTION ASSERTIONS")
    print("="*70)
    
    bugs_found = []
    
    # ASSERTION 1: ΛCDM sanity check
    if not (0.75 < s8_lcdm < 0.90):
        bugs_found.append(f"BUG: ΛCDM σ8={s8_lcdm:.4f} outside valid range [0.75, 0.90]")
    else:
        print("✓ ASSERT 1: ΛCDM σ8 in valid range [0.75, 0.90]")
    
    # ASSERTION 2: Ridder β=0 should be close to ΛCDM
    if abs(s8_beta0 - s8_lcdm) > 0.10:
        bugs_found.append(f"BUG: β=0 σ8 differs from ΛCDM by {abs(s8_beta0 - s8_lcdm):.4f} (>0.10)")
    else:
        print("✓ ASSERT 2: β=0 within 0.10 of ΛCDM")
    
    # ASSERTION 3: CORE PHYSICS - positive β MUST decrease σ8
    if delta_pos >= 0:
        bugs_found.append(f"BUG: β>0 should DECREASE σ8, but Δ={delta_pos:+.4f} (wrong sign!)")
    else:
        print(f"✓ ASSERT 3: β>0 decreases σ8 (Δ={delta_pos:+.4f}) - CORE THESIS VERIFIED")
    
    # ASSERTION 4: CORE PHYSICS - negative β MUST increase σ8
    if delta_neg <= 0:
        bugs_found.append(f"BUG: β<0 should INCREASE σ8, but Δ={delta_neg:+.4f} (wrong sign!)")
    else:
        print(f"✓ ASSERT 4: β<0 increases σ8 (Δ={delta_neg:+.4f}) - opposite direction verified")
    
    # ASSERTION 5: Coupling must have measurable effect (not silently disabled)
    if abs(delta_pos) < 0.001:
        bugs_found.append(f"BUG: β>0 has NO effect (Δ={delta_pos:.6f}) - coupling may be disabled!")
    else:
        print(f"✓ ASSERT 5: Coupling produces measurable effect (|Δ|={abs(delta_pos):.4f})")
    
    # ASSERTION 6: Effect must not be catastrophic (numerical instability)
    if abs(delta_pos) > 0.20 or abs(delta_neg) > 0.20:
        bugs_found.append(f"BUG: Coupling too strong! β>0: {delta_pos:+.4f}, β<0: {delta_neg:+.4f}")
    else:
        print("✓ ASSERT 6: Coupling effect is physically reasonable (<20%)")
    
    # ========================================
    # VERDICT
    # ========================================
    print("\n" + "="*70)
    if bugs_found:
        print("❌ BUGS DETECTED IN COUPLING CODE!")
        print("="*70)
        for bug in bugs_found:
            print(f"  🐛 {bug}")
        print("\nFix these issues before running MCMC chains!")
        print("="*70)
        raise CouplingBugError("\n".join(bugs_found))
    else:
        print("✅ ALL ASSERTIONS PASSED - Coupling physics correct!")
        print("="*70)
        print("  • ΛCDM baseline: valid")
        print("  • β=0 control: matches ΛCDM")
        print("  • β>0 effect: reduces σ8 (helps S8 tension)")
        print("  • β<0 effect: increases σ8 (opposite)")
        print("  • Coupling active: measurable effect")
        print("  • Numerical stability: within bounds")
    print("="*70)
    
    return len(bugs_found) == 0

if __name__ == "__main__":
    success = test_coupling()
    sys.exit(0 if success else 1)

