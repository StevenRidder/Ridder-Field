# Ridder Field Unit Conversion Fix - Status

## Date: November 24, 2025

## Summary

Successfully corrected the unit conversion constant for `eV_to_Mpc_inv` throughout the Ridder field implementation in CLASS. The dimensional logic is now correct, but the code crashes immediately after setting initial conditions.

## Changes Made

### 1. Corrected `eV_to_Mpc_inv` Constant

**Fixed in three locations:**
- `background_functions` (line ~530)
- `background_derivs` (line ~3120)
- `background_initial_conditions` (line ~2530)

**OLD (WRONG):**
```c
double eV_to_Mpc_inv = 1.64e-16;  // INVERTED! This is 1 Mpc^-1 in eV
```

**NEW (CORRECT):**
```c
double eV_to_Mpc_inv = 1.56e29;   // 1 eV ≈ 1.56×10²⁹ Mpc⁻¹
```

**Derivation:**
- 1 eV ≈ 5.07 × 10⁶ m⁻¹ (from ℏc = 197 eV·nm)
- 1 Mpc ≈ 3.09 × 10²² m
- Therefore: 1 eV ≈ 5.07×10⁶ / 3.09×10²² ≈ 1.56×10²⁹ Mpc⁻¹

### 2. Consistent Unit Conversions

**Energy Density (ρ):**
```c
// Kinetic: (φ'/a)² in eV²·Mpc⁻², divide by (3 M_Pl²) → Mpc⁻²
double kinetic_Mpc_inv2 = kinetic_eV2_Mpc_inv2 / (3.0 * M_Pl_eV * M_Pl_eV);

// Potential: V(φ) in eV⁴, convert to Mpc⁻²
double potential_Mpc_inv2 = potential_eV4 * (eV_to_Mpc_inv² / (3 M_Pl²));
```

**Force Term (dV/dφ):**
```c
// dV_ridder returns eV³, convert to eV·Mpc⁻² for evolution equation
double dV_conversion = eV_to_Mpc_inv * eV_to_Mpc_inv;  // eV³ → eV·Mpc⁻²
double dV_val_units = dV_ridder(pba, phi) * dV_conversion;
```

**Slow-Roll ICs:**
```c
// φ' ≈ -(a/2H) · dV/dφ, where dV/dφ is in eV·Mpc⁻²
double dV_for_slowroll = dV_eV3 * (eV_to_Mpc_inv * eV_to_Mpc_inv);
double phi_prime_ini = -c_slow * (a_ini / (2.0 * H_ini)) * dV_for_slowroll;
```

### 3. Removed Unused Variable

Removed unused `H_local` declaration in `background_functions`.

## Current Status

### ✅ FIXED
1. Unit conversion constant magnitude (was off by 10⁴⁵!)
2. Dimensional consistency across all three code blocks
3. Comments now correctly explain unit flow

### ⚠️ OUTSTANDING ISSUE

**CLASS crashes immediately after setting initial conditions, regardless of `ridder_c_slow` value.**

**Observed Behavior:**
```
RIDDER IC: a_ini=1.000e-14 z_ini=99999999999999.0 H_ini=2.183e+22 Mpc^-1
  phi_ini=3.653e+27 eV, phi_prime_ini=0.000e+00 eV/Mpc
  dV/dphi=1.061e+13 eV^3, dV_slowroll=2.583e+71 eV·Mpc^-2, c_slow=0.00

Error running background_init 
=>
```

**Characteristics:**
- Crash occurs after IC computation but before integration starts
- No derivative call debug prints appear
- No detailed error message (just "Error running background_init")
- Occurs with both `c_slow=0.0` (frozen) and `c_slow=1.0` (slow-roll)
- Occurs for all Lambda values tested by the shooter

### 📋 REMAINING TASKS

1. **Debug the crash:**
   - Check if `class_test` is triggering
   - Look for NaN/Inf checks failing
   - Verify background table allocation
   - Check if `background_functions` is crashing on first call

2. **After crash is fixed:**
   - Gate debug prints with `background_verbose`
   - Implement `dp_dloga` contribution for Ridder field
   - Test with physical parameter ranges

3. **Physics validation:**
   - Plot Ω_ridder(a) and w_ridder(a)
   - Verify EDE peak location and amplitude
   - Check field dynamics (onset, peak, decay)

## Physics Notes

With corrected units, the slow-roll IC formula gives:
```
phi_prime_ini = -c_slow · (a/2H) · dV/dφ
```

At a = 10⁻¹⁴, H = 2.18×10²² Mpc⁻¹ (Planck scale):
- With c_slow = 1.0: φ'_ini ≈ -5.9×10³⁴ eV/Mpc (enormous!)
- With c_slow = 0.0: φ'_ini = 0 (strictly frozen)

The huge slow-roll value suggests:
1. At such early times (z ~ 10¹⁴), Hubble friction is dominant
2. Field should remain frozen until H ~ m_eff
3. May need adaptive c_slow or different IC strategy

## Files Modified

- `phase2/class/source/background.c` (or `phase2/class/background.c` on VM)
  - Lines ~530: `eV_to_Mpc_inv` in `background_functions`
  - Lines ~2530: `eV_to_Mpc_inv` in `background_initial_conditions`
  - Lines ~3120: `eV_to_Mpc_inv` in `background_derivs`
- `diagnostic_test.ini`: Set `ridder_c_slow = 0.0` for testing

## Next Debug Step

Add verbose error messages to identify exact failure point:
1. After `class_test` for ICs
2. Before/after first `background_functions` call
3. At start of integration loop

