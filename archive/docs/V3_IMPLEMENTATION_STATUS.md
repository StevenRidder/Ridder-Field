# V3 Implementation Status

**Date:** 2025-11-25 05:00 UTC  
**Status:** 🟡 IN PROGRESS - Specification complete, implementation partially done

---

## ✅ COMPLETED

### 1. Full V3 Specification Documented
- `V3_COMPLETE_SPEC.md`: Complete mathematical spec for time-windowed EDE
- EDE now uses **Gaussian in ln(a)** for time localization (not Gaussian in θ)
- Tail unchanged from Track 2
- Full JSON schema defined
- CLI contract specified
- First scan grid planned (4×3×2 = 24 points)

### 2. Test Infrastructure Created
- `test_v3_stack.py`: Comprehensive validation suite
  - Tests v3 potential functions are called
  - Tests button API with all modes
  - Tests shooting mechanism
  - Tests JSON schema compliance
  - Tests physics sanity

### 3. Struct Updates
- Added `a_c`, `sigma_lna` to `ridder_unified_params`
- Added `ridder_model_v3_canon` to enum

---

## 🟡 PARTIALLY COMPLETE

### 1. V3 Potential Functions
- ✅ Time window `S(a; a_c, sigma_lna)` implemented
- ✅ Field bump `B(theta; theta_E, n_EDE)` implemented
- ✅ `V_EDE_v3(theta, a, rp)` updated for time-windowed form
- ⏳ Derivatives `dV_EDE/dtheta` and `d2V_EDE/dtheta2` need updating
- ⏳ Derivatives must include chain rule for time window
- ⏳ Tail potential unchanged (good)

### 2. Input Parser
- ⏳ `input.c` needs to recognize `ridder_model_type = v3_canon`
- ⏳ Need to read `a_c` and `sigma_lna` from INI
- ⏳ Currently fails with "Unknown ridder_model_type='v3_canon'"

---

## ❌ NOT STARTED

### 1. Button API Updates
- `run_unified_model_v3.py` still uses old parameter mapping
- Need to update CLI to accept:
  - `--Lambda_EDE_eV`
  - `--a_c` or `--z_c`
  - `--sigma_lna`
  - `--theta_E`
  - `--n_EDE`
  - `--Lambda_tail_eV`
  - `--alpha_tail`
  - `--n_tail`
  - `--theta_ini`

### 2. JSON Schema Implementation
- Need to output full schema from `V3_COMPLETE_SPEC.md`
- Add all diagnostic sections:
  - `ede_diagnostics`
  - `tail_diagnostics`
  - `bao_residuals`
  - `cmb_residuals`
  - `chi2` breakdown
  - `meta` with timestamps

### 3. First Scan Script
- Create `v3_first_scan.py`:
  - Fix tail to Track 2 values
  - Scan EDE grid (24 points)
  - Reuse `compute_chi2.py` from v1
  - Compare to v1 results

### 4. Chi-squared Computation
- Port `compute_chi2.py` logic from v1
- Apply same selection criteria
- Compute Δχ² vs ΛCDM and vs v1 best

---

## 🚧 BLOCKING ISSUES

### Issue 1: input.c doesn't recognize v3_canon
**Location:** `phase2/class/source/input.c:3381`  
**Error:** `Unknown ridder_model_type='v3_canon'. Allowed: 'simple_ede' or 'unified'.`

**Fix needed:**
```c
// Around line 3370-3390 in input.c
if ((strcmp(string1, "v3_canon") == 0) || (strcmp(string1, "V3_CANON") == 0)) {
  pba->ridder_unified.model_type = ridder_model_v3_canon;
  pba->has_ridder = _TRUE_;
}
```

### Issue 2: V_EDE derivatives incomplete
**Location:** `phase2/class/source/ridder_v3_potential.c`

Need to update:
- `dV_EDE_dtheta_v3(theta, a, rp)`: Add time window to chain rule
- `d2V_EDE_dtheta2_v3(theta, a, rp)`: Add time window to chain rule

**Chain rule:**
```
dV_EDE/dtheta = Lambda^4 * [S(a) * dB/dtheta]
d2V_EDE/dtheta2 = Lambda^4 * [S(a) * d2B/dtheta2]
```
(Time window doesn't depend on theta, so derivatives simpler than before)

### Issue 3: Scale factor 'a' not passed to potential
**Location:** Background evolution integration

The potential functions now need `a` as a parameter, but the background integrator currently only passes `phi`. 

**Options:**
1. Add `a` to potential function signatures globally
2. Store `a` in `pba` and read it in potential
3. Precompute `S(a)` table and interpolate

---

## 📋 NEXT ACTIONS (Priority Order)

### 1. Fix input.c parser (15 min)
```bash
ssh VM
cd ~/Ridder-Field/phase2/class/source
# Edit input.c around line 3370-3390
# Add v3_canon recognition
# Rebuild: make clean && make -j4
```

### 2. Complete V_EDE derivatives (30 min)
- Update `dV_EDE_dtheta_v3` to include S(a) factor
- Update `d2V_EDE_dtheta2_v3` to include S(a) factor
- Test that derivatives are correct

### 3. Solve scale factor passing (45 min)
**Recommended: Store a in pba**
```c
// In background.c integration loop
pba->a_current = a_value;  // Store before calling potential

// In ridder_v3_potential.c
static double V_EDE_v3(..., struct background *pba) {
  double a = pba->a_current;
  ...
}
```

### 4. Test one v3 point end-to-end (30 min)
```bash
# Create minimal v3 INI
# Run CLASS
# Verify f_EDE peaks at correct z_c
# Verify time window works
```

### 5. Update button API (1 hour)
- New CLI parameters
- Map z_c → a_c internally
- Generate proper INI
- Output full JSON schema

### 6. Create first scan script (30 min)
- 24-point grid
- Call button for each
- Collect results
- Compare to v1

---

## 🎯 ESTIMATED TIME TO COMPLETION

- **Minimal viable v3** (one working point): 2-3 hours
- **Full button + scan** (24 points + analysis): 4-5 hours
- **Paper-ready results**: 6-8 hours (includes iteration)

---

## 🔴 CRITICAL PATH

```
Fix input parser → Complete derivatives → Solve 'a' passing → Test one point
       ↓
Update button API → Test with presets → Verify JSON
       ↓
Create scan script → Run 24 points → Compare to v1 → Report
```

---

**RECOMMENDATION:** Focus on Critical Path in order. Don't parallelize until one full point works end-to-end.

**CURRENT BLOCKER:** input.c parser (15 min fix)

---

## 📞 READY TO PROCEED?

Reply with:
- **"fix it"**: I'll implement the critical path sequentially
- **"just the parser"**: I'll only fix input.c so CLASS runs
- **"status only"**: Keep this as documentation, proceed when ready

All work will be done on VM per your rules.

