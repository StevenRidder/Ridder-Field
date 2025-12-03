# Ridder Field Shooting Mechanism - Implementation Plan

**Date:** Nov 24, 2025  
**Goal:** Implement AxiCLASS-style shooting to calibrate `m_axion` for target `f_EDE` at `z_c`

---

## Architecture

### High-Level Flow
```
input.c reads parameters
  ↓
background_init() called
  ↓
IF use_shooting_EDE == TRUE:
  Call ridder_shoot_for_fEDE()
    ↓
    Bisect on m_axion ∈ [m_min, m_max]
      ↓
      For each m_axion:
        1. Temporarily set pba->ridder_unified.m_axion = m_test
        2. Call background_solve()
        3. Find f_ridder(z) peak in range [z_c/10, z_c*10]
        4. Compare f_peak to f_EDE_target
      ↓
      Adjust m_axion bracket
    ↓
    When |f_peak - f_target| < tolerance:
      Set pba->ridder_unified.m_axion = m_final
ELSE:
  Use m_axion from .ini file
  ↓
Proceed with normal background_solve()
```

---

## Code Changes Required

### 1. `background.h` ✅ DONE
Added to `struct ridder_unified_params`:
- `short use_shooting_EDE`
- `double f_EDE_target`
- `double z_c_target`
- `double shooting_m_min`
- `double shooting_m_max`
- `double shooting_tolerance`
- `int shooting_max_iterations`

### 2. `input.c` ✅ DONE
Added reads for all shooting parameters.

### 3. `background.c` - TO DO
Need to add:
- `ridder_shoot_for_fEDE()` function
- `get_f_ridder_peak()` helper
- Call from `background_init()` before main `background_solve()`

---

## Implementation Strategy

### Option A: Integrated Shooting (Recommended)
**Location:** Add functions directly to `background.c`

**Pros:**
- Access to all background structures
- Can call `background_solve()` internally
- Follows AxiCLASS pattern

**Cons:**
- Makes `background.c` larger

### Option B: Separate Module
**Location:** New file `ridder_shooting.c`

**Pros:**
- Cleaner separation
- Easier to test independently

**Cons:**
- Need to expose more internal functions
- More complex linking

**DECISION: Use Option A for simplicity**

---

## Detailed Implementation

### Function 1: `get_f_ridder_peak()`
```c
/**
 * Scan background table to find peak f_ridder in redshift range
 */
static int get_f_ridder_peak(
  struct background *pba,
  double z_min,
  double z_max,
  double *f_peak_out,
  double *z_peak_out
) {
  /* Sample 1000 points logarithmically between z_min and z_max */
  /* For each z, interpolate background table to get f_ridder */
  /* Track maximum */
  /* Return f_peak and z_peak */
}
```

### Function 2: `ridder_shoot_for_fEDE()`
```c
/**
 * Bisection solver for m_axion
 */
int ridder_shoot_for_fEDE(
  struct precision *ppr,
  struct background *pba,
  char errmsg[_MAX_LENGTH_]
) {
  /* 1. Extract target parameters */
  double f_target = pba->ridder_unified.f_EDE_target;
  double z_target = pba->ridder_unified.z_c_target;
  double m_low = pba->ridder_unified.shooting_m_min;
  double m_high = pba->ridder_unified.shooting_m_max;
  
  /* 2. Evaluate f_EDE at bracket endpoints */
  /*    - Set m_axion = m_low */
  /*    - Call background_solve() */
  /*    - Call get_f_ridder_peak() to get f_low */
  
  /* 3. Check that target is bracketed */
  if ((f_low - f_target) * (f_high - f_target) > 0)
    return error;
  
  /* 4. Bisection loop */
  for (iter = 0; iter < max_iter; iter++) {
    m_mid = 0.5 * (m_low + m_high);
    
    /* Set m_axion = m_mid and solve */
    pba->ridder_unified.m_axion = m_mid;
    background_solve(ppr, pba);
    get_f_ridder_peak(pba, z_target/10, z_target*10, &f_mid, &z_peak);
    
    /* Check convergence */
    if (|f_mid - f_target| < tolerance) {
      printf("Shooting converged: m_axion = %.4e\n", m_mid);
      return _SUCCESS_;
    }
    
    /* Update bracket */
    if ((f_mid - f_target) * (f_low - f_target) < 0)
      m_high = m_mid;
    else
      m_low = m_mid;
  }
  
  return error_no_convergence;
}
```

### Function 3: Integration into `background_init()`

Find the place in `background_init()` after parameters are set but before `background_solve()` is called:

```c
/* In background_init(), after parameter initialization */

if (pba->has_ridder == _TRUE_ && 
    pba->ridder_unified.model_type == ridder_model_unified &&
    pba->ridder_unified.use_shooting_EDE == _TRUE_) {
  
  printf("RIDDER: Shooting for f_EDE = %.4f at z_c = %.1f\n",
         pba->ridder_unified.f_EDE_target,
         pba->ridder_unified.z_c_target);
  
  class_call(ridder_shoot_for_fEDE(ppr, pba, errmsg),
             errmsg,
             errmsg);
}

/* Then proceed with normal background_solve() */
```

---

## Challenges & Solutions

### Challenge 1: Circular Dependency
**Problem:** `ridder_shoot_for_fEDE()` needs to call `background_solve()`, but it's called FROM `background_init()`.

**Solution:** The shooting happens BEFORE the final `background_solve()`. Each shooting iteration:
1. Sets test `m_axion`
2. Calls `background_solve()` to build table
3. Extracts `f_peak` from table
4. Clears table for next iteration

The final `background_solve()` after shooting builds the table with the calibrated `m_axion`.

### Challenge 2: Background Table Access
**Problem:** Need to read `f_ridder(z)` from background table during shooting.

**Solution:** After each `background_solve()`, use `background_at_z()` interpolation to sample `f_ridder` at multiple redshifts. This is standard CLASS functionality.

### Challenge 3: Performance
**Problem:** Bisection requires ~10-20 full background solves.

**Solution:** 
- Acceptable for calibration (runs once)
- Can cache H(z) splines to speed up
- Typical time: ~30 seconds for full shooting

---

## Testing Strategy

### Test 1: Fixed m_axion (No Shooting)
```ini
ridder_use_shooting_EDE = no
ridder_m_axion = 1e4
ridder_f_axion = 0.01
```
Should run exactly as before.

### Test 2: Shooting with Known Target
```ini
ridder_use_shooting_EDE = yes
ridder_f_EDE_target = 0.13
ridder_z_c_target = 3000
ridder_shooting_m_min = 1e2
ridder_shooting_m_max = 1e6
```
Should find `m_axion` that produces `f_EDE ≈ 0.13` at `z ≈ 3000`.

### Test 3: Reproduce AxiCLASS EDE
Use AxiCLASS EDE parameters:
- `fraction_axion_ac = 0.13`
- `log10_axion_ac = -3.5` (z_c ≈ 3162)
- `scf_parameters__1 = 2.8` (theta_i)
- `n_axion = 3`

Our shooting should find similar `m_axion` and `f_axion` values.

---

## Next Steps

1. ✅ Add shooting parameters to `background.h`
2. ✅ Add input reading in `input.c`
3. ⏳ Implement `get_f_ridder_peak()` in `background.c`
4. ⏳ Implement `ridder_shoot_for_fEDE()` in `background.c`
5. ⏳ Add shooting call in `background_init()`
6. ⏳ Test with fixed m_axion (no shooting)
7. ⏳ Test with shooting enabled
8. ⏳ Compare to AxiCLASS EDE

**Estimated time:** 2-3 hours total
**Status:** 40% complete (parameters defined, input reading done)

---

## Alternative: Lightweight Shooting

If full bisection is too complex for initial implementation:

### Simplified Version
Instead of full shooting, add a **scaling formula** based on AxiCLASS calibration:

```c
/* Empirical scaling from AxiCLASS: */
/* For fixed f_axion, theta_i, n: */
/*   f_EDE ∝ (m_axion)^p  where p ≈ 1.5-2.0 */
/*   z_peak ∝ (m_axion)^q where q ≈ -1.0 */

if (use_shooting_EDE) {
  /* Start from reference: */
  /* m_ref = 1e5 H0, f_ref ≈ 0.13, z_ref ≈ 3000 (AxiCLASS fluid example) */
  
  double z_ratio = z_c_target / 3000.0;
  double m_from_z = 1e5 * pow(z_ratio, -1.0);  /* Shift z_peak */
  
  double f_ratio = f_EDE_target / 0.13;
  double m_from_f = m_from_z * pow(f_ratio, 0.6);  /* Adjust f_EDE */
  
  pba->ridder_unified.m_axion = m_from_f;
  
  printf("SHOOTING (SCALING): m_axion = %.2e H0 for f_EDE=%.3f at z=%.0f\n",
         m_from_f, f_EDE_target, z_c_target);
}
```

**Pros:**
- Much faster (~1 background solve)
- Good enough for ~20% accuracy

**Cons:**
- Not exact
- Scaling exponents depend on (f_axion, n, theta_i)

**Recommendation:** 
- Use scaling for **rapid prototyping TODAY**
- Implement full bisection for **publication**

---

Ready to proceed with implementation?

