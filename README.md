# Ridder Field: Early Dark Energy Cosmology

[![Paper 1 Status](https://img.shields.io/badge/PRD-Submitted-blue.svg)](phase2/paper/ridder_cosmology_paper.tex)
[![Paper 2 Status](https://img.shields.io/badge/Paper-2_Complete-green.svg)](paper2_dr6/paper2_v2_anomaly.tex)
[![Data](https://img.shields.io/badge/Zenodo-10.5281%2Fzenodo.17822063-blue.svg)](https://doi.org/10.5281/zenodo.17822063)

**Author**: Steven Ridder  
**Contact**: sridder@post.harvard.edu  
**Repository**: [github.com/StevenRidder/Ridder-Field](https://github.com/StevenRidder/Ridder-Field)

---

## 📚 Papers

This repository contains code, data, and analysis for two papers on Early Dark Energy (EDE) cosmology:

### Paper 1: Geometric Early Dark Energy (φCDM)

**Title**: *Early Dark Energy and the Geometric Ceiling: Constraints from Planck, ACT DR6, and DESI Y1*

**Status**: Submitted to Physical Review D (December 2025)

**Location**: [`phase2/paper/ridder_cosmology_paper.tex`](phase2/paper/ridder_cosmology_paper.tex)

**Key Results**:
- Geometric ceiling: Early-time physics cannot reach H₀ > 71 km/s/Mpc
- DESI Y1 BAO reverses EDE-τ correlation, closing degeneracy
- H₀ tension reduction: 4.3σ → 2.3σ (pre-DESI data)
- S₈ tension reduction: 2.7σ → 1.1σ (pre-DESI data)

### Paper 2: Damping-Tail Feature Detection

**Title**: *A Resolution-Dependent Damping-Tail Feature in ACT DR6 and a Template Test for Pre-Recombination Physics*

**Status**: Complete (December 2025)

**Location**: [`paper2_dr6/paper2_v2_anomaly.tex`](paper2_dr6/paper2_v2_anomaly.tex)

**Key Results**:
- Template amplitude: A_sh = 1.61 ± 0.22 (7.4σ significance)
- Δχ² = -474 for one extra parameter (ACT DR6 + DESI BAO)
- Resolution-dependent discrepancy between ACT and Planck
- Robustness tests: frequency splits, phase scrambling, shift/dilation

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (3.10 recommended)
- **GCC/Clang** (for CLASS compilation)
- **LaTeX** (for paper compilation)
- **Cobaya** (MCMC sampler)
- **CLASS** (Boltzmann solver - modified version included)

### Installation

```bash
# Clone repository
git clone https://github.com/StevenRidder/Ridder-Field.git
cd Ridder-Field

# Create Python environment
conda create -n ridder python=3.10
conda activate ridder
# OR
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install numpy scipy matplotlib cython
pip install cobaya getdist

# Compile modified CLASS
cd phase2/class
make clean && make -j4
cd python && pip install .
```

### Running Analysis

**Paper 1 (Geometric EDE)**:
```bash
cd phase3
cobaya-run configs/tier5_baseline.yaml -f
```

**Paper 2 (Template Detection)**:
```bash
cd paper2_dr6
cobaya-run configs/prod_p2_dr6_ede.yaml -f
```

---

## 📖 Documentation

### Reproduction Guides

- **[REPRODUCIBILITY.md](REPRODUCIBILITY.md)**: Complete guide for Paper 1
- **[paper2_dr6/REPRODUCTION.md](paper2_dr6/REPRODUCTION.md)**: Complete guide for Paper 2

### Paper 2 Documentation

- **[PAPER2_PROJECT_PLAN.md](paper2_dr6/PAPER2_PROJECT_PLAN.md)**: Project plan and status
- **[CHAIN_VERIFICATION.md](paper2_dr6/CHAIN_VERIFICATION.md)**: MCMC chain verification
- **[VERIFICATION_STATUS.md](paper2_dr6/VERIFICATION_STATUS.md)**: Verification status of all claims
- **[BUG_REPORT.md](paper2_dr6/BUG_REPORT.md)**: Known issues and resolutions

### Repository Structure

```
Ridder-Field/
├── README.md                      # This file
├── REPRODUCIBILITY.md             # Paper 1 reproduction guide
│
├── paper2_dr6/                    # Paper 2: Template detection
│   ├── paper2_v2_anomaly.tex     # Main LaTeX paper
│   ├── paper2_soft_shoulder.tex  # Alternative version
│   ├── REPRODUCTION.md            # Paper 2 reproduction guide
│   ├── configs/                   # Cobaya YAML configurations
│   ├── chains/                    # MCMC chain outputs (on VM)
│   ├── figures/                   # Paper figures
│   ├── data/                      # Analysis data files
│   ├── tools/                     # Analysis scripts
│   └── *.md                       # Documentation files
│
├── phase2/                        # Paper 1: Geometric EDE
│   ├── paper/                     # LaTeX paper and figures
│   └── class/                     # Modified CLASS with Ridder potential
│
├── phase3/                        # Paper 1 MCMC analysis
│   ├── configs/                   # Cobaya YAML configurations
│   ├── chains/                    # MCMC chain outputs
│   └── figures/                   # Analysis figures
│
├── AxiCLASS/                      # Reference CLASS implementation
├── patches/                       # CLASS modification patches
└── archive/                       # Historical documentation
```

---

## 🔬 The Model

### One-Sentence Summary

A scalar field with a monodromy-inspired potential briefly injects a few percent of the total energy density at z ~ 3000, shrinking the sound horizon by ~1% and raising H₀ toward 69–70 km/s/Mpc, while modestly suppressing S₈—all through pure geometry (β = 0, no exotic dark matter coupling).

### Key Parameters

```yaml
Lambda_ridder:    # Potential steepness (typically 0.1-0.15 for Paper 2)
n_ridder:         # Potential power (fixed at 3.0)
theta_i_ridder:   # Initial field displacement (1.0 or 2.0)
beta_ridder:      # Dark matter coupling (fixed at 0.0)
```

---

## 📦 Data Archive

All MCMC chains, configuration files, and analysis scripts are permanently archived:

**Zenodo DOI**: [10.5281/zenodo.17822063](https://doi.org/10.5281/zenodo.17822063)

Contents:
- Production MCMC chains (GetDist format)
- Cobaya YAML configurations
- Modified CLASS source code
- Analysis and plotting scripts

---

## 🎯 Key Results Summary

### Paper 1: Geometric Ceiling

| Finding | Value | Notes |
|---------|-------|-------|
| **Pre-DESI improvement** | Δχ² ≈ −4.5 | EDE improves over ΛCDM |
| **H₀ tension reduction** | 4.3σ → 2.3σ | With pre-DESI data |
| **S₈ tension reduction** | 2.7σ → 1.1σ | With pre-DESI data |
| **DESI-era H₀ ceiling** | H₀ ≈ 69–70 | Geometric limit |
| **ΛCDM penalty at H₀=70** | Δχ² ≳ 30–40 | Forcing ΛCDM to convergence window |

### Paper 2: Template Detection

| Finding | Value | Notes |
|---------|-------|-------|
| **Template amplitude** | A_sh = 1.61 ± 0.22 | 7.4σ significance |
| **Δχ² improvement** | −474 | For one extra parameter |
| **H₀ (if interpreted)** | 70.7 ± 0.5 km/s/Mpc | In minimal EDE model |
| **σ₈ (if interpreted)** | 0.75 ± 0.01 | In minimal EDE model |
| **PTE** | < 10⁻⁴ | From 10,000 simulations |
| **Phase coherence** | 10.5σ | Phase scrambling test |

---

## 🛠️ Computational Resources

### What We Used

- **Azure VM**: Standard_D8s_v3 (8 vCPUs, 32 GB RAM)
- **Total compute time**: ~48 hours (Paper 1) + ~72 hours (Paper 2)
- **Storage**: ~10 GB for chains

### Estimated Requirements

| Component | Requirement |
|-----------|-------------|
| **Quick test** | Laptop, 10 min |
| **One production chain** | 8-core machine, 6–24 hours |
| **Full analysis suite** | 8-core machine, 3–5 days |
| **All chains from papers** | HPC cluster or cloud VM, 1–2 weeks |

---

## 📜 Citation

If you use this code or build on this work, please cite:

**Paper 1**:
```bibtex
@article{Ridder2025a,
    author = "Ridder, Steven",
    title = "{Early Dark Energy and the Geometric Ceiling: 
             Constraints from Planck, ACT DR6, and DESI Y1}",
    year = "2025",
    note = "Submitted to Physical Review D",
    doi = "10.5281/zenodo.17822063"
}
```

**Paper 2**:
```bibtex
@article{Ridder2025b,
    author = "Ridder, Steven",
    title = "{A Resolution-Dependent Damping-Tail Feature in ACT DR6 
             and a Template Test for Pre-Recombination Physics}",
    year = "2025",
    note = "In preparation"
}
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Cosmological codes**: CLASS, Cobaya
- **Data**: Planck 2018, ACT DR6, DESI Y1 BAO, SH0ES, Pantheon+, DES
- **AI Assistance**: ChatGPT, Claude (Anthropic), Gemini — used for literature review, code development, and manuscript drafting. All scientific decisions made by the author.
- **Computational resources**: Azure VM (Australia East)

---

## 📞 Contact & Support

For questions or issues:

- **Email**: sridder@post.harvard.edu
- **GitHub Issues**: [Open an issue](https://github.com/StevenRidder/Ridder-Field/issues)

---

*"The geometric ceiling is not a failure of imagination—it is a boundary condition imposed by the data."*
