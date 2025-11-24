# Phase 1.2: Damping Continuity Test

## Objective

Verify that `ridder_force_damping` parameter smoothly interpolates between frozen and full dynamics, using the calibrated Λ_ΛCDM = 0.01655 eV.

## Background

In Phase 1.1A, we calibrated Lambda to make a **frozen** Ridder field exactly match Ω_Λ ≈ 0.69.

The `ridder_force_damping` parameter scales the force term in the Klein-Gordon equation:

```c
dy[phi_prime] = -2*phi_prime - damp * (a/H) * dV/dphi - damp * (a/H) * coupling_term
```

Where `damp ∈ [0, 1]`:
- **damp = 0.0**: Field is purely inertial (only Hubble friction), effectively frozen
- **damp = 1.0**: Full Klein-Gordon evolution with all forces
- **0 < damp < 1**: Reduced force, intermediate behavior

## Test Configuration

### Fixed Parameters (from Phase 1.1A calibration)
- `Lambda_EDE_ridder = 0.01654817 eV` (calibrated for f_ridder = 0.69)
- `f_axion_ridder = 2.435e27 eV` (M_Pl)
- `theta_i_ridder = 1.5` (partway down potential hill)
- `ridder_c_slow = 0.0` (zero initial velocity - frozen start)

### Variable Parameter
- `ridder_force_damping ∈ {0.0, 0.1, 0.3, 0.5, 0.7, 1.0}`

### Special Test Case
- At `damp = 0.0`, test both:
  - `ridder_freeze_phi = no` (relies on damping logic)
  - `ridder_freeze_phi = yes` (explicit freeze)
  - **These should give identical results**

## Expected Behavior

### 1. **Late-time f_ridder (Energy Fraction)**

Since we're starting with `phi_prime_ini = 0` and on a flat plateau (small dV/dphi at theta=1.5), we expect:

- **All damping values**: f_ridder ≈ 0.69 ± 0.01
  - The field should remain essentially frozen regardless of damping
  - Potential energy dominates throughout
  - Small variations possible due to numerical drift

**Why?** With c_slow=0, the field starts at rest. The Hubble friction term (-2*phi_prime) keeps it pinned even without force damping. The plateau means dV/dphi is small, so even full force (damp=1) shouldn't move the field much.

### 2. **Field Evolution (Δφ, Δφ')**

- **damp = 0.0**: |Δφ| ≈ 0, |Δφ'| ≈ 0 (numerical noise only)
- **damp > 0.0**: Slight drift possible, but should be << 1% of initial value
- **Monotonic**: Higher damping → potentially more evolution (but still minimal on plateau)

### 3. **Integration Performance**

- **All cases**: Should complete in < 10 seconds
  - We're on a plateau, so no stiffness issues
  - Field is effectively a cosmological constant
  - No oscillations or rapid dynamics

**If any run is slow (>30s)**, something is wrong:
- Potential not flat enough at theta=1.5?
- Numerical instability creeping in?
- Integrator struggling with tiny force terms?

### 4. **Freeze Mode Equivalence**

At `damp = 0.0`:
- `freeze=no` (damping-based freeze) should give same result as
- `freeze=yes` (explicit freeze)
- Differences should be < 10^-6 relative

This validates that our damping logic correctly implements a freeze when set to zero.

## Success Criteria

✅ **Pass if:**
1. All runs complete successfully (no crashes)
2. All f_ridder values within [0.68, 0.70] (±1% of calibrated value)
3. Maximum |Δφ| < 1e-4 * phi_initial (field essentially static)
4. All runtimes < 30s (no stiffness/performance issues)
5. damp=0.0 freeze=yes matches damp=0.0 freeze=no to high precision

⚠️ **Warning if:**
1. f_ridder varies by >2% across damping values
2. Any run takes >30s (performance degradation)
3. Systematic trend in Δφ vs damping (unexpected dynamics)

❌ **Fail if:**
1. Any run crashes or times out
2. f_ridder deviates by >5% from 0.69 (field not frozen)
3. Field shows significant evolution (|Δφ| > 1% of initial)
4. Freeze modes give different results (logic bug)

## Interpretation

### If all tests pass:
- ✅ Damping parameter works as designed
- ✅ Calibrated Lambda gives stable Λ-like behavior
- ✅ Field is safely on plateau (no unwanted dynamics)
- ✅ Numerical integration is stable and efficient
- → **Ready for Phase 1.3** (full pipeline verification)

### If f_ridder varies significantly:
- Field may not be on a flat plateau
- theta_i = 1.5 may be too close to steep part of potential
- Consider adjusting theta_i or checking V(phi) shape

### If any run is slow:
- Potential may have features causing stiffness
- Integrator may need tighter tolerances
- Debug with damping = 1e-8 to diagnose

### If freeze modes differ:
- Bug in damping logic or freeze flag implementation
- Check background_derivs Ridder block carefully
- Verify dy[phi] and dy[phi'] assignments

## Next Steps After Phase 1.2

**Phase 1.3**: Full pipeline to z=0
- Turn on thermodynamics and perturbations
- Verify H(z), distance measures, Omega(z) match ΛCDM baseline
- Compare against standard CLASS ΛCDM run

**Phase 2.1**: Gentle shooting activation
- Turn on `use_ridder_shooting = yes`
- Start with tiny f_EDE_target (0.01) to validate shooter
- Verify shooter converges and doesn't break calibrated Lambda

## Notes

- This phase uses the **same Lambda** for all tests - we're not searching, just verifying stability
- All tests use **freeze-like initial conditions** (c_slow=0) to ensure no initial kick
- The damping parameter is a **debug/diagnostic tool**, not a physics parameter
- In production EDE runs, we'll always use damp=1.0 (full physics)

## References

- Phase 1.1A calibration: `lambda_calibration_v2.log`
- Calibrated Lambda: `test_lcdm_recovery_calibrated.ini`
- Freeze validation: `FREEZE_AND_DAMPING_VALIDATED.md`

