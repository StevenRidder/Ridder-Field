# Lessons from Previous Work: What Failed and How It Was Fixed

**Date:** 2025-11-21  
**Purpose:** Document the failure modes and fixes from previous work to avoid repeating mistakes

---

## Key Findings from Documentation Review

### 1. **Architecture: Two Conflicting Approaches**

There were TWO different implementation approaches documented:

#### Approach A: "Native CLASS Potential" (CORRECT - from FINAL_RESTORATION_REPORT.md)
- Uses `scf_pot_ridder` enum in `background_potential()` switch statement
- Uses CLASS's built-in tuning: `scf_tuning_index = 1`, `Omega_scf = 0.10`
- Uses `scf_parameters = [f, Lambda, n]` where Lambda is tuned by CLASS
- Uses `attractor_ic_scf = yes` to let CLASS compute initial conditions
- **This is what the "Emergency Reconstruction Kit" specifies**

#### Approach B: "Custom Ridder Field" (WRONG - from RESTORATION_COMPLETE.md)
- Uses `has_ridder` flag and `Lambda_EDE_ridder` parameter
- Bypasses CLASS tuning mechanism
- Sets initial conditions manually
- **This approach was documented but contradicts the Emergency Kit**

**Resolution:** Approach A is correct. The Emergency Kit is the definitive specification.

---

### 2. **The Tuning Problem**

**Failure Mode:**
- Setting `Lambda_EDE_ridder = 1.0` in .ini file
- Disabling `scf_tuning_index` (commenting it out)
- Result: Lambda is too large, field oscillates too late, f_EDE too high, z_peak too low

**Root Cause:**
- The potential function uses `scf_parameters[1]` (which gets tuned)
- `Lambda_EDE_ridder` is NOT used by the potential (only for compatibility)
- If tuning is disabled, `scf_parameters[1]` stays at the initial guess (e.g., 1.0 or 50.0)
- This is physically wrong (Lambda should be ~1e-9 in Planck units)

**Fix:**
- Set `scf_parameters = 0.41, 1.0e-9, 3.0` (small starting guess for Lambda)
- Enable `scf_tuning_index = 1` (tune scf_parameters[1])
- Set `Omega_scf = 0.10` (target EDE fraction)
- Let CLASS's shooting algorithm find the correct Lambda

**Expected Result:**
- CLASS will tune Lambda to ~1e-9 (or whatever gives Omega_scf = 0.10)
- Field oscillates at correct redshift (z ~ 6500-6700)
- f_EDE peak ~15% at z ~ 6697
- r_s ~ 139 Mpc

---

### 3. **The "Redline" Discovery**

**From PHASE3_COMPLETE.md and SMOKE_TEST_RESULTS.md:**

| θᵢ | Status | CMB Excess | H₀ | r_s |
|----|--------|------------|----|----|
| 2.0 | 🟢 Safe | ~10% | ~70.5 | ~140 Mpc |
| 2.1 | 🟡 Yellow | ~12-14% | ~71.0 | ~139 Mpc |
| 2.15 | 🔴 Red | ~18% | ~71.5 | ~138 Mpc |
| 2.2+ | ❌ Explosion | >100% | N/A | N/A |

**Physical Interpretation:**
- Above θᵢ ≈ 2.1-2.2, field oscillations resonate with CMB acoustic oscillations
- Creates catastrophic blow-up in damping tail
- This is a fundamental constraint, not a bug

**Safe Mode Configuration:**
- θᵢ = 2.1 (optimal safe value)
- β = 0.01 (small coupling)
- Expected: r_s = 139.06 Mpc, f_EDE = 15.46%, z_peak = 6697

---

### 4. **Unit Conversion Confusion**

**Failure Mode:**
- Setting φ_i = f × θ_i = 1e27 × 2.1 (in eV)
- Result: Field doesn't evolve (dV/dφ too small)

**Root Cause:**
- CLASS uses Planck units (M_Pl = 1)
- f_physical = 1e27 eV → f_Planck = 1e27 / 2.435e27 ≈ 0.41
- φ_i = θ_i × f_Planck = 2.1 × 0.41 = 0.861

**Fix:**
- Convert f from eV to Planck units in `input.c`: `f_axion_ridder = param2 / M_Pl_eV`
- Set `scf_parameters[0] = 0.41` (Planck units)
- Set `scf_phi_ini = 0.84` (or let `attractor_ic_scf = yes` compute it)

---

### 5. **Perturbation Crashes**

**From PERTURBATION_FIX_SUMMARY.md:**

**Failure Mode:**
- Background works (r_s reduction achieved)
- Perturbations crash with "Step size too small" at τ ~ 65-207 Mpc

**Root Cause:**
- Field switches to fluid mode at z_osc = 5304
- Perturbations still use Klein-Gordon equations (stiff)
- Smooth transition (tanh blend) creates artificial stiffness

**Fix:**
- Hard switch to fluid equations when `a > a_osc_ridder`
- Match background logic exactly
- Use adiabatic initial conditions when starting in fluid mode

**Status:** This was fixed in previous work. Current implementation should have this.

---

### 6. **What Actually Worked (from SMOKETEST2_SUMMARY.md)**

**Successful Configuration:**
```ini
Lambda_EDE_ridder = 1.0
f_axion_ridder = 1.0e27
theta_i_ridder = 2.1
beta_ridder = 0.01
scf_tuning_index = 0  # NO TUNING!
scf_parameters = 0.0, 0.0, 0.0, 0.0
```

**Results:**
- r_s = 138.81 Mpc ✅
- z_osc = 6460 ✅
- CMB excess = 14.0% ✅
- H₀ = 70.1 km/s/Mpc ✅

**Wait, this contradicts the Emergency Kit!**

**Resolution:** This configuration worked because:
1. The potential was using `LambdaEDE4` (from `Lambda_EDE_ridder`) directly, not `scf_parameters[1]`
2. OR the implementation was different (custom Ridder field, not native CLASS potential)
3. The Emergency Kit represents the "correct" architecture that should be used going forward

---

### 7. **The Current Problem**

**What I Was Doing Wrong:**
1. Setting `scf_parameters = 0.41, 50.0, 3` (manual Lambda=50)
2. Disabling `scf_tuning_index` (commenting it out)
3. Result: Lambda too large, wrong physics

**What I Should Do:**
1. Set `scf_parameters = 0.41, 1.0e-9, 3.0` (small starting guess)
2. Enable `scf_tuning_index = 1` (let CLASS tune)
3. Set `Omega_scf = 0.10` (target)
4. Let CLASS's shooting algorithm find the correct Lambda

**Expected Outcome:**
- CLASS tunes Lambda to correct value (~1e-9 or whatever gives Omega_scf = 0.10)
- Field oscillates at z ~ 6500-6700
- f_EDE peak ~15% at z ~ 6697
- r_s ~ 139 Mpc

---

## Action Plan

### Immediate Steps:
1. ✅ Fixed `.ini` file to use correct tuning configuration
2. Test with `scf_tuning_index = 1` enabled
3. Verify CLASS's shooting algorithm finds correct Lambda
4. Check results match target: r_s ~ 139 Mpc, f_EDE ~ 15%, z_peak ~ 6697

### If Tuning Fails:
1. Check `input_shooting()` function - ensure it's not bypassed for Ridder field
2. Verify `scf_parameters[1]` is actually being updated during shooting
3. Add debug prints to see what Lambda value CLASS finds
4. Check if `Omega_scf` target is being hit

### If Results Still Wrong:
1. Verify potential function is using `scf_parameters[1]` (not `LambdaEDE4`)
2. Check initial conditions are correct (φ_i = θ_i × f)
3. Verify unit conversions are correct
4. Check if `attractor_ic_scf = yes` is working correctly

---

## Key Takeaways

1. **Use the Emergency Kit specification** - it's the definitive guide
2. **Enable CLASS tuning** - don't manually set Lambda
3. **Use small starting guess** - Lambda ~ 1e-9, not 1.0 or 50.0
4. **Trust the shooting algorithm** - it will find the correct Lambda
5. **Read the documentation** - don't hack and flail

---

**Status:** Ready to test with correct configuration

