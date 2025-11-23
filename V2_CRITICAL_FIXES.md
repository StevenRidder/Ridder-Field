# V2 Critical Fixes - New Feedback Incorporated

**Date**: November 23, 2025  
**Status**: Must implement BEFORE touching CLASS

---

## 🚨 Three Major "Holes" to Avoid

### Hole A: Late-Time DE Mechanism
**Problem**: Field oscillates at z~6000 → energy decays → ρ_φ ≈ 0 at z=0  
**Fix**: Rely on V_offset (cosmological constant) for late acceleration  
**Action**: Don't try to make field become Quintessence

### Hole B: Derivative Trap in CLASS
**Problem**: V''(φ) errors cause crashes or wrong perturbations  
**Fix**: Use sympy to generate d²V/dφ² automatically  
**Action**: Run `ridder_v2_check.py` BEFORE writing C code

### Hole C: Coupling Window Movement
**Problem**: If φ* = α θ_i f, coupling window moves with θ_i in MCMC  
**Fix**: Use simpler coupling without extra parameters  
**Action**: β(φ) = β₀ (φ/f)² / (1 + (φ/f)²)

---

## ✅ Revised V2 Coupling (Simplified)

### Old (Too Complex):
```python
β(φ) = β₀ * exp(-λ (φ/f)²)  # Extra λ parameter
```

### New (Better):
```python
β(φ) = β₀ * (φ/f)² / (1 + (φ/f)²)
```

**Why better**:
- ✅ No extra λ parameter
- ✅ Naturally 0 at φ=0 (today, no fifth force)
- ✅ ≈ β₀ when φ≫f (early universe, full coupling)
- ✅ Smooth transition, no jagged likelihood

---

## 📋 New Phase 0: Python Sandbox (BEFORE CLASS)

### Step 1: Run Symbolic Check
```bash
cd /Users/steveridder/Git/Ridder-Field/phase3/tools
python3 ridder_v2_check.py
```

### Step 2: Review Plots
Check for:
- ✅ V(φ) smooth "staircase" shape
- ✅ V''(φ) > 0 at minimum (stable)
- ✅ V''(φ) no wild oscillations
- ✅ β(φ) → 0 as φ → 0
- ✅ β(φ) ≈ β₀ at high φ

### Step 3: Copy Generated C Code
Script outputs:
- Optimized C code for `background.c`
- Coupling code for `perturbations.c`
- Uses CSE (Common Subexpression Elimination)
- Guaranteed mathematically correct

### Step 4: Only THEN Touch CLASS
- Paste C code into CLASS
- Compile
- Run single-point test
- Check background evolution

---

## 🎯 Updated Implementation Order

### Phase 0: Python Sandbox (NEW - 1 hour)
1. Run `ridder_v2_check.py`
2. Verify plots look physical
3. Generate C code
4. Document any issues

### Phase 1: AxiCLASS Validation (2-3 days)
- Download AxiCLASS
- Reproduce their results
- Understand parameter knobs

### Phase 2: Port to Our Fork (3-4 days)
- Apply AxiCLASS as patches (not wholesale copy)
- Verify output matches

### Phase 3: V2 Modifications (5-7 days)
- Implement flattened potential (from Python script)
- Implement simplified β(φ) (from Python script)
- Remove θ_i as free parameter (attractor)

### Phase 4: MCMC (5-7 days)
- Tier 1: Planck only
- Tier 3: Planck + BAO + SH0ES
- Tier 4: Full dataset

---

## 📊 Success Criteria (REVISED AGAIN)

### Minimum Viable V2:
- ✅ χ² comparable to ΛCDM for Planck-only
- ✅ H₀ shifted upward vs ΛCDM (e.g., 68.5 → 70.0)
- ✅ Tension reduced in σ (e.g., 4.4σ → 3.0σ)
- ✅ No catastrophic χ² hit

### Stretch Goals:
- ✅ H₀ ≈ 72-73 with Planck-lite + SH0ES
- ✅ Δχ² ≤ 0 for some combinations
- ✅ S₈ tension also improved via β coupling

### NOT Success Criteria:
- ❌ H₀ = 72-73 with full Planck (unrealistic)
- ❌ Field drives late-time acceleration (use V_offset instead)

---

## 🔧 Files Created

- ✅ `phase3/tools/ridder_v2_check.py` - Symbolic math + C code generator
- ✅ `V2_ACTION_PLAN.md` - Decision point summary
- ✅ `V2_CRITICAL_FIXES.md` - This file

---

## ⚡ Immediate Next Action

**Run the Python script**:
```bash
cd /Users/steveridder/Git/Ridder-Field/phase3/tools
python3 ridder_v2_check.py
```

Review plots, then decide:
- **Option A**: Start V2 implementation (download AxiCLASS)
- **Option B**: Wait for V1 bug-fixed results (6-12 hours)
- **Option C**: Parallel track (monitor V1 + start V2)
