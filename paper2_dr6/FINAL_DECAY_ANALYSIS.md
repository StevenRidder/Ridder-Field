# Final Analysis: Ridder EDE + Dark Radiation Decay

## Executive Summary

**The α-branching (radiation decay) mechanism is now correctly implemented and working.** However, the physics imposes a hard ceiling:

- **Maximum ΔH₀ ≈ +0.7 km/s/Mpc** (taking H₀ from 67.4 → 68.1)
- **Not** the ΔH₀ ≈ +3 km/s/Mpc needed to reach H₀ ~ 70

This is not a code bug. It is the geometry of the Ridder EDE model.

---

## The Results

### Parameter Scan: (Λ, α) → H₀

| Λ (eV) | α | r_s (Mpc) | ΔH₀ (km/s/Mpc) | DR/ρ_tot @ z=1100 |
|--------|-----|-----------|----------------|-------------------|
| ΛCDM | - | 143.55 | 0.00 | - |
| 0.5 | 0.0 | 142.81 | +0.36 | 0.00% |
| 0.5 | 1.0 | 142.66 | +0.43 | 0.26% |
| 0.8 | 0.0 | 142.79 | +0.37 | 0.00% |
| 0.8 | 1.0 | 142.21 | **+0.65** | 0.97% |
| 1.0 | 0.0 | 142.85 | +0.34 | 0.00% |
| 1.0 | 1.0 | 142.15 | **+0.68** | 1.18% |
| 1.5 | 0.0 | 142.98 | +0.28 | 0.00% |
| 1.5 | 1.0 | 142.36 | +0.58 | 1.03% |
| 2.0 | 0.0 | 143.06 | +0.24 | 0.00% |
| 2.0 | 1.0 | 142.48 | +0.52 | 0.96% |

### Key Observations

1. **Pure geometric EDE (α=0)** gives ΔH₀ ≈ +0.3-0.4 km/s/Mpc
2. **Maximum α-branching (α=1)** adds another ≈ +0.3 km/s/Mpc
3. **Total maximum: ΔH₀ ≈ +0.7 km/s/Mpc**
4. **Higher Λ > 1.0 eV gives SMALLER shifts** (field overshoots)

---

## Why the Ceiling Exists

### The Energy Budget Problem

The H₀ shift scales as:
```
ΔH₀/H₀ ≈ -Δr_s/r_s ≈ ∫ f_DR(z) d ln(1+z)
```

To get ΔH₀ ~ +3 km/s/Mpc, we need:
```
Δr_s/r_s ≈ -3/67 ≈ -4.5%
```

This requires f_DR ~ 4-5% over the z = 1100-3500 window.

### What the Ridder Field Can Provide

| Quantity | Peak Value | At z=1100 |
|----------|------------|-----------|
| f_peak (max rho_ridder/rho_tot) | ~3% | ~1.5% |
| f_DR with α=1 | α × f_peak × redshift factor | ~1.2% |

The DR redshifts by factor (a_decay/a_recomb)^4 ≈ 0.01 from z=3500 to z=1100.

### The Bottleneck

Even with:
- Λ = 1-2 eV (pushing numerical stability)
- α = 1.0 (100% conversion to radiation)
- z_decay = 3500 (optimal timing)

The maximum DR fraction at recombination is **~1.2%**, not the **~4-5%** needed.

---

## What This Means for Paper 2

### The Honest Statement

The Ridder EDE model with radiation decay coupling:

1. **Works as implemented** - The geometry is correct
2. **Provides H₀ ≈ 68.0-68.1** - A modest improvement over ΛCDM
3. **Cannot reach H₀ ≈ 70** - Insufficient field amplitude

### Options Moving Forward

1. **Accept the result**: Report that Ridder EDE + decay gives H₀ ~ 68.1, which is an improvement but not a full solution to the Hubble tension

2. **Different potential**: A potential that allows f_peak ~ 10-15% at z ~ 3000-4000 could work, but would need to be carefully constructed to avoid disrupting CMB/BAO

3. **Combined mechanisms**: Ridder EDE (geometric) + enhanced N_eff (from other physics) might add up

4. **Phenomenological approach**: Use the α-branching as a "what if" to constrain how much DR the data would tolerate at high f_peak

---

## Implementation Status

### Working Features

- [x] α-branching with clean thermodynamic split
- [x] Peak tracking at z_c ~ 3000-4000  
- [x] DR redshifting correctly as a^-4
- [x] DR added to rho_tot and rho_r
- [x] Background output includes rho_dr_ridder and f_ridder

### Parameters Available

```ini
# Alpha-branching (effective fluid model)
alpha_ridder_to_dr = 0.5    # Fraction of peak energy → DR
z_ridder_decay = 3500       # Redshift of conversion

# Gamma-decay (microphysical, kinetic-limited)
Gamma_decay_ridder = 2.0    # Decay rate in units of H
```

---

## Conclusion

The napkin math was not wrong. It correctly predicted that f_DR ~ 4-5% would give ΔH₀ ~ 3 km/s/Mpc. The issue is that the Ridder monodromy potential, even at high Λ, cannot deliver f_peak > 3% without numerical instability or other issues.

The α-branching mechanism is now correctly implemented and tested. It does what it's supposed to do. The limitation is physics, not code.

**Bottom line**: Maximum H₀ ≈ 68.1 km/s/Mpc with current Ridder + decay model.

