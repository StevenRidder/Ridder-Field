#!/usr/bin/env python3
"""
Analyze Beta Ladder V6 Results

Extracts:
- H0_eff from r_s scaling
- S8 from sigma8 and Omega_m
- CMB distortions (max and RMS)
- EDE diagnostics (f_peak, z_peak)

Compares to ΛCDM baseline.
"""

import numpy as np
import sys
from pathlib import Path

REPO_ROOT = Path.home() / "Ridder-Field"
OUTPUT_DIR = REPO_ROOT / "phase2" / "class" / "output"
LCDM_OUTPUT_DIR = OUTPUT_DIR  # Assume ΛCDM baseline is in same dir

# Planck baseline values
H0_LCDM = 67.36  # km/s/Mpc
RS_LCDM = 147.079  # Mpc (from previous calibration)
S8_LCDM = 0.8415  # From previous ΛCDM run

print("="*70)
print("BETA LADDER V6 ANALYSIS")
print("="*70)
print()

# Find all v6 output files
configs = [
    ("0.05", "beta0.05_lambda1.0_v6"),
    ("0.10", "beta0.10_lambda1.0_v6"),
    ("0.15", "beta0.15_lambda1.0_v6"),
    ("0.20", "beta0.20_lambda1.0_v6"),
]

results = []

for beta_val, tag in configs:
    print(f"Analyzing beta = {beta_val}")
    print("-"*70)
    
    # Check if files exist
    bg_file = OUTPUT_DIR / f"unified_{tag}_00_background.dat"
    params_file = OUTPUT_DIR / f"unified_{tag}_00_parameters.ini"
    cl_file = OUTPUT_DIR / f"unified_{tag}_00_cl.dat"
    pk_file = OUTPUT_DIR / f"unified_{tag}_00_pk.dat"
    
    if not bg_file.exists():
        print(f"  ✗ Background file not found")
        print()
        continue
    
    # Extract r_s from background
    try:
        with open(bg_file, "r") as f:
            for line in f:
                if not line.startswith("#"):
                    parts = line.split()
                    if len(parts) > 8:
                        rs = float(parts[8])  # comov.snd.hrz column
        
        # Compute H0_eff
        H0_eff = H0_LCDM * (RS_LCDM / rs)
        delta_H0 = H0_eff - H0_LCDM
        
        print(f"  r_s = {rs:.3f} Mpc")
        print(f"  H0_eff = {H0_eff:.4f} km/s/Mpc")
        print(f"  ΔH0 = {delta_H0:+.4f} km/s/Mpc")
    except Exception as e:
        print(f"  ✗ Error extracting r_s: {e}")
        rs = np.nan
        H0_eff = np.nan
        delta_H0 = np.nan
    
    # Extract S8
    S8 = np.nan
    if params_file.exists():
        try:
            params = {}
            with open(params_file, "r") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, val = line.split("=", 1)
                        try:
                            params[key.strip()] = float(val.strip().split()[0])
                        except:
                            pass
            
            sigma8 = params.get("sigma8", np.nan)
            Omega_m = params.get("Omega0_m", np.nan)
            
            if not np.isnan(sigma8) and not np.isnan(Omega_m):
                S8 = sigma8 * np.sqrt(Omega_m / 0.3)
                delta_S8 = S8 - S8_LCDM
                
                print(f"  σ8 = {sigma8:.4f}")
                print(f"  Ω_m = {Omega_m:.4f}")
                print(f"  S8 = {S8:.4f}")
                print(f"  ΔS8 = {delta_S8:+.4f}")
        except Exception as e:
            print(f"  ✗ Error extracting S8: {e}")
    
    # Check CMB
    if cl_file.exists():
        print(f"  CMB spectra: ✓")
        # TODO: Compute actual residuals vs ΛCDM
    else:
        print(f"  CMB spectra: ✗ (perturbations failed)")
    
    # Extract EDE diagnostics from background
    try:
        with open(bg_file, "r") as f:
            lines = f.readlines()
        
        # Find columns
        header = [l for l in lines if l.startswith("#")][0]
        # Typically: col 1=a, col 15=rho_ridder, col 20=rho_tot
        
        data_lines = [l for l in lines if not l.startswith("#")]
        if len(data_lines) > 100:
            # Compute f_ridder = rho_ridder / rho_tot over full range
            a_vals = []
            f_ridder_vals = []
            
            for line in data_lines:
                parts = line.split()
                if len(parts) > 20:
                    a = float(parts[0])
                    rho_r = float(parts[14])  # 0-indexed, so col 15 -> idx 14
                    rho_tot = float(parts[19])  # col 20 -> idx 19
                    
                    if rho_tot > 0:
                        f_ridder = rho_r / rho_tot
                        a_vals.append(a)
                        f_ridder_vals.append(f_ridder)
            
            if len(f_ridder_vals) > 0:
                # Find peak in range 0 < a < 0.01 (z > 100)
                mask = np.array(a_vals) < 0.01
                if np.any(mask):
                    f_masked = np.array(f_ridder_vals)[mask]
                    a_masked = np.array(a_vals)[mask]
                    
                    if len(f_masked) > 0:
                        idx_peak = np.argmax(f_masked)
                        f_peak = f_masked[idx_peak]
                        a_peak = a_masked[idx_peak]
                        z_peak = 1.0/a_peak - 1.0
                        
                        print(f"  f_peak = {f_peak:.4f} at z = {z_peak:.0f}")
    except Exception as e:
        print(f"  ⚠ Could not extract EDE diagnostics: {e}")
    
    print()
    
    results.append({
        "beta": beta_val,
        "H0_eff": H0_eff,
        "delta_H0": delta_H0,
        "S8": S8,
        "delta_S8": delta_S8 if not np.isnan(S8) else np.nan,
    })

# Summary table
print("="*70)
print("SUMMARY")
print("="*70)
print()
print(f"{'Beta':<8} {'H0_eff':<10} {'ΔH0':<10} {'S8':<10} {'ΔS8':<10} {'Status':<10}")
print("-"*70)

for r in results:
    status = "✓" if not np.isnan(r['H0_eff']) and not np.isnan(r['S8']) else "✗"
    print(f"{r['beta']:<8} "
          f"{r['H0_eff']:<10.4f} "
          f"{r['delta_H0']:<+10.4f} "
          f"{r['S8']:<10.4f} "
          f"{r['delta_S8']:<+10.4f} "
          f"{status:<10}")

print()
print("Baseline: H0 = 67.36 km/s/Mpc, S8 = 0.8415")
print()
print("Next: Identify optimal beta, proceed to Phase 1B (tail activation)")
print()

