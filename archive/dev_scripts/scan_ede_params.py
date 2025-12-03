#!/usr/bin/env python3
"""
EDE PARAMETER SCAN - Track 1
============================
Scan Lambda_EDE to find configurations that hit:
- f_EDE ~ 0.1
- z_peak ~ 3000

This is a coarse grid search to identify working parameter regions.
"""

import subprocess
import numpy as np
from pathlib import Path
import os

CLASS_BIN = "phase2/class/class"
OUTPUT_DIR = Path("output")

def create_ede_ini(m_axion, f_axion, root_tag, theta_i=2.5):
    """Create EDE test INI with m_axion and f_axion."""
    ridder_f = f_axion * 2.435e27  # f_axion in M_Pl units -> eV
    content = f"""# EDE scan configuration
use_ridder = yes
ridder_model_type = unified
gauge = newtonian

H0 = 67.36
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842

# TAIL: OFF
ridder_use_tail = no

# SHELF: ON with m²f² dynamics
ridder_use_shelf = yes
ridder_m_axion = {m_axion:.6e}
ridder_f_axion = {f_axion:.6e}
ridder_n_EDE = 3.0
ridder_theta_EDE_low = 0.5
ridder_theta_EDE_high = 3.5
ridder_sigma_theta_EDE = 0.5

ridder_use_plateau = no

ridder_f = {ridder_f:.6e}
theta_i_ridder = {theta_i}
beta_ridder = 0.0
ridder_c_slow = 0.0

output = tCl
root = output/{root_tag}
write background = yes
background_verbose = 0
"""
    temp_path = f"temp_{root_tag}.ini"
    with open(temp_path, 'w') as f:
        f.write(content)
    return temp_path

def run_class(ini_file, timeout=60):
    """Run CLASS, return success."""
    try:
        result = subprocess.run(
            [CLASS_BIN, ini_file],
            capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False

def extract_f_ede(bg_file):
    """Extract f_EDE peak and z_peak from background file."""
    try:
        bg = np.loadtxt(bg_file)
    except Exception as e:
        print(f"    Error loading {bg_file}: {e}")
        return None, None
    
    z = bg[:, 0]
    ncols = bg.shape[1]
    
    # Column indices (0-indexed) from CLASS background output:
    # 14: rho_ridder, 19: rho_tot
    # Note: Column 20 is p_tot, 21 is p_tot_prime - don't use those!
    if ncols >= 20:
        rho_ridder = bg[:, 14]
        rho_tot = bg[:, 19]  # Always column 19 for rho_tot
    else:
        print(f"    Only {ncols} columns, expected >= 20")
        return None, None
    
    # Compute f_ridder = rho_ridder / rho_tot
    valid = (rho_tot > 0) & (rho_ridder >= 0)
    f_ede = np.zeros_like(z)
    f_ede[valid] = rho_ridder[valid] / rho_tot[valid]
    
    # Find peak in z > 100 (avoid z=0 artifacts)
    mask = z > 100
    if not np.any(mask):
        return None, None
    
    f_masked = f_ede[mask]
    z_masked = z[mask]
    
    peak_idx = np.argmax(f_masked)
    f_peak = f_masked[peak_idx]
    z_peak = z_masked[peak_idx]
    
    return f_peak, z_peak

def main():
    print("=" * 70)
    print("EDE PARAMETER SCAN - Track 1")
    print("=" * 70)
    print("Target: f_EDE ~ 0.1 at z_peak ~ 3000")
    print()
    
    # Parameter grid - m_axion controls z_peak, f_axion controls amplitude
    # For z_peak ~ 3000: m ~ 3*H(z_c)/H0 ~ 500
    # But we found peak at z~50000 with m=500, so try smaller m
    m_values = [30, 100]
    f_values = [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]
    
    results = []
    
    print(f"{'m_axion':<12} {'f_axion':<12} {'f_EDE':>12} {'z_peak':>12} {'Status':<12}")
    print("-" * 70)
    
    for m in m_values:
        for f in f_values:
            tag = f"scan_m{m}_f{f}".replace('.', 'p')
            ini_file = create_ede_ini(m, f, tag)
            
            try:
                success = run_class(ini_file)
                
                if success:
                    bg_file = OUTPUT_DIR / f"{tag}00_background.dat"
                    if bg_file.exists():
                        f_peak, z_peak = extract_f_ede(bg_file)
                        
                        if f_peak is not None:
                            f_ok = 0.05 < f_peak < 0.20
                            z_ok = 1000 < z_peak < 10000
                            
                            if f_ok and z_ok:
                                status = "✓ TARGET"
                            elif f_peak > 0.01:
                                status = "~ some EDE"
                            else:
                                status = "✗ too weak"
                            
                            results.append({
                                'm': m, 'f': f,
                                'f_EDE': f_peak,
                                'z_peak': z_peak,
                                'target': f_ok and z_ok
                            })
                            
                            print(f"{m:<12.0f} {f:<12.2f} {f_peak:>12.6f} {z_peak:>12.0f} {status:<12}")
                        else:
                            print(f"{m:<12.0f} {f:<12.2f} {'N/A':>12} {'N/A':>12} {'extract err':<12}")
                    else:
                        print(f"{m:<12.0f} {f:<12.2f} {'---':>12} {'---':>12} {'no output':<12}")
                else:
                    print(f"{m:<12.0f} {f:<12.2f} {'---':>12} {'---':>12} {'FAILED':<12}")
            
            except subprocess.TimeoutExpired:
                print(f"{m:<12.0f} {f:<12.2f} {'---':>12} {'---':>12} {'TIMEOUT':<12}")
            
            finally:
                if os.path.exists(ini_file):
                    os.remove(ini_file)
    
    print("=" * 70)
    
    # Summary
    targets = [r for r in results if r['target']]
    if targets:
        print(f"\n✅ Found {len(targets)} configuration(s) hitting target:")
        for r in targets:
            print(f"   m={r['m']}, f={r['f']} -> f_EDE = {r['f_EDE']:.4f}, z_peak = {r['z_peak']:.0f}")
    else:
        print("\n⚠️ No configuration hit the target yet.")
        if results:
            best = max(results, key=lambda x: x['f_EDE'])
            print(f"   Best: m={best['m']}, f={best['f']} -> f_EDE = {best['f_EDE']:.6f}, z_peak = {best['z_peak']:.0f}")
        print("   Try adjusting m_axion (controls z_peak) and f_axion (controls amplitude)")
    
    return 0

if __name__ == "__main__":
    exit(main())
