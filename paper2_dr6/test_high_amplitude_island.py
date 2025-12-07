#!/usr/bin/env python3
"""
HIGH-AMPLITUDE ISLAND TEST

The Question: Does the data tolerate f_peak ≈ 5-10% with radiation decay?

If YES → H₀ ≈ 70-71 is achievable
If NO → The geometric ceiling is physics, not bugs

This script:
1. Runs background with varying Lambda to find f_peak ~ 8%
2. Compares r_s and H₀ with/without α-branching
3. Estimates ΔH₀ from the geometry
"""
import subprocess
import os
import re

CLASS = "/Users/steveridder/Git/Ridder-Field/phase2/class/class"
OUTPUT_DIR = "/Users/steveridder/Git/Ridder-Field/phase2/class/output"


def run_class_background(name, Lambda, alpha=0.0, gamma=0.0, verbose=False):
    """Run CLASS and extract key background quantities."""
    
    ini_content = f"""
root = {OUTPUT_DIR}/{name}
write background = yes

h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
tau_reio = 0.0544

Lambda_EDE_ridder = {Lambda}
f_axion_ridder = 1.0e+27
theta_i_ridder = 1.0
n_ridder = 3
beta_ridder = 0.0

alpha_ridder_to_dr = {alpha}
z_ridder_decay = 3500
Gamma_decay_ridder = {gamma}

ridder_force_damping = 1.0
ridder_freeze_phi = no
use_ridder_shooting = 0

output = 
background_verbose = 1
gauge = newtonian
"""
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(ini_content)
        ini_file = f.name
    
    try:
        result = subprocess.run([CLASS, ini_file], capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        
        if verbose:
            print(output[-2000:])  # Last 2000 chars
        
        # Parse output for key quantities
        parsed = {
            'success': result.returncode == 0,
            'f_peak': None,
            'rho_max': None,
            'a_max': None,
            'r_s': None,
        }
        
        # Look for our debug output
        for line in output.split('\n'):
            if 'PEAK UPDATE' in line:
                # Extract f_peak from peak update
                m = re.search(r'f_peak=([\d.e+-]+)', line)
                if m:
                    f_val = float(m.group(1))
                    if parsed['f_peak'] is None or f_val > parsed['f_peak']:
                        parsed['f_peak'] = f_val
                m = re.search(r'rho_max=([\d.e+-]+)', line)
                if m:
                    parsed['rho_max'] = float(m.group(1))
                m = re.search(r'a=([\d.e+-]+)', line)
                if m:
                    parsed['a_max'] = float(m.group(1))
            
            if 'RIDDER FINAL STATE' in line or 'f_ridder' in line.lower():
                m = re.search(r'f_ridder\s*[=:]\s*([\d.e+-]+)', line, re.I)
                if m:
                    parsed['f_peak'] = max(parsed['f_peak'] or 0, float(m.group(1)))
        
        # Get r_s from background file
        bg_file = f"{OUTPUT_DIR}/{name}00_background.dat"
        if os.path.exists(bg_file):
            with open(bg_file) as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.split()
                    if len(parts) > 7:
                        z = float(parts[0])
                        if 1090 < z < 1110:
                            parsed['r_s'] = float(parts[7])
                            break
        
        return parsed
        
    except Exception as e:
        print(f"Error: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        os.unlink(ini_file)


def main():
    print("=" * 70)
    print("HIGH-AMPLITUDE ISLAND TEST")
    print("=" * 70)
    print()
    print("Question: Does the data tolerate f_peak ≈ 5-10% with radiation decay?")
    print()
    
    # Step 1: Find Lambda that gives f_peak ~ 8%
    print("STEP 1: Finding Lambda for f_peak ≈ 8%")
    print("-" * 50)
    
    lambdas_to_test = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    
    print(f"{'Lambda (eV)':<15} {'f_peak (%)':<15} {'r_s (Mpc)':<15} {'Status':<10}")
    print("-" * 55)
    
    results = {}
    for L in lambdas_to_test:
        result = run_class_background(f"island_L{L:.1f}", L, alpha=0.0)
        f_peak = result.get('f_peak', 0) or 0
        r_s = result.get('r_s', 0)
        status = '✓' if result.get('success') else '✗'
        
        f_pct = f_peak * 100 if f_peak else 0
        r_s_str = f"{r_s:.2f}" if r_s else "N/A"
        
        print(f"{L:<15.1f} {f_pct:<15.4f} {r_s_str:<15} {status:<10}")
        results[L] = result
    
    # Find best Lambda for f_peak ~ 8%
    best_L = None
    best_diff = float('inf')
    target_f = 0.08
    for L, res in results.items():
        if res.get('success') and res.get('f_peak'):
            diff = abs(res['f_peak'] - target_f)
            if diff < best_diff:
                best_diff = diff
                best_L = L
    
    if best_L is None:
        # Default to 0.5 if we can't find optimal
        best_L = 0.5
        print(f"\nCouldn't determine optimal Lambda, using {best_L}")
    else:
        print(f"\nOptimal Lambda for f_peak ≈ 8%: {best_L} eV")
    
    # Step 2: Compare with/without α-branching at best Lambda
    print()
    print("STEP 2: Testing α-branching effect at high amplitude")
    print("-" * 50)
    
    configs = [
        ('Baseline (α=0)', 0.0, 0.0),
        ('α=0.3', 0.3, 0.0),
        ('α=0.5', 0.5, 0.0),
        ('α=1.0', 1.0, 0.0),
        ('Γ=2.0', 0.0, 2.0),
        ('Γ=4.0', 0.0, 4.0),
    ]
    
    print(f"Lambda = {best_L} eV")
    print()
    print(f"{'Config':<20} {'f_peak (%)':<12} {'r_s (Mpc)':<12} {'Δr_s (Mpc)':<12}")
    print("-" * 60)
    
    baseline_rs = None
    for name, alpha, gamma in configs:
        result = run_class_background(f"island_{name.replace('=','').replace('.','')}", 
                                      best_L, alpha=alpha, gamma=gamma)
        
        f_peak = result.get('f_peak', 0) or 0
        r_s = result.get('r_s')
        
        if baseline_rs is None and r_s:
            baseline_rs = r_s
        
        f_pct = f_peak * 100
        r_s_str = f"{r_s:.4f}" if r_s else "N/A"
        delta_rs = f"{r_s - baseline_rs:+.4f}" if r_s and baseline_rs else "N/A"
        
        print(f"{name:<20} {f_pct:<12.4f} {r_s_str:<12} {delta_rs:<12}")
    
    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()
    print("• If r_s decreases significantly with α-branching:")
    print("  → The geometry works! Run MCMC to check χ²")
    print()
    print("• If r_s barely changes:")
    print("  → Either f_peak is still too small, or there's an implementation issue")
    print()
    print("• Expected scaling: Δr_s/r_s ≈ -f_peak × ln(3501/1101) ≈ -f_peak × 1.16")
    print(f"  For f_peak = 8%, expect Δr_s ≈ -{0.08 * 1.16 * 140:.1f} Mpc = ~-13 Mpc")
    print()


if __name__ == "__main__":
    main()

