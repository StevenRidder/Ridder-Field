#!/usr/bin/env python3
"""Test larger Lambda_tail values to boost tail contribution."""

import subprocess
import numpy as np
import os

CLASS_BIN = "phase2/class/class"

INI_TEMPLATE = """
output = tCl,pCl,mPk
root = output/unified_big_tail_{tag}
H0 = 67.36
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842

use_ridder = yes
ridder_model_type = unified
gauge = newtonian

ridder_use_tail = yes
ridder_Lambda_tail_eV = {lambda_tail}
ridder_alpha_tail = 1.0
ridder_n_tail = 1.0

ridder_use_shelf = yes
ridder_m_axion = 7e4
ridder_f_axion = 0.25
ridder_n_EDE = 3.0
ridder_theta_EDE_low = 0.5
ridder_theta_EDE_high = 3.5
ridder_sigma_theta_EDE = 0.5

ridder_use_plateau = no
ridder_f = 7.305e26
theta_i_ridder = 2.5
beta_ridder = 0.0
ridder_c_slow = 0.0

write background = yes
background_verbose = 0
"""

print("Testing larger Lambda_tail to boost tail contribution")
print("-" * 60)
print(f"{'L_tail [meV]':>12} {'f_late':>10} {'H0_eff':>10} {'S8':>10}")
print("-" * 60)

for lt in [15e-3, 18e-3, 20e-3, 22e-3, 25e-3]:
    tag = f"L{lt:.0e}".replace("+", "").replace(".", "p")
    ini = INI_TEMPLATE.format(lambda_tail=lt, tag=tag)
    
    with open("temp_scan.ini", "w") as f:
        f.write(ini)
    
    result = subprocess.run([CLASS_BIN, "temp_scan.ini"], 
                          capture_output=True, text=True, timeout=180)
    
    if result.returncode != 0:
        print(f"{lt*1e3:>12.1f} {'FAILED':>10}")
        continue
    
    bg_file = f"output/unified_big_tail_{tag}00_background.dat"
    if not os.path.exists(bg_file):
        print(f"{lt*1e3:>12.1f} {'NO FILE':>10}")
        continue
        
    bg = np.loadtxt(bg_file)
    z = bg[:, 0]
    r_s = bg[:, 7]
    rho_r = bg[:, 14]
    rho_t = bg[:, 19]
    
    f_late = rho_r[-1] / rho_t[-1] if rho_t[-1] > 0 else 0
    
    idx_drag = np.argmin(np.abs(z - 1060))
    H0_eff = 67.36 * (147.04 / r_s[idx_drag])
    
    pk_file = f"output/unified_big_tail_{tag}00_pk.dat"
    S8 = 0
    if os.path.exists(pk_file):
        pk = np.loadtxt(pk_file)
        k, Pk = pk[:, 0], pk[:, 1]
        R = 8.0
        x = k * R
        W = np.where(x > 0.01, 3.0 * (np.sin(x) - x * np.cos(x)) / x**3, 1.0)
        sigma8 = np.sqrt(np.trapz(Pk * W**2 * k**2, k) / (2 * np.pi**2))
        rho_b = bg[-1, 9]
        rho_cdm = bg[-1, 10]
        rho_crit = bg[-1, 13]
        Omega_m = (rho_b + rho_cdm) / rho_crit
        S8 = sigma8 * np.sqrt(Omega_m / 0.3)
    
    print(f"{lt*1e3:>12.1f} {f_late:>10.4f} {H0_eff:>10.2f} {S8:>10.4f}")

if os.path.exists("temp_scan.ini"):
    os.remove("temp_scan.ini")

