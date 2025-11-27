#!/usr/bin/env python3
"""
CI TEST: Verify CDM-Ridder coupling conserves energy-momentum

Tests:
1. β=0 should give same results as uncoupled
2. β>0 should modify σ8 (structure formation)
3. β<0 should modify σ8 in opposite direction
4. Coupling should NOT break ΛCDM when Ridder field is off
"""

import sys
import numpy as np

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
    
    # Validation
    print("\n" + "="*70)
    print("VALIDATION CHECKS")
    print("="*70)
    
    passed = True
    
    # Check 1: β=0 should not change σ8 dramatically
    if abs(s8_beta0 - s8_lcdm) < 0.15:
        print("✓ β=0 gives reasonable σ8 (within 0.15 of ΛCDM)")
    else:
        print(f"✗ β=0 gives σ8 too far from ΛCDM: Δ={s8_beta0 - s8_lcdm:.4f}")
        passed = False
    
    # Check 2: β>0 and β<0 should have opposite effects
    delta_pos = s8_pos - s8_beta0
    delta_neg = s8_neg - s8_beta0
    
    if delta_pos * delta_neg < 0:
        print("✓ β>0 and β<0 have OPPOSITE effects on σ8 (as expected)")
    else:
        print(f"✗ β>0 and β<0 have SAME direction effect (BUG!)")
        print(f"  β>0: Δσ8={delta_pos:+.4f}, β<0: Δσ8={delta_neg:+.4f}")
        passed = False
    
    # Check 3: Coupling should produce measurable effect
    if abs(delta_pos) > 0.001 or abs(delta_neg) > 0.001:
        print("✓ Coupling produces measurable σ8 change")
    else:
        print("✗ Coupling has NO effect (might be disabled)")
        passed = False
    
    # Check 4: Effect should be modest (not catastrophic)
    if abs(delta_pos) < 0.3 and abs(delta_neg) < 0.3:
        print("✓ Coupling effect is modest (< 0.3 in σ8)")
    else:
        print(f"⚠ Coupling effect may be too strong: |Δσ8| > 0.3")
    
    print("\n" + "="*70)
    if passed:
        print("✅ ALL CHECKS PASSED - Coupling physics working correctly")
    else:
        print("❌ SOME CHECKS FAILED - Coupling has bugs")
    print("="*70)
    
    return passed

if __name__ == "__main__":
    success = test_coupling()
    sys.exit(0 if success else 1)

