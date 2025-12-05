# CLASS EDE Setup: Known Issues and Fixes

## Quick Reference

**Working Configuration:**
```yaml
theory:
  classy:
    extra_args:
      gauge: newtonian
      use_ridder: "yes"
      ridder_model_type: v3_canon      # NOT unified!
      ridder_use_shelf: "yes"
      ridder_use_tail: "no"
      ridder_f_eV: 3.0e26              # Field range
      theta_i_ridder: 2.8              # Initial angle
      ridder_Lambda_EDE_eV: 0.1        # MUST be 0.1 or ≥0.6
      ridder_a_c: 0.000309             # Critical scale factor
      ridder_sigma_lna: 0.656          # Transition width
```

---

## Issue 1: Model Type Selection

### Problem
There are two Ridder field models in CLASS:
- `unified` (model_type=1) - **BROKEN**, causes perturbation failures
- `v3_canon` (model_type=2) - **WORKS**

### Symptoms
```
Error: Could not find random point giving finite posterior after 20000 tries
```
or
```
Error: Step size too small in perturbations_solve
```

### Fix
Always use `ridder_model_type: v3_canon` in your config.

### Parameter Differences

| Unified Model (broken) | V3 Canon Model (working) |
|------------------------|--------------------------|
| `Lambda_EDE_ridder` | `ridder_Lambda_EDE_eV` |
| `f_axion_ridder` | `ridder_f_eV` |
| `n_ridder` | (built into potential) |

---

## Issue 2: Lambda_EDE_eV Stability

### Problem
The perturbation solver becomes numerically unstable for certain Lambda values.

**Tested ranges (with f_eV=3e26):**
| Lambda_EDE_eV | Result |
|---------------|--------|
| 0.1 | ✅ Works (f_EDE ~2.6% at z~1000) |
| 0.2-0.5 | ❌ "Step size too small" error |
| 0.6+ | ✅ Works (f_EDE ~3.3% at z~7000+) |

### Symptoms
```
Error in Class: perturbations_solve
=> evolver_ndf15: Step size too small: step:9.89e-14, minimum:9.89e-14
```

### Fix
Use `ridder_Lambda_EDE_eV: 0.1` (fixed, not sampled) or values ≥0.6.

For Paper 2 control run, we use Lambda=0.1 and only sample `ridder_a_c`.

---

## Issue 3: NaN in Effective Mass Calculation

### Problem
The switching check computes `m_eff = sqrt(ddV)` where `ddV` is the second derivative of the potential. When ddV < 0 (field at local maximum), this produces NaN.

### Symptoms
```
SWITCH_CHECK: z=9.68e+04 a=1.03e-05 3H=6.17e+04 m_eff=-nan
```
This causes likelihood evaluations to fail silently.

### Fix
Applied in `phase2/class/source/background.c`:
```c
// OLD (broken):
double m_eff_eV = sqrt(ddV_val);

// NEW (fixed):
double m_eff_eV = (ddV_val > 0) ? sqrt(ddV_val) : 0.0;
```

---

## Issue 4: Excessive Debug Output

### Problem
CLASS has many `printf` statements that output every N steps, causing:
- Log files growing to MBs in minutes
- ~2.5 sec/evaluation (instead of ~1 sec)
- Slow initial point finding

### Symptoms
Log file contains thousands of lines like:
```
DERIVS: call#=5000 a=2.31e-04 phi=...
V_RIDDER_RAW: a=2.94e-13 phi=5.60e+26...
RIDDER DEBUG (adding to rho_tot)...
```

### Fix
Applied in `phase2/class/source/background.c`:
```c
// Changed conditions from:
if (deriv_counter < 10 || deriv_counter % 5000 == 0)
// To:
if (0)  // Never print
```

Same for: `v_counter`, `rho_add_counter`, `deriv_entry_counter`

---

## Rebuilding CLASS After Fixes

After modifying `background.c`:

```bash
cd ~/Ridder-Field/phase2/class
make clean
make -j4

cd python
source ~/cosmo_env/bin/activate
pip uninstall classy -y
pip install --no-build-isolation .

# Test
python3 -c "from classy import Class; print('OK')"
```

---

## Testing a Configuration

Before running an MCMC chain, test the CLASS parameters directly:

```python
from classy import Class

c = Class()
c.set({
    'output': 'tCl, pCl, lCl',
    'l_max_scalars': 2508,
    'lensing': 'yes',
    'gauge': 'newtonian',
    'use_ridder': 'yes',
    'ridder_model_type': 'v3_canon',
    'ridder_use_shelf': 'yes',
    'ridder_use_tail': 'no',
    'ridder_f_eV': 3.0e26,
    'theta_i_ridder': 2.8,
    'ridder_Lambda_EDE_eV': 0.1,
    'ridder_a_c': 0.000309,
    'ridder_sigma_lna': 0.656,
    'H0': 69.0,
    'omega_b': 0.02237,
    'omega_cdm': 0.12,
    'tau_reio': 0.055,
    'A_s': 2.1e-9,
    'n_s': 0.965,
})
try:
    c.compute()
    cl = c.lensed_cl(2508)
    print(f"✅ SUCCESS! Got Cls to ℓ={len(cl['tt'])-1}")
except Exception as e:
    print(f"❌ FAILED: {e}")
```

---

## EDE Fraction Check

To verify the EDE is actually contributing:

```python
bg = c.get_background()
import numpy as np
rho_r = bg['(.)rho_ridder']
rho_tot = rho_r + bg['(.)rho_g'] + bg['(.)rho_b'] + bg['(.)rho_cdm'] + bg['(.)rho_ur']
f_ede = rho_r / rho_tot
print(f"Peak f_EDE = {np.max(f_ede):.3f} at z = {bg['z'][np.argmax(f_ede)]:.0f}")
```

Expected results:
- Lambda=0.1: f_EDE ~2.6% at z~1000
- Lambda=0.6: f_EDE ~3.3% at z~7000

---

## Troubleshooting Checklist

1. **Chain won't find initial point:**
   - Check Lambda_EDE_eV is in stable range (0.1 or ≥0.6)
   - Look for `m_eff=-nan` in logs (NaN bug)
   - Narrow cosmology priors to known-good region

2. **"Step size too small" error:**
   - Lambda_EDE_eV in unstable range (0.2-0.5)
   - Solution: Use Lambda=0.1

3. **Log file growing rapidly (MBs/min):**
   - Debug output not suppressed
   - Rebuild CLASS with counter checks set to `if (0)`

4. **f_ridder ≈ 0 (no EDE contribution):**
   - Wrong model type (unified instead of v3_canon)
   - Wrong parameter names (Lambda_EDE_ridder vs ridder_Lambda_EDE_eV)

---

## Files Modified

1. `phase2/class/source/background.c`
   - Line ~565: NaN fix for m_eff
   - Lines ~550, 630, 3330, 3380: Debug output suppression

2. `phase4/configs/run_control_planck_only.yaml`
   - Uses v3_canon with stable Lambda=0.1

---

*Last updated: 2025-12-05 after debugging session*

