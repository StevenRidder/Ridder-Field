# Geometric Early Dark Energy: Resolving the H₀–S₈ Tensions

**Author**: Steven Ridder  
**Contact**: sridder@post.harvard.edu  
**Repository**: [github.com/StevenRidder/Ridder-Field](https://github.com/StevenRidder/Ridder-Field)

---

## Overview

This repository contains the code, analysis, and paper for **Geometric EDE (φCDM)**—a minimal scalar field model that simultaneously addresses both the Hubble tension and the S₈ tension through a geometry-first approach to early dark energy.

### Key Results

| Finding | Value | Significance |
|---------|-------|--------------|
| **H₀ convergence window** | 69–70 km/s/Mpc | Matches JWST/TRGB calibrations |
| **S₈ suppression** | 0.81–0.82 | Moves toward weak-lensing values |
| **ACT damping-tail signature** | A_sh = 1.16 ± 0.18 | **6.4σ detection** of predicted pattern |
| **Geometric ceiling** | Δχ² = +91 at H₀ = 72 | Early physics cannot reach SH0ES value |

### The Model in One Sentence

A single scalar field with a monodromy-inspired potential briefly injects energy at z ~ 3000, shrinking the sound horizon by ~1% and raising H₀ while the enhanced Hubble friction suppresses structure growth—all through pure geometry (β = 0, no exotic couplings).

---

## Paper

The main paper is located at:

```
phase2/paper/ridder_cosmology_paper.tex
```

**Title**: *Geometry-First Cosmology: Early Dark Energy, the H₀–S₈ Tensions, and a CMB Damping-Tail Signature*

To compile:
```bash
cd phase2/paper
pdflatex ridder_cosmology_paper.tex
```

---

## Repository Structure

```
Ridder-Field/
├── README.md                    # This file
├── phase2/
│   ├── paper/                   # LaTeX paper and figures
│   │   ├── ridder_cosmology_paper.tex
│   │   └── figures/
│   └── class/                   # Modified CLASS implementation
├── phase3/                      # MCMC configuration files
│   ├── ridder_v3_baseline.yaml
│   ├── ridder_v3_shoes.yaml
│   └── ridder_v3_trgb.yaml
├── docs/                        # Documentation
└── archive/                     # Historical development files
```

---

## Key Predictions

### 1. The Soft Shoulder (CMB Damping Tail)
The model predicts an oscillatory residual pattern in high-ℓ TT/EE spectra:
- Positive near ℓ ~ 800
- Crosses zero near ℓ ~ 1200  
- Negative at ℓ > 2000

**Current status**: ACT DR6 template fit yields A_sh = 1.16 ± 0.18 (6.4σ preference for non-zero amplitude, consistent with prediction of A_sh = 1).

### 2. The Geometric Ceiling
Fixed-H₀ profile likelihoods show:
- Δχ² ≈ +2 at H₀ = 69
- Δχ² ≈ +91 at H₀ = 72
- Δχ² ≈ +163 at H₀ = 73

Early-universe physics alone cannot reach the SH0ES value of 73.

### 3. CMB-S4 Decision Point
CMB-S4 will reduce σ(A_sh) by an order of magnitude:
- **Confirmation**: A_sh = 1.0 ± 0.1 with correct phase → validates Geometric EDE
- **Exclusion**: A_sh = 0.0 ± 0.1 → rules out this class of models at >10σ

---

## Dependencies

- **CLASS**: Boltzmann solver ([Blas, Lesgourgues & Tram 2011](https://arxiv.org/abs/1104.2933))
- **Cobaya**: MCMC sampler ([Torrado & Lewis 2021](https://arxiv.org/abs/2005.05290))
- **Python 3.8+**: numpy, scipy, matplotlib, getdist

---

## Citation

If you use this code or build on this work, please cite:

```bibtex
@article{Ridder2025,
    author = "Ridder, Steven",
    title = "{Geometry-First Cosmology: Early Dark Energy, the H₀–S₈ Tensions, and a CMB Damping-Tail Signature}",
    year = "2025",
    note = "In preparation"
}
```

---

## License

MIT License. See LICENSE file for details.

---

## Acknowledgments

This work was developed with substantial assistance from AI tools (Claude, Anthropic). Cosmological calculations were performed using CLASS and Cobaya. This work made use of data from Planck, ACT, and DESI.

---

*"Geometry-first: let the data pull on the metric, then read off which parts of the expansion history need to move."*
