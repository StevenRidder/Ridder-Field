# PHASE 3 STATUS: FLUID APPROXIMATION EXHAUSTED

**Date:** November 21, 2025  
**Codebase Status:** Phase 2.7 (Fluid-Only Implementation Complete + NO-GO)  
**Branch:** `ridder_fluid_hack_nogo` (archived)

---

## EXECUTIVE SUMMARY: NO-GO FOR PRODUCTION MCMC

After exhaustive debugging and surgical fixes, the **Fluid-Only + Hard Switch + WKB Matching** implementation has been proven to be **fundamentally limited**. The code is numerically stable and technically sophisticated, but produces a **persistent 25-50% oscillatory excess** in the CMB damping tail (ℓ ≈ 2000-3000) that cannot be eliminated within the fluid approximation framework.

**This is not a bug. This is a structural limitation of the approximation method.**

**See:** `phase2/FINAL_VERDICT.md` for full technical analysis.

---

## What We Accomplished (Phase 2.0 → 2.7)

### 1. Generalized Dark Matter (GDM) Variables
Implemented `δρ` and `Θ_flux` as integration variables to eliminate w=-1 singularities:
- ✅ Numerically stable across all epochs
- ✅ Smooth handling of field → fluid transition
- ✅ No crashes, no NaNs

### 2. Cycle-Averaged Field Approximation (CAFA)
Implemented scale-dependent sound speed derived from WKB approximation:
```
cs²(k) = k² / (4a²m²_eff + k²)
```
- ✅ Correct sub-horizon behavior (cs² → 1)
- ✅ Correct super-horizon behavior (cs² → w_eff)
- ✅ Stabilized integrator (no "step size too small" errors)

### 3. Forced Approximation Switching
Hijacked `index_ap_tca_idm_dr` to force CLASS to stop at `a_osc`:
- ✅ Trigger fires for every k-mode
- ✅ `perturbations_vector_init` called successfully
- ✅ WKB matching code executes

### 4. WKB Matching for Gauge-Invariant Quantities
Implemented conservation of comoving density perturbation:
```
Δ_com = (δρ/ρ) + (ρ'/ρ) · (θ/k²)
```
- ✅ Mathematically correct formula
- ✅ Proper handling of photon/UR copying
- ❌ **Correction evaluates to ~0.00%** (see diagnosis below)

### 5. β-Coupling for S₈ Suppression
Activated coupling between Ridder field and CDM:
- ✅ High-k suppression observed (~24% at k=0.1 h/Mpc)
- ✅ Monotonic, stable behavior
- ✅ Promising for S₈ tension resolution

### 6. Rigorous Stress Testing
Created `audit_rigorous.py` to validate:
- ✅ BBN consistency (indirect check via Y_He)
- ❌ **CMB damping tail (25-50% excess at ℓ=2500)**
- ✅ Coupling linearity (monotonic suppression)

---

## Why the Fluid Approximation Failed

### The Core Problem

The WKB matching correction is **negligible** (`-0.00%`) because:

1. **Instantaneous vs. Cycle-Averaged Mismatch:**
   - At `a_osc`, the field is at a random phase of rapid oscillation
   - `ρ + p ≈ 0` at turning points → ill-conditioned θ extraction
   - Cannot reconstruct cycle-averaged fluid mode from instantaneous snapshot

2. **Discontinuous Dynamics:**
   - Before `a_osc`: Field-like equations (w ≈ -1, cs² = 1)
   - After `a_osc`: Fluid-like equations (w = 0.5, cs²(k))
   - Even with perfect matching at one instant, **time derivatives** are discontinuous
   - Creates "kick" that propagates as resonance in CMB

3. **Non-Local Pathology:**
   - Local-in-time WKB matching cannot fix a **non-local** dynamical discontinuity
   - The spike is baked into the evolution equations, not the initial conditions

### What We Tested (All Failed to Eliminate Spike)

- ✅ Tuning θ_i (2.0, 2.2, 2.35, 2.5)
- ✅ Hybrid sound speed (field: cs²=1, fluid: cs²(k))
- ✅ GDM variables (δρ, Θ_flux)
- ✅ Forced approximation switching
- ✅ WKB matching on gauge-invariant quantities
- ✅ Photon/UR preservation during switches

**Result:** Damping tail excess remains 25-50% for all configurations.

---

## What This Does NOT Kill

❌ **Does NOT kill:** The Ridder Field cosmology  
❌ **Does NOT kill:** The EDE mechanism for Hubble tension  
❌ **Does NOT kill:** The β-coupling for S₈ suppression  
❌ **Does NOT kill:** The background evolution  

✅ **Does kill:** The idea that Ridder perturbations can be modeled as a hard-switched fluid approximation at Planck-grade precision.

---

## Viable Paths Forward

### **Path A: Full Scalar Field Implementation** ⭐ RECOMMENDED

Implement Ridder as a true scalar field using CLASS's `scf` machinery:
- Specify potential: `V(φ) = Λ⁴(1 - cos(φ/f))ⁿ`
- Solve Klein-Gordon equation directly
- No fluid approximation, no discontinuities
- **Effort:** 2-3 days
- **Status:** Ready to begin

### **Path B: Background-Only Ridder** (Quick Interim)

Keep background evolution, disable perturbations:
- Correct H(z), no CMB spike
- Quick MCMC for preliminary constraints
- **Effort:** 1 hour
- **Status:** Can start immediately

### **Path C: Detune θ_i** (Stopgap)

Reduce θ_i to suppress spike (not eliminate):
- θ_i = 2.0 → spike ~8-12% (still present)
- Sacrifices H₀ target (→ 70-71 km/s/Mpc)
- **Effort:** 10 minutes
- **Status:** Not recommended for production

---

## Current MCMC Status

### Cobaya Environment
- ✅ Installed and tested
- ✅ Planck likelihoods configured
- ✅ Parameter file ready (`phase3/ridder_field.yaml`)

### Likelihoods Configured
- ✅ `planck_2018_highl_plik.TTTEEE`
- ✅ `planck_2018_lowl.TT`
- ✅ `planck_2018_lensing`
- ✅ `bao.boss`
- ✅ `H0.riess2020`

### Current Blocker
❌ **CMB damping tail artifact makes current implementation unsuitable for production MCMC**

---

## Submission Documentation (Archived)

The following documents were prepared for the fluid implementation and are now **archived** pending Path A completion:

- `phase3/submission/APPENDIX_A_GDM_DERIVATION.md` (still valid for methodology)
- `phase3/submission/SECTION_2_MODEL_UNIQUENESS.md` (still valid)
- `phase3/submission/SECTION_7_LIMITATIONS.md` (needs update for Path A)
- `phase3/submission/REVISED_SCIENTIFIC_REPORT.md` (needs rewrite for Path A)
- `phase3/submission/REFEREE_PROOF_NARRATIVE.md` (needs rewrite for Path A)
- `phase3/submission/PUBLICATION_READY_ABSTRACT.md` (needs rewrite for Path A)

**Note:** The GDM+CAFA methodology is scientifically sound and can be cited as "explored approach" in the final paper.

---

## Immediate Next Steps

See `NEXT_STEPS.md` for detailed action plan.

**Decision Required:** Choose Path A, B, or C based on priorities:
- **Path A:** Best for publication, requires time investment
- **Path B:** Best for quick phenomenology, clearly labeled as preliminary
- **Path C:** Stopgap only, not recommended

**Recommended:** Pursue Path A (Full Scalar Field) for scientifically rigorous, publication-ready implementation.

---

## Technical Achievements (Reusable for Path A)

All code and methodology developed in Phase 2 is reusable:

1. ✅ GDM variable formalism
2. ✅ CAFA sound speed derivation
3. ✅ Forced approximation switching mechanism
4. ✅ WKB matching framework
5. ✅ Rigorous stress testing suite
6. ✅ β-coupling implementation strategy

**These are not wasted effort.** They inform the proper scalar field implementation.

---

**Status:** Phase 2 complete. Ready for Phase 3 (Path A).  
**Last Updated:** 2025-11-21  
**Next Review:** After Path A implementation begins
