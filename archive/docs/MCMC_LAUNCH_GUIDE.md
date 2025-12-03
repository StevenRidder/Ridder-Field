# MCMC LAUNCH GUIDE (Phase 3)

You are ready to race for the Nobel.

## 1. Prerequisites
Ensure dependencies are installed:
```bash
cd phase3
bash install_deps.sh
```

## 2. Install Planck Data
You need the Planck 2018 likelihood files (several GBs).
Run this command and follow prompts:
```bash
cobaya-install ridder_field.yaml -p ./packages
```
*This will download data to a `packages` folder.*

## 3. Run the Chains
Start the MCMC run:
```bash
export OMP_NUM_THREADS=4
python3 run_mcmc.py
```
*Or use MPI for cluster runs:*
```bash
mpirun -n 4 python3 -m cobaya run ridder_field.yaml
```

## 4. Victory Check
Monitor the `chains/` directory.
When `R-1 < 0.05`, the chain has converged.
Plot the posteriors using `getdist`.

**Good Luck.**

