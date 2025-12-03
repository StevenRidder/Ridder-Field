# Pre-Publication Optimization Suite

Scripts and configs for squeezing the last few χ² points out of the model.

## Contents

- `profile_scan.py` - 1D profile scans for n_ridder and sigma_ln_a
- `chi2_breakdown.py` - Decompose χ² by likelihood component  
- `run_optimization.sh` - Shell script to run the full optimization pipeline

## Optimized Configs

All configs include:
- Tighter integration tolerances: `tol_background: 1e-4`, `tol_perturb: 1e-8`
- Higher CMB multipoles: `l_max_scalars: 3500`
- More k-modes: `k_per_decade_for_bao: 200`, `k_per_decade_for_pk: 20`
- Better MCMC settings: `oversample_power: 0.3`, `Rminus1_stop: 0.01`

### SH0ES Pre-DESI World (Main paper world)
- `optimized_ede_shoes_predesi.yaml` - EDE model
- `optimized_lcdm_shoes_predesi.yaml` - ΛCDM baseline

### SH0ES + DESI World (Geometry tax world)
- `optimized_ede_shoes_desi.yaml` - EDE with DESI Y1 BAO
- `optimized_lcdm_shoes_desi.yaml` - ΛCDM with DESI Y1 BAO

### Growth World (S8 test)
- `optimized_ede_growth.yaml` - EDE with DES Y1 weak lensing
- `optimized_lcdm_growth.yaml` - ΛCDM with DES Y1 weak lensing

### Best-fit Refinement
- `bestfit_refine_ede.yaml` - Local minimizer (bobyqa) around best MCMC sample

## Expected Gains

| Optimization | Expected Δχ² |
|-------------|--------------|
| Tighter tolerances | -2 to -5 |
| Optimal n_ridder | -3 to -5 |
| Optimal σ_ln_a | -2 to -4 |
| Best-fit refinement | -2 to -5 |
| **Total** | **-9 to -19** |

## Usage

```bash
# After current chains finish (~overnight):

# 1. Run profile scans to find optimal shape params
python optimization/profile_scan.py --param n_ridder
python optimization/profile_scan.py --param sigma_ln_a

# 2. Run optimized production chains
cobaya-run optimization/configs/optimized_ede_shoes_predesi.yaml &
cobaya-run optimization/configs/optimized_lcdm_shoes_predesi.yaml &

# 3. After chains converge, do best-fit refinement
# Update refs in bestfit_refine_ede.yaml with best sample, then:
cobaya-run optimization/configs/bestfit_refine_ede.yaml
```

## Planck Nuisances

Note: Planck nuisance parameters are handled automatically by Cobaya's Planck likelihood.
They are sampled with default priors. Both EDE and ΛCDM configs use identical likelihood 
blocks to ensure fair Δχ² comparisons.
