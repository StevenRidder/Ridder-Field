# Geometric Early Dark Energy: The Ridder Field (φCDM)

[![Paper Status](https://img.shields.io/badge/PRD-Submitted-blue.svg)](phase2/paper/ridder_cosmology_paper.tex)
[![Data](https://img.shields.io/badge/Zenodo-10.5281%2Fzenodo.17822063-blue.svg)](https://doi.org/10.5281/zenodo.17822063)

**Author**: Steven Ridder  
**Contact**: sridder@post.harvard.edu  
**Repository**: [github.com/StevenRidder/Ridder-Field](https://github.com/StevenRidder/Ridder-Field)

---

## 📄 Paper

**Title**: *Early Dark Energy and the Geometric Ceiling: Constraints from Planck, ACT DR6, and DESI Y1*

**Status**: Submitted to Physical Review D (December 2025)

The paper proposes a minimal scalar field model (**Geometric EDE** or "φ-EDE") that addresses both the Hubble tension and S₈ tension through pre-recombination expansion history modifications.

📁 **Paper location**: [`phase2/paper/ridder_cosmology_paper.tex`](phase2/paper/ridder_cosmology_paper.tex)

---

## 🎯 Key Results

### Three Novel Contributions

1. **Geometric Ceiling**: Fixed-H₀ profile likelihoods reveal that early-time physics alone cannot reach H₀ > 71 km/s/Mpc. The χ² cost rises from +2 at H₀=69 to +15 at H₀=70 to ≳90 at H₀=72.

2. **Correlation Flip**: DESI Y1 BAO reverses the sign of the correlation between EDE amplitude and reionization optical depth τ, closing a degeneracy that previously allowed low-ℓ polarization to compensate damping-tail costs.

3. **Soft Shoulder Detection**: A percent-level oscillatory residual in the CMB damping tail, fit as a template amplitude A_sh = 1.16 ± 0.18 (6.4σ conditional) in ACT DR6 data.

### Quantitative Results

| Finding | Value | Notes |
|---------|-------|-------|
| **Pre-DESI improvement** | Δχ² ≈ −4.5 | EDE improves over ΛCDM |
| **H₀ tension reduction** | 4.3σ → 2.3σ | With pre-DESI data |
| **S₈ tension reduction** | 2.7σ → 1.1σ | With pre-DESI data |
| **DESI-era H₀ ceiling** | H₀ ≈ 69–70 | Geometric limit |
| **ΛCDM penalty at H₀=70** | Δχ² ≳ 30–40 | Forcing ΛCDM to convergence window |

### H₀ Profile (The Geometric Ceiling)

| H₀ Target | Δχ² vs ΛCDM | Interpretation |
|-----------|-------------|----------------|
| 69.0 | +2 | Nearly degenerate |
| 70.0 | +15 | Moderate penalty |
| 71.0 | +40 | Significant cost |
| 72.0 | ≳90 | Effectively excluded |
| 73.0 (SH0ES) | Geometrically impossible | Early-time physics cannot reach |

---

## 🔬 The Model

### One-Sentence Summary

A scalar field with a monodromy-inspired potential briefly injects a few percent of the total energy density at z ~ 3000, shrinking the sound horizon by ~1% and raising H₀ toward 69–70 km/s/Mpc, while modestly suppressing S₈—all through pure geometry (β = 0, no exotic dark matter coupling).

### Predicted Observational Signatures

1. **Soft Shoulder** (CMB Damping Tail)
   - Oscillatory residual pattern in high-ℓ TT/EE spectra
   - Phase determined by Δr_s ≈ −0.9 Mpc
   - **ACT DR6**: A_sh = 1.16 ± 0.18 (6.4σ conditional)

2. **S₈ Suppression**
   - φ-EDE predicts S₈ ≈ 0.81–0.82
   - Consistent with weak-lensing (DES Y3: 0.776 ± 0.017)

3. **CMB-S4 Decision Point**
   - Will reduce σ(A_sh) by order of magnitude
   - Confirmation: A_sh = 1.0 ± 0.2 with predicted phase
   - Exclusion: A_sh = 0.0 ± 0.1

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

## 📁 Repository Structure

```
Ridder-Field/
├── README.md                      # This file
├── REPRODUCIBILITY.md             # How to reproduce our results
├── cover_letter_prd.txt           # PRD submission cover letter
├── create_zenodo_archive.sh       # Archive creation script
│
├── phase2/                        # Publication materials
│   ├── paper/                     # LaTeX paper and figures
│   │   ├── ridder_cosmology_paper.tex
│   │   └── figures/              
│   └── class/                     # Modified CLASS with Ridder potential
│       ├── source/ridder_unified_potential.c
│       └── include/background.h  
│
├── phase3/                        # MCMC analysis
│   ├── configs/                   # Cobaya YAML configurations
│   ├── chains/                    # MCMC chain outputs
│   ├── generate_h0_profile_figure.py
│   ├── run_act_null_tests.py
│   └── figures/                   
│
├── overleaf_final/                # Submission-ready paper
│   └── main.tex                   
│
├── patches/                       # CLASS modification patches
│
└── AxiCLASS/                      # Reference implementation
```

---

## 🚀 Quick Start

### Requirements

- **Python 3.8+** with numpy, scipy, matplotlib, getdist
- **CLASS** (Boltzmann solver) - modified version included
- **Cobaya** (MCMC sampler)
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
cobaya-run configs/tier5_baseline.yaml -f
```

### Compile the Paper

```bash
cd overleaf_final
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

---

## 📜 Citation

If you use this code or build on this work, please cite:

```bibtex
@article{Ridder2025,
    author = "Ridder, Steven",
    title = "{Early Dark Energy and the Geometric Ceiling: 
             Constraints from Planck, ACT DR6, and DESI Y1}",
    year = "2025",
    note = "Submitted to Physical Review D",
    doi = "10.5281/zenodo.17822063"
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

*"The geometric ceiling is not a failure of imagination—it is a boundary condition imposed by the data."*
