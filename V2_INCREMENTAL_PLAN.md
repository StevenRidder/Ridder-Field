# V2 Model Design: Learning from V1's Failure

**Date**: November 23, 2025  
**Status**: Design Phase - Following Incremental Validation  
**Current Phase**: Phase 0 (Preparation)

---

## Core Philosophy

**"Copy success, then innovate."**

V1 failed because we tried to build a novel EDE model from scratch without validating against known working implementations. V2 will:

1. Start with a proven EDE model (AxiCLASS)
2. Reproduce their published results EXACTLY
3. Only then add Ridder-specific modifications
4. Test each modification independently

---

## Phase 0: Quick Validation Check ✅ COMPLETE

**Goal**: Validate current V2 implementation before committing to full plan

**Status**: ✅ **COMPLETE** (November 23, 2025)

### Steps

1. ✅ **Create single-point χ² calculator**
   - Tool to test CLASS parameters without MCMC
   - Returns: χ², H₀, C_ℓ(TT), C_ℓ(TE), C_ℓ(EE)
   - **File**: `phase3/tools/single_point_chi2.py`

2. ✅ **Test V2 with smoke test parameters**
   - Lambda_EDE = 0.6
   - theta_i = 2.17
   - beta = 0.035
   - **Result**: χ² = 2919.19

3. ✅ **Compare to ΛCDM baseline**
   - Run same test with Lambda_EDE = 0
   - **Result**: χ² = 2919.19 (ΛCDM)
   - **Δχ² = 0.00** ✅ **PASS**

4. ✅ **Decision Point**
   - ✅ Δχ² < 10 → **PASS** (V2 doesn't break CMB)
   - ⚠️ **BUT**: Δχ² = 0 means V2 is doing nothing!
   - **Conclusion**: V2 parameters need tuning OR EDE is too weak

### Results Summary

| Test | χ² | H₀ (km/s/Mpc) | Status |
|------|-----|---------------|--------|
| ΛCDM (Lambda=0) | 2919.19 | 67.36 | ✅ Baseline |
| V2 (Lambda=0.6) | 2919.19 | 67.36 | ⚠️ No effect |

**Interpretation:**
- ✅ V2 doesn't crash CLASS
- ✅ V2 doesn't break CMB (Δχ² = 0)
- ⚠️ **V2 has no observable effect** (same χ² and H₀ as ΛCDM)
- 🚨 **This confirms we need AxiCLASS validation** to understand correct parameter ranges

### Success Criteria
- ✅ Single-point test runs without crashes
- ⚠️ χ² = 2919 (higher than expected ~2760-2780, but consistent)
- ✅ Δχ² = 0 < 10 (V2 doesn't break CMB)
- ❌ V2 has no effect (EDE too weak or parameters wrong)

### Files Created
- `phase3/tools/single_point_chi2.py` - χ² calculator ✅
- `V2_INCREMENTAL_PLAN.md` - This document ✅

### Next Action
**Proceed to Phase 1: AxiCLASS Validation**

We need to:
1. Download AxiCLASS
2. See what parameters they use
3. Understand why their EDE works and ours doesn't

---

## Phase 1: Reproduce AxiCLASS (Validation) ⏳ NEXT

**Goal**: Prove we can implement a working EDE model by reproducing AxiCLASS results

**Status**: 🔴 **NOT STARTED**

### Steps

1. **Download and Study AxiCLASS**
   ```bash
   cd ~/Downloads
   git clone https://github.com/PoulinV/AxiCLASS.git
   cd AxiCLASS
   make
   ```

2. **Run Their Default EDE Parameters**
   ```python
   # From AxiCLASS paper (Poulin et al. 2018)
   params = {
       'scf_potential': 'axion',
       'n_axion': 3,
       'f_axion': 1e27,  # eV
       'log10_axion_ac': -3.5,  # log10(a_c)
       'log10_fraction_axion_ac': -1.0,  # log10(f_EDE(a_c))
       'theta_i_scf': 2.83,  # Initial field value
   }
   ```

3. **Verify Their χ² Values**
   - Run MCMC with Planck 2018 data
   - Expected: χ² ≈ 2760-2770 (comparable to ΛCDM)
   - Expected: H₀ ≈ 68-69 km/s/Mpc (Planck-like for Planck-only data)
   - Expected: f_EDE ≈ 10-14% at z ≈ 3000

4. **Compare to V1**
   - What's different in their potential?
   - What's different in their initial conditions?
   - What's different in their coupling (if any)?

### Success Criteria
- ✅ AxiCLASS reproduces published results
- ✅ χ² ≈ 2760-2770 (good CMB fit)
- ✅ We understand WHY it works

### Files Created
- `phase3/axiclass_test.py` - Test AxiCLASS with default params
- `phase3/axiclass_results.log` - Their χ² and parameter values
- `phase3/AXICLASS_VALIDATION.md` - Summary of findings

---

## Phase 2: Implement AxiCLASS in Our Codebase 🔴 NOT STARTED

**Goal**: Copy AxiCLASS implementation into our CLASS fork and verify it works identically

**Status**: 🔴 **NOT STARTED**

### Steps

1. **Copy Source Files**
   ```bash
   # Copy AxiCLASS modifications to our CLASS fork
   cp AxiCLASS/source/background.c phase2/class/source/
   cp AxiCLASS/source/perturbations.c phase2/class/source/
   cp AxiCLASS/include/*.h phase2/class/include/
   ```

2. **Compile and Test**
   ```bash
   cd phase2/class
   make clean
   make -j8
   cd python
   python3 setup.py install --user
   ```

3. **Run Identical Test**
   - Use EXACT same parameters as AxiCLASS
   - Compare output: C_ℓ(TT), C_ℓ(TE), C_ℓ(EE)
   - Verify: Do we get identical power spectra?

4. **Run Single-Point χ² Test**
   ```python
   # Test with Planck 2018 data
   from cobaya.run import run
   
   info = {
       'likelihood': {'planck_2018_lowl.TT': None, ...},
       'theory': {'classy': {'extra_args': {...}}},
       'params': {...},  # AxiCLASS default values
   }
   
   # Should get χ² ≈ 2760-2770
   ```

### Success Criteria
- ✅ Our CLASS fork produces identical results to AxiCLASS
- ✅ Single-point χ² test passes (χ² < 2800)
- ✅ Power spectra match AxiCLASS output

### Files Created
- `phase3/v2_validation.py` - Compare our CLASS to AxiCLASS
- `phase3/v2_validation_plots/` - Power spectra comparisons
- `phase3/V2_AXICLASS_COMPARISON.md` - Detailed comparison

---

## Phase 3: Add Ridder-Specific Modifications (Innovation) 🚨 BLOCKED

**Goal**: Incrementally add Ridder features while maintaining a good CMB fit

**Status**: 🚨 **BLOCKED - V2 IMPLEMENTATION IS BROKEN**

### 🚨 CRITICAL ISSUE DISCOVERED

**Grid scan results (November 23, 2025):**
- Tested Lambda_EDE: 0, 2, 5, 10
- Tested theta_i: 2.0, 2.5
- Tested beta: 0.0, 0.05

**Result:** ALL parameter combinations give **IDENTICAL** χ² = 2919.19 and H₀ = 67.36

**Conclusion:** V2 Ridder field has **ZERO observable effect** on cosmology, even with Lambda=10 (17× larger than smoke test value).

**Evidence:**
- CLASS debug shows "Ridder field ENABLED"
- But χ² and H₀ are unchanged from ΛCDM
- This means the field is not actually contributing to the energy budget

**Possible causes:**
1. **Field is stuck at minimum** (φ = 0) and never evolves
2. **Energy scale is too small** (Λ⁴ is negligible compared to radiation/matter)
3. **Initial conditions are wrong** (field starts at zero instead of θᵢ)
4. **Potential is broken** (V(φ) = 0 for all φ)
5. **Background evolution is not using the field** (ρ_ridder = 0 always)

**Next action:** Debug V2 implementation before proceeding

### Modification 1: Add Matter Coupling (β)

**What**: Add a coupling between the Ridder field and matter (CDM/baryons).

**How**:
```c
// In perturbations.c
// Modify the CDM/baryon equations to include Ridder field coupling
delta_cdm' += beta_ridder * phi * delta_cdm
```

**Test**:
- Start with β = 0 (no coupling) → Should match AxiCLASS
- Increase β gradually: 0.001, 0.005, 0.01, 0.02, 0.03
- Plot χ² vs β
- Find: What's the maximum β that keeps χ² < 2800?

**Success Criteria**:
- ✅ β = 0 matches AxiCLASS (χ² ≈ 2760-2770)
- ✅ Small β (e.g., 0.001) doesn't break the CMB (χ² < 2800)
- ✅ We understand the β threshold where CMB breaks

### Modification 2: Adjust Potential Shape

**What**: Modify the potential V(φ) to allow different behaviors.

**Options**:
1. Keep axion potential: V(φ) = Λ⁴[1 - cos(φ/f)]
2. Add polynomial term: V(φ) = Λ⁴[1 - cos(φ/f)] + λφⁿ
3. Use different n_axion values (n = 1, 2, 4, 5)

**Test**:
- For each potential, run single-point χ² test
- Plot χ² vs potential parameters
- Find: Which potential gives best CMB fit?

**Success Criteria**:
- ✅ At least one potential variant gives χ² < 2800
- ✅ We understand how potential shape affects CMB

### Modification 3: Optimize Initial Conditions

**What**: Find the optimal θᵢ (initial field value) for our potential.

**How**:
- Grid scan: θᵢ ∈ [0.5, 3.5], step = 0.1
- For each θᵢ, compute:
  - f_EDE(z=3000) - Early dark energy fraction
  - χ² - CMB fit quality
  - H₀ - Hubble constant (Planck-only)

**Test**:
- Plot f_EDE vs θᵢ
- Plot χ² vs θᵢ
- Find: Which θᵢ gives f_EDE ≈ 10% AND χ² < 2800?

**Success Criteria**:
- ✅ We find a θᵢ range that works
- ✅ f_EDE is in the correct range (5-15%)
- ✅ χ² is acceptable (< 2800)

### Files Created
- `phase3/v2_grid_scan.py` - Parameter space exploration
- `phase3/v2_grid_scan_results.csv` - Grid scan data
- `phase3/v2_grid_scan_plots/` - Heatmaps and evolution plots
- `phase3/V2_MODIFICATIONS.md` - Summary of each modification

---

## Phase 4: MCMC Testing (Validation) 🔴 NOT STARTED

**Goal**: Run MCMC with the working V2 model and verify it performs well

**Status**: 🔴 **NOT STARTED**

### Test 1: Planck-Only (Tier 1)

**Config**:
- Likelihood: Planck 2018 (low-ℓ + high-ℓ + lensing)
- Priors: θᵢ ∈ [θ_min, θ_max] (from Phase 3 grid scan)
- Priors: β ∈ [0.0, β_max] (from Phase 3 coupling test)

**Success Criteria**:
- ✅ χ² ≈ 2760-2780 (comparable to ΛCDM)
- ✅ θᵢ stays in the allowed range (doesn't collapse)
- ✅ Chains converge (R-1 < 0.01)

### Test 2: Planck + BAO (Tier 2)

**Config**:
- Add BAO likelihoods
- Same priors as Test 1

**Success Criteria**:
- ✅ χ² increases by ~10-20 (BAO contribution)
- ✅ H₀ stays Planck-like (~68-69) for Planck+BAO only
- ✅ Model doesn't break with additional data

### Test 3: Planck + BAO + SH0ES (Tier 3)

**Config**:
- Add SH0ES external likelihood
- Same priors as Test 1

**Success Criteria**:
- ✅ H₀ increases toward 72-73 km/s/Mpc
- ✅ χ² penalty from SH0ES is balanced by improved H₀
- ✅ Δχ² (Ridder - ΛCDM) < 10 (model is competitive)

### Test 4: Full Dataset (Tier 4)

**Config**:
- Add Pantheon SN
- Optionally add DES Y1 (if we can get it working)

**Success Criteria**:
- ✅ Model fits all data simultaneously
- ✅ H₀ ≈ 72-73 km/s/Mpc (tension relief)
- ✅ Δχ² (Ridder - ΛCDM) < 5 (model is better)

### Files Created
- `phase3/configs/v2_tier1_validated.yaml` - V2 Tier 1 config
- `phase3/configs/v2_tier2_validated.yaml` - V2 Tier 2 config
- `phase3/configs/v2_tier3_validated.yaml` - V2 Tier 3 config
- `phase3/configs/v2_tier4_validated.yaml` - V2 Tier 4 config

---

## Key Differences from V1

| Aspect | V1 (Failed) | V2 (Planned) |
|--------|-------------|--------------|
| **Starting Point** | Novel implementation from scratch | Copy proven AxiCLASS |
| **Validation** | None - went straight to MCMC | Reproduce AxiCLASS results first |
| **Testing** | Only MCMC | Single-point tests, grid scans, then MCMC |
| **Coupling** | Added from the start (β ≠ 0) | Start with β = 0, add gradually |
| **Initial Conditions** | Guessed θᵢ ≈ 2.1 | Grid scan to find optimal θᵢ |
| **Failure Mode** | Discovered after 50,000 samples | Catch failures in single-point tests |

---

## Diagnostic Tools (Build These First)

### Tool 1: Single-Point χ² Calculator ⏳ IN PROGRESS

```python
def test_single_point(theta_i, beta, potential_params):
    """
    Run CLASS with given parameters and compute χ² with Planck.
    Returns: chi2, C_l_TT, C_l_TE, C_l_EE
    """
    # ... implementation ...
```

**Status**: 🟡 Creating now

### Tool 2: Parameter Grid Scanner 🔴 NOT STARTED

```python
def grid_scan(theta_i_range, beta_range):
    """
    Scan parameter space and plot χ² heatmap.
    Returns: DataFrame with (theta_i, beta, chi2, f_EDE, H0)
    """
    # ... implementation ...
```

**Status**: 🔴 Waiting for Phase 3

### Tool 3: Power Spectrum Comparator 🔴 NOT STARTED

```python
def compare_power_spectra(model1, model2):
    """
    Compare C_ℓ from two models (e.g., V2 vs AxiCLASS).
    Returns: Plots and residuals
    """
    # ... implementation ...
```

**Status**: 🔴 Waiting for Phase 2

### Tool 4: f_EDE Evolution Plotter 🔴 NOT STARTED

```python
def plot_f_EDE_evolution(theta_i, beta):
    """
    Plot f_EDE(z) from z=10000 to z=0.
    Verify: Does f_EDE peak at z ≈ 3000 with f_EDE ≈ 10%?
    """
    # ... implementation ...
```

**Status**: 🔴 Waiting for Phase 3

---

## Timeline (Estimated)

| Phase | Duration | Deliverable | Status |
|-------|----------|-------------|--------|
| **Phase 0** | 30 min - 1 hour | Quick validation of current V2 | 🟡 **IN PROGRESS** |
| **Phase 1** | 1-2 days | AxiCLASS running and validated | 🔴 Not started |
| **Phase 2** | 2-3 days | Our CLASS fork reproduces AxiCLASS | 🔴 Not started |
| **Phase 3** | 3-5 days | Ridder modifications tested and working | 🔴 Not started |
| **Phase 4** | 5-7 days | Full MCMC runs (Tier 1-4) | 🔴 Not started |
| **Total** | **11-17 days** | V2 model ready for publication | |

---

## Success Metrics

### Minimum Viable V2 (Must Achieve):
- ✅ χ² < 2800 for Planck-only (comparable to ΛCDM)
- ✅ H₀ ≈ 72-73 km/s/Mpc with SH0ES (tension relief)
- ✅ Δχ² (Ridder - ΛCDM) < 10 for full dataset

### Stretch Goals (Nice to Have):
- ✅ Δχ² (Ridder - ΛCDM) < 0 (model is better than ΛCDM)
- ✅ Bayesian evidence favors Ridder over ΛCDM
- ✅ Model also improves S₈ tension (via β coupling)

---

## Red Flags (Stop and Debug If You See):

🚨 **Phase 0**:
- Single-point test crashes
- χ² > 2800 with current V2 parameters
- Δχ² > 10 (V2 breaks CMB)

🚨 **Phase 1**:
- AxiCLASS doesn't reproduce published results
- χ² > 2800 with their default parameters

🚨 **Phase 2**:
- Our CLASS fork doesn't match AxiCLASS output
- Power spectra differ by >1%

🚨 **Phase 3**:
- ANY β > 0 causes χ² > 2800
- NO θᵢ value gives f_EDE ≈ 10% with χ² < 2800

🚨 **Phase 4**:
- θᵢ collapses to low values (< 1.0)
- χ² > 2800 in MCMC
- Chains don't converge (R-1 > 0.05)

**If any red flag appears, STOP and debug before proceeding.**

---

## Current Status Summary

**Date**: November 23, 2025  
**Phase**: Phase 0 (Quick Validation)  
**Next Action**: Create single-point χ² calculator  
**Blockers**: None  
**ETA to Phase 1**: 30 minutes - 1 hour

---

## Change Log

| Date | Phase | Action | Result |
|------|-------|--------|--------|
| 2025-11-23 | Phase 0 | Created incremental plan document | ✅ Plan documented |
| 2025-11-23 | Phase 0 | Starting single-point χ² calculator | 🟡 In progress |

---

## The Bottom Line

**V2 will succeed where V1 failed because we're following a proven path:**

1. Start with a working model (AxiCLASS)
2. Validate every step before moving forward
3. Test modifications independently
4. Only run expensive MCMC after passing all diagnostic tests

**Do NOT skip steps.** Each phase builds on the previous one. If Phase 1 fails, Phase 4 will definitely fail.

**Be patient.** This will take 2-3 weeks, but it's better than wasting months on a broken model.

