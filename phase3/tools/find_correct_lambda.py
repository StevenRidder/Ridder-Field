#!/usr/bin/env python3
"""
Find Correct Lambda_EDE

Goal: Find Lambda_EDE value that gives f_EDE ~ 10% at z ~ 3000
"""

import numpy as np
from classy import Class

def test_lambda(Lambda_EDE, theta_i=2.0, target_f_EDE=0.10):
    """
    Test a Lambda_EDE value and return peak f_EDE.
    """
    params = {
        'output': 'tCl',
        'H0': 70.0,
        'omega_b': 0.0224,
        'omega_cdm': 0.120,
        'A_s': 2.1e-9,
        'n_s': 0.965,
        'tau_reio': 0.054,
        'Lambda_EDE_ridder': Lambda_EDE,
        'theta_i_ridder': theta_i,
        'beta_ridder': 0.015,
        'f_axion_ridder': 1.0,
        'n_ridder': 3,
        'gauge': 'newtonian',
    }
    
    try:
        cosmo = Class()
        cosmo.set(params)
        cosmo.compute()
        
        bg = cosmo.get_background()
        z = bg['z']
        rho_scf = bg['(.)rho_ridder']
        rho_tot = bg['(.)rho_tot']
        
        f_EDE = rho_scf / rho_tot
        peak_f_EDE = np.max(f_EDE)
        peak_z = z[np.argmax(f_EDE)]
        
        cosmo.struct_cleanup()
        cosmo.empty()
        
        return {
            'success': True,
            'peak_f_EDE': peak_f_EDE,
            'peak_z': peak_z,
            'Lambda_EDE': Lambda_EDE
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'Lambda_EDE': Lambda_EDE
        }

print("="*70)
print("FINDING CORRECT LAMBDA_EDE FOR f_EDE ~ 10%")
print("="*70)
print("")

# Binary search for correct Lambda
Lambda_values = [10, 100, 1000, 10000, 100000, 1000000]

print("Testing Lambda_EDE values...")
print("")

results = []
for Lambda in Lambda_values:
    print(f"Testing Lambda_EDE = {Lambda:.0e}...", end=" ")
    result = test_lambda(Lambda)
    
    if result['success']:
        f_EDE_percent = result['peak_f_EDE'] * 100
        print(f"f_EDE = {f_EDE_percent:.2f}% at z = {result['peak_z']:.0f}")
        results.append(result)
        
        # Stop if we're in the right ballpark
        if 5 < f_EDE_percent < 20:
            print(f"  ✓ Found good range!")
            break
    else:
        print(f"FAILED: {result['error']}")

print("")
print("="*70)
print("RESULTS")
print("="*70)

if results:
    for r in results:
        f_EDE_percent = r['peak_f_EDE'] * 100
        status = "✓" if 5 < f_EDE_percent < 20 else "✗"
        print(f"{status} Lambda_EDE = {r['Lambda_EDE']:.2e}: f_EDE = {f_EDE_percent:.2f}% at z = {r['peak_z']:.0f}")
    
    # Find closest to 10%
    best = min(results, key=lambda x: abs(x['peak_f_EDE'] - 0.10))
    print("")
    print(f"BEST MATCH: Lambda_EDE = {best['Lambda_EDE']:.2e}")
    print(f"  f_EDE = {best['peak_f_EDE']*100:.2f}% at z = {best['peak_z']:.0f}")
else:
    print("❌ No successful runs")

print("="*70)

