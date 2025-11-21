# CLASS Modifications for Ridder Field

This directory contains the modified CLASS source files needed to implement the Ridder Field model.

## Files Modified

1. **`include/background.h`**
   - Added `scf_pot_ridder` to `enum scf_potential_type`
   - Added `LambdaEDE4` to `background` struct
   - Added Ridder field parameters to `background` struct

2. **`source/input.c`**
   - Added parameter reading for `Lambda_EDE_ridder`, `f_axion_ridder`, `theta_i_ridder`, `beta_ridder`, `n_ridder`
   - Added potential name parser for "ridder"
   - Set `has_scf = _TRUE_` when `has_ridder = _TRUE_`
   - Enabled shooting mechanism for Ridder field

3. **`source/background.c`**
   - Added `case scf_pot_ridder:` in `V_scf()`, `dV_scf()`, and `ddV_scf()` functions
   - Implemented Ridder potential: `V(φ) = Λ⁴ [1 - cos(φ/f)]ⁿ`
   - Set initial conditions: `phi_ini = theta_i * f_axion_ridder`

4. **`source/perturbations.c`**
   - Added 3-term coupling for CDM-Scalar Field interaction:
     - CDM Continuity: Energy exchange term
     - CDM Euler: Momentum drag term
     - Scalar Field KG: Backreaction term

## How to Apply

1. Copy the modified files to your CLASS installation:
   ```bash
   cp patches/class/background.h.modified phase2/class/include/background.h
   cp patches/class/input.c.modified phase2/class/source/input.c
   cp patches/class/background.c.modified phase2/class/source/background.c
   cp patches/class/perturbations.c.modified phase2/class/source/perturbations.c
   ```

2. Recompile CLASS:
   ```bash
   cd phase2/class
   make clean
   make
   ```

## Verification

After applying the modifications, test with:
```bash
cd phase2/class
./class ../../phase3/ridder_smoketest_spec.ini
```

Expected results (from last night's successful run):
- r_s ≈ 139.06 Mpc
- f_EDE peak ≈ 15.46% at z ≈ 6697
- H₀ ≈ 70-71 km/s/Mpc

## Notes

- The `phase2/class` directory is a separate git repository
- These modified files are tracked in the main repository for backup
- Always verify the modifications match the specification in `FINAL_RESTORATION_REPORT.md`

