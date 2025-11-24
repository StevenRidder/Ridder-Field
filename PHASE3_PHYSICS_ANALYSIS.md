# Phase 3: Physics Analysis - EDE vs. ΛCDM

## Configuration Comparison

| Parameter | Vanilla ΛCDM | EDE Benchmark |
|-----------|--------------|---------------|
| has_ridder | no | yes |
| Lambda [eV] | N/A | 0.4964 |
| theta_i | N/A | 0.75 |
| z_peak | N/A | ~691 |
| f_peak | N/A | ~0.063 |

**Status:** Using vanilla CLASS ΛCDM as control (frozen Ridder control abandoned due to calibration issues).

---

## Key Findings from Plots

### 1. Expansion History (H(z))

**Observations:**
- ΔH/H < 1% at all redshifts
- Slight enhancement in EDE at intermediate z
- H₀ identical by construction (both = 67.36 km/s/Mpc)

**Interpretation:** The EDE bump at z~691 is too late and too weak to significantly alter the expansion rate.

### 2. Energy Density Evolution

**ΛCDM:**
- Standard radiation → matter → Λ transitions
- Equality at z ~ 3400
- Recombination at z ~ 1100

**EDE:**
- Ridder field peaks at z ~ 691 with Ω_Ridder ~ 0.063
- Peak is in **matter-dominated era**, not near equality
- Field decays completely by z ~ 10
- Other components (γ, matter, Λ) nearly unchanged

**Critical Issue:** EDE peaks ~5× too late compared to canonical EDE models (which peak at z ~ 3000-5000 near equality).

### 3. Ridder Field Evolution

**Peak behavior:**
- ρ_Ridder peaks around z ~ 691
- f_peak ~ 6.3% of total energy density
- Rapid decay post-peak

**Late-time behavior:**
- Ω_Ridder < 10⁻⁹ for z < 100
- Completely negligible by z = 0
- No late-time dark energy contamination ✓

**Problem:** Field activates after matter-radiation equality, so it doesn't affect the expansion history at epochs that matter for H₀.

### 4. CMB Power Spectrum

**Differences observed:**
- ΔC_ℓ/C_ℓ ~ +3% at first peak (ℓ ~ 220)
- ΔC_ℓ/C_ℓ ~ +3-5% at high-ℓ (damping tail)
- Peak locations unchanged
- No dramatic shifts in acoustic structure

**Interpretation:** 
- The EDE field is affecting recombination-era physics
- ~3% shifts are detectable but not dramatic
- Shifts are smaller than needed to resolve H₀ tension
- Peak locations fixed because we fixed H₀ (not solving for it)

---

## Why No H₀ Shift?

### The H₀ Tension Mechanism (Canonical EDE)

In successful EDE models that address H₀ tension:

1. **Field peaks near equality** (z ~ 3000-5000)
2. **Increases expansion rate** pre-recombination
3. **Reduces sound horizon** r_s at recombination
4. **To preserve acoustic angle** θ_s = r_s/D_A:
   - If r_s decreases, must compensate
   - Increase H₀ to decrease D_A
   - Result: Higher H₀ matches same θ_s

### Our Current Configuration

1. **Field peaks at z ~ 691** ❌ (matter era, not equality)
2. **f_peak ~ 6.3%** ❌ (canonical EDE uses ~10%)
3. **H₀ fixed to input** ❌ (not solving for H₀)

**Result:** EDE is present but doesn't affect the right epochs → no H₀ shift mechanism engaged.

---

## Concrete Numbers

### Expansion Rate Differences

| Epoch | z | ΔH/H [%] | Comment |
|-------|---|----------|---------|
| Today | 0 | 0.00 | Fixed by construction |
| Recombination | 1100 | +0.3 | Minimal effect |
| Equality | 3400 | +0.1 | EDE not yet active |
| EDE Peak | 691 | +0.5 | Peak effect, but too late |

### CMB Spectrum

| Observable | ΛCDM | EDE | Δ | % Change |
|-----------|------|-----|---|----------|
| ℓ(1st peak) | 221 | 221 | 0 | 0.0% |
| C_ℓ^TT(peak) | 7.73e-10 | 7.98e-10 | +2.6e-11 | +3.3% |
| High-ℓ power | 5.03e-11 | 5.21e-11 | +1.7e-12 | +3.4% |

---

## What We've Learned

### ✅ What's Working

1. **Code is stable** - Full CLASS runs with perturbations, lensing, CMB spectra
2. **Field decays properly** - No late-time contamination
3. **Physics is sane** - No pathologies, reasonable spectrum shapes
4. **Numerical precision good** - ~3% effects are cleanly resolved

### ❌ What's Not Working

1. **z_peak too late** - 691 vs. target ~3000-5000
2. **f_peak too small** - 6.3% vs. target ~10%
3. **Not affecting H₀** - Expansion history nearly unchanged at relevant epochs

### 🎯 What's Needed

To get H₀ shifts, we need to move the EDE bump **earlier** and make it **stronger**:

**Parameter adjustments:**
- **Increase Lambda** → pushes z_peak earlier (from Phase 2: Lambda × 10 → z_peak × ~10)
- **Increase theta_i** → increases f_peak (from Phase 2: higher theta → higher f_peak)
- **Target:** z_peak ~ 3000-5000, f_peak ~ 0.10

---

## Next Steps

### Option A: Lambda Scan (Push z_peak Earlier)

**Goal:** Find Lambda that gives z_peak ~ 3000-5000

**Method:**
1. From Phase 2: Lambda ~ 0.50 eV → z_peak ~ 691
2. Empirical scaling: z_peak ∝ Lambda (roughly)
3. Try Lambda ~ 2-5 eV → target z_peak ~ 3000-5000
4. Use proper diagnostic to measure z_peak

**Expected result:** Peak moves into equality era, engages H₀ shift mechanism.

### Option B: Implement "Fix θ_s, Solve for H₀"

**Goal:** Extract effective H₀ from current EDE model

**Method:**
1. Measure θ_s from both ΛCDM and EDE
2. For EDE: find H₀ that would preserve ΛCDM's θ_s
3. This gives "effective H₀" that EDE prefers
4. Compare to input H₀ = 67.36 km/s/Mpc

**Expected result:** Will likely show ΔH₀ ~ 0 because field peaks too late, confirming diagnosis.

### Recommendation

**Do Option A first** - Scan Lambda to find configuration with z_peak ~ 3000-5000. Once we have a physically relevant EDE model, then implement Option B to quantify the actual H₀ shift.

---

## Files Generated

### Plots (in `plots/`)
- `phase3_comparison_expansion.png` - H(z) and ΔH/H
- `phase3_comparison_densities.png` - Ω_i(z) for all components
- `phase3_comparison_ridder_evolution.png` - Ridder field zoom
- `phase3_comparison_cl_comparison.png` - C_ℓ^TT and fractional differences

### Scripts
- `plot_ede_vs_lcdm.py` - Physics comparison plotting tool

### Documentation
- `PHASE3_PHYSICS_ANALYSIS.md` - This document

---

## Summary

We now have clean physics comparisons showing:
1. Current EDE configuration peaks too late (z~691 vs. z~3000 target)
2. Peak amplitude is modest (6.3% vs. 10% target)  
3. CMB shows ~3% effects but no H₀ shift mechanism engaged
4. All code infrastructure working correctly

**Next action:** Lambda scan to push z_peak into the z ~ 3000-5000 range where EDE can actually affect H₀.

---

**Date:** 2025-11-24  
**Status:** Phase 3.1 complete with correct baseline. Ready for Lambda scan to find H₀-relevant parameters.

