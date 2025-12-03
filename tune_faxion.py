#!/usr/bin/env python3
"""Tune f_axion with m_axion=7e4 to hit f_EDE target."""

import subprocess
import numpy as np
import os

CLASS_BIN = "phase2/class/class"

def run_point(m_axion, f_axion):
    ini = f"""
output = tCl
root = output/tune_f_{f_axion}
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
ridder_m_axion = {m_axion}
ridder_f_axion = {f_axion}
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
    ini_file = "tune_f.ini"
    with open(ini_file, "w") as f:
        f.write(ini)
    
    result = subprocess.run([CLASS_BIN, ini_file], capture_output=True, text=True, timeout=120)
    
    if result.returncode != 0:
        return None, None
    
    bg_file = f"output/tune_f_{f_axion}00_background.dat"
    if not os.path.exists(bg_file):
        return None, None
    
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
    
    return f_masked[idx], z_masked[idx]

print("Tuning f_axion with m_axion=7e4 (z_peak ~ 3900)")
print("-" * 55)
print(f"{'f_axion':>10} {'f_peak':>10} {'z_peak':>10} {'Status':>15}")
print("-" * 55)

for f_ax in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]:
    f_peak, z_peak = run_point(7e4, f_ax)
    if f_peak is None:
        print(f"{f_ax:>10.2f} {'FAILED':>10}")
    else:
        f_ok = 0.05 < f_peak < 0.15
        z_ok = 2000 < z_peak < 5000
        status = "✓ TARGET" if (f_ok and z_ok) else ("z ok" if z_ok else ("f ok" if f_ok else "-"))
        print(f"{f_ax:>10.2f} {f_peak:>10.4f} {z_peak:>10.0f} {status:>15}")

print("-" * 55)

