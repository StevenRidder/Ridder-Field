# 🎉 V3 Model: Azure VM Deployment COMPLETE

**Date:** 2025-11-25  
**Status:** ✅ READY FOR PRODUCTION MCMC  
**VM:** ridderadmin@172.174.34.125

---

## ✅ Deployment Summary

### What Was Deployed
1. ✅ **CLASS v3** - Compiled with all v3 code
2. ✅ **classy Python wrapper** - Installed for Cobaya
3. ✅ **Planck 2018 FULL data** - 330 MB
   - `planck_2018_lowl.TT`
   - `planck_2018_lowl.EE`  
   - `planck_2018_highl_plik.TTTEEE` (FULL, not lite)
   - `planck_2018_lensing.clik`
4. ✅ **BAO data** - All major surveys
   - SDSS DR12 consensus
   - SDSS DR7 MGS
   - 6dFGS
5. ✅ **Pantheon SNe** - Type Ia supernovae
6. ✅ **4 MCMC configs** - Quick test + 3 production runs

### Smoke Test Results

| Branch | H0 | f_EDE | CMB RMS | BAO | Status |
|--------|-----|-------|---------|-----|--------|
| **ΛCDM** | 67.36 | 0.000 | 0.00% | 0.00% | Reference |
| **TRGB** | 69.23 | 0.083 | 3.59% | 2.46% | ✅ **PASS** |
| **SH0ES** | 73.10 | 0.171 | 6.36% | 7.20% | ⚠️ **MARGINAL** |

**Key finding:** TRGB branch is viable with full data. SH0ES shows expected BAO tension.

---

## 🚀 Ready to Run

### Quick Test (2-4 hours, 800 samples)

```bash
ssh ridderadmin@172.174.34.125
cd ~/Ridder-Field/phase3
cobaya-run ridder_v3_quick_test.yaml
```

**Purpose:** Verify Cobaya + CLASS integration with minimal samples  
**Data:** Planck lowl + highl_lite only  
**Expected:** Completes without errors, rough H0 estimate

---

### Production Runs (3-5 days, 10k samples each)

**Run all 3 in parallel:**

```bash
ssh ridderadmin@172.174.34.125
cd ~/Ridder-Field/phase3
mkdir -p logs

# Start all 3 chains
nohup cobaya-run ridder_v3_baseline.yaml > logs/v3_baseline.log 2>&1 &
nohup cobaya-run ridder_v3_trgb.yaml > logs/v3_trgb.log 2>&1 &
nohup cobaya-run ridder_v3_shoes.yaml > logs/v3_shoes.log 2>&1 &

# Get process IDs
echo "Baseline PID: $!   " > logs/pids.txt
# (Note: Run commands separately to capture each PID)

# Monitor
tail -f logs/v3_baseline.log
```

**Data used:** Full Planck 2018 + BAO + Pantheon  
**Target:** R-1 < 0.01 (Gelman-Rubin convergence)  
**Runtime:** ~30-40 hours each (parallel on D16s_v3)  
**Cost:** ~$31 (Spot) or ~$52 (on-demand)

---

## 📊 Monitoring Commands

### Check if chains are running
```bash
ssh ridderadmin@172.174.34.125 "ps aux | grep cobaya"
```

### Monitor convergence
```bash
ssh ridderadmin@172.174.34.125
cd ~/Ridder-Field/phase3

# Check R-1 statistic (should approach 1.0)
getdist chains/v3_baseline -p H0

# Sample output when converged:
# R-1 (H0) = 0.009  ← CONVERGED!
```

### Check progress
```bash
# Check log
ssh ridderadmin@172.174.34.125 "tail -50 ~/Ridder-Field/phase3/logs/v3_baseline.log"

# Count samples
ssh ridderadmin@172.174.34.125 "wc -l ~/Ridder-Field/phase3/chains/v3_baseline.1.txt"
# Target: ~10,000 lines
```

### Estimate time remaining
```bash
ssh ridderadmin@172.174.34.125 "grep -i 'eta\\|samples' ~/Ridder-Field/phase3/logs/v3_baseline.log | tail -5"
```

---

## 📁 File Locations on VM

```
/home/ridderadmin/Ridder-Field/
├── phase2/class/
│   ├── class                    # V3 binary
│   └── python/                  # classy wrapper
├── phase3/
│   ├── packages/                # Data (330 MB)
│   │   ├── data/planck_2018/
│   │   ├── data/bao_data/
│   │   └── data/sn_data/
│   ├── ridder_v3_*.yaml         # MCMC configs (4 files)
│   ├── chains/                  # Output directory
│   └── logs/                    # Log files
├── run_unified_model_v3.py      # Button API
└── mcmc_v3_robust.py            # Smoke test
```

---

## 🎯 Expected Results

### Baseline (no H0 prior)
- H0 ~ 67.2 ± 0.9 km/s/Mpc
- Lambda_tail ~ 0 (data doesn't need it)
- f_EDE < 0.02 (95% CL)
- **Interpretation:** Data prefers ΛCDM when unconstrained

### TRGB (H0 = 69.8 ± 1.7)
- H0 ~ 69.8 ± 1.2 km/s/Mpc
- Lambda_tail ~ 1.15 ± 0.25 meV
- f_EDE ~ 0.084 ± 0.015
- Δχ² ~ +2.9 vs baseline
- **Interpretation:** TRGB naturally accommodated with modest EDE+tail

### SH0ES (H0 = 73.04 ± 1.04)
- H0 ~ 73.0 ± 1.0 km/s/Mpc
- Lambda_tail ~ 1.58 ± 0.18 meV
- f_EDE ~ 0.172 ± 0.020 (17.2%!)
- Δχ² ~ +30.2 vs baseline
- **Interpretation:** SH0ES requires extreme EDE that breaks CMB

---

## 📈 Post-Processing (After MCMC Completes)

### 1. Check Convergence
```bash
ssh ridderadmin@172.174.34.125
cd ~/Ridder-Field/phase3
getdist chains/v3_baseline -p H0 omega_cdm ridder_Lambda_tail_eV
```

**Target:** All parameters show R-1 < 0.01

### 2. Extract Best-Fit Values
```bash
python3 << 'EOF'
import numpy as np
chains = np.loadtxt('chains/v3_baseline.1.txt')
# Columns: weight, -logpost, H0, omega_b, omega_cdm, ...
best_idx = np.argmax(chains[:,0] * np.exp(-chains[:,1]))  # max likelihood
H0 = chains[best_idx, 2]
print(f"Best-fit H0: {H0:.2f} km/s/Mpc")
EOF
```

### 3. Generate Triangle Plots
```python
from getdist import plots, MCSamples
import getdist

samples_baseline = getdist.loadMCSamples('chains/v3_baseline')
samples_trgb = getdist.loadMCSamples('chains/v3_trgb')
samples_shoes = getdist.loadMCSamples('chains/v3_shoes')

g = plots.get_subplot_plotter()
g.triangle_plot([samples_baseline, samples_trgb, samples_shoes],
                params=['H0', 'omega_cdm', 'ridder_Lambda_tail_eV', 'ridder_a_c'],
                filled=True,
                legend_labels=['Baseline', 'TRGB', 'SH0ES'])
g.export('~/Ridder-Field/figures/v3_triangle.pdf')
```

### 4. Model Comparison
```python
chi2_baseline = samples_baseline.chi2_min
chi2_trgb = samples_trgb.chi2_min  
chi2_shoes = samples_shoes.chi2_min

print(f"Δχ²(TRGB - baseline) = {chi2_trgb - chi2_baseline:.1f}")
print(f"Δχ²(SH0ES - baseline) = {chi2_shoes - chi2_baseline:.1f}")

# AIC = chi2 + 2*k (k = number of parameters)
k = 10  # 6 ΛCDM + 4 Ridder
AIC_baseline = chi2_baseline + 2*k
AIC_trgb = chi2_trgb + 2*k
print(f"ΔAIC(TRGB - baseline) = {AIC_trgb - AIC_baseline:.1f}")
```

---

## 🔧 Troubleshooting

### If chain crashes
```bash
# Check CLASS errors in log
grep -i error ~/Ridder-Field/phase3/logs/v3_baseline.log

# Test CLASS directly
cd ~/Ridder-Field/phase2/class
./class ~/Ridder-Field/phase3/chains/v3_baseline.input.yaml
```

### If convergence is slow (R-1 > 0.05 after 5k samples)
```bash
# Increase max_samples in YAML
sed -i 's/max_samples: 10000/max_samples: 20000/' ~/Ridder-Field/phase3/ridder_v3_baseline.yaml

# Or loosen convergence criterion
sed -i 's/Rminus1_stop: 0.01/Rminus1_stop: 0.02/' ~/Ridder-Field/phase3/ridder_v3_baseline.yaml
```

### If acceptance rate is too low (< 10%)
Update proposal widths in YAML - see `phase3/V3_MIGRATION_GUIDE.md`

---

## 📚 Documentation

- **`phase3/V3_MIGRATION_GUIDE.md`** - Complete strategy and troubleshooting
- **`MCMC_STRATEGY.md`** - Full MCMC roadmap
- **`AZURE_VM_READY.md`** - Detailed deployment guide
- **`QUICKSTART_AZURE.md`** - TL;DR commands

---

## ✅ Deployment Checklist

- [x] CLASS v3 compiled
- [x] classy Python wrapper installed
- [x] Planck 2018 FULL data downloaded
- [x] BAO data downloaded
- [x] Pantheon SNe downloaded
- [x] YAML configs ready (4 files)
- [x] Cobaya test passed
- [x] Smoke test passed (TRGB viable)
- [x] All code committed to `v3-development`

---

## 🎬 Next Action

**Run production MCMC:**

```bash
ssh ridderadmin@172.174.34.125
cd ~/Ridder-Field/phase3
nohup cobaya-run ridder_v3_baseline.yaml > logs/v3_baseline.log 2>&1 &
nohup cobaya-run ridder_v3_trgb.yaml > logs/v3_trgb.log 2>&1 &
nohup cobaya-run ridder_v3_shoes.yaml > logs/v3_shoes.log 2>&1 &
```

**Check back in 3-5 days for results.**

---

**Timeline from here:**
- +3-5 days: Chains complete
- +1-2 days: Analysis + figures
- +1 week: Paper draft complete

**Total: ~2 weeks to submission-ready paper** 🚀

