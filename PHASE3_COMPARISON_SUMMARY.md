# Phase 3: ΛCDM vs. EDE Comparison Summary

## Configurations Compared

| Config | Lambda [eV] | theta_i | Dynamics | Purpose |
|--------|-------------|---------|----------|---------|
| **Vanilla ΛCDM** | 0.0 (no Ridder) | N/A | N/A | Standard cosmology baseline |
| **EDE Benchmark** | 0.4964 | 0.75 | Full (damp=1.0) | H₀-relevant EDE model |

---

## Observable Comparison

### Primary Observables

| Observable | Vanilla ΛCDM | EDE (θ=0.75) | Δ(EDE-ΛCDM) | % Change |
|-----------|--------------|--------------|-------------|----------|
| **H0 [km/s/Mpc]** | 67.3600 | 67.3600 | **+0.0000** | **0.00%** |
| **l(1st peak)** | 221 | 221 | 0 | 0.00% |
| **TT(peak) [×10⁻¹⁰]** | 7.728 | 7.984 | +0.257 | +3.32% |
| **TT(high-l) [×10⁻¹¹]** | 5.034 | 5.208 | +0.174 | +3.44% |

### Ridder Field Energy Budget

| Observable | Vanilla ΛCDM | EDE (θ=0.75) |
|-----------|--------------|--------------|
| f_ridder(z=0) | 0.000 (no field) | 0.000 (fully decayed) |
| rho_ridder(z=0) [Mpc⁻²] | 0.0 | 2.80×10⁻¹⁵ (negligible) |

---

## Key Findings

### 1. ❌ **No H₀ Shift Observed**

The EDE benchmark produces **ΔH₀ = 0.00 km/s/Mpc** compared to ΛCDM.

**Expected behavior:** EDE should *increase* H₀ by ~3-7 km/s/Mpc to help resolve the Hubble tension.

**Actual behavior:** H₀ is identical to the input value (67.36 km/s/Mpc) and unchanged from vanilla ΛCDM.

**Possible explanations:**
1. **EDE fraction too small:** f_peak ~ 0.063 (~6.3%) may be below the threshold needed for observable H₀ shift
2. **Peak redshift too late:** z_peak ~ 691 is later than canonical EDE (z ~ 3000-5000)
3. **Field decay too fast:** Field has completely disappeared by z=0, may not be affecting late-time expansion
4. **Parameter space issue:** Current (Lambda, theta_i) combination not in the H₀-shifting regime

### 2. ✅ **Small CMB Spectrum Shifts**

The CMB power spectrum shows modest differences:
- TT amplitude increased by ~3.3% at first acoustic peak
- High-l tail increased by ~3.4%
- Peak location unchanged (both at l=221)

**Interpretation:** The EDE field *is* affecting the CMB, but only at the few-percent level. This is consistent with a small f_peak and suggests the field is having *some* dynamical effect during recombination.

### 3. ✅ **Field Decay Confirmed**

The Ridder field has completely decayed by z=0:
- f_ridder(z=0) = 0.000
- rho_ridder(z=0) ~ 10⁻¹⁵ Mpc⁻² (negligible)

This is **correct EDE behavior** - the field should be gone today. ✓

---

## Diagnosis: Why No H₀ Shift?

To shift H₀ in EDE models, the field must:
1. **Exist during radiation-matter equality** (z ~ 3000-5000) ✗ (our peak is at z~691)
2. **Contribute ~10% of energy density** at peak ✗ (we have ~6.3%)
3. **Dilute faster than radiation** pre-recombination ??? (need to check w_eff)

**Current status:**
- z_peak = 691 is in the **matter-dominated era**, not near equality
- f_peak = 0.063 is on the low side (canonical EDE uses ~10%)
- Peak is ~5× too late compared to typical EDE models

### What This Means

The current EDE configuration is behaving more like **"late-peaking dark energy"** than **"early dark energy at equality."** The field peaks after equality, has modest amplitude, and doesn't significantly alter the expansion rate at the epochs that matter for H₀.

---

## Path Forward

### Option 1: Increase Lambda Further (Target Earlier Peak)

From Phase 2, we found:
- Lambda ~ 0.017 eV → z_peak ~ 15
- Lambda ~ 0.50 eV → z_peak ~ 691
- Lambda ~ 1.5 eV → z_peak ~ ?

**Action:** Run Lambda scan up to ~5-10 eV to push z_peak into the z~3000-5000 range.

### Option 2: Increase f_peak (Target Larger Amplitude)

From Phase 2, theta_i controls f_peak at fixed Lambda.

**Action:** 
- At Lambda = 0.50 eV, scan theta_i = {1.0, 1.25, 1.5} to find configuration with f_peak ~ 0.10
- Check if higher f_peak at z~691 produces H₀ shift

### Option 3: Combined Scan (2D Parameter Space)

**Action:** 
- Scan Lambda × theta_i grid
- Target: z_peak ~ 3000, f_peak ~ 0.10
- Find configuration that actually shifts H₀

### Option 4: Check w_eff Evolution

**Action:**
- Plot w_ridder(a) from background file
- Verify field is behaving as expected (oscillating, then freezing)
- Check if w_eff < -1/3 during relevant epochs

---

## Recommended Next Step

**Run Option 4 first** (check w_eff evolution) to understand *how* the field is behaving, then decide between Options 1-3 based on that diagnosis.

If w_ridder is behaving correctly but just peaking too late, go with **Option 1** (increase Lambda to push z_peak earlier).

If w_ridder shows unexpected behavior (e.g., not oscillating, wrong equation of state), we may have a physics bug to fix first.

---

## Files Generated

### Benchmark Configurations
- `benchmark_vanilla_lcdm.ini` - Working vanilla ΛCDM control
- `benchmark_ede_theta075.ini` - Working EDE benchmark
- `benchmark_lcdm_control.ini` - Broken frozen field config (not used)

### Output Data
Located in `output/`:
- `benchmark_vanilla_lcdm_00_*.dat` - Vanilla ΛCDM (background, C_l, pk, etc.)
- `benchmark_ede_theta075_00_*.dat` - EDE benchmark (background, C_l, pk, etc.)

### Analysis Scripts
- `extract_observables.py` - Observable extraction (handles both Ridder and vanilla files)

### Documentation
- `PHASE3_INITIAL_RESULTS.md` - Initial findings and ΛCDM control issue
- `PHASE3_COMPARISON_SUMMARY.md` - This document

---

## Status

✅ Phase 3.1 Complete: Baseline comparison established
- Vanilla ΛCDM control working
- EDE benchmark running successfully  
- Key finding: ΔH₀ = 0.00 (no shift)

⏳ Phase 3.2 Next: Diagnose why no H₀ shift
- Check w_ridder(a) evolution
- Determine if issue is z_peak, f_peak, or dynamics
- Plan parameter adjustments

🎯 **Goal:** Find (Lambda, theta_i) that produces ΔH₀ ~ +5 km/s/Mpc at z_peak ~ 3000-5000 with f_peak ~ 0.10

---

**Date:** 2025-11-24  
**Phase:** 3.1 Complete, 3.2 In Progress

