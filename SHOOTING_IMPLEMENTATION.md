# Ridder Field Lambda Shooting Implementation

## Summary
Successfully implemented Lambda shooting mechanism in `background.c`. The code is ready but needs parameters added to the background structure and wired into initialization.

## Changes Made to background.c

### New Functions Added (lines ~3529-3700):
1. `background_clear_tables()` - Cleans up tables between shooting trials
2. `background_init_trial()` - Runs background solve for a trial Lambda value
3. `background_ridder_measure_peak()` - Measures f_EDE peak in redshift range
4. `background_shoot_Lambda()` - Bisection loop that finds Lambda for target f_EDE

## Required Changes to background.h

Add these parameters to `struct background`:

```c
/* Ridder EDE shooting controls */
short use_ridder_shooting;      /* _TRUE_ to enable Lambda shooting, _FALSE_ for manual */
double ridder_fEDE_target;       /* Target peak f_EDE, e.g. 0.10 */
double ridder_zc_target;         /* Optional target z_c (unused for now, future feature) */
double ridder_c_slow;            /* Slow-roll coefficient for phi'_ini, default 1.0 */
```

## Required Changes to background_init()

Replace the current `background_init` function with:

```c
int background_init(struct precision *ppr, struct background *pba) {
  int status;

  /* Step 1: define all indices, including Ridder rho and p */
  class_call(background_indices(ppr, pba),
             pba->error_message,
             pba->error_message);

  if (pba->has_ridder == _TRUE_ && pba->use_ridder_shooting == _TRUE_) {
    
    /* Lambda shooting to match target f_EDE */
    double log10_Lambda_min = 10.0;   /* 10^10 eV */
    double log10_Lambda_max = 16.0;   /* 10^16 eV */
    double z_min            = 500.0;
    double z_max            = 10000.0;
    double tol_f            = 1e-3;    /* 0.1% tolerance */

    class_call(background_shoot_Lambda(ppr, pba,
                                       log10_Lambda_min,
                                       log10_Lambda_max,
                                       z_min,
                                       z_max,
                                       tol_f),
               pba->error_message,
               pba->error_message);

    /* On return, pba->Lambda_EDE_ridder is tuned and tables are filled */
  }
  else {
    /* No shooting, standard run with manually specified Lambda */
    class_call(background_solve(ppr, pba),
               pba->error_message,
               pba->error_message);
  }

  return _SUCCESS_;
}
```

## Required Changes to Initial Conditions

In the section where Ridder ICs are set (around line ~2430), replace:

```c
double phi_prime_ridder_ini = 0.0;
```

With slow-roll calculation:

```c
/* Slow-roll initial derivative: 3 H a phi' = - dV/dphi */
double H_ini = pvecback[pba->index_bg_H];  /* H already computed at a_ini */
double dV_dphi = dV_ridder(pba, phi_ridder_ini);
double phi_prime_ridder_ini = - pba->ridder_c_slow * dV_dphi / (3.0 * H_ini * a);
```

Note: This assumes H is already available from `background_functions` called at initial time.
If not, use: `H_ini = sqrt(rho_tot * 8 * M_PI * G / 3)` with appropriate units.

## Required Changes to input.c

Add parsing for new parameters:

```c
class_read_int("use_ridder_shooting", pba->use_ridder_shooting);
class_read_double("ridder_fEDE_target", pba->ridder_fEDE_target);
class_read_double("ridder_c_slow", pba->ridder_c_slow);

/* Set defaults */
if (pba->use_ridder_shooting == _UNINITIALIZED_) pba->use_ridder_shooting = _FALSE_;
if (pba->ridder_fEDE_target == _UNINITIALIZED_) pba->ridder_fEDE_target = 0.10;
if (pba->ridder_c_slow == _UNINITIALIZED_) pba->ridder_c_slow = 1.0;
```

## Testing

### Test 1: Manual Lambda (existing behavior)
```python
cosmo.set({
    'Lambda_EDE_ridder': 1e13,
    'theta_i_ridder': 1.5,
    'use_ridder_shooting': False,  # Manual mode
    ...
})
```

### Test 2: Automatic shooting
```python
cosmo.set({
    'theta_i_ridder': 1.5,
    'use_ridder_shooting': True,    # Enable shooting
    'ridder_fEDE_target': 0.10,     # Target 10% EDE
    'ridder_c_slow': 1.0,           # Full slow-roll IC
    ...
})
# Lambda will be found automatically!
```

## Benefits

1. **No more guessing Lambda**: User specifies desired f_EDE, code finds Lambda
2. **Better IC timing**: Slow-roll phi' adapts to Lambda scale
3. **Robust convergence**: Bisection guarantees finding Lambda if it exists in bracket
4. **Diagnostic output**: Can watch shooting converge iteration by iteration

## Next Steps

1. Add parameters to `background.h`
2. Update `background_init()` as shown above  
3. Add slow-roll IC calculation
4. Add input parsing in `input.c`
5. Test with shooting enabled to verify convergence

## Status

✅ Core shooting functions implemented in background.c
⏳ Waiting for structure/init/input updates to activate

