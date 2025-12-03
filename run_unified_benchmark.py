#!/usr/bin/env python3
"""
UNIFIED BENCHMARK: Tail + Shelf Combined
=========================================
Test the unified Ridder model with both tail and shelf active.
Extract key observables and compare to Track 1 and Track 2 results.
"""

import subprocess
import numpy as np
from pathlib import Path

CLASS_BIN = "phase2/class/class"
OUTPUT_DIR = Path("output")

def run_class(ini_file, timeout=180):
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

def extract_observables(bg_file, pk_file=None, has_ridder=True):
    """Extract key observables from CLASS output."""
    bg = np.loadtxt(bg_file)
    
    z = bg[:, 0]
    H = bg[:, 3] * 299792.458  # 1/Mpc to km/s/Mpc
    r_s = bg[:, 7]
    
    ncols = bg.shape[1]
    
    if has_ridder and ncols >= 20:
        rho_ridder = bg[:, 14]
        rho_tot = bg[:, 19]
        p_ridder = bg[:, 15]
    else:
        rho_ridder = np.zeros_like(z)
        rho_tot = bg[:, 14]
        p_ridder = np.zeros_like(z)
    
    # f_ridder = rho_ridder / rho_tot
    valid = (rho_tot > 0) & (rho_ridder >= 0)
    f_ridder = np.zeros_like(z)
    f_ridder[valid] = rho_ridder[valid] / rho_tot[valid]
    
    # Find f_EDE peak (EDE episode around z ~ 1000-10000)
    mask_ede = (z > 1000) & (z < 20000)
    if mask_ede.any() and has_ridder:
        f_ede_masked = f_ridder[mask_ede]
        z_ede_masked = z[mask_ede]
        peak_idx = np.argmax(f_ede_masked)
        f_peak = f_ede_masked[peak_idx]
        z_peak = z_ede_masked[peak_idx]
    else:
        f_peak = 0.0
        z_peak = 0.0
    
    # f_ridder at z=0 (late-time dark energy)
    f_late = f_ridder[-1] if has_ridder else 0.0
    
    # w(z) at z=0 for late-time field
    w_late = 0.0
    if has_ridder and rho_ridder[-1] > 1e-50:
        w_late = p_ridder[-1] / rho_ridder[-1]
    
    # r_s at drag
    idx_drag = np.argmin(np.abs(z - 1060))
    r_s_drag = r_s[idx_drag]
    
    # H0
    H0 = H[-1]
    
    results = {
        'f_peak': f_peak,
        'z_peak': z_peak,
        'f_late': f_late,
        'w_late': w_late,
        'r_s_drag': r_s_drag,
        'H0': H0,
    }
    
    # S8 from P(k)
    if pk_file and Path(pk_file).exists():
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
        
        results['sigma8'] = sigma8
        results['Omega_m'] = Omega_m
        results['S8'] = S8
    
    return results, f_ridder, z

def main():
    print("=" * 70)
    print("UNIFIED BENCHMARK: Tail + Shelf Combined")
    print("=" * 70)
    print()
    
    # Run LCDM baseline
    print("[1/2] Running ΛCDM baseline...")
    if not run_class("lcdm_baseline.ini"):
        return 1
    
    # Run unified hero
    print("[2/2] Running unified (tail + shelf)...")
    if not run_class("unified_hero.ini"):
        return 1
    
    print()
    print("=" * 70)
    print("EXTRACTING OBSERVABLES")
    print("=" * 70)
    
    lcdm_obs, _, _ = extract_observables(
        OUTPUT_DIR / "lcdm_baseline00_background.dat",
        OUTPUT_DIR / "lcdm_baseline00_pk.dat",
        has_ridder=False
    )
    
    unified_obs, f_ridder, z = extract_observables(
        OUTPUT_DIR / "unified_hero00_background.dat",
        OUTPUT_DIR / "unified_hero00_pk.dat",
        has_ridder=True
    )
    
    print()
    print("=" * 70)
    print("UNIFIED MODEL RESULTS")
    print("=" * 70)
    
    # EDE Episode
    print("\n### EDE Episode (Shelf) ###")
    print(f"  f_EDE (peak)  = {unified_obs['f_peak']:.4f}")
    print(f"  z_peak        = {unified_obs['z_peak']:.0f}")
    
    # Late-time (Tail)
    print("\n### Late-Time Dark Energy (Tail) ###")
    print(f"  f_ridder(z=0) = {unified_obs['f_late']:.4f}")
    print(f"  w(z=0)        = {unified_obs['w_late']:.3f}")
    
    # Comparison table
    print("\n### Comparison to ΛCDM ###")
    print(f"{'Quantity':<15} {'ΛCDM':>12} {'Unified':>12} {'Δ':>12}")
    print("-" * 55)
    
    r_s_lcdm = lcdm_obs['r_s_drag']
    r_s_unified = unified_obs['r_s_drag']
    delta_rs = (r_s_unified - r_s_lcdm) / r_s_lcdm * 100
    print(f"{'r_s [Mpc]':<15} {r_s_lcdm:>12.2f} {r_s_unified:>12.2f} {delta_rs:>+12.2f}%")
    
    # H0 via inverse r_s scaling
    H0_lcdm = 67.36
    H0_eff = H0_lcdm * (r_s_lcdm / r_s_unified)
    delta_H0 = H0_eff - H0_lcdm
    print(f"{'H0_eff':<15} {H0_lcdm:>12.2f} {H0_eff:>12.2f} {delta_H0:>+12.2f}")
    
    if 'S8' in lcdm_obs and 'S8' in unified_obs:
        for key in ['sigma8', 'Omega_m', 'S8']:
            l_val = lcdm_obs.get(key, 0)
            u_val = unified_obs.get(key, 0)
            delta = u_val - l_val
            print(f"{key:<15} {l_val:>12.4f} {u_val:>12.4f} {delta:>+12.4f}")
    
    # Summary assessment
    print()
    print("=" * 70)
    print("ASSESSMENT")
    print("=" * 70)
    
    h0_target = H0_eff > 71
    s8_target = unified_obs.get('S8', 1.0) < 0.78
    
    print(f"""
Unified Model Assessment:
  • H0_eff = {H0_eff:.2f} km/s/Mpc {'✓' if h0_target else '✗'} (target > 71)
  • S8 = {unified_obs.get('S8', 'N/A'):.4f} {'✓' if s8_target else '✗'} (target < 0.78)
  • f_EDE = {unified_obs['f_peak']:.4f} at z = {unified_obs['z_peak']:.0f}
  • f_late = {unified_obs['f_late']:.4f}, w_late = {unified_obs['w_late']:.3f}
""")
    
    if h0_target and s8_target:
        print("✅ UNIFIED MODEL PASSES BASIC CHECKS!")
    else:
        print("⚠️ Unified model needs tuning")
        if not h0_target:
            print("   - H0 too low: need stronger EDE or larger tail")
        if not s8_target:
            print("   - S8 too high: tail not suppressing growth enough")
    
    return 0

if __name__ == "__main__":
    exit(main())

