# Unified Potential Validation Roadmap

**Status:** Deployed, awaiting validation  
**Goal:** Verify unified mode before MCMC

---

## Strategic Decision: Validate First, MCMC Later

**Why not MCMC now?**
1. ✅ **v2 already mapped the space** - We know where hero (β=0.20) and safe (β=0.15) live
2. ⚠️  **Unified is fresh code** - Need to prove it reproduces v2 physics
3. 🎯 **Big payoff is unified story** - Show one field across all epochs, not just EDE

**What we're doing instead:**
1. Validate unified reproduces v2 at EDE epoch
2. Test tail behaves like dark energy
3. Test plateau can drive inflation
4. THEN bring in MCMC as final arbiter

---

## Phase 1: Validate Unified EDE vs V2

### Goal
Prove that unified hero and safe reproduce v2 benchmarks within 5%

### Tool
`test_unified_cdm_metrics.py` (created)

### What it does
1. Runs `unified_cdm_hero.ini` and `unified_cdm_safe.ini`
2. Extracts:
   - r_s from background
   - ΔH₀ (effective H0 shift)
   - z_peak, f_peak (EDE diagnostics)
   - Max CMB Δ, RMS CMB Δ (spectral quality)
3. Compares to v2 reference from `cdm_coupling_optimization_results.json`
4. Reports PASS/FAIL for each metric

### Success Criteria
**Hero (β=0.20, σ_z=0.5):**
- ΔH₀ within 5% of +3.49 km/s/Mpc
- z_peak within 5% of ~3000
- f_peak within 5% of ~14%
- Max CMB Δ within 5% of 40%

**Safe (β=0.15, σ_z=0.5):**
- ΔH₀ within 5% of +3.14 km/s/Mpc
- z_peak within 5% of ~3000
- f_peak within 5% of ~14%
- Max CMB Δ within 5% of 37%

### If it passes
✅ Unified EDE implementation is validated  
✅ Can trust that shelf window parameters are correct  
✅ Move to Phase 2  

### If it fails
- Review shelf window parameters (theta_EDE_low/high, sigma)
- Check initial conditions mapping
- Adjust and re-test

---

## Phase 2: Validate Tail (Late Dark Energy)

### Goal
Verify tail-only mode produces acceptable late-time dark energy

### Tool
`test_tail_only.ini` (created)

### Config
- `ridder_use_tail = yes`
- `ridder_use_shelf = no`
- `ridder_use_plateau = no`
- `beta_ridder = 0.0` (no coupling)

### What to check
1. Run CLASS with tail-only config
2. Extract from background:
   - Ω_Λ (should be ~ 0.7)
   - w(z) at z=0 (should be ~ -1.0)
   - w(z) evolution (should stay close to -1)
3. Compare to standard ΛCDM

### Success Criteria
- Ω_Λ matches target within 1%
- |w₀ - (-1.0)| < 0.01
- |dw/dz| small at late times

### Parameters to tune
- `ridder_Lambda_tail_eV` - sets vacuum energy scale
- `ridder_n_tail` - controls minimum flatness

### If it passes
✅ Tail behaves like cosmological constant  
✅ Late-time dark energy regime validated  
✅ Move to Phase 3  

---

## Phase 3: Validate Plateau (Inflation)

### Goal
Verify plateau-only mode can drive acceptable inflation

### Tool
`test_plateau_only.ini` (created)

### Config
- `ridder_use_tail = no`
- `ridder_use_shelf = no`
- `ridder_use_plateau = yes`
- `theta_i_ridder = 10.0` (start on plateau)

### What to check
1. Run CLASS in minimal mode (scalar-dominated)
2. Extract slow-roll parameters from V, V', V'':
   - ε = (M_Pl²/2)(V'/V)²
   - η = M_Pl²(V''/V)
3. Compute inflationary observables:
   - n_s ≈ 1 - 6ε + 2η
   - r ≈ 16ε
   - N_e (number of e-folds)
4. Compare to Planck constraints

### Success Criteria
- n_s within Planck 1σ range (0.9649 ± 0.0042)
- r < 0.07 (Planck + BICEP upper limit)
- N_e ~ 50-60 (typical for standard inflation)

### Parameters to tune
- `ridder_Lambda_inf_eV` - sets inflation energy scale
- `ridder_theta0_inf` - controls plateau rise
- `ridder_f` - decay constant (affects slow-roll)

### If it passes
✅ Plateau can drive inflation  
✅ Inflationary regime validated  
✅ Move to Phase 4  

---

## Phase 4: Full Unified Test

### Goal
Verify all three components can coexist

### Config
- All three components ON
- Parameters from validated regimes
- Full cosmology (matter, radiation, etc.)

### What to check
1. Run full unified config
2. Verify no interference between regimes:
   - Tail doesn't affect EDE epoch
   - Shelf doesn't affect late times
   - Plateau isolated at early times
3. Extract metrics from all epochs

### Success Criteria
- Late-time: matches tail-only results
- EDE epoch: matches v2 validated results
- Early-time: consistent with plateau tests
- No numerical instabilities

---

## Phase 5: MCMC (Only After Phases 1-4 Pass)

### Why wait until now?
At this point you will have:
- ✅ Proven unified = v2 at EDE epoch
- ✅ Shown tail fits late-DE data
- ✅ Shown plateau fits inflation data
- ✅ Verified all three can coexist

**Then MCMC answers:** "How hard do Planck + BAO + SH0ES constrain this complete theory?"

### MCMC Setup
**Free parameters:**
- Shelf: `Lambda_EDE`, `theta_EDE_low/high`
- CDM coupling: `beta_ridder`, `beta_sigma_z`
- Tail: `Lambda_tail`, `n_tail`
- Plateau: `Lambda_inf`, `theta0_inf` (if including inflation)

**Priors:**
- Use v2 validated ranges for shelf + CDM coupling
- Use Phase 2 results for tail priors
- Use Phase 3 results for plateau priors

**Data:**
- Planck TT,TE,EE + lowl + lensing
- BAO (BOSS, eBOSS)
- SH0ES (local H0)

### Expected Outcome
MCMC will tell you:
- Posterior on `beta_ridder` (how much coupling do data prefer?)
- Posterior on `f_EDE` (how much EDE energy is allowed?)
- Constraints on inflation parameters (if included)
- Whether model prefers hero (β=0.20) or safe (β=0.15) region

---

## Current Status

### Completed
- [x] Unified potential deployed and running
- [x] Hero and safe configs smoke tested (both run successfully)
- [x] Validation script created (`test_unified_cdm_metrics.py`)
- [x] Tail-only test config created
- [x] Plateau-only test config created

### Next Actions (Immediate)
- [ ] **Phase 1:** Run `test_unified_cdm_metrics.py`
  - Extract metrics from unified hero/safe runs
  - Compare to v2 benchmarks
  - Verify within 5% tolerance
  
- [ ] **Phase 2:** Run tail-only test
  - Verify Ω_Λ ~ 0.7, w₀ ~ -1
  - Tune `Lambda_tail` if needed
  
- [ ] **Phase 3:** Run plateau-only test
  - Extract inflation observables
  - Tune plateau parameters
  - Verify Planck compatibility

### Later Actions
- [ ] **Phase 4:** Full unified test (all components)
- [ ] **Phase 5:** Tier 3 MCMC with validated model

---

## Files Created

### Validation Tools
- `test_unified_cdm_metrics.py` - Hero/safe validation
- `test_tail_only.ini` - Late-DE test config
- `test_plateau_only.ini` - Inflation test config

### Documentation
- `UNIFIED_DEPLOYMENT_SUCCESS.md` - Deployment report
- `UNIFIED_VALIDATION_ROADMAP.md` - This document
- `V2_TO_UNIFIED_MAPPING.md` - Parameter mapping

---

## Key Insights

### Why This Approach Works
1. **Incremental validation** - Test each regime separately
2. **Data-driven** - Use v2 optimization to guide shelf
3. **Theory-driven** - Constrain tail and plateau independently
4. **Complete** - MCMC tests full model, not partial

### Why Not Jump to MCMC
- v2 already explored EDE + CDM space thoroughly
- Unified is new code, needs validation first
- Big scientific payoff is showing one field across epochs
- MCMC on partial model wastes compute and risks wrong conclusions

### Strategic Value
By validating incrementally, you will know EXACTLY what breaks if something fails:
- If Phase 1 fails: shelf window or CDM coupling issue
- If Phase 2 fails: tail energy scale or minimum shape
- If Phase 3 fails: plateau parameters or slow-roll
- If Phase 4 fails: interference between regimes

This is much better than "MCMC didn't converge" with no diagnostic power.

---

## Bottom Line

**Current state:** Unified potential deployed, smoke tested, awaiting validation

**Next milestone:** Phase 1 validation (unified = v2 within 5%)

**Path to MCMC:** Phases 1 → 2 → 3 → 4 → 5

**Timeline estimate:**
- Phase 1: 1-2 hours (run tests, adjust if needed)
- Phase 2: 1-2 hours (tail tuning)
- Phase 3: 2-4 hours (inflation parameter space)
- Phase 4: 1 hour (integration test)
- Phase 5: Days-weeks (MCMC runtime)

**You're on the right path.** Validate first, MCMC last.

---

**END OF VALIDATION ROADMAP**

