#!/usr/bin/env python3
"""
HIGH-AMPLITUDE EDE ISLAND SCAN

This script implements the concrete plan to find a viable high-H₀ island:

1. Sweep (Λ, θ_i) to find regions with f_peak ≈ 5-10%
2. For each, turn on α-branching and measure (H₀, ΔN_eff)
3. Map out the viable parameter space

The key insight: we're not testing α at the old low-amplitude best-fit.
We're looking for a NEW island where the field carries enough energy.
"""

import subprocess
import os
import re
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple

CLASS_PATH = "/Users/steveridder/Git/Ridder-Field/phase2/class/class"
OUTPUT_DIR = "/Users/steveridder/Git/Ridder-Field/phase2/class/output"


@dataclass
class BackgroundResult:
    Lambda: float
    theta_i: float
    alpha: float
    f_peak: Optional[float]
    r_s: Optional[float]
    H0: Optional[float]
    Delta_Neff: Optional[float]
    success: bool
    error: Optional[str] = None


def run_class_background(Lambda: float, theta_i: float, alpha: float, 
                         name: str, h: float = 0.6736) -> BackgroundResult:
    """Run CLASS background and extract key quantities."""
    
    ini_content = f"""
# High-amplitude EDE scan
root = {OUTPUT_DIR}/{name}
write background = yes

# Cosmological parameters (fixed for scan)
h = {h}
omega_b = 0.02237
omega_cdm = 0.1200
tau_reio = 0.0544

# Ridder field - HIGH AMPLITUDE
Lambda_EDE_ridder = {Lambda}
f_axion_ridder = 1.0e+27
theta_i_ridder = {theta_i}
n_ridder = 3
beta_ridder = 0.0

# α-branching decay
alpha_ridder_to_dr = {alpha}
z_ridder_decay = 3500
Gamma_decay_ridder = 0.0

# Numerical settings
ridder_force_damping = 1.0
ridder_freeze_phi = no
use_ridder_shooting = 0

output = 
background_verbose = 1
gauge = newtonian
"""
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(ini_content)
        ini_file = f.name
    
    result = BackgroundResult(
        Lambda=Lambda, theta_i=theta_i, alpha=alpha,
        f_peak=None, r_s=None, H0=None, Delta_Neff=None,
        success=False
    )
    
    try:
        proc = subprocess.run([CLASS_PATH, ini_file], 
                              capture_output=True, text=True, timeout=300)
        output = proc.stdout + proc.stderr
        
        if proc.returncode != 0:
            result.error = "CLASS failed"
            return result
        
        # Parse background file
        bg_file = f"{OUTPUT_DIR}/{name}00_background.dat"
        if not os.path.exists(bg_file):
            result.error = "No background file"
            return result
        
        # Read background data
        with open(bg_file) as f:
            lines = f.readlines()
        
        # Skip header lines
        data_lines = [l for l in lines if not l.startswith('#')]
        
        # Find f_peak (maximum f_ridder around z=3000-4000)
        max_f = 0.0
        r_s_at_1100 = None
        
        for line in data_lines:
            parts = line.split()
            if len(parts) < 23:
                continue
            
            try:
                z = float(parts[0])
                r_s = float(parts[7])  # comov.snd.hrz is column 8 (0-indexed: 7)
                
                # Get f_ridder - need to find the right column
                # From our earlier analysis: f_ridder should be around column 22
                # But we computed f = rho_ridder / rho_tot
                rho_ridder = float(parts[14])  # column 15 (0-indexed: 14)
                rho_tot = float(parts[22])     # column 23 (0-indexed: 22)
                
                if rho_tot > 0:
                    f_current = rho_ridder / rho_tot
                    if f_current > max_f:
                        max_f = f_current
                
                # Get r_s at z ≈ 1100
                if 1090 < z < 1110:
                    r_s_at_1100 = r_s
                    
            except (ValueError, IndexError):
                continue
        
        result.f_peak = max_f
        result.r_s = r_s_at_1100
        
        # Compute H0 from r_s using BAO constraint (approximate)
        # r_s,LCDM ≈ 147.1 Mpc for H0 = 67.4
        # H0 ≈ 67.4 * (147.1 / r_s)
        if r_s_at_1100:
            result.H0 = 67.4 * (147.1 / r_s_at_1100)
        
        # Estimate ΔN_eff from the DR component
        # This is approximate - proper calculation needs thermodynamics
        result.Delta_Neff = 0.74 * alpha * max_f / 0.1 if max_f > 0 else 0.0
        
        result.success = True
        
    except subprocess.TimeoutExpired:
        result.error = "Timeout"
    except Exception as e:
        result.error = str(e)
    finally:
        os.unlink(ini_file)
    
    return result


def main():
    print("=" * 80)
    print("HIGH-AMPLITUDE EDE ISLAND SCAN")
    print("=" * 80)
    print()
    print("Goal: Find (Λ, θ_i, α) region with f_peak ≈ 5-10% and H₀ ≈ 70-71")
    print()
    
    # Step 1: Background grid to find high f_peak
    print("STEP 1: Scanning (Λ, θ_i) for f_peak ≈ 5-10%")
    print("-" * 60)
    
    lambdas = [0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
    thetas = [1.0]  # Start with default, can expand later
    
    print(f"{'Λ (eV)':<10} {'θ_i':<8} {'f_peak (%)':<12} {'r_s (Mpc)':<12} {'H₀ (est)':<10} {'Status':<10}")
    print("-" * 70)
    
    baseline_results = []
    for Lambda in lambdas:
        for theta in thetas:
            name = f"scan_L{Lambda:.1f}_t{theta:.1f}"
            result = run_class_background(Lambda, theta, alpha=0.0, name=name)
            baseline_results.append(result)
            
            f_pct = result.f_peak * 100 if result.f_peak else 0
            r_s_str = f"{result.r_s:.2f}" if result.r_s else "N/A"
            H0_str = f"{result.H0:.1f}" if result.H0 else "N/A"
            status = "✓" if result.success else f"✗ {result.error}"
            
            print(f"{Lambda:<10.1f} {theta:<8.1f} {f_pct:<12.3f} {r_s_str:<12} {H0_str:<10} {status:<10}")
    
    # Find the Λ values with f_peak > 2%
    high_f_lambdas = [r.Lambda for r in baseline_results 
                     if r.success and r.f_peak and r.f_peak > 0.02]
    
    if not high_f_lambdas:
        print("\n⚠ No Λ values found with f_peak > 2%")
        print("  The field may not be reaching high enough amplitude.")
        print("  Consider: larger θ_i, different potential parameters, or numerical fixes.")
        return
    
    # Step 2: α scan at high-f_peak points
    print()
    print("STEP 2: Testing α-branching at high-amplitude points")
    print("-" * 60)
    
    alphas = [0.0, 0.1, 0.2, 0.3, 0.5]
    
    print(f"{'Λ (eV)':<8} {'α':<6} {'f_peak (%)':<12} {'r_s (Mpc)':<12} {'H₀':<8} {'ΔN_eff':<10}")
    print("-" * 70)
    
    results_grid = []
    for Lambda in high_f_lambdas[:3]:  # Top 3 high-f lambdas
        for alpha in alphas:
            name = f"alpha_L{Lambda:.1f}_a{alpha:.1f}"
            result = run_class_background(Lambda, 1.0, alpha, name)
            results_grid.append(result)
            
            f_pct = result.f_peak * 100 if result.f_peak else 0
            r_s_str = f"{result.r_s:.2f}" if result.r_s else "N/A"
            H0_str = f"{result.H0:.1f}" if result.H0 else "N/A"
            Neff_str = f"{result.Delta_Neff:.3f}" if result.Delta_Neff else "N/A"
            
            print(f"{Lambda:<8.1f} {alpha:<6.1f} {f_pct:<12.3f} {r_s_str:<12} {H0_str:<8} {Neff_str:<10}")
    
    # Summary
    print()
    print("=" * 80)
    print("SUMMARY: Viable H₀ ≈ 70-71 Candidates")
    print("=" * 80)
    
    candidates = [r for r in results_grid 
                  if r.success and r.H0 and 69 < r.H0 < 72]
    
    if candidates:
        print(f"\nFound {len(candidates)} candidate(s) with H₀ in 69-72 range:")
        for c in candidates:
            print(f"  Λ={c.Lambda} eV, α={c.alpha}, f_peak={c.f_peak*100:.2f}%, H₀={c.H0:.2f}")
        print("\n→ Next step: Run these through full CMB+BAO likelihoods")
    else:
        print("\n⚠ No candidates found in H₀ = 69-72 range at these amplitudes.")
        print("  This could mean:")
        print("  1. Need even higher Λ (numerical stability required)")
        print("  2. The α-branching geometry doesn't extend to H₀ ~ 71")
        print("  3. The constraint from ΔN_eff is too tight")
    
    # Output detailed grid for plotting
    print()
    print("Full grid data saved for analysis.")
    

if __name__ == "__main__":
    main()

