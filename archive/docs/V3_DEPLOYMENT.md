# V3 Canonical Model - Deployment Status

**Date:** 2025-11-25  
**Branch:** `v3-development`  
**Commit:** `771931f`

---

## ✅ DEPLOYMENT COMPLETE

### Repository Structure

```
v3-development/
├── phase2/class/
│   ├── include/
│   │   ├── background.h          [v3 struct: ridder_unified_params]
│   │   └── parallel.h            [C-compatible stubs]
│   ├── source/
│   │   ├── ridder_v3_potential.c [V3 CANON: EDE + tail + floor]
│   │   ├── input.c               [Updated for v3 field names]
│   │   └── background.c          [Calls v3 potential]
│   └── Makefile                  [Compiles ridder_v3_potential.o]
├── run_unified_model_v3.py       [Button with shooting + JSON]
├── check_mcmc_status.py          [MCMC diagnostics]
├── MODEL_1_FINAL_STATUS.md       [Model 1.0 exclusion result]
└── MODEL_DEFINITION.md           [Model 1.0 definition - archived]
```

---

## 🔧 V3 Canonical Potential (FROZEN)

### Mathematical Form

```
V(θ) = V_floor + V_EDE(θ) + V_tail(θ)

V_floor = Λ_floor⁴

V_EDE(θ) = Λ_EDE⁴ · exp[-(θ - θ_E_center)² / (2σ_E²)] · [1 - cos(θ)]^n_EDE

V_tail(θ) = Λ_tail⁴ · [1 + α_tail · (1 - cos(θ - θ_T_center))^n_tail]
```

### Default Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `f_eV` | 1.0e26 | Field normalization |
| `theta_E_center` | 2.4 | EDE bump center |
| `sigma_E` | 0.4 | EDE Gaussian width |
| `n_EDE` | 2.0 | EDE power |
| `theta_T_center` | 0.0 | Tail center |
| `alpha_tail` | 1.0 | Tail modulation |
| `n_tail` | 1.0 | Tail power |
| `Lambda_floor_eV` | 0.0 | Constant floor (disabled) |

**User Knobs:**
- `Lambda_tail_meV`: Tail energy scale (controls S8)
- `f_axion`: EDE strength (controls H0 via r_s)

---

## 📍 Sync Status

### Local Mac (development machine)
- **Branch:** `v3-development` ✅
- **Commit:** `771931f` ✅
- **Files:** All v3 files present ✅

### VM (ridderadmin@172.174.34.125)
- **Branch:** `v3-development` ✅
- **Commit:** `771931f` ✅
- **CLASS Binary:** Built successfully (Nov 25, 01:45) ✅
- **Patches Applied:**
  - `parallel.h`: C-compatible stubs ✅
  - `input.c`: Updated to use v3 field names (`Lambda_tail_eV`, `Lambda_EDE_eV`) ✅

### Remote (GitHub)
- **Branch:** `v3-development` ✅
- **URL:** https://github.com/StevenRidder/Ridder-Field/tree/v3-development ✅

---

## 🚀 Workflow Going Forward

### ALL C/CLASS work MUST run on VM:

```bash
# On local Mac - edit code
vim phase2/class/source/ridder_v3_potential.c

# Commit and push
git add phase2/class/source/ridder_v3_potential.c
git commit -m "V3: update potential"
git push origin v3-development

# On VM - pull and rebuild
ssh ridderadmin@172.174.34.125
cd ~/Ridder-Field
git pull origin v3-development
cd phase2/class
make clean && make -j4
```

### ALL Python/JSON analysis runs on VM:

```bash
# Run v3 button on VM
ssh ridderadmin@172.174.34.125
cd ~/Ridder-Field
python3 run_unified_model_v3.py --preset unified_compromise --mode full
```

### Never run CLASS locally on Mac
- Mac has different compiler flags
- Parallel.h issues
- All execution is VM-only

---

## 🧪 Verification Tests

### Test 1: V3 Button with Preset
```bash
ssh ridderadmin@172.174.34.125 "cd ~/Ridder-Field && python3 run_unified_model_v3.py --preset lcdm_baseline --mode quick --skip_shooting"
```
**Expected:** LCDM background, no EDE, no tail

### Test 2: V3 Button with Parameters
```bash
ssh ridderadmin@172.174.34.125 "cd ~/Ridder-Field && python3 run_unified_model_v3.py --Lambda_tail_meV 16.0 --f_axion 0.40 --mode quick"
```
**Expected:** Shooting for Lambda_EDE, background with EDE+tail

### Test 3: Check V3 Potential is Active
```bash
ssh ridderadmin@172.174.34.125 "cd ~/Ridder-Field/phase2/class && ./class ~/Ridder-Field/test_v3.ini 2>&1 | grep 'V_UNIFIED_DEBUG\|ridder_V_v3'"
```
**Expected:** Debug prints from v3 potential functions

---

## 📦 VM Patches Applied

These are VM-specific patches that are NOT committed to git:

1. **`phase2/class/include/parallel.h`**
   - Replaced C++ threading with C-compatible stubs
   - Defines: `class_setup_parallel`, `class_finish_parallel`, `class_run_parallel*`

2. **`phase2/class/source/input.c`**
   - Updated field names: `Lambda_tail` → `Lambda_tail_eV`
   - Updated field names: `Lambda_EDE` → `Lambda_EDE_eV`

These patches are needed because the VM uses GCC with strict C compilation.

---

## 🗂️ Model 1.0 Archive

Model 1.0 (2-parameter tail+shelf) is **excluded** by MCMC smoke test.

Archived scripts:
- `mcmc_smoke.py`
- `ridder_solver.py`
- `systematic_scan.py`
- `relaxed_scan.py`
- `find_viable_point.py`

Result: `MODEL_1_FINAL_STATUS.md`

---

## 🎯 Next Steps

1. ✅ Test v3 button with presets
2. ✅ Verify shooting mechanism works
3. ⏳ Implement full JSON contract
4. ⏳ Add CMB/BAO observables extraction
5. ⏳ Design Model 2.0 (additional freedom beyond v3 defaults)

---

## 🔐 Critical Rules

1. **Never** commit VM-specific patches (`parallel.h`, `input.c` field name fixes)
2. **Always** test on VM before pushing to v3-development
3. **Never** run CLASS locally on Mac
4. **Always** sync Mac → GitHub → VM for code changes
5. **Keep** v3 potential frozen unless changing physics story

---

**Status:** CLEAN V3 DEPLOYMENT ✅  
**All machines synced:** Mac ✅ | GitHub ✅ | VM ✅  
**CLASS builds:** ✅  
**Ready for v3 experimentation:** ✅

