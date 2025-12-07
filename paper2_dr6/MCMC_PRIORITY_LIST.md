# MCMC Priority List: Testing High-Amplitude EDE Island

## The Discovery

**Current Paper 2 chains have θ_i FIXED at 1.0**, which locks the model into:
- f_peak ~ 0.1-2%
- z_peak ~ 1650 (TOO LATE - after recombination!)
- Maximum H₀ ~ 69.5 km/s/Mpc

**With θ_i ~ 1.7-1.8**, the model can reach:
- f_peak ~ 10-12%  
- z_peak ~ 2500-2600 (optimal window!)
- H₀ ~ 70.5-71 km/s/Mpc
- **NO decay needed** - pure geometry does the work!

## Critical Constraints Found

| θ_i | α | ΔN_eff | Status |
|-----|---|--------|--------|
| 1.5 | 0.5 | 0.21 | ✓ OK |
| 1.5 | 1.0 | 0.41 | ⚠️ Marginal |
| 2.0 | 0.5 | 0.66 | ✗ EXCLUDED |

**θ_i > 1.8 with significant α is ruled out by N_eff!**

## Background-Only Predictions

| θ_i | Λ (eV) | α | f_peak | H₀ (km/s/Mpc) |
|-----|--------|---|--------|---------------|
| 1.0 | 0.2 | 0 | 0.1% | 69.1 |
| 1.0 | 0.5 | 1 | 2.3% | 69.5 |
| **1.5** | **0.5** | **1** | **7.1%** | **70.6** |
| **1.5** | **1.0** | **1** | **8.6%** | **70.7** |
| 2.0 | 0.5 | 1 | 15.2% | 72.8 |

## MCMC Runs to Prioritize

### Priority 1: ACT-Only with Floating θ_i ⭐
```
Config: p2_act_high_theta.yaml (NEW)
Data: Planck lowℓ + ACT DR6 only
Parameters: θ_i ∈ [0.8, 2.5], Λ ∈ [0.1, 1.5], α ∈ [0, 1]
Expected: H₀ ~ 70-71 if ACT tolerates high f_peak
Why: Most permissive data combination
```

### Priority 2: ACT-Only with θ_i = 1.5 Fixed
```
Config: Modify p2_act_only.yaml
Data: Planck lowℓ + ACT DR6 only  
Parameters: θ_i = 1.5 fixed, Λ ∈ [0.3, 1.0], α ∈ [0, 1]
Expected: H₀ ~ 70.5
Why: Targeted test of the island
```

### Priority 3: Full Data (No DESI) with Floating θ_i
```
Config: Modify prod_p2_dr6_ede.yaml
Data: Planck lowℓ + lensing + ACT + old BAO + SN (NO DESI)
Parameters: θ_i ∈ [0.8, 2.0], Λ ∈ [0.1, 1.0], α ∈ [0, 1]
Expected: H₀ ~ 69-70
Why: Tests if pre-DESI data allows high amplitude
```

### Priority 4: Full Data with DESI
```
Config: prod_p2_dr6_ede.yaml modified
Data: Everything including DESI
Parameters: θ_i floating
Expected: See if DESI kills the island
Why: Final reality check
```

## Key Questions Each Run Answers

1. **Priority 1**: Does ACT DR6 damping tail tolerate f_peak ~ 8-15%?
2. **Priority 2**: What's the χ² at the H₀ ~ 70.5 point specifically?
3. **Priority 3**: Do BAO + SN rule out high θ_i even without DESI?
4. **Priority 4**: Is there ANY surviving parameter space with DESI?

## What Success Looks Like

If Priority 1 finds a region with:
- H₀ > 70 km/s/Mpc
- Δχ² < 0 vs ΛCDM
- θ_i ~ 1.3-1.8
- f_peak ~ 5-10%

Then we have found the **high-amplitude island** where α-branching matters.

## Current Paper 2 Limitation

The existing `prod_p2_dr6_ede.yaml` has:
```yaml
theta_i_ridder: 1.0  # FIXED - this is the problem!
```

This means the MCMC never explores the high-amplitude regime where the physics gets interesting.

## Files Created

- `configs/p2_act_high_theta.yaml` - Ready to run Priority 1
- This document - MCMC priority list

