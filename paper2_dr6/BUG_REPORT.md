# Bug Report: Paper 2 Analysis

## Critical Issues

### 1. **CRITICAL: theta_i Parameter Mismatch**

**Location**: 
- Paper: `paper2_soft_shoulder.tex` line 267 states `theta_i = 2.0`
- Config: `prod_p2_dr6_ede.yaml` line 17 uses `theta_i_ridder: 1.0`
- Test scripts: `shifted_template_test.py` and `wrong_template_v3.py` use `theta_i = 2.0`

**Problem**: The paper claims the model uses `theta_i = 2.0`, but the actual production chains use `theta_i = 1.0`. This is a fundamental parameter mismatch that could invalidate the results.

**Impact**: 
- The template shape computed in test scripts (using theta_i=2.0) may not match the actual EDE model used in chains (theta_i=1.0)
- The paper's description of the model does not match what was actually run
- All template fits may be using the wrong template shape

**Fix Required**:
- Either update the paper to say `theta_i = 1.0` (if that's what was actually used)
- Or re-run chains with `theta_i = 2.0` (if that's what the paper should describe)
- Ensure all template computations use the same theta_i value as the chains

---

### 2. **Chi-squared Improvement Formula Sign**

**Location**: 
- `shifted_template_test.py` line 88: `dchi2 = -A * A * den`
- `wrong_template_v3.py` line 89: `return n / d, np.sqrt(1 / d), -(n / d) ** 2 * d`

**Problem**: The chi-squared improvement formula uses a negative sign. Let's verify:
- If `A > 0` and `den > 0`, then `dchi2 = -A^2 * den < 0` (improvement)
- The formula for chi-squared improvement when fitting `r = A*t + noise` is:
  - `Δχ² = χ²(A=0) - χ²(A=A_hat) = (r^T C^-1 r) - ((r - A_hat*t)^T C^-1 (r - A_hat*t))`
  - Expanding: `= A_hat^2 * (t^T C^-1 t) - 2*A_hat*(t^T C^-1 r)`
  - At best-fit: `A_hat = (t^T C^-1 r) / (t^T C^-1 t)`
  - So: `Δχ² = A_hat^2 * den - 2*A_hat^2 * den = -A_hat^2 * den`

**Verdict**: The formula appears **CORRECT** - negative means improvement.

**However**: Need to verify that the paper's reported `Δχ² = -1,940` matches this calculation.

---

### 3. **Template Computation Inconsistency**

**Location**: 
- `shifted_template_test.py` lines 120-122 compute EDE bandpowers with `theta_i = 2.0`
- But chains use `theta_i = 1.0` (from config)

**Problem**: The template `t0 = Cl_EDE - Cl_LCDM` is computed using a different theta_i than the actual chains. This means:
- The "correct" template in the null test may not actually match the best-fit EDE model
- The 27.7σ detection quoted in the paper (line 589) may be inflated because the template doesn't match

**Fix Required**:
- Ensure template computation uses the same parameters as the best-fit chain
- Load theta_i from the chain best-fit, don't hardcode it

---

### 4. **Significance Calculation Verification**

**Location**: Paper line 335: `A_sh = 1.72 ± 0.22 (7.8σ)`

**Calculation**: `1.72 / 0.22 = 7.82σ` ✓ This is correct.

**However**: Need to verify:
- Is this the marginalized posterior width, or conditional?
- The paper says "fully marginalized" but the uncertainty seems small for a marginalized result
- Check if the 0.22 includes all parameter correlations

---

### 5. **Chi-squared Decomposition Numbers**

**Location**: Paper lines 340-354, Table showing:
- ACT DR6: 9,020 → 6,903 (Δχ² = -2,117)
- Total: 10,893 → 8,757 (Δχ² = -2,136)

**Issue**: The sum of components doesn't match:
- ACT: -2,117
- Planck low-ℓ: -2
- Lensing: -20
- BAO: +4
- Pantheon+: -1
- Sum: -2,136 ✓ (matches total)

**Verdict**: Math checks out, but need to verify these numbers come from actual chain analysis, not theoretical estimates.

---

### 6. **Phase Scrambling Implementation**

**Location**: `run_act_null_tests.py` lines 102-118

**Code Review**:
```python
def scramble_phase(template_tt, template_ee, ell):
    tt_fft = np.fft.fft(template_tt)
    ee_fft = np.fft.fft(template_ee)
    random_phase = np.exp(2j * np.pi * np.random.random(len(template_tt)))
    tt_scrambled = np.real(np.fft.ifft(np.abs(tt_fft) * random_phase))
```

**Potential Issues**:
1. Uses same random phase for TT and EE - should they be independent?
2. FFT on bandpowers may not preserve the correct phase structure (bandpowers are already integrated)
3. The paper says "scramble the phases of the ACT power spectra" (line 553) - does this mean scramble the data or the template?

**Clarification Needed**: 
- What exactly is being scrambled? The ACT data or the template?
- If scrambling the template, does this preserve the covariance structure?

---

### 7. **Wrong Template Test - Lambda Values**

**Location**: `wrong_template_v3.py` line 124

**Issue**: Tests lambda values `[0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.16, 0.18]` but:
- The best-fit lambda from chain is `lam0 = pe.get('Lambda_EDE_ridder', 0.11)` (line 95)
- The test skips values within 0.015 of lam0 (line 125-126)
- But 0.10 and 0.12 are both within 0.015 of 0.11, so they get skipped
- This means the test doesn't check nearby wrong values

**Fix**: Either:
- Test more lambda values closer to the best-fit
- Or adjust the skip threshold
- Or explicitly test lam0 ± 0.02, ±0.05, etc.

---

### 8. **Template Normalization**

**Location**: Template is computed as `t0 = Cl_EDE - Cl_LCDM` (difference in bandpowers)

**Potential Issue**: 
- Is the template properly normalized?
- The amplitude A_sh = 1.72 means the template is scaled by 1.72
- But if the template itself has an arbitrary normalization, this could be misleading
- Should verify: what does A_sh = 1.0 mean? Does it mean "full EDE effect" or something else?

**Check**: 
- What is the physical interpretation of A_sh = 1.0?
- Does A_sh = 1.0 correspond to the best-fit EDE model, or something else?

---

### 9. **C Code Potential Issues**

**Location**: `ridder_unified_potential.c`

**Issues Found**:

1. **Line 166-169**: V_scale calculation uses a hardcoded normalization `1e50`:
   ```c
   V_scale = m2f2 / 1e50;  /* Normalize to cosmological scale */
   ```
   This seems arbitrary - what is the physical justification?

2. **Line 232-233**: Comment says "Full implementation left as TODO":
   ```c
   /* Full implementation left as TODO for numerical stability */
   ```
   The second derivative is incomplete - this could affect numerical accuracy.

3. **Line 341**: `d2V_plateau_dtheta2` returns 0.0 as placeholder - this is used in the code but may not be correct.

4. **Debug prints**: Lines 148-152 and 362-367 have debug print statements that should be removed or made conditional.

---

### 10. **Config File Issues**

**Location**: `prod_p2_dr6_ede.yaml`

**Issues**:

1. **Line 17**: `theta_i_ridder: 1.0` - hardcoded, but paper says 2.0
2. **Line 19**: `f_axion_ridder: 1.0e+27` - very large number, is this correct?
3. **Line 11**: `l_max_scalars: 2508` - is this sufficient for ACT DR6 which goes to ℓ ~ 4000?

---

## Recommendations

### Immediate Actions:

1. **Fix theta_i mismatch** - This is the most critical issue. Decide which value is correct and update everything consistently.

2. **Verify template computation** - Ensure templates are computed using the exact same parameters as the best-fit chain, loaded from the chain file.

3. **Check chi-squared numbers** - Verify the reported Δχ² values come from actual chain analysis, not theoretical calculations.

4. **Clarify phase scrambling** - Document exactly what is being scrambled and why.

5. **Complete C code** - Finish the second derivative implementations or document why they're not needed.

### Testing Needed:

1. Re-run template fit with theta_i=1.0 to match chains
2. Re-run template fit with theta_i=2.0 to match paper
3. Compare results to see if the mismatch affects conclusions
4. Verify all chi-squared decompositions match chain outputs
5. Test phase scrambling on actual ACT data (not just templates)

### Documentation Needed:

1. Document what A_sh = 1.0 means physically
2. Document template normalization convention
3. Document which parameters were actually used in chains vs. paper description
4. Document phase scrambling procedure in detail

---

## Additional Critical Findings

### 11. **A_sh Value Discrepancy**

**Location**: 
- Paper: `A_sh = 1.72 ± 0.22 (7.8σ)` (line 335)
- Chain analysis: `CHAIN_RESULTS_SUMMARY.md` line 13 mentions `A_sh = 2.65 ± 0.19 (13.7σ)`

**Problem**: There's a significant discrepancy between:
- The paper's reported value: 1.72 ± 0.22
- A chain result mentioned in documentation: 2.65 ± 0.19

**Possible Explanations**:
1. Different analysis methods (marginalized vs conditional)
2. Different datasets (ACT-only vs ACT+Planck+BAO)
3. Different template definitions
4. One is from an old analysis, one is current

**Fix Required**:
- Verify which value is correct for the paper
- Document which analysis produced which number
- Ensure consistency between paper and supporting documentation

---

### 12. **Significance Value Inconsistencies**

**Location**: Paper mentions multiple significance values:
- Line 335: 7.8σ (for A_sh = 1.72 ± 0.22) - marginalized
- Line 589: 27.7σ (for unshifted template in shifted-template test) - conditional
- Line 563: 13.4σ (for phase-coherence test)

**Issue**: These are different tests, but the paper should clarify:
- 7.8σ is the marginalized posterior significance (all params float)
- 27.7σ is the conditional fit significance (template fixed, no other params)
- 13.4σ is the phase-coherence test significance (comparing to scrambled)

**Verdict**: This is likely correct but needs clearer explanation in the paper to avoid confusion.

---

## Summary of Severity

- **CRITICAL**: 
  - theta_i mismatch (#1) - could invalidate main result
  - A_sh value discrepancy (#11) - paper and docs don't match
- **HIGH**: 
  - Template computation inconsistency (#3) - affects null tests
  - Chi-squared decomposition verification (#5) - need to confirm numbers
- **MEDIUM**: 
  - Phase scrambling clarity (#6)
  - Wrong template test (#7)
  - Significance value explanations (#12)
- **LOW**: 
  - C code TODOs (#9)
  - Config questions (#10)

The theta_i mismatch and A_sh discrepancy are the most serious issues and should be addressed immediately before publication.. Test phase scrambling on actual ACT data (not just templates)

### Documentation Needed:

1. Document what A_sh = 1.0 means physically
2. Document template normalization convention
3. Document which parameters were actually used in chains vs. paper description
4. Document phase scrambling procedure in detail

---

## Summary of Severity

- **CRITICAL**: theta_i mismatch (#1) - could invalidate main result
- **HIGH**: Template computation inconsistency (#3) - affects null tests
- **MEDIUM**: Phase scrambling clarity (#6), Wrong template test (#7)
- **LOW**: C code TODOs (#9), Config questions (#10)

The theta_i mismatch is the most serious issue and should be addressed immediately before publication.

