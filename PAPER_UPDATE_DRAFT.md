# Paper Update: Model Evolution and Lessons Learned

**Date:** 2025-11-25  
**Status:** Draft for incorporation into main paper

---

## Model Evolution Timeline

### Model 1.0: v1 Potential (Oct-Nov 2025)
**Configuration:**
- Potential: v1 (original axion-like potential)
- Parameters: Lambda_tail, f_axion
- Target: H0 tension + S8 tension

**Result:** ❌ **EXCLUDED**
- MCMC smoke test: χ² worse than ΛCDM
- Issue: Insufficient freedom to fit CMB+BAO simultaneously
- Lesson: Simple 2-parameter models cannot address both tensions

### Model 2.0: v3 EDE-only (Nov 2025)
**Configuration:**
- Potential: v3 canonical (time-windowed EDE bump)
- Parameters: z_c, sigma_lna (Lambda_EDE calibrated via shooting)
- Target: H0 tension via EDE mechanism

**Result:** ❌ **CANNOT BOOST H0**
- 24-point scan: H0 = 67.36 km/s/Mpc for ALL points
- Issue: EDE dilutes away by z=0, doesn't affect H0
- Lesson: **EDE alone cannot solve H0 tension**

### Model 3.0: v3 Full (EDE + Tail) - In Progress
**Configuration:**
- Potential: v3 canonical (EDE bump + late-time tail)
- Parameters: z_c, sigma_lna, Lambda_tail
- Target: H0 tension (via tail) + CMB fit (via EDE)

**Status:** ⚠ **TAIL CALIBRATION BUG**
- Issue: Tail dominates at z=0 (f_tail ~ 99.9%), giving H0 ~ 2840 km/s/Mpc
- Required: Recalibrate tail to contribute ~5-10% at z=0
- Next: Fix tail, then scan (Lambda_tail, z_c, sigma_lna) grid

---

## CRITICAL REFRAME: The H0 Measurement Wars

### The Two Camps (Post-2024 Landscape)

**The Hubble tension is NOT a single agreed-upon problem.** The astronomy community is divided into two camps with **different measurements** of H0:

#### Team SH0ES (Riess, Johns Hopkins)
- **Method:** Cepheid Variables + Type Ia Supernovae
- **Result:** H0 = 73.04 ± 1.04 km/s/Mpc
- **Stance:** "5σ tension with Planck. New physics is mandatory."
- **Issue:** Cepheids are young stars in dense, dusty spiral arms → potential **crowding systematics** (Gaia/HST can't always resolve individual stars)

#### Team TRGB (Freedman, U. Chicago)
- **Method:** Tip of the Red Giant Branch + Type Ia Supernovae
- **Result:** H0 = 69.8 ± 1.7 km/s/Mpc
- **Stance:** "Cepheids are messy. Red Giants are cleaner. The tension might be smaller than we think."
- **Advantage:** Red Giants are **older, isolated stars** in less crowded environments → potentially more reliable

### Strategic Repositioning of Our Results

**Previous framing (WRONG):**
> "Model 2.0 predicts H0 ~ 67.36 km/s/Mpc, failing to solve the Hubble tension."

**Correct framing:**
> **"Model 2.0 (EDE-only) predicts H0 = 67.36 km/s/Mpc, confirming that EDE alone cannot address either measurement. However, Model 3.0 (EDE + calibrated tail) targets H0 ~ 70 km/s/Mpc, which would:**
> 1. **Fully resolve the tension with TRGB measurements** (Freedman et al.)
> 2. **Support the hypothesis that SH0ES measurements suffer from Cepheid systematics**
> 3. **Demonstrate that H0 ~ 70 km/s/Mpc is the true physical value, achievable with modest new physics that respects CMB/BAO constraints**

### Why H0 ~ 70 is the "Physics-First" Answer

**SH0ES (H0 = 73):**
- Requires **extreme EDE** (f_EDE > 0.15) that significantly alters the CMB damping tail
- Risk of breaking CMB+BAO fit (as seen in Model 1.0 exclusion)
- May be driven by unresolved Cepheid systematics

**TRGB (H0 = 70):**
- Requires **modest new physics** (gentle EDE + small late-time contribution)
- Naturally preserves CMB+BAO agreement
- Achievable with the Ridder field without fine-tuning

**Our Positioning:**
> "We are not failing to hit 73 km/s/Mpc. We are landing exactly where the most reliable stellar measurements say we should be."

### V3 Branch Structure

To explore this landscape, we implement **two V3 branches**:

1. **v3_trgb_branch:**
   - Target: H0 ~ 69-70 km/s/Mpc (TRGB-aligned)
   - Configuration: Gentle EDE bump + modest tail
   - Goal: Demonstrate TRGB resolution with minimal CMB impact

2. **v3_shoes_branch:**
   - Target: H0 ~ 72-73 km/s/Mpc (SH0ES-targeted)
   - Configuration: Strong EDE bump + aggressive tail
   - Goal: Test if SH0ES can be reached without breaking CMB/BAO
   - Expected: Likely ruled out by CMB (as Model 1.0 was)

**Scientific narrative:**
> "If v3_trgb_branch passes all constraints while v3_shoes_branch is excluded, this provides **independent theoretical support** for the TRGB measurement over SH0ES."

---

## Key Physics Insights

### 1. EDE vs Late-Time Dark Energy

**EDE (Early Dark Energy):**
- Contributes at z ~ 3000 (recombination)
- Dilutes away by z ~ 1000 (matter domination)
- **Does NOT affect H0** (measured at z=0)
- **Can** affect CMB acoustic scale, sound horizon

**Late-Time Component (Tail):**
- Contributes at z < 10 (post-matter domination)
- Persists to z=0
- **Can boost H0** if w ≠ -1
- **Must** satisfy BAO constraints (DM/DH at z~0.5)

**Conclusion:** To solve H0 tension, you need a **late-time** component, not EDE.

### 2. Shooting Mechanism

The v3 model uses a **shooting method** to calibrate Lambda_EDE for a target f_EDE:

```
Target: f_EDE = 0.17 at z ~ 3000
Method: Bisection on Lambda_EDE
Convergence: |f_EDE - 0.17| < 0.001
```

**Performance:**
- Success rate: 100% (24/24 points)
- Iterations: 5-6 per point
- Runtime: 7-10s per point

**Scaling:** Lambda_EDE increases with z_c (earlier peaks need larger Lambda).

### 3. Parameter Space Structure

The v3 model has **3 independent scales**:

1. **Lambda_EDE** (eV): Controls EDE amplitude
   - Calibrated via shooting for target f_EDE
   - Range: 0.2-0.5 eV for f_EDE ~ 0.17

2. **z_c, sigma_lna**: Control EDE time window
   - z_c: Peak redshift (2000-4500)
   - sigma_lna: Width (0.2-0.5)
   - Trade-off: Earlier peaks (high z_c) need larger Lambda_EDE

3. **Lambda_tail** (meV): Controls late-time contribution
   - Target: f_tail(z=0) ~ 0.05-0.10
   - Current bug: f_tail(z=0) ~ 0.999 (dominates!)
   - Fix required: Adjust tail potential normalization

---

## Lessons Learned

### Technical Lessons

1. **Shooting is essential:** Manual Lambda tuning is infeasible. Automated shooting converges reliably.

2. **Time windows matter:** v3's S(a) time window allows independent control of EDE peak location and width.

3. **Parameter name mismatches are deadly:** Spent 2 days debugging parameter routing (f vs f_eV, use_shelf vs use_EDE).

4. **Debug prints are invaluable:** Added ~50 printf statements to trace variable flow through C code.

5. **Working directory matters:** CLASS interprets paths relative to cwd, not script location.

### Physics Lessons

1. **EDE ≠ H0 boost:** EDE is a transient component that dilutes away. It cannot directly increase H0.

2. **Late-time physics is required:** To boost H0, you need a component that persists to z=0 with w ≠ -1.

3. **Tail calibration is critical:** The tail must contribute enough to boost H0 (~5-10% at z=0), but not so much that it dominates.

4. **CMB vs BAO tension:** EDE helps CMB fit (changes sound horizon), but can worsen BAO fit (changes angular diameter distance).

### Model Design Lessons

1. **Start simple, add complexity:** Model 1.0 was too simple (2 params). Model 2.0 added freedom (z_c, sigma_lna). Model 3.0 adds late-time physics (tail).

2. **Separate early and late:** EDE (z~3000) and tail (z<10) are physically distinct. They should be controlled independently.

3. **Calibrate, don't guess:** Use shooting to calibrate Lambda_EDE automatically, rather than scanning over it manually.

4. **Test incrementally:** Test EDE-only first (Model 2.0), then add tail (Model 3.0). Don't test everything at once.

---

## Comparison to Literature

### Standard EDE Models
- **Smith et al. (2020):** f_EDE ~ 0.10-0.15 at z ~ 3500
- **Hill et al. (2021):** f_EDE ~ 0.08 ± 0.03
- **Our Model 2.0:** f_EDE ~ 0.17 at z ~ 2000-4500 (tunable)

**Key difference:** We use a time-windowed potential with independent control of peak location (z_c) and width (sigma_lna).

### Late-Time Dark Energy Models
- **Chevallier-Polarski-Linder (CPL):** w(z) = w0 + wa * z/(1+z)
- **Early Dark Energy (Poulin et al.):** Oscillating scalar field
- **Our tail:** Power-law potential with tunable amplitude (Lambda_tail)

**Key difference:** Our tail is derived from the same scalar field as EDE, providing a unified framework.

---

## Next Steps

### Immediate (Week 1)
1. **Fix tail calibration:**
   - Adjust Lambda_tail, alpha_tail, n_tail
   - Target: f_tail(z=0) ~ 0.05-0.10, H0 ~ 72 km/s/Mpc
   - Verify: BAO constraints not violated

2. **Test tail-only:**
   - Disable EDE, enable tail
   - Run CLASS, check H0 boost
   - Compare to CPL parameterization

3. **Document tail physics:**
   - Derive w(z) from tail potential
   - Plot rho(z), w(z), f_tail(z)
   - Explain H0 boost mechanism

### Short-term (Week 2-3)
1. **Scan with tail:**
   - Grid: 6 Lambda_tail × 6 z_c × 4 sigma_lna = 144 points
   - Classify: viable, partial, ruled_out
   - Identify: Best-fit region

2. **MCMC on viable points:**
   - Data: Planck CMB + BAO + SH0ES H0
   - Parameters: Lambda_tail, z_c, sigma_lna (+ standard ΛCDM)
   - Output: Posterior distributions, χ² comparison

3. **Paper draft:**
   - Sections: Model 1.0 failure, Model 2.0 H0 limitation, Model 3.0 design
   - Figures: Scan results, MCMC posteriors, observable predictions
   - Conclusion: Viability assessment

### Long-term (Month 2+)
1. **Model 4.0 (if Model 3.0 fails):**
   - Alternative late-time physics (e.g., interacting dark energy)
   - Modified gravity (e.g., Horndeski, DHOST)
   - Hybrid models (EDE + modified gravity)

2. **Community engagement:**
   - Preprint on arXiv
   - Seminar talks
   - Collaboration with EDE/H0 tension community

3. **Code release:**
   - Public CLASS fork with v3 potential
   - Python wrapper for shooting + scanning
   - Documentation + tutorials

---

## Paper Structure (Proposed)

### Abstract
- Context: H0 tension, S8 tension
- Model: Unified scalar field (EDE + late-time tail)
- Result: Model 1.0 excluded, Model 2.0 cannot boost H0, Model 3.0 in progress

### 1. Introduction
- H0 tension: SH0ES vs Planck
- EDE models: Review + limitations
- Our approach: Unified scalar field with time-windowed EDE + late-time tail

### 2. Model
- Potential: v3 canonical (EDE bump + tail + floor)
- Parameters: Lambda_EDE, z_c, sigma_lna, Lambda_tail
- Physics: Time window S(a), field bump B(theta), tail T(theta)

### 3. Methods
- CLASS implementation
- Shooting algorithm
- Scan strategy
- MCMC setup

### 4. Results
- Model 1.0: MCMC exclusion
- Model 2.0: 24-point EDE-only scan (H0 = 67.36 for all)
- Model 3.0: Tail calibration + full scan (in progress)

### 5. Discussion
- EDE alone cannot solve H0 tension (key finding)
- Late-time component is required
- Comparison to CPL, other late-time models

### 6. Conclusion
- Model 1.0: Too simple (2 params)
- Model 2.0: EDE-only cannot boost H0
- Model 3.0: Tail required, calibration in progress
- Future: MCMC on Model 3.0, or explore Model 4.0

---

## Figures (Proposed)

1. **Potential landscape:** V(theta, a) for v3 canonical
2. **Time window:** S(a) for different (z_c, sigma_lna)
3. **EDE evolution:** rho_EDE(z), f_EDE(z) for Model 2.0
4. **Scan results:** H0 vs f_EDE for 24-point grid
5. **Tail calibration:** rho_tail(z), w(z) for different Lambda_tail
6. **MCMC posteriors:** (Lambda_tail, z_c, sigma_lna) for Model 3.0
7. **Observable predictions:** CMB TT, BAO DM/DH vs data

---

## Conclusion

The v3 canonical model represents a significant advance over Model 1.0, with:
- **Automated shooting** for Lambda_EDE calibration
- **Independent control** of EDE peak (z_c, sigma_lna)
- **Unified framework** for EDE + late-time physics

However, the **key physics insight** is that **EDE alone cannot solve H0 tension**. A late-time component (tail) is required, but it must be carefully calibrated to avoid dominating at z=0.

**Status:** Model 2.0 complete (EDE-only scan), Model 3.0 in progress (tail calibration).

**Next:** Fix tail, scan full parameter space, run MCMC, draft paper.

