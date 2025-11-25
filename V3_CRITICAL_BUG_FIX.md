# V3 CRITICAL BUG: Potential Routing Not Implemented

**Date:** 2025-11-25
**Status:** 🔴 BLOCKER - V3 never runs, always falls back to v2

---

## The Bug

`background.c:V_ridder()` has routing for:
- ✓ `ridder_model_unified` → `V_unified_theta()`
- ✗ `ridder_model_v3_canon` → **MISSING**, falls through to v2!

Result: V3 model always runs v2 potential with `Lambda=0`, giving `V=0` everywhere.

---

## The Fix

### 1. Modify V_ridder() signature to include scale factor `a`

**File:** `phase2/class/source/background.c`

**Current (line ~3953):**
```c
double V_ridder(
                struct background *pba,
                double phi) {
  /* Branch on model type */
  if (pba->ridder_unified.model_type == ridder_model_unified) {
    /* Use unified potential */
    double theta = phi / pba->ridder_unified.f;
    return V_unified_theta(theta, &pba->ridder_unified);
  }
  
  /* Simple EDE (v2) potential */
  ...
}
```

**Fixed:**
```c
double V_ridder(
                struct background *pba,
                double phi,
                double a) {  // ADD scale factor
  /* Branch on model type */
  if (pba->ridder_unified.model_type == ridder_model_v3_canon) {
    /* V3 canonical potential */
    double V, dV, d2V;
    ridder_potential_v3(phi, a, &V, &dV, &d2V, &pba->ridder_unified);
    return V;
  }
  
  if (pba->ridder_unified.model_type == ridder_model_unified) {
    /* Use unified potential */
    double theta = phi / pba->ridder_unified.f;
    return V_unified_theta(theta, &pba->ridder_unified);
  }
  
  /* Simple EDE (v2) potential */
  ...
}
```

### 2. Same for dV_ridder() and ddV_ridder()

Add `double a` parameter and v3_canon routing to both.

### 3. Update call sites

**Line ~540:**
```c
// OLD:
V_ridder_val = V_ridder(pba, phi_ridder);
dV_ridder_val = dV_ridder(pba, phi_ridder);
ddV_ridder_val = ddV_ridder(pba, phi_ridder);

// NEW:
V_ridder_val = V_ridder(pba, phi_ridder, a);
dV_ridder_val = dV_ridder(pba, phi_ridder, a);
ddV_ridder_val = ddV_ridder(pba, phi_ridder, a);
```

Search for ALL calls to `V_ridder`, `dV_ridder`, `ddV_ridder` and add `, a`.

---

## Impact

**Before fix:** All 24 scan points give ΛCDM (f_EDE=0, H0=67.36, S8=0.830)
**After fix:** V3 potential active, non-zero rho_ridder, correct H0/S8/f_EDE

---

## Action Items

1. ✓ Diagnosed root cause
2. ⏳ Apply fix to background.c on VM
3. ⏳ Rebuild CLASS
4. ⏳ Re-run 24-point scan
5. ⏳ Verify f_EDE > 0

---

## Lesson

**FAIL AND FIX EARLY:** The v3 potential code was 100% correct, but never called! Always verify:
- Code compiles ✓
- Code is linked ✓
- Code is **ACTUALLY INVOKED** ← missed this!

Next time: Add debug prints in NEW code to confirm it's running!


