# Phase 4: Systematic Optimization to Close the Efficiency Gap

**Date:** 2025-11-24  
**Goal:** Boost ΔH₀ from +2 km/s/Mpc (30% tension reduction) to +4-5 km/s/Mpc (60-80% reduction)

---

## The Efficiency Gap

**Current Performance:**
- f_peak ~ 14% → ΔH₀ ~ +2.1 km/s/Mpc
- Ratio: ~0.15 km/s/Mpc per 1% f_peak

**Canonical EDE Performance:**
- f_peak ~ 10% → ΔH₀ ~ +5.0 km/s/Mpc
- Ratio: ~0.50 km/s/Mpc per 1% f_peak

**Gap:** We are **3.3× less efficient** than canonical EDE.

---

## Three-Lever Strategy

### Lever 1: Potential Shape (n_ridder)
**Physics:** Controls how sharply field rolls off plateau
- Lower n (2): Gentler roll, broader peak
- Higher n (4,5): Sharper roll, narrower peak

**Hypothesis:** Sharper peak (higher n) concentrates energy injection → better r_s suppression per unit f_peak

**Target:** 30-50% efficiency boost (ΔH₀: +2.1 → +3.0 km/s/Mpc)

### Lever 2: Photon Coupling (beta_ridder)
**Physics:** Direct coupling to photon bath modifies effective g_*
- beta = 0: Current (no coupling)
- beta ~ 0.05: Modest coupling amplifies r_s effect

**Hypothesis:** Coupling acts as multiplier on background expansion effect

**Target:** 30-50% additional boost (ΔH₀: +3.0 → +4.5 km/s/Mpc)

### Lever 3: Perturbation Treatment (fluid approximation)
**Physics:** Prevent field from clustering on small scales
- Current: Full Klein-Gordon perturbations
- Fluid: Force c_s² = 1, no clustering

**Hypothesis:** Reduces CMB damage, allows higher f_peak ceiling

**Target:** Raise viable f_peak from 14% → 18%, giving ΔH₀: +4.5 → +5.5 km/s/Mpc

**Combined Target:** ΔH₀ ~ +5.0 km/s/Mpc (75% tension reduction)

---

## Week-by-Week Plan

### Week 1: n-scan (THIS WEEK)

**Baseline:** Lambda = 1.5 eV, theta_i = 1.0 (known good from Phase 3)

**Scan:** n_ridder = [2, 3, 4, 5]

**For each n:**
1. Run CLASS with full perturbations
2. Extract: z_peak, f_peak, r_s, ΔH₀
3. Run CMB quality assessment
4. Record: Δℓ₁, max ΔC_ℓ/C_ℓ, RMS

**Success criteria:**
- ✅ Find n where ΔH₀ > +2.5 km/s/Mpc at similar CMB quality
- ✅ Understand n → efficiency relationship
- ❌ If all n give similar results → potential shape not the issue

**Deliverable:** `n_scan_results.md` with recommendation for optimal n

### Week 2: beta coupling

**Starting point:** Optimal n from Week 1

**Scan:** beta_ridder = [0.0, 0.01, 0.05, 0.10]

**Implementation check:**
- Verify beta is actually being used in perturbations
- May need to enable coupling code in `perturbations.c`

**For each beta:**
1. Run at optimal (Lambda, theta, n)
2. Same observables as Week 1
3. Check if beta boosts ΔH₀ without breaking CMB

**Success criteria:**
- ✅ beta > 0 gives measurable ΔH₀ boost (>20%)
- ✅ CMB quality preserved or improved
- ❌ If beta has no effect → coupling not implemented correctly OR not physics we need

**Deliverable:** `beta_scan_results.md` with coupling effectiveness

### Week 3: Fluid perturbations

**Starting point:** Optimal (n, beta) from Weeks 1-2

**Test:** Compare canonical vs. fluid perturbation treatments

**Implementation:**
- Add `ridder_fluid_approx` switch to code
- When enabled: c_s² = 1, no anisotropic stress
- Use w(a) from background solution

**For each mode:**
1. Run same (Lambda, theta, n, beta)
2. Compare CMB spectra
3. Try pushing theta higher in fluid mode

**Success criteria:**
- ✅ Fluid mode reduces max ΔC_ℓ/C_ℓ by >20%
- ✅ Allows theta = 1.2-1.3 with acceptable CMB
- ❌ If no difference → perturbations not the limiting factor

**Deliverable:** `perturbation_mode_comparison.md`

### Week 4: Combined optimization

**Starting point:** Best configuration from Weeks 1-3

**Task:** Fine-tune (Lambda, theta) with all improvements active

**Scan:** Small grid around Lambda=1.5, theta=1.0
- Lambda: [1.3, 1.5, 1.7]
- theta: [0.9, 1.0, 1.1, 1.2, 1.3]

**Goal:** Find sweet spot with all levers engaged

**Success criteria:**
- ✅ ΔH₀ ≥ +4.0 km/s/Mpc with acceptable CMB
- ✅ Clear improvement over Phase 3 baseline
- Decision point for Week 5

**Deliverable:** `optimized_configuration.md` with final parameters

---

## Week 5+: MCMC (Conditional)

**Only proceed if Week 4 achieves ΔH₀ ≥ +4.0 km/s/Mpc**

**Configuration:**
- Use optimized (n, beta, pert_mode) from Week 4
- Free parameters: Lambda, theta, omega_b, omega_cdm, H0, A_s, n_s, tau
- Fixed: beta (at optimal value), n (at optimal value)
- Data: Planck 2018 (TT,TE,EE) + BAO + SH0ES

**Sampler:** Cobaya
- 4-8 parallel chains
- Target: R-1 < 0.01
- Expected runtime: 2-7 days

**Questions to answer:**
1. What H₀ posterior do we get?
2. Is tension with Planck-ΛCDM statistically significant?
3. What happens to S₈?
4. Bayesian evidence ratio vs. ΛCDM

**Deliverable:** `mcmc_results.md` with full posterior analysis

---

## Fallback Plans

### If Week 1 fails (n doesn't help)
→ Potential shape not the issue
→ Focus on Weeks 2-3 (coupling and perturbations)

### If Weeks 1-2 fail (n and beta don't help)
→ Background physics not improvable
→ Week 3 (perturbations) becomes critical

### If Weeks 1-3 all fail (stuck at ΔH₀ ~ +2.5)
→ Fundamental model limitation identified
→ Pivot to "partial solution + cocktail" narrative
→ Document: "Ridder provides 40% relief, other mechanisms needed"

### If Week 4 reaches ΔH₀ ~ +3.5 (60% relief)
→ Marginal for full MCMC
→ Decision: Accept partial win OR explore more exotic modifications

---

## Success Metrics

### Minimal Success (acceptable)
- ΔH₀ ≥ +3.0 km/s/Mpc (45% tension reduction)
- CMB max ΔC_ℓ/C_ℓ < 30%
- Clear improvement over baseline

### Good Success (target)
- ΔH₀ ≥ +4.0 km/s/Mpc (60% tension reduction)
- CMB quality similar to Phase 3 theta=1.0
- Ready for MCMC

### Excellent Success (stretch goal)
- ΔH₀ ≥ +5.0 km/s/Mpc (75% tension reduction)
- CMB differences < 25% across all ℓ
- Viable single-mechanism solution

---

## Documentation Strategy

**Week-by-week summaries:**
- `WEEK1_N_SCAN.md`
- `WEEK2_BETA_COUPLING.md`
- `WEEK3_PERTURBATIONS.md`
- `WEEK4_OPTIMIZATION.md`

**Final synthesis:**
- `PHASE4_RESULTS.md` - What we learned
- `PHASE4_BEST_CONFIG.ini` - Optimal parameters
- `PHASE4_VS_PHASE3.md` - Before/after comparison

---

## Current Status

**Starting point (Phase 3 baseline):**
- Lambda = 1.5 eV
- theta_i = 1.0
- n_ridder = 3
- beta_ridder = 0.0
- Perturbations: canonical Klein-Gordon
- Result: ΔH₀ = +2.1 km/s/Mpc, f_peak = 14%

**Week 1 target:**
- Find optimal n_ridder
- Achieve ΔH₀ ≥ +2.5 km/s/Mpc
- Start date: Today!

---

**Phase 4 Status:** Week 1 starting now  
**Expected completion:** 4-5 weeks  
**Go/No-Go for MCMC:** End of Week 4

