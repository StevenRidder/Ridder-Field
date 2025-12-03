#!/usr/bin/env python3
"""
Phase 2.2: Theta_i Parameter Scan with Proper Diagnostics

Fixed parameters:
- Lambda = 0.01655 eV (slope calibration)
- c_slow = 1.0 (standard slow-roll kick)
- damping = 1.0 (full KG)
- freeze = no

Variable:
- theta_i ∈ [0.5, 1.0, 1.5, 2.0, 2.5]

Goal: Map theta_i → (z_peak, f_peak) to understand which parameter controls what.
"""

import subprocess
import sys
import os
import json
from pathlib import Path

# Fixed from Phase 1 slope calibration
LAMBDA_FIXED = 0.01654817  # eV
C_SLOW_FIXED = 1.0
F_AXION = 2.435e27  # M_Pl in eV

def write_theta_scan_ini(theta_i, Lambda=LAMBDA_FIXED, c_slow=C_SLOW_FIXED,
                         output_dir="output", run_id=None):
    """Generate CLASS ini file for theta_i scan."""
    
    if run_id is None:
        run_id = f"theta_{theta_i:.4f}".replace('.', 'p')
    
    ini_content = f"""# Theta_i Scan: theta = {theta_i:.3f}
# Lambda = {Lambda:.6e} eV (fixed)
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

# Enable background output for diagnostic
output = tCl
write background = yes
k_output_values = 0.01
l_max_scalars = 2500

# Output naming
root = {output_dir}/{run_id}
"""
    
    ini_file = f"scan_theta_{run_id}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini_content)
    
    return ini_file, run_id

def run_class_with_diagnostic(ini_file, run_id, class_exe="./phase2/class/class",
                               diagnostic_script="./extract_ede_diagnostics.py",
                               z_min=50.0, timeout=300):
    """
    Run CLASS and extract EDE diagnostics.
    
    Returns:
        dict with: theta_i, Lambda, z_peak, f_peak, success, runtime, error
    """
    
    result = {
        'ini_file': ini_file,
        'run_id': run_id,
        'theta_i': None,
        'Lambda': None,
        'c_slow': None,
        'z_peak': None,
        'f_peak': None,
        'a_peak': None,
        'success': False,
        'runtime': None,
        'error': None,
        'background_file': None
    }
    
    # Extract parameters from ini file
    try:
        with open(ini_file, 'r') as f:
            content = f.read()
            import re
            theta_match = re.search(r'theta_i_ridder\s*=\s*([\d.e+-]+)', content)
            if theta_match:
                result['theta_i'] = float(theta_match.group(1))
            lambda_match = re.search(r'Lambda_EDE_ridder\s*=\s*([\d.e+-]+)', content)
            if lambda_match:
                result['Lambda'] = float(lambda_match.group(1))
            c_slow_match = re.search(r'ridder_c_slow\s*=\s*([\d.e+-]+)', content)
            if c_slow_match:
                result['c_slow'] = float(c_slow_match.group(1))
    except:
        pass
    
    # Run CLASS
    print(f"  Running CLASS for theta_i = {result['theta_i']:.3f}...", end='', flush=True)
    
    try:
        import time
        start = time.time()
        
        class_result = subprocess.run(
            [class_exe, ini_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        result['runtime'] = time.time() - start
        
        # Check if CLASS succeeded
        if class_result.returncode != 0:
            result['error'] = "CLASS failed"
            print(f" FAILED ({result['runtime']:.1f}s)")
            return result
        
        # Find background file (CLASS may add extra decimal places)
        # Try exact match first
        bg_file = f"output/{run_id}_background.dat"
        
        if not os.path.exists(bg_file):
            # Search for pattern match
            import glob
            pattern = f"output/{run_id.split('_')[0]}_*_background.dat"
            matches = glob.glob(pattern)
            if matches:
                bg_file = matches[0]  # Take first match
            else:
                result['error'] = f"Background file not found: {bg_file}"
                print(f" NO OUTPUT ({result['runtime']:.1f}s)")
                return result
        
        result['background_file'] = bg_file
        
        # Run diagnostic
        diag_result = subprocess.run(
            ['python3', diagnostic_script, bg_file, '--z-min', str(z_min)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if diag_result.returncode != 0:
            result['error'] = "Diagnostic extraction failed"
            print(f" DIAG FAILED ({result['runtime']:.1f}s)")
            return result
        
        # Parse diagnostic output (JSON)
        try:
            diag_data = json.loads(diag_result.stdout)
            result['f_peak'] = diag_data.get('f_peak')
            result['z_peak'] = diag_data.get('z_peak')
            result['a_peak'] = diag_data.get('a_peak')
            result['success'] = True
            print(f" OK ({result['runtime']:.1f}s)")
        except json.JSONDecodeError:
            result['error'] = "Could not parse diagnostic JSON"
            print(f" PARSE FAILED ({result['runtime']:.1f}s)")
            return result
        
        return result
        
    except subprocess.TimeoutExpired:
        result['error'] = f"Timeout after {timeout}s"
        print(f" TIMEOUT")
        return result
    except Exception as e:
        result['error'] = str(e)
        print(f" ERROR: {e}")
        return result

def theta_i_scan(theta_values, output_json="scan_theta_i_results.json",
                 Lambda=LAMBDA_FIXED, c_slow=C_SLOW_FIXED, z_min=50.0):
    """
    Run theta_i parameter scan with proper diagnostics.
    
    Args:
        theta_values: list of theta_i values to scan
        output_json: where to save results
        Lambda: fixed Lambda value (from Phase 1 calibration)
        c_slow: fixed c_slow value
        z_min: minimum redshift for EDE peak search
    """
    
    print("=" * 70)
    print("Phase 2.2: Theta_i Parameter Scan (Proper Diagnostics)")
    print("=" * 70)
    print(f"Fixed parameters:")
    print(f"  Lambda = {Lambda:.6e} eV (from Phase 1 slope calibration)")
    print(f"  c_slow = {c_slow:.3f}")
    print(f"  damping = 1.0 (full Klein-Gordon)")
    print(f"  freeze = no")
    print(f"")
    print(f"Scanning theta_i: {theta_values}")
    print(f"EDE diagnostic: z > {z_min}, reading full CLASS background table")
    print()
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    results = []
    
    print(f"{'Theta_i':<10} {'z_peak':<12} {'f_peak':<12} {'a_peak':<12} {'Time':<8} {'Status':<10}")
    print("-" * 70)
    
    for theta in theta_values:
        # Generate ini file
        ini_file, run_id = write_theta_scan_ini(theta, Lambda=Lambda, c_slow=c_slow)
        
        # Run CLASS and extract diagnostics
        result = run_class_with_diagnostic(ini_file, run_id, z_min=z_min)
        results.append(result)
        
        # Format output
        theta_str = f"{theta:.3f}"
        
        if result['success']:
            z_str = f"{result['z_peak']:.1f}" if result['z_peak'] < 10000 else f"{result['z_peak']:.1e}"
            f_str = f"{result['f_peak']:.6f}"
            a_str = f"{result['a_peak']:.3e}"
            time_str = f"{result['runtime']:.1f}s"
            status = "✓ OK"
        else:
            z_str = "N/A"
            f_str = "N/A"
            a_str = "N/A"
            time_str = f"{result['runtime']:.1f}s" if result['runtime'] else "N/A"
            status = result['error'] or "✗ FAIL"
        
        print(f"{theta_str:<10} {z_str:<12} {f_str:<12} {a_str:<12} {time_str:<8} {status:<10}")
    
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
    
    successful = [r for r in results if r['success']]
    
    if not successful:
        print("No successful runs!")
        return results
    
    print(f"\nSuccessful runs: {len(successful)}/{len(results)}")
    print()
    
    # Check for patterns
    print("Pattern Analysis:")
    print()
    
    # Sort by theta_i
    successful.sort(key=lambda x: x['theta_i'])
    
    z_values = [r['z_peak'] for r in successful]
    f_values = [r['f_peak'] for r in successful]
    
    z_min_val, z_max_val = min(z_values), max(z_values)
    f_min_val, f_max_val = min(f_values), max(f_values)
    
    z_range = z_max_val - z_min_val
    f_range = f_max_val - f_min_val
    
    print(f"z_peak range: {z_min_val:.1f} to {z_max_val:.1f} (span: {z_range:.1f})")
    print(f"f_peak range: {f_min_val:.6f} to {f_max_val:.6f} (span: {f_range:.6f})")
    print()
    
    # Classify behavior
    if z_range < 100:
        print("→ z_peak is INSENSITIVE to theta_i (range < 100)")
        print("  Interpretation: Effective mass or Lambda sets timing, not theta_i")
        print("  Next step: Vary Lambda to push z_peak higher")
    elif z_range > 1000:
        print("→ z_peak is VERY SENSITIVE to theta_i (range > 1000)")
        print("  Interpretation: theta_i strongly controls onset time")
        print("  Next step: Fine-tune theta_i to target z~3000")
    else:
        print("→ z_peak shows MODERATE sensitivity to theta_i")
        print("  Interpretation: theta_i matters, but may need Lambda adjustment too")
    
    print()
    
    if f_range / f_min_val > 2.0:
        print("→ f_peak varies by >2x across theta_i")
        print("  Interpretation: theta_i also controls amplitude significantly")
    else:
        print("→ f_peak is relatively stable across theta_i")
        print("  Interpretation: Amplitude mostly set by Lambda")
    
    print()
    
    # Find best match to target (z > 1000, f ~ 0.05)
    target_z = 2000.0
    target_f = 0.05
    
    print(f"Target EDE regime: z_peak ~ {target_z:.0f}, f_peak ~ {target_f:.2f}")
    print()
    
    for r in successful:
        z_err = abs(r['z_peak'] - target_z) / target_z
        f_err = abs(r['f_peak'] - target_f) / target_f
        r['score'] = z_err + f_err
    
    successful.sort(key=lambda x: x['score'])
    
    best = successful[0]
    print(f"Closest configuration:")
    print(f"  theta_i = {best['theta_i']:.3f}")
    print(f"  z_peak = {best['z_peak']:.1f} (target: {target_z:.0f})")
    print(f"  f_peak = {best['f_peak']:.4f} (target: {target_f:.2f})")
    
    if best['z_peak'] < 500:
        print()
        print("⚠️  ALL configurations peak at z < 500 (late dark energy regime)")
        print("    This is NOT early dark energy!")
        print()
        print("Recommendation:")
        print("  1. Increase Lambda by factor of 10-100 to boost early-time energy")
        print("  2. OR change potential shape (decrease f_axion, increase n)")
        print("  3. Repeat theta_i scan with new parameters")
    elif best['z_peak'] > 10000:
        print()
        print("⚠️  Peak at z > 10000 may be too early (before recombination)")
        print()
        print("Recommendation:")
        print("  1. Decrease Lambda or adjust theta_i downward")
        print("  2. Target z ~ 2000-5000 for H0-relevant EDE")
    else:
        print()
        print("✓ Peak redshift in reasonable range for EDE!")
        print()
        if best['f_peak'] < 0.02:
            print("  But f_peak too small - consider increasing Lambda")
        elif best['f_peak'] > 0.15:
            print("  But f_peak too large - may overdo H0 shift")
        else:
            print("  And amplitude in viable range - good starting point!")
    
    print()
    print("=" * 70)
    print("Scan Complete!")
    print("=" * 70)
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 2.2: Theta_i Parameter Scan")
    parser.add_argument('--theta-values', nargs='+', type=float,
                        default=[0.5, 1.0, 1.5, 2.0, 2.5],
                        help='Theta_i values to scan (default: 0.5 1.0 1.5 2.0 2.5)')
    parser.add_argument('--lambda-fixed', type=float, default=LAMBDA_FIXED,
                        help=f'Fixed Lambda value in eV (default: {LAMBDA_FIXED:.6e})')
    parser.add_argument('--c-slow', type=float, default=C_SLOW_FIXED,
                        help=f'Fixed c_slow value (default: {C_SLOW_FIXED})')
    parser.add_argument('--z-min', type=float, default=50.0,
                        help='Minimum z for EDE peak search (default: 50)')
    parser.add_argument('--output', type=str, default='scan_theta_i_results.json',
                        help='Output JSON file')
    parser.add_argument('--class-exe', type=str, default='./phase2/class/class',
                        help='Path to CLASS executable')
    
    args = parser.parse_args()
    
    # Check CLASS
    if not os.path.exists(args.class_exe):
        print(f"ERROR: CLASS executable not found: {args.class_exe}")
        sys.exit(1)
    
    # Run scan
    results = theta_i_scan(
        theta_values=args.theta_values,
        output_json=args.output,
        Lambda=args.lambda_fixed,
        c_slow=args.c_slow,
        z_min=args.z_min
    )
    
    return 0 if any(r['success'] for r in results) else 1

if __name__ == '__main__':
    sys.exit(main())

