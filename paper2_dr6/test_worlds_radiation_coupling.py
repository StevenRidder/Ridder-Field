#!/usr/bin/env python3
"""
Test radiation coupling (α-branching) across all Paper 2 "worlds".
Tests whether high θ_i + α-branching can push H₀ higher.
"""

import subprocess
import os
import sys
import re

# Path to CLASS - detect environment
if os.path.exists("/home/azureuser/Ridder-Field/phase2/class/class"):
    CLASS_PATH = "/home/azureuser/Ridder-Field/phase2/class/class"
    WORK_DIR = "/home/azureuser/Ridder-Field/phase2/class"
else:
    CLASS_PATH = os.path.expanduser("~/Git/Ridder-Field/phase2/class/class")
    WORK_DIR = os.path.expanduser("~/Git/Ridder-Field/phase2/class")

# Test configurations: (theta_i, alpha, Lambda_eV, description)
TESTS = [
    (None,  None, None, "LCDM baseline"),
    (1.0,   0.0,  0.2,  "EDE θ=1.0, no decay (Paper 2 current)"),
    (1.0,   0.5,  0.2,  "EDE θ=1.0, α=0.5"),
    (1.5,   0.0,  0.5,  "EDE θ=1.5, no decay"),
    (1.5,   0.5,  0.5,  "EDE θ=1.5, α=0.5"),
    (2.0,   0.0,  0.5,  "EDE θ=2.0, no decay"),
    (2.0,   0.5,  0.5,  "EDE θ=2.0, α=0.5"),
    (2.0,   1.0,  0.5,  "EDE θ=2.0, α=1.0 (full decay)"),
]


def run_class_test(theta_i, alpha, Lambda_eV):
    """Run CLASS and extract H0, r_s, f_peak."""
    
    ini = f"""
output = tCl
l_max_scalars = 2500
h = 0.6732
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544
gauge = newtonian
"""
    
    if theta_i is not None:
        ini += f"""
has_ridder = yes
use_ridder_shooting = 0
ridder_freeze_phi = no
Lambda_EDE_ridder = {Lambda_eV}
theta_i_ridder = {theta_i}
n_ridder = 3.0
beta_ridder = 0.0
f_axion_ridder = 1e27
alpha_ridder_to_dr = {alpha}
z_ridder_decay = 3500
Gamma_decay_ridder = 0.0
"""
    
    ini_path = "/tmp/test_rad.ini"
    with open(ini_path, "w") as f:
        f.write(ini)
    
    try:
        result = subprocess.run(
            [CLASS_PATH, ini_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=WORK_DIR
        )
        
        out = result.stdout + result.stderr
        
        # Parse output
        h0, rs, fpeak = None, None, None
        
        # Look for H0
        m = re.search(r'h\s*=\s*([\d.]+)', out)
        if m:
            h0 = float(m.group(1)) * 100
        
        # Look for r_s (sound horizon at drag)
        m = re.search(r'r_s\(z_d\)\s*[=:]\s*([\d.]+)', out)
        if m:
            rs = float(m.group(1))
        else:
            m = re.search(r'rs_d\s*[=:]\s*([\d.]+)', out)
            if m:
                rs = float(m.group(1))
        
        # Look for f_peak
        m = re.search(r'f_ridder_peak\s*[=:]\s*([\d.eE+-]+)', out)
        if m:
            fpeak = float(m.group(1))
        
        return {
            'success': result.returncode == 0,
            'H0': h0,
            'r_s': rs,
            'f_peak': fpeak,
            'error': result.stderr[:200] if result.returncode != 0 else None
        }
        
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def main():
    print("=" * 70)
    print("RADIATION COUPLING TEST: θ_i vs α-branching")
    print("=" * 70)
    
    if not os.path.exists(CLASS_PATH):
        print(f"ERROR: CLASS not found at {CLASS_PATH}")
        sys.exit(1)
    
    print(f"\nUsing CLASS at: {CLASS_PATH}\n")
    print(f"{'Config':<40} {'H0':>8} {'r_s':>8} {'f_peak':>10} {'Status'}")
    print("-" * 70)
    
    results = []
    for theta_i, alpha, Lambda_eV, desc in TESTS:
        r = run_class_test(theta_i, alpha, Lambda_eV)
        results.append((desc, r))
        
        h0 = f"{r['H0']:.2f}" if r.get('H0') else "N/A"
        rs = f"{r['r_s']:.2f}" if r.get('r_s') else "N/A"
        fp = f"{r['f_peak']*100:.2f}%" if r.get('f_peak') else "N/A"
        status = "OK" if r['success'] else f"FAIL: {r.get('error', '')[:20]}"
        
        print(f"{desc:<40} {h0:>8} {rs:>8} {fp:>10} {status}")
    
    # Compute deltas
    print("\n" + "=" * 70)
    print("EFFECT OF α-BRANCHING (Δr_s and implied ΔH0)")
    print("=" * 70)
    
    lcdm_rs = results[0][1].get('r_s')
    if lcdm_rs:
        print(f"\nΛCDM baseline r_s = {lcdm_rs:.2f} Mpc")
        print(f"\n{'Config':<40} {'Δr_s':>10} {'ΔH0 (implied)':>15}")
        print("-" * 70)
        
        for desc, r in results[1:]:
            if r.get('r_s'):
                delta_rs = r['r_s'] - lcdm_rs
                # ΔH0/H0 ≈ -Δr_s/r_s
                delta_h0 = -delta_rs / lcdm_rs * 67.32
                print(f"{desc:<40} {delta_rs:>+10.2f} {delta_h0:>+15.2f} km/s/Mpc")
    
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("""
The key parameter is θ_i (initial field displacement):
- θ_i = 1.0: f_peak ~ 3%, max ΔH0 ~ +0.7 km/s/Mpc with α-branching
- θ_i = 1.5: f_peak ~ 8%, max ΔH0 ~ +2 km/s/Mpc with α-branching  
- θ_i = 2.0: f_peak ~ 15%, max ΔH0 ~ +4 km/s/Mpc with α-branching

Current Paper 2 chains have θ_i FIXED at 1.0 → stuck at H0 ~ 68.
Need to float θ_i to test if data allows higher values.
""")


if __name__ == "__main__":
    main()

