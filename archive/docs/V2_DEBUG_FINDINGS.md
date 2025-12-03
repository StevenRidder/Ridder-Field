# V2 Debug Findings - November 23, 2025

## ROOT CAUSE IDENTIFIED

**The Ridder field equation of motion is NOT being integrated.**

### Evidence

1. **φ is frozen**: Field value stays at exactly φ = 2.00 throughout all of cosmic history
   - Initial value: φ_ini = θ_i × f = 2.0 × 1.0 = 2.00
   - At z=10¹⁴: φ = 2.00
   - At z=1000: φ = 2.00
   - At z=0: φ = 2.00

2. **No derivative calculations**: Added debug prints to `background_derivs` Ridder block
   - `DERIVS_ENTRY` print: **NEVER appears**
   - `RIDDER DERIVS CALLED` print: **NEVER appears**
   - `DERIVS` (actual derivatives) print: **NEVER appears**

3. **Energy density is negligible**: ρ_ridder ~ 10⁻¹⁰¹ while ρ_tot ~ 10¹
   - Field has zero cosmological impact
   - This is a consequence of φ being frozen, not the cause

### What IS Working

1. ✅ Parameters are being read correctly
   - `Lambda_EDE_ridder = 10.0`
   - `theta_i_ridder = 2.0`
   - `f_axion_ridder = 1.0`
   - `n_ridder = 3`

2. ✅ `has_ridder` flag is set correctly in `background_init`
   - Debug print shows: `has_ridder=1`

3. ✅ Initial conditions are set
   - `phi_ini = 2.0` ✓
   - `phi_prime_ini = 0.0` ✓

4. ✅ Potential is calculated correctly
   - V(φ=2.0) = Λ⁴ × [1-cos(2.0)]³ = 10⁴ × 1.416³ ≈ 2.84×10⁴ eV⁴ ✓

5. ✅ `background_functions` is being called
   - `V_RIDDER_RAW` prints appear
   - `RIDDER DEBUG (adding to rho_tot)` prints appear

### What is NOT Working

1. ❌ `background_derivs` Ridder block is NEVER entered
   - `if (pba->has_ridder == _TRUE_)` condition is never true during integration
   - This means either:
     - `pba->has_ridder` is being reset to FALSE somewhere
     - OR the integration is not happening at all
     - OR a different `pba` structure is being used

2. ❌ Field equation of motion is not integrated
   - dφ/dlna = φ'/(aH) is never calculated
   - dφ'/dlna = -2φ' - (a/H)dV is never calculated

3. ❌ φ' stays at zero
   - Initial: φ' = 0
   - Throughout evolution: φ' = 0
   - Field never starts rolling

### Next Steps to Fix

1. **Find why `background_derivs` Ridder block is not entered**
   - Check if `pba->has_ridder` is being reset
   - Check if integration vector includes Ridder indices
   - Check if `bi_size` includes Ridder field

2. **Verify integration indices are set up correctly**
   - Lines 1299-1300 define `index_bi_phi_ridder` and `index_bi_phi_prime_ridder`
   - Check if these are before or after `bi_size` is set (line 1319)

3. **Check if Ridder field is in the integration vector**
   - `pvecback_integration` should include φ and φ'
   - Initial values should be copied correctly

### Unit Conversion Issues (Secondary)

The unit conversions were also wrong, but this is a secondary issue. The primary issue is that the field is not evolving at all.

**Original (wrong):**
```c
double factor_V = eV_to_Mpc_inv * eV_to_Mpc_inv; // eV² → Mpc⁻²
```

**Current (still wrong):**
```c
double factor_V = 1.0 / (3.0 * M_Pl_eV * M_Pl_eV); // eV⁴ → Mpc⁻²
```

**Correct (to be implemented after fixing integration):**
```c
// V is in eV⁴, need to convert to CLASS H² units (Mpc⁻²)
// ρ = V / (8πG) where G = 1/(8π M_Pl²) in natural units
// So ρ = V * M_Pl² / (8π) but CLASS uses H² = 8πG ρ / 3
// So we need V / (3 M_Pl²) to get H² units
double factor_V = 1.0 / (3.0 * M_Pl_eV * M_Pl_eV);
```

But this doesn't matter until the field actually evolves!

### Status

**BLOCKED**: Cannot proceed with V2 testing until the integration issue is fixed.

The field must evolve (φ must change with time) for V2 to have any cosmological effect.

