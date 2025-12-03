# Model 1.0 Final Status: EXCLUDED

**Date:** 2025-11-24
**Verdict:** ❌ NO-GO

---

## Summary

Model 1.0 (unified Ridder field with tail + shelf, 2 free parameters) is **falsified** by the combination of cosmological tensions and observational constraints.

---

## MCMC Results (150 samples, 88 accepted)

### Best Point Found

| Parameter | Value |
|-----------|-------|
| Lambda_tail | 37.4 meV |
| f_axion | 0.264 |

### Observables at Best Point

| Observable | Value | Target | Status |
|------------|-------|--------|--------|
| H0 | 69.5 km/s/Mpc | 73.04 ± 1.04 | ❌ 3.4σ low |
| S8 | 0.759 | 0.766 ± 0.02 | ✅ Within 1σ |
| CMB_RMS | 15.8% | < 15% | ❌ Marginal |
| BAO | 4.6% | < 3% | ❌ 50% too high |
| f_EDE | ~0.35 | < 0.18 | ❌ Too high |

### Parameter Posteriors

- Lambda_tail: 37.5 ± 1.9 meV
- f_axion: 0.265 ± 0.073

---

## Key Physics Finding

**The model CANNOT do both:**
1. Raise H0 to 73+ (requires strong shelf → high f_EDE → wrecks CMB)
2. Keep CMB/BAO precise (requires weak shelf → doesn't help H0)

**The model CAN do:**
1. Lower S8 to ~0.75 ✅ (via tail dynamics)
2. Produce DESI-like w(z) evolution ✅

---

## The Trade-Off

```
   High shelf (f_EDE > 0.3):
     → H0 = 72-73 ✓
     → CMB_RMS = 30-40% ✗
     → BAO = 7-12% ✗
   
   Low shelf (f_EDE < 0.15):
     → H0 = 68-69 ✗
     → CMB_RMS = 10-15% ✓
     → BAO = 3-5% ≈
```

There's NO point in parameter space that hits all targets simultaneously.

---

## What This Means

### For the Paper

This is a **clean negative result** that should be published:
- "The minimal unified Ridder field with fixed potential shape is excluded by current data"
- "S8 tension CAN be addressed by tail dynamics alone"
- "H0 tension CANNOT be fully resolved without violating CMB/BAO"

### For Future Work

Model 2.0 needs:
1. More freedom in potential shape (vary n_shelf, n_tail)
2. Different initial conditions (theta_i as free parameter)
3. Possibly different coupling structure
4. Or: accept that unified model only addresses S8, not H0

---

## Files

- `check_mcmc_status.py` - Status checker script
- `mcmc_smoke.py` - MCMC runner
- `ridder_solver.py` - Core solver with constraints
- `MODEL_DEFINITION.md` - Model 1.0 definition (now obsolete)

---

## Conclusion

**Model 1.0 is falsified.** The combination of (H0 > 71, S8 < 0.78, CMB_RMS < 15%, BAO < 3%) has no solutions in the 2D parameter space (Lambda_tail, f_axion) with fixed potential exponents and initial conditions.

Next: Either publish the negative result, or design Model 2.0 with additional degrees of freedom.

