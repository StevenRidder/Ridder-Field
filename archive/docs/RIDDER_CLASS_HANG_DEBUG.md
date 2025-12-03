# Ridder CLASS High-ℓ Hang: Root Cause Analysis

**Date**: 2025-12-02  
**Status**: Deep diagnostic based on C code audit  
**Issue**: EDE chains hang silently at high l_max_scalars (≥1000)

---

## Executive Summary

After auditing the CLASS C code, the hang appears to originate from **stiff ODEs in the perturbation evolution** when the Ridder field is active. The `evolver_ndf15` stiff solver gets stuck in Newton iterations when:

1. High-k modes (corresponding to high ℓ) are evolved
2. The Ridder field perturbations become numerically stiff
3. The sound speed calculation produces extreme values

This is NOT a simple step-size failure (which would produce an error message). It's a convergence failure within the Newton iteration loop that doesn't trigger the `tooslow` flag quickly enough.

---

## Part 1: Where the Hang Occurs

### The Call Chain

```
cobaya-run (Python)
  → classy.compute() (Python wrapper)
    → perturb_init() (C)
      → perturbations_solve() (C) - loops over k modes
        → evolver_ndf15() (C) - stiff ODE solver
          → perturbations_derivs() (C) - derivative callback
            → Ridder field perturbation equations
```

### The Evolver Loop (evolver_ndf15.c, lines 301-530)

The stiff solver has a main while loop:

```c
while (done==_FALSE_){
    // ... step size adjustment ...
    
    for( ; ; ){  // Inner loop for Newton iterations
        // ... Newton iteration with maxit=4 ...
        
        if (tooslow==_TRUE_){
            // Recompute Jacobian or reduce step size
        }
    }
}
```

**The hang happens when**:
- Newton iterations converge *just barely* (not triggering `tooslow`)
- But step sizes keep shrinking toward hmin
- The process takes an exponentially increasing time

---

## Part 2: The Ridder Perturbation Equations

From `perturbations.c` lines 9574-9706, the Ridder field is evolved as a fluid:

```c
if (pba->has_ridder == _TRUE_) {
    double w_eff = pba->w_eff_ridder;  // (n-1)/(n+1) = 0.5 for n=3
    
    // Sound speed calculation - THIS IS THE PROBLEMATIC PART
    double cs2 = w_eff;
    if (m2_eff > 0.0) {
        double a2m2 = a2 * m2_eff;
        cs2 = (2.0 * a2m2 * w_eff + k2) / (2.0 * a2m2 + k2);  // ← DANGER
    }
    
    // Energy conservation
    dy[index_pt_phi_ridder] = 
        -3.0 * a_prime_over_a * (delta_rho + delta_p)
        - Theta_flux
        - (rho_ridder + p_ridder) * metric_continuity;
        
    // Momentum conservation  
    dy[index_pt_phi_prime_ridder] =
        -4.0 * a_prime_over_a * Theta_flux
        + k2 * delta_p
        + (rho_ridder + p_ridder) * metric_euler;
}
```

### Problem 1: Sound Speed at High k

The sound speed formula:

```c
cs2 = (2.0 * a2m2 * w_eff + k2) / (2.0 * a2m2 + k2);
```

At high k (high ℓ), this approaches:
- `cs2 → 1` as `k² >> a² m²`

But the transition creates **numerical stiffness** because:
- At low k: `cs2 ≈ w_eff = 0.5`
- At high k: `cs2 ≈ 1.0`
- The transition region has rapid changes in cs2 with k

### Problem 2: Effective Mass Calculation

The effective mass `m2_eff` is computed from:

```c
double rho_eV = rho_ridder * 3.0 * pow(M_Pl_eV/eV_to_Mpc_inv, 2.0);
double V_eff = rho_eV / 2.0; 
double term_V = V_eff / pow(Lambda, 4.0);
double m2_eV = n * (2*n - 1) * pow(Lambda, 4.0) * pow(term_V, (double)(n-1)/n) / (f*f);
m2_eff = m2_eV * pow(eV_to_Mpc_inv, 2.0);
```

**Danger**: When `term_V` is small or when Lambda is near 1.0, the `pow(term_V, (n-1)/n)` term can produce:
- Very small values (stiff low-k behavior)
- Rapid variations with a (stiff time evolution)

---

## Part 3: Why High ℓ Triggers the Hang

High ℓ maps to high k modes via:
```
k ≈ ℓ / (conformal distance to recombination)
```

For ℓ = 7000, k ≈ 0.5 h/Mpc (high k).

At high k:
1. **More k-modes to evolve**: The k-loop has more iterations
2. **Faster oscillations**: cs² ≈ 1 means sound waves propagate at speed of light
3. **Stiff coupling**: The k² term in the momentum equation dominates
4. **Small timesteps required**: The Courant condition requires dt ∝ 1/k

The combination creates a situation where:
- Each k-mode takes longer to evolve
- The number of k-modes scales with ℓ_max
- Newton iterations converge slowly but not slowly enough to abort
- Total time grows as O(ℓ_max³) or worse

---

## Part 4: Why ΛCDM Works But EDE Doesn't

**ΛCDM code path** (background.c line 582):
```c
if (pba->ridder_fluid_mode == _FALSE_) {
    // Standard scalar field evolution
}
```

ΛCDM runs with `has_ridder = FALSE`, so:
- Ridder field perturbation equations are never called
- No stiff cs² calculation
- No effective mass computation
- Perturbations evolve smoothly

**EDE code path**:
- `has_ridder = TRUE`
- Ridder perturbations are active
- cs² and m² calculations run at every timestep
- Newton iterations struggle with stiff equations

---

## Part 5: Potential Fixes

### Fix A: Early Cutoff for Ridder Perturbations at High k

In `perturbations.c` line 9592, there's a disabled cutoff:

```c
/* TEMPORARILY DISABLE CUTOFF FOR DEBUGGING */
if (0) { // DISABLED DEBUG rho_ridder < 1.e-4 * rho_crit) {
    dy[pv->index_pt_phi_ridder] = 0.0;
    dy[pv->index_pt_phi_prime_ridder] = 0.0;
}
```

**Enable and modify this** to also check for high-k:

```c
double k_cutoff = 0.1;  // h/Mpc - tune empirically
if (rho_ridder < 1.e-4 * rho_crit || k > k_cutoff) {
    dy[pv->index_pt_phi_ridder] = 0.0;
    dy[pv->index_pt_phi_prime_ridder] = 0.0;
}
```

**Why this works**: At high k, Ridder field perturbations are physically negligible anyway (the field doesn't have causal contact on those scales). Setting them to zero eliminates the stiff equations.

### Fix B: Regularize the Sound Speed

Replace the raw cs² formula with a regularized version:

```c
// Current (stiff at transition):
cs2 = (2.0 * a2m2 * w_eff + k2) / (2.0 * a2m2 + k2);

// Regularized (smooth transition):
double k2_reg = k2 + 1e-10;  // Prevent division issues
double transition = 1.0 / (1.0 + exp(-(k2 - 4.0 * a2m2) / (a2m2 + 1e-10)));
cs2 = w_eff * (1.0 - transition) + 1.0 * transition;
```

### Fix C: Increase Newton Iteration Limit for Stiff Regions

In `evolver_ndf15.c` line 91:

```c
int maxit=4, maxk=5;  // Current: 4 Newton iterations max
```

For stiff problems, this may not be enough:

```c
int maxit=8, maxk=5;  // Double the Newton iterations
```

**Caution**: This slows down ALL integrations, not just EDE.

### Fix D: Use k-Dependent Tolerance

Currently (perturbations.c line 3234):
```c
ppr->tol_perturbations_integration,  // Global tolerance
```

Could be modified to:
```c
double tol_k = ppr->tol_perturbations_integration * (1.0 + k/k_pivot);
```

Where `k_pivot` is a reference scale. This relaxes tolerance at high k where precision is less critical.

---

## Part 6: Recommended Debugging Steps

### Step 1: Add Timing Diagnostics

In `perturbations.c`, add before the evolver call:

```c
static int k_debug_count = 0;
if (k_debug_count < 10 || k > 0.1) {
    printf("DEBUG: Starting k=%.4e, ell~%.0f\n", k, k * 14000.0);  // rough ℓ estimate
    clock_t start = clock();
}
```

And after:
```c
if (k_debug_count < 10 || k > 0.1) {
    clock_t end = clock();
    printf("DEBUG: Finished k=%.4e in %.2f sec\n", k, (double)(end-start)/CLOCKS_PER_SEC);
    k_debug_count++;
}
```

This will show which k-mode is hanging.

### Step 2: Test the Cutoff Fix

Enable the k-cutoff in perturbations.c:

```c
double k_cutoff_Mpc = 0.5;  // Start conservative
if (k > k_cutoff_Mpc) {
    // Zero out Ridder perturbations
    dy[pv->index_pt_phi_ridder] = 0.0;
    dy[pv->index_pt_phi_prime_ridder] = 0.0;
    return _SUCCESS_;  // Skip rest of Ridder block
}
```

### Step 3: Profile with gprof

Compile CLASS with `-pg` flag and run a failing case:
```bash
make clean
CCFLAG="-pg" make class
./class test_ede.ini
gprof class gmon.out > profile.txt
```

This will show exactly where time is being spent.

---

## Part 7: The Real Root Cause

Based on the code analysis, the root cause is:

**The Ridder field perturbation equations become numerically stiff at high k due to the scale-dependent sound speed formula. The NDF15 solver handles stiffness, but the Newton iterations converge slowly enough to not trigger the abort condition, leading to exponentially increasing integration time.**

This is a **fundamental numerical issue** with the fluid approximation for a scalar field at high k, not a bug per se. The fix is either:

1. Cut off Ridder perturbations at high k (physically justified)
2. Switch to a different approximation at high k (e.g., tight coupling)
3. Accept higher tolerance at high k (trade precision for speed)

---

## Summary Table

| Issue | Location | Severity | Fix Difficulty |
|-------|----------|----------|----------------|
| Stiff cs² at high k | perturbations.c:9648 | High | Medium |
| m² calculation near small rho | perturbations.c:9630-9639 | Medium | Low |
| Newton iteration limit | evolver_ndf15.c:91 | Medium | Low |
| Disabled cutoff | perturbations.c:9592 | High | Low |

---

## Immediate Workaround

Until the C code is fixed, the config-level workaround is:

1. **Use l_max_scalars ≤ 5000** instead of 8500
2. **Provide starting point** to avoid random initial point search
3. **Tighten Lambda prior** to [0.8, 1.2] to stay in stable regime

These reduce the probability of hitting the stiff region, but don't eliminate it.

---

**Last Updated**: 2025-12-02  
**Based On**: Audit of phase2/class/source/perturbations.c, background.c, evolver_ndf15.c

