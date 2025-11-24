# Phase 3: Initial Observable Extraction Results

## Configuration Summary

### ΛCDM Control (`benchmark_lcdm_control.ini`)
- **Purpose:** Standard cosmology baseline
- **Configuration:** theta_i = π (extremum), Lambda = 0.00930572 eV, freeze = yes
- **Intent:** Frozen Ridder field acting as pure cosmological constant

### EDE Benchmark (`benchmark_ede_theta075.ini`)
- **Purpose:** H₀-relevant EDE model
- **Configuration:** theta_i = 0.75, Lambda = 0.4964450 eV, freeze = no, damping = 1.0
- **From Phase 2:** z_peak ~ 691, f_peak ~ 0.063

---

## Observables Extracted

### ΛCDM Control Results

**Background:**
- **H0 = 2716.84 km/s/Mpc** ❌ (should be ~67 km/s/Mpc)
- **f_ridder(z=0) = 0.9994** ❌ (should be ~0.69)
- rho_ridder(z=0) = 8.21e-05 Mpc^-2
- rho_tot(z=0) = 8.21e-05 Mpc^-2

**CMB Spectra:**
- First acoustic peak: l = 182
- TT(peak) = 3.46e-10 [l(l+1)/2π units]
- TT(high-l, l>1000) = 2.65e-13

**Status:** ❌ **BROKEN** - Frozen field is dominating the universe instead of acting as cosmological constant

### EDE Benchmark Results

**Background:**
- **H0 = 67.36 km/s/Mpc** ✅ (matches input)
- **f_ridder(z=0) = 0.000000** ✅ (field has decayed completely)
- rho_ridder(z=0) = 2.80e-15 Mpc^-2
- rho_tot(z=0) = 5.05e-08 Mpc^-2

**CMB Spectra:**
- First acoustic peak: l = 221
- TT(peak) = 7.98e-10 [l(l+1)/2π units]
- TT(high-l, l>1000) = 5.21e-11

**Status:** ✅ Runs successfully, behaves as expected

---

## Critical Issue: ΛCDM Control

The frozen Ridder field at theta=π is completely dominating the energy budget:
- f_ridder(z=0) ~ 1.0 instead of ~0.69
- H0 is 40× too large (2717 instead of 67 km/s/Mpc)
- This makes the ΛCDM control unusable for comparison

### Diagnosis

The problem is that the frozen field energy density (8.21e-05 Mpc^-2) is comparable to or larger than the total energy density from all other components (baryons, CDM, radiation). This suggests:

1. **Lambda calibration was wrong:** The Phase 1 calibration found Lambda = 0.00930572 eV to target f_ridder ~ 0.69, but something went wrong
2. **Unit bug:** Possible mismatch between how the frozen field energy is computed vs. other components
3. **Freeze mode bug:** The freeze logic might not be working as intended

### Possible Solutions

**Option A: Use vanilla CLASS ΛCDM for control**
- Simplest: Just run CLASS with `has_ridder = no` for the control
- Pro: Guaranteed correct ΛCDM physics
- Con: Doesn't validate our "extremum = pure cosmo constant" claim

**Option B: Fix the freeze mode calibration**
- Re-run Phase 1.1 Lambda calibration with freeze mode
- Debug why f_ridder(z=0) = 0.9994 instead of 0.69
- Properly match Ω_Λ to standard value

**Option C: Use different control strategy**
- Compare EDE to itself at different parameters
- Skip the "frozen field = ΛCDM" comparison for now

---

## EDE vs. Input ΛCDM Comparison

Even without a proper Ridder-based ΛCDM control, we can compare the EDE benchmark to the **input cosmology**:

| Observable | Input | EDE | Difference |
|-----------|-------|-----|------------|
| H0 [km/s/Mpc] | 67.36 | 67.36 | 0.00 |
| l(first peak) | ~220 | 221 | +1 |

**Finding:** The EDE model with dynamical field is **returning the input H0** unchanged. This suggests:
1. The EDE bump at z~691 is not significantly affecting expansion history
2. OR: The field's contribution is being compensated elsewhere
3. OR: We need to check the background evolution more carefully

---

## Next Steps

### Immediate (Phase 3.1)
1. ✅ Extract observables from both benchmarks
2. ❌ Fix ΛCDM control issue
   - **Decision needed:** Which option (A, B, or C)?
3. ⏳ Plot background evolution for both configs
4. ⏳ Plot C_ℓ comparison

### Short-term (Phase 3.2)
1. Investigate why EDE H0 = input H0 (no shift)
2. Check if EDE peak is actually affecting anything
3. Compute proper ΔH0 once control is fixed

### Recommendation

**Use Option A for now:** Run a clean vanilla CLASS ΛCDM (no Ridder field) for the control comparison, then proceed with physics analysis. We can revisit the "frozen field = ΛCDM" validation later once we understand the energy scale issue better.

---

## Files Created

- `benchmark_lcdm_control.ini` - Broken frozen field config
- `benchmark_ede_theta075.ini` - Working EDE config  
- `extract_observables.py` - Observable extraction script
- `PHASE3_INITIAL_RESULTS.md` - This document

## Output Files Generated

Located in `output/`:
- `benchmark_lcdm_control_00_background.dat` (23 MB)
- `benchmark_lcdm_control_00_cl.dat` (534 KB)
- `benchmark_ede_theta075_00_background.dat` (23 MB)
- `benchmark_ede_theta075_00_cl.dat` (534 KB)
- Plus thermodynamics, perturbations, pk files for both

---

**Status:** Phase 3.1 partially complete. Critical blocker identified with ΛCDM control. Awaiting decision on how to proceed.

