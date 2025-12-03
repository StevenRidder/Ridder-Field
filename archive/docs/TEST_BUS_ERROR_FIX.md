# Testing & Fixing Bus Errors in H0 Fixed Chains

## Hypothesis
The bus errors are triggered by specific H0 values or parameter combinations in the Ridder field code, not general system overload.

## Test Plan

### Test 1: Run Chains Sequentially (Not Parallel)
**Purpose:** Determine if it's a concurrency issue specific to H0 fixed chains

```bash
# Run one H0 chain at a time, wait for completion
for h0 in 68.5 69.5 70.5 71.5 72.5 73 73.5; do
    echo "Testing H0=$h0 sequentially..."
    cobaya-run configs/tier5_ede_shoes_desi_h0_fixed_${h0}.yaml
    # Wait for completion or crash
    sleep 5
done
```

**Expected:** If sequential runs work, it's a concurrency issue. If they still crash, it's a parameter-specific bug.

---

### Test 2: Run with Memory Sanitizer
**Purpose:** Catch memory corruption before it causes bus errors

```bash
# Recompile CLASS with AddressSanitizer
cd phase2/class
make clean
export CFLAGS="-fsanitize=address -g -O0"
export LDFLAGS="-fsanitize=address"
make

# Run one chain with sanitizer
cd ../../phase3
ASAN_OPTIONS=detect_leaks=0 cobaya-run configs/tier5_ede_shoes_desi_h0_fixed_70.5.yaml
```

**Expected:** AddressSanitizer will show exactly where memory corruption occurs.

---

### Test 3: Reduce Number of H0 Chains
**Purpose:** Test if running fewer H0 chains prevents crashes

```bash
# Run only 3 H0 chains at a time
# Group 1: 68.5, 69.5, 70.5
# Group 2: 71.5, 72.5, 73
# Group 3: 73.5
```

**Expected:** If 3 chains work but 7 crash, it's a resource contention issue.

---

### Test 4: Check for H0-Specific Numerical Issues
**Purpose:** Identify if certain H0 values trigger numerical problems

**Potential Issues:**
1. **Division by zero in H0-dependent calculations**
   - Check: `pow(pba->H0,2)` - H0=0 would cause issues, but we're using 68-73
   - Check: Any calculations that become unstable at specific H0 values

2. **Array index corruption**
   - When H0 is fixed, other parameters adjust
   - Maybe some parameter combination causes index calculation to go wrong

3. **Ridder field switching logic**
   - The switching from Klein-Gordon to fluid might be triggered differently at different H0
   - Check: `a_osc_ridder` calculation might be problematic

---

### Test 5: Add Safety Checks to Code
**Purpose:** Prevent crashes by catching issues early

**Add to `background.c` around line 616:**
```c
// Safety check before decay_factor calculation
if (pba->a_osc_ridder <= 0.0 || pba->a_osc_ridder > 1.0) {
    class_stop(pba->error_message, 
        "Invalid a_osc_ridder = %e at a=%e (H0=%f)", 
        pba->a_osc_ridder, a, pba->H0);
}

// Check for NaN/Inf before assignment
double decay_factor = pow(a / pba->a_osc_ridder, -3.0 * (1.0 + pba->w_eff_ridder));
if (!isfinite(decay_factor)) {
    class_stop(pba->error_message,
        "Non-finite decay_factor = %e at a=%e (a_osc=%e, w_eff=%e, H0=%f)",
        decay_factor, a, pba->a_osc_ridder, pba->w_eff_ridder, pba->H0);
}
```

**Add to `perturbations.c` around line 9374:**
```c
// Strengthen phi_prime check
if (fabs(phi_prime) < 1.e-20 || !isfinite(phi_prime)) {
    // Skip coupling if phi_prime is too small or invalid
    cdm_velocity_coupling = 0.0;
} else {
    double raw_coupling = 3.0 * beta_eff * a2 * Theta_ridder * M_Pl_eV / phi_prime;
    // Check result is finite
    if (!isfinite(raw_coupling)) {
        raw_coupling = 0.0;  // Safety fallback
    }
    // ... rest of code
}
```

---

### Test 6: Compare Working vs Crashing Configs
**Purpose:** Identify what's different about H0 fixed configs

```bash
# Compare a working config (tier5_ede_shoes_desi) with H0 fixed version
diff configs/tier5_ede_shoes_desi.yaml configs/tier5_ede_shoes_desi_h0_fixed_70.yaml
```

**Check:**
- Are there any other differences besides H0 being fixed?
- Are parameter ranges different?
- Are there missing safety checks?

---

## Immediate Actions (No Code Changes)

### Option 1: Run Chains in Smaller Batches
```bash
# Run 3 at a time, wait for completion
# This reduces memory pressure and avoids potential race conditions
```

### Option 2: Increase Safety Thresholds
- Increase `phi_prime` threshold from `1.e-30` to `1.e-20`
- Add explicit NaN/Inf checks before critical calculations

### Option 3: Disable Debug Output
- Remove or comment out all `static` debug counters
- This eliminates any potential thread-safety issues (even if unlikely)

---

## Recommended Testing Order

1. **First:** Run Test 1 (sequential) - fastest way to see if it's concurrency
2. **If sequential works:** Run Test 3 (smaller batches) - find the safe batch size
3. **If sequential fails:** Run Test 2 (AddressSanitizer) - find exact bug location
4. **Then:** Apply Test 5 (safety checks) - prevent crashes

---

## Quick Fix: Run Fewer Chains

Since you can run 15 other chains fine, try running only 4-5 H0 fixed chains at a time:

```bash
# Group 1: 68.5, 69.5, 70.5, 71.5
# Wait for completion, then:
# Group 2: 72.5, 73, 73.5
```

This might be enough to avoid whatever triggers the bus errors while still getting results.
