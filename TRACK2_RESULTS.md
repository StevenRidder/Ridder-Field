# Track 2 Results: Ridder Unified Tail as Late-Time Dark Energy

## Summary
The Ridder unified potential tail successfully acts as late-time dark energy, achieving:

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| S8 | **0.747** | <0.76 (KiDS) | ✅ Below KiDS |
| σ8 | 0.79 | ~0.8 | ✅ Good |
| Ω_m | 0.27 | ~0.3 | ✅ Reasonable |
| w(z=0) | -0.9996 | ≈-1 | ✅ CC-like |
| w(z=3) | -0.96 | >-1 | ✅ DESI direction |
| H0 | 73 km/s/Mpc | 67-74 | ✅ In range |
| Age | 13.3 Gyr | 13-14 | ✅ Good |

## Key Finding
**The tail alone (β=0, no CDM coupling) naturally reduces S8 below the KiDS tension value while producing DESI-style w(z) evolution.**

## Configuration
```ini
ridder_model_type = unified
ridder_use_tail = yes
ridder_use_shelf = no
ridder_use_plateau = no
ridder_Lambda_tail_eV = 1.6e-3
ridder_alpha_tail = 1.0
ridder_n_tail = 1.0
ridder_f = 1.0e26
theta_i_ridder = 0.5
beta_ridder = 0.0
```

## Bugs Fixed (Nov 24, 2024)
1. **IC bug**: `f_for_ic` used `f_eV` (=0) instead of `ridder_unified.f`
2. **f_eV overwrite**: Was being set to 0 when `f_axion=0`
3. **alpha_tail**: Missing from struct and input parsing
4. **Output columns**: Background file now correctly stores rho_ridder

## Known Issues
- **CDM coupling (β>0)**: Current perturbation implementation either causes P(k) instability or enhances (rather than suppresses) structure growth. Needs redesign.
- **Shelf (EDE)**: Not yet calibrated for H0 tension (Track 1)

## Physics Interpretation
The unified tail potential V = Λ⁴[1 + α(1-cos θ)^n] provides:
1. A non-zero vacuum energy floor (~Λ⁴) for dark energy
2. Dynamical evolution as θ varies
3. w(z) that departs from -1 at higher z (quintessence-like)

This quintessence behavior naturally affects growth history differently from pure Λ, leading to the lower S8.

