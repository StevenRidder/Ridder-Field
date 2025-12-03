# V2 Development Status

**Last Updated**: November 23, 2025  
**Branch**: `v2-development`  
**Status**: Phase 0 Complete ✅

---

## ✅ Phase 0: Setup Complete

### What Was Done:
1. **Created V2 directory structure**:
   - `phase2_v2/class/` - V2 CLASS implementation
   - `phase3_v2/configs/` - V2 MCMC configs
   - `phase3_v2/scripts/` - V2 run scripts
   - `phase3_v2/results/` - V2 chain data and plots
   - `phase3_v2/tests/` - V2 validation tests

2. **Froze V1 codebase**:
   - Added `FROZEN_V1.txt` markers in `phase2/` and `phase3/`
   - V1 will not be modified during V2 development

3. **Copied CLASS source to V2**:
   - Full copy of `phase2/class` → `phase2_v2/class`
   - Ready for V2 modifications

4. **Created Git branch**:
   - Branch: `v2-development`
   - Pushed to GitHub: https://github.com/StevenRidder/Ridder-Field/tree/v2-development

5. **Documentation created**:
   - `V2_DESIGN.md` - Overall V2 model design
   - `V2_IMPLEMENTATION_PLAN.md` - Step-by-step execution plan
   - `V2_STATUS.md` - This file (progress tracker)

---

## 📋 Next Steps (Phase 1)

### Phase 1: Download and Validate AxiCLASS (1-2 days)

**Tasks**:
- [ ] Clone AxiCLASS from GitHub
- [ ] Compile AxiCLASS
- [ ] Install Python wrapper
- [ ] Run test with default EDE parameters
- [ ] Verify chi2 < 2800 (or at least reasonable)

**Commands**:
```bash
cd ~/Downloads
git clone https://github.com/PoulinV/AxiCLASS.git
cd AxiCLASS
make clean && make -j8
cd python && python3 setup.py install --user
```

**Success Criteria**:
- ✅ AxiCLASS compiles without errors
- ✅ Python import works: `from classy import Class`
- ✅ Test run produces C_ℓ values
- ✅ No obvious crashes or errors

---

## 🎯 Overall Progress

| Phase | Status | Duration | Completion |
|-------|--------|----------|------------|
| **Phase 0: Setup** | ✅ Complete | 1 hour | 100% |
| **Phase 1: AxiCLASS** | ⬜ Not Started | 1-2 days | 0% |
| **Phase 2: V2 Potential** | ⬜ Not Started | 2-3 days | 0% |
| **Phase 3: Single-Point Tests** | ⬜ Not Started | 2-3 days | 0% |
| **Phase 4: MCMC Configs** | ⬜ Not Started | 1 day | 0% |
| **Phase 5: Production Runs** | ⬜ Not Started | 5-7 days | 0% |

**Total Estimated Time**: 11-17 days  
**Days Completed**: 0.04 (1 hour)  
**Days Remaining**: 11-17

---

## 📁 Directory Structure

```
Ridder-Field/
├── phase2/                    # V1 CLASS (FROZEN)
│   └── FROZEN_V1.txt
├── phase2_v2/                 # V2 CLASS (ACTIVE)
│   └── class/                 # Full CLASS copy, ready for V2 mods
├── phase3/                    # V1 MCMC (FROZEN)
│   ├── FROZEN_V1.txt
│   ├── configs/               # V1 configs (archived)
│   ├── scripts/               # V1 scripts (archived)
│   └── results/               # V1 results (archived)
├── phase3_v2/                 # V2 MCMC (ACTIVE)
│   ├── configs/               # V2 configs (empty, to be created)
│   ├── scripts/               # V2 scripts (empty, to be created)
│   ├── results/               # V2 results (empty, to be created)
│   └── tests/                 # V2 tests (empty, to be created)
├── V1_FAILURE_ANALYSIS.md     # What went wrong in V1
├── V1_TRUTH_REVEALED.md       # Why V1 was never good
├── V2_DESIGN.md               # V2 model design
├── V2_IMPLEMENTATION_PLAN.md  # Step-by-step execution plan
└── V2_STATUS.md               # This file (progress tracker)
```

---

## 🔑 Key Decisions

### V2 Model Features:
1. **Flattened Monodromy Potential**:
   ```
   V(φ) = μ³φ + Λ⁴[1 - cos(φ/f)]ⁿ / (1 + c(φ/f)²)
   ```
   - Fixes V1's "brick wall" resonance
   - Allows θᵢ to stay in EDE-active region

2. **Dynamical β(φ) Coupling**:
   ```
   m_χ(φ) = m_χ,0[1 + ε sin(φ/f)]
   β(φ) = (M_Pl/m_χ) dm_χ/dφ
   ```
   - No more constant β
   - Automatically satisfies fifth-force constraints

3. **Reduced Parameter Count**:
   - V1: 5 parameters (f, n, Λ, θᵢ, β)
   - V2: 3 free parameters (f, c, θᵢ) + 1 tied (ε)
   - Λ and μ are derived, not free

4. **Validation Strategy**:
   - Start with AxiCLASS (proven working model)
   - Single-point tests BEFORE expensive MCMC
   - Grid scans to find viable regions
   - Only run MCMC after passing all diagnostic tests

---

## 🚨 Red Flags to Watch For

**STOP and debug if you see**:

1. **Phase 1**: AxiCLASS doesn't compile or gives chi2 > 2800
2. **Phase 2**: V2 CLASS doesn't compile
3. **Phase 3**: ALL single-point tests give chi2 > 2800
4. **Phase 4**: Test MCMC crashes or hangs
5. **Phase 5**: Production MCMC shows θᵢ collapse (< 1.0) or chi2 > 2800

---

## 📝 Git Workflow

### Current Branch:
```bash
git branch
# * v2-development
```

### Commit Strategy:
```bash
# After each phase milestone
git add phase2_v2/ phase3_v2/ V2_STATUS.md
git commit -m "V2: [describe milestone]"
git push origin v2-development
```

### Merge to Main:
- **DO NOT merge to main until V2 is fully validated**
- V2 must pass all tests and show chi2 < 2800 before merge
- Keep V1 frozen on main branch as reference

---

## 📊 Success Metrics

### Minimum Viable V2:
- ✅ chi2 < 2800 for Planck-only (comparable to ΛCDM)
- ✅ H₀ ≈ 72-73 km/s/Mpc with SH0ES (tension relief)
- ✅ Δχ² (V2 - ΛCDM) < 10 for full dataset

### Stretch Goals:
- ✅ Δχ² (V2 - ΛCDM) < 0 (V2 is better than ΛCDM)
- ✅ Bayesian evidence favors V2 over ΛCDM
- ✅ V2 also improves S₈ tension (via β coupling)

---

## 🎯 Next Action

**Start Phase 1: Download and Validate AxiCLASS**

```bash
cd ~/Downloads
git clone https://github.com/PoulinV/AxiCLASS.git
cd AxiCLASS
make clean && make -j8
```

**Estimated Time**: 1-2 hours for compilation and basic testing

---

**Last Commit**: `57b7d66` - Initialize V2 development  
**GitHub**: https://github.com/StevenRidder/Ridder-Field/tree/v2-development

