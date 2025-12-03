# Geometric Early Dark Energy: The Ridder Field (φCDM)

[![Paper Status](https://img.shields.io/badge/Paper-Submitted-green.svg)](phase2/paper/ridder_cosmology_paper.tex)
[![arXiv](https://img.shields.io/badge/arXiv-coming%20soon-orange.svg)]()

**Author**: Steven Ridder  
**Contact**: sridder@post.harvard.edu  
**Repository**: [github.com/StevenRidder/Ridder-Field](https://github.com/StevenRidder/Ridder-Field)

---

## 📄 Paper

**Title**: *Geometry-First Cosmology: Early Dark Energy, the H₀–S₈ Tensions, and a CMB Damping-Tail Signature*

The paper proposes a minimal scalar field model (**φCDM** or "Ridder Field") that addresses both the Hubble tension and S₈ tension through pure geometric effects—no exotic couplings required.

📁 **Paper location**: [`phase2/paper/ridder_cosmology_paper.tex`](phase2/paper/ridder_cosmology_paper.tex)

---

## 🎯 Key Results (MCMC Validated)

Our Tier 5 MCMC chains (December 2025) confirm the paper's predictions:

| Finding | Measurement | Prediction | Status |
|---------|-------------|------------|--------|
| **Geometric Tax** (DESI era) | Δχ² = +10.8 | +10 to +15 | ✅ Confirmed |
| **H₀ Convergence Window** | 69.82 ± 0.21 km/s/Mpc | 69–71 | ✅ Confirmed |
| **ΛCDM H₀ (DESI era)** | 68.57 ± 0.09 km/s/Mpc | ~68.5 | ✅ Confirmed |
| **Soft Shoulder Detection** | A_sh = 2.65 ± 0.19 (13.7σ) | A_sh ≈ 1 | ⚠️ Stronger than predicted |
| **Geometric Ceiling** | Δχ² = +91 at H₀ = 72 | Ceiling exists | ✅ Confirmed |

### The "Geometric Tax" Explained

In the DESI era, the Ridder Field pays ~11 χ² to elevate H₀ from 68.5 to ~70:

```
ΛCDM:  χ² = 4244.5,  H₀ = 68.57 ± 0.09 km/s/Mpc
φ-EDE: χ² = 4255.3,  H₀ = 69.82 ± 0.21 km/s/Mpc,  Λ = 0.79

Δχ² = +10.8 (the "price of admission" to the convergence window)
```

### H₀ Profile (The Geometric Ceiling)

| H₀ Target | Δχ² vs ΛCDM | Interpretation |
|-----------|-------------|----------------|
| 69.0 | +2.2 | Nearly degenerate with ΛCDM |
| 70.0 | +14.5 | Mild penalty |
| 71.0 | +33.7 | Significant cost |
| 72.0 | +91.0 | Effectively excluded |
| 73.0 | +140 | Ruled out by geometry |

This quantifies the **"geometric ceiling"**: early-universe physics can reach H₀ ≈ 69–70, but the SH0ES value of 73 is geometrically impossible.

---

## 🔬 The Model

### One-Sentence Summary

A single scalar field with a monodromy-inspired potential briefly injects energy at z ~ 3000, shrinking the sound horizon by ~1% and raising H₀, while the enhanced Hubble friction suppresses structure growth (S₈)—all through pure geometry (β = 0, no exotic couplings).

### Predicted Observational Signatures

1. **Soft Shoulder** (CMB Damping Tail)
   - Oscillatory residual pattern in high-ℓ TT/EE spectra
   - Positive near ℓ ~ 800, zero crossing at ℓ ~ 1200, negative at ℓ > 2000
   - **ACT DR6 detection**: A_sh = 2.65 ± 0.19 (13.7σ)

2. **S₈ Suppression**
   - φ-EDE predicts S₈ = 0.81–0.82
   - Moves toward weak-lensing measurements (DES, KiDS)

3. **CMB-S4 Decision Point**
   - CMB-S4 will reduce σ(A_sh) by an order of magnitude
   - Either confirms the model at >10σ or rules it out

---

## 📁 Repository Structure

```
Ridder-Field/
├── README.md                      # This file
├── REPRODUCIBILITY.md             # How to reproduce our results
├── requirements.txt               # Python dependencies
│
├── phase2/                        # Publication materials
│   ├── paper/                     # LaTeX paper and figures
│   │   ├── ridder_cosmology_paper.tex
│   │   └── figures/              # Paper figures (PNG/PDF)
│   └── class/                     # Modified CLASS with Ridder potential
│       ├── source/ridder_unified_potential.c
│       └── include/background.h  # Added φ-field declarations
│
├── phase3/                        # MCMC analysis
│   ├── configs/                   # Cobaya YAML configurations
│   ├── chains/                    # MCMC chain outputs
│   ├── CHAIN_RESULTS_SUMMARY.md   # Detailed results documentation
│   └── figures/                   # Analysis plots
│
├── patches/                       # CLASS modification patches
│   └── class/                     # Diffs for all modified files
│
├── AxiCLASS/                      # Reference AxiCLASS implementation
│
└── archive/                       # Development history
```

### Key Files

| File | Description |
|------|-------------|
| `phase2/paper/ridder_cosmology_paper.tex` | Main paper (LaTeX) |
| `phase2/class/source/ridder_unified_potential.c` | φ-field potential implementation |
| `phase3/CHAIN_RESULTS_SUMMARY.md` | Full MCMC results documentation |
| `phase3/configs/tier5_*.yaml` | Production MCMC configurations |
| `patches/class/` | All CLASS modifications as patches |

---

## 🚀 Quick Start

### Requirements

- **Python 3.8+** with numpy, scipy, matplotlib
- **CLASS** (Boltzmann solver) - modified version included
- **Cobaya** (MCMC sampler) - for chain runs
- **Planck/ACT likelihoods** - see REPRODUCIBILITY.md

### Compile Modified CLASS

```bash
cd phase2/class
make clean && make -j4
cd python && pip install .
```

### Run a Test Chain

```bash
cd phase3
cobaya-run configs/ridder_v3_baseline.yaml -f
```

### Compile the Paper

```bash
cd phase2/paper
pdflatex ridder_cosmology_paper.tex
bibtex ridder_cosmology_paper
pdflatex ridder_cosmology_paper.tex
pdflatex ridder_cosmology_paper.tex
```

---

## 📊 MCMC Chain Results

All production chains are documented in [`phase3/CHAIN_RESULTS_SUMMARY.md`](phase3/CHAIN_RESULTS_SUMMARY.md).

### Summary Table (Tier 5: Planck + BAO + Local H₀)

| World | Model | Best χ² | H₀ (km/s/Mpc) | Λ_EDE | Δχ² |
|-------|-------|---------|---------------|-------|-----|
| **SH0ES + DESI** | ΛCDM | 4244.5 | 68.57 ± 0.09 | — | 0 (ref) |
| **SH0ES + DESI** | φ-EDE | 4255.3 | 69.82 ± 0.21 | 0.79 | **+10.8** |
| TRGB + DESI | ΛCDM | 4229.0 | 68.54 ± 0.20 | — | 0 (ref) |
| TRGB + DESI | φ-EDE | 4251.6 | 69.71 ± 0.06 | 1.20 | +22.6 |
| DES Y1 | ΛCDM | 4690.2 | 69.76 ± 0.13 | — | 0 (ref) |
| DES Y1 | φ-EDE | 4700.7 | 70.54 ± 0.08 | 1.55 | +10.5 |

---

## 🔄 Reproducibility

See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for complete instructions on:

1. Setting up the environment
2. Compiling the modified CLASS
3. Installing likelihoods (Planck, ACT, BAO, SH0ES)
4. Running MCMC chains
5. Reproducing all paper figures

---

## 📜 Citation

If you use this code or build on this work, please cite:

```bibtex
@article{Ridder2025,
    author = "Ridder, Steven",
    title = "{Geometry-First Cosmology: Early Dark Energy, 
             the H₀–S₈ Tensions, and a CMB Damping-Tail Signature}",
    year = "2025",
    eprint = "XXXX.XXXXX",
    archivePrefix = "arXiv",
    primaryClass = "astro-ph.CO",
    note = "Submitted to JCAP"
}
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Cosmological codes**: CLASS ([Blas, Lesgourgues & Tram 2011](https://arxiv.org/abs/1104.2933)), Cobaya ([Torrado & Lewis 2021](https://arxiv.org/abs/2005.05290))
- **Data**: Planck 2018, ACT DR6, DESI Y1 BAO, SH0ES, DES Y1
- **Development assistance**: Claude (Anthropic)
- **Computational resources**: Azure VM

---

*"Geometry-first: let the data pull on the metric, then read off which parts of the expansion history need to move."*
