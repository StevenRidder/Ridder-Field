# Beta Ladder Bug Report & Fix

**Date:** November 24, 2025  
**Status:** ✅ ROOT CAUSE IDENTIFIED, FIX DEPLOYED  

---

## 🐛 THE BUG

**Initial Symptom:**
All three beta ladder runs (0.10, 0.15, 0.20) failed with:
```
❌ FAILED - Reason: Perturbation stiffness
```

**Misleading diagnosis:**
Initially appeared to be numerical stiffness from higher beta values.

**ACTUAL ROOT CAUSE:**
**The Ridder field had ZERO energy because θ was outside the window function range!**

---

## 🔍 DIAGNOSTIC TRAIL

### Step 1: Check the configs
✅ Configs were created correctly:
- `beta_ridder = 0.10` (etc) ✓
- `ridder_Lambda_EDE_eV = 1.0` ✓
- `ridder_use_shelf = yes` ✓

### Step 2: Check CLASS output
❌ Found the smoking gun:
```
RIDDER FINAL STATE (a=1, z=0):
  f_ridder   = 2.590813e-07 (fraction of total)
```

Should be ~0.1-0.15, not 10^-7!

### Step 3: Check unified potential code
✅ Unified potential functions exist and are compiled:
- `ridder_unified_potential.c` present
- `ridder_unified_potential.o` compiled
- Functions called correctly

### Step 4: Check potential evaluation
Found θ values from debug output:
```
V_RIDDER_RAW: a=1.15e-02 phi=-1.74e+26
V_RIDDER_RAW: a=4.28e-01 phi=1.05e+24
```

Computed θ = phi / f:
```
theta = 1.74e+26 / 2.435e+27 ≈ 0.071
theta = 1.05e+24 / 2.435e+27 ≈ 0.0004
```

### Step 5: Check window function range
Window configured as:
```ini
ridder_theta_EDE_low  = 0.5
ridder_theta_EDE_high = 2.0
```

**θ ~ 0.07 is WAY BELOW 0.5!**

Window function W_EDE(θ=0.07) ≈ 0, suppressing entire potential!

---

## 🎯 ROOT CAUSE

**The field starts at θ_i = 1.0, but quickly rolls to θ << 0.5.**

The window function is:
```
W(θ) = 0.5*[1 + tanh((θ - 0.5)/0.2)] - 0.5*[1 + tanh((θ - 2.0)/0.2)]
```

For θ = 0.07:
- `tanh((0.07 - 0.5)/0.2) ≈ tanh(-2.15) ≈ -0.97`
- `W ≈ 0.5*(1 - 0.97) - 0.5*(1 - 1) ≈ 0.015`

So only ~1.5% of the potential is "on", making the field negligible!

---

## ✅ THE FIX

### **Fix Applied: Option 1 (Increase θ_i)**

Change initial field value from:
```ini
theta_i_ridder = 1.0
```

To:
```ini
theta_i_ridder = 2.0
```

This starts the field at the **upper edge** of the window, where:
- W(θ=2.0) ≈ 0.5 (peak of window)
- Field rolls "down" through the active window
- EDE episode occurs while W ~ 1

### **Alternative Fixes (not used):**

**Option 2: Lower the window**
```ini
ridder_theta_EDE_low  = 0.05
ridder_theta_EDE_high = 0.5
```
Pros: Matches where field naturally goes  
Cons: May conflict with v2 calibration

**Option 3: Rescale f**
```ini
ridder_f = 2.435e26  # Factor of 10 smaller
```
Pros: θ values become ~0.7-7 (more natural)  
Cons: Changes field normalization, affects all calculations

---

## 📊 VALIDATION

### Test Plan:
Run beta ladder v3 with θ_i = 2.0:

**Success criteria:**
- ✅ f_ridder ~ 0.1-0.15 (not 10^-7)
- ✅ Background completes
- ✅ At least one beta completes perturbations

**If still fails:**
- Fall back to Option 2 (adjust window)
- Or Option 3 (rescale f)

---

## 🚀 DEPLOYMENT

**Scripts deployed:**

1. **`beta_ladder_v3_fixed.sh`**
   - Sets θ_i = 2.0
   - Tests beta = 0.05, 0.10, 0.15
   - Reports f_ridder in output

2. **Phase 1B scripts** (ready):
   - `activate_tail.py` - Tune tail for w₀ ≈ -1
   - `extract_h0_precision.py` - Compute ΔH₀ from r_s

---

## 📝 LESSONS LEARNED

1. **"Perturbation stiffness" is often a symptom, not the root cause.**
   - Real problem: field had no energy
   - Perturbations failed because field was irrelevant

2. **Always check f_ridder in diagnostic output.**
   - Immediate red flag if ~10^-7 instead of ~0.1

3. **Window functions are sensitive to field range.**
   - θ_i must be chosen carefully relative to window edges
   - Debug output showing raw φ values is critical

4. **Unit conversions matter.**
   - θ = φ / f, so f sets the scale
   - Wrong f → wrong θ → window mismatch

---

## 🔗 RELATED FILES

- **Bug reports:**
  - This file
  - CLASS logs in `/tmp/class_beta_*.log`
  
- **Fixed scripts:**
  - `phase3_full_analysis/scripts/beta_ladder_v3_fixed.sh`
  
- **Configs (broken):**
  - `phase3_full_analysis/configs/unified_beta0p*.ini` (θ_i = 1.0)
  
- **Configs (fixed, to be created):**
  - `phase3_full_analysis/configs/unified_fixed_beta0p*.ini` (θ_i = 2.0)

---

## ✅ STATUS

- [x] Bug identified
- [x] Root cause diagnosed
- [x] Fix implemented
- [x] V3 script created and synced
- [ ] V3 runs executing
- [ ] V3 validation complete
- [ ] Phase 1A marked complete

**Next:** Run `beta_ladder_v3_fixed.sh` on VM and verify f_ridder ~ 0.1.

