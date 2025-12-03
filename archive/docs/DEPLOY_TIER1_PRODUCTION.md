# Tier 1 Production Deployment Guide

## Overview
Deploy the V1 publication-quality Tier 1 run on the Australia VM:
- **8 Ridder field chains** (5000 samples each)
- **2 ΛCDM baseline chains** (5000 samples each)
- **Total**: 50,000 samples for robust statistics
- **Runtime**: 24-36 hours on F8s_v2 (8 vCPU)

## Pre-Deployment Checklist

### 1. Verify Australia VM is Running
```bash
# From local machine
ssh ridderadmin@<AUSTRALIA_VM_IP> "uptime && free -h && df -h"
```

### 2. Sync Latest Code
```bash
# On Australia VM
cd ~/Ridder-Field
git pull origin main
```

### 3. Verify CLASS Compilation
```bash
# On Australia VM
cd ~/Ridder-Field/phase2/class
./class --version

# Should show CLASS version and Ridder modifications
# If not, recompile:
make clean
make -j8
cd python
python3 setup.py install --user
```

### 4. Verify Planck Data
```bash
# On Australia VM
ls -lh ~/.local/share/cobaya/data/planck_2018/

# Should show:
# - baseline/
# - lensing/
# - low_l/
# - high_l/
```

## Deployment Steps

### Step 1: Launch Production Run
```bash
# On Australia VM
cd ~/Ridder-Field/phase3/scripts
./run_tier1_production.sh
```

**Expected output:**
```
==========================================
TIER 1 PRODUCTION RUN - V1 PUBLICATION
==========================================
Target: 5000 samples per chain
Ridder chains: 8
ΛCDM baseline: 2
Total chains: 10
Estimated runtime: 24-36 hours
==========================================

Cleaning previous production chains...

Launching 8 Ridder field chains...
  Chain 1: PID 12345 in .../ridder_prod_chain1_work
  Chain 2: PID 12346 in .../ridder_prod_chain2_work
  ...
  Chain 8: PID 12352 in .../ridder_prod_chain8_work

Launching 2 ΛCDM baseline chains...
  ΛCDM Chain 1: PID 12353 in .../lcdm_prod_chain1_work
  ΛCDM Chain 2: PID 12354 in .../lcdm_prod_chain2_work

==========================================
All 10 chains launched successfully!
==========================================
```

### Step 2: Verify All Chains Started
```bash
# Check running processes
ps aux | grep cobaya-run | wc -l
# Should show: 10

# Check log files
ls -lh ~/Ridder-Field/phase3/chains/*_work/*.log
```

### Step 3: Monitor Progress
```bash
# Run status script
cd ~/Ridder-Field/phase3/scripts
./tier1_production_status.sh
```

**Expected output (after ~1 hour):**
```
============================================================
TIER 1 PRODUCTION STATUS - V1 PUBLICATION
Target: 5000 samples per chain | 8 Ridder + 2 ΛCDM
============================================================

RIDDER FIELD CHAINS:
------------------------------------------------------------
[Ridder-1] 150/5000 | θᵢ=2.087 | β=0.0023 | H0=67.82 | χ²=2761.3 (best: 2758.1)
[Ridder-2] 148/5000 | θᵢ=2.105 | β=0.0019 | H0=67.91 | χ²=2762.8 (best: 2759.4)
[Ridder-3] 152/5000 | θᵢ=2.093 | β=0.0027 | H0=67.75 | χ²=2760.5 (best: 2757.8)
...

ΛCDM BASELINE CHAINS:
------------------------------------------------------------
[ΛCDM-1] 145/5000 | H0=67.34 | χ²=2765.2 (best: 2763.1)
[ΛCDM-2] 147/5000 | H0=67.41 | χ²=2766.0 (best: 2764.3)

============================================================
TOTAL PROGRESS: 1492 / 50000 samples (3.0%)
============================================================
```

### Step 4: Set Up Auto-Monitoring (Optional)
```bash
# Watch status every 60 seconds
watch -n 60 ./tier1_production_status.sh

# Or run in tmux/screen for persistent session
tmux new -s tier1_monitor
./tier1_production_status.sh
# Ctrl+B, D to detach
```

## Monitoring from Local Machine

### SSH and Check Status
```bash
# From your laptop
ssh ridderadmin@<AUSTRALIA_VM_IP> "cd ~/Ridder-Field/phase3/scripts && ./tier1_production_status.sh"
```

### Check Individual Chain Logs
```bash
# Ridder chain 1
ssh ridderadmin@<AUSTRALIA_VM_IP> "tail -n 50 ~/Ridder-Field/phase3/chains/ridder_prod_chain1_work/ridder_chain1.log"

# ΛCDM chain 1
ssh ridderadmin@<AUSTRALIA_VM_IP> "tail -n 50 ~/Ridder-Field/phase3/chains/lcdm_prod_chain1_work/lcdm_chain1.log"
```

## Expected Timeline

| Time | Progress | Status |
|------|----------|--------|
| 0h | 0% | All chains initializing |
| 1h | 3-5% | Burn-in phase, high chi2 |
| 6h | 15-20% | Parameters converging |
| 12h | 35-45% | Stable sampling |
| 24h | 70-85% | Nearing completion |
| 36h | 100% | All chains complete |

## What to Watch For

### Good Signs ✅
- All 10 chains running (check with `ps aux | grep cobaya`)
- Sample counts increasing steadily
- θᵢ values staying in range 1.5-2.3 (not drifting to 0.5)
- β values exploring 0.0-0.03 range
- χ² decreasing over time (especially in first 500 samples)
- Ridder χ² comparable to or better than ΛCDM χ²

### Warning Signs ⚠️
- Chains crashing (fewer than 10 cobaya processes)
- θᵢ drifting rapidly to 0.5 (Ridder field turning off)
- χ² stuck at high values (>3000) after 1000 samples
- Log files showing CLASS errors

### Critical Issues 🚨
- All chains stopped (check disk space: `df -h`)
- CLASS errors about "use_scf" not recognized (recompile needed)
- Memory errors (check with `free -h`)

## Troubleshooting

### Chain Crashed
```bash
# Find which chain
ps aux | grep cobaya-run

# Check its log
tail -n 100 ~/Ridder-Field/phase3/chains/ridder_prod_chain<N>_work/ridder_chain<N>.log

# Restart just that chain
cd ~/Ridder-Field/phase3/chains/ridder_prod_chain<N>_work
nohup cobaya-run config.yaml --force > ridder_chain<N>.log 2>&1 &
```

### Out of Disk Space
```bash
# Check usage
df -h

# Clean old test chains
rm -rf ~/Ridder-Field/phase3/chains/*test*
rm -rf ~/Ridder-Field/phase3/chains/chain*_work  # Old test runs
```

### CLASS Errors
```bash
# Recompile CLASS
cd ~/Ridder-Field/phase2/class
make clean
make -j8
cd python
python3 setup.py install --user

# Restart failed chains (see above)
```

## Post-Completion

### Step 1: Verify All Chains Complete
```bash
cd ~/Ridder-Field/phase3/scripts
./tier1_production_status.sh

# Should show all chains at 5000/5000 samples
```

### Step 2: Copy Chains to Local Machine
```bash
# From local machine
scp ridderadmin@<AUSTRALIA_VM_IP>:~/Ridder-Field/phase3/chains/ridder_tier1_production_chain*.txt \
    ~/Git/Ridder-Field/phase3/chains/

scp ridderadmin@<AUSTRALIA_VM_IP>:~/Ridder-Field/phase3/chains/lcdm_production_chain*.txt \
    ~/Git/Ridder-Field/phase3/chains/
```

### Step 3: Run Visualization
```bash
# On local machine
cd ~/Git/Ridder-Field/phase3
python3 visualize_tier1_production.py
```

### Step 4: Commit Results
```bash
cd ~/Git/Ridder-Field
git add phase3/chains/ridder_tier1_production_chain*.txt
git add phase3/chains/lcdm_production_chain*.txt
git commit -m "Add Tier 1 production chains (5000 samples, 8+2 chains)"
git push
```

## Cost Estimate

**Australia VM (F8s_v2):**
- Hourly rate: ~$0.16/hour
- 36 hours runtime: ~$5.76
- Monthly if left running: ~$115/month

**Recommendation:** Stop VM after chains complete to save costs.

## Next Steps After Tier 1

1. **Analyze results** (GetDist, corner plots, R-1 convergence)
2. **Compare Ridder vs ΛCDM** (Bayesian evidence, chi2 improvement)
3. **Write up Tier 1 results** for paper
4. **Deploy Tier 3** (Planck + SH0ES) on Australia VM
5. **Deploy Tier 4** (Full dataset) on Australia VM
6. **Start V2 development** on US East VM

---

**Status**: Ready to deploy
**Last updated**: 2024-11-22

