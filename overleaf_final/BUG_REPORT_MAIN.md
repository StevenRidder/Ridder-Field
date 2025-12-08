# Bug Report: main.tex (Paper 1)

## Critical Issues

### 1. **sigma_ln_a Parameter Inconsistency**

**Location**: 
- Line 497: Table says `σ_ln a = 0.5`
- Line 1817: Table says `σ_ln a = 0.8`
- Line 1857: Robustness test uses `σ_ln a ∈ [0.6, 1.0]`

**Problem**: The paper gives two different values for the fixed parameter `σ_ln a`:
- Table 1 (line 497): 0.5
- Table in Appendix (line 1817): 0.8
- The robustness test (line 1857) suggests values in [0.6, 1.0]

**Impact**: 
- Unclear which value was actually used in the chains
- Could affect reproducibility
- The robustness test uses 0.8 as benchmark, suggesting that's the actual value

**Fix Required**:
- Determine which value was actually used in production chains
- Update all tables to be consistent
- If 0.8 is correct, update line 497

---

### 2. **A_sh Value Discrepancy Between Papers**

**Location**: 
- main.tex line 1093: `A_sh = 1.16 ± 0.18` (6.4σ conditional)
- paper2_soft_shoulder.tex line 335: `A_sh = 1.72 ± 0.22` (7.8σ marginalized)

**Problem**: The two papers report different values for the same quantity:
- Paper 1 (main.tex): 1.16 ± 0.18 (conditional, 6.4σ)
- Paper 2 (paper2_soft_shoulder.tex): 1.72 ± 0.22 (marginalized, 7.8σ)

**Possible Explanations**:
1. Different analysis methods (conditional vs marginalized)
2. Different datasets (ACT-only vs ACT+Planck+BAO)
3. Different template definitions
4. Different chain results

**Impact**: 
- Confusing for readers comparing the two papers
- Need to clarify the relationship between these values

**Fix Required**:
- Add explicit note explaining the difference
- Clarify that Paper 1 is conditional, Paper 2 is marginalized
- Document which analysis corresponds to which paper

---

### 3. **Lambda_EDE Prior Range Inconsistency**

**Location**: 
- Line 533: `Λ_EDE [eV]` prior range `[0, 5.0]`
- Line 1814: `Λ_EDE [eV]` prior range `[10^{-28}, 10^{-26}]` (log-flat)

**Problem**: Two completely different prior specifications:
- Table 3 (line 533): Flat prior [0, 5.0] eV
- Appendix table (line 1814): Log-flat prior [10^{-28}, 10^{-26}] eV

**Impact**: 
- These are orders of magnitude different!
- 10^{-28} eV is essentially zero
- 5.0 eV is a very large energy scale
- Unclear which was actually used

**Fix Required**:
- Determine which prior was used in actual chains
- Update both tables to match
- If log-flat is correct, the range [10^{-28}, 10^{-26}] seems too narrow and too small

---

### 4. **Chi-squared Values Need Verification**

**Location**: Multiple locations with Δχ² values:
- Line 21: `Δχ² ≃ -4.5` (pre-DESI)
- Line 65: `Δχ² = -3.3` (CPL)
- Line 94: `Δχ² ≈ +2` at H₀=69, `+11` at H₀=70, `≳ 90` at H₀=72
- Line 108: `Δχ² ≈ +19` (Planck high-ℓ), `-18` (low-ℓ), `-3.5` (SH0ES)
- Line 110: `Δχ² ≈ +11` (with DESI)

**Issue**: Need to verify these match actual chain outputs

**Check Needed**:
- Verify all Δχ² values come from actual chain analysis
- Ensure consistency between different sections
- Check that sums add up correctly (e.g., +19 - 18 - 3.5 = -2.5, not -4.5)

---

### 5. **H₀ Profile Likelihood Values**

**Location**: 
- Line 94: `Δχ² ≈ +2` at H₀=69, `+11` at H₀=70, `≳ 90` at H₀=72
- Line 897-898: Table shows H₀=71.0 → Δχ²=+33.7, H₀=72.0 → Δχ²=+91.0
- Line 1005-1007: Text says H₀=71.0 → +34, H₀=72.0 → +91

**Issue**: 
- Line 94 says "≳ 90" at H₀=72, but table shows exactly 91.0
- Need to verify these match actual profile likelihood chains

**Fix Required**:
- Verify all profile likelihood values match chain outputs
- Update line 94 to match table values if needed

---

### 6. **A_sh Significance Calculation**

**Location**: Line 1093-1095

**Reported**: `A_sh = 1.16 ± 0.18` with "≈ 6σ" significance

**Calculation**: `1.16 / 0.18 = 6.44σ` ✓ Correct

**However**: The paper says this is "conditional" - need to clarify:
- Conditional on what exactly?
- What would the marginalized significance be?
- Line 112 says "fully marginalized analysis may reduce this significance to 3--5σ"

**Fix Required**:
- Clarify what "conditional" means in this context
- Document what parameters are held fixed
- If possible, provide marginalized result for comparison

---

### 7. **Template Definition Consistency**

**Location**: 
- Line 1063-1067: Template defined as `ΔC_ℓ^sh = C_ℓ^R(θ_R) - C_ℓ^ΛCDM(θ_Λ)`
- Line 1081: Says `A_sh=1` corresponds to "full EDE shoulder predicted by the Planck+BAO+SH0ES best fit"

**Issue**: 
- Template is defined from Planck+BAO+SH0ES best-fit
- But analysis may use different data combinations
- Need to verify template is computed consistently

**Fix Required**:
- Document exactly which best-fit was used to compute template
- Ensure template computation matches the analysis context
- Verify template normalization is consistent

---

### 8. **Parameter Count Inconsistency**

**Location**: 
- Line 454: EDE (Minimal) has k=8 with fixed `n_φ, σ_ln a, θ_i, β`
- Line 455: EDE (Extended) has k=9 with `σ_ln a` now free
- Line 497: Says `σ_ln a = 0.5` (fixed)
- Line 1817: Says `σ_ln a = 0.8` (fixed)

**Issue**: 
- If σ_ln a is fixed at 0.5 in minimal, but robustness test uses 0.8 as benchmark, which is correct?
- Extended model (k=9) floats σ_ln a, but what are its bounds?

**Fix Required**:
- Clarify which value of σ_ln a was used in minimal model
- Document prior range for σ_ln a in extended model
- Ensure consistency across all mentions

---

### 9. **Null Test Results**

**Location**: Lines 1128-1144, Table 4

**Reported Values**:
- Signal: `A_sh = 1.16 ± 0.18` (6.4σ)
- Null 1 (phase-scrambled): `0.02 ± 0.19` (0.1σ)
- Null 2 (Planck residuals): `0.15 ± 0.25` (0.6σ)
- Null 3 (wrong z_c): `0.08 ± 0.20` (0.4σ)

**Issue**: 
- Need to verify these come from actual analysis
- Phase scrambling procedure needs documentation
- "Wrong z_c" test needs specification of what z_c was used

**Fix Required**:
- Document how each null test was performed
- Verify results match actual code outputs
- Specify what "wrong z_c" means (factor of 2? different value?)

---

### 10. **Delta Chi-squared Formula**

**Location**: Line 1156-1161

**Formula**: `Δχ²_ACT = χ²_ΛCDM,min - χ²_EDE,min`

**Issue**: 
- This defines Δχ² > 0 as EDE preference
- But elsewhere in paper, negative Δχ² means improvement
- Need consistency in sign convention

**Verdict**: This is **CORRECT** for this specific definition (ACT-only comparison), but the sign convention should be clearly stated.

**Fix Required**:
- Add explicit note about sign convention
- Ensure all Δχ² definitions are consistent throughout paper

---

### 11. **Tier-5 EDE Configuration**

**Location**: Lines 1153-1154

**Mentions**: "Tier-5 EDE configuration" with `Λ_EDE=0.79 eV` and "narrow shelf near z ~ 3500"

**Issue**: 
- What is "Tier-5"? Not defined in main.tex
- Is this the same as the "minimal EDE" model?
- Need to clarify relationship between different model configurations

**Fix Required**:
- Define what "Tier-5" means
- Clarify relationship to "minimal EDE" (k=8) model
- Document all model configurations used

---

### 12. **CMB-S4 Forecast**

**Location**: Lines 1171-1185

**Mentions**: `σ(A_sh) ~ 0.1` for CMB-S4

**Issue**: 
- Need to verify this forecast is correct
- Should cite the forecast methodology
- The "exclusion" criterion (A_sh = 0.0 ± 0.1) at >5σ needs calculation verification

**Fix Required**:
- Verify forecast calculation
- Add citation for CMB-S4 specifications
- Document forecast methodology

---

## Medium Priority Issues

### 13. **TRGB H₀ Value Inconsistency**

**Location**: 
- Line 36: `H₀ = 70.4 ± 1.2` km/s/Mpc (Freedman 2024)
- Line 318: `H₀ = 69.8 ± 1.7` km/s/Mpc (TRGB-CCHP)

**Issue**: Two different TRGB values cited
- First is from Freedman 2024
- Second is from TRGB-CCHP (also Freedman?)

**Fix Required**:
- Clarify if these are different measurements or same measurement
- Use consistent value throughout, or explain the difference

---

### 14. **Correlation Flip Values**

**Location**: Line 121

**Mentions**: Correlation between `Λ_EDE` and `τ` changes from `+0.73` (pre-DESI) to `-0.24` (with DESI)

**Issue**: 
- Need to verify these correlation values from actual chains
- Should show correlation matrices or provide evidence

**Fix Required**:
- Verify correlation values from chain analysis
- Consider adding correlation matrix figure or table

---

### 15. **Profile Likelihood Methodology**

**Location**: Lines 1148-1167

**Describes**: Profile likelihood analysis of ACT DR6

**Issue**: 
- Methodology is described but some details are unclear
- What exactly is "Tier-5 EDE configuration"?
- How are ACT nuisance parameters handled?

**Fix Required**:
- Clarify all methodological details
- Document exact procedure used
- Ensure reproducibility

---

## Low Priority Issues

### 16. **Table Formatting**

**Location**: Multiple tables

**Issue**: Some tables could be clearer:
- Table 3 (line 515): Very wide, could be split
- Table 4 (line 1134): Could add more context

**Fix Required**: Minor formatting improvements

---

### 17. **Citation Consistency**

**Location**: Throughout

**Issue**: 
- Some citations may be missing
- Need to verify all claims are properly cited

**Fix Required**: Review all citations

---

## Summary of Severity

- **CRITICAL**: 
  - sigma_ln_a inconsistency (#1)
  - Lambda_EDE prior range mismatch (#3)
  - A_sh discrepancy between papers (#2)
- **HIGH**: 
  - Chi-squared values verification (#4)
  - H₀ profile likelihood values (#5)
  - Parameter count consistency (#8)
- **MEDIUM**: 
  - A_sh significance clarification (#6)
  - Template definition (#7)
  - Null test documentation (#9)
  - TRGB value consistency (#13)
- **LOW**: 
  - Table formatting (#16)
  - Citation review (#17)

The sigma_ln_a and Lambda_EDE prior inconsistencies are the most serious and should be fixed immediately, as they affect reproducibility and could invalidate results if the wrong values were used.

