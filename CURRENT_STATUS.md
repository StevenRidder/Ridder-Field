# Current Status: Ridder Field Implementation

**Date:** 2025-11-21  
**Status:** ⚠️ **IMPLEMENTATION COMPLETE, BUT RESULTS NOT MATCHING**

## What's Working

1. ✅ **Code pushed to GitHub** - All modifications backed up in `patches/class/`
2. ✅ **Compilation successful** - CLASS compiles without errors
3. ✅ **Potential function** - V_scf, dV_scf, ddV_scf implemented correctly
4. ✅ **Parameter reading** - Lambda_EDE_ridder, f_axion_ridder, theta_i_ridder, beta_ridder all read
5. ✅ **Initial conditions** - phi_ini = 0.862423 (theta_i * f) computed correctly
6. ✅ **Potential value** - V_i = 3.43 (positive, correct magnitude)

## What's NOT Working

1. ❌ **Field not evolving** - phi stays constant at 0.862423
2. ❌ **Energy density too small** - rho_scf = 3.4e-36 (should be ~1.14)
3. ❌ **f_EDE = 0%** - Field contributes nothing to energy budget
4. ❌ **r_s = 143.55 Mpc** - Should be ~139.06 Mpc

## Root Cause Hypothesis

The potential V = 3.43 is being computed correctly, but when used in the energy density calculation:
```c
rho_scf = (phi_prime^2/(2*a^2) + V_scf(pba,phi))/3.;
```
we get rho = 3.4e-36 instead of the expected ~1.14.

This suggests a **unit conversion issue**. CLASS expects:
- V(φ) in units of `m_pl^2/Mpc^2` (from background.c line 2919)
- But our Lambda = 1.0 might be in wrong units

## Next Steps

1. Check if Lambda_EDE_ridder needs unit conversion (maybe multiply by some factor?)
2. Verify that LambdaEDE4 should be Lambda (not Lambda^4) and we raise it correctly
3. Check if there's a missing normalization factor in the potential
4. Compare with working implementation from last night's results

## Files Modified

- `phase2/class/include/background.h` - Added scf_pot_ridder enum
- `phase2/class/source/input.c` - Parameter reading, initial conditions
- `phase2/class/source/background.c` - Potential functions (V, dV, ddV)
- `phase2/class/source/perturbations.c` - 3-term coupling (already implemented)

## Configuration

Current `.ini` file (`phase3/ridder_smoketest_spec.ini`):
```ini
Lambda_EDE_ridder = 1.0
f_axion_ridder = 1e27
theta_i_ridder = 2.1
beta_ridder = 0.01
scf_parameters = 0.41, 0.0, 3
```

Expected results (from last night):
- r_s = 139.06 Mpc
- f_EDE peak = 15.46% at z = 6697
- H₀ ≈ 71 km/s/Mpc

