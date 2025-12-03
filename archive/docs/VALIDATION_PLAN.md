# Ridder Field Shooting Mechanism - Validation Plan

**Date:** November 24, 2025  
**Status:** ✅ Internal check implemented, external suite ready

---

## Summary

Following best practices for production-ready numerical algorithms, we've implemented a **two-tier validation strategy**:

1. **Lightweight internal check** - Runs automatically after every shooting convergence
2. **External validation suite** - Run once before production use, then periodically

This approach balances robustness (catches bugs early) with performance (no heavy overhead on every call).

---

## What Was Implemented

### 1. Internal Sanity Check (in `background_shoot_Lambda`)

**Location:** `phase2/class/source/background.c`, lines 3758-3771

**What it does:**
- After bisection converges, remeasures f_peak one more time
- Compares to target: if `|f_peak - f_target| > 5 × tolerance`, prints warning
- **Does NOT crash** - soft failure allows investigation without breaking MCMC

**Cost:** One extra `background_ridder_measure_peak()` call (~0.01% overhead)

**Code:**
```c
/* Lightweight sanity check: verify final result is still within reasonable tolerance */
double f_final_check, z_final_check;
class_call(background_ridder_measure_peak(pba, z_min, z_max, 
                                           &f_final_check, &z_final_check),
           pba->error_message,
           pba->error_message);

double final_diff = fabs(f_final_check - pba->ridder_fEDE_target);
if (final_diff > 5.0 * tol_f) {
  /* Soft failure: warn but do not crash */
  fprintf(stdout,
          "RIDDER_SHOOT warning: final f_peak=%.5f differs from target=%.5f by %.5f "
          "(>5*tol=%.5f) at z=%.1f. Check bracket or tolerance.\n",
          f_final_check, pba->ridder_fEDE_target, final_diff, 
          5.0 * tol_f, z_final_check);
}
```

**Tested:** ✅ Runs without warning on 10% EDE target (f_peak = 0.09821, within 5×0.001 = 0.005)

---

### 2. External Validation Suite (`validate_shooting.py`)

**Location:** `validate_shooting.py` (repo root)

**What it does:**
Runs 3 comprehensive tests on the VM:

#### Test 1: Manual Replicate
- Run with shooting ON → capture converged Lambda
- Run with shooting OFF, using that Lambda
- Verify f_peak and z_peak match within tolerance

**Purpose:** Confirms shooter result is reproducible when used manually

**Tolerance:** Δf < 0.5%, Δz < 100

---

#### Test 2: Multi-Target
- Run shooting for f_EDE = 0.05, 0.10, 0.20
- Verify each converges within tolerance
- Verify Lambda is monotonic (higher target → higher Lambda)

**Purpose:** Confirms shooter works across parameter range and scaling is sensible

**Expected scaling:** 
| f_EDE | Lambda (eV) | log10(Lambda) |
|-------|-------------|---------------|
| 5%    | ~10¹²–10¹³  | ~12–13        |
| 10%   | ~5×10¹³     | ~13.7         |
| 20%   | ~10¹⁴–10¹⁵  | ~14–15        |

---

#### Test 3: Bracket Robustness
- Run shooting with different [log10_Lambda_min, log10_Lambda_max]:
  - Wide: [10, 16]
  - Medium: [12, 15]
  - Narrow: [13, 14.5]
- Verify converged Lambda is consistent (within 1%)

**Purpose:** Confirms result is independent of bracket choice (as long as solution is inside)

---

## How to Use

### Step 1: Internal Check (Automatic)
**Already running!** Every shooting call includes the sanity check.

If you see a warning like:
```
RIDDER_SHOOT warning: final f_peak=0.15000 differs from target=0.10000 by 0.05000
(>5*tol=0.00500) at z=500.1. Check bracket or tolerance.
```

**This means:**
- Shooter "converged" but result is far from target
- Likely causes:
  - True solution is outside bracket → widen bracket
  - Tolerance too loose → tighten `ridder_shoot_tol_f`
  - Peak redshift at boundary (z_min or z_max) → adjust search window

---

### Step 2: External Suite (Run Once Now)

**When to run:**
- ✅ **Right now** - before relying on shooter in production
- ⏰ **After major changes** - if you modify potential, units, or EOM
- ⏰ **Before MCMC runs** - final sanity check before long jobs

**How to run:**
```bash
# On your local machine:
cd /Users/steveridder/Git/Ridder-Field
python3 validate_shooting.py
```

**What to expect:**
- Takes ~5-10 minutes (runs multiple CLASS instances on VM)
- Prints detailed progress for each test
- Final summary: ✓ ALL TESTS PASSED or ✗ SOME TESTS FAILED

**If tests fail:**
- Review printed diagnostics (Lambda, f_peak, z_peak for each run)
- Check for consistent failures (e.g., always too low → bracket issue)
- Debug and re-run before moving to production

---

## Current Status

### ✅ What's Working
- **Internal check:** Implemented, compiled, tested on 10% EDE → no warnings
- **External suite:** Written, ready to run
- **Shooter convergence:** Reliable bisection, ~10 iterations typical
- **Code quality:** Clean, well-commented, minimal overhead

### ⏳ What's Pending
- **Run external suite:** Need to execute `validate_shooting.py` (do this next!)
- **Multi-target verification:** Confirm scaling for 5%, 20% EDE
- **Bracket robustness:** Verify narrow brackets work if solution is inside

---

## Decision Point: Move to Physics Tuning

**Once external suite passes,** you have two paths:

### Path A: Stop here, use shooter as-is
- **What you have:** Automatic Lambda tuning for any f_EDE target
- **What you do manually:** Pick θ_i to get desired z_peak
- **Workflow:** Trial-and-error on θ_i, or accept whatever z_peak you get

**Good for:** Quick exploration, parameter scans, proof-of-concept

---

### Path B: Add z_peak targeting (later)
- **Upgrade:** Two-parameter shooting on (Lambda, θ_i) for (f_EDE, z_peak) targets
- **Example:** "I want 10% EDE peaking at z=3000"
- **Requires:** More machinery (2D bisection or nested loops)

**Good for:** Precision cosmology, CMB fitting, H0 tension studies

**Recommendation:** Start with Path A. Only go to Path B if you find yourself repeatedly tuning θ_i by hand.

---

## Next Steps (Priority Order)

### Immediate (This Session)
1. ✅ Internal check implemented and pushed
2. ⏳ **Run `validate_shooting.py`** ← **DO THIS NEXT**
3. ⏳ Review results, debug any failures
4. ✅ If all tests pass → **shooter is production-ready**

### Short-Term (This Week)
5. ⏳ **Theta scan:** For fixed f_EDE = 0.10, scan θ_i ∈ [1.0, 2.5], plot z_peak(θ_i)
6. ⏳ **Decay constant scan:** Scan f ∈ [10⁹, M_Pl], map effect on z_peak and m_eff
7. ⏳ **Slow-roll tuning:** Adjust c_slow ∈ [0.5, 1.5] to see effect on onset timing
8. ⏳ **Plot f_EDE(z):** Visual diagnostic of peak shape, width, decay

### Medium-Term (Next 2 Weeks)
9. ⏳ **CMB spectra:** Compute TT, TE, EE for fiducial EDE model
10. ⏳ **Compare to Planck:** Overlay with Planck data, assess χ²
11. ⏳ **H0 sensitivity:** Measure ΔH0 for f_EDE ∈ [5%, 15%]
12. ⏳ **MCMC integration:** Test shooter in MontePython/CosmoMC

### Long-Term (Month+)
13. ⏳ **Precision tuning:** If z_peak is consistently off, add soft penalty or 2D shooting
14. ⏳ **DM coupling:** Activate β_ridder ≠ 0 for perturbation coupling
15. ⏳ **Monodromy refinement:** Switch from [1-cos(θ)]³ to sin(θ/n) staircase
16. ⏳ **Publication prep:** Parameter constraints, tension relief, model comparison

---

## Validation Checklist

Use this to track progress:

- [x] Internal sanity check coded
- [x] Internal check compiled and tested
- [x] External suite written (`validate_shooting.py`)
- [ ] **Test 1 (Manual replicate) run and passed** ← NEXT
- [ ] **Test 2 (Multi-target) run and passed**
- [ ] **Test 3 (Bracket robustness) run and passed**
- [ ] All warnings/failures debugged
- [ ] Shooter declared production-ready
- [ ] **Move to physics tuning phase**

---

## Files in This Commit

```
✅ phase2/class/source/background.c   (+16 lines)  - Internal sanity check
✅ validate_shooting.py                (new file)   - External test suite
✅ VALIDATION_PLAN.md                  (this file)  - Roadmap and instructions
```

---

## Philosophy

> **"Spot check now, lightweight check always, then move on to physics."**

The goal is **not** to build an infinitely robust numerical fortress. The goal is to:
1. Catch obvious bugs early (✅ internal check)
2. Verify behavior once on representative cases (⏳ external suite)
3. Trust the plumbing and **focus on the science** (⏳ physics tuning)

Over-engineering validation wastes time. Under-engineering causes silent failures. This approach hits the sweet spot.

---

**Status:** Ready for external validation, then physics tuning! 🚀

