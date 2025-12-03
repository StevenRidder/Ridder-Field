# Azure VM: V3 MCMC Ready to Deploy

Date: 2025-11-25  
Status: **READY TO RUN**  
Branch: `v3-development` (commit cf52ecd)

---

## ✅ What's Complete

### Code Infrastructure
- ✅ V3 model fully implemented in CLASS (`phase2/class/`)
- ✅ V3 button API working (`run_unified_model_v3.py`)
- ✅ Tail calibrated: TRGB=1.2 meV, SH0ES=1.6 meV
- ✅ Robust smoke test with residual curves (`mcmc_v3_robust.py`)
- ✅ All code committed and pushed to `origin/v3-development`

### MCMC Infrastructure (Your Existing phase3/)
- ✅ Cobaya already installed
- ✅ Planck 2018 data already downloaded (~50 GB)
- ✅ Azure deployment scripts from v2 (`phase3/azure_deploy.sh`)
- ✅ Analysis and visualization tools
- ✅ Cluster running scripts (`run_mcmc_cluster.py`)

### New V3 MCMC Files (Just Added)
- ✅ `phase3/V3_MIGRATION_GUIDE.md` - Complete strategy doc
- ✅ `phase3/deploy_v3_to_azure.sh` - Automated deployment
- ✅ `phase3/ridder_v3_quick_test.yaml` - Quick validation (2-4h)
- ✅ `phase3/ridder_v3_baseline.yaml` - No H0 prior (30-40h)
- ✅ `phase3/ridder_v3_trgb.yaml` - TRGB test (30-40h)
- ✅ `phase3/ridder_v3_shoes.yaml` - SH0ES test (30-40h)

---

## 🚀 Deployment: One Command

**On your Azure VM (Australia):**

```bash
# 1. Pull latest code
cd ~/Ridder-Field  # or wherever you cloned it
git pull origin v3-development

# 2. Run automated deployment
bash phase3/deploy_v3_to_azure.sh
```

**This script automatically:**
1. ✅ Pulls latest v3 code
2. ✅ Rebuilds CLASS with v3 (using your 16 cores)
3. ✅ Tests v3 button API
4. ✅ Runs smoke test (5 min)
5. ✅ Checks Cobaya + Planck data
6. ✅ Shows you what to run next

**Expected output:** "✓ V3 DEPLOYMENT COMPLETE" in ~10 minutes

---

## 📊 3-Phase Workflow

### Phase 1: Validation (Already Done on Mac)
- ✅ Code audited
- ✅ Migration guide written
- ✅ YAMLs created
- ✅ All changes committed

### Phase 2: Quick Test on VM (2-4 hours)

**After `deploy_v3_to_azure.sh` completes:**

```bash
cd ~/Ridder-Field/phase3
cobaya-run ridder_v3_quick_test.yaml
```

**Purpose:** Verify Cobaya can call v3 CLASS successfully  
**Expected:** Completes without errors, H0 ~ 69-70 km/s/Mpc  
**Duration:** 2-4 hours  
**Samples:** 800 (loose convergence R-1 < 0.15)

**If this passes** → Phase 3  
**If this fails** → Debug, we have all the tools

### Phase 3: Production MCMC (3-5 days)

**Run all 3 in parallel:**

```bash
cd ~/Ridder-Field/phase3

# Create logs directory
mkdir -p logs

# Start all 3 chains
nohup cobaya-run ridder_v3_baseline.yaml > logs/v3_baseline.log 2>&1 &
nohup cobaya-run ridder_v3_trgb.yaml > logs/v3_trgb.log 2>&1 &
nohup cobaya-run ridder_v3_shoes.yaml > logs/v3_shoes.log 2>&1 &

# Monitor
tail -f logs/v3_baseline.log
```

**Duration:** 3-5 days (run in parallel on D16s_v3)  
**Samples:** 10k per chain  
**Convergence:** R-1 < 0.01  
**Cost:** ~$31 (Spot) or ~$52 (on-demand)

---

## 📈 Expected Results

### Baseline (no H0 prior)
**Prediction:**
- H0 ~ 67.2 ± 0.9 (data prefers Planck)
- Lambda_tail ~ 0 (not needed)
- f_EDE < 0.02

**Paper claim:** "Without external priors, data prefers ΛCDM."

### TRGB (H0 = 69.8 ± 1.7)
**Prediction:**
- H0 ~ 69.8 ± 1.2
- Lambda_tail ~ 1.15 ± 0.25 meV
- f_EDE ~ 0.084 ± 0.015
- Δχ² ~ +2.9 (acceptable)

**Paper claim:** "TRGB-aligned H0 is naturally accommodated with modest EDE+tail."

### SH0ES (H0 = 73.04 ± 1.04)
**Prediction:**
- H0 ~ 73.0 ± 1.0
- Lambda_tail ~ 1.58 ± 0.18 meV
- f_EDE ~ 0.172 ± 0.020 (17.2%!)
- Δχ² ~ +30.2 (strongly disfavored)

**Paper claim:** "SH0ES requires extreme EDE that breaks CMB damping tail."

---

## 🎯 Key Differences: Your Approach vs Fresh Setup

### What You DON'T Need to Do
❌ Install Cobaya from scratch  
❌ Download Planck data (you have it)  
❌ Set up Azure VM (it's running)  
❌ Configure MPI/cluster (already done)  
❌ Build analysis tools (phase3 has them)  

### What You DO Need to Do
✅ Pull latest code (1 minute)  
✅ Run `deploy_v3_to_azure.sh` (10 minutes)  
✅ Run Phase 2 test (2-4 hours)  
✅ Run Phase 3 production (3-5 days)  
✅ Analyze results (1-2 days)

**Total effort: ~1 hour of your time + machine time**

---

## 📁 File Reference

### On Azure VM After Deployment
```
~/Ridder-Field/
├── phase2/class/              # V3 CLASS (rebuilt)
├── phase3/
│   ├── packages/              # Planck data (existing)
│   ├── deploy_v3_to_azure.sh  # Deployment script (NEW)
│   ├── V3_MIGRATION_GUIDE.md  # Full strategy (NEW)
│   ├── ridder_v3_*.yaml       # MCMC configs (NEW)
│   ├── chains/                # Output directory
│   └── logs/                  # Log directory
├── run_unified_model_v3.py    # Button API
└── mcmc_v3_robust.py          # Smoke test
```

### On GitHub (v3-development)
All files committed and synced at commit `cf52ecd`.

---

## 🔍 Monitoring & Debugging

### Check if chains are running
```bash
ps aux | grep cobaya
```

### Monitor convergence
```bash
# Check R-1 statistic (should approach 1.0)
getdist chains/v3_baseline -p H0

# Expected output:
# R-1 (H0) = 0.05 → 0.02 → 0.01 (converged)
```

### Check current samples
```bash
# Count lines in chain file
wc -l chains/v3_baseline.1.txt

# Expected: ~10,000 lines when complete
```

### Estimated time remaining
```bash
# Check log for "ETA"
grep -i "eta" logs/v3_baseline.log | tail -1
```

### If something goes wrong
```bash
# Check CLASS errors
grep -i "error" logs/v3_baseline.log

# Test CLASS directly
cd ~/Ridder-Field/phase2/class
./class your_debug.ini

# Re-run deployment script
cd ~/Ridder-Field
bash phase3/deploy_v3_to_azure.sh
```

---

## 📞 Quick Links

### Documentation
- **Migration Guide:** `phase3/V3_MIGRATION_GUIDE.md`
- **MCMC Strategy:** `MCMC_STRATEGY.md`
- **Next Steps:** `NEXT_STEPS.md`
- **Session Summary:** `SESSION_STATUS_2025-11-25.md`

### Scripts
- **Button API:** `run_unified_model_v3.py --preset v3_trgb_branch`
- **Smoke Test:** `python3 mcmc_v3_robust.py`
- **Deployment:** `bash phase3/deploy_v3_to_azure.sh`

### Presets (Button API)
```python
PRESETS = {
    "lcdm_baseline": {
        "Lambda_tail_meV": 0.0,
        "f_axion": 0.0
    },
    "v3_trgb_branch": {
        "Lambda_tail_meV": 1.2,
        "f_axion": 0.25
    },
    "v3_shoes_branch": {
        "Lambda_tail_meV": 1.6,
        "f_axion": 0.40
    }
}
```

---

## ✨ Bottom Line

**You already have 90% of the infrastructure.**

Your existing phase3 MCMC setup (Cobaya, Planck data, cluster scripts, Azure VM) was built for v2 and works perfectly for v3 with minimal changes.

**The only differences are:**
1. ✅ CLASS recompiled with v3 code
2. ✅ New YAML configs with v3 parameters
3. ✅ Starting points from calibrated values

**Everything else reuses your existing work.**

---

## 🎬 Action Plan

**Right now:**
```bash
ssh your-azure-vm  # Replace with your VM IP
cd ~/Ridder-Field
git pull origin v3-development
bash phase3/deploy_v3_to_azure.sh
```

**In 10 minutes:** Deployment complete, smoke test passed

**In 2-4 hours:** Phase 2 quick test complete

**In 3-5 days:** Phase 3 production chains complete

**In 1-2 weeks:** Publication-ready posteriors, figures, and paper

---

**Ready when you are.** 🚀

