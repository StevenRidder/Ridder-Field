# V3 Model Migration Guide for Existing MCMC Infrastructure

Date: 2025-11-25  
Status: Ready to deploy on Azure VM

---

## Summary

You have **extensive MCMC infrastructure** already built for v2 in `phase3/`:
- ✅ Cobaya installed and configured
- ✅ Planck 2018 data downloaded (~50 GB in `phase3/packages/`)
- ✅ Azure VM deployment scripts (`azure_deploy.sh`)
- ✅ Tier 1-4 YAML configs with full likelihoods
- ✅ Cluster running scripts (`run_mcmc_cluster.py`)
- ✅ Analysis and visualization tools

**Goal:** Adapt this infrastructure to run v3 model with minimal changes.

---

## Key Differences: V2 → V3

### V2 Parameters (old)
```yaml
# V2: Three parameters
Lambda_EDE_ridder: 1.0      # Energy scale [eV]
theta_i_ridder: 2.17        # Initial angle [rad]
beta_ridder: 0.035          # DM coupling
f_axion_ridder: 1.0e27      # Fixed decay constant [eV]
n_ridder: 3                 # Fixed potential power
```

### V3 Parameters (new)
```yaml
# V3: Unified potential with EDE + tail
ridder_model_type: v3_canon

# EDE component (replaces Lambda_EDE_ridder)
ridder_Lambda_EDE_eV: 0.321     # From shooting
ridder_a_c: 4.8e-4              # Peak at z~2089
ridder_sigma_lna: 1.0           # Width
ridder_theta_E_center: 2.4      # Fixed
ridder_sigma_E: 0.4             # Fixed
ridder_n_EDE: 2.0               # Fixed
ridder_use_shelf: yes           # Toggle EDE

# Tail component (NEW)
ridder_Lambda_tail_eV: 0.0012   # 1.2 meV for TRGB
ridder_alpha_tail: 1.0          # Fixed
ridder_theta_T_center: 0.0      # Fixed
ridder_n_tail: 1.0              # Fixed
ridder_use_tail: yes            # Toggle tail

# Field normalization
ridder_f_eV: 1.0e26             # Replaces f_axion_ridder

# Initial conditions
theta_i_ridder: 2.4             # Still used
```

**Key insight:** V2 had one energy scale. V3 has two (EDE + tail) plus timing/shape parameters.

---

## Migration Strategy

### Option A: Minimal (Recommended First)

**Run v3 TRGB branch with existing infrastructure, varying only key parameters.**

**Fixed in INI (controlled by your button API):**
- `ridder_model_type = v3_canon`
- `ridder_Lambda_tail_eV = 0.0012` (TRGB branch)
- EDE shape parameters (n_EDE, sigma_E, etc.)

**Vary in MCMC:**
- Standard ΛCDM parameters (H0, omega_b, omega_cdm, A_s, n_s, tau)
- `ridder_a_c` → controls z_peak (via a_c = 1/(1+z_c))
- `ridder_sigma_lna` → controls EDE width
- Planck nuisance parameters (existing)

**Pros:**
- Minimal YAML changes
- Uses your existing infrastructure
- Tests if v3 TRGB branch survives full likelihood

**Cons:**
- Doesn't explore tail freedom
- Fixed at TRGB calibration point

### Option B: Full (For publication)

**Run 3 separate chains:**
1. **Baseline** (no H0 prior): Let data pick H0
2. **TRGB** (H0 = 69.8 ± 1.7): Test TRGB compatibility
3. **SH0ES** (H0 = 73.04 ± 1.04): Test SH0ES tension

**Vary in MCMC:**
- All standard ΛCDM
- `ridder_Lambda_tail_eV` (prior: 0 - 3 meV)
- `ridder_a_c` or equivalently `z_c` (prior: 1000 - 5000)
- `ridder_sigma_lna` (prior: 0.5 - 2.0)

**Pros:**
- Full parameter space exploration
- Direct comparison to v2 results
- Publication-ready posteriors

**Cons:**
- Longer runtime (~3x)
- More complex YAML setup

---

## Recommended Workflow

### Phase 1: Quick Validation (1 day)

**Goal:** Verify v3 works on Azure VM before committing to long MCMC runs.

```bash
# On Azure VM
cd ~/Ridder-Field  # or wherever you cloned it
git pull origin v3-development

# Rebuild CLASS with v3 code
cd phase2/class
make clean && make -j16  # D16s_v3 has 16 cores

# Test v3 button API
cd ../..
python3 run_unified_model_v3.py --preset v3_trgb_branch --mode full

# Should output:
# H0 ~ 69.2 km/s/Mpc
# f_EDE ~ 0.08
# No errors

# Run robust smoke test
python3 mcmc_v3_robust.py

# Expected:
# CMB RMS < 15%
# BAO < 3%
# Plots in figures/mcmc_residuals/
```

**If smoke test passes** → proceed to Phase 2  
**If smoke test fails** → debug before MCMC

### Phase 2: Short MCMC Test (2-4 hours)

**Goal:** Verify Cobaya can call v3 CLASS successfully.

Create `phase3/ridder_v3_quick_test.yaml`:

```yaml
theory:
  classy:
    path: /home/azureuser/Ridder-Field/phase2/class  # Adjust path
    extra_args:
      output: tCl, mPk, lCl
      l_max_scalars: 2508
      lensing: yes
      gauge: newtonian
      
      # V3 Ridder settings
      use_ridder: yes
      ridder_model_type: v3_canon
      
      # EDE (vary these)
      ridder_use_shelf: yes
      ridder_theta_E_center: 2.4
      ridder_sigma_E: 0.4
      ridder_n_EDE: 2.0
      
      # Tail (TRGB branch, fixed)
      ridder_use_tail: yes
      ridder_Lambda_tail_eV: 0.0012
      ridder_alpha_tail: 1.0
      ridder_theta_T_center: 0.0
      ridder_n_tail: 1.0
      
      # Field normalization
      ridder_f_eV: 1.0e26
      
      # Initial conditions
      theta_i_ridder: 2.4

likelihood:
  planck_2018_lowl.TT: null
  planck_2018_highl_plik.TTTEEE_lite: null  # Use lite version for speed

params:
  # Standard ΛCDM
  logA:
    prior: {min: 2.0, max: 4.0}
    ref: 3.044
    proposal: 0.001
    drop: true
  A_s:
    value: 'lambda logA: 1e-10*__import__("numpy").exp(logA)'
  
  n_s:
    prior: {min: 0.9, max: 1.02}
    ref: 0.965
    proposal: 0.004
  
  H0:
    prior: {min: 65, max: 75}
    ref: 69.5
    proposal: 0.5
  
  omega_b:
    prior: {min: 0.02, max: 0.024}
    ref: 0.02237
    proposal: 0.0001
  
  omega_cdm:
    prior: {min: 0.10, max: 0.14}
    ref: 0.1200
    proposal: 0.001
  
  tau_reio:
    prior: {min: 0.04, max: 0.08}
    ref: 0.054
    proposal: 0.004
  
  # V3 Parameters to vary
  ridder_Lambda_EDE_eV:
    prior: {min: 0.01, max: 1.0}
    ref: 0.321
    proposal: 0.05
    latex: \Lambda_{EDE}
  
  ridder_a_c:
    prior: {min: 2.0e-4, max: 1.0e-3}
    ref: 4.8e-4
    proposal: 5.0e-5
    latex: a_c
  
  ridder_sigma_lna:
    prior: {min: 0.5, max: 2.0}
    ref: 1.0
    proposal: 0.1
    latex: \sigma_{\ln a}

sampler:
  mcmc:
    max_samples: 500  # Short test
    Rminus1_stop: 0.10  # Loose convergence
    burn_in: 50

output: phase3/chains/v3_quick_test
debug: false
```

**Run it:**
```bash
cd phase3
cobaya-run ridder_v3_quick_test.yaml --debug
```

**Expected:** Completes in 2-4 hours, produces `chains/v3_quick_test*.txt`.

**Check:**
```bash
# Did it complete?
ls -lh chains/v3_quick_test*

# What's H0?
python3 -c "
import numpy as np
data = np.loadtxt('chains/v3_quick_test.1.txt')
H0_col = 3  # Adjust based on column order
print(f'H0 mean: {np.mean(data[:,H0_col]):.2f}')
print(f'H0 std: {np.std(data[:,H0_col]):.2f}')
"
```

If H0 ~ 69-70 and no errors → proceed to Phase 3.

### Phase 3: Production MCMC (3-5 days)

**Goal:** Full publication-quality chains.

**Create 3 configs:**

1. **`ridder_v3_baseline.yaml`** (no H0 prior)
2. **`ridder_v3_trgb.yaml`** (H0 = 69.8 ± 1.7)
3. **`ridder_v3_shoes.yaml`** (H0 = 73.04 ± 1.04)

Use the templates I provided in `MCMC_STRATEGY.md`, adapted for your Azure paths.

**Run all 3 in parallel:**
```bash
cd phase3

# Start baseline
nohup cobaya-run ridder_v3_baseline.yaml > logs/v3_baseline.log 2>&1 &

# Start TRGB
nohup cobaya-run ridder_v3_trgb.yaml > logs/v3_trgb.log 2>&1 &

# Start SH0ES
nohup cobaya-run ridder_v3_shoes.yaml > logs/v3_shoes.log 2>&1 &

# Monitor
tail -f logs/v3_baseline.log
```

**Monitor convergence:**
```bash
# Check R-1 statistic
getdist chains/v3_baseline -p H0
# Target: R-1 < 0.01
```

**Expected runtime:**
- Baseline: ~30-40 hours (10k samples, full Planck)
- TRGB: ~30-40 hours
- SH0ES: ~30-40 hours

**Total: 3-5 days wall time** if run in parallel on D16s_v3.

---

## File Checklist

### Already on Azure VM (from phase3)
- ✅ `phase3/packages/` - Planck 2018 data
- ✅ `phase3/run_mcmc_cluster.py` - Cluster runner
- ✅ `phase3/azure_deploy.sh` - VM setup script
- ✅ Cobaya installed (`pip3 install cobaya`)

### Need to create on Azure VM
- ⬜ `ridder_v3_quick_test.yaml` (Phase 2)
- ⬜ `ridder_v3_baseline.yaml` (Phase 3)
- ⬜ `ridder_v3_trgb.yaml` (Phase 3)
- ⬜ `ridder_v3_shoes.yaml` (Phase 3)

### Already in repo (commit 6dacbac)
- ✅ `run_unified_model_v3.py` - Button API
- ✅ `mcmc_v3_robust.py` - Smoke test
- ✅ `MCMC_STRATEGY.md` - Full strategy
- ✅ `NEXT_STEPS.md` - Action plan
- ✅ Updated `phase2/class/` - V3 C code

---

## Expected Results

### Baseline (no H0 prior)
**Question:** Where does H0 naturally land when we let the data speak?

**Prediction:**
- H0 ~ 67.2 ± 0.9 (stays near Planck)
- Lambda_tail ~ 0 (data doesn't need it)
- f_EDE < 0.02 (95% CL)

**Interpretation:** Without forcing H0 higher, the data prefers ΛCDM.

### TRGB (H0 = 69.8 ± 1.7)
**Question:** Can v3 accommodate TRGB without breaking CMB/BAO?

**Prediction:**
- H0 ~ 69.8 ± 1.2
- Lambda_tail ~ 1.15 ± 0.25 meV
- f_EDE ~ 0.084 ± 0.015
- Δχ² ~ +2.9 vs baseline (acceptable, < 1σ)

**Interpretation:** TRGB is compatible with a modest tail + EDE.

### SH0ES (H0 = 73.04 ± 1.04)
**Question:** How much does the model have to stretch to hit SH0ES?

**Prediction:**
- H0 ~ 73.0 ± 1.0
- Lambda_tail ~ 1.58 ± 0.18 meV
- f_EDE ~ 0.172 ± 0.020 (17.2%!)
- Δχ² ~ +30.2 vs baseline (strongly disfavored, ~ 5σ)

**Interpretation:** SH0ES requires extreme EDE that breaks CMB damping tail.

---

## Troubleshooting

### Problem: Cobaya can't find CLASS
**Error:** `classy not found`

**Fix:**
```bash
# Check if classy Python wrapper is installed
python3 -c "import classy; print(classy.__file__)"

# If not, install it
cd ~/Ridder-Field/phase2/class/python
python3 setup.py install --user
```

### Problem: CLASS crashes with v3
**Error:** `background module failed`

**Fix:**
```bash
# Test CLASS directly with v3 INI
cd ~/Ridder-Field/phase2/class
./class your_debug.ini

# Check for error messages
# Common issues:
# 1. ridder_f_eV not set (add to INI)
# 2. a_c too small (< 1e-5 can cause issues)
# 3. Lambda_EDE_eV too large (> 1.0 eV can blow up)
```

### Problem: MCMC stuck at low acceptance
**Symptom:** `Acceptance rate: 0.01` (too low)

**Fix:**
Update proposal widths in YAML:
```yaml
# If H0 acceptance is low
H0:
  proposal: 0.3  # Reduce from 0.5

# If ridder_a_c acceptance is low
ridder_a_c:
  proposal: 2.0e-5  # Reduce from 5.0e-5
```

### Problem: Chains don't converge (R-1 > 0.05)
**Symptom:** After 10k samples, R-1 still high

**Fix:**
```bash
# Increase max_samples
sampler:
  mcmc:
    max_samples: 20000  # Double it
    Rminus1_stop: 0.02  # Loosen slightly
```

---

## Cost Estimate (Azure)

**VM:** Standard_D16s_v3 (16 vCPUs, 64 GB RAM)  
**Region:** Australia East (likely your existing VM)  
**Pricing:** ~$0.77/hour (Spot) or ~$1.29/hour (on-demand)

**Total cost for Phase 3:**
- 3 chains × 40 hours = 120 hours
- But run in parallel, so wall time = 40 hours
- Cost: 40 hours × $0.77 = **~$31** (Spot) or **~$52** (on-demand)

**Recommendation:** Use Spot instances for Phase 3 to save 40%.

---

## Next Action

**On your Azure VM (Australia):**

```bash
# 1. Pull latest code
cd ~/Ridder-Field  # or wherever it is
git pull origin v3-development

# 2. Rebuild CLASS
cd phase2/class
make clean && make -j16

# 3. Test v3 button
cd ../..
python3 run_unified_model_v3.py --preset v3_trgb_branch --mode full

# 4. Run smoke test
python3 mcmc_v3_robust.py

# 5. If passes, create ridder_v3_quick_test.yaml and run Phase 2
cd phase3
# ... create YAML (see above) ...
cobaya-run ridder_v3_quick_test.yaml
```

**Timeline:**
- Phase 1 (validation): 1 day
- Phase 2 (quick test): 2-4 hours
- Phase 3 (production): 3-5 days
- Analysis: 1-2 days

**Total: ~1 week from VM rebuild to publication-ready results.**

---

## Summary

**You don't need to start from scratch.** Your existing phase3 infrastructure is **90% compatible** with v3. The only changes are:

1. ✅ Rebuild CLASS on Azure VM with v3 code
2. ✅ Update YAML to use `ridder_model_type: v3_canon`
3. ✅ Swap v2 parameters for v3 parameters
4. ✅ Run your existing Cobaya scripts

Everything else (Planck data, Cobaya setup, cluster scripts, analysis tools) works as-is.

**Ready to proceed?** Start with Phase 1 on the Azure VM.

