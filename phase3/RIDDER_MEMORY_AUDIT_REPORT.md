# Ridder Field Memory Safety Audit Report
**Date:** 2025-12-02  
**Status:** READ-ONLY AUDIT - NO CHANGES MADE

## 🔴 CRITICAL ISSUE: Thread-Safety Violation

### Problem: Static Variables in Multi-Threaded Context

**Location:** `phase2/class/source/background.c` and `perturbations.c`

**Issue:** Multiple `static` variables are used for debug counters:
- `static int bg_func_counter = 0;` (line 603)
- `static int rho_add_counter = 0;` (line 629)
- `static int ddV_debug_counter = 0;` (line 569)
- `static int derivs_entry_counter = 0;` (line 3263)
- `static int switch_check_counter = 0;` (line 3392)
- `static int ridder_debug_counter = 0;` (line 3438)
- `static int coupling_counter = 0;` (line 3548)
- And more...

**Why This Causes Bus Errors:**
1. **Race Conditions**: When 7 chains run simultaneously, they all share the same static variables
2. **Memory Corruption**: Concurrent writes to static variables can corrupt memory
3. **Bus Errors**: Memory corruption leads to invalid pointer dereferences → Bus Error (Signal 7)

**Evidence:**
- Bus errors occur when multiple chains run simultaneously
- All chains crash at roughly the same time
- Error: "Signal: Bus error (7) - Non-existant physical address"

## 🟡 MEDIUM ISSUE: Potential Division by Zero

### Location: `perturbations.c:9374`

```c
double raw_coupling = 3.0 * beta_eff * a2 * Theta_ridder * M_Pl_eV / phi_prime;
```

**Issue:** Division by `phi_prime` without explicit check (though there's a check at line 9372: `fabs(phi_prime) > 1.e-30`)

**Status:** Protected by the `if` condition, but the threshold `1.e-30` is very small. If `phi_prime` is exactly zero or NaN, this could cause issues.

## 🟡 MEDIUM ISSUE: Array Bounds

### Location: Multiple locations accessing `pvecback[]` and `y[]`

**Issue:** Array accesses use indices like:
- `pvecback[pba->index_bg_phi_prime_ridder]`
- `y[pv->index_pt_phi_prime_ridder]`

**Status:** These indices are defined via `class_define_index()` which should be safe, but there's no runtime bounds checking. If an index is incorrectly initialized or corrupted, this could cause out-of-bounds access.

## 🟢 LOW ISSUE: Large Static Arrays

No large static arrays found that would cause stack overflow.

---

## RECOMMENDATIONS

### Immediate Fix (High Priority):

1. **Remove or Make Thread-Safe All Static Variables**
   - Option A: Remove static variables entirely (they're only for debug)
   - Option B: Use thread-local storage (`__thread` in GCC)
   - Option C: Pass counters as function parameters

2. **Add Explicit Bounds Checking**
   - Verify `index_bg_*` and `index_pt_*` are within valid ranges
   - Add assertions: `assert(index >= 0 && index < bg_size)`

3. **Strengthen Division Checks**
   - Increase `phi_prime` threshold from `1.e-30` to `1.e-20`
   - Add explicit NaN/Inf checks before division

### Long-term Fix:

1. **Thread-Safety Audit**: Review all CLASS code for static variables
2. **Memory Sanitizer**: Run with `-fsanitize=address` to catch memory errors
3. **Valgrind**: Run chains under Valgrind to detect memory corruption

---

## CODE SECTIONS TO REVIEW

### Critical Section 1: `background.c` lines 600-643
- Static variable `bg_func_counter` (line 603)
- Static variable `rho_add_counter` (line 629)
- Multiple `pvecback[]` accesses

### Critical Section 2: `perturbations.c` lines 9360-9385
- Division by `phi_prime` (line 9374)
- Array accesses: `pvecback[]`, `y[]`, `dy[]`
- No static variables here (good)

### Critical Section 3: `background.c` lines 3263-3654
- Multiple static counters
- These are in derivative functions called frequently

---

## CONCLUSION

**Root Cause:** The bus errors are most likely caused by **thread-safety violations from static variables** when multiple chains run simultaneously. The static counters are being modified concurrently by different processes, causing memory corruption.

**Immediate Action:** Remove or disable all static debug counters when running multiple chains. The debug output is not critical for production runs.

**Risk Level:** HIGH - This explains why all chains crash simultaneously when running in parallel.
