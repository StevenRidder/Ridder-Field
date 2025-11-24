# CRITICAL ARCHITECTURE BUG REPORT

## Date: November 24, 2024

## Summary

Both the **tail** (late-time DE) and **shelf** (EDE) potentials use forms that vanish at their minima, making them unsuitable for their intended purposes.

## Bug Details

### Current Implementation

```c
V_tail = Λ_tail⁴ * [1 - cos(θ)]^n_tail
V_shelf = Λ_EDE⁴ * W(θ) * [1 - cos(θ)]^n_EDE
```

### The Problem

When `θ → 0`:
- `1 - cos(0) = 0`
- `V_tail → 0`
- `V_shelf → 0`

This means:
1. **Tail cannot be dark energy** - dark energy requires V > 0 at the minimum
2. **Field always ends at V = 0** - no residual cosmological constant
3. **w(z=0) undefined** - can't compute equation of state at minimum

### What We Need

**For Late-Time Dark Energy (Tail):**
Need a potential with:
- Non-zero minimum at θ = 0
- V(θ=0) ≈ ρ_DE ≈ (2.3 meV)⁴

Options:
1. `V_tail = Λ⁴ * (1 + small modulation)` - constant floor with perturbation
2. `V_tail = Λ⁴ * [1 + cos(θ)/θ₀² + ...]` - expanded around minimum
3. Add explicit cosmological constant: `Omega_Lambda` separate from Ridder field

**For EDE (Shelf):**
The current form is correct for EDE that dilutes away, BUT:
- The **window function** causes issues - field free-streams when outside window
- Pure [1-cos(θ)]^n without window (like AxiCLASS) would work better

## Impact

1. **Track 1 (EDE/H₀):** Blocked by z_peak timing (separate issue)
2. **Track 2 (Late-time/S₈):** Blocked by V_tail = 0 at minimum

## Recommended Fix

### Option A: Fix Tail Potential
Replace current tail with:
```c
// Cosmological constant floor + axion-like modulation
V_tail = Λ_tail⁴ * (1.0 + α * [1 - cos(θ)])
// where α << 1 for small perturbation
```

### Option B: Use Explicit Cosmological Constant
Keep current Ridder field for EDE only, add separate `Omega_Lambda` for late-time.

### Option C: Redesign Unified Potential
Completely redesign to have proper asymptotic behavior:
- V → V₀ > 0 as θ → 0 (late-time)
- V has bump at θ ~ θ_EDE (early-time)
- V → flat plateau at θ → ∞ (inflation)

## Next Steps

1. Decide which option to pursue
2. Implement fix
3. Re-test both tracks

## Files Affected

- `phase2/class/source/ridder_unified_potential.c`: V_tail_theta(), V_shelf_theta()
- `phase2/class/source/background.c`: V_unified_theta() calls

