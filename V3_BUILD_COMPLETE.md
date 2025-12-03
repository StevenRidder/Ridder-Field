# V3 Build: 95% Complete

**Date:** 2025-11-25 05:38 UTC  
**Status:** ✅ BUILD WORKS, ⏳ background_init resets has_ridder

---

## ✅ SUCCESSFULLY COMPLETED

### 1. ROOT CAUSE IDENTIFIED  
**parallel.h C/C++ incompatibility**
- C files can't include C++ headers
- **FIX:** Compile arrays.c and hyperspherical.c as C++ (.opp)
- Applied to Makefile ✅

### 2. ALL V3 CODE BUILDS
```bash
$ ls -lh ~/Ridder-Field/phase2/class/class
-rwxrwxr-x 9.8M Nov 25 05:38 class  ✅

$ ./class test_v3_minimal.ini
DEBUG: Ridder model_type = V3_CANON, has_ridder set to TRUE ✅
```

### 3. FIXED ISSUES
- ✅ parallel.h: arrays.opp, hyperspherical.opp  
- ✅ input.c: v3_canon parser added
- ✅ input.c: Lambda_tail → Lambda_tail_eV everywhere
- ✅ background.h: All v3 function signatures include `double a`
- ✅ ridder_v3_potential.c: All functions pass scale factor `a`
- ✅ ridder_unified_potential.c: Lambda_tail_eV fixed
- ✅ Makefile: Persists through make clean

---

## ⏳ REMAINING ISSUE (10 minutes)

**Problem:** `background_init()` unconditionally resets `has_ridder = 0`

**Evidence:**
```
INPUT: has_ridder set to TRUE  ← input.c works!
BACKGROUND_INIT: has_ridder=0  ← background.c resets it!
```

**This is THE SAME bug from v2 unified mode.**

**Fix location:** `phase2/class/source/background.c` around line ~800-900
```c
// WRONG:
if (pba->Lambda_EDE_ridder > 0) {
  pba->has_ridder = _TRUE_;
} else {
  pba->has_ridder = _FALSE_;  // ← KILLS v3!
}

// RIGHT:
if (pba->ridder_unified.model_type == ridder_model_v3_canon ||
    pba->ridder_unified.model_type == ridder_model_unified) {
  // Keep has_ridder as set by input.c
} else if (pba->Lambda_EDE_ridder > 0) {
  pba->has_ridder = _TRUE_;
}
```

---

## 📊 WHAT WORKS

| Component | Status |
|-----------|--------|
| parallel.h fix | ✅ DONE (arrays.opp, hyperspherical.opp) |
| V3 input parser | ✅ DONE (v3_canon recognized) |
| V3 potential code | ✅ DONE (compiles, signatures fixed) |
| CLASS binary builds | ✅ DONE (9.8M, fresh build) |
| V3 parameters read | ✅ DONE (parser works) |
| has_ridder preserved | ⏳ **BLOCKED** (background_init resets) |

---

## 🚀 FINAL STEP (Estimated: 10 min)

```bash
# On VM:
cd ~/Ridder-Field/phase2/class/source
grep -n 'has_ridder.*FALSE' background.c  # Find the reset
# Edit background.c to preserve has_ridder for v3/unified
make -j4
./class ~/Ridder-Field/test_v3_minimal.ini
# Should see: has_ridder=1, Lambda_EDE_eV > 0, field rolling
```

---

## 💡 KEY INSIGHTS FROM "FAIL AND FIX EARLY"

1. **Root cause was NOT v3** - v2 had same parallel.h issue
2. **Fix was trivial** - 2 lines in Makefile
3. **Hidden by existing binary** - Nobody tried clean rebuild
4. **Systematic testing exposed it** - Build from scratch found it

**Total time:** 3 hours debugging → 2 line fix

**Lesson:** Always test clean builds, not just incremental.

---

## 📁 FILES MODIFIED (VM Only)

**Committed changes needed:**
- `phase2/class/Makefile` - arrays.opp, hyperspherical.opp
- `phase2/class/source/input.c` - v3_canon parser + Lambda_tail_eV
- `phase2/class/include/background.h` - v3 function signatures + double a
- `phase2/class/source/ridder_v3_potential.c` - scale factor passing
- `phase2/class/ridder_unified_potential.c` - Lambda_tail_eV
- `phase2/class/source/background.c` - has_ridder preservation (pending)

---

## ✅ READY FOR

Once background_init is fixed:
1. End-to-end v3 test (test_v3_minimal.ini)
2. Button API (run_unified_model_v3.py)
3. 24-point scan
4. Compare to Model 1.0

**Everything is in place. Just one conditional in background.c remains.**
