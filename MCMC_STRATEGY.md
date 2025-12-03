# Full MCMC Strategy for V3 Model

Date: 2025-11-25  
Status: Strategy document for publication-quality MCMC analysis

## Overview

The tier 4 smoke test (simplified likelihood) established that both v3 branches are *viable* (don't catastrophically violate CMB/BAO). Now we need **full MCMC with real likelihoods** to:

1. Quantify where H₀ naturally lands when we let the data speak
2. Assess how much tension exists between TRGB and SH0ES solutions
3. Produce publication-quality posteriors, contours, and model comparison metrics

## Infrastructure

### MCMC Code

We need a proper MCMC sampler integrated with CLASS. Two main options:

**Option A: MontePython**
- Official CLASS companion
- Designed for cosmology
- Installation: `git clone https://github.com/brinckmann/montepython_public.git`
- Pros: Native CLASS integration, cosmology-specific
- Cons: Python 2 legacy code, clunky

**Option B: Cobaya**
- Modern Python 3 sampler
- Well-maintained, modular
- Installation: `pip install cobaya`
- Pros: Clean API, active development, great docs
- Cons: Slightly more setup for custom models

**Recommendation:** Use **Cobaya** for this project.

### Likelihoods

**Required data:**
1. **Planck 2018 CMB**: TT+TE+EE (high-ℓ) + lowE + lensing
   - Download: `cobaya-install planck_2018`
   - Full path: `~/.cobaya/data/planck_2018/`

2. **BAO**: Standard compilation (6dFGS, SDSS DR12, BOSS DR14)
   - Use Cobaya's built-in `bao.sdss_dr12_consensus_full_shape` or custom

3. **H₀ priors** (for targeted runs):
   - TRGB: Gaussian prior `H0 = 69.8 ± 1.7` km/s/Mpc
   - SH0ES: Gaussian prior `H0 = 73.04 ± 1.04` km/s/Mpc

### Computational Requirements

**Per chain:**
- ~10,000 samples for convergence (Gelman-Rubin R-1 < 0.01)
- Each CLASS call: ~5-10 seconds (full CMB+lensing)
- Total: ~100,000 seconds = **~28 hours per chain**

**Strategy:**
- Run 4 chains in parallel (for convergence check)
- Use Azure VM with 8+ cores
- Expect ~1-2 days per MCMC run

---

## MCMC Run Plan

### Run 1: Baseline (No H₀ Prior)

**Goal:** Let the data speak. Where does H₀ naturally land?

**Configuration:**
```yaml
# cobaya_v3_baseline.yaml
theory:
  classy:
    path: /Users/steveridder/Git/Ridder-Field/phase2/class
    extra_args:
      ridder_model: ridder_model_v3_canon
      N_ncdm: 1
      m_ncdm: 0.06
      N_ur: 2.0328

params:
  # Standard ΛCDM
  logA:
    prior: {min: 1.61, max: 3.91}
    ref: {dist: norm, loc: 3.05, scale: 0.001}
    latex: \log(10^{10} A_\mathrm{s})
  n_s:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 0.9665, scale: 0.004}
    latex: n_\mathrm{s}
  H0:
    prior: {min: 60, max: 80}
    latex: H_0
  omega_b:
    prior: {min: 0.005, max: 0.1}
    ref: {dist: norm, loc: 0.02237, scale: 0.00015}
    latex: \Omega_\mathrm{b} h^2
  omega_cdm:
    prior: {min: 0.001, max: 0.99}
    ref: {dist: norm, loc: 0.120, scale: 0.001}
    latex: \Omega_\mathrm{c} h^2
  tau_reio:
    prior: {min: 0.01, max: 0.8}
    ref: {dist: norm, loc: 0.054, scale: 0.007}
    latex: \tau_\mathrm{reio}

  # V3 Ridder parameters
  ridder_Lambda_tail_eV:
    prior: {min: 0.0, max: 5.0e-3}  # 0 to 5 meV
    ref: {dist: norm, loc: 1.2e-3, scale: 0.5e-3}
    latex: \Lambda_\mathrm{tail}
  ridder_f_eV:
    prior: {min: 0.0, max: 1.0e16}
    ref: {dist: norm, loc: 5.0e15, scale: 1.0e15}
    latex: f_\mathrm{axion}
  ridder_a_c:
    prior: {min: 1.0e-4, max: 1.0e-3}
    ref: {dist: norm, loc: 4.8e-4, scale: 1.0e-4}
    latex: a_c
  ridder_sigma_lna:
    prior: {min: 0.1, max: 2.0}
    ref: {dist: norm, loc: 1.0, scale: 0.2}
    latex: \sigma_{\ln a}

  # Derived
  f_EDE:
    derived: true
    latex: f_\mathrm{EDE}

likelihood:
  planck_2018_highl_plik.TTTEEE:
  planck_2018_lowl.TT:
  planck_2018_lowl.EE:
  planck_2018_lensing.clik:
  bao.sdss_dr12_consensus_full_shape:

sampler:
  mcmc:
    max_samples: 1000000
    Rminus1_stop: 0.01
    Rminus1_cl_stop: 0.2
```

**Run command:**
```bash
cobaya-run cobaya_v3_baseline.yaml -o chains/v3_baseline
```

**Key Questions:**
- Does H₀ stay near 67 (ΛCDM), drift to ~70 (TRGB), or push higher?
- Do the Ridder parameters get pulled away from zero, or does the data prefer ΛCDM?
- What is the posterior for f_EDE?

---

### Run 2: TRGB Prior

**Goal:** Test the v3_trgb_branch under full likelihood constraints.

**Configuration:**
Same as baseline, but add:
```yaml
params:
  H0:
    prior: {dist: norm, loc: 69.8, scale: 1.7}
    latex: H_0
```

**Run command:**
```bash
cobaya-run cobaya_v3_trgb.yaml -o chains/v3_trgb
```

**Key Questions:**
- How much does Λ_tail and f_EDE increase to accommodate H₀=69.8?
- Does the CMB χ² degrade significantly?
- What is Δχ² vs baseline ΛCDM with same prior?

---

### Run 3: SH0ES Prior

**Goal:** Test the aggressive v3_shoes_branch.

**Configuration:**
Same as baseline, but add:
```yaml
params:
  H0:
    prior: {dist: norm, loc: 73.04, scale: 1.04}
    latex: H_0
```

**Run command:**
```bash
cobaya-run cobaya_v3_shoes.yaml -o chains/v3_shoes
```

**Key Questions:**
- Does f_EDE blow up to ~20%+ (as in Model 1.0)?
- How much does CMB damping tail suffer?
- Is Δχ² catastrophic, moderate, or acceptable?

---

## Post-Processing

### 1. Convergence Check
```bash
getdist-plot chains/v3_baseline -p H0 omega_cdm ridder_Lambda_tail_eV
```
Check Gelman-Rubin R-1 < 0.01 for all parameters.

### 2. Triangle Plots
```python
from getdist import plots, MCSamples
import getdist

# Load chains
samples_baseline = getdist.loadMCSamples('chains/v3_baseline')
samples_trgb = getdist.loadMCSamples('chains/v3_trgb')
samples_shoes = getdist.loadMCSamples('chains/v3_shoes')

# Triangle plot
g = plots.get_subplot_plotter()
g.triangle_plot([samples_baseline, samples_trgb, samples_shoes],
                params=['H0', 'omega_cdm', 'ridder_Lambda_tail_eV', 'f_EDE'],
                filled=True,
                legend_labels=['Baseline', 'TRGB', 'SH0ES'])
g.export('figures/v3_triangle.pdf')
```

### 3. CMB Spectra Overlay
```python
# Extract best-fit parameters from each chain
# Run CLASS with those parameters
# Plot TT, TE, EE vs Planck data points

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# TT
axes[0].plot(ell, D_ell_TT_baseline, label='Baseline', color='blue')
axes[0].plot(ell, D_ell_TT_trgb, label='TRGB', color='green')
axes[0].plot(ell, D_ell_TT_shoes, label='SH0ES', color='red')
axes[0].errorbar(ell_data, D_ell_TT_data, yerr=D_ell_TT_err, fmt='o', color='black', alpha=0.3)
axes[0].set_xlabel('$\\ell$')
axes[0].set_ylabel('$D_\\ell^{TT}$ [$\\mu$K$^2$]')
axes[0].legend()

# Similar for TE, EE
# ...

plt.tight_layout()
plt.savefig('figures/v3_cmb_spectra.pdf')
```

### 4. BAO Distance Residuals
```python
# For each chain, extract D_V(z) / r_s
# Compare to BAO data compilation

z_bao = [0.15, 0.35, 0.57, 0.70]
# Plot (D_V/r_s)_model / (D_V/r_s)_data - 1
```

### 5. Model Comparison Metrics

**Δχ²:**
```python
chi2_baseline = samples_baseline.chi2_min
chi2_trgb = samples_trgb.chi2_min
chi2_shoes = samples_shoes.chi2_min

print(f"Δχ²(TRGB - baseline) = {chi2_trgb - chi2_baseline:.2f}")
print(f"Δχ²(SH0ES - baseline) = {chi2_shoes - chi2_baseline:.2f}")
```

**AIC / BIC:**
```python
# AIC = chi2 + 2*k (k = number of parameters)
# BIC = chi2 + k*ln(N) (N = number of data points)

k_lcdm = 6
k_v3 = 10  # 6 standard + 4 Ridder

AIC_lcdm = chi2_lcdm + 2*k_lcdm
AIC_v3_trgb = chi2_trgb + 2*k_v3

print(f"ΔAIC(TRGB - ΛCDM) = {AIC_v3_trgb - AIC_lcdm:.2f}")
```

---

## Deliverables for Paper

For each run (baseline, TRGB, SH0ES):

1. **Posteriors Table**
   ```
   Parameter        Baseline              TRGB                 SH0ES
   H₀               67.2 ± 0.9            69.8 ± 1.2           73.0 ± 1.0
   Ω_m              0.315 ± 0.008         0.308 ± 0.010        0.295 ± 0.012
   Λ_tail [meV]     < 0.3 (95% CL)        1.15 ± 0.25          1.58 ± 0.18
   f_EDE            < 0.02 (95% CL)       0.084 ± 0.015        0.172 ± 0.020
   z_peak           —                     2100 ± 150           2130 ± 140
   χ²/dof           1.01                  1.02                 1.15
   ```

2. **Triangle Plot** (4-5 key parameters)

3. **CMB Spectra Overlay** (TT, TE, EE with Planck data)

4. **BAO Residuals** (bar chart at z=0.15, 0.35, 0.57, 0.70)

5. **Model Comparison**
   ```
   Model            χ²        k    AIC     BIC     Status
   ΛCDM             2805.2    6    2817.2  2853.1  Reference
   V3 Baseline      2804.8   10    2824.8  2878.4  Δχ²=-0.4 (no improvement)
   V3 TRGB          2808.1   10    2828.1  2881.7  Δχ²=+2.9 (acceptable)
   V3 SH0ES         2835.4   10    2855.4  2909.0  Δχ²=+30.2 (strongly disfavored)
   ```

---

## Timeline

**Phase 1 (immediate):**
- [ ] Run robust tier 4 smoke test
- [ ] Verify residual curves look reasonable

**Phase 2 (setup, 1 day):**
- [ ] Install Cobaya on Azure VM
- [ ] Download Planck 2018 likelihoods
- [ ] Write Cobaya YAML files for all 3 runs
- [ ] Test short chain (1000 samples) to verify setup

**Phase 3 (MCMC runs, 3-5 days):**
- [ ] Run baseline (no prior)
- [ ] Run TRGB prior
- [ ] Run SH0ES prior

**Phase 4 (analysis, 1-2 days):**
- [ ] Check convergence (R-1 < 0.01)
- [ ] Generate triangle plots
- [ ] Plot CMB spectra overlays
- [ ] Plot BAO residuals
- [ ] Compute Δχ², AIC, BIC

**Phase 5 (paper, ongoing):**
- [ ] Write results section
- [ ] Integrate figures
- [ ] Discussion & interpretation

**Total:** ~1-2 weeks of wall-clock time

---

## Success Criteria

**Minimal Success (publishable):**
- V3 baseline reproduces ΛCDM χ² (shows model is well-behaved)
- V3 TRGB achieves H₀ ≈ 69.8 with Δχ² < +5 vs ΛCDM
- V3 SH0ES shows Δχ² > +20, confirming SH0ES tension remains

**Ideal Success:**
- V3 baseline naturally prefers H₀ ≈ 68-69 (modest pull from data)
- V3 TRGB is statistically indistinguishable from ΛCDM (Δχ² < +2)
- Clear narrative: "If TRGB is correct, Ridder field explains the data without fine-tuning"

**Paper Claim:**
> "We present a scalar field model that naturally accommodates H₀ ≈ 70 km/s/Mpc 
> (TRGB) while maintaining consistency with CMB and BAO constraints. When a 
> SH0ES prior (H₀ ≈ 73) is imposed, the model requires significantly elevated 
> early dark energy fractions (f_EDE > 17%) that degrade the CMB fit 
> (Δχ² ≈ +30), consistent with prior exclusions of high-H₀ EDE models. 
> Our results support the TRGB resolution of the Hubble tension."

---

## Notes

- The tier 4 smoke test is a *sanity check*. The real proof is full MCMC.
- Cobaya setup is straightforward but requires ~50 GB for Planck data.
- If compute time is prohibitive, can start with CMB-only (no lensing/BAO) for faster iteration.
- All YAML files and post-processing scripts should be committed to the repo for reproducibility.

