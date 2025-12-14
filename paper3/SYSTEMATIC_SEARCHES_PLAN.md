# Paper 3: Systematic Parameter Searches Plan

## Overview

Following the methodology from Paper 2 (where we found the sweet spot at Λ_EDE = 0.16), we need to perform systematic parameter searches for the Unified Ridder Field model to:

1. Find optimal parameter values
2. Confirm results aren't flukes
3. Map the likelihood landscape
4. Identify degeneracies

---

## Current Best-Fit (from MCMC)

| Parameter | Value | Status |
|-----------|-------|--------|
| xi_late | 0.05 (fixed) | Need to optimize |
| w0 | -1.065 | Sampled |
| H0 | 70.96 | Derived |
| S8 | 0.813 | Derived |
| Δχ² | -6.6 (Planck) | vs ΛCDM |

---

## Phase 1: Grid Searches (Fixed Cosmology)

### 1.1 xi_late Scan

```yaml
# Scan xi_late with fixed w0 = -1.05
xi_late_values: [0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.10]
w0_fld: -1.05 (fixed)
cosmology: Planck 2018 best-fit

Outputs:
  - chi2_planck vs xi_late
  - H0 vs xi_late
  - S8 vs xi_late
  - Omega_m vs xi_late
```

### 1.2 w0 Scan

```yaml
# Scan w0 with fixed xi_late = 0.05
w0_values: [-1.15, -1.12, -1.10, -1.08, -1.06, -1.04, -1.02, -1.00]
xi_late: 0.05 (fixed)
cosmology: Planck 2018 best-fit

Outputs:
  - chi2_planck vs w0
  - H0 vs w0
  - S8 vs w0
```

### 1.3 2D Grid Search

```yaml
# Full 2D grid
xi_late: [0.02, 0.04, 0.05, 0.06, 0.08]
w0: [-1.12, -1.08, -1.05, -1.02]

# 20 grid points total
# Find minimum chi2 and optimal (xi_late, w0) combination
```

---

## Phase 2: Free-Floating Parameter MCMC

### 2.1 Planck-only with Free xi_late

```yaml
# Let xi_late float along with cosmology
sampled_params:
  xi_late:
    prior: {min: 0.0, max: 0.15}
    ref: {dist: norm, loc: 0.05, scale: 0.02}
  w0_fld:
    prior: {min: -1.3, max: -0.9}
    ref: {dist: norm, loc: -1.05, scale: 0.03}
  H0:
    prior: {min: 60, max: 80}
  omega_cdm:
    prior: {min: 0.10, max: 0.14}
  # ... other cosmological params

likelihoods:
  - planck_2018_lowl.TT
  - planck_2018_lowl.EE
  - planck_2018_highl_plik.TTTEEE
  - planck_2018_lensing.clik
```

### 2.2 Full Data with Free xi_late

```yaml
# Full data suite with xi_late floating
sampled_params:
  xi_late:
    prior: {min: 0.0, max: 0.15}
  w0_fld:
    prior: {min: -1.3, max: -0.9}
  # ... cosmological params

likelihoods:
  # CMB
  - planck_2018_lowl.TT
  - planck_2018_lowl.EE
  - planck_2018_highl_plik.TTTEEE
  - planck_2018_lensing.clik
  # BAO
  - bao.sdss_dr12_consensus_bao
  - bao.sixdf_2011_bao
  # SNe
  - sn.pantheon
  # Optional: SH0ES
  - H0.riess2020
```

---

## Phase 3: Robustness Tests

### 3.1 Null Tests

```yaml
# Test 1: Random parameter perturbations
# Verify chi2 worsens when moving away from best-fit

# Test 2: Different random seeds
# Run same config 5x with different seeds
# Verify convergence to same region

# Test 3: Prior sensitivity
# Vary priors by ±50% and check posterior stability
```

### 3.2 Dataset Consistency

```yaml
# Run separately on:
- Planck TT only
- Planck EE only  
- Planck TE only
- Planck + BAO (no SNe)
- Planck + SNe (no BAO)

# Check: Does each dataset independently prefer xi_late > 0?
```

### 3.3 Tension Decomposition

```yaml
# Compute chi2 contributions from each likelihood component
# at best-fit xi_late vs xi_late = 0

# Expected:
#   Planck low-ell: slight improvement
#   Planck high-ell: neutral
#   Planck lensing: slight penalty (lower A_lens)
#   BAO: neutral to slight improvement
#   SNe: neutral
```

---

## Phase 4: Extended Parameter Space

### 4.1 Time-Dependent Coupling

```yaml
# Test: Does coupling turn-on redshift matter?
z_late_on_values: [5, 10, 15, 20, 30]

# Fixed xi_late = 0.05, w0 = -1.05
# Scan z_late_on to find optimal transition
```

### 4.2 Coupling Form

```yaml
# Test different coupling functional forms:
# 1. Step function (current): xi(z) = xi_late for z < z_on
# 2. Smooth: xi(z) = xi_late * (1 - tanh((z-z_on)/delta_z))
# 3. Power law: xi(z) = xi_late * (1+z)^{-alpha}
```

### 4.3 Early + Late Combined

```yaml
# Test if adding early-time EDE improves further
# This would be the full unified model

# Add parameters:
#   Lambda_EDE (early energy scale)
#   z_c (critical redshift for EDE)
#   
# But: Expect early EDE to ADD chi2 penalty from Planck TE
```

---

## Phase 5: Forecasts

### 5.1 DESI Y5 Forecast

```yaml
# Mock DESI Y5 BAO data at:
z_eff: [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]

# Forecast constraints on:
#   - w0 precision
#   - H(z) reconstruction
#   - Will DESI definitively measure w < -1?
```

### 5.2 CMB-S4 Forecast

```yaml
# Mock CMB-S4 lensing with 1% A_lens precision
# Can CMB-S4 detect the 2% A_lens suppression?

# Also forecast:
#   - Improved sigma8 constraint
#   - Better Omega_m from lensing tomography
```

---

## Execution Plan

### Week 1: Grid Searches
- [ ] Run 1D xi_late scan (10 points)
- [ ] Run 1D w0 scan (8 points)
- [ ] Run 2D grid (20 points)
- [ ] Identify optimal (xi_late, w0)

### Week 2: Free-Floating MCMC
- [ ] Planck-only with free xi_late
- [ ] Full data with free xi_late
- [ ] Compare posteriors to fixed runs

### Week 3: Robustness
- [ ] Null tests (random perturbations)
- [ ] Dataset splits
- [ ] Prior sensitivity

### Week 4: Analysis & Write-up
- [ ] Compile all results
- [ ] Create figures (contours, chi2 profiles)
- [ ] Update Paper 3 with results

---

## Key Questions to Answer

1. **Is xi_late = 0.05 optimal, or is there a better value?**
   - Grid search will answer this

2. **Is the improvement robust when xi_late floats freely?**
   - Free MCMC will answer this

3. **Does every dataset prefer xi_late > 0?**
   - Dataset splits will answer this

4. **Is there degeneracy between xi_late and w0?**
   - 2D posterior will reveal this

5. **What's the detection significance for xi_late ≠ 0?**
   - Compare Bayesian evidence: xi_late free vs fixed to 0

---

## Files to Create

```
paper3/
├── configs/
│   ├── grid_xi_late.yaml
│   ├── grid_w0.yaml
│   ├── grid_2d.yaml
│   ├── free_xi_late_planck.yaml
│   ├── free_xi_late_fulldata.yaml
│   └── robustness/
│       ├── planck_tt_only.yaml
│       ├── planck_ee_only.yaml
│       └── ...
├── scripts/
│   ├── run_grid_search.py
│   ├── analyze_grid.py
│   ├── plot_contours.py
│   └── compute_evidence.py
├── results/
│   └── (output chains and plots)
└── SYSTEMATIC_SEARCHES_PLAN.md (this file)
```

---

## Success Criteria

The model is considered **validated** if:

1. ✅ Grid search finds clear minimum at xi_late ~ 0.04-0.06
2. ✅ Free MCMC converges to same region
3. ✅ Δχ² < -5 holds across dataset splits
4. ✅ No dataset shows Δχ² > +10 penalty
5. ✅ Bayesian evidence favors xi_late > 0 at >3σ

The model is considered **falsified** if:

1. ❌ Optimal xi_late is consistent with 0
2. ❌ Any major dataset shows Δχ² > +20
3. ❌ Results are prior-dependent
4. ❌ Different seeds give inconsistent posteriors

---

# 🔬 CLASS Validation & Sanity Checks - Critical Protocol

Before publishing, we must be **absolutely certain** results aren't numerical artifacts.

---

## Phase 1: Basic CLASS Sanity Checks

### Test 1: Reproduce Standard ΛCDM First

Set `xi_late = 0`, `w0 = -1.0` and verify textbook values:

| Parameter | Expected (Planck 2018) | Tolerance |
|-----------|------------------------|-----------|
| H0 | 67.36 ± 0.54 | ±1.0 |
| Omega_m | 0.315 ± 0.007 | ±0.01 |
| sigma_8 | 0.811 ± 0.006 | ±0.02 |
| Age | 13.787 ± 0.020 Gyr | ±0.1 |

**If CLASS gives H0 = 68.5 with xi_late=0, something is wrong.**

### Test 2: Energy Conservation

The coupling transfers energy: `Q = ξ H ρ_DM f_DE`

Verify at each timestep:
```
d(rho_DM)/dt + 3H*rho_DM = -Q
d(rho_DE)/dt + 3H(rho_DE + P_DE) = +Q
Sum → standard conservation: d(rho_tot)/dt + 3H(rho_tot + P_tot) = 0
```

**Action:** Add diagnostic print statements to verify Q_in = Q_out.

### Test 3: Background Evolution Continuity

Plot H(a), Omega_m(a), w_eff(a) vs scale factor.

**Red flags:**
- Discontinuities in H(a)
- Omega_m going negative
- w_eff jumping around
- Deviations starting at z > 10 (coupling should be off!)

---

## Phase 2: CMB-Specific Validation

### Test 4: Sound Horizon Must Not Change

```
r_s = ∫[c_s / H(z)] dz  from z=1100 to z=∞

ΛCDM: r_s ≈ 144.4 Mpc
Your model: r_s = ???

If r_s changes by >0.5%, you're modifying early-time physics!
```

**Action:** Extract `r_s` from CLASS and verify < 0.3% difference from ΛCDM.

### Test 5: Acoustic Peak Positions

Peak positions (ΛCDM):
- 1st peak: ℓ ≈ 220
- 2nd peak: ℓ ≈ 540
- 3rd peak: ℓ ≈ 810

**Allowed shift: < 1 ℓ per peak**

### Test 6: Matter-Radiation Equality

```
ΛCDM: z_eq ≈ 3387
Your model: z_eq = ???

If z_eq changes by >2%, early-time physics is affected
```

---

## Phase 3: Late-Time Physics Validation

### Test 7: H₀ Calculation Cross-Check

H₀ can be computed multiple ways in CLASS:
1. Direct from H(a=1)
2. From 100*h parameter
3. Back-calculated from angular diameter distance to CMB

**All three should agree to <0.01 km/s/Mpc**

### Test 8: Distance Ladder Consistency

```
Angular diameter distance to CMB:
D_A(z=1100) ≈ 13.8 Mpc (comoving ~40 Mpc)

Luminosity distance to z=1:
D_L(z=1) ≈ 6.6 Gpc

Compare to ΛCDM: ensure <3% difference
```

### Test 9: Matter Power Spectrum Normalization

```
σ₈² = (1/2π²) ∫ P(k) k² W²(kR) dk

Your σ₈ should be ~0.83-0.85
If σ₈ < 0.75 or > 0.90, something is wrong
```

---

## Phase 4: Numerical Stability Tests

### Test 10: Resolution Independence

Run with different CLASS precision settings:
```yaml
perturb_sampling_stepsize: [0.01, 0.05, 0.10]
l_max_scalars: [2500, 3000, 4000]
k_max: [1.0, 5.0, 10.0] h/Mpc
```

**Results should agree to <0.5% in H₀, σ₈**

### Test 11: Initial Conditions Test

Try different initial redshifts:
```
z_initial = [10000, 50000, 100000]
```

**If results change significantly, IC problems exist.**

### Test 12: Coupling Implementation Double-Check

Review CLASS modification:
```c
if (z < pba->z_late_on) {  // z < 10
    double f_DE = Omega_DE / (Omega_DE + Omega_m);
    double coupling = pba->xi_late * f_DE;
    rho_cdm_effective = rho_cdm * (1.0 - coupling);
}
```

**Common bugs:**
- Using 'a' instead of 'z' (watch sign!)
- Applying coupling to background but not perturbations
- Double-counting the coupling effect
- Wrong normalization of f_DE

---

## Phase 5: Independent Cross-Checks

### Test 13: Compare to CAMB

If possible, implement same model in CAMB:
- CAMB H₀ vs CLASS H₀: should match to <0.1%
- CAMB C_ℓ^TT vs CLASS C_ℓ^TT: should match to <1%

### Test 14: Analytical Estimates

Quick analytical check for late-time H(z):

For phantom w = -1.07:
```
H(z)/H₀ ≈ sqrt(Ω_m(1+z)³ + Ω_DE(1+z)^(3(1+w)))

At z=0.5:
H(0.5) ≈ H₀ * sqrt(0.27*3.375 + 0.73*1.11) ≈ 1.29 H₀
```

**If CLASS gives H(0.5)/H₀ = 1.5, something is very wrong.**

### Test 15: Cobaya Self-Consistency

Check derived parameters:
- H₀ = 100*h (by definition)
- Ω_m = ω_m / h² (verify consistency)
- σ₈ from CLASS matches σ₈ in MCMC output
- Age of universe is physical (13-14 Gyr)

---

## Phase 6: Pathological Case Tests

### Test 16: Extreme Parameter Values

```
xi_late = 0.0    → Should reproduce ΛCDM exactly
xi_late = 0.2    → Should give unphysical results (catch this!)
w0 = -0.9        → Quintessence, should work
w0 = -1.5        → Strong phantom, might break
```

**If CLASS crashes or gives NaNs, implementation has stability issues.**

### Test 17: Coupling Sign Test (CRITICAL)

Flip the coupling sign and verify it makes things WORSE:
```
Q = +ξ H ρ_DM  (energy DM → DE, your model)
Q = -ξ H ρ_DM  (energy DE → DM, should be terrible)
```

**If negative coupling also "improves" fit, implementation is wrong!**

---

## Phase 7: Literature Comparison

### Test 18: Compare to Published IDE Models

Reference papers:
- Di Valentino+ 2020: IDE with Q ∝ H ρ_DM
- Kumar & Nunes 2016: Coupled quintessence
- Valiviita+ 2008: Adiabatic vs isocurvature

**Check H₀ boost is similar magnitude (2-4 km/s/Mpc).**

### Test 19: EDE Comparison (Negative Control)

Your model should NOT show EDE pathologies:

| EDE Problems | Your Model Should Show |
|--------------|------------------------|
| High-ℓ damping tail anomaly (Δχ² ~ +50) | None (late-time only) |
| TE phase shift | None (CMB unaffected) |
| ns pushed to ~0.99 | ns ≈ 0.965 (standard) |

**If you see EDE-like problems, coupling is leaking to early times!**

---

## Validation Script

```python
#!/usr/bin/env python3
"""CLASS Output Validation for Ridder Field Model"""

import numpy as np
from classy import Class

def validate_ridder_class(params):
    cosmo = Class()
    cosmo.set(params)
    cosmo.compute()
    
    # Test 1: Basic Sanity
    h = cosmo.h()
    H0 = 100 * h
    Omega_m = cosmo.Omega_m()
    sigma_8 = cosmo.sigma8()
    age = cosmo.age()
    
    print(f"H0 = {H0:.2f} km/s/Mpc")
    print(f"Omega_m = {Omega_m:.4f}")
    print(f"sigma_8 = {sigma_8:.4f}")
    print(f"Age = {age:.3f} Gyr")
    
    assert 60 < H0 < 80, f"H0 = {H0} is unphysical!"
    assert 0.2 < Omega_m < 0.4, f"Omega_m = {Omega_m} is unphysical!"
    assert 0.7 < sigma_8 < 0.9, f"sigma_8 = {sigma_8} is unphysical!"
    assert 13 < age < 15, f"Age = {age} Gyr is unphysical!"
    
    # Test 2: Sound Horizon
    rs = cosmo.rs_drag()
    rs_lcdm = 144.4
    delta_rs = abs(rs - rs_lcdm) / rs_lcdm * 100
    print(f"r_s = {rs:.2f} Mpc (Δ = {delta_rs:.2f}%)")
    assert delta_rs < 0.5, f"Sound horizon changed by {delta_rs}%!"
    
    # Test 3: Distance Measures
    DA_cmb = cosmo.angular_distance(1100)
    print(f"D_A(z=1100) = {DA_cmb:.2f} Mpc")
    assert 13 < DA_cmb < 15, "DA to CMB is unphysical!"
    
    # Test 4: Power Spectrum
    k = np.logspace(-4, 0, 100)
    Pk = np.array([cosmo.pk(ki, 0) for ki in k])
    assert np.all(Pk > 0), "Negative power spectrum!"
    assert np.all(np.isfinite(Pk)), "NaN in power spectrum!"
    
    cosmo.struct_cleanup()
    cosmo.empty()
    
    print("\n✅ All validation tests passed!\n")
    return True
```

---

## Red Flags Summary

| Symptom | Likely Problem |
|---------|----------------|
| H₀ jumps around between runs | Numerical instability |
| r_s changes by >0.5% | Early-time coupling leakage |
| χ² improves but H₀ < 68 | Not actually solving tension |
| Ω_m goes negative at some z | Energy conservation violated |
| σ₈ > 0.90 | Unphysical growth |
| Age < 13 Gyr | Something very wrong |
| C_ℓ peaks shift | CMB physics modified (bad!) |
| Negative P(k) anywhere | Implementation bug |

---

## Validation Sprint Schedule

**Day 1:** Tests 1-9 (basic sanity + CMB)
**Day 2:** Tests 10-19 (stability + literature)

**Only proceed to publication if ALL tests pass.**

