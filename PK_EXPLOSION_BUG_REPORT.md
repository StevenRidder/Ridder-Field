# CRITICAL BUG REPORT: P(k) Explosion

**Date**: November 20, 2024  
**Status**: UNRESOLVED - Requires CLASS Expert Consultation  
**Severity**: CRITICAL - Blocks MCMC (Phase 3)

## Summary
Matter power spectrum `P(k)` at z=0 is **40,000× larger** than ΛCDM baseline when Ridder field is enabled, despite all other observables (CMB, background) being correct.

## Observations
- **ΛCDM**: `P(k=1e-5) = 47.6 (Mpc/h)³` ✓ Correct
- **Ridder**: `P(k=1e-5) = 1.9e6 (Mpc/h)³` ✗ Wrong (40,000× too large)
- **CMB**: Clean, no discontinuities ✓ Correct
- **Background**: `r_s` reduced by 14% as expected ✓ Correct
- **H(z)**: Matches theory ✓ Correct

## Diagnostics Performed
1. ✅ Verified Ridder perturbations are tiny (`δ ~ 10⁻³`) at cutoff
2. ✅ Verified stress-energy contributions are gated correctly
3. ✅ Verified `delta_m` definition excludes Ridder field
4. ✅ Verified `Omega_Lambda` closure is identical in both cases
5. ✅ Verified CDM equations are unmodified
6. ✅ Tested with/without perturbation cutoffs - no difference
7. ✅ Verified background `rho_ridder` decays correctly

## Hypothesis
The P(k) explosion occurs **despite** Ridder perturbations being negligible. This suggests:
- Possible issue with how CLASS computes P(k) when background evolution is modified
- Possible numerical artifact in growth function integration
- Possible gauge transformation issue in P(k) output (though gauge is forced to Newtonian)

## What Works
- Background evolution (H(z), r_s, rho_ridder decay)
- CMB power spectra (C_l^TT, C_l^EE, C_l^TE)
- Perturbation integration (stable to z=0, no crashes)
- Gauge restriction (Newtonian only, fails safely in synchronous)

## What Doesn't Work
- Matter power spectrum P(k) at z=0
- Growth kink analysis (depends on P(k))

## Recommended Next Steps
1. **Consult CLASS developers** - This may be a known issue with modified background evolution
2. **Compare with `fld` module** - Test if standard fluid dark energy has same issue
3. **Check transfer functions** - Verify `delta_cdm(k,z)` evolution directly
4. **Test with `output=mTk`** - Get raw transfer functions instead of P(k)

## Impact on Paper
- **CMB analysis**: ✅ Ready for publication
- **Background/H0**: ✅ Ready for publication
- **Structure formation**: ❌ Blocked until P(k) is fixed
- **MCMC**: ❌ Blocked (requires P(k) for likelihood)

## Files for CLASS Developers
- `phase2/class/source/perturbations.c` (lines 7190-7216, 9447-9483)
- `phase2/class/source/background.c` (Ridder field implementation)
- `phase3/scan/scan_1.00.ini` (test case)
- This report

## Workaround for arXiv v1
Publish **background + CMB only**. Frame P(k)/structure formation as "future work requiring full WKB treatment of oscillating field perturbations."

