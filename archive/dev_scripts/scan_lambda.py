#!/usr/bin/env python3
"""
Scan Lambda to find value that gives f_EDE ~ 10%
This is a manual shooting procedure until we implement it in C
"""

from classy import Class
import numpy as np

def measure_fede(Lambda_eV, theta_i=3.0, f_axion=2.435e27):
    """
    Run CLASS with given Lambda and measure peak f_EDE
    Returns (f_peak, z_peak) or None if fails
    """
    try:
        cosmo = Class()
        cosmo.set({
            'H0': 70.0,
            'omega_b': 0.0224,
            'omega_cdm': 0.120,
            'A_s': 2.1e-9,
            'n_s': 0.965,
            'tau_reio': 0.054,
            'YHe': 0.245,  # Bypass BBN
            
            # Ridder parameters
            'Lambda_EDE_ridder': Lambda_eV,
            'theta_i_ridder': theta_i,
            'beta_ridder': 0.0,
            'f_axion_ridder': f_axion,
            'n_ridder': 3,
            
            'gauge': 'newtonian',
            'output': '',  # Background only
        })
        
        cosmo.compute()
        
        # Sample z from 1000 to 10000
        z_samples = np.logspace(3, 4.5, 50)
        f_ede_vals = []
        
        for z in z_samples:
            try:
                f = cosmo.Omega_ridder(z)
                f_ede_vals.append((z, f))
            except:
                pass
        
        if not f_ede_vals:
            return None
            
        # Find peak
        z_arr, f_arr = zip(*f_ede_vals)
        idx_max = np.argmax(f_arr)
        
        cosmo.struct_cleanup()
        cosmo.empty()
        
        return (f_arr[idx_max], z_arr[idx_max])
        
    except Exception as e:
        print(f"  Lambda={Lambda_eV:.2e}: Failed ({str(e)[:50]})")
        return None

# Scan Lambda values
print("=" * 70)
print("LAMBDA SCAN: Finding Λ for f_EDE ~ 10%")
print("=" * 70)
print()

# Start from empirical result: Lambda~10^14 gave ~70%
# Target: 10% = 0.14 × 70%, so Lambda ~ 10^14 × (0.14)^0.25 ~ 6×10^13

lambda_values = [
    3e13,
    5e13,
    7e13,
    1e14,
    2e14,
]

print(f"{'Lambda (eV)':>15} {'f_EDE_peak':>12} {'z_peak':>10}")
print("-" * 40)

results = []
for Lambda in lambda_values:
    result = measure_fede(Lambda)
    if result:
        f_peak, z_peak = result
        results.append((Lambda, f_peak, z_peak))
        print(f"{Lambda:>15.2e} {f_peak:>12.4f} {z_peak:>10.1f}")
    else:
        print(f"{Lambda:>15.2e} {'FAILED':>12} {'-':>10}")

print()
print("=" * 70)

if results:
    # Find closest to target f_EDE = 0.10
    target = 0.10
    best = min(results, key=lambda x: abs(x[1] - target))
    Lambda_best, f_best, z_best = best
    
    print(f"Best match: Λ = {Lambda_best:.2e} eV")
    print(f"  → f_EDE = {f_best:.3f} at z = {z_best:.0f}")
    print()
    
    if abs(f_best - target) < 0.05:
        print("✓ Good match! Use this Lambda for further testing.")
    else:
        error = f_best - target
        # f_EDE ∝ Λ⁴, so Λ_new = Λ_old × (f_target/f_old)^0.25
        Lambda_suggested = Lambda_best * (target / f_best)**0.25
        print(f"Suggested refinement: Λ ≈ {Lambda_suggested:.2e} eV")

