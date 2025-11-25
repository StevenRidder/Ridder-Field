#!/usr/bin/env python3
"""
UNIFIED GRID: Hero + 8 Neighbors
================================
Run a 3x3 grid around the hero configuration to map the local landscape.

Hero: Lambda_tail = 20 meV, f_axion = 0.40
Grid: Lambda_tail ∈ {18, 20, 22} meV × f_axion ∈ {0.35, 0.40, 0.45}
"""

import subprocess
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime

CLASS_BIN = "phase2/class/class"
OUTPUT_DIR = Path("output")

# Grid definition
LAMBDA_TAIL_VALUES = [18e-3, 20e-3, 22e-3]  # meV
F_AXION_VALUES = [0.35, 0.40, 0.45]

INI_TEMPLATE = """
output = tCl,pCl,mPk
root = output/unified_grid_{tag}
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
l_max_scalars = 2500
P_k_max_h/Mpc = 1.7
"""

# Reference values
R_S_LCDM = 147.04  # Mpc
H0_LCDM = 67.36

def run_class(ini_file, timeout=180):
    """Run CLASS and return success status."""
    result = subprocess.run(
        [CLASS_BIN, ini_file],
        capture_output=True, text=True, timeout=timeout
    )
    return result.returncode == 0

def extract_observables(tag):
    """Extract all observables for a grid point."""
    bg_file = OUTPUT_DIR / f"unified_grid_{tag}00_background.dat"
    pk_file = OUTPUT_DIR / f"unified_grid_{tag}00_pk.dat"
    cl_file = OUTPUT_DIR / f"unified_grid_{tag}00_cl.dat"
    
    if not bg_file.exists():
        return None
    
    bg = np.loadtxt(bg_file)
    z = bg[:, 0]
    H = bg[:, 3] * 299792.458  # 1/Mpc to km/s/Mpc
    r_s = bg[:, 7]
    rho_ridder = bg[:, 14]
    rho_tot = bg[:, 19]
    
    # f_ridder
    valid = (rho_tot > 0) & (rho_ridder > 0)
    f_ridder = np.zeros_like(z)
    f_ridder[valid] = rho_ridder[valid] / rho_tot[valid]
    
    # f_EDE peak
    mask_ede = (z > 1000) & (z < 20000)
    if mask_ede.any():
        f_ede = f_ridder[mask_ede]
        z_ede = z[mask_ede]
        peak_idx = np.argmax(f_ede)
        f_peak = f_ede[peak_idx]
        z_peak = z_ede[peak_idx]
    else:
        f_peak, z_peak = 0, 0
    
    # f_late (z=0)
    f_late = f_ridder[-1]
    
    # r_s at drag
    idx_drag = np.argmin(np.abs(z - 1060))
    r_s_drag = r_s[idx_drag]
    
    # H0_eff via inverse r_s scaling
    H0_eff = H0_LCDM * (R_S_LCDM / r_s_drag)
    
    # Omega_m
    rho_b = bg[-1, 9]
    rho_cdm = bg[-1, 10]
    rho_crit = bg[-1, 13]
    Omega_m = (rho_b + rho_cdm) / rho_crit
    
    obs = {
        'r_s_drag': r_s_drag,
        'H0_eff': H0_eff,
        'Omega_m': Omega_m,
        'f_EDE': f_peak,
        'z_peak': z_peak,
        'f_late': f_late,
    }
    
    # S8 from P(k)
    if pk_file.exists():
        pk = np.loadtxt(pk_file)
        k, Pk = pk[:, 0], pk[:, 1]
        R = 8.0
        x = k * R
        W = np.where(x > 0.01, 3.0 * (np.sin(x) - x * np.cos(x)) / x**3, 1.0)
        sigma8 = np.sqrt(np.trapz(Pk * W**2 * k**2, k) / (2 * np.pi**2))
        S8 = sigma8 * np.sqrt(Omega_m / 0.3)
        obs['sigma8'] = sigma8
        obs['S8'] = S8
    
    # CMB diagnostics
    if cl_file.exists():
        cl = np.loadtxt(cl_file)
        ell = cl[:, 0]
        # Assuming TT is column 1
        TT = cl[:, 1]
        obs['cl_TT_max'] = np.max(TT)
        obs['ell_TT_max'] = ell[np.argmax(TT)]
    
    return obs

def main():
    print("=" * 70)
    print("UNIFIED GRID: Hero + 8 Neighbors")
    print("=" * 70)
    print()
    print("Grid: Lambda_tail ∈ {18, 20, 22} meV × f_axion ∈ {0.35, 0.40, 0.45}")
    print("Hero: Lambda_tail = 20 meV, f_axion = 0.40")
    print()
    
    results = []
    
    print("-" * 80)
    print(f"{'Λ_tail':>8} {'f_ax':>6} {'H0':>8} {'S8':>8} {'f_EDE':>8} {'z_peak':>8} {'Ω_m':>8} {'Hero?':>6}")
    print("-" * 80)
    
    for lt in LAMBDA_TAIL_VALUES:
        for fa in F_AXION_VALUES:
            tag = f"L{lt*1e3:.0f}_f{fa:.2f}".replace(".", "p")
            
            # Generate INI
            ini = INI_TEMPLATE.format(lambda_tail=lt, f_axion=fa, tag=tag)
            ini_file = f"unified_grid_{tag}.ini"
            
            with open(ini_file, 'w') as f:
                f.write(ini)
            
            # Run CLASS
            success = run_class(ini_file)
            
            if not success:
                print(f"{lt*1e3:>8.0f} {fa:>6.2f} {'FAILED':>8}")
                os.remove(ini_file)
                continue
            
            # Extract observables
            obs = extract_observables(tag)
            os.remove(ini_file)
            
            if obs is None:
                print(f"{lt*1e3:>8.0f} {fa:>6.2f} {'NO DATA':>8}")
                continue
            
            # Mark hero
            is_hero = (lt == 20e-3 and fa == 0.40)
            hero_mark = "★" if is_hero else ""
            
            # Store result
            result = {
                'lambda_tail_meV': lt * 1e3,
                'f_axion': fa,
                'is_hero': is_hero,
                **obs
            }
            results.append(result)
            
            print(f"{lt*1e3:>8.0f} {fa:>6.2f} {obs['H0_eff']:>8.2f} {obs.get('S8', 0):>8.4f} "
                  f"{obs['f_EDE']:>8.4f} {obs['z_peak']:>8.0f} {obs['Omega_m']:>8.4f} {hero_mark:>6}")
    
    print("-" * 80)
    
    # Save results to JSON
    output_file = "unified_grid_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'grid': {
                'lambda_tail_meV': [lt * 1e3 for lt in LAMBDA_TAIL_VALUES],
                'f_axion': F_AXION_VALUES,
            },
            'hero': {
                'lambda_tail_meV': 20,
                'f_axion': 0.40,
            },
            'results': results,
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Summary statistics
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    h0_vals = [r['H0_eff'] for r in results]
    s8_vals = [r.get('S8', 0) for r in results]
    
    print(f"H0 range:  {min(h0_vals):.2f} - {max(h0_vals):.2f} km/s/Mpc")
    print(f"S8 range:  {min(s8_vals):.4f} - {max(s8_vals):.4f}")
    
    # Count winners
    winners = [r for r in results if r['H0_eff'] > 71 and r.get('S8', 1) < 0.78]
    print(f"Winners (H0>71, S8<0.78): {len(winners)}/{len(results)}")
    
    # Hero stats
    hero = [r for r in results if r.get('is_hero', False)]
    if hero:
        h = hero[0]
        print(f"\nHero config:")
        print(f"  H0 = {h['H0_eff']:.2f} km/s/Mpc")
        print(f"  S8 = {h.get('S8', 'N/A'):.4f}")
        print(f"  f_EDE = {h['f_EDE']:.4f} at z = {h['z_peak']:.0f}")

if __name__ == "__main__":
    main()

