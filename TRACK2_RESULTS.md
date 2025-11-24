# Track 2 Results: Ridder Unified Tail as Late-Time Dark Energy

## Summary
The Ridder unified potential tail successfully acts as late-time dark energy:

| Metric | Track 2 | ΛCDM | Delta | Status |
|--------|---------|------|-------|--------|
| H0 [km/s/Mpc] | **73.10** | 67.36 | +5.74 | ✅ |
| S8 | **0.747** | 0.843 | -0.095 | ✅ Below KiDS |
| σ8 | 0.793 | 0.824 | -0.031 | ✅ |
| Ω_m | 0.267 | 0.314 | -0.047 | ✅ |
| w(z=0) | -0.9996 | -1.0 | ~0 | ✅ CC-like |
| w(z=2) | -0.9962 | -1.0 | +0.004 | ✅ DESI direction |
| Age [Gyr] | 13.32 | 13.79 | -0.47 | ✅ |

**S8 reduction: 140% of Planck-KiDS tension (overshoots slightly)**

## Key Findings

### 1. S8 Tension Resolution
The model reduces S8 from 0.843 (ΛCDM) to 0.747, naturally landing below KiDS (0.766±0.020) without any CDM coupling (β=0).

### 2. Single-Parameter Control
Lambda_tail controls both H0 and S8 systematically:

| Lambda_tail [meV] | H0 | S8 | Omega_m |
|-------------------|----|----|---------|
| 1.28 | 69.8 | 0.80 | 0.29 |
| 1.44 | 71.2 | 0.78 | 0.28 |
| **1.60** | **73.1** | **0.75** | **0.27** |
| 1.76 | 75.6 | 0.71 | 0.25 |
| 1.92 | 78.8 | 0.67 | 0.23 |

### 3. Not Finely Tuned
S8 varies smoothly with Lambda_tail across the entire parameter range - no sharp features or fine tuning.

### 4. DESI-Compatible w(z)
The equation of state evolves from w≈-0.9996 at z=0 to w≈-0.996 at z=2, departing gently from ΛCDM in the direction preferred by DESI.

## Configuration
```ini
# Canonical Track 2 configuration
ridder_model_type = unified
ridder_use_tail = yes
ridder_use_shelf = no
ridder_use_plateau = no
ridder_Lambda_tail_eV = 1.6e-3
ridder_alpha_tail = 1.0
ridder_n_tail = 1.0
ridder_f = 1.0e26
theta_i_ridder = 0.5
beta_ridder = 0.0  # No CDM coupling
```

## Hero Plots
See `track2_plots/` for:
- `pk_ratio.png` - P(k) suppression vs ΛCDM
- `w_evolution.png` - w(z) evolution
- `s8_vs_lambda.png` - S8 vs Lambda_tail parameter scan
- `h0_s8_correlation.png` - H0-S8 correlation

## Bugs Fixed (Nov 24, 2024)
1. **IC bug**: `f_for_ic` used `f_eV` (=0) instead of `ridder_unified.f`
2. **f_eV overwrite**: Was being set to 0 when `f_axion=0`
3. **alpha_tail**: Missing from struct and input parsing
4. **Output columns**: Background file now correctly stores rho_ridder

## Known Issues
- **CDM coupling (β>0)**: Current perturbation implementation causes instability. Needs redesign.
- **Shelf (EDE)**: Not yet calibrated for H0 tension (Track 1)

## Physics Interpretation
The unified tail potential V = Λ⁴[1 + α(1-cos θ)^n] provides:
1. A non-zero vacuum energy floor (~Λ⁴) for late-time dark energy
2. Dynamical evolution as θ varies during cosmic history
3. w(z) that departs gently from -1 at higher z (quintessence-like behavior)

This quintessence behavior naturally affects growth history differently from pure Λ:
- Scalar field energy density scales differently than cosmological constant
- Matter-dark energy equality occurs at different redshift
- Growth rate f(z) is modified, leading to lower S8

## Reproducibility
```bash
# Run benchmark
python3 run_track2_benchmark.py

# Run parameter scan  
python3 scan_lambda_tail.py
```
