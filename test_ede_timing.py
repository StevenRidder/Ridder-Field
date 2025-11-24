#!/usr/bin/env python3
"""
Test script to verify EDE timing with Lambda = 1.0 eV
Extracts full background evolution to see when field unfreezes
"""

from classy import Class
import numpy as np

cosmo = Class()

params = {
    'output': 'tCl',
    'H0': 70.0,
    'omega_b': 0.0224,
    'omega_cdm': 0.120,
    'A_s': 2.1e-9,
    'n_s': 0.965,
    'tau_reio': 0.054,
    
    # Ridder field parameters
    'Lambda_EDE_ridder': 1.0,      # 1 eV (EDE scale)
    'theta_i_ridder': 2.0,         # Initial angle
    'beta_ridder': 0.0,            # No coupling for now
    'f_axion_ridder': 1.0,         # f ~ M_Pl
    'n_ridder': 3,                 # Cosine cubed
    
    'gauge': 'newtonian',
}

print("=" * 70)
print("EDE TIMING TEST: Lambda = 1.0 eV")
print("=" * 70)
print()

cosmo.set(params)

print("Computing background evolution...")
try:
    cosmo.compute()
    print("✓ Computation successful!")
    print()
    
    # Get background at multiple scales
    z_samples = [1e14, 1e10, 1e8, 1e6, 1e5, 1e4, 5000, 3000, 1100, 100, 10, 1, 0]
    
    print("BACKGROUND EVOLUTION:")
    print("-" * 70)
    print(f"{'z':>10} {'a':>12} {'H [Mpc⁻¹]':>15} {'ρ_ridder':>15} {'f_ridder':>10}")
    print("-" * 70)
    
    for z in z_samples:
        try:
            bg = cosmo.get_background()
            # Look for ridder density in background
            # This will show when field becomes significant
            a = 1.0 / (1.0 + z)
            H = cosmo.Hubble(z)  # in km/s/Mpc
            
            print(f"{z:10.1e} {a:12.2e} {H:15.2e}")
            
        except Exception as e:
            print(f"{z:10.1e}  [Error: {e}]")
    
    print("-" * 70)
    print()
    
    # Try to get full background table
    print("Attempting to extract full background table...")
    bg = cosmo.get_background()
    print(f"Background columns: {list(bg.keys())}")
    
except Exception as e:
    print(f"✗ Computation failed: {e}")
    print()
    print("This likely means the field evolution is causing numerical issues.")
    print("Check the terminal output above for DERIVS messages.")

cosmo.struct_cleanup()
cosmo.empty()

print()
print("=" * 70)
print("Check terminal output above for DERIVS: messages showing field motion")
print("=" * 70)

