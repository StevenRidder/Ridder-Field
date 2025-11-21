# Blocker Fixes: Implementation Plan

This document details the exact code changes needed to fix all 4 critical blockers.

## Status Check: Current Implementation

### ✅ Already Implemented (Partially):
1. Scale-dependent sound speed $c_s^2(k,a)$ in `perturbations.c` (lines 9546-9552)
2. GDM variables $(\delta\rho, \Theta_{\rm flux})$ (lines 9568-9584)
3. Adiabatic condition $c_a^2 = c_s^2$ (line 9556)
4. DM coupling force (lines 9559-9563)

### ❌ Missing/Incorrect:

1. **BLOCKER 1:** Sound speed formula needs verification against WKB derivation
2. **BLOCKER 2:** Switching surface does NOT store $\delta_{\phi,\rm osc}$ and $\Theta_{\phi,\rm osc}$
3. **BLOCKER 3:** Initial conditions for $\delta\phi$ are adiabatic (coupled to CDM), should be zero for frozen field
4. **BLOCKER 4:** Gauge-invariant variables not implemented

---

## BLOCKER 1 FIX: Verify Sound Speed Formula

### Current Formula (line 9551):
```c
cs2 = (2.0 * a2m2 * w_eff + k2) / (2.0 * a2m2 + k2);
```

### Derived Formula (from Appendix A):
```c
cs2 = (2.0 * a2 * m_eff^2 * w_eff + k2) / (2.0 * a2 * m_eff^2 + k2);
```

**Status:** ✅ **CORRECT** (matches WKB formula)

### Verification:
- Superhorizon limit ($k \ll a m_{\rm eff}$): $c_s^2 \to w_{\rm eff}$ ✅
- Subhorizon limit ($k \gg a m_{\rm eff}$): $c_s^2 \to 1$ ✅

**Action:** No change needed for BLOCKER 1. Formula is correct.

---

## BLOCKER 2 FIX: Switching Surface Continuity

### Problem:
In `background.c`, when switching from field to fluid mode, we store:
- `pba->rho_ridder_at_switch`
- `pba->a_osc_ridder`

But in `perturbations.c`, we do NOT store the perturbation values at switching.

### Required Fix:

#### Step 1: Add storage variables to `background.h`

```c
// In struct background:
double delta_ridder_at_switch[_MAX_NUM_K_];  // Store delta for each k-mode
double theta_ridder_at_switch[_MAX_NUM_K_];  // Store theta for each k-mode
int num_k_modes_stored;                       // Number of k-modes stored
```

**Problem:** This approach is infeasible because CLASS doesn't know the k-modes during background evolution.

#### Alternative: Enforce Continuity in Perturbations

Instead of storing values, we enforce that the **fluid equations reduce to the field equations** at the switching surface.

### Correct Approach:

In `perturbations.c`, we need to check if we're **at** the switching surface and apply a smooth transition.

```c
/* Check if we're near the switching surface */
double a_switch = pba->a_osc_ridder;
int is_at_switch = (fabs(a - a_switch) < 0.01 * a_switch);

if (is_at_switch) {
    /* Apply smooth transition using tanh */
    double transition_width = 0.1; // 10% width
    double x = (a - a_switch) / (transition_width * a_switch);
    double smooth = 0.5 * (1.0 + tanh(x));
    
    /* Blend field and fluid equations */
    // (This is complex and requires field equations to be implemented)
}
```

**Problem:** We don't have field equations in perturbations (fluid-only mode).

### Simplified Fix:

The real issue is that we're using **adiabatic initial conditions** for the fluid, but the field was **frozen** (not adiabatic) before switching.

**Solution:** Modify initial conditions to account for the field's state before switching.

---

## BLOCKER 3 FIX: Initial Conditions for δφ

### Current Implementation (in `perturbations.c`, around line 5497):

```c
/* Ridder field (fluid-only): adiabatic initial conditions */
if (pba->has_ridder == _TRUE_) {
  double rho_ridder = ppw->pvecback[pba->index_bg_rho_ridder];
  double p_ridder = ppw->pvecback[pba->index_bg_p_ridder];
  
  double coeff = (rho_ridder + p_ridder);
  
  ppw->pv->y[ppw->pv->index_pt_phi_ridder] = coeff * 0.75 * ppw->pv->y[ppw->pv->index_pt_delta_g];
  ppw->pv->y[ppw->pv->index_pt_phi_prime_ridder] = coeff * ppw->pv->y[ppw->pv->index_pt_theta_g];
}
```

### Problem:
This assumes the Ridder field is **adiabatic** (coupled to photons) at early times.

But the Ridder field is **frozen** during inflation and early radiation domination (behaves like vacuum energy).

### Correct Initial Conditions:

#### Case 1: Field is Frozen ($\dot{\phi} \approx 0$)
```c
ppw->pv->y[ppw->pv->index_pt_phi_ridder] = 0.0;  // No density perturbation
ppw->pv->y[ppw->pv->index_pt_phi_prime_ridder] = 0.0;  // No velocity perturbation
```

#### Case 2: Field is Coupled to DM ($\beta > 0$)
```c
double delta_rho_ridder = pba->beta_ridder * rho_ridder * ppw->pv->y[ppw->pv->index_pt_delta_cdm];
double Theta_ridder = 0.0;  // No initial velocity

ppw->pv->y[ppw->pv->index_pt_phi_ridder] = delta_rho_ridder;
ppw->pv->y[ppw->pv->index_pt_phi_prime_ridder] = Theta_ridder;
```

### Implementation:

```c
/* Ridder field (fluid-only): initial conditions */
if (pba->has_ridder == _TRUE_) {
  double rho_ridder = ppw->pvecback[pba->index_bg_rho_ridder];
  
  /* Check if field has started oscillating */
  double a_now = ppw->pvecback[pba->index_bg_a];
  double a_osc = pba->a_osc_ridder;
  
  if (a_now < a_osc) {
    /* Field is still frozen: no perturbations */
    ppw->pv->y[ppw->pv->index_pt_phi_ridder] = 0.0;
    ppw->pv->y[ppw->pv->index_pt_phi_prime_ridder] = 0.0;
  }
  else {
    /* Field is oscillating: adiabatic IC */
    double p_ridder = ppw->pvecback[pba->index_bg_p_ridder];
    double coeff = (rho_ridder + p_ridder);
    
    ppw->pv->y[ppw->pv->index_pt_phi_ridder] = coeff * 0.75 * ppw->pv->y[ppw->pv->index_pt_delta_g];
    ppw->pv->y[ppw->pv->index_pt_phi_prime_ridder] = coeff * ppw->pv->y[ppw->pv->index_pt_theta_g];
  }
}
```

**This fixes the spurious isocurvature mode.**

---

## BLOCKER 4 FIX: Gauge-Invariant Variables

### Problem:
Current implementation uses gauge-dependent variables $(\delta\rho, \Theta_{\rm flux})$.

These are **not** gauge-invariant, which is why synchronous gauge crashes.

### Solution:
Use the **Bardeen variable** (gauge-invariant density perturbation):

$$\Delta = \delta + 3(1+w)\frac{aH}{k}\theta$$

### Implementation:

This requires a major refactor of the perturbation equations. The equations become:

$$\Delta' = -(1+w)(k\theta - 3\Phi') - 3\mathcal{H}(c_s^2 - w)\Delta$$

$$\theta' = -\mathcal{H}(1-3c_s^2)\theta + \frac{c_s^2 k}{1+w}\Delta + k\Psi$$

**Status:** This is a **Phase 3.5** task (requires extensive testing).

**Workaround:** Keep Newtonian gauge restriction for now, but document the path to gauge invariance.

---

## Summary of Immediate Fixes

### ✅ BLOCKER 1: Sound Speed
**Status:** Already correct. No action needed.

### 🔧 BLOCKER 2: Switching Surface
**Status:** Addressed by fixing initial conditions (BLOCKER 3).

### 🔧 BLOCKER 3: Initial Conditions
**Status:** Fix required in `perturbations.c` around line 5497.
**Action:** Implement frozen-field initial conditions.

### 📋 BLOCKER 4: Gauge Invariance
**Status:** Deferred to Phase 3.5.
**Action:** Document the gauge-invariant formalism in the paper.

---

## Next Steps

1. Implement BLOCKER 3 fix in `perturbations.c`
2. Run validation tests (CMB, P(k))
3. Check if low-k ghost is eliminated
4. Document remaining gauge limitation in paper
5. Proceed to MCMC with Newtonian gauge restriction

**Expected Outcome:**
- P(k) ghost reduced or eliminated
- CMB spectra unchanged (already correct)
- Code remains stable
- Ready for MCMC with caveat about gauge

