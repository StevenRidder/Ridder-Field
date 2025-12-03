#!/usr/bin/env python3
"""
Tune z_peak by scanning theta_i and f.

In Lambda^4 form, timing is controlled by:
- theta_i: initial field position
- f: controls d(theta)/dt = phi'/f

Higher f → slower theta evolution → later roll
"""

import subprocess
import numpy as np
import os

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

ridder_m_axion = 100
ridder_f_axion = 0.3
ridder_n_EDE = 3.0
ridder_theta_EDE_low = 0.5
ridder_theta_EDE_high = 3.5
ridder_sigma_theta_EDE = 0.5
ridder_f = {f}
theta_i_ridder = {theta_i}
beta_ridder = 0.0
ridder_c_slow = 0.0

write background = yes
background_verbose = 0
"""

def run_and_extract(f, theta_i):
    """Run CLASS and extract f_EDE, z_peak."""
    tag = f"f{f:.0e}_th{theta_i:.1f}".replace('+', '')
    root = f"output/tune_{tag}"
    
    ini_content = BASE_INI.format(root=root, f=f, theta_i=theta_i)
    ini_file = f"tune_{tag}.ini"
    with open(ini_file, 'w') as f_handle:
        f_handle.write(ini_content)
    
    result = subprocess.run(
        [CLASS_BIN, ini_file],
        capture_output=True, text=True, timeout=120
    )
    
    if result.returncode != 0:
        os.remove(ini_file)
        return None, None
    
    bg_file = f"{root}00_background.dat"
    if not os.path.exists(bg_file):
        os.remove(ini_file)
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
        os.remove(ini_file)
        return None, None
    
    f_masked = f_ridder[mask]
    z_masked = z[mask]
    peak_idx = np.argmax(f_masked)
    f_peak = f_masked[peak_idx]
    z_peak = z_masked[peak_idx]
    
    os.remove(ini_file)
    
    return f_peak, z_peak

def main():
    print("=" * 70)
    print("TUNING z_peak BY SCANNING theta_i AND f")
    print("=" * 70)
    print()
    print("Physics: Higher f → slower theta evolution → later roll → lower z_peak")
    print("         Higher theta_i → starts further from minimum → later roll")
    print()
    
    # Current: f=7.305e26, theta_i=2.5, z_peak=8937
    # Target: z_peak ~ 3000
    
    # Scan f: try larger values
    f_values = [1e26, 5e26, 7.305e26, 1e27, 5e27, 1e28]
    theta_values = [2.0, 2.5, 3.0, 3.14]  # max is pi
    
    print("-" * 70)
    print(f"{'f':>12} {'theta_i':>10} {'f_EDE':>10} {'z_peak':>10} {'Status':>15}")
    print("-" * 70)
    
    results = []
    for f in f_values:
        for theta_i in theta_values:
            f_peak, z_peak = run_and_extract(f, theta_i)
            
            if f_peak is None:
                print(f"{f:>12.1e} {theta_i:>10.2f} {'FAIL':>10} {'-':>10} {'ERROR':>15}")
                continue
            
            # Check targets
            f_ok = 0.05 < f_peak < 0.15
            z_ok = 2000 < z_peak < 5000
            
            if f_ok and z_ok:
                status = "✓ TARGET"
            elif z_ok:
                status = "z ok"
            elif f_ok:
                status = "f ok"
            else:
                status = "-"
            
            print(f"{f:>12.1e} {theta_i:>10.2f} {f_peak:>10.4f} {z_peak:>10.0f} {status:>15}")
            results.append((f, theta_i, f_peak, z_peak))
    
    print("-" * 70)
    
    # Find best configuration
    best = None
    best_score = float('inf')
    for f, theta_i, f_peak, z_peak in results:
        # Score: distance from targets
        f_dist = abs(f_peak - 0.10) / 0.05  # target f_EDE = 0.10
        z_dist = abs(z_peak - 3000) / 1000   # target z_peak = 3000
        score = f_dist + z_dist
        
        if score < best_score:
            best = (f, theta_i, f_peak, z_peak)
            best_score = score
    
    if best:
        print()
        print("BEST CONFIGURATION:")
        print(f"  f         = {best[0]:.1e}")
        print(f"  theta_i   = {best[1]:.2f}")
        print(f"  f_EDE     = {best[2]:.4f}")
        print(f"  z_peak    = {best[3]:.0f}")

if __name__ == "__main__":
    main()

