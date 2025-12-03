# Unified Validation - Current Status

**Date:** November 24, 2025  
**Status:** Debugging - Ridder field active, perturbations failing

---

## What Just Happened

### Progress Made ✅
1. ✅ Created validation script (`test_unified_cdm_metrics.py`)
2. ✅ Fixed script to handle CLASS output format
   - Skip duplicate `root` and `write background` lines
   - Handle `00` suffix in filenames
   - Extract r_s from correct column (column 8)
3. ✅ Fixed unified INIs to trigger Ridder field
   - Added `Lambda_EDE_ridder`, `f_axion_ridder`, `theta_i_ridder`
   - Ridder field now activates properly

### Current Issue ❌
**CLASS fails in perturbation integration:**
```
Error in perturbations_init
=>evolver_ndf15: Step size too small
```

**Why:**
- Background evolution works (we see Ridder debug output)
- Perturbations encounter numerical stiffness
- Integration step size drops below minimum

**Diagnostics from output:**
```
RIDDER FINAL STATE (a=1, z=0):
  rho_ridder = 5.354549e-15 Mpc^-2
  rho_tot    = 5.048505e-08 Mpc^-2
  f_ridder   = 1.060621e-07 (fraction of total)
  Omega_ridder = 0.000000 (if f ~ Omega_Lambda)
```

**Problem:** `f_ridder = 1.06e-7` is TINY (should be ~0.13-0.15 for EDE)

This means the Ridder field isn't contributing significantly to energy density.

---

## Root Cause Analysis

### Issue 1: Unified mode not using unified parameters
Even though we set `ridder_model_type = unified`, the code might still be using simple_ede path.

**Evidence:**
- We had to add `Lambda_EDE_ridder` to trigger `has_ridder`
- The unified parameters (`ridder_Lambda_EDE_eV`, etc.) might not be read
- Field might be evolving with v2 parameters, not unified shelf

### Issue 2: Unified parameters not properly initialized
The unified parameter reading code is inside `if (pba->has_ridder == _TRUE_)`, but `has_ridder` is only set AFTER reading `Lambda_EDE_ridder > 0`.

**Chicken-and-egg problem:**
1. CLASS checks `Lambda_EDE_ridder > 0` to set `has_ridder`
2. Unified params only read if `has_ridder == TRUE`
3. But unified mode doesn't use `Lambda_EDE_ridder`!

**Fix needed:**
- Read `ridder_model_type` BEFORE checking `Lambda_EDE_ridder`
- Set `has_ridder = TRUE` if model_type is unified, even if `Lambda_EDE_ridder == 0`

---

## What Needs To Be Fixed

### Priority 1: Fix `has_ridder` Logic
**File:** `phase2/class/source/input.c`

**Current logic:**
```c
if (pba->Lambda_EDE_ridder > 0.0) {
    pba->has_ridder = _TRUE_;
}
```

**Needed logic:**
```c
// Read model type first
class_read_string("ridder_model_type", string1);
if (string1 contains "unified") {
    pba->ridder_unified.model_type = ridder_model_unified;
    pba->has_ridder = _TRUE_;  // <-- SET FOR UNIFIED
}

if (pba->Lambda_EDE_ridder > 0.0) {
    pba->has_ridder = _TRUE_;  // <-- OR SET FOR SIMPLE_EDE
}
```

### Priority 2: Verify Unified Potential is Actually Called
**File:** `phase2/class/source/background.c`

**Check:** Are the `V_ridder`, `dV_ridder`, `ddV_ridder` functions actually branching to unified mode?

**Add debug:**
```c
if (pba->ridder_unified.model_type == ridder_model_unified) {
    printf("UNIFIED_MODE: Using unified potential\n");
    // ... unified code ...
} else {
    printf("SIMPLE_EDE_MODE: Using v2 potential\n");
    // ... v2 code ...
}
```

### Priority 3: Check Unified Parameters Are Read
**File:** `phase2/class/source/input.c`

**Add debug after reading unified params:**
```c
if (pba->ridder_unified.model_type == ridder_model_unified) {
    printf("UNIFIED PARAMS: Lambda_EDE=%e, theta_low=%e, theta_high=%e\n",
           pba->ridder_unified.Lambda_EDE,
           pba->ridder_unified.theta_EDE_low,
           pba->ridder_unified.theta_EDE_high);
}
```

---

## Quick Diagnostic Test

**To verify if unified mode is actually running:**

1. Add debug print in `V_ridder()`:
```c
double V_ridder(struct background *pba, double phi) {
    if (pba->ridder_unified.model_type == ridder_model_unified) {
        printf("V_RIDDER: UNIFIED MODE ACTIVE\n");
    } else {
        printf("V_RIDDER: SIMPLE_EDE MODE\n");
    }
    // ... rest of function ...
}
```

2. Run CLASS with hero INI
3. Check output for which mode is active

**Expected:** Should see "UNIFIED MODE ACTIVE"  
**If not:** Unified parameters aren't being set properly

---

## Alternative: Force Unified Mode in INI

**Workaround until input.c is fixed:**

Add to INIs:
```ini
# Force unified mode recognition
use_ridder = yes
Lambda_EDE_ridder = 1.5  # Triggers has_ridder flag
ridder_model_type = unified

# These unified params should override v2 params
ridder_use_shelf = yes
ridder_Lambda_EDE_eV = 1.5
ridder_theta_EDE_low = 0.5
ridder_theta_EDE_high = 2.0
```

But this still requires fixing input.c to actually READ these unified parameters.

---

## Current Status Summary

**What works:**
- ✅ Unified potential code compiles
- ✅ Smoke test passes (CLASS runs without crashes for simple cases)
- ✅ Validation script framework is solid
- ✅ Ridder field activates (we see debug output)

**What's broken:**
- ❌ Unified parameters not being read/used correctly
- ❌ Field has tiny energy density (f_ridder ~ 1e-7 instead of ~0.14)
- ❌ Perturbations fail due to numerical stiffness

**What's needed:**
1. Fix input.c to read unified params correctly
2. Verify unified potential functions are called
3. Debug why field has negligible energy
4. Fix perturbation numerical stiffness (might self-resolve after 1-3)

---

## Recommended Next Steps

### Option A: Fix input.c (recommended)
1. Move `ridder_model_type` reading BEFORE `has_ridder` check
2. Set `has_ridder = TRUE` for unified mode
3. Recompile and test

**Time:** 30-60 minutes  
**Payoff:** Proper fix that enables unified mode correctly

### Option B: Add Debug and Diagnose
1. Add debug prints to V_ridder, input reading
2. Run hero INI and capture full output
3. Trace exactly what's happening

**Time:** 15-30 minutes  
**Payoff:** Know exactly what's wrong before fixing

### Option C: Simplify Test Case
1. Create minimal unified INI (tail-only or shelf-only)
2. Test without CDM coupling
3. Get ONE unified regime working first

**Time:** 15-30 minutes  
**Payoff:** Verify unified architecture works at all

---

## Bottom Line

**We're 80% there:**
- Code compiles ✅
- Architecture is clean ✅
- Ridder field activates ✅
- Validation framework ready ✅

**Last 20%:**
- Fix parameter reading logic in input.c
- Verify unified mode actually runs
- Debug why field energy is too small

**This is fixable.** The architecture is sound, just need to debug the parameter plumbing.

---

**NEXT ACTION:** Either fix input.c directly, or add debug output to trace the issue.

