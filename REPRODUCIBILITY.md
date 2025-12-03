# Reproducibility Guide

This document provides complete instructions for reproducing the results in *"Geometry-First Cosmology: Early Dark Energy, the H₀–S₈ Tensions, and a CMB Damping-Tail Signature"* (Ridder 2025).

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Environment Setup](#environment-setup)
3. [Installing Modified CLASS](#installing-modified-class)
4. [Installing Likelihoods](#installing-likelihoods)
5. [Running MCMC Chains](#running-mcmc-chains)
6. [Reproducing Paper Figures](#reproducing-paper-figures)
7. [Computational Resources](#computational-resources)

---

## System Requirements

### Minimum Requirements
- **OS**: Linux or macOS (Windows via WSL2)
- **RAM**: 16 GB (32 GB recommended for MCMC)
- **Disk**: 50 GB free space (likelihoods are large)
- **CPU**: 4+ cores (8+ recommended for parallel chains)

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
```

### 3. Install Python Dependencies

```bash
pip install numpy scipy matplotlib cython
pip install cobaya getdist

# For development
pip install jupyter ipython
```

---

## Installing Modified CLASS

Our model requires a modified version of CLASS with the Ridder (φ-field) potential.

### Option A: Use Pre-Modified Source (Recommended)

```bash
cd phase2/class
make clean
make -j4

# Install Python wrapper
cd python
pip install .
```

### Option B: Apply Patches to Vanilla CLASS

If you want to start from upstream CLASS:

```bash
# Clone vanilla CLASS
git clone https://github.com/lesgourg/class_public.git class_vanilla
cd class_vanilla
git checkout v3.2.0  # or latest stable

# Apply our patches
cp ../patches/class/*.patch .
patch -p1 < background.c.patch
patch -p1 < background.h.patch
patch -p1 < input.c.patch
patch -p1 < perturbations.c.patch

# Copy our potential source
cp ../phase2/class/source/ridder_unified_potential.c source/
cp ../phase2/class/source/ridder_v3_potential.c source/

# Compile
make clean && make -j4
```

### Verify Installation

```python
from classy import Class

cosmo = Class()
cosmo.set({
    'output': 'tCl,pCl,lCl',
    'l_max_scalars': 2500,
    'ridder_field_enable': 'yes',
    'Lambda_ridder': 0.8,
    'n_ridder': 3.0,
})
cosmo.compute()
print("Ridder field enabled successfully!")
```

---

## Installing Likelihoods

### Planck 2018

```bash
# Using Cobaya's automatic installer
cobaya-install planck_2018_highl_plik.TTTEEE_lite
cobaya-install planck_2018_lowl.TT
cobaya-install planck_2018_lowl.EE
cobaya-install planck_2018_lensing.clik
```

### ACT DR6

```bash
# Download ACT mflike
cobaya-install pyactlike
# Or manually:
pip install pyactlike
```

### BAO Likelihoods

```bash
# SDSS DR12 and sixdF are bundled with Cobaya
# DESI Y1 BAO (when public):
# pip install desilike  # or follow DESI instructions
```

### SH0ES Prior

Built into Cobaya as a Gaussian prior:
```yaml
params:
  H0:
    prior:
      dist: norm
      loc: 73.04
      scale: 1.04
```

### TRGB Prior

```yaml
params:
  H0:
    prior:
      dist: norm
      loc: 69.8
      scale: 1.7
```

### DES Y1 Weak Lensing

```bash
# Follow DES instructions at:
# https://github.com/des-science/DESPipelines
```

---

## Running MCMC Chains

### Tier 3: Quick Smoke Test (~10 minutes)

```bash
cd phase3
cobaya-run configs/ridder_v3_baseline.yaml -f
```

### Tier 4: Medium Precision (~2 hours)

```bash
cobaya-run configs/tier4_v3_shoes.yaml -f
```

### Tier 5: Production Quality (~24 hours)

```bash
# Single chain
cobaya-run configs/tier5_v3_baseline.yaml -f

# Parallel chains (recommended)
mpirun -n 4 cobaya-run configs/tier5_v3_shoes.yaml -f
```

### Configuration Files

| Config | Description | Est. Runtime |
|--------|-------------|--------------|
| `ridder_v3_baseline.yaml` | Quick test, no external priors | 10 min |
| `tier4_v3_shoes.yaml` | Medium precision, SH0ES prior | 2 hr |
| `tier5_v3_baseline.yaml` | Full Planck, no local H₀ | 6 hr |
| `tier5_ede_shoes_desi.yaml` | Planck + BAO + SH0ES + DESI | 24 hr |
| `tier5_ede_des_y1.yaml` | Planck + BAO + DES weak lensing | 24 hr |

### Key Parameters

The Ridder field is controlled by these parameters:

```yaml
params:
  Lambda_ridder:         # Potential steepness (typically 0.5–2.0)
    prior:
      min: 0.1
      max: 3.0
  n_ridder:              # Potential power (fixed at 3.0)
    value: 3.0
  theta_i_ridder:        # Initial field displacement
    value: 0.75
  beta_ridder:           # Dark matter coupling (fixed at 0)
    value: 0.0
```

---

## Reproducing Paper Figures

### Figure 1: Geometric Ceiling

```bash
cd phase3
python plot_geometric_ceiling.py
```

### Figure 2: CMB Soft Shoulder

```bash
python plot_cmb_comparison.py
```

### Figure 3: H₀–S₈ Plane

```bash
python generate_paper_plots.py --plot h0_s8
```

### Figure 4: Forest Plot

```bash
python generate_paper_plots.py --plot forest
```

### All Figures

```bash
cd phase3
python generate_paper_plots.py --all
# Outputs saved to phase3/figures/
```

---

## Computational Resources

### What We Used

- **Azure VM**: Standard_D8s_v3 (8 vCPUs, 32 GB RAM)
- **Total compute time**: ~48 hours
- **Total cost**: ~$50 Azure credits
- **Storage**: ~10 GB for chains

### Estimated Requirements for Full Reproduction

| Component | Requirement |
|-----------|-------------|
| **Quick test** | Laptop, 10 min |
| **One Tier 5 chain** | 8-core machine, 6–24 hours |
| **Full Tier 5 suite** | 8-core machine, 3–5 days |
| **All chains from paper** | HPC cluster or cloud VM, 1 week |

### Cloud VM Setup (Azure)

```bash
# Create VM
az vm create \
  --resource-group myResourceGroup \
  --name ridder-chains \
  --image Ubuntu2204 \
  --size Standard_D8s_v3 \
  --admin-username <VM_USER> \
  --generate-ssh-keys

# SSH into VM
ssh <VM_USER>@<VM_IP>

# Clone and setup
git clone https://github.com/StevenRidder/Ridder-Field.git
cd Ridder-Field
pip install -r requirements.txt
cd phase2/class && make -j8
```

---

## Troubleshooting

### CLASS Won't Compile

```bash
# Missing dependencies
sudo apt-get install gcc make

# On macOS
xcode-select --install
```

### Cobaya Can't Find Likelihoods

```bash
# Check likelihood paths
cobaya-install --help
cobaya-install planck_2018_highl_plik.TTTEEE_lite -p /path/to/likelihoods
```

### MCMC Chain Crashes

- Check memory usage (32 GB recommended for Tier 5)
- Reduce `max_samples` for testing
- Use `--debug` flag: `cobaya-run config.yaml --debug`

### Numerical Instabilities

If you see NaN or inf in chains:
- Check `Lambda_ridder` bounds (0.1 < Λ < 3.0)
- Ensure `theta_i_ridder` < 1.5
- Use `ignore_prior: false` in minimize settings

---

## Contact

For questions or issues reproducing results:

- **Email**: sridder@post.harvard.edu
- **GitHub Issues**: [Open an issue](https://github.com/StevenRidder/Ridder-Field/issues)

---

## Version History

- **v1.0** (December 2025): Initial submission
- **v1.1** (December 2025): Updated Δχ² values from final chains

