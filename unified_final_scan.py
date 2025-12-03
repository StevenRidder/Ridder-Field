#!/usr/bin/env python3
"""
Final unified scan: Lambda_tail (S8 control) x f_axion (H0 control)
Target: H0 > 71 AND S8 < 0.78
"""

import subprocess
import numpy as np
import os

CLASS_BIN = "phase2/class/class"

INI_TEMPLATE = """
output = tCl,pCl,mPk
root = output/unified_final_{tag}
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
ridder_f_axion = {f_axion}
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

print("=" * 70)
print("UNIFIED FINAL SCAN: Lambda_tail x f_axion")
print("=" * 70)
print()
print("Lambda_tail: 18-25 meV (controls S8)")
print("f_axion: 0.30-0.50 (controls H0 via EDE)")
print()
print("Target: H0 > 71 AND S8 < 0.78")
print()
print("-" * 70)
print(f"{'L_tail':>8} {'f_ax':>6} {'f_late':>8} {'f_EDE':>8} {'H0':>8} {'S8':>8} {'Status':>10}")
print("-" * 70)

winners = []

for lt in [18e-3, 20e-3, 22e-3, 25e-3]:
    for fa in [0.30, 0.35, 0.40, 0.45, 0.50]:
        tag = f"L{lt*1e3:.0f}_f{fa:.2f}".replace(".", "p")
        ini = INI_TEMPLATE.format(lambda_tail=lt, f_axion=fa, tag=tag)
        
        with open("temp.ini", "w") as f:
            f.write(ini)
        
        result = subprocess.run([CLASS_BIN, "temp.ini"], 
                              capture_output=True, text=True, timeout=180)
        
        if result.returncode != 0:
            print(f"{lt*1e3:>8.0f} {fa:>6.2f} {'FAILED':>8}")
            continue
        
        bg_file = f"output/unified_final_{tag}00_background.dat"
        pk_file = f"output/unified_final_{tag}00_pk.dat"
        
        if not os.path.exists(bg_file):
            continue
        
        bg = np.loadtxt(bg_file)
        z = bg[:, 0]
        r_s = bg[:, 7]
        rho_r = bg[:, 14]
        rho_t = bg[:, 19]
        
        f_late = rho_r[-1] / rho_t[-1] if rho_t[-1] > 0 else 0
        
        # f_EDE peak
        mask = (z > 1000) & (z < 20000)
        if mask.any():
            f_ridder = np.zeros_like(z)
            valid = (rho_t > 0) & (rho_r > 0)
            f_ridder[valid] = rho_r[valid] / rho_t[valid]
            f_EDE = np.max(f_ridder[mask])
        else:
            f_EDE = 0
        
        idx_drag = np.argmin(np.abs(z - 1060))
        H0 = 67.36 * (147.04 / r_s[idx_drag])
        
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
        
        h0_ok = H0 > 71
        s8_ok = S8 < 0.78
        
        if h0_ok and s8_ok:
            status = "✓ WINNER"
            winners.append((lt, fa, H0, S8, f_EDE, f_late))
        elif h0_ok:
            status = "H0 ok"
        elif s8_ok:
            status = "S8 ok"
        else:
            status = "-"
        
        print(f"{lt*1e3:>8.0f} {fa:>6.2f} {f_late:>8.4f} {f_EDE:>8.4f} {H0:>8.2f} {S8:>8.4f} {status:>10}")

print("-" * 70)

if os.path.exists("temp.ini"):
    os.remove("temp.ini")

print()
if winners:
    print("✅ WINNING CONFIGURATIONS:")
    for lt, fa, h0, s8, fede, flate in winners:
        print(f"   Lambda_tail = {lt*1e3:.0f} meV, f_axion = {fa:.2f}")
        print(f"   H0 = {h0:.2f}, S8 = {s8:.4f}, f_EDE = {fede:.4f}")
else:
    print("⚠️ No configuration meets both targets")
    print("   May need stronger EDE (higher f_axion) or different approach")

