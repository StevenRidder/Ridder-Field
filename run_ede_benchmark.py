#!/usr/bin/env python3
"""
PURE EDE BENCHMARK RUNNER - Track 1
===================================
Test pure axion-like EDE in ΛCDM background (no tail).

Goal: Hit f_EDE ~ 0.1 at z_c ~ 3000

This runs:
1. ΛCDM baseline
2. Pure EDE configuration
3. Extracts f_EDE, z_peak, r_s, H0, S8
4. Compares to expected EDE behavior
"""

import subprocess
import numpy as np
from pathlib import Path

CLASS_BIN = "phase2/class/class"
EDE_INI = "pure_ede_benchmark.ini"
LCDM_INI = "lcdm_baseline.ini"
OUTPUT_DIR = Path("output")

def run_class(ini_file):
    """Run CLASS and return success."""
    print(f"  Running: {ini_file}...")
    result = subprocess.run(
        [CLASS_BIN, ini_file],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[:500]}")
        return False
    return True

def extract_f_ede(bg_file):
    """Extract f_EDE peak and z_peak from background file."""
    bg = np.loadtxt(bg_file)
    
    z = bg[:, 0]
    # For Ridder outputs: column 14 = rho_ridder, column 19 = rho_tot
    # But column indices depend on output format
    ncols = bg.shape[1]
    
    # Try to find rho_ridder and rho_tot
    # Standard: rho_ridder = col 14 (0-indexed), rho_tot = col 19 or 21
    if ncols >= 20:
        rho_ridder = bg[:, 14]
        rho_tot = bg[:, 19] if ncols < 24 else bg[:, 21]
    else:
        print("  Warning: Can't identify rho_ridder column")
        return None, None
    
    # Compute f_EDE = rho_ridder / rho_tot
    valid = (rho_tot > 0) & (rho_ridder >= 0)
    f_ede = np.zeros_like(z)
    f_ede[valid] = rho_ridder[valid] / rho_tot[valid]
    
    # Find peak in z range [100, 100000]
    mask = (z > 100) & (z < 100000)
    if not np.any(mask):
        return None, None
    
    f_masked = f_ede[mask]
    z_masked = z[mask]
    
    peak_idx = np.argmax(f_masked)
    f_peak = f_masked[peak_idx]
    z_peak = z_masked[peak_idx]
    
    return f_peak, z_peak

def extract_observables(bg_file, pk_file):
    """Extract H0, S8, r_s from outputs."""
    bg = np.loadtxt(bg_file)
    
    # H0 from last row, column 3
    H0 = bg[-1, 3] * 299792.458
    
    # r_s at drag (z~1060)
    z = bg[:, 0]
    r_s = bg[:, 7]  # Comoving sound horizon
    idx_drag = np.argmin(np.abs(z - 1060))
    r_s_drag = r_s[idx_drag]
    
    # S8 from P(k)
    if Path(pk_file).exists():
        pk = np.loadtxt(pk_file)
        k, Pk = pk[:, 0], pk[:, 1]
        R = 8.0
        x = k * R
        W = 3.0 * (np.sin(x) - x * np.cos(x)) / x**3
        W[x < 0.01] = 1.0
        sigma8 = np.sqrt(np.trapz(Pk * W**2 * k**2, k) / (2 * np.pi**2))
        
        # Omega_m
        rho_b = bg[-1, 9]
        rho_cdm = bg[-1, 10]
        rho_crit = bg[-1, 13]
        Omega_m = (rho_b + rho_cdm) / rho_crit
        
        S8 = sigma8 * np.sqrt(Omega_m / 0.3)
    else:
        sigma8, S8 = None, None
    
    return {
        'H0': H0,
        'r_s': r_s_drag,
        'sigma8': sigma8,
        'S8': S8
    }

def main():
    print("=" * 70)
    print("PURE EDE BENCHMARK - Track 1")
    print("=" * 70)
    print("Target: f_EDE ~ 0.1 at z_c ~ 3000")
    print()
    
    # Run LCDM baseline
    print("[1/2] Running ΛCDM baseline...")
    if not run_class(LCDM_INI):
        return 1
    
    # Run pure EDE
    print("[2/2] Running Pure EDE...")
    if not run_class(EDE_INI):
        return 1
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    # Extract f_EDE
    ede_bg = OUTPUT_DIR / "pure_ede00_background.dat"
    if ede_bg.exists():
        f_peak, z_peak = extract_f_ede(ede_bg)
        if f_peak is not None:
            print(f"\nEDE Episode:")
            print(f"  f_EDE (peak) = {f_peak:.4f}")
            print(f"  z_peak       = {z_peak:.0f}")
            print()
            
            # Check if we hit targets
            if 0.05 < f_peak < 0.20:
                print("  ✓ f_EDE in target range (0.05-0.20)")
            else:
                print(f"  ⚠️ f_EDE outside target range")
            
            if 1000 < z_peak < 10000:
                print("  ✓ z_peak in target range (1000-10000)")
            else:
                print(f"  ⚠️ z_peak outside target range")
        else:
            print("  Could not extract f_EDE")
    
    # Extract observables
    print("\nObservables:")
    print("-" * 50)
    
    lcdm_obs = extract_observables(
        OUTPUT_DIR / "lcdm_baseline00_background.dat",
        OUTPUT_DIR / "lcdm_baseline00_pk.dat"
    )
    ede_obs = extract_observables(
        OUTPUT_DIR / "pure_ede00_background.dat",
        OUTPUT_DIR / "pure_ede00_pk.dat"
    )
    
    print(f"{'Quantity':<12} {'ΛCDM':>12} {'Pure EDE':>12} {'Δ':>12}")
    print("-" * 50)
    print(f"{'H0':<12} {lcdm_obs['H0']:>12.2f} {ede_obs['H0']:>12.2f} {ede_obs['H0']-lcdm_obs['H0']:>+12.2f}")
    print(f"{'r_s [Mpc]':<12} {lcdm_obs['r_s']:>12.2f} {ede_obs['r_s']:>12.2f} {ede_obs['r_s']-lcdm_obs['r_s']:>+12.2f}")
    if ede_obs['S8']:
        print(f"{'S8':<12} {lcdm_obs['S8']:>12.4f} {ede_obs['S8']:>12.4f} {ede_obs['S8']-lcdm_obs['S8']:>+12.4f}")
    
    print("=" * 70)
    
    # Verdict
    print("\nVERDICT:")
    if f_peak and 0.05 < f_peak < 0.20 and 1000 < z_peak < 10000:
        print("✅ Pure EDE module working - f_EDE and z_peak in target range")
    else:
        print("⚠️ Need to tune parameters to hit f_EDE ~ 0.1 at z_c ~ 3000")
        print("   Try adjusting ridder_m_axion and ridder_Lambda_EDE_eV")
    
    return 0

if __name__ == "__main__":
    exit(main())

