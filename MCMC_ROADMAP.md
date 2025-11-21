# MCMC Roadmap: From Local Test to Full Cluster Run

**Date:** November 21, 2024  
**Status:** Ready to begin Phase 1 (Local Test)

---

## Overview

We'll proceed in **3 phases**, starting small and scaling up:

```
Phase 1: Local Mac Test (5-10 minutes)
   ↓
Phase 2: Azure Single Machine (30-60 minutes)
   ↓
Phase 3: Azure Cluster (Full MCMC, hours-days)
```

---

## Phase 1: Local Mac Test ⚡ **START HERE**

### Purpose
- Verify MCMC infrastructure works
- Test CLASS integration with Cobaya
- Explore small parameter space
- **NO Planck data needed** (just technical test)

### What It Does
- Samples `theta_i ∈ [2.0, 2.2]` and `beta ∈ [0.005, 0.015]`
- Runs ~500 CLASS evaluations
- Computes r_s for each parameter combination
- Uses simple Gaussian likelihood on r_s (target: 139.06 Mpc)

### How to Run

```bash
cd /Users/steveridder/Git/Ridder-Field/phase3
python3 run_local_mcmc_test.py
```

**Expected Runtime:** 5-10 minutes on Mac

**Expected Output:**
```
✓ Cobaya version: 3.3.2
✓ CLASS executable: /Users/steveridder/Git/Ridder-Field/phase2/class/class
✓ Parameter file: ridder_local_test.yaml
✓ Output directory: chains/

Starting MCMC test...
...
✅ MCMC TEST COMPLETED!

Samples collected: 500
Mean parameter values:
  theta_i_ridder: 2.1000 ± 0.0200
  beta_ridder: 0.0100 ± 0.0020
```

### Success Criteria
- ✅ MCMC runs without crashes
- ✅ CLASS evaluates successfully for each parameter set
- ✅ Chains are saved to `chains/ridder_local_test*`
- ✅ Mean values are reasonable (theta_i ≈ 2.1, beta ≈ 0.01)

### If It Fails
1. **Cobaya not installed:**
   ```bash
   pip3 install cobaya
   ```

2. **CLASS not compiled:**
   ```bash
   cd /Users/steveridder/Git/Ridder-Field/phase2/class
   make clean && make class
   ```

3. **Other errors:**
   - Check error message
   - Verify paths in `ridder_local_test.yaml`
   - Run CLASS manually to test: `./class ../../phase3/ridder_smoketest_spec.ini`

---

## Phase 2: Azure Single Machine Test

### Purpose
- Test Azure deployment
- Run longer chains (more samples)
- Verify cloud infrastructure
- Still no full Planck data (use simplified likelihood)

### Prerequisites
- ✅ Phase 1 completed successfully
- Azure account with credits
- SSH access to Azure VM

### Setup Steps

1. **Create Azure VM**
   ```bash
   # Use existing script
   cd /Users/steveridder/Git/Ridder-Field/phase3
   bash azure_deploy.sh --single-vm
   ```

2. **Copy Code to Azure**
   ```bash
   # SSH into VM
   ssh ridder@<azure-ip>
   
   # Clone repo
   git clone https://github.com/StevenRidder/Ridder-Field.git
   cd Ridder-Field
   
   # Compile CLASS
   cd phase2/class
   make clean && make class
   cd ../../phase3
   ```

3. **Run Test**
   ```bash
   # Install dependencies
   pip3 install cobaya getdist
   
   # Run longer test (5000 samples)
   python3 run_local_mcmc_test.py
   ```

### Success Criteria
- ✅ Azure VM accessible
- ✅ Code compiles on Azure
- ✅ MCMC runs for 5000+ samples
- ✅ Convergence R-1 < 0.05

### Expected Runtime
30-60 minutes (depending on VM size)

---

## Phase 3: Full MCMC with Planck Data

### Purpose
- **PRODUCTION RUN**
- Full parameter space exploration
- Real Planck 2018 likelihoods
- Multi-chain convergence
- Publication-quality results

### Prerequisites
- ✅ Phase 2 completed successfully
- Azure cluster (4-8 VMs recommended)
- Planck 2018 data downloaded (~10 GB)

### Configuration

**Parameters to Sample:**
- `theta_i_ridder ∈ [1.8, 2.15]`
- `beta_ridder ∈ [0.0, 0.03]`
- `omega_b, omega_cdm, A_s, n_s, tau_reio` (standard 6)
- **Total: 8 parameters**

**Likelihoods:**
- Planck 2018 TT+TE+EE+lowE
- BAO (SDSS, 6dF)
- Supernovae (Pantheon)

**Chains:**
- 4-8 independent chains
- ~100,000 samples per chain
- Convergence: R-1 < 0.01

### Setup Steps

1. **Create Azure Cluster**
   ```bash
   cd /Users/steveridder/Git/Ridder-Field/phase3
   bash azure_deploy.sh --cluster --nodes 8
   ```

2. **Download Planck Data** (on each node)
   ```bash
   # This downloads ~10 GB
   cobaya-install ridder_mcmc.yaml -p ./packages
   ```

3. **Configure MPI**
   ```bash
   # Update ridder_mcmc.yaml with correct paths
   # Set output directory
   # Configure MPI settings
   ```

4. **Launch MCMC**
   ```bash
   # Run on cluster
   mpirun -n 32 python3 -m cobaya run ridder_mcmc.yaml
   ```

### Expected Runtime
- **Optimistic:** 24-48 hours (with 8 VMs, 4 cores each)
- **Realistic:** 3-5 days
- **Pessimistic:** 1 week (if convergence is slow)

### Monitoring

```bash
# Check convergence
python3 -c "from getdist import loadMCSamples; s=loadMCSamples('chains/ridder_mcmc'); print(f'R-1: {s.getGelmanRubin()}')"

# Plot chains (on local machine after downloading)
python3 plot_chains.py
```

### Success Criteria
- ✅ All chains converge (R-1 < 0.01)
- ✅ Effective sample size > 1000 per parameter
- ✅ Posteriors are well-constrained
- ✅ Best-fit χ² comparable to ΛCDM

---

## Cost Estimates

### Phase 1: Local Mac
- **Cost:** $0 (runs on your Mac)
- **Time:** 5-10 minutes

### Phase 2: Azure Single VM
- **VM:** Standard_D4s_v3 (4 vCPUs, 16 GB RAM)
- **Cost:** ~$0.20/hour × 1 hour = **$0.20**
- **Time:** 30-60 minutes

### Phase 3: Azure Cluster
- **VMs:** 8× Standard_D8s_v3 (8 vCPUs, 32 GB RAM each)
- **Cost:** ~$0.40/hour × 8 VMs × 48 hours = **$153.60**
- **Time:** 2-5 days
- **Storage:** ~50 GB for chains and data = **$2.50/month**

**Total Estimated Cost:** ~$160 for full MCMC run

---

## Decision Points

### After Phase 1
**If successful:**
- ✅ Proceed to Phase 2 (Azure single VM test)

**If failed:**
- ⚠️ Debug locally before spending on Azure
- Check CLASS compilation
- Verify Cobaya installation
- Test CLASS manually

### After Phase 2
**If successful:**
- ✅ Proceed to Phase 3 (full cluster)
- Download Planck data
- Set up cluster

**If failed:**
- ⚠️ Debug Azure setup
- Check network/firewall
- Verify MPI configuration
- Test with smaller parameter space

### During Phase 3
**Monitor convergence every 12 hours:**
- If R-1 dropping: ✅ Continue
- If R-1 stuck > 0.05: ⚠️ Investigate
  - Check for multimodality
  - Adjust proposal widths
  - Increase burn-in
- If R-1 < 0.01: ✅ **SUCCESS!**

---

## Files Created

### For Phase 1 (Local Test)
- ✅ `ridder_local_test.yaml` - Minimal MCMC config
- ✅ `run_local_mcmc_test.py` - Test script

### For Phase 2 (Azure Single VM)
- Reuse Phase 1 files
- Modify for longer chains

### For Phase 3 (Full MCMC)
- ✅ `ridder_mcmc.yaml` - Production config (already exists)
- ✅ `run_mcmc.py` - Production script (already exists)
- ✅ `azure_deploy.sh` - Cluster deployment (already exists)

---

## Current Status

**Phase 1:** ✅ **READY TO RUN**
- Cobaya installed (v3.3.2)
- CLASS compiled
- Test scripts created
- Configuration files ready

**Phase 2:** 🟡 **READY AFTER PHASE 1**
- Azure deployment script exists
- Need to test on single VM

**Phase 3:** 🟡 **READY AFTER PHASE 2**
- Production config exists
- Need to download Planck data
- Need to set up cluster

---

## Next Steps

### Immediate (NOW)
1. **Run Phase 1 local test:**
   ```bash
   cd /Users/steveridder/Git/Ridder-Field/phase3
   python3 run_local_mcmc_test.py
   ```

2. **If successful, review results:**
   ```bash
   ls -lh chains/ridder_local_test*
   python3 -c "from getdist import loadMCSamples; s=loadMCSamples('chains/ridder_local_test'); print(s)"
   ```

### After Phase 1 Success
3. **Deploy to Azure single VM**
4. **Run longer test (5000 samples)**
5. **Verify convergence**

### After Phase 2 Success
6. **Set up Azure cluster**
7. **Download Planck data**
8. **Launch full MCMC**
9. **Monitor convergence**
10. **Analyze results**
11. **Write paper!** 🎉

---

## Emergency Contacts

**If stuck:**
- Check `TROUBLESHOOTING.md` (to be created)
- Review Cobaya docs: https://cobaya.readthedocs.io
- Check CLASS docs: https://lesgourg.github.io/class_public/class.html

**Azure Issues:**
- Azure support portal
- Check billing/credits

**Physics Questions:**
- Review `COSMOLOGIST_AUDIT_REPORT.md`
- Check `SMOKE_TEST_RESULTS.md`

---

## Success Metrics

### Phase 1
- ✅ MCMC runs without errors
- ✅ ~500 samples collected
- ✅ Mean values reasonable

### Phase 2
- ✅ Azure VM accessible
- ✅ ~5000 samples collected
- ✅ R-1 < 0.05

### Phase 3
- ✅ All chains converge (R-1 < 0.01)
- ✅ ESS > 1000 per parameter
- ✅ Posteriors well-constrained
- ✅ Best-fit model matches data

---

**Ready to start Phase 1?** Run:
```bash
cd /Users/steveridder/Git/Ridder-Field/phase3
python3 run_local_mcmc_test.py
```

**Good luck!** 🚀

