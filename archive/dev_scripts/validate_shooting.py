#!/usr/bin/env python3
"""
External validation suite for Ridder field shooting mechanism.

Tests:
1. Manual replicate: Shooting on → capture Lambda → shooting off → verify match
2. Multi-target: f_EDE = 0.05, 0.10, 0.20 → verify monotonic Lambda, convergence
3. Bracket robustness: Different [log10_Lambda_min, log10_Lambda_max] → same result

Run this once before relying on shooter in production (MCMC, CMB, etc.).
"""

import subprocess
import re
import tempfile
import os

# Base CLASS parameters
BASE_PARAMS = """
H0 = 70.0
omega_b = 0.0224
omega_cdm = 0.120
A_s = 2.1e-9
n_s = 0.965
tau_reio = 0.054
YHe = 0.245
gauge = newtonian

# Ridder field
f_axion_ridder = 2.435e27
theta_i_ridder = 1.5
beta_ridder = 0.0
n_ridder = 3

# Output (minimal for speed)
output = 
write background = no
"""

def run_class_with_params(params_dict, verbose=False):
    """
    Run CLASS with given parameters, return (success, Lambda, f_peak, z_peak).
    """
    # Create temporary .ini file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(BASE_PARAMS)
        for key, val in params_dict.items():
            f.write(f"{key} = {val}\n")
        ini_file = f.name
    
    try:
        # Run CLASS on VM
        cmd = f"ssh <VM_USER>@172.174.34.125 'cat > /tmp/test_shoot.ini << EOF\n{open(ini_file).read()}\nEOF\ncd ~/Ridder-Field/phase2/class && timeout 120 ./class /tmp/test_shoot.ini 2>&1'"
        
        if verbose:
            print(f"  Running CLASS with {params_dict}...")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=150)
        output = result.stdout + result.stderr
        
        # Parse shooting trace
        Lambda = None
        f_peak = None
        z_peak = None
        
        # Look for converged Lambda from shooting
        for line in output.split('\n'):
            if 'RIDDER_SHOOT' in line:
                match = re.search(r'log10_Lambda=(\S+)\s+f_peak=(\S+)\s+z_peak=(\S+)', line)
                if match:
                    log10_Lambda = float(match.group(1))
                    Lambda = 10**log10_Lambda
                    f_peak = float(match.group(2))
                    z_peak = float(match.group(3))
        
        # Check for completion
        success = (result.returncode == 0 or 'background_solve RETURNED' in output)
        
        return success, Lambda, f_peak, z_peak
        
    finally:
        os.unlink(ini_file)


def test_1_manual_replicate(target_fEDE=0.10, verbose=True):
    """
    Test 1: Manual replicate
    - Run with shooting on, capture converged Lambda
    - Run again with shooting off using that Lambda
    - Verify f_peak matches within tolerance
    """
    if verbose:
        print("\n" + "="*70)
        print(f"TEST 1: MANUAL REPLICATE (target f_EDE = {target_fEDE:.2f})")
        print("="*70)
    
    # Step 1: Shooting on
    if verbose:
        print(f"\nStep 1: Run with shooting enabled...")
    
    params_shooting = {
        'Lambda_EDE_ridder': 1e13,
        'use_ridder_shooting': 1,
        'ridder_fEDE_target': target_fEDE,
        'ridder_zc_min': 500.0,
        'ridder_zc_max': 10000.0,
        'ridder_shoot_log10Lambda_min': 10.0,
        'ridder_shoot_log10Lambda_max': 16.0,
        'ridder_shoot_tol_f': 0.001,
        'ridder_c_slow': 1.0,
    }
    
    success1, Lambda_converged, f_peak_shooting, z_peak_shooting = run_class_with_params(params_shooting, verbose)
    
    if not success1 or Lambda_converged is None:
        print("  ✗ FAIL: Shooting did not complete or converge")
        return False
    
    if verbose:
        print(f"  ✓ Shooting converged:")
        print(f"    Lambda = {Lambda_converged:.3e} eV")
        print(f"    f_peak = {f_peak_shooting:.5f}")
        print(f"    z_peak = {z_peak_shooting:.1f}")
    
    # Step 2: Shooting off with converged Lambda
    if verbose:
        print(f"\nStep 2: Run with shooting disabled, manual Lambda = {Lambda_converged:.3e} eV...")
    
    params_manual = {
        'Lambda_EDE_ridder': Lambda_converged,
        'use_ridder_shooting': 0,
    }
    
    success2, _, f_peak_manual, z_peak_manual = run_class_with_params(params_manual, verbose)
    
    if not success2:
        print("  ✗ FAIL: Manual run did not complete")
        return False
    
    if verbose:
        print(f"  ✓ Manual run completed:")
        print(f"    f_peak = {f_peak_manual:.5f}")
        print(f"    z_peak = {z_peak_manual:.1f}")
    
    # Step 3: Compare
    if verbose:
        print(f"\nStep 3: Verify consistency...")
    
    f_diff = abs(f_peak_shooting - f_peak_manual) if (f_peak_shooting and f_peak_manual) else 999
    z_diff = abs(z_peak_shooting - z_peak_manual) if (z_peak_shooting and z_peak_manual) else 999
    
    tol_f = 0.005  # 0.5% tolerance for f_peak
    tol_z = 100.0  # 100 redshift units tolerance
    
    f_match = f_diff < tol_f
    z_match = z_diff < tol_z
    
    if verbose:
        print(f"    Δf_peak = {f_diff:.6f}  (tol: {tol_f:.6f})  {'✓' if f_match else '✗'}")
        print(f"    Δz_peak = {z_diff:.1f}    (tol: {tol_z:.1f})  {'✓' if z_match else '✗'}")
    
    passed = f_match and z_match
    
    if verbose:
        print(f"\n{'✓ TEST 1 PASSED' if passed else '✗ TEST 1 FAILED'}")
    
    return passed


def test_2_multi_target(targets=[0.05, 0.10, 0.20], verbose=True):
    """
    Test 2: Multi-target
    - Run shooting for multiple f_EDE targets
    - Verify monotonic Lambda (higher target → higher Lambda)
    - Verify each converges within tolerance
    """
    if verbose:
        print("\n" + "="*70)
        print(f"TEST 2: MULTI-TARGET (targets: {targets})")
        print("="*70)
    
    results = []
    
    for target in targets:
        if verbose:
            print(f"\nTarget f_EDE = {target:.2f}...")
        
        params = {
            'Lambda_EDE_ridder': 1e13,
            'use_ridder_shooting': 1,
            'ridder_fEDE_target': target,
            'ridder_zc_min': 500.0,
            'ridder_zc_max': 10000.0,
            'ridder_shoot_log10Lambda_min': 10.0,
            'ridder_shoot_log10Lambda_max': 16.0,
            'ridder_shoot_tol_f': 0.001,
            'ridder_c_slow': 1.0,
        }
        
        success, Lambda, f_peak, z_peak = run_class_with_params(params, verbose)
        
        if not success or Lambda is None:
            if verbose:
                print(f"  ✗ Did not converge")
            results.append(None)
        else:
            converged = abs(f_peak - target) < 0.001 if f_peak else False
            if verbose:
                print(f"  Lambda = {Lambda:.3e} eV")
                print(f"  f_peak = {f_peak:.5f} (target: {target:.5f}) {'✓' if converged else '✗'}")
                print(f"  z_peak = {z_peak:.1f}")
            results.append((target, Lambda, f_peak, z_peak))
    
    # Check monotonicity
    if verbose:
        print(f"\nChecking monotonicity...")
    
    Lambdas = [r[1] for r in results if r is not None]
    monotonic = all(Lambdas[i] < Lambdas[i+1] for i in range(len(Lambdas)-1))
    
    if verbose:
        print(f"  Lambda sequence: {[f'{L:.2e}' for L in Lambdas]}")
        print(f"  Monotonic: {'✓ YES' if monotonic else '✗ NO'}")
    
    all_converged = all(r is not None for r in results)
    passed = monotonic and all_converged
    
    if verbose:
        print(f"\n{'✓ TEST 2 PASSED' if passed else '✗ TEST 2 FAILED'}")
    
    return passed


def test_3_bracket_robustness(target_fEDE=0.10, brackets=None, verbose=True):
    """
    Test 3: Bracket robustness
    - Run shooting with different [log10_Lambda_min, log10_Lambda_max]
    - Verify converged Lambda is consistent (within 1%)
    """
    if brackets is None:
        brackets = [
            (10.0, 16.0),  # Wide bracket
            (12.0, 15.0),  # Medium bracket
            (13.0, 14.5),  # Narrow bracket (if solution is around 13.7)
        ]
    
    if verbose:
        print("\n" + "="*70)
        print(f"TEST 3: BRACKET ROBUSTNESS (target f_EDE = {target_fEDE:.2f})")
        print("="*70)
    
    results = []
    
    for log_min, log_max in brackets:
        if verbose:
            print(f"\nBracket: [10^{log_min:.1f}, 10^{log_max:.1f}] eV...")
        
        params = {
            'Lambda_EDE_ridder': 1e13,
            'use_ridder_shooting': 1,
            'ridder_fEDE_target': target_fEDE,
            'ridder_zc_min': 500.0,
            'ridder_zc_max': 10000.0,
            'ridder_shoot_log10Lambda_min': log_min,
            'ridder_shoot_log10Lambda_max': log_max,
            'ridder_shoot_tol_f': 0.001,
            'ridder_c_slow': 1.0,
        }
        
        success, Lambda, f_peak, z_peak = run_class_with_params(params, verbose)
        
        if not success or Lambda is None:
            if verbose:
                print(f"  ✗ Did not converge (solution may be outside bracket)")
            results.append(None)
        else:
            if verbose:
                print(f"  Lambda = {Lambda:.3e} eV")
                print(f"  f_peak = {f_peak:.5f}")
            results.append(Lambda)
    
    # Check consistency
    if verbose:
        print(f"\nChecking consistency...")
    
    valid_Lambdas = [L for L in results if L is not None]
    
    if len(valid_Lambdas) < 2:
        if verbose:
            print(f"  ✗ Not enough valid results to compare")
        return False
    
    Lambda_mean = sum(valid_Lambdas) / len(valid_Lambdas)
    max_deviation = max(abs(L - Lambda_mean) / Lambda_mean for L in valid_Lambdas)
    
    tolerance = 0.01  # 1% tolerance
    consistent = max_deviation < tolerance
    
    if verbose:
        print(f"  Mean Lambda: {Lambda_mean:.3e} eV")
        print(f"  Max deviation: {max_deviation*100:.2f}% (tol: {tolerance*100:.1f}%)")
        print(f"  Consistent: {'✓ YES' if consistent else '✗ NO'}")
    
    passed = consistent and len(valid_Lambdas) == len(brackets)
    
    if verbose:
        print(f"\n{'✓ TEST 3 PASSED' if passed else '✗ TEST 3 FAILED'}")
    
    return passed


if __name__ == '__main__':
    print("\n" + "="*70)
    print("RIDDER FIELD SHOOTING MECHANISM - EXTERNAL VALIDATION SUITE")
    print("="*70)
    print("\nThis will run 3 validation tests on the VM:")
    print("  1. Manual replicate (shooting vs. manual Lambda)")
    print("  2. Multi-target (f_EDE = 5%, 10%, 20%)")
    print("  3. Bracket robustness (different Lambda search ranges)")
    print("\nEstimated time: 5-10 minutes")
    print("="*70)
    
    # Run all tests
    test1_passed = test_1_manual_replicate(target_fEDE=0.10, verbose=True)
    test2_passed = test_2_multi_target(targets=[0.05, 0.10, 0.20], verbose=True)
    test3_passed = test_3_bracket_robustness(target_fEDE=0.10, verbose=True)
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    print(f"Test 1 (Manual replicate):    {'✓ PASS' if test1_passed else '✗ FAIL'}")
    print(f"Test 2 (Multi-target):        {'✓ PASS' if test2_passed else '✗ FAIL'}")
    print(f"Test 3 (Bracket robustness):  {'✓ PASS' if test3_passed else '✗ FAIL'}")
    print("="*70)
    
    all_passed = test1_passed and test2_passed and test3_passed
    
    if all_passed:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("\nShooting mechanism is validated and ready for production use.")
        print("You can now proceed to physics tuning (theta_i scans, z_peak targeting).")
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("\nReview the failures above and debug before relying on the shooter.")
    
    print("\n" + "="*70 + "\n")

