# V2 Production Deployment Guide

**Date**: November 23, 2025  
**Status**: Ready to Deploy  
**Strategy**: Dual VM Parallel Production

---

## Executive Summary

**Smoke Test Results:** ✅ **PASSED**
- 43 samples completed without crashes
- H₀ = 68.17 ± 0.37 km/s/Mpc (elevated above Planck)
- χ² = 2784.6 (good fit)
- Speed: 3.6 sec/CLASS evaluation (acceptable)

**Next Step:** Deploy production MCMC to both VMs simultaneously

---

## Deployment Architecture

### **Australia VM (172.174.34.125)**
- **Configuration:** Tier 3 (Planck + BAO + SH0ES)
- **Goal:** Test if V2 can resolve H₀ tension with SH0ES prior
- **Samples:** 10,000 per chain
- **Runtime:** ~10 hours

### **US East VM (<VM_IP>)**
- **Configuration:** Tier 4 (Planck + BAO + Pantheon SN)
- **Goal:** Test V2 with distance ladder (SNe) instead of direct H₀ prior
- **Samples:** 10,000 per chain
- **Runtime:** ~10 hours

**Why both?**
- Tier 3 (SH0ES): Direct H₀ constraint → tests if V2 can reconcile Planck + SH0ES
- Tier 4 (Pantheon): Indirect H₀ via luminosity distance → independent check

---

## Files Created

### **Configuration Files**
1. `phase3/ridder_v2_tier3_production.yaml` (Australia)
   - Planck + BAO + SH0ES
   - 10,000 samples
   - Ref values from smoke test

2. `phase3/ridder_v2_tier4_production.yaml` (US East)
   - Planck + BAO + Pantheon SN
   - 10,000 samples
   - Ref values from smoke test

### **Deployment Scripts**
1. `phase3/scripts/deploy_v2_to_vm.sh` (single VM)
   - Usage: `./deploy_v2_to_vm.sh <VM_USER>@<IP>`
   - Handles compilation, patching, symlinks

2. `phase3/scripts/deploy_v2_production.sh` (both VMs)
   - Master script for dual deployment
   - Runs both VMs in sequence
   - Checks if classy already installed (skips recompilation)

### **Documentation**
1. `V2_COMPILATION_GUIDE.md`
   - Complete reference for why compilation fails
   - 3 root causes + solutions
   - One-liner fix for quick repairs

2. `V2_PRODUCTION_DEPLOYMENT.md` (this file)
   - Deployment architecture
   - Step-by-step instructions
   - Monitoring and troubleshooting

---

## Deployment Instructions

### **Option A: Automated Deployment (Recommended)**

```bash
cd /Users/steveridder/Git/Ridder-Field

# Deploy to both VMs
./phase3/scripts/deploy_v2_production.sh
```

This will:
1. Sync V2 code to both VMs
2. Check if classy is installed
3. Compile if needed (or skip if already installed)
4. Create symlinks and copy data
5. Test imports
6. Print launch commands

**ETA:** 5-10 minutes (or 2 minutes if classy already installed)

---

### **Option B: Manual Deployment (Step-by-Step)**

#### **Step 1: Deploy to Australia VM**

```bash
cd /Users/steveridder/Git/Ridder-Field

# Sync code
rsync -avz --exclude='*.o' --exclude='*.a' \
    phase2/class/ <VM_USER>@172.174.34.125:~/Ridder-Field/phase2/class/

rsync -avz phase3/ridder_v2_tier3_production.yaml \
    <VM_USER>@172.174.34.125:~/Ridder-Field/phase3/

# SSH to VM
ssh <VM_USER>@172.174.34.125

# Compile (if not already done)
cd ~/Ridder-Field/phase2/class
make clean && make -j8

cd python
python3 -m Cython.Build.Cythonize classy.pyx
python3 setup.py install --user

# Create symlink (if not already done)
CLASSY_PATH=$(python3 -c 'import classy; print(classy.__file__)' | xargs dirname)
sudo ln -sf "$CLASSY_PATH" /classy
sudo cp -r ~/Ridder-Field/phase2/class/external /classy/

# Set environment
echo 'export CLASS_DATA_PATH=/classy' >> ~/.bashrc
export CLASS_DATA_PATH=/classy

# Test
python3 -c 'from classy import Class; print("✓ Success")'
```

#### **Step 2: Deploy to US East VM**

Repeat Step 1, but:
- Replace IP: `172.174.34.125` → `<VM_IP>`
- Replace config: `ridder_v2_tier3_production.yaml` → `ridder_v2_tier4_production.yaml`

---

## Launch Instructions

### **Australia VM (Tier 3)**

```bash
ssh <VM_USER>@172.174.34.125

cd ~/Ridder-Field/phase3
export CLASS_DATA_PATH=/classy

# Launch in background
nohup python3 -m cobaya.run ridder_v2_tier3_production.yaml > tier3_prod.log 2>&1 &

# Check it started
tail -f tier3_prod.log
# Press Ctrl+C to exit tail
```

### **US East VM (Tier 4)**

```bash
ssh <VM_USER>@<VM_IP>

cd ~/Ridder-Field/phase3
export CLASS_DATA_PATH=/classy

# Launch in background
nohup python3 -m cobaya.run ridder_v2_tier4_production.yaml > tier4_prod.log 2>&1 &

# Check it started
tail -f tier4_prod.log
# Press Ctrl+C to exit tail
```

---

## Monitoring

### **Quick Status Check**

```bash
# Australia VM (Tier 3)
ssh <VM_USER>@172.174.34.125 "
    cd ~/Ridder-Field/phase3/chains
    SAMPLES=\$(wc -l < ridder_v2_tier3_prod.1.txt)
    echo \"Tier 3: \$((SAMPLES - 1)) / 10000 samples\"
    tail -3 ridder_v2_tier3_prod.1.txt | awk '{printf \"  H0=%.2f  Lambda=%.3f  theta=%.3f  beta=%.4f\\n\", \$5, \$9, \$10, \$11}'
"

# US East VM (Tier 4)
ssh <VM_USER>@<VM_IP> "
    cd ~/Ridder-Field/phase3/chains
    SAMPLES=\$(wc -l < ridder_v2_tier4_prod.1.txt)
    echo \"Tier 4: \$((SAMPLES - 1)) / 10000 samples\"
    tail -3 ridder_v2_tier4_prod.1.txt | awk '{printf \"  H0=%.2f  Lambda=%.3f  theta=%.3f  beta=%.4f\\n\", \$5, \$9, \$10, \$11}'
"
```

### **Detailed Status (Adapt v2_smoke_status.sh)**

Create `phase3/scripts/v2_production_status.sh`:

```bash
#!/bin/bash
# Monitor both VMs
echo "=== AUSTRALIA VM (TIER 3) ==="
ssh <VM_USER>@172.174.34.125 "cd ~/Ridder-Field/phase3 && [status commands]"

echo ""
echo "=== US EAST VM (TIER 4) ==="
ssh <VM_USER>@<VM_IP> "cd ~/Ridder-Field/phase3 && [status commands]"
```

---

## Expected Timeline

| Time | Event |
|------|-------|
| T+0h | Launch both VMs |
| T+1h | ~360 samples each (burn-in phase) |
| T+5h | ~1800 samples each (halfway) |
| T+10h | ~3600 samples each (converging) |
| T+12h | 10,000 samples complete |

**Total runtime:** ~12 hours (overnight)

---

## Success Criteria

### **Convergence**
- R-1 < 0.01 (Gelman-Rubin statistic)
- Acceptance rate: 20-40%
- No crashes or NaNs

### **Physics**
- **Tier 3 (SH0ES):**
  - H₀ posterior should peak near 70-73 km/s/Mpc
  - χ² should not increase dramatically vs Planck-only
  
- **Tier 4 (Pantheon):**
  - H₀ should be consistent with Tier 3 (within 1σ)
  - Provides independent check without direct H₀ prior

### **Comparison**
- If Tier 3 and Tier 4 agree → V2 is robust
- If they disagree → investigate systematics

---

## Troubleshooting

### **"TypeError: 'classy' is not a package"**
→ See `V2_COMPILATION_GUIDE.md`, Section: Issue 2

### **"buffer overflow detected"**
→ See `V2_COMPILATION_GUIDE.md`, Section: Issue 3

### **"Class did not read input parameter(s)"**
→ Check YAML parameter names match CLASS expectations:
- `Lambda_EDE_ridder` (not `Lambda_ridder`)
- `theta_i_ridder` (not `theta_ridder`)
- `beta_ridder` (not `beta0_ridder`)

### **"Newtonian gauge required"**
→ Already set in YAML: `gauge: newtonian`

### **MCMC stuck at 0 samples**
→ Check log for initialization errors:
```bash
ssh <VM> "tail -50 ~/Ridder-Field/phase3/tier*_prod.log"
```

---

## Post-Run Analysis

Once both runs complete:

1. **Download chains:**
   ```bash
   rsync -avz <VM_USER>@172.174.34.125:~/Ridder-Field/phase3/chains/ridder_v2_tier3_prod* ./results/tier3/
   rsync -avz <VM_USER>@<VM_IP>:~/Ridder-Field/phase3/chains/ridder_v2_tier4_prod* ./results/tier4/
   ```

2. **Generate corner plots:**
   ```bash
   python3 phase3/scripts/generate_plots.py results/tier3/ridder_v2_tier3_prod
   python3 phase3/scripts/generate_plots.py results/tier4/ridder_v2_tier4_prod
   ```

3. **Compare posteriors:**
   - H₀: Tier 3 vs Tier 4
   - Lambda_EDE: Tier 3 vs Tier 4
   - theta_i: Tier 3 vs Tier 4
   - beta: Tier 3 vs Tier 4

4. **Compute tension metrics:**
   - ΔH₀ (Planck vs SH0ES)
   - Δχ² (V2 vs ΛCDM)
   - Evidence ratio (Bayes factor)

---

## Quick Reference

### **VM IPs**
- Australia: `172.174.34.125`
- US East: `<VM_IP>`

### **Key Files**
- Tier 3 config: `phase3/ridder_v2_tier3_production.yaml`
- Tier 4 config: `phase3/ridder_v2_tier4_production.yaml`
- Deployment script: `phase3/scripts/deploy_v2_production.sh`
- Compilation guide: `V2_COMPILATION_GUIDE.md`

### **Key Commands**
```bash
# Deploy
./phase3/scripts/deploy_v2_production.sh

# Launch (Australia)
ssh <VM_USER>@172.174.34.125 "cd ~/Ridder-Field/phase3 && export CLASS_DATA_PATH=/classy && nohup python3 -m cobaya.run ridder_v2_tier3_production.yaml > tier3_prod.log 2>&1 &"

# Launch (US East)
ssh <VM_USER>@<VM_IP> "cd ~/Ridder-Field/phase3 && export CLASS_DATA_PATH=/classy && nohup python3 -m cobaya.run ridder_v2_tier4_production.yaml > tier4_prod.log 2>&1 &"

# Monitor
ssh <VM_USER>@172.174.34.125 "tail -f ~/Ridder-Field/phase3/tier3_prod.log"
ssh <VM_USER>@<VM_IP> "tail -f ~/Ridder-Field/phase3/tier4_prod.log"
```

---

## Summary

**Ready to deploy:** ✅  
**Estimated time:** 10-15 minutes deployment + 12 hours runtime  
**Expected output:** 20,000 total samples (10k × 2 VMs)  
**Next milestone:** H₀ posterior from V2 with full Planck + distance ladder

**Run the deployment script when ready:**
```bash
./phase3/scripts/deploy_v2_production.sh
```

