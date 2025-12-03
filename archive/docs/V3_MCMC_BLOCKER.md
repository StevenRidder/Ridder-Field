# V3 MCMC BLOCKER - Session End Status
**Date:** 2025-11-25  
**Status:** BLOCKED - Critical Bug in CLASS Parameter Reading

## What We Accomplished Today

### ✅ Fixed Bugs
1. **ridder_f_eV:** Was 1e26, fixed to 1.0 in all YAMLs
2. **CLASS path:** Changed from `/home/azureuser` to `/home/ridderadmin` in all YAMLs  
3. **Baseline ref values:** Set to near-zero (0.001, 0.00001) for valid LCDM-like starting point
4. **V3 EDE derivatives:** Added missing `S(a)` time window to `dV_EDE_dtheta_v3` and `d2V_EDE_dtheta2_v3`
5. **Azure VM setup:** Successfully rebuilt CLASS, installed classy wrapper, downloaded all Planck/BAO/Pantheon data

### ⚠️ Current Blocker

**CLASS is not reading Lambda values from Cobaya/INI files properly.**

**Evidence:**
```
# Cobaya passes these parameters:
ridder_Lambda_EDE_eV: 0.321
ridder_Lambda_tail_eV: 0.0012

# But CLASS debug output shows:
DEBUG: Ridder field DISABLED. Lambda = 0.000000e+00
```

**Symptoms:**
- With `Lambda_EDE_eV = 1e-10` (effectively zero): CLASS completes in <10 seconds ✅
- With `Lambda_EDE_eV = 0.01` or higher: CLASS hangs in infinite loop (99.9% CPU) ❌
- All Cobaya test runs fail with "null likelihood"

## Root Cause Analysis

The issue is in the CLASS C code parameter reading (`input.c`). When Cobaya/INI passes `ridder_Lambda_EDE_eV` and `ridder_Lambda_tail_eV`, CLASS is either:
1. Not reading them correctly
2. Not setting them in the `ridder_unified_params` struct
3. Setting them but then zeroing them out somewhere

The debug print "Lambda = 0.000000e+00" comes from `background.c` and shows the field is being disabled even when it shouldn't be.

## Next Steps (For Next Session)

### 1. Diagnose Parameter Flow
```bash
# Add debug prints in input.c to trace:
printf("INPUT.C: Read ridder_Lambda_EDE_eV = %.3e\n", pba->ridder_unified.Lambda_EDE_eV);
printf("INPUT.C: Read ridder_Lambda_tail_eV = %.3e\n", pba->ridder_unified.Lambda_tail_eV);

# Add debug prints in background.c to confirm values:
printf("BACKGROUND.C: Lambda_EDE_eV = %.3e\n", pba->ridder_unified.Lambda_EDE_eV);
printf("BACKGROUND.C: Lambda_tail_eV = %.3e\n", pba->ridder_unified.Lambda_tail_eV);
```

### 2. Check input.c Parsing
Look for where `ridder_Lambda_EDE_eV` and `ridder_Lambda_tail_eV` are read:
- File: `/Users/steveridder/Git/Ridder-Field/phase2/class/source/input.c`
- Search for: `class_read_double("ridder_Lambda_EDE_eV"`
- Verify the values are being written to the correct struct fields

### 3. Once Parameter Reading is Fixed
Then we can:
- Start all 3 production MCMC runs (baseline, TRGB, SH0ES)
- Use `check_v3_status.py` to monitor progress
- Runs should take 3-5 days for 10K samples per chain

## Files Ready for Production

### YAML Configs (All Fixed)
- `phase3/ridder_v3_baseline.yaml` - 10K samples, no H0 prior
- `phase3/ridder_v3_trgb.yaml` - 10K samples, H0 = 69.8 ± 1.7
- `phase3/ridder_v3_shoes.yaml` - 10K samples, H0 = 73.0 ± 1.0
- `phase3/ridder_v3_quick_test.yaml` - 100 samples for testing

### Monitoring Scripts
- `check_v3_status.py` - Real-time chain monitoring
- `start_v3_production.sh` - Launch all 3 runs

### VM Status
- **Location:** ridderadmin@172.174.34.125
- **CLASS:** Compiled with v3 fixes
- **Data:** All Planck 2018, BAO, Pantheon downloaded
- **classy:** Python wrapper installed

## Command to Resume

Once the Lambda reading bug is fixed:

```bash
# On VM:
cd ~/Ridder-Field/phase3
nohup cobaya-run ridder_v3_baseline.yaml > logs/v3_baseline.log 2>&1 &
nohup cobaya-run ridder_v3_trgb.yaml > logs/v3_trgb.log 2>&1 &
nohup cobaya-run ridder_v3_shoes.yaml > logs/v3_shoes.log 2>&1 &

# Monitor from local:
python3 check_v3_status.py
```

## Summary

**We're 95% there.** All infrastructure is in place, all major bugs are fixed except one critical parameter reading bug that's causing Lambda values to be zero when they shouldn't be. Fix that one issue and the MCMC runs can start immediately.

