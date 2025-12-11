# Paper 2 Reproduction Guide

**Title**: *A Resolution-Dependent Damping-Tail Feature in ACT DR6 and a Template Test for Pre-Recombination Physics*

This document provides complete instructions for reproducing all results in Paper 2.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Environment Setup](#environment-setup)
3. [Installing Dependencies](#installing-dependencies)
4. [Running MCMC Chains](#running-mcmc-chains)
5. [Reproducing Key Results](#reproducing-key-results)
6. [Generating Figures](#generating-figures)
7. [Verification Tests](#verification-tests)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **OS**: Linux or macOS (Windows via WSL2)
- **RAM**: 32 GB (64 GB recommended for production chains)
- **Disk**: 50 GB free space (likelihoods and chains are large)
- **CPU**: 8+ cores (16+ recommended for parallel chains)

### Software Dependencies
- Python 3.8+ (3.10 recommended)
- GCC or Clang (for CLASS compilation)
- MPI (optional, for parallel chains)
- LaTeX (for paper compilation)

---

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/StevenRidder/Ridder-Field.git
cd Ridder-Field
```

### 2. Create Python Environment

```bash
# Using conda (recommended)
conda create -n ridder python=3.10
conda activate ridder

# Or using venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
source venv/bin/activate  # macOS
```

### 3. Install Python Dependencies

```bash
pip install numpy scipy matplotlib cython
pip install cobaya getdist
pip install pyactlike  # ACT DR6 likelihood

# For development
pip install jupyter ipython
```

---

## Installing Dependencies

### Modified CLASS

Paper 2 uses the same modified CLASS as Paper 1:

```bash
cd phase2/class
make clean
make -j4

# Install Python wrapper
cd python
pip install .
```

### Likelihoods

#### ACT DR6

```bash
# Install ACT likelihood
pip install pyactlike

# Or using Cobaya's installer
cobaya-install act_dr6_mflike
```

#### Planck 2018

```bash
cobaya-install planck_2018_highl_plik.TTTEEE_lite
cobaya-install planck_2018_lowl.TT
cobaya-install planck_2018_lowl.EE
cobaya-install planck_2018_lensing.clik
```

#### DESI Y1 BAO

The DESI Y1 BAO likelihood is included in the repository:

```bash
# The likelihood is at paper2_dr6/likelihoods/desi_y1_bao/
# It will be automatically found if python_path is set correctly in YAML
```

#### Other BAO

```bash
# SDSS DR12 and sixdF are bundled with Cobaya
# No additional installation needed
```

---

## Running MCMC Chains

### Production Chains

All production chains are configured in `paper2_dr6/configs/`:

#### Main Result: EDE with ACT DR6 + DESI

```bash
cd paper2_dr6
cobaya-run configs/prod_p2_dr6_ede.yaml -f
```

**Expected runtime**: 12-24 hours on 8-core machine  
**Output**: `chains/prod_p2_dr6_ede.*.txt`

**Key parameters**:
- Lambda_EDE_ridder: 0.01 - 0.15 (prior)
- theta_i_ridder: 2.0 (fixed)
- n_ridder: 3.0 (fixed)
- beta_ridder: 0.0 (fixed)

#### Baseline: ΛCDM with ACT DR6 + DESI

```bash
cobaya-run configs/prod_p0b_dr6_lcdm.yaml -f
```

**Expected runtime**: 6-12 hours  
**Output**: `chains/prod_p0b_dr6_lcdm.*.txt`

#### Template Fit: A_sh marginalized

```bash
# This requires a modified likelihood that fits A_sh as a free parameter
# See tools/ for template fitting scripts
```

### Configuration Files

| Config | Description | Est. Runtime |
|--------|-------------|--------------|
| `prod_p2_dr6_ede.yaml` | EDE with ACT DR6 + DESI | 12-24 hr |
| `prod_p0b_dr6_lcdm.yaml` | ΛCDM baseline | 6-12 hr |
| `p2_act_only.yaml` | EDE with ACT only | 8-16 hr |
| `p2_act_high_theta.yaml` | EDE with high theta_i | 12-24 hr |

---

## Reproducing Key Results

### 1. Main Result: Template Amplitude

**Claim**: A_sh = 1.61 ± 0.22 (7.4σ significance)

**Method**: Run template fit chain or analyze existing chain

```bash
# If you have the template fit chain
cd paper2_dr6/chains
getdist p3_template_dr6_v2.1.txt

# Or use Python
python -c "
import getdist
g = getdist.loadMCSamples('chains/p3_template_dr6_v2.1')
print('A_sh =', g.getTable().table['A_sh'])
"
```

**Expected output**: A_sh ≈ 1.61 ± 0.22

### 2. Δχ² Improvement

**Claim**: Δχ² = -474 (template vs ΛCDM)

**Method**: Compare best-fit χ² values

```bash
# Extract best-fit χ² from chains
cd paper2_dr6
python -c "
import numpy as np

# Load ΛCDM chain
lcdm = np.loadtxt('chains/prod_p0b_dr6_lcdm.1.txt', skiprows=1)
chi2_lcdm = np.min(lcdm[:, -1])  # Last column is χ²

# Load template chain
template = np.loadtxt('chains/p3_template_dr6_v2.1.txt', skiprows=1)
chi2_template = np.min(template[:, -1])

print(f'Δχ² = {chi2_template - chi2_lcdm:.1f}')
"
```

**Expected output**: Δχ² ≈ -474

### 3. Profile Likelihood at Λ = 0.16

**Claim**: Δχ² = -766 (EDE at Λ=0.16 vs ΛCDM)

**Method**: Run profile likelihood chain

```bash
# The profile likelihood chain should be at:
# chains/lscan_0_16.1.txt

# Verify result
python -c "
import numpy as np
chain = np.loadtxt('chains/lscan_0_16.1.txt', skiprows=1)
chi2_ede = np.min(chain[:, -1])
print(f'EDE χ² = {chi2_ede:.1f}')

# Compare to ΛCDM
lcdm = np.loadtxt('chains/prod_p0b_dr6_lcdm.1.txt', skiprows=1)
chi2_lcdm = np.min(lcdm[:, -1])
print(f'ΛCDM χ² = {chi2_lcdm:.1f}')
print(f'Δχ² = {chi2_ede - chi2_lcdm:.1f}')
"
```

**Expected output**: Δχ² ≈ -766

### 4. PTE Test

**Claim**: PTE < 10⁻⁴ (10,000 simulations)

**Method**: Run PTE simulation script

```bash
cd paper2_dr6/tools
python proper_pte_sims.py
```

**Expected output**: PTE histogram saved to `data/proper_pte_histogram.txt`

### 5. Phase Scrambling Test

**Claim**: Phase coherence at 10.5σ

**Method**: Run phase scrambling simulation

```bash
cd paper2_dr6/tools
python phase_scrambling_sims.py
```

**Expected output**: Results saved to `data/phase_scrambling_results.txt`

---

## Generating Figures

### Figure 1: Spectrum Residuals (The Money Plot)

```bash
cd paper2_dr6
python -c "
# This figure shows the residual between ACT DR6 data and ΛCDM
# with the EDE template overlaid
# See tools/ for plotting scripts
"
```

**Output**: `figures/act_dr6_spectrum_residuals.pdf`

### Figure 2: Robustness Tests

```bash
cd paper2_dr6/tools
python generate_robustness_figure.py
```

**Output**: `figures/robustness_tests.pdf`

### Figure 3: Frequency Achromaticity

```bash
# Run frequency-split chains first, then plot
# See configs/ for frequency-specific configurations
```

**Output**: `figures/frequency_achromaticity.pdf`

### All Figures

Most figures are pre-generated in `paper2_dr6/figures/`. To regenerate:

```bash
cd paper2_dr6
# Run analysis scripts in tools/
# Figures will be saved to figures/
```

---

## Verification Tests

### Chain Convergence

```bash
cd paper2_dr6/chains
getdist prod_p2_dr6_ede.1.txt

# Check R-1 statistic (should be < 0.02)
# Check effective sample size
# Check parameter posteriors
```

### Pipeline Validation

See `PIPELINE_VALIDATION_PLAN.md` for detailed validation steps.

### Key Checks

1. **Reproduce ACT ΛCDM**: Compare to published ACT results
2. **Reproduce Planck ΛCDM**: Compare to published Planck results
3. **Template shape**: Verify template matches EDE prediction
4. **Frequency splits**: Verify achromaticity

---

## Troubleshooting

### CLASS Won't Compile

```bash
# Missing dependencies
sudo apt-get install gcc make  # Linux
xcode-select --install  # macOS
```

### Cobaya Can't Find Likelihoods

```bash
# Check likelihood paths
cobaya-install --help
cobaya-install act_dr6_mflike -p /path/to/likelihoods

# For DESI likelihood, ensure python_path is set in YAML
```

### MCMC Chain Crashes

- Check memory usage (32 GB recommended)
- Reduce `max_samples` for testing
- Use `--debug` flag: `cobaya-run config.yaml --debug`
- Check parameter bounds (especially Lambda_EDE_ridder: 0.01-0.15)

### Numerical Instabilities

If you see NaN or inf in chains:
- Check `Lambda_ridder` bounds (0.01 < Λ < 0.15 for Paper 2)
- Ensure `theta_i_ridder` is reasonable (1.0 or 2.0)
- Use `ignore_prior: false` in minimize settings

### Chain Location Issues

Production chains are located on the Azure VM at:
```
/home/azureuser/Ridder-Field/paper2_dr6/chains/
```

If running locally, chains will be in:
```
paper2_dr6/chains/
```

---

## Computational Resources

### What We Used

- **Azure VM**: Standard_D8s_v3 (8 vCPUs, 32 GB RAM)
- **Total compute time**: ~72 hours for all chains
- **Storage**: ~15 GB for chains and data

### Estimated Requirements

| Component | Requirement |
|-----------|-------------|
| **Quick test** | Laptop, 30 min |
| **One production chain** | 8-core machine, 12-24 hours |
| **Full analysis suite** | 8-core machine, 3-5 days |
| **All chains + tests** | HPC cluster or cloud VM, 1-2 weeks |

---

## Contact

For questions or issues reproducing results:

- **Email**: sridder@post.harvard.edu
- **GitHub Issues**: [Open an issue](https://github.com/StevenRidder/Ridder-Field/issues)

---

## Version History

- **v1.0** (December 2025): Initial release with Paper 2 results

