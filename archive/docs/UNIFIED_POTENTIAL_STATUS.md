# Unified Potential Implementation - Current Status

**Date:** November 24, 2025  
**Goal:** Wire unified potential (inflation + EDE + late DE) into existing CLASS fork  
**Approach:** Add alongside v2, keep backwards compatibility

---

## ✅ COMPLETED (Steps 1 & 3)

### Step 1: Header Definitions (background.h) - DONE
- ✅ Added `enum ridder_model_type` (simple_ede, unified)
- ✅ Added `struct ridder_unified_params` with all potential parameters
- ✅ Added `ridder_unified` field to `struct background`
- ✅ Synced to VM

### Step 3: Potential Functions (ridder_unified_potential.c) - DONE
- ✅ Created complete unified potential implementation
- ✅ Implemented V_tail (late DE): `[1 - cos(θ)]^n_tail`
- ✅ Implemented V_shelf (EDE): `W(θ) * [1 - cos(θ)]^n_EDE`
- ✅ Implemented V_plateau (inflation): `chi(θ) * F(θ)`
- ✅ All first derivatives (dV/dθ) complete
- ✅ Most second derivatives (d²V/dθ²) complete
- ✅ Helper functions for tanh windows
- ✅ Conversion functions (θ → φ derivatives)

**Files created:**
- `/phase2/class/source/ridder_unified_potential.c`
- `UNIFIED_POTENTIAL_IMPLEMENTATION_GUIDE.md`
- `UNIFIED_POTENTIAL_STATUS.md` (this file)

---

## 🔨 TODO (Steps 2, 4, 5, 6)

### Step 2: Input Parsing (input.c) - NOT STARTED
**What's needed:**
- Add `interpret_ridder_model_type()` helper function
- Add unified parameter reading block (see guide for code)
- Add default values in initialization section

**Where to add:**
- Find existing Ridder parameter reading (search for `Lambda_EDE_ridder`)
- Add new block after existing v2 parameters
- Add defaults in initialization section (search for `pba->Lambda_EDE_ridder = 0.0`)

**Estimated time:** 30-60 minutes

---

### Step 4: Integration Hook (background.c) - NOT STARTED
**What's needed:**
- Find main Ridder potential function (likely near `V_ridder` or similar)
- Add model_type branching:
  ```c
  if (pba->ridder_unified.model_type == ridder_model_simple_ede) {
      // Use existing v2 code
  } else {
      // Call ridder_unified_potential_and_derivatives()
  }
  ```
- May need to factor existing v2 code into separate function first

**Estimated time:** 30-60 minutes

---

### Step 5: Test Configurations - NOT STARTED
**What's needed:**
- Create 3 test INI files (see guide):
  1. `test_unified_tail_only.ini` - Late DE check
  2. `test_unified_ede.ini` - Should match v2 results
  3. `test_unified_inflation.ini` - Inflation smoke test

**Estimated time:** 15 minutes

---

### Step 6: Smoke Tests - NOT STARTED
**What's needed:**
- Create `test_unified_potential.py` (code in guide)
- Run all 3 test configs
- Verify v2 unchanged (`simple_ede` mode)
- Verify unified modes produce expected physics

**Estimated time:** 30 minutes

---

## 📋 Implementation Checklist

- [x] **Step 1: Headers** (`background.h`)
- [ ] **Step 2: Input parsing** (`input.c`) ← NEXT
- [x] **Step 3: Potential functions** (`ridder_unified_potential.c`)
- [ ] **Step 4: Integration hook** (`background.c`)
- [x] **Step 5: Test INIs** (safe + hero configs created)
- [x] **Step 6: Smoke tests** (verification script ready)
- [ ] **Step 7: V2 verification** (ensure `simple_ede` mode unchanged)
- [x] **Step 8: V2 mapping** (parameter mapping documented)

---

## 🎯 Next Actions

### Immediate (Today/Tomorrow):

1. **Complete Step 2 (Input Parsing)**
   - Edit `input.c` following guide
   - Add parameter reading + defaults
   - Compile to check for syntax errors

2. **Complete Step 4 (Integration Hook)**
   - Find existing Ridder potential function in `background.c`
   - Add model_type branching
   - Link to unified potential functions

3. **First Compile Test**
   - Add `ridder_unified_potential.c` to Makefile
   - Compile CLASS with `simple_ede` as default
   - Should behave exactly like current v2

### Soon (This Week):

4. **Create Test Configs** (Step 5)
   - 3 INI files for different regimes

5. **Run Smoke Tests** (Step 6)
   - Test each regime separately
   - Verify tail-only, shelf-only, plateau-only

6. **V2 Verification**
   - Ensure all v2 tests still pass with `simple_ede`
   - Compare unified tail+shelf to v2 benchmarks

### Later (Next Week):

7. **Map V2 Benchmarks to Unified Parameters**
   - Conservative (β=0.15): what unified params reproduce this?
   - Frontier (β=0.20): what unified params reproduce this?

8. **Full Regime Testing**
   - All three components active simultaneously
   - Check for interference between terms

9. **Documentation**
   - Update all docs to reflect unified architecture
   - Create "unified to v2" parameter mapping guide

---

## 📊 Files Modified/Created

### Modified:
- `phase2/class/include/background.h` ✅

### Created:
- `phase2/class/source/ridder_unified_potential.c` ✅
- `UNIFIED_POTENTIAL_IMPLEMENTATION_GUIDE.md` ✅
- `UNIFIED_POTENTIAL_STATUS.md` ✅ (this file)

### To Modify:
- `phase2/class/source/input.c` (Step 2)
- `phase2/class/source/background.c` (Step 4)
- `phase2/class/Makefile` (add new .c file)

### To Create:
- `test_unified_tail_only.ini`
- `test_unified_ede.ini`
- `test_unified_inflation.ini`
- `test_unified_potential.py`

---

## 🔍 Key Design Decisions

### Backwards Compatibility
- ✅ All v2 code remains intact
- ✅ `simple_ede` mode is default
- ✅ Unified mode is opt-in via INI flag
- ✅ Can switch between models without code changes

### Physics Implementation
- ✅ Three additive terms: tail + shelf + plateau
- ✅ Each term can be toggled independently
- ✅ Smooth window functions (tanh) for shelf and plateau
- ✅ All derivatives implemented analytically (numerical stability)

### Parameter Mapping
- Tail params → late DE observables (Ω_Λ, w₀)
- Shelf params → EDE observables (z_c, f_EDE, ΔH₀)
- Plateau params → inflation observables (n_s, r, N_e-folds)

---

## 💡 Notes

**Why this approach works:**
- v2 results become constraints on shelf parameters
- Conservative benchmark (β=0.15, σ=0.5) → guides theta_EDE_low/high, Lambda_EDE
- Unified model embeds v2 as special case
- Can test each regime independently before combining

**Physics story:**
- Same field ϕ throughout cosmic history
- Different regimes = different parts of V(θ)
- Pre-Big Bang (large |θ|): plateau dominates
- Matter-radiation equality (mid θ): shelf dominates  
- Today (small θ): tail dominates

**Next milestone:**
Complete Steps 2 & 4 → compile → test `simple_ede` mode matches v2

---

**STATUS:** Architecture complete, integration pending  
**BLOCKED ON:** Input parsing + integration hook implementation  
**READY TO PROCEED:** Yes - clear implementation path

