# CLASS WITH RIDDER FIELD - CURRENT STATUS

**Date:** 2025-11-21 07:50  
**Status:** ⚠️ PARTIAL - Infrastructure in place, shooting issue needs fix

---

## WHAT'S WORKING ✅

1. **Compilation** - CLASS compiles successfully on macOS
2. **Parameter reading** - Ridder parameters are read from .ini files
3. **Potential functions** - V_scf(), dV_scf(), ddV_scf() implement Ridder potential correctly
4. **Vanilla CLASS** - Standard ΛCDM runs perfectly

---

## CURRENT ISSUE ❌

**Problem:** "Shooting failed" error when running with Ridder field

**Root cause:** CLASS's scalar field (scf) infrastructure expects to "shoot" for initial conditions that produce a target `Omega_scf` today. The Ridder field is Early Dark Energy (EDE) that decays away, so this shooting method doesn't work.

**Error message:**
```
Shooting failed, try optimising input_get_guess()
root must be bracketed in zriddr
```

---

## WHY THIS HAPPENS

CLASS's scf module workflow:
1. User sets `Omega_scf` (target density today)
2. CLASS "shoots" for initial conditions (phi_ini, phi_prime_ini) that produce this Omega today
3. This works for quintessence (dark energy today) but NOT for EDE (negligible today)

The Ridder field:
- Is EDE (peaks at z~6500, then decays)
- Has negligible density today
- Initial conditions should be: `phi_ini = f * theta_i`, `phi_prime_ini = 0` (Hubble-frozen)
- Density is computed from potential, not from target Omega

---

## SOLUTIONS

### Option 1: Bypass Shooting (Recommended)
Modify CLASS to skip shooting when `has_ridder == TRUE`:

**File:** `source/input.c`  
**Location:** Around line 1200-1300 in `input_shooting()` function

**Change:**
```c
if (pba->has_ridder == _TRUE_) {
  // Use explicit initial conditions for Ridder field
  pba->phi_ini_scf = pba->f_axion_ridder * pba->theta_i_ridder;
  pba->phi_prime_ini_scf = 0.0;  // Hubble-frozen
  return _SUCCESS_;  // Skip shooting
}
```

### Option 2: Use Explicit Initial Conditions in .ini
Set initial conditions directly in .ini file:

```ini
use_scf = yes
attractor_ic_scf = no
scf_parameters = 0.0, 0.0, PHI_INI, PHI_PRIME_INI

# Where:
# PHI_INI = f_axion_ridder * theta_i_ridder
# PHI_PRIME_INI = 0.0
```

**Problem:** This requires computing phi_ini manually for each run.

### Option 3: Implement Ridder-Specific IC Function
Add a new function `background_ridder_initial_conditions()` that CLASS calls when `has_ridder == TRUE`.

---

## RECOMMENDED FIX

Implement Option 1 (bypass shooting). This is the cleanest solution and matches how the previous implementation likely worked.

**Steps:**
1. Find the shooting function in `source/input.c`
2. Add check for `has_ridder`
3. If true, set explicit ICs and return
4. Otherwise, proceed with normal shooting

**Estimated time:** 15-30 minutes

---

## WHAT'S ALREADY IMPLEMENTED

### ✅ background.h
- Ridder field parameters added to struct
- `has_ridder` flag

### ✅ input.c  
- Default values set
- Parameters read from .ini
- `has_ridder` flag set when `Lambda_EDE_ridder > 0`

### ✅ background.c
- `V_scf()` implements Ridder potential: `Λ⁴ * [1 - cos(φ/f)]ⁿ`
- `dV_scf()` implements first derivative
- `ddV_scf()` implements second derivative
- All functions check `has_ridder` flag

### ❌ NOT YET IMPLEMENTED
- Shooting bypass
- DM coupling in background evolution
- Switching surface logic
- Perturbation modifications

---

## TEST RESULTS

### Vanilla CLASS
```bash
./class explanatory.ini
```
**Result:** ✅ SUCCESS

### Ridder Field
```bash
./class ../../phase3/ridder_smoketest.ini
```
**Result:** ❌ FAIL - Shooting error

---

## NEXT STEPS

1. **Immediate:** Implement shooting bypass (Option 1)
2. **Then:** Test with ridder_smoketest.ini
3. **Verify:** H0 should be > 72 km/s/Mpc (EDE effect)
4. **Later:** Add DM coupling and switching logic

---

## FILES TO MODIFY

**To fix shooting:**
- `source/input.c` - Add shooting bypass in `input_shooting()` function

**For full implementation:**
- `source/background.c` - Add DM coupling to CDM evolution
- `source/background.c` - Add switching surface logic
- `source/perturbations.c` - Add Ridder field perturbations

---

**Status:** Infrastructure 80% complete, needs shooting bypass to be functional.

