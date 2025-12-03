# Phase 1A Status: Beta Ladder V6 (Post Bug Fix)

## **Current Status: BLOCKED on Zero Potential Issue**

Date: Nov 24, 2025 17:25 UTC

---

## ✅ **Bugs Fixed (6 total)**

1. ✅ Validation script filename pattern (glob)
2. ✅ Missing `gauge = newtonian` in test configs
3. ✅ Old v2 code in `input.c` reset `has_ridder` (line ~2447)
4. ✅ **CRITICAL:** `background_init()` unconditionally reset `has_ridder` (line 1188)
5. ✅ Test config `theta_i` too small (0.01 → 3.0)
6. ✅ `ridder_freeze_phi = 0` should be `ridder_freeze_phi = no`

**Key achievement:** Unified potential is now **activating correctly** (`has_ridder=1`)

---

## ⚠️ **Current Blocker: Unified Potential Returns V=0**

### Symptom

Beta ladder V6 runs complete in 2-3 seconds with exit code 0, but:
```
dV/dphi=0.000e+00 eV^3
f_ridder = 0.000e+00
```

### Debug Output

```
DEBUG: Ridder model_type = UNIFIED, has_ridder set to TRUE ✓
DEBUG: Unified parameters read successfully:
  f = 2.435000e+27 eV ✓
  use_tail=1, use_shelf=1, use_plateau=0 ✓
  Lambda_EDE = 1.000000e+00 eV ✓
  theta_low = 1.000000e-01, theta_high = 5.000000e+00 ✓

RIDDER IC: phi_ini=2.000e+16 eV
  dV/dphi=0.000e+00 eV^3  ← **ZERO!**
```

### Hypothesis

**The unified potential functions are returning zero even though:**
- `has_ridder = 1` (activated)
- Parameters are read correctly
- φ = 2.0×10¹⁶ eV (corresponds to θ = φ/f = 0.82 rad)
- θ = 0.82 is INSIDE the shelf window [0.1, 5.0]

**Possible causes:**
1. `V_unified_theta()` not being called (still using v2 code path?)
2. Unit conversion issue in `ridder_unified_potential.c`
3. Window function W_EDE(θ=0.82) evaluating to zero
4. Branching logic in `background.c` not switching to unified potential

---

## 📊 **Beta Ladder V6 Results**

Configuration:
- Lambda_EDE = 1.0 eV
- theta_i = 2.0 (θ ≈ 0.82 rad)
- Window: [0.1, 5.0] rad
- Beta scan: 0.05, 0.10, 0.15, 0.20

| Beta | Status | Runtime | Background | CMB | Notes |
|------|--------|---------|------------|-----|-------|
| 0.05 | ✓ | 2s | ✓ | ✗ | V=0, no EDE |
| 0.10 | ✓ | 3s | ✓ | ✗ | V=0, no EDE |
| 0.15 | ✓ | 2s | ✓ | ✗ | V=0, no EDE |
| 0.20 | ✓ | 3s | ✓ | ✗ | V=0, no EDE |

**All runs:** Field activates but potential is zero → no EDE → no perturbation outputs

---

## 🔍 **Next Debugging Steps**

### Option A: Check if unified potential functions exist in compiled binary

```bash
ssh <VM_USER>@172.174.34.125 '
  cd ~/Ridder-Field/phase2/class && 
  nm class | grep -i "unified\|V_tail\|V_shelf"
'
```

If these symbols don't exist, `ridder_unified_potential.c` wasn't compiled/linked.

### Option B: Add debug output to unified potential functions

Edit `ridder_unified_potential.c`:
```c
double V_tail_theta(double theta, const struct ridder_unified_params *rp) {
  printf("V_TAIL_DEBUG: theta=%e, use_tail=%d, Lambda_tail=%e\n", 
         theta, rp->use_tail, rp->Lambda_tail);
  // ... rest of function
}
```

Recompile and see if debug output appears.

### Option C: Check branching logic in background.c

Verify that `V_ridder()`, `dV_ridder()`, `ddV_ridder()` are calling the unified functions:

```c
if (pba->ridder_unified.model_type == ridder_model_unified) {
    // Call V_unified_theta(), dV_unified_dtheta()
} else {
    // Call v2 potential
}
```

### Option D: Simplify test case

Create minimal test with:
- Tail only (use_shelf = no, use_plateau = no)
- theta_i = 3.0 (clearly on tail slope)
- Lambda_tail = 2.3e-3 eV
- No CDM coupling (beta = 0)

If this also gives V=0, it's definitely a code path issue.

---

## 📂 **Files to Investigate**

1. `phase2/class/source/ridder_unified_potential.c`
   - Are functions implemented correctly?
   - Do they handle the ridder_unified_params struct?

2. `phase2/class/source/background.c`
   - Line ~2300-2400: V_ridder() branching
   - Does it call unified functions or v2 functions?

3. `phase2/class/Makefile`
   - Is `ridder_unified_potential.o` in the SOURCE list?
   - Was it actually compiled?

---

## 🎯 **Once Unblocked**

After fixing V=0 issue, complete Phase 1A:
1. Re-run beta ladder
2. Extract H0_eff, S8, f_peak, z_peak for each beta
3. Compare to previous results
4. Proceed to Phase 1B (tail activation)

---

## 📝 **Questions for Code Review**

When you review `ridder_unified_potential.c`:

1. **Are these functions actually being called?**
   - `V_unified_theta()`
   - `dV_unified_dtheta()`
   - `V_tail_theta()`, `V_shelf_theta()`

2. **Is the window function W_EDE correct?**
   ```c
   W(θ) = ½[1 + tanh((θ - θ_low)/σ)] - ½[1 + tanh((θ - θ_high)/σ)]
   ```
   For θ=0.82, θ_low=0.1, θ_high=5.0, σ=0.2:
   - Should give W ≈ 1 (inside window)
   - If W=0, bug in tanh logic

3. **Are unit conversions correct?**
   - Input: V in eV⁴, φ in eV
   - Output: ρ in Mpc⁻²
   - Conversion factor: `(eV_to_Mpc_inv²) / (3 M_Pl²)`

---

**STATUS:** Validation bugs fixed (6/6), but unified potential returns zero.  
**BLOCKER:** Need to diagnose why V=0 even though code path is correct.  
**NEXT:** Option B or C (add debug output or check branching logic).

