# Phase 3: MCMC Parameter Fitting

**Goal:** Fit Ridder field model to observational data and test if it resolves Hubble and S8 tensions.

**Status:** 🚧 SETTING UP

---

## Objectives

1. **Fit model to data:**
   - Planck 2018 CMB (TT, TE, EE, low-ℓ)
   - BAO measurements (BOSS, eBOSS)
   - SH0ES H₀ measurement
   - Pantheon+ SNe Ia (optional)

2. **Test if tensions are resolved:**
   - H₀ posterior should peak at ~73 km/s/Mpc (not ~67)
   - S₈ should decrease (if beta > 0)
   - Model should fit CMB data well (Δχ² < 10 vs ΛCDM)

3. **Parameter constraints:**
   - Lambda_EDE: EDE energy scale
   - f_axion: Decay constant
   - theta_i: Initial misalignment angle
   - beta_ridder: DM coupling strength

---

## Tools

### Option 1: MontePython
- **Pros:** Well-documented, widely used, good CLASS integration
- **Cons:** Requires manual setup
- **Install:** `git clone https://github.com/brinckmann/montepython_public.git`

### Option 2: Cobaya
- **Pros:** Modern, actively maintained, better performance
- **Cons:** Steeper learning curve
- **Install:** `pip install cobaya`

**Recommendation:** Start with Cobaya (more modern, better maintained)

---

## Setup Steps

1. Install MCMC sampler (Cobaya or MontePython)
2. Configure CLASS interface
3. Create parameter file for Ridder field model
4. Download observational data (Planck, BAO, SH0ES)
5. Run test chain
6. Analyze results

---

## Victory Conditions

✅ **Success if:**
- H₀ posterior peaks at 72-74 km/s/Mpc
- Δχ² < 10 vs ΛCDM
- Bayes factor > 3 (moderate evidence)
- All parameters well-constrained

❌ **Failure if:**
- H₀ still peaks at ~67 km/s/Mpc
- Model fits worse than ΛCDM
- Parameters unconstrained or unphysical

---

## Files

- `setup_mcmc.sh` - Installation script
- `ridder_field.param` - Parameter file for MCMC
- `run_chains.sh` - Script to run MCMC chains
- `analyze_results.py` - Analysis script
- `chains/` - MCMC chain output directory

---

**Next:** Install Cobaya and set up parameter file

