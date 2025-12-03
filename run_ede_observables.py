#!/usr/bin/env python3
"""
TRACK 1: EDE OBSERVABLES PIPELINE
=================================
Run shelf-only EDE benchmark and extract key observables:
- f_EDE peak and z_peak
- r_s (sound horizon)
- H0 shift via r_s scaling
- S8, sigma8, Omega_m
- w(z) for the EDE field

Compare to LCDM baseline to quantify EDE impact.
"""

import subprocess
import numpy as np
from pathlib import Path

CLASS_BIN = "phase2/class/class"
OUTPUT_DIR = Path("output")

def run_class(ini_file, timeout=120):
    """Run CLASS."""
    print(f"  Running: {ini_file}...")
    result = subprocess.run(
        [CLASS_BIN, ini_file],
        capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[:500]}")
        return False
    return True

def extract_ede_observables(bg_file, pk_file=None, has_ridder=True):
    """Extract EDE-specific observables from CLASS output."""
    bg = np.loadtxt(bg_file)
    
    z = bg[:, 0]
    H = bg[:, 3] * 299792.458  # 1/Mpc to km/s/Mpc
    r_s = bg[:, 7]  # Comoving sound horizon
    
    # Column mapping depends on whether Ridder is active
    # LCDM: 14=rho_crit, 15=rho_tot (19 cols)
    # EDE:  14=rho_crit, 15=rho_ridder, 20=rho_tot (24 cols)
    ncols = bg.shape[1]
    
    if has_ridder and ncols >= 20:
        rho_ridder = bg[:, 14]  # 15th col = rho_ridder
        rho_tot = bg[:, 19]     # 20th col = rho_tot
        p_ridder = bg[:, 15]    # 16th col = p_ridder
    else:
        # LCDM - no ridder
        rho_ridder = np.zeros_like(z)
        rho_tot = bg[:, 14]     # 15th col = rho_tot
        p_ridder = np.zeros_like(z)
    
    # f_ridder = rho_ridder / rho_tot
    valid = (rho_tot > 0) & (rho_ridder >= 0)
    f_ridder = np.zeros_like(z)
    f_ridder[valid] = rho_ridder[valid] / rho_tot[valid]
    
    # Find f_EDE peak
    if has_ridder:
        mask = z > 100
        f_masked = f_ridder[mask]
        z_masked = z[mask]
        peak_idx = np.argmax(f_masked)
        f_peak = f_masked[peak_idx]
        z_peak = z_masked[peak_idx]
    else:
        f_peak = 0.0
        z_peak = 0.0
    
    # r_s at drag (z ~ 1060)
    idx_drag = np.argmin(np.abs(z - 1060))
    r_s_drag = r_s[idx_drag]
    
    # H0 (z=0)
    H0 = H[-1]
    
    # w(z) for ridder field if available
    w_ridder = np.zeros_like(z)
    w_valid = rho_ridder > 1e-50
    w_ridder[w_valid] = p_ridder[w_valid] / rho_ridder[w_valid]
    
    results = {
        'f_peak': f_peak,
        'z_peak': z_peak,
        'r_s_drag': r_s_drag,
        'H0': H0,
    }
    
    # S8 from P(k) if available
    if pk_file and Path(pk_file).exists():
        pk = np.loadtxt(pk_file)
        k, Pk = pk[:, 0], pk[:, 1]
        
        # sigma8 calculation
        R = 8.0  # Mpc/h
        x = k * R
        W = np.where(x > 0.01, 3.0 * (np.sin(x) - x * np.cos(x)) / x**3, 1.0)
        sigma8 = np.sqrt(np.trapz(Pk * W**2 * k**2, k) / (2 * np.pi**2))
        
        # Omega_m from background
        rho_b = bg[-1, 9]
        rho_cdm = bg[-1, 10]
        rho_crit = bg[-1, 13]
        Omega_m = (rho_b + rho_cdm) / rho_crit
        
        S8 = sigma8 * np.sqrt(Omega_m / 0.3)
        
        results['sigma8'] = sigma8
        results['Omega_m'] = Omega_m
        results['S8'] = S8
    
    return results, w_ridder, z

def main():
    print("=" * 70)
    print("TRACK 1: EDE OBSERVABLES PIPELINE")
    print("=" * 70)
    print()
    
    # Run LCDM baseline
    print("[1/2] Running ΛCDM baseline...")
    if not run_class("lcdm_baseline.ini"):
        return 1
    
    # Run EDE benchmark
    print("[2/2] Running EDE shelf-only benchmark...")
    if not run_class("ede_benchmark.ini"):
        return 1
    
    print()
    print("=" * 70)
    print("EXTRACTING OBSERVABLES")
    print("=" * 70)
    
    # Extract LCDM
    lcdm_obs, _, _ = extract_ede_observables(
        OUTPUT_DIR / "lcdm_baseline00_background.dat",
        OUTPUT_DIR / "lcdm_baseline00_pk.dat",
        has_ridder=False
    )
    
    # Extract EDE
    ede_obs, w_ede, z_ede = extract_ede_observables(
        OUTPUT_DIR / "ede_benchmark00_background.dat",
        OUTPUT_DIR / "ede_benchmark00_pk.dat",
        has_ridder=True
    )
    
    print()
    print("=" * 70)
    print("TRACK 1 EDE RESULTS")
    print("=" * 70)
    
    # EDE-specific metrics
    print("\n### EDE Episode ###")
    print(f"  f_EDE (peak)  = {ede_obs['f_peak']:.4f}")
    print(f"  z_peak        = {ede_obs['z_peak']:.0f}")
    
    target_f = 0.05 < ede_obs['f_peak'] < 0.15
    target_z = 2000 < ede_obs['z_peak'] < 5000
    print(f"  Target f_EDE ∈ [0.05, 0.15]: {'✓' if target_f else '✗'}")
    print(f"  Target z_peak ∈ [2000, 5000]: {'✓' if target_z else '✗'}")
    
    # Sound horizon and H0
    print("\n### Sound Horizon & H0 ###")
    print(f"{'Quantity':<15} {'ΛCDM':>12} {'EDE':>12} {'Δ':>12}")
    print("-" * 55)
    
    r_s_lcdm = lcdm_obs['r_s_drag']
    r_s_ede = ede_obs['r_s_drag']
    delta_rs = (r_s_ede - r_s_lcdm) / r_s_lcdm * 100
    print(f"{'r_s [Mpc]':<15} {r_s_lcdm:>12.2f} {r_s_ede:>12.2f} {delta_rs:>+12.2f}%")
    
    # H0 shift from inverse r_s scaling
    H0_lcdm = 67.36  # Input value
    H0_eff = H0_lcdm * (r_s_lcdm / r_s_ede)
    delta_H0 = H0_eff - H0_lcdm
    print(f"{'H0 [km/s/Mpc]':<15} {H0_lcdm:>12.2f} {H0_eff:>12.2f} {delta_H0:>+12.2f}")
    
    # S8 and structure
    if 'S8' in lcdm_obs and 'S8' in ede_obs:
        print("\n### Structure Growth ###")
        print(f"{'Quantity':<15} {'ΛCDM':>12} {'EDE':>12} {'Δ':>12}")
        print("-" * 55)
        
        for key in ['sigma8', 'Omega_m', 'S8']:
            l_val = lcdm_obs[key]
            e_val = ede_obs[key]
            delta = e_val - l_val
            print(f"{key:<15} {l_val:>12.4f} {e_val:>12.4f} {delta:>+12.4f}")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print(f"""
Track 1 Shelf-Only EDE Results:
  • f_EDE = {ede_obs['f_peak']:.4f} at z = {ede_obs['z_peak']:.0f}
  • Δr_s/r_s = {delta_rs:+.2f}%
  • ΔH0 = {delta_H0:+.2f} km/s/Mpc (via inverse r_s scaling)
""")
    
    if 'S8' in ede_obs:
        delta_s8 = ede_obs['S8'] - lcdm_obs['S8']
        print(f"  • ΔS8 = {delta_s8:+.4f}")
    
    if delta_H0 > 2.0:
        print("\n✓ EDE shifts H0 in the right direction!")
    else:
        print("\n⚠ H0 shift is small - may need stronger EDE")
    
    return 0

if __name__ == "__main__":
    exit(main())

