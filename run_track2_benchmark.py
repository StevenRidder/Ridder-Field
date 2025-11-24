#!/usr/bin/env python3
"""
RIDDER TRACK 2 BENCHMARK RUNNER
===============================
Single command to regenerate the Track 2 minimal tail model benchmark.

Usage:
    python3 run_track2_benchmark.py [--scan]

Outputs:
    - Background evolution
    - CMB spectra
    - Matter power spectrum
    - Observable summary (H0, S8, w(z), etc.)
    - Comparison plots vs LCDM

Created: November 24, 2024
"""

import subprocess
import sys
import os
import numpy as np
from pathlib import Path

# Configuration
CLASS_BIN = "phase2/class/class"
TRACK2_INI = "ridder_tail_minimal.ini"
LCDM_INI = "lcdm_baseline.ini"
OUTPUT_DIR = Path("output")
PLOTS_DIR = Path("track2_plots")

def run_class(ini_file, label=""):
    """Run CLASS with given INI file."""
    print(f"  Running CLASS: {ini_file} {label}...")
    result = subprocess.run(
        [CLASS_BIN, ini_file],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[:200]}")
        return False
    return True

def compute_s8(pk_file, bg_file):
    """Compute S8 from power spectrum and background."""
    data = np.loadtxt(pk_file)
    k, Pk = data[:, 0], data[:, 1]
    
    # Top-hat window at R=8 Mpc/h
    R = 8.0
    x = k * R
    W = 3.0 * (np.sin(x) - x * np.cos(x)) / x**3
    W[x < 0.01] = 1.0
    
    # sigma8^2 = integral P(k) W^2 k^2 dk / (2 pi^2)
    sigma8_sq = np.trapz(Pk * W**2 * k**2, k) / (2 * np.pi**2)
    sigma8 = np.sqrt(sigma8_sq)
    
    # Get Omega_m from background
    # Column indices depend on whether ncdm is included
    # Without ncdm: 9=rho_b, 10=rho_cdm, 13=rho_crit
    # With ncdm: indices shift by 2 per ncdm species
    bg = np.loadtxt(bg_file)
    
    # Use rho_tot (last density column before growth factors)
    # rho_b and rho_cdm are always at 9 and 10
    rho_b = bg[-1, 9]
    rho_cdm = bg[-1, 10]
    
    # Find rho_crit: it equals rho_tot for flat universe
    # Last few columns are usually rho_tot, p_tot, p_tot_prime, gr.fac D, gr.fac f
    # rho_tot is typically 5 columns before the end for Ridder outputs
    ncols = bg.shape[1]
    # Try column 13 (no ncdm) or use rho_tot
    if ncols == 24:  # Standard Ridder output without ncdm
        rho_crit = bg[-1, 13]
    elif ncols == 26:  # With 1 ncdm species
        rho_crit = bg[-1, 15]
    else:
        # Fallback: rho_crit = rho_tot (they should be equal)
        rho_crit = bg[-1, ncols - 6]
    
    Omega_m = (rho_b + rho_cdm) / rho_crit
    
    S8 = sigma8 * np.sqrt(Omega_m / 0.3)
    return sigma8, Omega_m, S8

def extract_background_observables(bg_file):
    """Extract key observables from background file."""
    bg = np.loadtxt(bg_file)
    
    # Column mapping (0-indexed):
    # 0=z, 1=proper time [Gyr], 2=conf time, 3=H [1/Mpc]
    z = bg[:, 0]
    proper_time = bg[:, 1]  # Already in Gyr
    H = bg[:, 3]  # H [1/Mpc]
    
    # Find z=0 row (last row)
    H0_Mpc = H[-1]
    H0_km_s_Mpc = H0_Mpc * 299792.458  # c in km/s
    
    # Age is directly available in column 1
    age_Gyr = proper_time[-1]
    
    return {
        'H0': H0_km_s_Mpc,
        'age_Gyr': age_Gyr,
        'z': z,
        'H': H
    }

def extract_w_of_z(bg_file):
    """Extract w(z) for the Ridder field."""
    bg = np.loadtxt(bg_file)
    z = bg[:, 0]
    ncols = bg.shape[1]
    
    # Column mapping depends on ncdm
    # Without ncdm (24 cols): 14=rho_ridder, 15=p_ridder
    # With ncdm (26 cols): 16=rho_ridder, 17=p_ridder
    try:
        if ncols == 24:
            rho_ridder = bg[:, 14]
            p_ridder = bg[:, 15]
        else:
            rho_ridder = bg[:, 16]
            p_ridder = bg[:, 17]
        
        w = p_ridder / rho_ridder
        # Filter valid entries
        valid = (rho_ridder > 1e-50) & np.isfinite(w)
        return z[valid], w[valid]
    except:
        return None, None

def create_lcdm_baseline():
    """Create LCDM baseline INI if it doesn't exist."""
    if not os.path.exists(LCDM_INI):
        with open(LCDM_INI, 'w') as f:
            f.write("""# LCDM Baseline for Track 2 comparison
output = tCl,pCl,mPk
root = output/lcdm_baseline

h = 0.6736
T_cmb = 2.7255
omega_b = 0.02237
omega_cdm = 0.12
N_ur = 2.0328
N_ncdm = 1
m_ncdm = 0.06

A_s = 2.1e-9
n_s = 0.9649
k_pivot = 0.05

l_max_scalars = 2500
P_k_max_h/Mpc = 1.7
k_per_decade_for_pk = 10

write background = yes
""")

def main(do_scan=False):
    print("=" * 70)
    print("RIDDER TRACK 2 BENCHMARK")
    print("=" * 70)
    
    # Create output directories
    OUTPUT_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)
    
    # Run Track 2 model
    print("\n[1/4] Running Track 2 minimal tail model...")
    if not run_class(TRACK2_INI):
        print("FAILED!")
        return 1
    print("  ✓ Done")
    
    # Run LCDM baseline
    print("\n[2/4] Running LCDM baseline...")
    create_lcdm_baseline()
    if not run_class(LCDM_INI):
        print("FAILED!")
        return 1
    print("  ✓ Done")
    
    # Extract observables
    print("\n[3/4] Extracting observables...")
    
    # Track 2 model (CLASS adds 00 suffix)
    t2_pk = OUTPUT_DIR / "track2_minimal00_pk.dat"
    t2_bg = OUTPUT_DIR / "track2_minimal00_background.dat"
    
    if t2_pk.exists() and t2_bg.exists():
        sigma8, Omega_m, S8 = compute_s8(t2_pk, t2_bg)
        obs = extract_background_observables(t2_bg)
        z_w, w = extract_w_of_z(t2_bg)
        
        print("\n" + "=" * 50)
        print("TRACK 2 OBSERVABLES")
        print("=" * 50)
        print(f"  H0        = {obs['H0']:.2f} km/s/Mpc")
        print(f"  Age       = {obs['age_Gyr']:.2f} Gyr")
        print(f"  sigma8    = {sigma8:.4f}")
        print(f"  Omega_m   = {Omega_m:.4f}")
        print(f"  S8        = {S8:.4f}")
        if z_w is not None:
            # w at various redshifts
            for z_target in [0, 0.5, 1.0, 2.0]:
                idx = np.argmin(np.abs(z_w - z_target))
                print(f"  w(z={z_target:.1f})  = {w[idx]:.4f}")
        print("=" * 50)
        
        # Save summary
        with open(OUTPUT_DIR / "track2_observables.txt", 'w') as f:
            f.write("TRACK 2 MINIMAL MODEL OBSERVABLES\n")
            f.write("=" * 40 + "\n")
            f.write(f"H0 = {obs['H0']:.4f} km/s/Mpc\n")
            f.write(f"Age = {obs['age_Gyr']:.4f} Gyr\n")
            f.write(f"sigma8 = {sigma8:.6f}\n")
            f.write(f"Omega_m = {Omega_m:.6f}\n")
            f.write(f"S8 = {S8:.6f}\n")
        print(f"  ✓ Saved to {OUTPUT_DIR}/track2_observables.txt")
    else:
        print("  ERROR: Output files not found!")
        return 1
    
    # LCDM comparison
    lcdm_pk = OUTPUT_DIR / "lcdm_baseline00_pk.dat"
    lcdm_bg = OUTPUT_DIR / "lcdm_baseline00_background.dat"
    
    if lcdm_pk.exists() and lcdm_bg.exists():
        sigma8_lcdm, Omega_m_lcdm, S8_lcdm = compute_s8(lcdm_pk, lcdm_bg)
        obs_lcdm = extract_background_observables(lcdm_bg)
        
        print("\n" + "-" * 50)
        print("COMPARISON TO LCDM")
        print("-" * 50)
        print(f"  ΔH0       = {obs['H0'] - obs_lcdm['H0']:+.2f} km/s/Mpc")
        print(f"  ΔS8       = {S8 - S8_lcdm:+.4f}")
        print(f"  ΔOmega_m  = {Omega_m - Omega_m_lcdm:+.4f}")
        print("-" * 50)
    
    # Generate plots
    print("\n[4/4] Generating plots...")
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        # Plot 1: w(z) comparison
        if z_w is not None:
            plt.figure(figsize=(8, 5))
            plt.plot(z_w, w, 'b-', label='Ridder Tail', linewidth=2)
            plt.axhline(-1, color='k', linestyle='--', label='ΛCDM (w=-1)')
            plt.xlabel('z', fontsize=12)
            plt.ylabel('w(z)', fontsize=12)
            plt.xlim(0, 5)
            plt.ylim(-1.1, -0.8)
            plt.legend()
            plt.title('Equation of State: Ridder Tail vs ΛCDM')
            plt.grid(alpha=0.3)
            plt.savefig(PLOTS_DIR / 'w_of_z.png', dpi=150, bbox_inches='tight')
            plt.close()
            print(f"  ✓ Saved {PLOTS_DIR}/w_of_z.png")
        
        # Plot 2: P(k) ratio
        if lcdm_pk.exists():
            pk_t2 = np.loadtxt(t2_pk)
            pk_lcdm = np.loadtxt(lcdm_pk)
            
            plt.figure(figsize=(8, 5))
            ratio = pk_t2[:, 1] / pk_lcdm[:, 1]
            plt.semilogx(pk_t2[:, 0], ratio, 'b-', linewidth=2)
            plt.axhline(1.0, color='k', linestyle='--')
            plt.xlabel('k [h/Mpc]', fontsize=12)
            plt.ylabel('P(k)_Ridder / P(k)_ΛCDM', fontsize=12)
            plt.title('Matter Power Spectrum Ratio')
            plt.grid(alpha=0.3)
            plt.savefig(PLOTS_DIR / 'pk_ratio.png', dpi=150, bbox_inches='tight')
            plt.close()
            print(f"  ✓ Saved {PLOTS_DIR}/pk_ratio.png")
        
        print("  ✓ All plots generated")
        
    except ImportError:
        print("  (matplotlib not available, skipping plots)")
    
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    do_scan = "--scan" in sys.argv
    sys.exit(main(do_scan))

