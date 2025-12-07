#!/usr/bin/env python3
"""
DATASET COMPARISON TEST: High-amplitude EDE + α-branching

Tests the (θ_i, Λ, α) → H₀ parameter space and shows which 
dataset combinations might allow the high-amplitude island.

Paper 2 Dataset Configurations:
1. FULL: Planck lowℓ + lensing + ACT DR6 + BAO + DESI + Pantheon+
2. ACT-ONLY: Planck lowℓ + ACT DR6 (no external data)
3. NO-LENSING: FULL without Planck lensing
4. NO-DESI: FULL without DESI Y1 BAO
5. NO-BAO: CMB only (Planck lowℓ + ACT DR6 + lensing)

Key question: Which dataset combo allows θ_i > 1 ?
"""

import subprocess
import os
import numpy as np

CLASS = "/Users/steveridder/Git/Ridder-Field/phase2/class/class"
OUTPUT = "/Users/steveridder/Git/Ridder-Field/phase2/class/output"


# Approximate r_s constraints from different datasets (from literature)
DATASET_CONSTRAINTS = {
    "ΛCDM": {
        "r_s": 147.1,      # Planck ΛCDM
        "r_s_err": 0.3,
        "H0": 67.4,
        "H0_err": 0.5,
        "notes": "Planck 2018 baseline"
    },
    "ACT-only": {
        "r_s": 146.5,      # ACT prefers slightly lower r_s
        "r_s_err": 1.5,    # Larger uncertainty without external data
        "H0": 67.9,
        "H0_err": 1.5,
        "notes": "ACT DR6, no external data"
    },
    "No-Lensing": {
        "r_s": 147.0,
        "r_s_err": 0.8,
        "H0": 67.5,
        "H0_err": 0.8,
        "notes": "Removes lensing amplitude constraint"
    },
    "No-DESI": {
        "r_s": 147.2,
        "r_s_err": 0.5,
        "H0": 67.3,
        "H0_err": 0.6,
        "notes": "Pre-DESI constraints only"
    },
    "SH0ES-prior": {
        "r_s": 140.0,      # Would need this to hit H0=73
        "r_s_err": 2.0,
        "H0": 73.0,
        "H0_err": 1.0,
        "notes": "What SH0ES would require"
    }
}


def run_background(theta_i, Lambda, alpha, name):
    """Run CLASS background and return (r_s, H0, f_peak)."""
    
    ini = f"""
root = {OUTPUT}/{name}
write background = yes
h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
Lambda_EDE_ridder = {Lambda}
f_axion_ridder = 1.0e+27
theta_i_ridder = {theta_i}
n_ridder = 3
alpha_ridder_to_dr = {alpha}
z_ridder_decay = 3500
ridder_force_damping = 1.0
ridder_freeze_phi = no
use_ridder_shooting = 0
gauge = newtonian
"""
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(ini)
        ini_file = f.name
    
    try:
        subprocess.run([CLASS, ini_file], capture_output=True, timeout=120)
        
        bg_file = f"{OUTPUT}/{name}00_background.dat"
        if not os.path.exists(bg_file):
            return None, None, None
        
        with open(bg_file) as f:
            lines = f.readlines()
        
        r_s = None
        f_peak = 0.0
        
        for line in lines:
            if line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 22:
                continue
            
            z = float(parts[0])
            
            # Get r_s at z ≈ 1100
            if 1095 < z < 1105:
                r_s = float(parts[7])
            
            # Get max f_ridder in z = 2000-5000
            if 2000 < z < 5000:
                f = float(parts[20])  # f_ridder column
                if f > f_peak:
                    f_peak = f
        
        H0 = 67.4 * 147.1 / r_s if r_s else None
        
        return r_s, H0, f_peak * 100  # Convert f_peak to %
        
    except Exception as e:
        return None, None, None
    finally:
        os.unlink(ini_file)


def main():
    print("=" * 90)
    print("PAPER 2 DATASET COMPARISON: High-Amplitude EDE + α-branching")
    print("=" * 90)
    print()
    
    # Define test points
    test_points = [
        # (θ_i, Λ, α, label)
        (1.0, 0.5, 0.0, "Current best-fit region (no decay)"),
        (1.0, 0.5, 1.0, "Current best-fit + full decay"),
        (1.5, 0.5, 0.0, "High θ_i (no decay)"),
        (1.5, 0.5, 1.0, "High θ_i + full decay"),
        (1.5, 1.0, 1.0, "High θ_i, high Λ + decay"),
        (2.0, 0.5, 0.0, "Very high θ_i (no decay)"),
        (2.0, 0.5, 1.0, "Very high θ_i + full decay"),
    ]
    
    print("STEP 1: Computing model predictions")
    print("-" * 70)
    print(f"{'Config':<35} {'f_peak':<10} {'r_s (Mpc)':<12} {'H₀':<8}")
    print("-" * 70)
    
    results = []
    for theta, L, alpha, label in test_points:
        name = f"ds_t{theta}_L{L}_a{alpha}"
        r_s, H0, f_peak = run_background(theta, L, alpha, name)
        
        if r_s is not None:
            results.append((label, theta, L, alpha, r_s, H0, f_peak))
            print(f"{label:<35} {f_peak:>6.1f}%    {r_s:>10.2f}   {H0:>6.1f}")
        else:
            print(f"{label:<35} FAILED")
    
    print()
    print("=" * 90)
    print("STEP 2: Compatibility with different dataset worlds")
    print("=" * 90)
    print()
    
    # Create compatibility table
    print("How many σ away from each dataset's preferred r_s?")
    print()
    
    header = f"{'Config':<30}"
    for ds in DATASET_CONSTRAINTS:
        header += f" {ds:<12}"
    print(header)
    print("-" * 100)
    
    for label, theta, L, alpha, r_s, H0, f_peak in results:
        row = f"{label:<30}"
        for ds, constraints in DATASET_CONSTRAINTS.items():
            rs_target = constraints["r_s"]
            rs_err = constraints["r_s_err"]
            tension = abs(r_s - rs_target) / rs_err
            
            if tension < 1:
                compat = f"✓ {tension:.1f}σ"
            elif tension < 2:
                compat = f"~ {tension:.1f}σ"
            else:
                compat = f"✗ {tension:.1f}σ"
            
            row += f" {compat:<12}"
        print(row)
    
    print()
    print("=" * 90)
    print("STEP 3: Summary - Which configs are worth MCMC?")
    print("=" * 90)
    print()
    
    for label, theta, L, alpha, r_s, H0, f_peak in results:
        print(f"\n{label}:")
        print(f"  θ_i={theta}, Λ={L}, α={alpha}")
        print(f"  f_peak = {f_peak:.1f}%, r_s = {r_s:.2f} Mpc, H₀ = {H0:.1f} km/s/Mpc")
        
        # Check compatibility
        compatible = []
        for ds, constraints in DATASET_CONSTRAINTS.items():
            tension = abs(r_s - constraints["r_s"]) / constraints["r_s_err"]
            if tension < 2:
                compatible.append(ds)
        
        if compatible:
            print(f"  Compatible (<2σ) with: {', '.join(compatible)}")
            if H0 > 70:
                print(f"  → ⭐ WORTH MCMC with these datasets!")
        else:
            print(f"  → Not compatible with any dataset at <2σ")


if __name__ == "__main__":
    main()

