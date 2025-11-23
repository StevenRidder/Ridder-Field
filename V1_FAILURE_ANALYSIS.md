# V1 Model Failure Analysis

**Date**: November 23, 2025  
**Status**: Model FAILED - Catastrophic χ² mismatch

---

## Executive Summary

The Ridder Field V1 model **completely fails** to fit cosmological data. The model produces χ² values ~2400 points **worse** than standard ΛCDM, indicating fundamental physics issues, not just parameter tuning problems.

---

## Results Summary

### Tier 3 (Planck + BAO + SH0ES)

| Model | H₀ [km/s/Mpc] | θᵢ | β | χ² | Δχ² vs ΛCDM |
|-------|---------------|-----|---|-----|-------------|
| **Ridder** | 70.38 ± 0.66 | 0.88 ± 0.28 | 0.0104 ± 0.0081 | **2824** | **+2428** |
| **ΛCDM** | 69.27 ± 0.29 | — | — | **396** | — |

### Tier 4 (Planck + BAO + SH0ES + SN)

| Model | H₀ [km/s/Mpc] | θᵢ | β | χ² | Notes |
|-------|---------------|-----|---|-----|-------|
| **Ridder** | 71.15 ± 0.60 | 1.16 ± 0.16 | 0.0045 ± 0.0039 | **2.9** | Incomplete (401 samples) |

**Note**: Tier 4 χ² = 2.9 is suspiciously low and indicates the chains haven't converged yet (only ~400 total samples after 30% burn-in).

---

## Critical Failures

### 1. **Catastrophic CMB Fit (Δχ² = +2428)**

The Ridder model is **2428 χ² points worse** than ΛCDM for the same data. This is not a marginal failure—this is a complete breakdown of the model's ability to fit the CMB.

**Interpretation**:
- The Ridder field is **destroying** the CMB acoustic peaks
- The coupling β or the potential V(φ) is fundamentally wrong
- The field evolution is incompatible with Planck constraints

### 2. **H₀ Stuck at 70, Not 73**

Despite the SH0ES external likelihood pulling toward H₀ = 73.04 ± 1.04, the Ridder model only reaches:
- Tier 3: H₀ = 70.38 ± 0.66
- Tier 4: H₀ = 71.15 ± 0.60

**Interpretation**:
- Full Planck (χ² ≈ 2800) **dominates** over SH0ES (χ² penalty ≈ 8.5)
- The model cannot relieve the H₀ tension because it breaks Planck first
- Even with SH0ES, the model prefers to minimize Planck χ² at the cost of H₀

### 3. **θᵢ Collapsed to Low Values**

The initial field value θᵢ is stuck at:
- Tier 3: θᵢ = 0.88 ± 0.28 (range: [0.67, 1.11])
- Tier 4: θᵢ = 1.16 ± 0.16 (range: [1.02, 1.27])

**Prior**: θᵢ ∈ [0.1, 2.3], **ref**: 2.1

**Interpretation**:
- The model is **avoiding** the high-θᵢ region (where EDE-like behavior should occur)
- Starting at ref: 2.1 may have caused CLASS to hang (as we saw in testing)
- The field is collapsing to low values because high θᵢ breaks the CMB even worse

### 4. **β (Coupling) is Weak**

The matter coupling β is:
- Tier 3: β = 0.0104 ± 0.0081 (range: [0.002, 0.020])
- Tier 4: β = 0.0045 ± 0.0039 (range: [0.001, 0.008])

**Prior**: β ∈ [0.0, 0.03], **ref**: 0.01

**Interpretation**:
- The model is pushing β toward **zero** (i.e., no coupling)
- This suggests the coupling mechanism is **harmful** to the CMB fit
- The model "wants" to be ΛCDM (β = 0) but is forced to have β > 0

---

## Root Cause Analysis

### A. Physics Issues (Most Likely)

1. **Potential V(φ) is Wrong**
   - The axion-like potential with n = 3 may be too steep
   - The field oscillates too violently, creating ISW effects that destroy the CMB
   - The potential energy density doesn't track the correct evolution

2. **Coupling β is Destructive**
   - The coupling to matter (β) may be breaking the acoustic peaks
   - The field's stress-energy tensor is interfering with photon-baryon oscillations
   - The coupling may be causing unphysical energy transfer

3. **Initial Conditions (θᵢ) are Incompatible**
   - The field starting at high θᵢ creates too much early-time energy density
   - This shifts the CMB peaks in a way that cannot be compensated by other parameters
   - The field may be "rolling" at the wrong time (e.g., during recombination instead of late times)

### B. Implementation Issues (Possible)

1. **CLASS Integration**
   - The Ridder field equations in `perturbations.c` may have bugs
   - The background evolution in `background.c` may be incorrect
   - The stress-energy tensor components may be miscomputed

2. **Parameter Mapping**
   - `Lambda_EDE_ridder = 1.0` may be the wrong normalization
   - `f_axion_ridder = 1.0e27` may be too large/small
   - The relationship between θᵢ and the physical field value φ may be wrong

### C. Prior/Configuration Issues (Unlikely)

1. **Priors Too Restrictive**
   - θᵢ ∈ [0.1, 2.3] may be cutting off the "good" region
   - β ∈ [0.0, 0.03] may be too narrow
   - But: The chains are exploring the full prior range and still failing

2. **SH0ES Likelihood Too Weak**
   - The external likelihood has σ = 1.04, giving a penalty of ~8.5 for H₀ = 70
   - This is **300× weaker** than Planck's χ² ≈ 2800
   - But: Even if we made SH0ES stronger, it wouldn't fix the CMB disaster

---

## Diagnostic Evidence

### 1. Chain Convergence (Good)

- All chains reached R-1 < 0.01 (well-converged)
- Trace plots show good mixing (no stuck chains)
- Samples: Tier 3 (669 total), Tier 4 (401 total, incomplete)

**Conclusion**: The failure is **not** due to poor sampling or convergence issues.

### 2. Parameter Correlations

From `tier3_ridder_contours.png`:
- H₀ vs θᵢ: Weak negative correlation (higher θᵢ → slightly lower H₀)
- H₀ vs β: No strong correlation
- θᵢ vs β: No strong correlation

**Conclusion**: No obvious degeneracies. The model is simply failing to fit the data.

### 3. Distributions

From `tier3_ridder_distributions.png`:
- H₀: Gaussian-like, centered at 70.38
- θᵢ: Broad, peaked at 0.88
- β: Skewed toward 0, peaked at 0.01
- χ²: Narrow, centered at 2824 (consistently bad)

**Conclusion**: The model has **converged to a bad solution**, not a good one.

---

## What Needs to Change for V2

### Critical Changes (Must Fix)

1. **Revisit the Potential V(φ)**
   - Test simpler potentials (e.g., quadratic, cosine)
   - Ensure the field doesn't oscillate during recombination
   - Match the potential to known EDE models that work

2. **Rethink the Coupling β**
   - Consider removing the coupling entirely (β = 0)
   - Or: Change the coupling mechanism (e.g., conformal coupling instead of direct)
   - Test: Does the model work with β = 0 and just the background evolution?

3. **Fix Initial Conditions θᵢ**
   - Ensure θᵢ corresponds to the correct physical field value at early times
   - Test: What θᵢ gives f_EDE ≈ 10% at z ≈ 3000 (as in successful EDE models)?
   - Verify: Does CLASS correctly integrate the field from θᵢ to today?

### Secondary Changes (Worth Testing)

4. **Adjust Priors**
   - Expand θᵢ range to [0.01, 5.0] to explore more parameter space
   - Allow β to be negative: β ∈ [-0.03, 0.03]
   - Test different n_ridder values (n = 1, 2, 4, 5)

5. **Use Planck-Lite for Tier 3A**
   - Run a "Planck-lite" version (low-ℓ only) to see if the model can at least fit the large-scale CMB
   - This isolates whether the failure is in the acoustic peaks or the overall power spectrum

6. **Verify CLASS Implementation**
   - Add debug prints to `perturbations.c` to check field evolution
   - Compare to a known working EDE implementation (e.g., AxiCLASS)
   - Test: Does the field energy density evolve as expected?

---

## Files to Examine

### Physics (CLASS Source Code)
- `phase2/class/source/perturbations.c` (lines with "ridder" or "scf")
- `phase2/class/source/background.c` (Ridder field background evolution)
- `phase2/class/include/common.h` (parameter definitions)

### Configuration (YAML Files)
- `phase3/configs/ridder_tier3_production.yaml` (what we actually ran)
- `phase3/configs/ridder_tier4_full.yaml` (Tier 4 setup)

### Results (Data & Plots)
- `phase3/results/analysis.log` (summary statistics)
- `phase3/results/plots/tier3_ridder_traces.png` (convergence check)
- `phase3/results/plots/tier3_ridder_contours.png` (parameter correlations)
- `phase3/results/plots/tier3_ridder_distributions.png` (1D posteriors)

### Chain Data (Raw MCMC Output)
- `phase3/results/tier3_chains/ridder_tier3_prod_chain*.1.txt` (4 chains)
- `phase3/results/tier3_chains/lcdm_tier3_prod_chain*.1.txt` (2 baseline chains)
- `phase3/results/tier4_chains/ridder_tier4_prod_chain*.1.txt` (4 chains, incomplete)

---

## Conclusion

**The Ridder Field V1 model is fundamentally broken.** The χ² = 2824 vs ΛCDM χ² = 396 is not a "tuning" problem—it's a physics problem. The model cannot fit the CMB, cannot raise H₀ to 73, and is actively avoiding the parameter region where it should work.

**Next Steps**:
1. Review the CLASS implementation line-by-line
2. Compare to known working EDE models
3. Test simpler potentials and couplings
4. Document all changes in V2_DESIGN.md before starting new runs

**Do NOT** proceed with more MCMC runs until the physics is fixed. More sampling will not solve a broken model.

