#!/usr/bin/env python3
"""
Phase 1.2: Damping Continuity Test

Tests that ridder_force_damping smoothly interpolates between:
  - damping = 0.0: Frozen field (pure Λ behavior)
  - damping = 1.0: Full Klein-Gordon evolution

Using the calibrated Lambda_LCDM = 0.01655 eV from Phase 1.1A.
"""

import subprocess
import re
import sys
import os
from pathlib import Path
import json

# Calibrated Lambda from Phase 1.1A
LAMBDA_LCDM = 0.01654817  # eV, gives f_ridder ~ 0.69

def write_damping_test_ini(damping_value, freeze_flag=False, output_path=None):
    """Generate ini file for damping test."""
    if output_path is None:
        output_path = f"test_damping_{damping_value:.2f}.ini"
    
    freeze_str = "yes" if freeze_flag else "no"
    
    ini_content = f"""# Phase 1.2: Damping Continuity Test
# damping = {damping_value:.2f}, freeze = {freeze_str}
# Lambda = {LAMBDA_LCDM:.6e} eV (calibrated for Omega_Lambda ~ 0.69)

H0 = 67.36
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544
YHe = 0.2454
gauge = newtonian

# Ridder field with calibrated Lambda
Lambda_EDE_ridder = {LAMBDA_LCDM:.6e}
f_axion_ridder = 2.435e27
theta_i_ridder = 1.5
beta_ridder = 0.0
n_ridder = 3
ridder_c_slow = 0.0

# DAMPING TEST: vary force damping
ridder_freeze_phi = {freeze_str}
ridder_force_damping = {damping_value:.6f}

# No shooting - testing fixed configuration
use_ridder_shooting = 0

# Minimal output for speed
output = 
write background = no
"""
    
    with open(output_path, 'w') as f:
        f.write(ini_content)
    
    return output_path

def run_and_extract_metrics(ini_file, class_exe="./phase2/class/class", timeout=120):
    """
    Run CLASS and extract key metrics.
    
    Returns:
        dict with: damping, f_ridder_late, phi_initial, phi_final, success, runtime
    """
    import time
    
    metrics = {
        'ini_file': ini_file,
        'success': False,
        'runtime': None,
        'damping': None,
        'freeze': None,
        'f_ridder_late': None,
        'rho_ridder_late': None,
        'rho_tot_late': None,
        'phi_initial': None,
        'phi_final': None,
        'phi_prime_initial': None,
        'phi_prime_final': None,
        'error': None
    }
    
    try:
        start_time = time.time()
        result = subprocess.run(
            [class_exe, ini_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        runtime = time.time() - start_time
        metrics['runtime'] = runtime
        
        output = result.stdout + result.stderr
        
        # Extract damping and freeze settings from output
        damp_match = re.search(r'force_damping\s*=\s*([\d.e+-]+)', output)
        freeze_match = re.search(r'ridder_freeze_phi\s*=\s*(\d+)', output)
        if damp_match:
            metrics['damping'] = float(damp_match.group(1))
        if freeze_match:
            metrics['freeze'] = int(freeze_match.group(1))
        
        # Look for initial phi/phi_prime (first RIDDER EVOLVE or FREEZE line)
        init_pattern = r'(RIDDER EVOLVE|RIDDER FREEZE).*a=([\d.e+-]+).*phi=([\d.e+-]+).*phi_prime=([\d.e+-]+)'
        init_matches = re.findall(init_pattern, output)
        if init_matches:
            _, a_init, phi_init, phi_prime_init = init_matches[0]
            metrics['phi_initial'] = float(phi_init)
            metrics['phi_prime_initial'] = float(phi_prime_init)
        
        # Extract late-time values from debug output
        # Pattern: "RIDDER DEBUG (adding to rho_tot): a=X, rho_ridder=Y, rho_tot_after=Z"
        debug_pattern = r'RIDDER DEBUG.*a=([\d.e+-]+).*rho_ridder=([\d.e+-]+).*rho_tot_after=([\d.e+-]+)'
        matches = re.findall(debug_pattern, output)
        
        if matches:
            # Get last entry (closest to z=0)
            a_val, rho_ridder, rho_tot = matches[-1]
            a_val = float(a_val)
            rho_ridder = float(rho_ridder)
            rho_tot = float(rho_tot)
            
            metrics['rho_ridder_late'] = rho_ridder
            metrics['rho_tot_late'] = rho_tot
            
            if rho_tot > 0:
                metrics['f_ridder_late'] = rho_ridder / rho_tot
        
        # Look for final phi value (last EVOLVE/FREEZE line with large a)
        if init_matches:
            _, a_final, phi_final, phi_prime_final = init_matches[-1]
            metrics['phi_final'] = float(phi_final)
            metrics['phi_prime_final'] = float(phi_prime_final)
        
        # Check if run completed successfully (reached background_solve OK)
        if "BG_INIT: background_solve OK" in output:
            metrics['success'] = True
        else:
            # Extract error message
            error_match = re.search(r'Error in (\w+)', output)
            if error_match:
                metrics['error'] = error_match.group(0)
            else:
                metrics['error'] = "Unknown failure"
        
        return metrics
        
    except subprocess.TimeoutExpired:
        metrics['error'] = f"Timeout after {timeout}s"
        return metrics
    except Exception as e:
        metrics['error'] = str(e)
        return metrics

def run_damping_suite(damping_values, output_json="phase1_2_results.json"):
    """
    Run full damping continuity test suite.
    
    Args:
        damping_values: list of damping factors to test
        output_json: where to save results
    """
    
    print("=" * 70)
    print("Phase 1.2: Damping Continuity Test")
    print("=" * 70)
    print(f"Lambda_LCDM = {LAMBDA_LCDM:.6e} eV (calibrated for f_ridder ~ 0.69)")
    print(f"Testing {len(damping_values)} damping values: {damping_values}")
    print()
    
    results = []
    
    dphi_prime_label = "Δphi'"
    print(f"{'Damp':<8} {'Freeze':<8} {'f_ridder':<12} {'Δphi':<12} {dphi_prime_label:<12} {'Time':<8} {'Status':<12}")
    print("-" * 80)
    
    for damp in damping_values:
        # For damping=0, we can optionally test both freeze=on and freeze=off
        # They should give identical results
        test_freeze_modes = [False]
        if damp == 0.0:
            test_freeze_modes = [False, True]  # Test both modes at damp=0
        
        for freeze_mode in test_freeze_modes:
            ini_file = write_damping_test_ini(damp, freeze_flag=freeze_mode)
            metrics = run_and_extract_metrics(ini_file)
            results.append(metrics)
            
            # Calculate field evolution metrics
            delta_phi = None
            delta_phi_prime = None
            if metrics['phi_initial'] is not None and metrics['phi_final'] is not None:
                delta_phi = abs(metrics['phi_final'] - metrics['phi_initial'])
            if metrics['phi_prime_initial'] is not None and metrics['phi_prime_final'] is not None:
                delta_phi_prime = abs(metrics['phi_prime_final'] - metrics['phi_prime_initial'])
            
            # Format output
            damp_str = f"{damp:.2f}"
            freeze_str = "yes" if freeze_mode else "no"
            f_str = f"{metrics['f_ridder_late']:.6f}" if metrics['f_ridder_late'] else "N/A"
            dphi_str = f"{delta_phi:.3e}" if delta_phi is not None else "N/A"
            dphi_prime_str = f"{delta_phi_prime:.3e}" if delta_phi_prime is not None else "N/A"
            time_str = f"{metrics['runtime']:.1f}s" if metrics['runtime'] else "N/A"
            status = "OK" if metrics['success'] else (metrics['error'] or "FAIL")
            
            print(f"{damp_str:<8} {freeze_str:<8} {f_str:<12} {dphi_str:<12} {dphi_prime_str:<12} {time_str:<8} {status:<12}")
    
    # Save results to JSON
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print(f"Results saved to: {output_json}")
    print()
    
    # Analysis
    print("=" * 70)
    print("ANALYSIS:")
    print("=" * 70)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"Successful runs: {len(successful)}/{len(results)}")
    
    if failed:
        print(f"\nFailed runs: {len(failed)}")
        for r in failed:
            print(f"  damping={r['damping']:.2f}: {r['error']}")
    
    if len(successful) >= 2:
        print("\nContinuity Check:")
        f_values = [(r['damping'], r['f_ridder_late']) for r in successful if r['f_ridder_late'] is not None]
        f_values.sort()
        
        # Check that f_ridder doesn't vary too much (should be ~constant for frozen plateau)
        f_vals_only = [f for _, f in f_values]
        if f_vals_only:
            f_mean = sum(f_vals_only) / len(f_vals_only)
            f_std = (sum((f - f_mean)**2 for f in f_vals_only) / len(f_vals_only))**0.5
            
            print(f"  f_ridder: mean = {f_mean:.6f}, std = {f_std:.6f}")
            
            if f_std / f_mean < 0.05:  # Less than 5% variation
                print("  ✓ f_ridder is stable across damping values (field on plateau)")
            else:
                print("  ⚠ f_ridder varies significantly - may indicate field evolution")
        
        # Check runtime scaling
        print("\nPerformance:")
        for r in successful:
            if r['runtime']:
                print(f"  damping={r['damping']:.2f}: {r['runtime']:.1f}s")
    
    print()
    print("=" * 70)
    print("Phase 1.2 Complete!")
    print("=" * 70)
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 1.2: Damping Continuity Test")
    parser.add_argument('--damping-values', nargs='+', type=float,
                        default=[0.0, 0.1, 0.3, 0.5, 0.7, 1.0],
                        help='List of damping values to test (default: 0.0 0.1 0.3 0.5 0.7 1.0)')
    parser.add_argument('--class-exe', type=str, default='./phase2/class/class',
                        help='Path to CLASS executable')
    parser.add_argument('--output', type=str, default='phase1_2_results.json',
                        help='Output JSON file for results')
    
    args = parser.parse_args()
    
    # Check CLASS executable
    if not os.path.exists(args.class_exe):
        print(f"ERROR: CLASS executable not found: {args.class_exe}")
        sys.exit(1)
    
    # Run suite
    results = run_damping_suite(args.damping_values, args.output)
    
    # Determine exit code
    if any(not r['success'] for r in results):
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())

