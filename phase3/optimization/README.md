# Pre-Publication Optimization Suite

This directory contains scripts for squeezing additional χ² improvement before final publication.

## Quick Start

```bash
# 1. Run profile scans (finds optimal n_ridder, sigma_ln_a)
python profile_scan.py --param n_ridder --range 2.5 3.5 --steps 5

# 2. Run χ² breakdown diagnostic
python chi2_breakdown.py --chain chains/tier5_ede_shoes_predesi.1.txt

# 3. Run best-fit refinement
cobaya-run configs/optimized_bestfit_refine.yaml
```

## Expected Gains

| Optimization | Expected Δχ² |
|-------------|--------------|
| Tighter tolerances | -2 to -5 |
| Optimal n_ridder | -3 to -5 |
| Optimal σ_ln_a | -2 to -4 |
| Best-fit refinement | -2 to -5 |
| **Total** | **-9 to -19** |

## Files

- `profile_scan.py` - 1D profile likelihood scans
- `chi2_breakdown.py` - Decompose χ² by dataset
- `configs/optimized_*.yaml` - Configs with tighter tolerances
