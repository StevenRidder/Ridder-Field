# Track 1: EDE Shelf Results

## Summary

Track 1 implements **Early Dark Energy (EDE)** using the Ridder unified shelf potential. The shelf produces a transient energy density bump around recombination that shrinks the sound horizon and increases H₀.

## Calibrated Configuration

```ini
ridder_model_type = unified
ridder_use_tail = no
ridder_use_shelf = yes
ridder_m_axion = 7e4     # Controls z_peak
ridder_f_axion = 0.25    # Controls f_EDE amplitude
ridder_n_EDE = 3.0
ridder_theta_EDE_low = 0.5
ridder_theta_EDE_high = 3.5
ridder_f = 7.305e26
theta_i_ridder = 2.5
```

## Key Results

| Metric | ΛCDM | EDE (f_axion=0.25) | Change |
|--------|------|-------------------|--------|
| f_EDE | 0 | 0.138 | +0.138 |
| z_peak | - | 3969 | - |
| r_s [Mpc] | 147.04 | 143.69 | -2.28% |
| H₀ [km/s/Mpc] | 67.36 | 68.93 | +1.57 |
| σ₈ | 0.8236 | 0.8445 | +0.0209 |
| S₈ | 0.8426 | 0.8637 | +0.0210 |

## Physics Interpretation

1. **EDE Episode**: The shelf potential creates an EDE bump with f_EDE ≈ 0.14 peaking at z ≈ 4000, close to recombination.

2. **Sound Horizon Shrinkage**: The increased expansion rate during the EDE epoch reduces the comoving sound horizon by 2.28%, which shifts H₀ up via the inverse r_s scaling.

3. **H₀ Shift**: The +1.6 km/s/Mpc increase is in the correct direction but insufficient for full tension resolution (need ~5 km/s/Mpc). This is expected - standard EDE with f_EDE ~ 0.1-0.15 gives modest H₀ shifts.

4. **S₈ Impact**: The small S₈ increase (+0.02) is a known feature of EDE - it accelerates expansion during matter domination, slightly enhancing growth.

## Bugs Fixed

1. **dV_shelf inconsistency**: The derivative `dV_shelf_dtheta` was using Lambda^4 scaling while `V_shelf_theta` used m²f² scaling. Fixed to use consistent V_scale logic.

2. **Source file duplication**: Two copies of `ridder_unified_potential.c` existed in different locations. The Makefile compiled the old version. Fixed by syncing to correct location.

## Parameter Dependencies

- **m_axion**: Controls z_peak (larger m → higher z_peak)
- **f_axion**: Controls f_EDE amplitude (larger f_axion → larger f_EDE)
- Rough scaling: z_peak ∝ m_axion, f_EDE ∝ f_axion²

## Status

✓ Track 1 EDE mechanism working correctly
✓ Sound horizon shrinks as expected  
✓ H₀ increases in correct direction
✓ S₈ impact is modest
⚠ Full H₀ tension resolution requires larger f_EDE than standard EDE allows

## Next Steps

1. Test combined tail + shelf (unified model with both active)
2. Explore CDM coupling to address S₈
3. Write Track 1 paper section

