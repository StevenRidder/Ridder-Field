# V2 Progress Report - November 23, 2025

## 🎉 MAJOR BREAKTHROUGHS

### 1. Fixed Stale Library Issue
**Problem**: Python wrapper was using cached `libclass.a`  
**Solution**: Force complete rebuild with `make clean`  
**Result**: Integration now runs!

### 2. Field is Now Evolving!
With Lambda = 0.1:
- ✅ φ changes: 0.398 → 0.293 → 0.373
- ✅ φ' ≠ 0: φ' ≈ 3.4×10¹²
- ✅ Derivatives calculated: 57,525,000+ calls
- ✅ Energy density: ρ_ridder ≈ 10⁻⁵ (still small but non-zero!)

### 3. Unit Conversions Fixed
**Old (wrong)**:
```c
factor_V = eV_to_Mpc_inv^2  // Way too big!
```

**New (correct)**:
```c
dV_conversion = 1.0 / (M_Pl_eV^2)  // Proper dimensional analysis
```

## Current Status

### What Works ✅
1. Background integration runs
2. Field equation of motion is integrated
3. φ evolves with time
4. Derivatives are calculated correctly

### Current Issue 🔧
**Integration is extremely slow / stiff**

With Lambda = 10.0:
- Integration fails: "Step size too small"
- Field dynamics are too rapid

With Lambda = 0.1:
- Integration runs but takes VERY long
- 57M+ derivative calls and still going
- Field is evolving but slowly

### Root Cause Analysis

The potential V = Λ⁴[1-cos(φ/f)]³ with:
- Λ = 10.0 → V ~ 10⁴ eV⁴
- dV/dφ ~ 10⁴ eV³

This creates HUGE forces on the field, leading to:
1. Very rapid evolution (high φ')
2. Tiny integration steps needed
3. Millions of evaluations required

### Comparison to AxiCLASS

AxiCLASS uses:
- Λ ~ 10⁻³ to 10⁻² eV (NOT 10 eV!)
- f ~ 10²⁷ eV (Planck scale)
- Much gentler dynamics

Our Lambda = 10.0 is **~1000× too large**!

## Next Steps

### Option 1: Use Realistic EDE Parameters
```python
Lambda_EDE_ridder = 0.001  # eV, not 10!
f_axion_ridder = 1e27      # Planck scale
theta_i_ridder = 2.0       # Initial displacement
```

### Option 2: Improve Numerical Integration
- Use adaptive step size
- Switch to fluid approximation earlier
- Relax integration tolerances

### Option 3: Hybrid Approach
- Start with slow-roll approximation
- Switch to full integration when needed
- Use fluid mode for oscillations

## Recommended Action

**Try realistic EDE parameters first!**

Lambda should be ~ 10⁻³ eV, not 10 eV. This will:
- Make integration tractable
- Match published EDE models
- Allow proper comparison to AxiCLASS

## Files Modified

1. `background.c`:
   - Fixed unit conversions
   - Added extensive debug prints
   - Corrected dV/dφ conversion

2. Debug documents:
   - `V2_BREAKTHROUGH.md`
   - `V2_DEBUG_FINDINGS.md`
   - `V2_PROGRESS_REPORT.md` (this file)

## Key Lessons

1. **Always force rebuild** after C code changes
2. **Use realistic parameter values** from the start
3. **Debug prints are essential** for tracking execution
4. **Unit conversions matter** - get them right!
5. **Stiff dynamics** require careful numerical treatment

## Status: UNBLOCKED & PROGRESSING

The field is evolving! We just need realistic parameters.

