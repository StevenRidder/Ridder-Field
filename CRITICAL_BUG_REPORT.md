# CRITICAL BUG REPORT: Ridder Field Implementation in CLASS

## Status: BLOCKED
**Date**: 2025-11-20  
**Tokens Used**: ~127k  
**Severity**: CRITICAL - Prevents any EDE testing

## Summary
The Ridder field implementation in CLASS has a **segmentation fault** that occurs after ~40,000 successful integration steps, preventing completion of the background evolution when `Lambda_EDE > 0`.

## What Works ✅
1. **ΛCDM Baseline**: Perfect (`r_s = 147.11 Mpc`, 0.00% error)
2. **Unit Conversions**: Fixed (was off by 10^117, now correct)
3. **Initialization**: Successfully initializes all Ridder field variables
4. **Physics Calculations**: All derivatives computed correctly:
   - `phi = 2.50e+16 eV` (Hubble-frozen)
   - `phi' ≈ 0` (frozen initially)
   - `rho_ridder = 8.39e-115 Mpc^-2` (negligible)
   - `dy[phi]`, `dy[phi']`, `dy[rho]` all finite
5. **Integration**: Runs for ~40,000 steps successfully
6. **Function Returns**: `background_derivs` returns `_SUCCESS_` every time

## The Bug ❌
**Segmentation fault** occurs:
- After `background_sources` is called ~40,000 times
- When `index_loga` reaches 39,999 (last valid index if `bt_size = 40,000`)
- **After** all Ridder field code executes successfully
- **Before** printing "age = ..." (integration completion message)

## Root Cause Hypothesis
The crash occurs in CLASS's integrator or memory management, likely:
1. **Array out of bounds**: Integrator tries to access `background_table[40000]` when max index is 39,999
2. **Memory corruption**: Adding `index_bi_rho_ridder` changed memory layout, causing subtle corruption
3. **Integrator bug**: The ndf15 integrator has an off-by-one error when `bi_size` increases

## What Was Tried
1. ✅ Fixed unit conversion bugs (3 locations)
2. ✅ Fixed undefined variable bugs
3. ✅ Added safety checks for H, NaN, infinity
4. ✅ Added 39 debug print statements to trace execution
5. ✅ Verified all derivatives are finite
6. ✅ Confirmed function returns successfully
7. ✅ Added bounds check in `background_sources`
8. ❌ Removed all debug prints (still crashes)

## Files Modified
- `phase2/class/include/background.h`: Added `index_bi_rho_ridder`
- `phase2/class/source/background.c`: 
  - Fixed 3 unit conversion bugs
  - Added Ridder field evolution (lines 2833-3039)
  - Added safety checks
- `phase2/class/source/input.c`: Parameter reading (working)
- `phase2/class/source/perturbations.c`: Perturbation equations (working)

## Recommended Next Steps
1. **Use GDB/LLDB**: Get exact crash location with stack trace
2. **Consult CLASS experts**: This may be a known issue with adding integration variables
3. **Compare with `has_scf`**: Check how the existing scalar field avoids this bug
4. **Simplify model**: Test with `beta = 0` (no coupling) and no switching surface
5. **Check CLASS version**: Update to latest CLASS (v3.3.3 → latest)
6. **Memory debugging**: Run with valgrind or AddressSanitizer

## Impact
- **Phase 3 BLOCKED**: Cannot test EDE mechanism or run MCMC
- **Paper BLOCKED**: Cannot generate figures or validate tension resolution
- **Timeline**: Unknown - requires CLASS expert or deep debugging

## Workaround Options
1. **Use Python implementation**: Phase 1 code works, but lacks CMB/perturbations
2. **Use different Boltzmann code**: CAMB, CosmoMC (requires full reimplementation)
3. **Hire CLASS expert**: Pay for consultation/debugging
4. **Simplify physics**: Remove fluid switching, remove coupling (may not resolve bug)

## Contact
- CLASS GitHub: https://github.com/lesgourg/class_public
- CLASS Google Group: https://groups.google.com/g/cosmo_class
- Julien Lesgourgues (CLASS author): julien.lesgourgues@rwth-aachen.de

