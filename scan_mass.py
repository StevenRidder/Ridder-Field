#!/usr/bin/env python3
"""Scan m_axion to find impact on z_peak."""

import subprocess
import numpy as np
import os

CLASS_BIN = "phase2/class/class"

INI_TEMPLATE = """
output = tCl
root = output/scan_m_{m:.0e}
H0 = 67.36
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
ridder_m_axion = {m}
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

def run_and_extract(m):
    ini = INI_TEMPLATE.format(m=m)
    ini_file = f"scan_m_{m:.0e}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini)
    
    result = subprocess.run([CLASS_BIN, ini_file], capture_output=True, text=True, timeout=120)
    
    if result.returncode != 0:
        os.remove(ini_file)
        return None, None, None
    
    bg_file = f"output/scan_m_{m:.0e}00_background.dat"
    if not os.path.exists(bg_file):
        os.remove(ini_file)
        return None, None, None
    
    bg = np.loadtxt(bg_file)
    z = bg[:, 0]
    rho_r = bg[:, 14]
    rho_t = bg[:, 19]
    
    mask = z > 100
    f = np.zeros_like(z)
    valid = (rho_t > 0) & (rho_r > 0)
    f[valid] = rho_r[valid] / rho_t[valid]
    
    f_masked = f[mask]
    z_masked = z[mask]
    idx = np.argmax(f_masked)
    
    # Also get m_eV from debug output
    m_eV = None
    for line in result.stdout.split('\n'):
        if 'm_eV=' in line:
            import re
            match = re.search(r'm_eV=([\d.e+-]+)', line)
            if match:
                m_eV = float(match.group(1))
            break
    
    os.remove(ini_file)
    return f_masked[idx], z_masked[idx], m_eV

print("=" * 60)
print("SCANNING m_axion TO FIND z_peak DEPENDENCE")
print("=" * 60)
print()
print(f"{'m_axion':>12} {'f_peak':>10} {'z_peak':>10} {'Status':>15}")
print("-" * 60)

for m in [2e4, 3e4, 5e4, 7e4, 1e5, 1.5e5, 2e5]:
    f_peak, z_peak, m_eV = run_and_extract(m)
    if f_peak is None:
        print(f"{m:>12.0e} {'FAILED':>12}")
    else:
        # Check targets
        f_ok = 0.05 < f_peak < 0.15
        z_ok = 2000 < z_peak < 5000
        status = "✓ TARGET" if (f_ok and z_ok) else ("z ok" if z_ok else ("f ok" if f_ok else "-"))
        print(f"{m:>12.0e} {f_peak:>10.4f} {z_peak:>10.0f} {status:>15}")

