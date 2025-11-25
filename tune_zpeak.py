#!/usr/bin/env python3
"""
Tune z_peak by scanning m_axion.

Goal: Find m_axion that gives z_peak ~ 3000 (during recombination)
Physics: Lighter field rolls later → lower z_peak
"""

import subprocess
import numpy as np
import tempfile
import os
from pathlib import Path

CLASS_BIN = "phase2/class/class"

BASE_INI = """
output = tCl
root = {root}
H0 = 67.36
T_cmb = 2.7255
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842

use_ridder = yes
ridder_model_type = unified
gauge = newtonian

ridder_use_tail = no
ridder_use_shelf = yes
ridder_use_plateau = no

ridder_m_axion = {m_axion}
ridder_f_axion = 0.3
ridder_n_EDE = 3.0
ridder_theta_EDE_low = 0.5
ridder_theta_EDE_high = 3.5
ridder_sigma_theta_EDE = 0.5
ridder_f = 7.305e26
theta_i_ridder = 2.5
beta_ridder = 0.0
ridder_c_slow = 0.0

write background = yes
background_verbose = 0
"""

def run_and_extract(m_axion):
    """Run CLASS and extract f_EDE, z_peak."""
    root = f"output/tune_m_{m_axion:.0f}"
    
    # Write temp INI
    ini_content = BASE_INI.format(root=root, m_axion=m_axion)
    ini_file = f"tune_m_{m_axion:.0f}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini_content)
    
    # Run CLASS
    result = subprocess.run(
        [CLASS_BIN, ini_file],
        capture_output=True, text=True, timeout=120
    )
    
    if result.returncode != 0:
        return None, None
    
    # Read background
    bg_file = f"{root}00_background.dat"
    if not os.path.exists(bg_file):
        return None, None
    
    bg = np.loadtxt(bg_file)
    z = bg[:, 0]
    rho_ridder = bg[:, 14]
    rho_tot = bg[:, 19]
    
    valid = (rho_tot > 0) & (rho_ridder > 0)
    f_ridder = np.zeros_like(z)
    f_ridder[valid] = rho_ridder[valid] / rho_tot[valid]
    
    mask = z > 100
    if not mask.any():
        return None, None
    
    f_masked = f_ridder[mask]
    z_masked = z[mask]
    peak_idx = np.argmax(f_masked)
    f_peak = f_masked[peak_idx]
    z_peak = z_masked[peak_idx]
    
    # Cleanup
    os.remove(ini_file)
    
    return f_peak, z_peak

def main():
    print("=" * 60)
    print("TUNING z_peak BY SCANNING m_axion")
    print("=" * 60)
    print()
    print("Physics: z_peak ~ m_axion / H(z_c)")
    print("Lighter field → rolls later → lower z_peak")
    print()
    print("-" * 60)
    print(f"{'m_axion':>12} {'f_EDE':>10} {'z_peak':>10} {'Status':>15}")
    print("-" * 60)
    
    # Current m=100 gives z~9000. We want z~3000.
    # z_peak ∝ m, so try m ~ 100 * (3000/9000) ~ 30
    m_values = [10, 20, 30, 50, 75, 100, 150, 200]
    
    results = []
    for m in m_values:
        f_peak, z_peak = run_and_extract(m)
        
        if f_peak is None:
            print(f"{m:>12.0f} {'FAILED':>10} {'-':>10} {'ERROR':>15}")
            continue
        
        # Status based on targets
        f_ok = 0.05 < f_peak < 0.15
        z_ok = 2000 < z_peak < 5000
        
        if f_ok and z_ok:
            status = "✓ TARGET"
        elif z_ok:
            status = "z ok, f off"
        elif f_ok:
            status = "f ok, z off"
        else:
            status = "both off"
        
        print(f"{m:>12.0f} {f_peak:>10.4f} {z_peak:>10.0f} {status:>15}")
        results.append((m, f_peak, z_peak))
    
    print("-" * 60)
    
    # Find best m for z_peak ~ 3000
    best = None
    best_diff = float('inf')
    for m, f_peak, z_peak in results:
        diff = abs(z_peak - 3000)
        if diff < best_diff:
            best = (m, f_peak, z_peak)
            best_diff = diff
    
    if best:
        print()
        print(f"BEST for z_peak ~ 3000:")
        print(f"  m_axion = {best[0]}")
        print(f"  f_EDE   = {best[1]:.4f}")
        print(f"  z_peak  = {best[2]:.0f}")

if __name__ == "__main__":
    main()

