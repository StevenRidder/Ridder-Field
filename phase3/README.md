# Phase 3: MCMC Parameter Fitting

**Status:** ✅ **COMPLETE** — Chains validated, paper updated

---

## Summary

This directory contains MCMC analysis of the Ridder Field (φCDM) model using Cobaya with Planck, ACT, BAO, and local H₀ priors.

### December 2025 Results

| World | Model | Best χ² | H₀ | Δχ² |
|-------|-------|---------|--------|-----|
| SH0ES + DESI | ΛCDM | 4244.5 | 68.57 ± 0.09 | 0 (ref) |
| SH0ES + DESI | φ-EDE | 4255.3 | 69.82 ± 0.21 | **+10.8** |
| TRGB + DESI | φ-EDE | 4251.6 | 69.71 ± 0.06 | +22.6 |
| DES Y1 | φ-EDE | 4700.7 | 70.54 ± 0.08 | +10.5 |

**Key Finding**: The "geometric tax" of Δχ² ≈ +11 matches the paper's prediction of +10 to +15.

See [`CHAIN_RESULTS_SUMMARY.md`](CHAIN_RESULTS_SUMMARY.md) for complete documentation.

---

## Directory Structure

```
phase3/
├── README.md                    # This file
├── CHAIN_RESULTS_SUMMARY.md     # Full results documentation
│
├── configs/                     # Cobaya YAML configurations
│   ├── ridder_v3_baseline.yaml  # Quick test (no priors)
│   ├── tier4_*.yaml             # Medium precision runs
│   ├── tier5_*.yaml             # Production quality
│   └── act_*.yaml               # ACT DR6 analysis
│
├── chains/                      # MCMC chain outputs
│   ├── tier5_*.1.txt            # Main chain samples
│   ├── tier5_*.covmat           # Covariance matrices
│   └── FINAL_RESULTS.txt        # Summary of best-fits
│
├── figures/                     # Generated plots
├── scripts/                     # Analysis utilities
└── logs/                        # Run logs
```

---

## Quick Start

### Run a Test Chain (~10 min)

```bash
cobaya-run configs/ridder_v3_baseline.yaml -f
```

### Run Production Chain (~24 hr)

```bash
cobaya-run configs/tier5_ede_shoes_desi.yaml -f
```

### Check Running Chains

```bash
./check_chains.sh
```

---

## Key Parameters

The Ridder field model is controlled by:

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| `Lambda_ridder` | Potential steepness | 0.5–2.0 |
| `n_ridder` | Potential power | 3.0 (fixed) |
| `theta_i_ridder` | Initial displacement | 0.75 (fixed) |
| `beta_ridder` | DM coupling | 0.0 (fixed) |

---

## Configuration Tiers

| Tier | Likelihoods | Samples | Purpose |
|------|-------------|---------|---------|
| 3 | Planck lite | ~1000 | Smoke test |
| 4 | Planck + BAO | ~2000 | Validation |
| 5 | Full Planck + BAO + local H₀ | ~5000 | Publication |
| 6 | + ACT DR6 | ~5000 | Damping tail |

---

## Analysis Scripts

| Script | Purpose |
|--------|---------|
| `tier5_status.py` | Extract best-fits from chains |
| `generate_paper_plots.py` | Create publication figures |
| `plot_geometric_ceiling.py` | H₀ profile likelihood |
| `act_template_fit.py` | Soft shoulder amplitude |

---

## Likelihoods Used

- **CMB**: Planck 2018 (TT, TE, EE, low-ℓ, lensing)
- **ACT**: DR6 mflike (for damping tail)
- **BAO**: SDSS DR12, 6dF, MGS, DESI Y1
- **H₀ Priors**: SH0ES (73.04 ± 1.04), TRGB (69.8 ± 1.7)
- **Weak Lensing**: DES Y1 (for S₈)

---

## Results Archive

All production chains from the December 2025 runs are preserved:

```bash
# Main results
chains/tier5_lcdm_shoes_desi.1.txt
chains/tier5_ede_shoes_desi.1.txt

# H₀ profile scans
chains/tier5_ede_shoes_desi_h0_fixed_69.1.txt
chains/tier5_ede_shoes_desi_h0_fixed_70.1.txt
# ... etc.
```

---

## Contact

For questions about the MCMC analysis:
- **Email**: sridder@post.harvard.edu
- **Issues**: [GitHub Issues](https://github.com/StevenRidder/Ridder-Field/issues)
