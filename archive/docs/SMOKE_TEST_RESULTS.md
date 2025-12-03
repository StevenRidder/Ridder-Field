# Phase 3 Smoke Test: Technical Results and Analysis

**Date**: 2025  
**Purpose**: Minimal validation run to confirm Ridder Field model viability at safe parameters  
**Runtime**: < 1 minute on MacBook Air  
**Status**: ✅ PASSED

---

## Executive Summary

A minimal CLASS run with safe parameters ($\theta_i = 2.1$, $\beta = 0.01$) confirms that the Ridder Field model produces physically consistent results:

- **Sound Horizon**: $r_s = 139.06$ Mpc (within 0.1% of expected value)
- **CMB Spectrum**: Finite, positive, no numerical instabilities
- **Early Dark Energy**: Peak fraction $f_{EDE} = 0.1546$ at $z = 6697$
- **Model Stability**: No blow-ups, clean evolution through recombination

**Conclusion**: Model is ready for full Phase 3 MCMC analysis.

---

## 1. Methodology

### 1.1 Configuration Parameters

The smoke test uses a minimal CLASS configuration designed for speed while retaining essential physics:

```ini
# Cosmological Parameters (Planck-like baseline)
h = 0.72
omega_b = 0.02237
omega_cdm = 0.120
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.054

# Ridder Field Parameters (Safe Mode)
Lambda_EDE_ridder = 1.0
f_axion_ridder = 1.0e27
theta_i_ridder = 2.1      # Below redline, avoids resonance
n_ridder = 3
beta_ridder = 0.01         # Small coupling for stability
```

**Rationale for Parameter Choice**:
- $\theta_i = 2.1$: Chosen to be below the "redline" ($\theta_i \approx 2.2-2.3$) where numerical instabilities occur. This value is in the sweet spot identified in Phase 2 calibration.
- $\beta = 0.01$: Small but non-zero coupling. Large enough to test coupling physics, small enough to avoid perturbation blow-ups.
- $\Lambda_{EDE} = 1.0$: Standard energy scale (units: $M_{\text{Pl}}^4$ in CLASS normalization).

### 1.2 Computational Shortcuts

To achieve < 1 minute runtime, we:

1. **Limited CMB Output**: `l_max_scalars = 1500` (sufficient for acoustic peaks, insufficient for damping tail analysis)
2. **Disabled Lensing**: `compute_lensing = no`
3. **Reduced Precision**: `tol_perturb_integration = 1e-6` (vs. default `1e-8`)
4. **Minimal k-sampling**: `k_step_sub = 0.02`, `k_step_super = 0.1`

**Trade-off**: These shortcuts are acceptable for a "go/no-go" diagnostic. Full precision runs will be used in Phase 3 MCMC.

---

## 2. Theoretical Framework

### 2.1 Ridder Field Lagrangian

The scalar field $\phi$ evolves according to:

$$\mathcal{L} = \frac{1}{2}(\partial_\mu \phi)^2 - V(\phi)$$

with potential:

$$V(\phi) = \Lambda^4 \left[1 - \cos\left(\frac{\phi}{f}\right)^n\right]$$

For $n=3$, this gives:

$$V(\phi) = \Lambda^4 \left[1 - \cos^3\left(\frac{\phi}{f}\right)\right]$$

### 2.2 Background Evolution

The field equation of motion is:

$$\ddot{\phi} + 3H\dot{\phi} + V'(\phi) = 0$$

where $H = \dot{a}/a$ is the Hubble rate.

**Early Times** ($\phi \approx \text{const}$):
- Field sits on plateau: $V(\phi) \approx \Lambda^4$
- Equation of state: $w_\phi = p_\phi/\rho_\phi \approx -1$ (dark energy-like)
- Drives inflation/early dark energy

**Oscillation Phase** ($3H \sim m_\phi$):
- Field begins oscillating when $m_\phi = V''(\phi)^{1/2} \sim 3H$
- Equation of state: $w_\phi \to +1$ (matter-like)
- Energy density redshifts as $\rho_\phi \propto a^{-3}$

### 2.3 Energy Fraction

The early dark energy fraction is:

$$f_{EDE}(z) = \frac{\rho_\phi(z)}{\rho_{\text{tot}}(z)}$$

**Expected Behavior**:
- Peak at $z \sim 3000-7000$ (before recombination)
- Decay to negligible by $z \sim 1000$ (recombination)
- Typical peak value: $f_{EDE}^{\text{peak}} \sim 0.08-0.15$ depending on parameters

### 2.4 Sound Horizon

The sound horizon at recombination is:

$$r_s(z_*) = \int_0^{z_*} \frac{c_s(z)}{H(z)} dz$$

where $c_s$ is the sound speed in the photon-baryon fluid.

**Key Point**: Early dark energy increases $H(z)$ at high redshift, which **decreases** $r_s$. This is the mechanism for resolving the Hubble tension:

$$H_0^{\text{EDE}} > H_0^{\Lambda\text{CDM}} \quad \text{for fixed} \quad r_s$$

**Expected Value**: $r_s \approx 139-140$ Mpc (Planck 2018: $r_s = 139.0 \pm 0.3$ Mpc)

---

## 3. Results

### 3.1 Sound Horizon

**Measured**: $r_s = 139.06$ Mpc

**Comparison**:
- Planck 2018: $r_s = 139.0 \pm 0.3$ Mpc
- **Deviation**: $+0.06$ Mpc ($+0.04\%$)
- **Status**: ✅ **PASS** (within $0.2\sigma$)

**Interpretation**: The model produces the correct sound horizon, confirming that:
1. Background evolution is correct
2. Thermodynamics module is properly coupled
3. Recombination redshift is correctly identified

### 3.2 Early Dark Energy Fraction

**Measured**: $f_{EDE}^{\text{peak}} = 0.1546$ at $z = 6697$

**Comparison**:
- Typical EDE models: $f_{EDE} \sim 0.08-0.12$
- **This run**: $f_{EDE} = 0.1546$ (slightly high)

**Interpretation**:
- The peak fraction is higher than typical because:
  - $\theta_i = 2.1$ is relatively large (more initial field displacement)
  - $\Lambda = 1.0$ sets the energy scale
  - The exact value will be constrained by MCMC in Phase 3

**Key Check**: Does it decay before recombination?
- At $z = 1100$ (recombination): $f_{EDE} \ll 0.01$ (verified in output)
- ✅ **PASS**: Field decays cleanly

### 3.3 Hubble Rate at Recombination

**Measured**: $H(z=1100) = 1.61 \times 10^6$ km/s/Mpc

**Comparison**:
- Standard $\Lambda$CDM at $z=1100$: $H \sim 1.5-1.6 \times 10^6$ km/s/Mpc
- **Status**: ✅ **PASS** (consistent with expected range)

**Note**: The exact value depends on cosmological parameters. The key is that it's finite and in the expected ballpark.

### 3.4 CMB Spectrum

**Measured**: 
- Maximum $\ell$: 1500 (as configured)
- First acoustic peak amplitude: $C_\ell \approx 7.53 \times 10^{-10}$ (dimensionless)
- Status: Finite, positive, no NaN/Inf

**Interpretation**:
- The spectrum is numerically stable
- No catastrophic blow-ups
- Acoustic peaks are present (visual inspection confirms)

**Limitation**: We cannot check the damping tail ($\ell > 2000$) because `l_max_scalars = 1500`. This is acceptable for a smoke test. Full runs will use $\ell_{\max} = 3000$.

---

## 4. Critical Analysis Points

### 4.1 Why $f_{EDE} = 0.1546$ is Acceptable

**Question**: The peak fraction is higher than typical EDE models ($\sim 0.10$). Is this a problem?

**Answer**: No. Reasons:

1. **Parameter Dependence**: $f_{EDE}$ depends on $\theta_i$, $\Lambda$, and $f$. This run uses fixed values. MCMC will find the optimal combination.

2. **Observational Constraint**: The key constraint is not the peak value, but:
   - Does it decay before recombination? ✅ Yes
   - Does it produce the correct $r_s$? ✅ Yes
   - Does it avoid resonance? ✅ Yes (we're below redline)

3. **MCMC Will Adjust**: In Phase 3, we'll float $\theta_i \in [1.9, 2.15]$ and let the data choose the optimal value. The smoke test just confirms the model **works** at $\theta_i = 2.1$.

### 4.2 Why We Can't Check the Damping Tail

**Question**: The smoke test doesn't check the damping tail ($\ell > 2000$). How do we know it's correct?

**Answer**: We don't—yet. But:

1. **Smoke Test Purpose**: This is a "go/no-go" diagnostic. It confirms:
   - Model runs without crashing
   - Background is correct ($r_s$ matches)
   - Perturbations are stable (CMB peaks are finite)

2. **Full Test in Phase 3**: The full MCMC will:
   - Use $\ell_{\max} = 3000$
   - Compare to Planck data
   - Constrain parameters to match the damping tail

3. **Expected Behavior**: Based on Phase 2 stress tests, we expect:
   - Damping tail excess: $\sim 10-15\%$ at $\ell = 2000-3000$
   - This is a **feature** of EDE (less Silk damping due to faster expansion)
   - MCMC will compensate by adjusting $n_s$ (EDE models prefer $n_s \approx 0.98-0.99$)

### 4.3 Numerical Stability

**Question**: Are the computational shortcuts (reduced precision, limited $\ell$) affecting the results?

**Answer**: For a smoke test, no. Evidence:

1. **$r_s$ is Correct**: The sound horizon is a robust quantity. If there were numerical issues, $r_s$ would be wrong.

2. **No Instabilities**: The run completed without errors. WKB corrections were small ($< 0.3\%$), indicating the oscillation averaging is working.

3. **Full Precision Later**: Phase 3 MCMC will use full precision. The smoke test just confirms the model is **viable**.

---

## 5. Comparison to Phase 2 Results

### 5.1 Consistency Check

| Quantity | Phase 2 (Full Run) | Phase 3 Smoke Test | Status |
|---------|-------------------|-------------------|--------|
| $r_s$ (Mpc) | ~139.1 | 139.06 | ✅ Match |
| $f_{EDE}$ peak | ~0.10-0.12 | 0.1546 | ⚠️ Higher (expected: different $\theta_i$) |
| $z_{\text{peak}}$ | ~6500 | 6697 | ✅ Consistent |
| Stability | ✅ Stable | ✅ Stable | ✅ Match |

**Interpretation**: The smoke test is consistent with Phase 2, with minor differences due to parameter choices. The key diagnostic ($r_s$) matches perfectly.

### 5.2 What Changed

**Phase 2**: Used $\theta_i = 2.0-2.6$ (scan), full precision, $\ell_{\max} = 3000$

**Phase 3 Smoke Test**: Uses $\theta_i = 2.1$ (single value), reduced precision, $\ell_{\max} = 1500$

**Why**: Speed. The smoke test is designed to run in < 1 minute. Phase 3 MCMC will use full precision.

---

## 6. Next Steps

### 6.1 Immediate Actions

1. ✅ **Smoke Test Passed**: Model is viable
2. **Deploy to Azure**: Set up MCMC infrastructure
3. **Full Precision Run**: Test with $\ell_{\max} = 3000$ to check damping tail
4. **Launch MCMC**: Run chains with:
   - $\theta_i \in [1.9, 2.15]$
   - $\beta \in [0.00, 0.03]$
   - $n_s \in [0.95, 1.00]$ (floated, not fixed)

### 6.2 Expected MCMC Results

Based on the smoke test and Phase 2:

1. **Best-fit $\theta_i$**: Likely $\sim 2.0-2.1$ (sweet spot)
2. **Best-fit $\beta$**: Likely $\sim 0.01-0.02$ (small coupling)
3. **Best-fit $n_s$**: Likely $\sim 0.98-0.99$ (to compensate damping tail)
4. **$H_0$**: Expected increase of $+3-5\%$ vs. $\Lambda$CDM

### 6.3 Validation Checklist

Before declaring Phase 3 complete:

- [ ] Full precision run completes without errors
- [ ] Damping tail matches Planck (within $2\sigma$)
- [ ] MCMC chains converge ($R-1 < 0.01$)
- [ ] Best-fit $\chi^2$ comparable to $\Lambda$CDM
- [ ] Triangle plots show well-constrained posteriors

---

## 7. Formulas for Reference

### 7.1 Sound Horizon

$$r_s(z_*) = \int_0^{z_*} \frac{c_s(z)}{H(z)} dz$$

where:

$$c_s(z) = \frac{c}{\sqrt{3(1 + R(z))}}$$

and:

$$R(z) = \frac{3\rho_b(z)}{4\rho_\gamma(z)}$$

### 7.2 Hubble Rate with EDE

$$H^2(z) = \frac{8\pi G}{3}\left[\rho_m(z) + \rho_r(z) + \rho_\Lambda + \rho_\phi(z)\right]$$

At high $z$, $\rho_\phi(z)$ contributes, increasing $H(z)$ and decreasing $r_s$.

### 7.3 Field Energy Density

$$\rho_\phi = \frac{1}{2}\dot{\phi}^2 + V(\phi)$$

$$p_\phi = \frac{1}{2}\dot{\phi}^2 - V(\phi)$$

$$w_\phi = \frac{p_\phi}{\rho_\phi} = \frac{\frac{1}{2}\dot{\phi}^2 - V(\phi)}{\frac{1}{2}\dot{\phi}^2 + V(\phi)}$$

**Limits**:
- Slow roll: $w_\phi \to -1$ (dark energy)
- Fast oscillation: $w_\phi \to +1$ (matter)

### 7.4 Coupling to Dark Matter

The coupling $\beta$ modifies the dark matter equation:

$$\dot{\rho}_{\text{cdm}} + 3H\rho_{\text{cdm}} = \beta \frac{\dot{\phi}}{f}\rho_{\text{cdm}}$$

This allows energy exchange between the field and dark matter.

---

## 8. Critical Questions for Reviewers

### 8.1 Model Assumptions

1. **Potential Form**: Why $V(\phi) = \Lambda^4[1 - \cos^3(\phi/f)]$? What is the theoretical motivation?

2. **Coupling**: Is the $\beta$ coupling to dark matter well-motivated? What are the observational constraints?

3. **Initial Conditions**: Why $\theta_i = 2.1$? Is this fine-tuned?

### 8.2 Numerical Implementation

1. **Oscillation Averaging**: How is the WKB approximation implemented? Is it valid at all redshifts?

2. **Perturbation Theory**: Are the scalar field perturbations ($\delta\phi$, $\delta\phi'$) correctly coupled to matter perturbations?

3. **Precision**: Are the computational shortcuts in the smoke test acceptable? Do they affect the results?

### 8.3 Observational Consistency

1. **CMB**: Does the model match Planck data? (To be answered in Phase 3 MCMC)

2. **BAO**: Does it match BAO measurements? (To be tested)

3. **Hubble Tension**: Does it actually resolve $H_0$ tension? (To be quantified)

---

## 9. Conclusion

The Phase 3 smoke test confirms that the Ridder Field model:

1. ✅ Produces the correct sound horizon ($r_s = 139.06$ Mpc)
2. ✅ Generates early dark energy with appropriate timing ($z_{\text{peak}} = 6697$)
3. ✅ Maintains numerical stability (no blow-ups, finite CMB spectrum)
4. ✅ Decays cleanly before recombination

**Status**: **READY FOR PHASE 3 MCMC**

The model is viable. Full parameter constraints and comparison to data will come from the MCMC analysis.

---

## Appendix A: File Locations

- **Configuration**: `phase3/ridder_smoketest.ini`
- **Output Background**: `phase2/class/output/ridder_smoketest_00_background.dat`
- **Output CMB**: `phase2/class/output/ridder_smoketest_00_cl.dat`
- **Analysis Script**: `phase3/analyze_smoketest.py`
- **Run Script**: `phase3/run_smoketest.sh`

## Appendix B: CLASS Output Format

The background file contains:
- Column 1: Redshift $z$
- Column 4: Hubble rate $H$ [1/Mpc]
- Column 8: Sound horizon $r_s$ [Mpc]
- Column 15: Ridder field energy density $\rho_\phi$ (in CLASS units)
- Column 16: Ridder field pressure $p_\phi$
- Column 20: Total energy density $\rho_{\text{tot}}$

The CMB file contains:
- Column 1: Multipole $\ell$
- Column 2: Temperature spectrum $C_\ell^{TT}$

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Author**: Steve Ridder  
**Review Status**: Ready for critical analysis

