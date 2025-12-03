#!/usr/bin/env python3
"""
UNIFIED 2D SCAN: Lambda_tail x f_axion
======================================
Small grid scan to find where H0>71 and S8<0.78 intersect.
"""

import subprocess
import numpy as np
import os
from pathlib import Path

CLASS_BIN = "phase2/class/class"

INI_TEMPLATE = """
output = tCl,pCl,mPk
root = output/unified_scan_{tag}
H0 = 67.36
T_cmb = 2.7255
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842
k_pivot = 0.05

use_ridder = yes
ridder_model_type = unified
gauge = newtonian

# TAIL
ridder_use_tail = yes
ridder_Lambda_tail_eV = {lambda_tail}
ridder_alpha_tail = 1.0
ridder_n_tail = 1.0

# SHELF
ridder_use_shelf = yes
ridder_m_axion = 7e4
ridder_f_axion = {f_axion}
ridder_n_EDE = 3.0
ridder_theta_EDE_low = 0.5
ridder_theta_EDE_high = 3.5
ridder_sigma_theta_EDE = 0.5

# PLATEAU off
ridder_use_plateau = no

# Field params
ridder_f = 7.305e26
theta_i_ridder = 2.5
beta_ridder = 0.0
ridder_c_slow = 0.0

write background = yes
background_verbose = 0
l_max_scalars = 2500
P_k_max_h/Mpc = 1.7
"""

def run_point(lambda_tail, f_axion):
    """Run a single grid point and extract observables."""
    tag = f"L{lambda_tail:.2e}_f{f_axion:.2f}".replace('+', '').replace('.', 'p')
    
    ini = INI_TEMPLATE.format(lambda_tail=lambda_tail, f_axion=f_axion, tag=tag)
    ini_file = f"unified_scan_{tag}.ini"
    
    with open(ini_file, 'w') as f:
        f.write(ini)
    
    result = subprocess.run(
        [CLASS_BIN, ini_file],
        capture_output=True, text=True, timeout=180
    )
    
    if result.returncode != 0:
        os.remove(ini_file)
        return None
    
    # Read background
    bg_file = f"output/unified_scan_{tag}00_background.dat"
    pk_file = f"output/unified_scan_{tag}00_pk.dat"
    
    if not os.path.exists(bg_file):
        os.remove(ini_file)
        return None
    
    bg = np.loadtxt(bg_file)
    z = bg[:, 0]
    r_s = bg[:, 7]
    rho_ridder = bg[:, 14]
    rho_tot = bg[:, 19]
    
    # f_EDE peak
    valid = (rho_tot > 0) & (rho_ridder > 0)
    f_ridder = np.zeros_like(z)
    f_ridder[valid] = rho_ridder[valid] / rho_tot[valid]
    
    mask_ede = (z > 1000) & (z < 20000)
    if mask_ede.any():
        f_ede = f_ridder[mask_ede]
        z_ede = z[mask_ede]
        peak_idx = np.argmax(f_ede)
        f_peak = f_ede[peak_idx]
        z_peak = z_ede[peak_idx]
    else:
        f_peak, z_peak = 0, 0
    
    # r_s at drag
    idx_drag = np.argmin(np.abs(z - 1060))
    r_s_drag = r_s[idx_drag]
    
    # H0_eff via inverse r_s scaling (r_s_LCDM = 147.04)
    H0_eff = 67.36 * (147.04 / r_s_drag)
    
    # S8 from P(k)
    S8 = None
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
    
    os.remove(ini_file)
    
    return {
        'H0_eff': H0_eff,
        'S8': S8,
        'f_peak': f_peak,
        'z_peak': z_peak,
        'r_s': r_s_drag,
    }

def main():
    print("=" * 80)
    print("UNIFIED 2D SCAN: Lambda_tail x f_axion")
    print("=" * 80)
    print()
    print("Grid: Lambda_tail in {1.44, 1.52, 1.60, 1.68} meV")
    print("      f_axion in {0.20, 0.25, 0.30}")
    print()
    print("Target: H0 > 71 km/s/Mpc AND S8 < 0.78")
    print()
    
    lambda_values = [1.44e-3, 1.52e-3, 1.60e-3, 1.68e-3]
    f_axion_values = [0.20, 0.25, 0.30]
    
    print("-" * 80)
    print(f"{'Λ_tail':>10} {'f_axion':>8} {'H0_eff':>8} {'S8':>8} {'f_EDE':>8} {'z_peak':>8} {'Status':>12}")
    print("-" * 80)
    
    results = []
    winners = []
    
    for lambda_tail in lambda_values:
        for f_axion in f_axion_values:
            obs = run_point(lambda_tail, f_axion)
            
            if obs is None:
                print(f"{lambda_tail*1e3:>10.2f} {f_axion:>8.2f} {'FAILED':>8}")
                continue
            
            H0 = obs['H0_eff']
            S8 = obs['S8'] if obs['S8'] else 0
            f_peak = obs['f_peak']
            z_peak = obs['z_peak']
            
            h0_ok = H0 > 71
            s8_ok = S8 < 0.78
            
            if h0_ok and s8_ok:
                status = "✓ WINNER"
                winners.append((lambda_tail, f_axion, obs))
            elif h0_ok:
                status = "H0 ok"
            elif s8_ok:
                status = "S8 ok"
            else:
                status = "-"
            
            print(f"{lambda_tail*1e3:>10.2f} {f_axion:>8.2f} {H0:>8.2f} {S8:>8.4f} {f_peak:>8.4f} {z_peak:>8.0f} {status:>12}")
            results.append((lambda_tail, f_axion, obs))
    
    print("-" * 80)
    
    # Summary
    print()
    if winners:
        print("✅ WINNING CONFIGURATIONS:")
        for lt, fa, obs in winners:
            print(f"   Λ_tail = {lt*1e3:.2f} meV, f_axion = {fa:.2f}")
            print(f"   H0 = {obs['H0_eff']:.2f}, S8 = {obs['S8']:.4f}, f_EDE = {obs['f_peak']:.4f}")
            print()
    else:
        print("⚠️ No configuration meets both targets (H0>71 AND S8<0.78)")
        
        # Find best compromise
        best = None
        best_score = float('inf')
        for lt, fa, obs in results:
            if obs is None:
                continue
            # Score: distance from targets (lower is better)
            h0_dist = max(0, 71 - obs['H0_eff']) / 5  # Penalize low H0
            s8_dist = max(0, obs['S8'] - 0.78) / 0.05 if obs['S8'] else 10  # Penalize high S8
            score = h0_dist + s8_dist
            if score < best_score:
                best = (lt, fa, obs)
                best_score = score
        
        if best:
            lt, fa, obs = best
            print(f"\nBest compromise:")
            print(f"   Λ_tail = {lt*1e3:.2f} meV, f_axion = {fa:.2f}")
            print(f"   H0 = {obs['H0_eff']:.2f}, S8 = {obs['S8']:.4f}, f_EDE = {obs['f_peak']:.4f}")

if __name__ == "__main__":
    main()

