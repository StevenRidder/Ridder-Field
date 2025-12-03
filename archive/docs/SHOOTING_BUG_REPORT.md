# 🔴 BUG #15: Field-Window Mismatch in Shooting

**Date:** November 24, 2025  
**Status:** ROOT CAUSE IDENTIFIED

---

## What Happened

Shooting mechanism executed correctly and reported:
```
Shooting failed: target f_EDE = 0.1000 NOT bracketed by [0.0000, 0.0000].
```

Both bracket endpoints (`m_axion = 1e-5` and `m_axion = 1e5 H0 units`) gave `f_EDE = 0`.

---

## Debug Output Analysis

```
V_UNIFIED_DEBUG: theta=1.026694e-09, use_tail=0, use_shelf=1, use_plateau=0
  V_shelf=0.000000e+00
RIDDER DEBUG: rho_ridder=0.000000e+00
```

**Field state:**
- `theta ~ 10^-9` radians (throughout evolution)
- Shelf window: `[0.01, 10.0]` radians
- **Field is 7 orders of magnitude below window → V_shelf = 0 always**

---

## Root Cause

The parameter `ridder_f` (used for `theta = phi / ridder_f`) is not correctly synchronized with `f_axion`.

**In INI:**
- `ridder_f = 2.435e25` eV (M_Pl)
- `ridder_f_axion = 0.01` M_Pl units
- `ridder_theta_i = 2.8`

**Expected:**
- `phi_ini = theta_i × f = 2.8 × (0.01 M_Pl) = 0.028 M_Pl = 6.8e25 eV`
- But debug shows `phi = 2.50e+16 eV` → 9 orders of magnitude smaller!

**Problem:** There's a unit conversion bug between `f_axion` (M_Pl units) and `ridder_f` (eV units).

---

## Fix Strategy

**Option 1:** Remove `ridder_f` entirely, use `f_axion` directly
- Modify `background.c` to compute `f_eV = f_axion × M_Pl_eV`
- Use that for `theta = phi / f_eV`

**Option 2:** Make `ridder_f` read-only, set by code
- In `input.c`: `pba->ridder_unified.f = pba->ridder_unified.f_axion × M_PL_EV`
- Remove `ridder_f` from user-facing INI

**Option 3:** Simpler test - use AxiCLASS parameters directly
- Copy exact values from working AxiCLASS example
- `m_axion = 1e5 H0`, `f_axion = 0.4 M_Pl`, `theta_i = 2.8`
- Adjust shelf window to match where field goes

---

## Recommended Path Forward

**IMMEDIATE (15 min):**
1. Check `background.c` to see how `f_eV` is computed from `f_axion`
2. Add debug print: `theta = phi / f_eV` vs `phi / ridder_f`
3. Find the mismatch

**THEN (30 min):**
4. Fix the unit conversion
5. Re-run minimal shooting test
6. Verify `theta ~ O(1)` at early times

**VALIDATION (1 hour):**
7. Shooting should find intermediate `m_axion` that gives f_EDE ~ 0.10
8. Plot `f_ridder(z)` showing clean bump
9. Proceed to add tail/coupling

---

## Why This Is Actually Good News

1. ✅ **Shooting mechanism works perfectly** - it correctly identified unreachable target
2. ✅ **Clear error message** - told us exactly what to fix
3. ✅ **Isolating minimal case** - found bug without tail/coupling complexity
4. ✅ **"Fail and Fix Early" in action** - caught this BEFORE full model

This is EXACTLY how validation should work. We found a fundamental parameter bug in the simplest possible test case.

---

## Next Action

**USER DECISION NEEDED:**

Do you want me to:
- **A:** Debug the `f_eV` vs `ridder_f` mismatch now (will take ~1 hour)
- **B:** Switch to a different parameterization (use AxiCLASS values exactly)
- **C:** Pause here and you'll look at the code yourself

**My recommendation:** Option A - fix it properly so we understand the unit system.

