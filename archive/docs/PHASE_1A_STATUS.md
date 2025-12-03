# Phase 1A: Beta Ladder - STATUS

**Date:** November 24, 2025  
**Prerequisite:** ✅ Validation Complete (5/5 tests passing)  
**Status:** READY TO RUN

---

## 🎯 Objective

Systematically scan CDM coupling parameter `β` to find the stability frontier and measure observables:

- **H₀ shift:** How much does coupling boost Hubble?
- **S₈ reduction:** How much does "dark drag" suppress structure?
- **CMB deviations:** What's the cost in polarization spectra?
- **Perturbation stability:** Where does the integrator fail?

---

## 📋 Beta Ladder Configuration

### Parameter Grid
```
β ∈ {0.05, 0.10, 0.15, 0.20}
σ_z = 0.5 (fixed)
```

### Fixed Cosmology
```
Ω_b = 0.02238280
Ω_cdm = 0.1201075
h = 0.6732117
A_s = 2.098900e-09
n_s = 0.965952
τ_reio = 0.05430842
```

### Ridder Field (Unified Shelf Only)
```
ridder_model_type = unified
ridder_f = 1.0e16 eV (EDE scale, NOT M_Pl!)
ridder_theta_i = 2.0

# Shelf (EDE)
ridder_use_shelf = yes
ridder_Lambda_EDE_eV = 1.0
ridder_theta_EDE_low = 0.1
ridder_theta_EDE_high = 5.0
ridder_n_EDE = 3.0

# Tail/Plateau OFF
ridder_use_tail = no
ridder_use_plateau = no
```

**CRITICAL FIX APPLIED:** `ridder_f = 1.0e16 eV` instead of `M_Pl = 2.4e27 eV`  
This allows `θ = φ/f ~ O(1)` so the field can actually roll.

---

## 🔧 Script Ready

**Location:** `phase3_full_analysis/scripts/beta_ladder_v6_postfix.sh`

**What it does:**
1. Generates 4 `.ini` files (one per β value)
2. Runs CLASS with each config
3. Saves outputs to `phase3_full_analysis/beta_scan_unified_v6/`

**Analysis script:** `phase3_full_analysis/scripts/analyze_beta_v6.py`
- Parses background files
- Extracts r_s, H₀_eff, f_EDE, z_peak
- Computes ΔH₀, ΔS₈, w(z)
- Generates comparison table

---

## 📊 Expected Outcomes

### If β = 0.05 (Weak Coupling)
- ΔH₀ ~ +0.5 to +1 km/s/Mpc (small boost)
- ΔS₈ ~ -0.01 (modest suppression)
- CMB ~ 5-10% (should pass)
- **Perturbations:** Stable ✅

### If β = 0.10 (Moderate)
- ΔH₀ ~ +1.5 to +2.5 km/s/Mpc
- ΔS₈ ~ -0.03 to -0.05
- CMB ~ 15-25%
- **Perturbations:** Likely stable ✅

### If β = 0.15 (Strong)
- ΔH₀ ~ +3.0 to +3.5 km/s/Mpc
- ΔS₈ ~ -0.06 to -0.08
- CMB ~ 30-40%
- **Perturbations:** May be unstable ⚠️

### If β = 0.20 (Very Strong)
- ΔH₀ ~ +3.5 to +4.0 km/s/Mpc
- ΔS₈ ~ -0.08 to -0.10 (OVERSHOOTS tension!)
- CMB ~ 40-50%
- **Perturbations:** Likely unstable ❌

---

## ⚠️ Known Risks

### 1. Perturbation Stiffness
**Symptom:** `evolver error: integration step too small`  
**Cause:** Large `β` makes CDM-Ridder coupling oscillate rapidly  
**Workaround:**
- Loosen `tol_perturb_integration` to `1e-4` or `1e-3`
- Reduce `k_max_tau0_over_l_max` to `3.0`

### 2. Energy Scale Still Wrong
**Symptom:** Field frozen, `φ' ~ 10⁻³¹`, `f_ridder ~ 10⁻¹¹⁴`  
**Fix Applied:** `ridder_f = 1.0e16 eV` (EDE scale)  
**Verification:** Check debug output for `theta ~ O(1)` at early times

### 3. Shelf Window Mismatch
**Symptom:** `f_EDE` peaks at wrong redshift or has wrong amplitude  
**Diagnosis:** Check `theta_EDE_low/high` vs actual field trajectory  
**Fix:** Adjust window bounds based on `theta(z)` from background output

---

## 🚀 Execution Plan

### Step 1: Run Beta Ladder on VM
```bash
ssh <VM_USER>@172.174.34.125
cd ~/Ridder-Field/phase3_full_analysis/scripts
bash beta_ladder_v6_postfix.sh
```

**Expected runtime:** 1-2 hours (4 configs × 15-30 min each)

### Step 2: Monitor for Crashes
Watch for:
- ✅ "Computing background" → "Computing thermodynamics" → "Computing perturbations"
- ❌ "step size too small" → Note which β failed
- ✅ "Writing output..." → Success!

### Step 3: Analyze Results
```bash
cd ~/Ridder-Field/phase3_full_analysis/scripts
python3 analyze_beta_v6.py
```

This will generate:
- `beta_scan_unified_v6_results.json` - Raw metrics
- `beta_scan_unified_v6_summary.txt` - Human-readable table

### Step 4: Extract Key Metrics
From the summary, identify:
- **Highest stable β** (max β that completes perturbations)
- **H₀ boost** at that β
- **S₈ reduction** at that β
- **CMB cost** at that β

---

## 🎯 Success Criteria

### Minimum Viable Result
- ✅ At least 2/4 β values complete successfully
- ✅ Measure ΔH₀ > +1 km/s/Mpc for at least one point
- ✅ Measure ΔS₈ < -0.02 for at least one point
- ✅ Document where perturbations become unstable

### Ideal Result
- ✅ All 4 β values complete
- ✅ Clear trend: ΔH₀ and ΔS₈ increase with β
- ✅ Identify β where CMB cost becomes unacceptable
- ✅ Find "sweet spot": max(ΔH₀ + |ΔS₈|) subject to CMB < 30%

---

## 📈 Next Steps After Phase 1A

### If β Ladder Succeeds → Phase 1B: Tail Activation
- Turn on late-time tail
- Tune `Lambda_tail` to get `w₀ ≈ -1`
- Verify w(z) is dynamic at intermediate redshifts

### If Perturbations Unstable → Fallback Plan
- Reduce `Lambda_EDE` from 1.0 to 0.5 eV
- Re-run beta ladder with weaker shelf
- Accept smaller ΔH₀ but gain stability

### If Results Weak → Phase 1D: Optimization
- Run 2D grid: `(Lambda_EDE, β)`
- Find parameter combination that maximizes combined tension relief
- May discover non-obvious sweet spots

---

## 📝 Pre-Flight Checklist

- ✅ Validation complete (5/5 tests)
- ✅ Shooting mechanism deployed
- ✅ Beta ladder script ready
- ✅ Analysis script ready
- ✅ VM has latest code (commit `7487483`)
- ✅ Energy scale bug fixed (`ridder_f` corrected)
- ✅ Makefile clean, no stale objects
- ✅ Output directory exists

**STATUS: CLEARED FOR LAUNCH** 🚀

---

## 🎓 What We'll Learn

This isn't just parameter fitting. The beta ladder will tell us:

1. **Is the CDM coupling mechanism viable?**
   - If perturbations crash at low β → fundamental instability
   - If they're stable → mechanism is numerically sound

2. **What's the H₀ vs S₈ trade-off?**
   - Can we boost H₀ without killing S₈ too much?
   - Or does strong coupling suppress both equally?

3. **Where does the CMB push back?**
   - At what β do polarization distortions become fatal?
   - Is there a broad "plateau" or sharp cliff?

4. **Do we need the tail?**
   - If shelf alone gives good late-time, tail may be optional for observations
   - If w(z) wrong without tail, we NEED it

By the end of Phase 1A, we'll have **real numbers** to put in the story, not just "this could work in principle."

---

**Ready to run when you are.**

