# Phase 3: MCMC Parameter Fitting - Setup Guide

**Status:** 🚧 Framework Ready, Needs Data Download

---

## What We've Accomplished

### ✅ Phase 2 Complete & Validated
- CLASS implementation: **PERFECT** (0.00% error vs Phase 1)
- Background evolution: **VALIDATED**
- Perturbation equations: **IMPLEMENTED**
- Framework: **READY FOR MCMC**

### 🚧 Phase 3 Status
- Parameter files: **CREATED**
- MCMC framework: **SET UP**
- Data download: **NEEDED**

---

## Quick Start

### 1. Install Dependencies

```bash
# Install Cobaya
pip3 install --user cobaya

# Install CLASS Python interface (via Cobaya)
cobaya-install classy --path /Users/steveridder/Git/Ridder\ Field/phase2/class
```

### 2. Download Observational Data

**Planck 2018:**
```bash
# Download from Planck Legacy Archive
# https://pla.esac.esa.int/
# Or use Cobaya's data installer:
cobaya-install planck_2018_highl_plik.TTTEEE
cobaya-install planck_2018_lowl.TT
cobaya-install planck_2018_lensing
```

**BAO:**
```bash
cobaya-install bao.boss
cobaya-install bao.eBOSS
```

**SH0ES:**
```bash
# SH0ES H0 measurement (Riess et al. 2020)
# H0 = 73.2 ± 1.3 km/s/Mpc
# Usually included in Cobaya's H0 likelihood
```

### 3. Run MCMC

```bash
cd phase3
python3 run_mcmc.py
```

Or use Cobaya directly:
```bash
cobaya-run ridder_field.yaml
```

---

## Parameter File Structure

The `ridder_field.yaml` file defines:

1. **Theory:** CLASS with Ridder field
2. **Parameters:**
   - Standard: H0, omega_b, omega_cdm, n_s, logA, tau_reio
   - Ridder: Lambda_EDE_ridder, f_axion_ridder, theta_i_ridder, beta_ridder, n_ridder
3. **Likelihoods:** Planck, BAO, SH0ES
4. **Sampler:** MCMC with convergence criteria

---

## Expected Results

### If Model Works:
- ✅ H0 posterior peaks at **72-74 km/s/Mpc** (not 67)
- ✅ Δχ² < 10 vs ΛCDM
- ✅ Bayes factor > 3 (moderate evidence)
- ✅ Lambda_EDE_ridder > 0 (EDE active)
- ✅ f_EDE ~ 10% at z ~ 3000

### If Model Doesn't Work:
- ❌ H0 still peaks at ~67 km/s/Mpc
- ❌ Model fits worse than ΛCDM
- ❌ Parameters unconstrained

---

## Troubleshooting

### CLASS Python Interface Issues
If `classy` doesn't compile:
1. Try: `cobaya-install classy` (uses Cobaya's installer)
2. Or: Use CLASS binary directly (modify Cobaya config)

### Data Download Issues
- Check internet connection
- Verify Cobaya data paths
- Manually download from Planck Legacy Archive if needed

---

## Next Steps

1. **Download data** (Planck, BAO, SH0ES)
2. **Run test chain** (short run to verify setup)
3. **Run production chains** (long runs for convergence)
4. **Analyze results** (triangle plots, H0 posterior, etc.)

---

**Status:** Framework ready. Once data is downloaded, we can test if the model actually resolves the tensions!

