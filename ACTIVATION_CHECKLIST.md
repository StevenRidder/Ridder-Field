# Ridder Shooting Mechanism - Activation Checklist

## Status: Code Written, Needs Wiring

✅ Shooting functions implemented in `background.c` (lines ~3529-3731)  
⏳ Structural changes needed to activate  

---

## Step-by-Step Activation

### 1. Add Parameters to `background.h`

**Location:** Find `struct background` definition

**Add these fields:**
```c
  /**************************************************************/
  /* Ridder field EDE parameters */
  /**************************************************************/
  
  /* Existing Ridder parameters */
  short has_ridder;
  double Lambda_EDE_ridder;
  double theta_i_ridder;
  double beta_ridder;
  double f_axion_ridder;
  int n_ridder;
  short ridder_fluid_mode;
  /* ... other existing fields ... */
  
  /* NEW: Shooting mechanism parameters */
  short use_ridder_shooting;      /* _TRUE_ to enable Lambda shooting */
  double ridder_fEDE_target;       /* Target peak f_EDE (e.g., 0.10 for 10%) */
  double ridder_zc_target;         /* Optional: target z_c (future feature) */
  double ridder_c_slow;            /* Slow-roll coefficient for phi'_ini */
```

### 2. Update `background_init()` 

**Location:** Find `int background_init(struct precision *ppr, struct background *pba)`

**Replace with:**
```c
int background_init(struct precision *ppr, struct background *pba) {
  int status;

  /* Always compute indices first */
  class_call(background_indices(ppr, pba),
             pba->error_message,
             pba->error_message);

  /* Check if Ridder shooting is enabled */
  if (pba->has_ridder == _TRUE_ && pba->use_ridder_shooting == _TRUE_) {
    
    /* Lambda shooting to match target f_EDE */
    double log10_Lambda_min = 10.0;   /* 10^10 eV */
    double log10_Lambda_max = 16.0;   /* 10^16 eV - adjust if needed */
    double z_min            = 500.0;  /* Search window for peak */
    double z_max            = 10000.0;
    double tol_f            = 1e-3;   /* 0.1% tolerance on f_EDE */

    if (pba->background_verbose > 0) {
      printf("\nRidder Lambda shooting: target f_EDE = %.3f\n", pba->ridder_fEDE_target);
    }

    class_call(background_shoot_Lambda(ppr, pba,
                                       log10_Lambda_min,
                                       log10_Lambda_max,
                                       z_min,
                                       z_max,
                                       tol_f),
               pba->error_message,
               pba->error_message);

    /* On return: Lambda is tuned, tables are filled */
  }
  else {
    /* Standard path: use manually specified Lambda */
    class_call(background_solve(ppr, pba),
               pba->error_message,
               pba->error_message);
  }

  return _SUCCESS_;
}
```

### 3. Implement Slow-Roll Initial Conditions

**Location:** Find where Ridder initial conditions are set (around line 2430)

**Current code:**
```c
double phi_ridder_ini = pba->f_axion_ridder * pba->theta_i_ridder;
double phi_prime_ridder_ini = 0.0;  // OLD: always zero

pvecback_integration[pba->index_bi_phi_ridder] = phi_ridder_ini;
pvecback_integration[pba->index_bi_phi_prime_ridder] = phi_prime_ridder_ini;
```

**Replace with:**
```c
double phi_ridder_ini = pba->f_axion_ridder * pba->theta_i_ridder;

/* NEW: Slow-roll initial derivative */
/* At this point, pvecback should already have H computed via background_functions */
double H_ini = pvecback[pba->index_bg_H];
double dV_dphi = dV_ridder(pba, phi_ridder_ini);
double phi_prime_ridder_ini = - pba->ridder_c_slow * dV_dphi / (3.0 * H_ini * a);

/* DIAGNOSTIC: Print during development */
if (pba->background_verbose > 1) {
  printf("Ridder slow-roll IC: H_ini=%.2e, dV/dphi=%.2e, phi'_ini=%.2e\n",
         H_ini, dV_dphi, phi_prime_ridder_ini);
}

pvecback_integration[pba->index_bi_phi_ridder] = phi_ridder_ini;
pvecback_integration[pba->index_bi_phi_prime_ridder] = phi_prime_ridder_ini;
```

**Note:** If `H` is not yet available, compute it from Friedmann equation:
```c
double rho_tot = pvecback[pba->index_bg_rho_tot];  
double H_ini = sqrt(8.0 * _PI_ * _G_ * rho_tot / 3.0);  /* In CLASS units */
```

### 4. Add Input Parsing to `input.c`

**Location:** Find section where Ridder parameters are read

**Add:**
```c
  /* Shooting mechanism parameters */
  class_read_int("use_ridder_shooting", pba->use_ridder_shooting);
  class_read_double("ridder_fEDE_target", pba->ridder_fEDE_target);
  class_read_double("ridder_zc_target", pba->ridder_zc_target);
  class_read_double("ridder_c_slow", pba->ridder_c_slow);
  
  /* Set defaults */
  if (pba->use_ridder_shooting == _UNINITIALIZED_INT_) {
    pba->use_ridder_shooting = _FALSE_;
  }
  if (pba->ridder_fEDE_target == 0.0) {
    pba->ridder_fEDE_target = 0.10;  /* Default: 10% EDE */
  }
  if (pba->ridder_zc_target == 0.0) {
    pba->ridder_zc_target = 3000.0;  /* Optional target (not used yet) */
  }
  if (pba->ridder_c_slow == 0.0) {
    pba->ridder_c_slow = 1.0;  /* Full slow-roll by default */
  }
```

---

## Testing Procedure

### Phase 1: Compilation Check
```bash
cd phase2/class
make clean
make -j8
```
Expected: Clean compilation with no errors

### Phase 2: Manual Lambda (Baseline)
Test file: `test_manual.ini`
```ini
Lambda_EDE_ridder = 1e13
theta_i_ridder = 1.5
use_ridder_shooting = no
```
Expected: Runs as before (existing behavior preserved)

### Phase 3: Shooting Test
```bash
python3 test_shooting.py
```
Expected output:
```
RIDDER_SHOOT iter= 1  log10_Lambda=13.000  f_peak=0.00234  z_peak=...
RIDDER_SHOOT iter= 2  log10_Lambda=14.500  f_peak=0.45123  z_peak=...
RIDDER_SHOOT iter= 3  log10_Lambda=13.750  f_peak=0.08567  z_peak=...
...
RIDDER_SHOOT iter= 8  log10_Lambda=13.456  f_peak=0.10001  z_peak=...
Lambda shooting converged: Lambda=2.859e+13 eV → f_EDE=0.1000 at z=3245
```

### Phase 4: Consistency Check
1. Note the converged Lambda from Phase 3
2. Run manual mode with that Lambda
3. Verify f_EDE matches (within tolerance)

### Phase 5: Range Check
Test `ridder_fEDE_target` = [0.05, 0.10, 0.15]
- All should converge
- Lambda should increase monotonically with f_EDE
- z_peak should be in [500, 10000] range

---

## Success Criteria

✅ Compiles without errors  
✅ Manual mode still works (backward compatible)  
✅ Shooting converges in <15 iterations  
✅ Converged Lambda reproduces target f_EDE  
✅ Different targets produce sensible Lambda values  
✅ Slow-roll IC produces small w_ini ≈ -1  

---

## Rollback Plan

If shooting causes problems:
1. Set `use_ridder_shooting = no` in input file
2. Code falls back to manual Lambda mode
3. No existing functionality is broken

---

## After Activation

Once spot-checks pass:

1. **Guard diagnostic printf:**
   ```c
   #ifdef RIDDER_DEBUG
   printf("RIDDER_SHOOT iter=%d...\n", ...);
   #endif
   ```

2. **Document in README:**
   - How to use shooting mode
   - Typical f_EDE targets (0.05-0.15)
   - What to do if bracket fails

3. **Run physics validation:**
   - Generate CMB spectrum
   - Check H₀ shift is reasonable
   - Verify EDE decays before recombination

---

## Current Status

📝 Code written and ready in `background.c`  
⏳ Awaiting structural changes (Steps 1-4 above)  
🧪 Test script ready (`test_shooting.py`)  

**Estimated time to activate:** 30-45 minutes of careful editing

