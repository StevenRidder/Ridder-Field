#!/usr/bin/env python3
"""
TRACK 1A: Pure Axion-EDE Test
Scan m and f to find configuration matching AxiCLASS benchmark:
- f_EDE ~ 0.13
- z_peak ~ 3400
"""

import subprocess
import os
import sys

# M_Pl in eV
M_PL_EV = 2.435e27

# AxiCLASS target
TARGET_F_EDE = 0.13  # 13%
TARGET_Z_PEAK = 3400

INI_TEMPLATE = """
H0 = 72.81
omega_b = 0.02251
omega_cdm = 0.1320
A_s = 2.191e-9
n_s = 0.9860
tau_reio = 0.068
gauge = newtonian
use_ridder = yes
ridder_model_type = unified
ridder_use_tail = no
ridder_use_shelf = yes
ridder_use_plateau = no
ridder_theta_EDE_low = -1000.0
ridder_theta_EDE_high = 1000.0
ridder_sigma_theta_EDE = 100.0
theta_i_ridder = 2.72
ridder_n_EDE = 2.6
ridder_m_axion = {m}
ridder_f_axion = {f}
ridder_f = {f_eV:.6e}
beta_ridder = 0.0
ridder_use_shooting_EDE = no
ridder_c_slow = 1.0
output = tCl
write background = yes
background_verbose = 0
root = output/pure_scan_
tol_background_integration = 1e-5
"""

def run_test(m, f):
    """Run CLASS with given m and f, return f_peak and z_peak"""
    f_eV = f * M_PL_EV
    
    ini_content = INI_TEMPLATE.format(m=m, f=f, f_eV=f_eV)
    
    with open("test_scan.ini", "w") as fp:
        fp.write(ini_content)
    
    result = subprocess.run(
        ["./phase2/class/class", "test_scan.ini"],
        capture_output=True, text=True, timeout=60
    )
    
    if "age =" not in result.stdout and "age =" not in result.stderr:
        # Check for error
        for line in result.stderr.split('\n'):
            if 'non-rad' in line or 'Error' in line:
                return None, None, line[:80]
        return None, None, "Unknown error"
    
    # Extract f_peak and z_peak using Python
    try:
        result2 = subprocess.run(
            ["python3", "extract_f_peak.py", "output/pure_scan_00_background.dat"],
            capture_output=True, text=True, timeout=30
        )
        
        f_peak = None
        z_peak = None
        for line in result2.stdout.split('\n'):
            if 'f_peak' in line and '=' in line:
                f_peak = float(line.split('=')[1].strip())
            if 'z_peak' in line and '=' in line:
                z_peak = float(line.split('=')[1].strip())
        
        return f_peak, z_peak, None
    except Exception as e:
        return None, None, str(e)

def main():
    print("="*70)
    print("TRACK 1A: Pure Axion-EDE Parameter Scan")
    print(f"Target: f_EDE ~ {TARGET_F_EDE}, z_peak ~ {TARGET_Z_PEAK}")
    print("="*70)
    
    # Parameter ranges to scan
    m_values = [10, 50, 100, 500, 1000, 5000]  # H0 units
    f_values = [1e-8, 1e-7, 1e-6, 1e-5]  # M_Pl units
    
    results = []
    
    for m in m_values:
        for f in f_values:
            print(f"\nTesting m={m} H0, f={f:.0e} M_Pl...", end=" ", flush=True)
            f_peak, z_peak, error = run_test(m, f)
            
            if error:
                print(f"FAILED: {error[:50]}")
            else:
                print(f"f_peak={f_peak:.2e}, z_peak={z_peak:.2e}")
                results.append({
                    'm': m, 'f': f, 'f_peak': f_peak, 'z_peak': z_peak
                })
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY - Working configurations:")
    print("="*70)
    print(f"{'m (H0)':<12} {'f (M_Pl)':<12} {'f_peak':<15} {'z_peak':<15}")
    print("-"*54)
    
    for r in results:
        z_close = "✓" if r['z_peak'] and 1000 < r['z_peak'] < 10000 else ""
        f_close = "✓" if r['f_peak'] and 0.05 < r['f_peak'] < 0.3 else ""
        print(f"{r['m']:<12} {r['f']:<12.0e} {r['f_peak']:<15.2e} {r['z_peak']:<15.2e} {f_close}{z_close}")
    
    # Find best match
    print("\n" + "="*70)
    print("Best configurations (closest to target):")
    
    # Sort by distance to target
    def distance(r):
        if r['f_peak'] is None or r['z_peak'] is None:
            return float('inf')
        f_dist = abs(r['f_peak'] - TARGET_F_EDE) / TARGET_F_EDE
        z_dist = abs(r['z_peak'] - TARGET_Z_PEAK) / TARGET_Z_PEAK if r['z_peak'] > 0 else float('inf')
        return f_dist + z_dist
    
    sorted_results = sorted(results, key=distance)
    for r in sorted_results[:3]:
        print(f"m={r['m']} H0, f={r['f']:.0e} M_Pl → f_peak={r['f_peak']:.3f}, z_peak={r['z_peak']:.0f}")

if __name__ == "__main__":
    main()

