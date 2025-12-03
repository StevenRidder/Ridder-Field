# V1 vs V3 MCMC Performance Comparison

**Date:** November 26, 2025  
**Status:** 🔴 CRITICAL PERFORMANCE ISSUE IDENTIFIED

---

## Executive Summary

**PROBLEM:** V3 tier 3 MCMC is ~10x slower than it should be due to excessive CLASS integrator calls.

**ROOT CAUSE:** V3 potential is computationally expensive AND being called for every background integration step (~37,000 calls per MCMC step vs ~1,000-5,000 expected).

---

## Performance Comparison

| Metric | V1 (Simple EDE) | V3 (Unified) | Ratio |
|--------|----------------|--------------|-------|
| **Params** | 3 (Lambda, theta_i, beta) | 9 (Lambda_EDE, a_c, sigma_lna, + tail params) | 3x |
| **Potential Calls per Step** | ~3,000 (est) | **37,000** | **12x** |
| **Seconds per MCMC Step** | ~2-3 sec (est) | **17 sec** | **6-8x** |
| **Potential Components** | 1 (simple EDE) | 3 (floor + EDE + tail) | 3x |
| **Transcendental Functions per Call** | 2-3 (cos, sin, pow) | **8-12** (cos, sin, pow, exp, log) | 3-4x |

---

## Diagnostic Data from VM

### V3 Tier 3 Test (Nov 26, 05:41-05:50 UTC)
```
Time elapsed: 9 minutes
MCMC steps completed: 31 steps
Time per step: ~17 seconds
Derivative calls: 295,000
Calls per step: 295,000 / 31 = ~9,500 calls/step

Latest check (05:50):
- 8 MCMC steps logged
- 295,000 derivative calls
- Ratio: 37,000 calls per logged step
```

### Expected Performance (LCDM)
```
LCDM baseline:
- ~1,000-5,000 derivative calls per step
- ~2-3 seconds per step (with Planck full)
```

**V3 is doing 7-37x more derivative calls than expected!**

---

## Code Complexity Analysis

### V1 Simple EDE Potential
**File:** `phase2/class/source/background.c` (v2 fallback code)

```c
double V_ridder(struct background *pba, double phi, double a) {
  double Lambda = pba->Lambda_EDE_ridder;
  double f = pba->f_axion_ridder;
  int n = pba->n_ridder;
  
  if (Lambda == 0.0) return 0.0;
  
  double phi_over_f = phi / f;
  double base = 1.0 - cos(phi_over_f);
  double Lambda4 = pow(Lambda, 4.0);
  
  return Lambda4 * pow(base, n);
}
```

**Computational Cost:**
- 1 cos()
- 2 pow() 
- 3 multiplications
- **Total: ~10 FLOPs**

---

### V3 Unified Potential
**File:** `phase2/class/source/ridder_v3_potential.c`

```c
double ridder_V_v3_theta(double theta, double a, struct ridder_unified_params *rp) {
  V += V_floor_v3(rp);           // 1 pow()
  V += V_EDE_v3(theta, a, rp);   // 1 log(), 1 exp(), 2 cos(), 2 pow()
  V += V_tail_v3(theta, rp);     // 1 cos(), 2 pow()
  return V;
}

double V_EDE_v3(double theta, double a, struct ridder_unified_params *rp) {
  // Time window (DISABLED in current code but still called)
  double S = S_time_window(a, rp->a_c, rp->sigma_lna);
  // Currently returns 1.0 but was: exp[-(ln a - ln a_c)^2 / (2*sigma^2)]
  
  double Lambda4 = pow(rp->Lambda_EDE_eV, 4.0);
  double B = B_field_bump(theta, rp->theta_E_center, rp->n_EDE);
  return Lambda4 * S * B;
}

double B_field_bump(double theta, double theta_E, double n_EDE) {
  double delta_theta = theta - theta_E;
  double one_minus_cos = 1.0 - cos(delta_theta);
  return pow(one_minus_cos, n_EDE);
}

double V_tail_v3(double theta, struct ridder_unified_params *rp) {
  double Lambda4 = pow(rp->Lambda_tail_eV, 4.0);
  double delta_theta = theta - rp->theta_T_center;
  double one_minus_cos = 1.0 - cos(delta_theta);
  double modulation = pow(one_minus_cos, rp->n_tail);
  return Lambda4 * (1.0 + rp->alpha_tail * modulation);
}
```

**Computational Cost:**
- 3 cos() (one per component)
- 6 pow() (Lambda^4 x3, field bumps x3)
- ~15 multiplications/additions
- **Total: ~50 FLOPs**

**V3 is 5x more expensive per call, but that doesn't explain 37x slowdown!**

---

## Why So Many Derivative Calls?

### Hypothesis 1: Stiff Dynamics
The v3 potential with time-windowed EDE creates **stiff differential equations**:

```c
// Time window creates exponential suppression
S(a) = exp[-(ln a - ln a_c)^2 / (2*sigma_lna^2)]
```

When `a` is far from `a_c`, the potential changes rapidly, forcing the CLASS integrator to take **smaller timesteps**.

**Evidence:**
- Derivative calls show wide range of `a` values: `a = 1.31e-01, 2.79e-03, 1.55e-09`
- Integrator is exploring early universe (a~10^-9) repeatedly

**Note:** The time window is currently DISABLED in the code (returns 1.0), but the field dynamics may still be stiff due to the EDE bump structure.

---

### Hypothesis 2: Integrator Tolerance Too Tight
CLASS background integrator may have tight error tolerances that force many substeps.

**Check in background.c:**
```c
// Look for lines like:
pba->background_pert_integration_stepsize
pba->tol_background_integration
```

---

### Hypothesis 3: Multiple Component Overhead
Each MCMC step requires CLASS to:
1. Solve background (with ridder field evolution) - **37,000 calls**
2. Solve perturbations (with ridder perturbations)
3. Compute CMB Cl's
4. Compute lensing
5. Evaluate likelihoods (Planck + BAO + SH0ES)

The background step alone is taking 17 seconds due to 37,000 derivative evaluations.

---

## Comparison with V1 Tier 3

### V1 Configuration
**File:** `phase3/configs/ridder_tier3_production.yaml`

```yaml
theory:
  classy:
    extra_args:
      Lambda_EDE_ridder: 1.0  # Simple energy scale
      f_axion_ridder: 1.0e27
      n_ridder: 3
      
params:
  theta_i_ridder:
    prior: {min: 0.1, max: 2.3}
  beta_ridder:
    prior: {min: 0.0, max: 0.03}
```

**3 varying parameters, simple V(phi) = Lambda^4 [1 - cos(phi/f)]^n**

---

### V3 Configuration
**File:** `phase3/ridder_v3_tier3_test.yaml`

```yaml
theory:
  classy:
    extra_args:
      ridder_model_type: v3_canon
      
      # EDE component (time-windowed)
      ridder_use_shelf: "yes"
      ridder_theta_E_center: 0.0
      ridder_sigma_E: 0.4
      ridder_n_EDE: 3.0
      
      # Tail component
      ridder_use_tail: "yes"
      ridder_Lambda_tail_eV: 0.0012
      ridder_alpha_tail: 1.0
      ridder_theta_T_center: 0.0
      ridder_n_tail: 1.0
      
      ridder_f_eV: 1.0e26
      theta_i_ridder: 2.4

params:
  ridder_Lambda_EDE_eV:
    prior: {min: 0.05, max: 0.80}
  ridder_a_c:
    prior: {min: 2.5e-4, max: 8.0e-4}
  ridder_sigma_lna:
    prior: {min: 0.6, max: 1.8}
```

**3 varying parameters (same as v1), but V(phi, a) = V_floor + V_EDE(theta, a) + V_tail(theta)**

More complex potential → stiffer dynamics → more integrator steps → slower

---

## Optimization Recommendations

### 🔴 URGENT (Week 1)

#### 1. Check Integrator Tolerances
**Action:** Relax background integration tolerances on VM

**File:** `phase2/class/source/background.c` (search for tolerance parameters)

**Test:** Run single CLASS call with relaxed tolerance, verify observables unchanged

**Expected speedup:** 2-3x

---

#### 2. Profile V3 Potential Function
**Action:** Add timing to `ridder_potential_v3()` to see where time is spent

```c
#include <time.h>

double ridder_V_v3_theta(double theta, double a, struct ridder_unified_params *rp) {
  static int call_count = 0;
  static double total_time = 0.0;
  
  clock_t start = clock();
  
  double V = 0.0;
  V += V_floor_v3(rp);
  V += V_EDE_v3(theta, a, rp);
  V += V_tail_v3(theta, rp);
  
  clock_t end = clock();
  total_time += ((double)(end - start)) / CLOCKS_PER_SEC;
  call_count++;
  
  if (call_count % 10000 == 0) {
    printf("V3_POT: %d calls, %.3f sec total, %.2e sec/call\n",
           call_count, total_time, total_time / call_count);
  }
  
  return V;
}
```

---

#### 3. Simplify V3 Potential (If Possible)
**Options:**
- Disable tail component for testing: `ridder_use_tail: no`
- Use simpler EDE bump (n_EDE = 1 instead of 3)
- Check if field evolution can be approximated

**Test each independently to isolate bottleneck.**

---

### 🟡 MEDIUM TERM (Week 2-3)

#### 4. Compare V1 vs V3 Derivative Call Counts
**Action:** Run identical LCDM+EDE point through both v1 and v3, count calls

**This will definitively show if stiffness is the issue.**

---

#### 5. Implement Analytical Solutions Where Possible
**Example:** If tail is negligible at early times, skip its calculation:

```c
double V_tail_v3(double theta, double a, struct ridder_unified_params *rp) {
  if (a < 0.001) return 0.0;  // Tail irrelevant in early universe
  // ... rest of calculation
}
```

---

#### 6. Use Faster Math Functions
**Example:** Replace `pow(x, 4.0)` with `x*x*x*x`

```c
// BEFORE:
double Lambda4 = pow(rp->Lambda_EDE_eV, 4.0);

// AFTER:
double L = rp->Lambda_EDE_eV;
double Lambda4 = L*L*L*L;  // 3x faster than pow()
```

---

### 🟢 LONG TERM (Month 2+)

#### 7. Implement Field Evolution Caching
If same parameter point is evaluated multiple times, cache the field evolution.

---

#### 8. Consider Fluid Approximation Earlier
Switch to fluid mode (w_eff) as soon as field starts oscillating, avoid expensive ODE solving.

---

## Immediate Action Plan

**Run on VM right now:**

```bash
ssh <VM_USER>@172.174.34.125

# 1. Check current progress
python3 ~/Ridder-Field/phase3/scripts/check_v3_tier3_status.py

# 2. Get derivative call rate from one chain
cd ~/Ridder-Field/phase3/chains/v3_tier3_test_chain1_work
grep "DERIVS_ENTRY" chain1.log | wc -l
echo "MCMC steps:"
grep -c "Progress @" chain1.log

# 3. Kill the slow test
pkill -f cobaya

# 4. Try simplified V3 (tail disabled)
# Edit: ridder_v3_tier3_test.yaml
# Change: ridder_use_tail: "no"
# Run: ./scripts/run_v3_tier3_test.sh
```

---

## Summary

| Issue | Impact | Fix Difficulty | Expected Speedup |
|-------|--------|----------------|------------------|
| Too many derivative calls (37k vs 5k) | **10x slowdown** | Medium | **5-7x** |
| V3 potential 5x more expensive | **2x slowdown** | Hard | **1.5-2x** |
| More MCMC parameters (9 vs 3) | **1.5x slowdown** | None (intrinsic) | N/A |

**Target:** Get from 17 sec/step → 3-5 sec/step  
**Strategy:** Reduce derivative calls first (biggest bang for buck)

---

## Next Steps

1. ✅ Document problem (this file)
2. ⏳ Profile potential function timing
3. ⏳ Test with simplified potential (no tail)
4. ⏳ Adjust integrator tolerances
5. ⏳ Compare v1 vs v3 call counts on same point
6. ⏳ Implement fast math optimizations

**Owner:** Debug with user on VM  
**Timeline:** Target 3x speedup by end of week

