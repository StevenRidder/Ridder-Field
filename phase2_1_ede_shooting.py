#!/usr/bin/env python3
"""
Phase 2.1: EDE Shooting - First Real Physics

Goal: Turn theta_i = 1.5 slope configuration into controlled EDE bump

Strategy:
1. Fix Lambda = 0.01655 eV (from Phase 1 slope calibration)
2. Vary ridder_c_slow to control when field starts rolling
3. Extract f_EDE_peak and z_peak from each run
4. Target: f_peak ~ 0.05 at z ~ 3000-5000

This is the first step from "validation" to "physics exploration"
"""

import subprocess
import re
import sys
import os
import json
from pathlib import Path

# From Phase 1 calibrations
LAMBDA_SLOPE = 0.01654817  # eV, calibrated at theta=1.5
THETA_I_SLOPE = 1.5        # On descending slope of potential

def write_ede_test_ini(c_slow, Lambda=LAMBDA_SLOPE, theta_i=THETA_I_SLOPE, 
                       freeze=False, damping=1.0, output_path=None):
    """Generate ini file for EDE test."""
    if output_path is None:
        output_path = f"test_ede_cslow_{c_slow:.2e}.ini"
    
    freeze_str = "yes" if freeze else "no"
    
    ini_content = f"""# Phase 2.1: EDE Shooting Test
# c_slow = {c_slow:.3e}, theta_i = {theta_i:.3f}
# Lambda = {Lambda:.6e} eV (fixed from Phase 1)

H0 = 67.36
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544
YHe = 0.2454
gauge = newtonian

# Ridder field with EDE dynamics
Lambda_EDE_ridder = {Lambda:.6e}
f_axion_ridder = 2.435e27
theta_i_ridder = {theta_i:.6f}
beta_ridder = 0.0
n_ridder = 3

# EDE CONTROL: vary c_slow to tune onset
ridder_c_slow = {c_slow:.6e}

# Full Klein-Gordon dynamics
ridder_freeze_phi = {freeze_str}
ridder_force_damping = {damping:.6f}

# No shooting yet - manual parameter scan
use_ridder_shooting = 0

# Minimal output
output = 
write background = no
"""
    
    with open(output_path, 'w') as f:
        f.write(ini_content)
    
    return output_path

def run_and_extract_ede_metrics(ini_file, class_exe="./phase2/class/class", timeout=120):
    """
    Run CLASS and extract EDE diagnostics.
    
    Returns:
        dict with: c_slow, f_peak, z_peak, rho_ridder_evolution, success
    """
    metrics = {
        'ini_file': ini_file,
        'success': False,
        'runtime': None,
        'c_slow': None,
        'theta_i': None,
        'Lambda': None,
        'f_peak': None,
        'z_peak': None,
        'a_peak': None,
        'rho_history': [],  # List of (a, rho_ridder, rho_tot, f_ridder)
        'error': None
    }
    
    try:
        import time
        start_time = time.time()
        
        result = subprocess.run(
            [class_exe, ini_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        metrics['runtime'] = time.time() - start_time
        output = result.stdout + result.stderr
        
        # Extract parameters from ini file
        try:
            with open(ini_file, 'r') as f:
                content = f.read()
                c_slow_match = re.search(r'ridder_c_slow\s*=\s*([\d.e+-]+)', content)
                if c_slow_match:
                    metrics['c_slow'] = float(c_slow_match.group(1))
                theta_match = re.search(r'theta_i_ridder\s*=\s*([\d.e+-]+)', content)
                if theta_match:
                    metrics['theta_i'] = float(theta_match.group(1))
                lambda_match = re.search(r'Lambda_EDE_ridder\s*=\s*([\d.e+-]+)', content)
                if lambda_match:
                    metrics['Lambda'] = float(lambda_match.group(1))
        except:
            pass
        
        # Extract full rho_ridder history from debug output
        # Pattern: "RIDDER DEBUG (adding to rho_tot): a=X, rho_ridder=Y, rho_tot_after=Z"
        debug_pattern = r'RIDDER DEBUG.*a=([\d.e+-]+).*rho_ridder=([\d.e+-]+).*rho_tot_after=([\d.e+-]+)'
        matches = re.findall(debug_pattern, output)
        
        for a_str, rho_r_str, rho_tot_str in matches:
            a = float(a_str)
            rho_r = float(rho_r_str)
            rho_tot = float(rho_tot_str)
            
            if rho_tot > 0:
                f_r = rho_r / rho_tot
                metrics['rho_history'].append((a, rho_r, rho_tot, f_r))
        
        # Find peak f_ridder
        if metrics['rho_history']:
            f_values = [(entry[0], entry[3]) for entry in metrics['rho_history']]
            a_peak, f_peak = max(f_values, key=lambda x: x[1])
            
            metrics['f_peak'] = f_peak
            metrics['a_peak'] = a_peak
            metrics['z_peak'] = (1.0 / a_peak) - 1.0 if a_peak > 0 else None
        
        # Check success
        if "BG_INIT: background_solve OK" in output:
            metrics['success'] = True
        else:
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

def c_slow_ladder_scan(c_slow_values, output_json="phase2_1_results.json"):
    """
    Scan c_slow parameter to explore EDE bump behavior.
    
    Args:
        c_slow_values: list of c_slow values to test
        output_json: where to save results
    """
    
    print("=" * 70)
    print("Phase 2.1: EDE Shooting - c_slow Parameter Scan")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  Lambda = {LAMBDA_SLOPE:.6e} eV (fixed from Phase 1)")
    print(f"  theta_i = {THETA_I_SLOPE:.3f} rad (on descending slope)")
    print(f"  damping = 1.0 (full Klein-Gordon dynamics)")
    print(f"")
    print(f"Scanning {len(c_slow_values)} c_slow values: {c_slow_values}")
    print(f"")
    print("Goal: Find c_slow that gives f_EDE_peak ~ 0.05 at z ~ 3000")
    print()
    
    results = []
    
    print(f"{'c_slow':<12} {'f_peak':<12} {'z_peak':<12} {'Time':<8} {'Status':<12}")
    print("-" * 70)
    
    for c_slow in c_slow_values:
        ini_file = write_ede_test_ini(c_slow)
        metrics = run_and_extract_ede_metrics(ini_file)
        results.append(metrics)
        
        # Format output
        c_str = f"{c_slow:.3e}"
        f_str = f"{metrics['f_peak']:.6f}" if metrics['f_peak'] else "N/A"
        
        if metrics['z_peak'] is not None:
            if metrics['z_peak'] < 1000:
                z_str = f"{metrics['z_peak']:.1f}"
            else:
                z_str = f"{metrics['z_peak']:.1e}"
        else:
            z_str = "N/A"
        
        time_str = f"{metrics['runtime']:.1f}s" if metrics['runtime'] else "N/A"
        status = "OK" if metrics['success'] else (metrics['error'] or "FAIL")
        
        print(f"{c_str:<12} {f_str:<12} {z_str:<12} {time_str:<8} {status:<12}")
    
    # Save results
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print(f"Results saved to: {output_json}")
    print()
    
    # Analysis
    print("=" * 70)
    print("ANALYSIS:")
    print("=" * 70)
    
    successful = [r for r in results if r['success'] and r['f_peak'] is not None]
    
    if not successful:
        print("No successful runs with EDE peak data!")
        return results
    
    print(f"\nSuccessful runs: {len(successful)}/{len(results)}")
    
    # Find best match to target
    target_z = 3000.0
    target_f = 0.05
    
    print(f"\nTarget: f_peak ~ {target_f:.2f} at z ~ {target_z:.0f}")
    print()
    
    # Score each run by distance from target
    for r in successful:
        z_err = abs(r['z_peak'] - target_z) / target_z if r['z_peak'] else 999
        f_err = abs(r['f_peak'] - target_f) / target_f if r['f_peak'] else 999
        r['score'] = z_err + f_err  # Simple combined error
    
    successful.sort(key=lambda x: x['score'])
    
    print("Best matches (sorted by proximity to target):")
    print(f"{'Rank':<6} {'c_slow':<12} {'f_peak':<12} {'z_peak':<12} {'Score':<10}")
    print("-" * 60)
    
    for i, r in enumerate(successful[:5]):  # Top 5
        rank = f"#{i+1}"
        c_str = f"{r['c_slow']:.3e}" if r['c_slow'] is not None else "N/A"
        f_str = f"{r['f_peak']:.4f}" if r['f_peak'] is not None else "N/A"
        z_str = f"{r['z_peak']:.1f}" if (r['z_peak'] is not None and r['z_peak'] < 10000) else (f"{r['z_peak']:.1e}" if r['z_peak'] is not None else "N/A")
        score_str = f"{r['score']:.3f}"
        
        print(f"{rank:<6} {c_str:<12} {f_str:<12} {z_str:<12} {score_str:<10}")
    
    print()
    print("=" * 70)
    print("Phase 2.1 Scan Complete!")
    print()
    
    if successful:
        best = successful[0]
        print(f"Best configuration: c_slow = {best['c_slow']:.3e}")
        print(f"  → f_peak = {best['f_peak']:.4f}, z_peak = {best['z_peak']:.1f}")
        print()
        print("Next steps:")
        print("  1. If close to target: proceed to theta_i scan (Phase 2.2)")
        print("  2. If not close: adjust c_slow range and re-scan")
        print("  3. Eventually: 2D shooting on (Lambda, c_slow) or (Lambda, theta_i)")
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 2.1: EDE c_slow Parameter Scan")
    parser.add_argument('--c-slow-values', nargs='+', type=float,
                        default=[0.0, 0.1, 0.3, 1.0, 3.0, 10.0],
                        help='List of c_slow values to test')
    parser.add_argument('--class-exe', type=str, default='./phase2/class/class',
                        help='Path to CLASS executable')
    parser.add_argument('--output', type=str, default='phase2_1_results.json',
                        help='Output JSON file for results')
    
    args = parser.parse_args()
    
    # Check CLASS
    if not os.path.exists(args.class_exe):
        print(f"ERROR: CLASS executable not found: {args.class_exe}")
        sys.exit(1)
    
    # Run scan
    results = c_slow_ladder_scan(args.c_slow_values, args.output)
    
    return 0 if any(r['success'] for r in results) else 1

if __name__ == '__main__':
    sys.exit(main())

