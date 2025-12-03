#!/usr/bin/env python3
"""
DEBUG: Test CLASS output directly
=================================
This script tests CLASS computation to understand why D_ell values are zero.
"""
import numpy as np
import sys
import os

# Constants
T_CMB = 2.7255e6  # μK (2.7255 K in microKelvin)
T_CMB_SQ = T_CMB ** 2  # ~ 7.4e12 μK²

print("=" * 70)
print("CLASS OUTPUT DEBUGGING")
print("=" * 70)

# Check which CLASS is loaded
print("\n1. CHECKING CLASS INSTALLATION")
print("-" * 40)

try:
    from classy import Class
    print(f"  ✓ CLASS imported successfully")
    print(f"  Module location: {Class.__module__}")
    
    # Check if this is the Ridder CLASS
    import classy
    classy_path = classy.__file__
    print(f"  classy path: {classy_path}")
except ImportError as e:
    print(f"  ✗ Cannot import CLASS: {e}")
    sys.exit(1)

# Test basic cosmology first (no EDE)
print("\n2. TEST BASIC ΛCDM (NO EDE)")
print("-" * 40)

cosmo = Class()
basic_params = {
    'output': 'tCl pCl lCl',
    'l_max_scalars': 3000,
    'lensing': 'yes',
    # Standard ΛCDM parameters (Planck 2018)
    'H0': 67.4,
    'omega_b': 0.02237,
    'omega_cdm': 0.1200,
    'A_s': 2.1e-9,
    'n_s': 0.9649,
    'tau_reio': 0.0544,
}

print(f"  Setting parameters:")
for k, v in basic_params.items():
    print(f"    {k}: {v}")

cosmo.set(basic_params)
try:
    cosmo.compute()
    print(f"  ✓ CLASS computed successfully")
except Exception as e:
    print(f"  ✗ CLASS computation failed: {e}")
    sys.exit(1)

# Get spectra
cl = cosmo.lensed_cl(3000)
print(f"\n  Raw C_ell from CLASS:")
print(f"    cl['tt'][2] = {cl['tt'][2]:.6e}")
print(f"    cl['tt'][100] = {cl['tt'][100]:.6e}")
print(f"    cl['tt'][500] = {cl['tt'][500]:.6e}")
print(f"    cl['tt'][1000] = {cl['tt'][1000]:.6e}")

# Check if these are in physical units or normalized
# CLASS can return either:
#   - Normalized (dimensionless): C_ell ~ 10^-10
#   - Physical: C_ell in units of (2.7255K)^2
# 
# If C_ell ~ 10^-10, we need to multiply by T_CMB^2 to get μK²
# If C_ell ~ 10^3, it's already in μK² (but usually CLASS is normalized)

# Check magnitude to determine units
max_cl = np.max(cl['tt'][2:100])
print(f"\n  Max C_ell (ℓ=2-100): {max_cl:.6e}")

if max_cl < 1e-6:
    print(f"  → C_ell appears to be dimensionless (normalized by T_CMB²)")
    print(f"  → Need to multiply by T_CMB² = {T_CMB_SQ:.3e} μK²")
    need_tcmb = True
else:
    print(f"  → C_ell appears to already be in physical units")
    need_tcmb = False

# Convert to D_ell
ell = np.arange(3001)
factor = ell * (ell + 1) / (2 * np.pi)

# D_ell in μK²
if need_tcmb:
    D_tt = cl['tt'] * factor * T_CMB_SQ
else:
    D_tt = cl['tt'] * factor

print(f"\n  D_ell (should be in μK²):")
print(f"    D_TT[100] = {D_tt[100]:.2f} μK²  (expected ~1000-2000)")
print(f"    D_TT[500] = {D_tt[500]:.2f} μK²  (expected ~3000-5000)")
print(f"    D_TT[1000] = {D_tt[1000]:.2f} μK²  (expected ~500-1500)")
print(f"    Max D_TT = {np.max(D_tt[2:]):.2f} μK²  (expected ~6000)")

# Sanity check
if D_tt[100] > 100 and D_tt[100] < 10000:
    print(f"  ✓ D_ell values look physically reasonable!")
else:
    print(f"  ✗ D_ell values are WRONG - check units/conversion")

cosmo.struct_cleanup()

# Test with EDE (Ridder field)
print("\n3. TEST WITH RIDDER EDE")
print("-" * 40)

cosmo2 = Class()
ede_params = basic_params.copy()
ede_params.update({
    'gauge': 'newtonian',  # Required for Ridder
    'Lambda_EDE_ridder': 1.853,  # Typical chain value
    'f_axion_ridder': 1.0e+27,
    'theta_i_ridder': 1.0,
    'beta_ridder': 0.0,
    'n_ridder': 3,
})

print(f"  Adding EDE parameters:")
print(f"    Lambda_EDE_ridder: {ede_params['Lambda_EDE_ridder']}")
print(f"    f_axion_ridder: {ede_params['f_axion_ridder']}")
print(f"    gauge: {ede_params['gauge']}")

cosmo2.set(ede_params)
try:
    cosmo2.compute()
    print(f"  ✓ CLASS with EDE computed successfully")
except Exception as e:
    print(f"  ✗ CLASS with EDE failed: {e}")
    print(f"  This might mean the Ridder CLASS is not loaded!")
    cosmo2.struct_cleanup()
    sys.exit(1)

cl_ede = cosmo2.lensed_cl(3000)
print(f"\n  Raw C_ell from CLASS (EDE):")
print(f"    cl['tt'][100] = {cl_ede['tt'][100]:.6e}")
print(f"    cl['tt'][500] = {cl_ede['tt'][500]:.6e}")
print(f"    cl['tt'][1000] = {cl_ede['tt'][1000]:.6e}")

# Convert EDE D_ell
if need_tcmb:
    D_tt_ede = cl_ede['tt'] * factor * T_CMB_SQ
else:
    D_tt_ede = cl_ede['tt'] * factor

print(f"\n  D_ell (EDE):")
print(f"    D_TT[100] = {D_tt_ede[100]:.2f} μK²")
print(f"    D_TT[500] = {D_tt_ede[500]:.2f} μK²")
print(f"    D_TT[1000] = {D_tt_ede[1000]:.2f} μK²")

# Compute difference (the template)
diff = D_tt_ede - D_tt
rel_diff = diff / D_tt
print(f"\n  Difference (EDE - ΛCDM):")
print(f"    ΔD_TT[100] = {diff[100]:.2f} μK² ({rel_diff[100]*100:.2f}%)")
print(f"    ΔD_TT[500] = {diff[500]:.2f} μK² ({rel_diff[500]*100:.2f}%)")
print(f"    ΔD_TT[1000] = {diff[1000]:.2f} μK² ({rel_diff[1000]*100:.2f}%)")
print(f"    Max |ΔD_TT| = {np.max(np.abs(diff[2:])):.2f} μK²")

if np.max(np.abs(diff[2:])) > 0.1:
    print(f"  ✓ EDE makes a measurable difference (template is non-zero)")
else:
    print(f"  ✗ EDE makes no difference - check Ridder parameters")

cosmo2.struct_cleanup()

# Check what the actual chain values look like
print("\n4. CHECK CHAIN PARAMETER VALUES")
print("-" * 40)

chain_dir = os.path.expanduser("~/Ridder-Field/phase3/chains")
lcdm_files = sorted([f for f in os.listdir(chain_dir) if 'act_world_lcdm' in f and f.endswith('.1.txt')])
ede_files = sorted([f for f in os.listdir(chain_dir) if 'act_world_ede' in f and f.endswith('.1.txt')])

if lcdm_files:
    lcdm_chain = os.path.join(chain_dir, lcdm_files[0])
    print(f"  Reading LCDM chain: {lcdm_files[0]}")
    
    with open(lcdm_chain, 'r') as f:
        header = f.readline()
        cols = header[1:].strip().split() if header.startswith('#') else []
    
    print(f"    Columns ({len(cols)}): {cols[:10]}...")
    
    data = np.loadtxt(lcdm_chain)
    mlp_idx = cols.index('minuslogpost') if 'minuslogpost' in cols else 0
    best_idx = np.argmin(data[:, mlp_idx])
    
    print(f"    Best-fit sample index: {best_idx}")
    print(f"    Key parameters at best-fit:")
    
    for param in ['H0', 'logA', 'n_s', 'omega_b', 'omega_cdm', 'tau_reio']:
        if param in cols:
            idx = cols.index(param)
            val = data[best_idx, idx]
            print(f"      {param}: {val:.6f}")
            
    # Check if A_s needs conversion
    if 'logA' in cols:
        logA = data[best_idx, cols.index('logA')]
        A_s = 1e-10 * np.exp(logA)
        print(f"      A_s (from logA): {A_s:.6e}")
else:
    print(f"  No LCDM chains found in {chain_dir}")

if ede_files:
    ede_chain = os.path.join(chain_dir, ede_files[0])
    print(f"\n  Reading EDE chain: {ede_files[0]}")
    
    with open(ede_chain, 'r') as f:
        header = f.readline()
        cols = header[1:].strip().split() if header.startswith('#') else []
    
    data = np.loadtxt(ede_chain)
    mlp_idx = cols.index('minuslogpost') if 'minuslogpost' in cols else 0
    best_idx = np.argmin(data[:, mlp_idx])
    
    print(f"    Key parameters at best-fit:")
    for param in ['H0', 'logA', 'n_s', 'omega_b', 'omega_cdm', 'tau_reio', 'Lambda_EDE_ridder']:
        if param in cols:
            idx = cols.index(param)
            val = data[best_idx, idx]
            print(f"      {param}: {val:.6f}")
else:
    print(f"  No EDE chains found in {chain_dir}")

print("\n" + "=" * 70)
print("DIAGNOSIS SUMMARY")
print("=" * 70)

print("""
If D_ell values were zero in act_template_fit.py, possible causes:

1. MISSING T_CMB² CONVERSION
   - CLASS returns dimensionless C_ell (normalized by T_CMB²)
   - Must multiply by T_CMB² = 7.4e12 to get μK²
   - FIX: Add T_CMB_SQ factor to conversion

2. WRONG CLASS INSTALLATION
   - The Ridder CLASS might not be in PYTHONPATH
   - Standard CLASS would silently ignore EDE parameters
   - FIX: Ensure ~/.local/lib/python3.10/site-packages is in PYTHONPATH

3. PARAMETER EXTRACTION ISSUES
   - logA not being converted to A_s correctly
   - If A_s is too small, spectrum is tiny
   - FIX: Check A_s value explicitly

The fix should be applied to act_template_fit.py:
- Add T_CMB_SQ = (2.7255e6)**2 constant
- Multiply C_ell by T_CMB_SQ when converting to D_ell
""")
