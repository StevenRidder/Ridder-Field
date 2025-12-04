# Ridder Field: Geometric EDE Analysis

## Paper
"Early Dark Energy and the Geometric Ceiling: Constraints from Planck, ACT DR6, and DESI Y1"

## Contents

- `chains/` - MCMC chains from Cobaya (Tier 4-5 production runs)
- `configs/` - Cobaya YAML configuration files
- `figures/` - All figures from the paper
- `code/` - Analysis scripts (Python)
- `paper.tex` - LaTeX source

## Key Chains

| File | Description |
|------|-------------|
| `tier5_ede_shoes_predesi` | EDE + SH0ES, pre-DESI BAO |
| `tier5_ede_shoes_desi` | EDE + SH0ES + DESI Y1 |
| `tier5_ede_trgb_*` | EDE + TRGB prior |
| `tier5_lcdm_*` | ΛCDM baselines |
| `tier5_ede_shoes_desi_h0_fixed_*` | Fixed-H₀ profile scans |
| `tier5_ede_des_y1` | EDE + DES Y1 weak lensing |

## Requirements

- Python 3.9+
- CLASS (Boltzmann solver, with EDE modifications)
- Cobaya 3.3+
- See `requirements.txt`

## Citation

If you use these data, please cite:
Ridder, S. (2025). Physical Review D.

## License

MIT License
