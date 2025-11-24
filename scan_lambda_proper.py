#!/usr/bin/env python3
"""
Lambda Scan at Fixed Theta_i

Fixed: theta_i = 1.5, c_slow = 1.0
Variable: Lambda ∈ [0.01655 × (1, 3, 10, 30, 100)] eV

Goal: Empirically demonstrate that Lambda moves z_peak to higher redshift
"""

import subprocess
import sys
import os
import json
from pathlib import Path

THETA_FIXED = 1.5
C_SLOW_FIXED = 1.0
F_AXION = 2.435e27
LAMBDA_BASE = 0.01654817  # eV, from Phase 1

def write_lambda_scan_ini(Lambda, theta_i=THETA_FIXED, c_slow=C_SLOW_FIXED,
                          output_dir="output", run_id=None):
    """Generate CLASS ini file for Lambda scan."""
    
    if run_id is None:
        run_id = f"lambda_{Lambda:.3e}".replace('.', 'p').replace('+', 'p').replace('-', 'm')
    
    ini_content = f"""# Lambda Scan: Lambda = {Lambda:.6e} eV
# theta_i = {theta_i:.3f} (fixed)
# c_slow = {c_slow:.3f} (fixed)

H0 = 67.36
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544
YHe = 0.2454
gauge = newtonian

# Ridder field
Lambda_EDE_ridder = {Lambda:.6e}
f_axion_ridder = {F_AXION:.6e}
theta_i_ridder = {theta_i:.6f}
beta_ridder = 0.0
n_ridder = 3
ridder_c_slow = {c_slow:.6f}

# Full dynamics
ridder_freeze_phi = no
ridder_force_damping = 1.0
use_ridder_shooting = 0

# Enable background output
output = tCl
write background = yes
k_output_values = 0.01
l_max_scalars = 2500

root = {output_dir}/{run_id}
"""
    
    ini_file = f"scan_lambda_{run_id}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini_content)
    
    return ini_file, run_id

def lambda_scan(lambda_multipliers, base_lambda=LAMBDA_BASE, theta_i=THETA_FIXED,
                output_json="scan_lambda_results.json", z_min=1.0):
    """Run Lambda parameter scan."""
    
    print("=" * 70)
    print("Lambda Scan at Fixed Theta_i")
    print("=" * 70)
    print(f"Fixed parameters:")
    print(f"  theta_i = {theta_i:.3f}")
    print(f"  c_slow = {C_SLOW_FIXED:.3f}")
    print(f"  Base Lambda = {base_lambda:.6e} eV")
    print(f"")
    print(f"Scanning Lambda: base × {lambda_multipliers}")
    print(f"EDE diagnostic: z > {z_min}")
    print()
    
    os.makedirs("output", exist_ok=True)
    
    results = []
    
    print(f"{'Multiplier':<12} {'Lambda/eV':<14} {'z_peak':<12} {'f_peak':<12} {'Time':<8} {'Status':<10}")
    print("-" * 75)
    
    for mult in lambda_multipliers:
        Lambda = base_lambda * mult
        
        # Generate ini
        ini_file, run_id = write_lambda_scan_ini(Lambda, theta_i=theta_i)
        
        print(f"{mult:<12.1f} {Lambda:<14.6e} ", end='', flush=True)
        
        result = {
            'multiplier': mult,
            'Lambda': Lambda,
            'theta_i': theta_i,
            'z_peak': None,
            'f_peak': None,
            'a_peak': None,
            'success': False,
            'runtime': None,
            'error': None
        }
        
        # Run CLASS
        try:
            import time
            start = time.time()
            
            class_result = subprocess.run(
                ['./phase2/class/class', ini_file],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            result['runtime'] = time.time() - start
            
            if class_result.returncode != 0:
                result['error'] = "CLASS failed"
                print(f"{'N/A':<12} {'N/A':<12} {result['runtime']:.1f}s   FAILED")
                results.append(result)
                continue
            
            # Find background file
            import glob
            bg_files = glob.glob(f"output/{run_id}*_background.dat")
            
            if not bg_files:
                result['error'] = "No background file"
                print(f"{'N/A':<12} {'N/A':<12} {result['runtime']:.1f}s   NO OUTPUT")
                results.append(result)
                continue
            
            bg_file = bg_files[0]
            
            # Extract diagnostic
            diag_result = subprocess.run(
                ['python3', './extract_ede_diagnostics.py', bg_file, 
                 '--z-min', str(z_min), '--z-max', '1000000'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if diag_result.returncode != 0:
                result['error'] = "Diagnostic failed"
                print(f"{'N/A':<12} {'N/A':<12} {result['runtime']:.1f}s   DIAG FAIL")
                results.append(result)
                continue
            
            # Parse JSON
            try:
                diag_data = json.loads(diag_result.stdout)
                result['z_peak'] = diag_data['z_peak']
                result['f_peak'] = diag_data['f_peak']
                result['a_peak'] = diag_data['a_peak']
                result['success'] = True
                
                z_str = f"{result['z_peak']:.1f}" if result['z_peak'] < 1e4 else f"{result['z_peak']:.1e}"
                f_str = f"{result['f_peak']:.4f}"
                
                print(f"{z_str:<12} {f_str:<12} {result['runtime']:.1f}s   ✓ OK")
                
            except:
                result['error'] = "Parse failed"
                print(f"{'N/A':<12} {'N/A':<12} {result['runtime']:.1f}s   PARSE FAIL")
            
            results.append(result)
            
        except subprocess.TimeoutExpired:
            result['error'] = "Timeout"
            print(f"{'N/A':<12} {'N/A':<12} N/A      TIMEOUT")
            results.append(result)
        except Exception as e:
            result['error'] = str(e)
            print(f"{'N/A':<12} {'N/A':<12} N/A      ERROR")
            results.append(result)
    
    # Save
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
    
    if not successful:
        print("No successful runs!")
        return results
    
    print(f"\nSuccessful runs: {len(successful)}/{len(results)}")
    print()
    
    # Check Lambda → z_peak relationship
    successful.sort(key=lambda x: x['Lambda'])
    
    print("Lambda Effect on Timing:")
    for r in successful:
        z = r['z_peak']
        f = r['f_peak']
        mult = r['multiplier']
        z_str = f"{z:.1f}" if z < 1e4 else f"{z:.1e}"
        print(f"  Λ × {mult:>4.0f} → z_peak = {z_str:>10}, f_peak = {f:.4f}")
    
    print()
    
    # Check if z_peak increases with Lambda
    z_values = [r['z_peak'] for r in successful]
    if len(z_values) >= 2:
        z_min_scan, z_max_scan = min(z_values), max(z_values)
        z_range = z_max_scan - z_min_scan
        
        print(f"z_peak range: {z_min_scan:.1f} to {z_max_scan:.1f} (span: {z_range:.1f})")
        
        if z_range > 1000:
            print("→ Lambda STRONGLY affects z_peak (span > 1000)")
            print("  Empirically confirmed: Lambda controls timing!")
        elif z_range > 100:
            print("→ Lambda MODERATELY affects z_peak (span > 100)")
        else:
            print("→ Lambda has WEAK effect on z_peak in this range")
    
    print()
    
    # Find EDE regime
    ede_cases = [r for r in successful if r['z_peak'] > 1000]
    
    if ede_cases:
        print(f"✓ Found {len(ede_cases)} configurations in EDE regime (z > 1000):")
        for r in ede_cases:
            print(f"  Λ = {r['Lambda']:.3e} eV → z_peak = {r['z_peak']:.1f}, f_peak = {r['f_peak']:.4f}")
        print()
        print("Next step: Fine-tune theta_i at one of these Lambda values")
    else:
        print("⚠️  No configurations reached EDE regime (z > 1000)")
        if successful:
            best_z = max(z_values)
            print(f"  Best z_peak achieved: {best_z:.1f}")
            if best_z < 500:
                print("  Recommendation: Try even larger Lambda (×300, ×1000)")
    
    print()
    print("=" * 70)
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Lambda Parameter Scan")
    parser.add_argument('--multipliers', nargs='+', type=float,
                        default=[1.0, 3.0, 10.0, 30.0, 100.0],
                        help='Lambda multipliers to scan')
    parser.add_argument('--base-lambda', type=float, default=LAMBDA_BASE,
                        help=f'Base Lambda in eV (default: {LAMBDA_BASE:.6e})')
    parser.add_argument('--theta-i', type=float, default=THETA_FIXED,
                        help=f'Fixed theta_i (default: {THETA_FIXED})')
    parser.add_argument('--z-min', type=float, default=1.0,
                        help='Minimum z for peak search (default: 1.0)')
    parser.add_argument('--output', type=str, default='scan_lambda_results.json',
                        help='Output JSON file')
    
    args = parser.parse_args()
    
    results = lambda_scan(
        lambda_multipliers=args.multipliers,
        base_lambda=args.base_lambda,
        theta_i=args.theta_i,
        output_json=args.output,
        z_min=args.z_min
    )
    
    return 0 if any(r['success'] for r in results) else 1

if __name__ == '__main__':
    sys.exit(main())

