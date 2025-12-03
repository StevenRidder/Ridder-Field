# Phase 3 Debug Status

## Summary
We are implementing the Ridder field (RC-X* model) in CLASS to test the EDE mechanism for resolving the Hubble tension.

## Bugs Fixed
1. **Unit Conversion Bug (CRITICAL)**: Fixed incorrect conversion factor from eV to Mpc. Was using `eV_in_inv_Mpc = 1.5637e29` (inverse), corrected to `eV_to_Mpc_inv = 6.39e-30`.
2. **Undefined Variable**: Fixed `phi_ridder` undefined in `background_derivs` (should be `y[pba->index_bi_phi_ridder]`).

## Current Issue
**Segmentation Fault in `background_derivs`**

### What We Know
- Initialization completes successfully
- First call to `background_functions` succeeds
- `background_derivs` is called ~3400 times successfully
- Crash occurs during integration, likely when specific numerical conditions are met
- Debug output shows:
  - `phi = 2.50e+16 eV` (constant, Hubble-frozen)
  - `ddV = -2.45e-33` (negative, field at potential maximum)
  - `m_eff = 0` (correctly handled)
  - `rho_cdm = 1.34e-08 Mpc^-2`

### Likely Causes
1. **NaN propagation**: Despite checks, NaN might be generated in derivative calculations
2. **Array out of bounds**: `pvecback` or `y` array access with invalid index
3. **Infinite loop**: Integrator step size collapsing to zero
4. **Stack overflow**: Excessive recursion (unlikely given debug output)

### Next Steps
1. **Simplify**: Disable switching surface logic temporarily
2. **Validate**: Test with smaller `Lambda_EDE` values (0.01 eV instead of 0.5 eV)
3. **Instrument**: Add NaN checks before all array writes
4. **Alternative**: Use GDB or lldb to get exact crash location

## Files Modified
- `phase2/class/include/background.h`: Added `index_bi_rho_ridder`
- `phase2/class/source/background.c`: 
  - Fixed unit conversions (3 locations)
  - Added Ridder field evolution equations
  - Added fluid mode switching logic
  - Added extensive debug prints (to be removed)
- `phase2/class/source/input.c`: Parameter reading (already done)
- `phase2/class/source/perturbations.c`: Perturbation equations (already done)

## What Works
- ΛCDM baseline (`Lambda = 0`): **PERFECT** (`r_s = 147.11 Mpc`)
- Initialization of Ridder field: **SUCCESS**
- First ~3400 integration steps: **SUCCESS**

## What Doesn't Work
- EDE mode (`Lambda > 0`): **SEGFAULT** after ~3400 steps

## Recommendation
Given the time spent debugging (>120k tokens), I recommend:
1. **Consult CLASS experts** or use a debugger (GDB/LLDB)
2. **Simplify the model** temporarily (disable coupling, disable switching)
3. **Test incrementally** with very small `Lambda` values
4. **Compare with existing scalar field** implementation in CLASS (`has_scf`)

