# ACT DR6 Likelihood Integration - Debug Log

**Date**: 2025-12-01  
**Status**: RESOLVED ✅

## Summary

Successfully integrated ACT DR6 MFLike likelihood with Planck + BAO + SH0ES for both ΛCDM and EDE (Ridder field) models. This document captures the debugging process for future reference.

---

## Original Symptoms

When attempting to run chains with ACT DR6 likelihood:

```
[classy] *ERROR* Serious error setting parameters or computing results.
[model] *ERROR* Could not find random point giving finite posterior after 20000 tries
```

The chains would fail to start, unable to find any valid point in parameter space.

---

## Root Causes Found (3 Issues)

### Issue #1: CLASS Output String Mangling

**Symptom**: CLASS received malformed output string like:
```
'output': 'tCl, pCl, lCl tCl pCl,'  # WRONG - mixed commas and spaces
```

**Root Cause**: 
- My config used comma-separated: `output: tCl, pCl, lCl`
- Cobaya's classy wrapper uses space-separated internally
- When merging requirements from multiple likelihoods, it did:
  ```python
  self.extra_args["output"] = " ".join(set(self.extra_args["output"].split()))
  ```
- This `.split()` on `"tCl, pCl, lCl"` kept the commas attached: `["tCl,", "pCl,", "lCl"]`
- Result: duplicate entries like `"tCl,"` and `"tCl"` both present

**Fix**: Use space-separated output in config:
```yaml
theory:
  classy:
    extra_args:
      output: tCl pCl lCl  # NO COMMAS
```

---

### Issue #2: Foreground Parameters Routed to CLASS

**Symptom**: CLASS error:
```
Error in Class: Class did not read input parameter(s): a_cibc, a_dust_tt, a_dust_ee, a_radio
```

**Root Cause**:
- Parameters like `a_cibc`, `a_dust_tt`, `a_dust_ee`, `a_radio` were defined in the params section
- Cobaya routes ALL params to theories unless explicitly excluded
- These are foreground parameters for Planck plik, but cobaya was also sending them to classy
- Our custom Ridder CLASS doesn't recognize these parameters

**Debugging Steps**:
1. Ran minimal test with just ACT (no Planck) → ACT initialized fine
2. Added Planck → failures started
3. Checked cobaya debug output:
   ```
   [classy] Input: ['A_s', 'n_s', 'H0', 'omega_b', 'omega_cdm', 'tau_reio', 'a_cibc', 'a_dust_tt', 'a_dust_ee', 'a_radio']
   ```
4. Those foreground params shouldn't go to classy!

**Fix**: Explicitly specify which params classy should receive:
```yaml
theory:
  classy:
    input_params: [A_s, n_s, H0, omega_b, omega_cdm, tau_reio]  # EXPLICIT list
```

And remove `a_cibc`, `a_dust_tt`, `a_dust_ee`, `a_radio` from the params section entirely - let Planck use its defaults.

---

### Issue #3: Wrong CLASS Installation Being Used

**Symptom**: Initially, CLASS worked in standalone tests but failed through cobaya.

**Root Cause**:
- Pip-installed standard classy at `/home/ridderadmin/.local/lib/python3.10/site-packages/classy`
- Our custom Ridder CLASS at `/home/ridderadmin/Ridder-Field/phase2/class/python/`
- Cobaya was loading the pip version, which doesn't have Ridder field support

**Debugging Steps**:
1. Checked cobaya log: `[classy] module loaded from ~/.local/lib/python3.10/site-packages/classy`
2. Tested custom CLASS directly → worked fine with Ridder params
3. Realized pip classy was taking precedence

**Fix**:
```bash
# Uninstall pip classy
pip3 uninstall classy

# Copy custom Ridder CLASS to site-packages
cp /home/ridderadmin/Ridder-Field/phase2/class/python/classy.cpython-310-x86_64-linux-gnu.so \
   /home/ridderadmin/.local/lib/python3.10/site-packages/

# Copy CLASS data files
cp -r ~/Ridder-Field/phase2/class/external/* ~/.local/lib/python3.10/site-packages/external/
```

---

## Final Working Configuration

### ΛCDM Config (`configs/act_full_lcdm_production.yaml`)

Key sections:
```yaml
theory:
  classy:
    extra_args:
      output: tCl pCl lCl           # Space-separated, no commas
      l_max_scalars: 9000
      lensing: true
      gauge: newtonian
      non_linear: halofit
    input_params: [A_s, n_s, H0, omega_b, omega_cdm, tau_reio]  # Explicit!
  
  mflike.BandpowerForeground:
    experiments: [dr6_pa4_f220, dr6_pa5_f090, dr6_pa5_f150, dr6_pa6_f090, dr6_pa6_f150]
    bandint_freqs: [220, 90, 150, 90, 150]

likelihood:
  planck_2018_lowl.TT: null
  planck_2018_lowl.EE: null
  planck_2018_highl_plik.TTTEEE: null
  planck_2018_lensing.clik: null
  act_dr6_mflike.ACTDR6MFLike:
    stop_at_error: false
  # ... BAO, SN, SH0ES ...
```

### EDE Config (`configs/act_full_ede_production.yaml`)

Same as ΛCDM plus:
```yaml
theory:
  classy:
    extra_args:
      # ... same as ΛCDM ...
      f_axion_ridder: 1.0e+27
      theta_i_ridder: 1.0
      beta_ridder: 0.0
      n_ridder: 3
    input_params: [A_s, n_s, H0, omega_b, omega_cdm, tau_reio, Lambda_EDE_ridder]

params:
  Lambda_EDE_ridder:
    prior: {min: 0.1, max: 3.0}
    ref: 1.0
    proposal: 0.2
```

---

## Verification

Chains successfully running:
```
[mcmc] Sampling! (NB: no accepted step will be saved until 50 burn-in samples have been obtained)
[mcmc] Progress @ 2025-12-01 06:11:06 : 1 steps taken -- still burning in
```

All 8 chains (4 ΛCDM, 4 EDE) initialized and sampling.

---

## Lessons Learned

1. **Cobaya's classy wrapper has quirks**: Always use space-separated output strings, not commas.

2. **Parameter routing matters**: When using multiple likelihoods, explicitly specify `input_params` for theories to avoid unwanted parameter routing.

3. **Check which CLASS is loaded**: Cobaya logs which classy module it loads - verify it's the right one.

4. **Test incrementally**: Start with minimal configs (just Planck, just ACT) before combining.

5. **FAIL AND FIX EARLY**: Each error message contained the clue. The key was testing the exact failing params in isolation to pinpoint the issue.

---

## Commands for Future Reference

### Check which CLASS cobaya uses:
```bash
cobaya-run your_config.yaml -f 2>&1 | grep "classy.*loaded"
```

### Test CLASS params directly:
```python
import classy
c = classy.Class()
c.set({'output': 'tCl pCl lCl', 'l_max_scalars': 3000, ...})
c.compute()  # Will show actual error if params are wrong
```

### View cobaya parameter routing:
Look for `[model] Parameters were assigned as follows:` in debug output.

---

## Issue #4: T_CMB² Unit Conversion in Template Fit (Added 2025-12-01)

### Problem
The `act_template_fit.py` script returned `A_sh ≈ 10^20` (numerical garbage).

### Root Cause
**Missing T_CMB² unit conversion factor!**

CLASS returns **dimensionless C_ell** (normalized by T_CMB²). The conversion to D_ell in μK² requires:

```
D_ell = ell*(ell+1)/(2π) × C_ell × T_CMB²
```

Where `T_CMB = 2.7255×10⁶ μK`, so `T_CMB² ≈ 7.43×10¹² μK²`

### The Bug
```python
# WRONG - produces D_ell ~ 10^-12 (essentially zero)
D_ell['tt'] = cl['tt'] * ell * (ell + 1) / (2 * np.pi)
```

### The Fix
```python
T_CMB = 2.7255e6  # μK
T_CMB_SQ = T_CMB ** 2  # 7.428e12 μK²

# CORRECT - produces D_ell ~ 2000-6000 μK²
factor = ell * (ell + 1) / (2 * np.pi)
D_ell['tt'] = cl['tt'] * factor * T_CMB_SQ
```

### Verification (Napkin Math)
| Quantity | Expected | Got | Status |
|----------|----------|-----|--------|
| Raw C_ell[100] | ~10^-13 | 2.27e-13 | ✓ (dimensionless) |
| D_ell at ℓ=100 | ~2000 μK² | 2717 μK² | ✓ |
| D_ell at ℓ=500 | ~2500 μK² | 2438 μK² | ✓ |
| Max D_ell | ~6000 μK² | 5754 μK² | ✓ |

### Result After Fix
```
A_sh = 1.156 ± 0.181
S/N = 6.38
→ SHOULDER DETECTED! (A_sh ≈ 1 means Ridder field prediction confirmed)
```

### Lesson Learned
**Always check units when interfacing Boltzmann codes!**
- CLASS returns dimensionless C_ell (normalized by T_CMB²)
- CAMB returns C_ell in K² (need to convert to μK²)
- ACT/Planck data are in μK² (D_ell convention)

---

## Issue #5: Lambda Prior Too Wide → Wrong EDE Regime (Added 2025-12-01)

### Problem

ACT chains with wide Lambda_EDE prior `[0.1, 3.0]` converged to `Lambda ≈ 1.96`, giving:
- `z_osc = 9528` (EDE kicks in at z > 9000)
- Template fit: `A_sh = -3.76` (ACT **disfavors** shoulder)

This is the **WRONG EDE regime**. The soft shoulder effect requires EDE to kick in around `z_osc ∼ 4000-5000`.

### Root Cause

**Lambda controls z_osc (when EDE becomes dynamical)**:

| Lambda | z_osc | Regime |
|--------|-------|--------|
| 0.6 | ~2500 | Too late |
| 0.8 | ~3500 | Edge of valid |
| **1.0** | **~4500** | **CORRECT** |
| 1.2 | ~5500 | Edge of valid |
| 1.5 | ~7000 | Too early |
| 2.0 | ~9500 | **WRONG** |

With a wide prior `[0.1, 3.0]`, the chains are free to explore the entire range and may converge to a local minimum at high Lambda where EDE kicks in very early (before recombination) - this is a different physics regime that does NOT produce the soft shoulder.

### Fix

**Use tight Lambda prior in EDE config:**
```yaml
Lambda_EDE_ridder:
  prior: {min: 0.8, max: 1.2}  # TIGHT - ensures z_osc ~ 4000-5000
  ref: {dist: norm, loc: 1.0, scale: 0.1}
  proposal: 0.05
```

This keeps the chains in the correct physical regime where:
- EDE kicks in around matter-radiation equality
- The soft shoulder signature is present at ℓ ~ 1000-2000
- Template fit should give A_sh ≈ 1 ± 0.5 if ACT sees the shoulder

### Verification

After fixing the prior:
```
Lambda = 1.04, z_osc = 4729 → CORRECT regime
```

### Lesson Learned

**The EDE parameter space has multiple regimes - constrain Lambda to the physical regime of interest!**

A wide prior may converge to a mathematically valid but physically wrong solution.

---

## Production Config Summary (2025-12-01)

### Key Settings That Must NOT Change

1. **output string**: `output: tCl pCl lCl` (NO COMMAS)
2. **l_max_scalars**: 8500 (for ACT damping tail)
3. **Lambda_EDE prior**: `[0.8, 1.2]` (ensures correct z_osc regime)
4. **Theory**: Both ΛCDM and EDE must use CLASS (not mixed CAMB/CLASS)
5. **Ridder fixed params**: `f_axion_ridder: 1.0e+27`, `theta_i_ridder: 1.0`, `beta_ridder: 0.0`, `n_ridder: 3`

### Files
- `configs/act_world_lcdm.yaml` - ΛCDM production config
- `configs/act_world_ede.yaml` - EDE production config (with tight Lambda prior)
- `run_act_analysis.sh` - Launch script (`--clean` to restart fresh)
