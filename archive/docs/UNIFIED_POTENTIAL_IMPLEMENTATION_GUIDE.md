# Ridder Unified Potential Implementation Guide

**Status:** Step 1 (Header) COMPLETE  
**Next:** Steps 2-5 (Input parsing, potential functions, integration, testing)

---

## Completed: Step 1 - Header Definitions ✓

Added to `background.h`:
- `enum ridder_model_type` with `simple_ede` and `unified` options
- `struct ridder_unified_params` with all potential parameters
- Added `ridder_unified` field to `struct background`

---

## Step 2: Input Parsing (input.c)

### 2.1 Add String-to-Enum Helper

Add near top of `input.c`, with other helper functions:

```c
static int interpret_ridder_model_type(char *name, int *model_type, ErrorMsg errmsg) {
  if ((strstr(name, "simple_ede") != NULL) || (strstr(name, "simple") != NULL)) {
    *model_type = ridder_model_simple_ede;
    return _SUCCESS_;
  }
  if ((strstr(name, "unified") != NULL)) {
    *model_type = ridder_model_unified;
    return _SUCCESS_;
  }
  sprintf(errmsg, "ridder_model_type must be 'simple_ede' or 'unified', got '%s'", name);
  return _FAILURE_;
}
```

### 2.2 Add Parameter Reading Block

Find where Ridder parameters are currently read (search for `Lambda_EDE_ridder` or `theta_i_ridder`).

After the existing Ridder parameter block, add:

```c
/* ===================================================================== */
/* Ridder Unified Potential Parameters                                   */
/* ===================================================================== */

if (pba->has_ridder == _TRUE_) {
  
  /* Default to simple_ede for backwards compatibility */
  pba->ridder_unified.model_type = ridder_model_simple_ede;
  
  /* Read model type */
  class_call(parser_read_string(pfc, "ridder_model_type", &string1, &flag1, errmsg),
             errmsg, errmsg);
  if (flag1 == _TRUE_) {
    class_call(interpret_ridder_model_type(string1, &pba->ridder_unified.model_type, errmsg),
               errmsg, errmsg);
  }
  
  /* Global field properties */
  class_read_double("ridder_f", pba->ridder_unified.f);
  /* Fallback: use f_axion_ridder if ridder_f not specified */
  if (pba->ridder_unified.f == 0.0) {
    pba->ridder_unified.f = pba->f_axion_ridder;
  }
  
  /* Component toggles */
  class_read_flag("ridder_use_tail", pba->ridder_unified.use_tail);
  class_read_flag("ridder_use_shelf", pba->ridder_unified.use_shelf);
  class_read_flag("ridder_use_plateau", pba->ridder_unified.use_plateau);
  
  /* Tail parameters */
  class_read_double("ridder_Lambda_tail_eV", pba->ridder_unified.Lambda_tail);
  class_read_double("ridder_n_tail", pba->ridder_unified.n_tail);
  
  /* Shelf (EDE) parameters */
  class_read_double("ridder_Lambda_EDE_eV", pba->ridder_unified.Lambda_EDE);
  class_read_double("ridder_n_EDE", pba->ridder_unified.n_EDE);
  class_read_double("ridder_theta_EDE_low", pba->ridder_unified.theta_EDE_low);
  class_read_double("ridder_theta_EDE_high", pba->ridder_unified.theta_EDE_high);
  class_read_double("ridder_sigma_theta_EDE", pba->ridder_unified.sigma_theta_EDE);
  
  /* Plateau (inflation) parameters */
  class_read_double("ridder_Lambda_inf_eV", pba->ridder_unified.Lambda_inf);
  class_read_double("ridder_theta0_inf", pba->ridder_unified.theta0_inf);
  class_read_double("ridder_theta_inf_on", pba->ridder_unified.theta_inf_on);
  class_read_double("ridder_sigma_inf", pba->ridder_unified.sigma_inf);
  class_read_double("ridder_n_inf", pba->ridder_unified.n_inf);
}
```

### 2.3 Add Default Values

In the initialization section where defaults are set (search for `pba->Lambda_EDE_ridder = 0.0`), add after existing Ridder defaults:

```c
/* Unified potential defaults */
pba->ridder_unified.model_type = ridder_model_simple_ede;
pba->ridder_unified.f = 1.0;

/* Component toggles: default to tail+shelf only (no inflation) */
pba->ridder_unified.use_tail = _TRUE_;
pba->ridder_unified.use_shelf = _TRUE_;
pba->ridder_unified.use_plateau = _FALSE_;

/* Tail defaults (late DE) */
pba->ridder_unified.Lambda_tail = 2.3e-3;  /* ~meV scale for Omega_Lambda */
pba->ridder_unified.n_tail = 3.0;

/* Shelf defaults (EDE) - match v2 optimal */
pba->ridder_unified.Lambda_EDE = 1.5;      /* eV, from v2 optimization */
pba->ridder_unified.n_EDE = 3.0;
pba->ridder_unified.theta_EDE_low = 0.5;
pba->ridder_unified.theta_EDE_high = 2.0;
pba->ridder_unified.sigma_theta_EDE = 0.2;

/* Plateau defaults (inflation) - conservative initial values */
pba->ridder_unified.Lambda_inf = 1.0e-3;   /* Will be tuned for inflation */
pba->ridder_unified.theta0_inf = 5.0;
pba->ridder_unified.theta_inf_on = 8.0;
pba->ridder_unified.sigma_inf = 1.0;
pba->ridder_unified.n_inf = 1.0;
```

---

## Step 3: Unified Potential Functions (background.c)

These functions implement V(θ) = V_tail + V_shelf + V_plateau

### Location
Add near existing Ridder potential functions (search for `V_ridder` or similar)

### Implementation File

Due to length, see `ridder_unified_potential_functions.c` (to be created as separate file or added to background.c)

Key functions needed:
- `V_tail_theta()`, `dV_tail_dtheta()`, `d2V_tail_dtheta2()`
- `V_shelf_theta()`, `dV_shelf_dtheta()`, `d2V_shelf_dtheta2()`
- `V_plateau_theta()`, `dV_plateau_dtheta()`, `d2V_plateau_dtheta2()`
- `V_unified_theta()`, `dV_unified_dtheta()`, `d2V_unified_dtheta2()`

---

## Step 4: Integration Hook (background.c)

Find the main Ridder potential function (likely `background_ridder_potential` or similar).

Modify to branch on model_type:

```c
int background_ridder_potential(double phi,
                                double *V,
                                double *dV_dphi,
                                double *d2V_dphi2,
                                struct background *pba) {
  
  /* Branch on model type */
  if (pba->ridder_unified.model_type == ridder_model_simple_ede) {
    /* Use existing v2 potential (unchanged) */
    return background_ridder_simple_ede_potential(phi, V, dV_dphi, d2V_dphi2, pba);
  }
  
  /* Unified potential */
  const struct ridder_unified_params *rp = &(pba->ridder_unified);
  double theta = phi / rp->f;
  
  double Vtheta = V_unified_theta(theta, rp);
  double dV_dtheta = dV_unified_dtheta(theta, rp);
  double d2V_dtheta2 = d2V_unified_dtheta2(theta, rp);
  
  *V = Vtheta;
  *dV_dphi = dV_dtheta / rp->f;
  *d2V_dphi2 = d2V_dtheta2 / (rp->f * rp->f);
  
  return _SUCCESS_;
}
```

Note: If v2 code is not factored into a separate function, create `background_ridder_simple_ede_potential()` by moving existing code there first.

---

## Step 5: Test Configurations

### 5.1 Tail Only (Late DE Check)

`test_unified_tail_only.ini`:
```ini
use_ridder = yes
ridder_model_type = unified

# Global
ridder_f = 1.0

# Toggles
ridder_use_tail = yes
ridder_use_shelf = no
ridder_use_plateau = no

# Tail params
ridder_Lambda_tail_eV = 2.3e-3
ridder_n_tail = 3.0

# Standard cosmology
H0 = 67.36
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544

output = tCl
write background = yes
```

**Expected:** Omega_Lambda ~ 0.7, w ~ -1.0

### 5.2 Tail + Shelf (EDE Check - Should Match V2)

`test_unified_ede.ini`:
```ini
use_ridder = yes
ridder_model_type = unified

# Global
ridder_f = 2.435e27  # M_Pl in eV

# Toggles
ridder_use_tail = yes
ridder_use_shelf = yes
ridder_use_plateau = no

# Tail
ridder_Lambda_tail_eV = 2.3e-3
ridder_n_tail = 3.0

# Shelf (map from v2 conservative benchmark)
ridder_Lambda_EDE_eV = 1.5
ridder_n_EDE = 3.0
ridder_theta_EDE_low = 0.5
ridder_theta_EDE_high = 2.0
ridder_sigma_theta_EDE = 0.5

# Standard cosmology
H0 = 67.36
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544

# CDM coupling (from v2 conservative)
beta_ridder = 0.15
beta_z_c = 3000.0
beta_sigma_z = 0.5

output = tCl
lensing = yes
l_max_scalars = 2500
write background = yes
```

**Expected:** Should reproduce v2 conservative benchmark results:
- ΔH₀ ≈ +3.14 km/s/Mpc
- z_peak ≈ 3000
- f_peak ≈ 13-15%

### 5.3 Plateau Only (Inflation Smoke Test)

`test_unified_inflation.ini`:
```ini
use_ridder = yes
ridder_model_type = unified

# Global
ridder_f = 1.0

# Toggles
ridder_use_tail = no
ridder_use_shelf = no
ridder_use_plateau = yes

# Plateau
ridder_Lambda_inf_eV = 1.0e-3
ridder_theta0_inf = 5.0
ridder_theta_inf_on = 8.0
ridder_sigma_inf = 1.0
ridder_n_inf = 1.0

# Minimal cosmology (inflation only)
H0 = 67.36
omega_b = 0.0
omega_cdm = 0.0

output = background
write background = yes
```

**Expected:** Field rolls on plateau, can extract slow-roll parameters

---

## Step 6: Verification Script

`test_unified_potential.py`:
```python
#!/usr/bin/env python3
"""
Smoke test for unified potential implementation

Tests:
1. Tail only → late DE
2. Tail + Shelf → EDE (should match v2)
3. Plateau only → inflation
"""

import subprocess
import numpy as np

def run_test(ini_file, test_name):
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print('='*70)
    
    result = subprocess.run(
        ['./phase2/class/class', ini_file],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode != 0:
        print(f"❌ FAILED: {result.stderr[:200]}")
        return False
    
    print(f"✅ SUCCESS: CLASS ran without errors")
    return True

tests = [
    ('test_unified_tail_only.ini', 'Tail Only (Late DE)'),
    ('test_unified_ede.ini', 'Tail + Shelf (EDE)'),
    ('test_unified_inflation.ini', 'Plateau Only (Inflation)')
]

print("="*70)
print("UNIFIED POTENTIAL SMOKE TESTS")
print("="*70)

results = {}
for ini, name in tests:
    results[name] = run_test(ini, name)

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
for name, passed in results.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
```

---

## Implementation Checklist

- [x] Step 1: Header definitions (`background.h`) ✓
- [ ] Step 2: Input parsing (`input.c`)
- [ ] Step 3: Potential functions (`background.c`)
- [ ] Step 4: Integration hook (modify existing potential function)
- [ ] Step 5: Create test INI files
- [ ] Step 6: Run smoke tests
- [ ] Step 7: Verify v2 behavior unchanged with `simple_ede` mode
- [ ] Step 8: Verify unified mode produces expected physics

---

## Next Actions

1. **Implement Steps 2-4** (input parsing + potential functions)
2. **Compile and test** with `simple_ede` mode first (should be identical to v2)
3. **Create test INIs** for unified mode
4. **Run smoke tests** for each regime
5. **Document** which unified parameters map to v2 benchmarks

---

## Notes

- All v2 behavior is preserved via `simple_ede` mode
- Unified mode adds new physics without breaking existing code
- Can switch between models with single INI flag
- v2 benchmarks will guide unified parameter ranges
- Once working, v2 becomes "shelf-only case" of unified model

**END OF IMPLEMENTATION GUIDE**

