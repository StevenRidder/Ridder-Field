# Files for Code Review & Validation

Per your request, here are the critical files to verify correctness:

## 1. Core Implementation Files

### `ridder_unified_potential.c` ✅ Already provided
- Tail, Shelf, Plateau potential pieces
- Derivatives (analytic)
- θ → φ conversion via `ridder_f`

### `background.h` - REQUESTED
Location: `phase2/class/include/background.h`

Key sections to review:
- `enum ridder_model_type` definition
- `struct ridder_unified_params` with all parameters
- Integration into main `struct background`

### `input.c` - REQUESTED  
Location: `phase2/class/source/input.c`

Key sections:
- Parameter parsing for `ridder_model_type`
- Reading unified params (Lambda_EDE, theta windows, etc)
- Logic that sets `has_ridder = TRUE`

### `background.c` - REQUESTED (Ridder sections)
Location: `phase2/class/source/background.c`

Key functions:
- `V_ridder()` - calls unified vs v2 potential
- Unit conversion: eV^4 → Mpc^-2
- Equation of motion for φ (Klein-Gordon)
- CDM coupling application

### `perturbations.c` - REQUESTED (Ridder sections)
Location: `phase2/class/source/perturbations.c`

Key sections:
- Ridder perturbation variables setup
- Use of V, dV/dφ, d²V/dφ² 
- Fluid mode switch logic

## 2. Analysis Scripts - REQUESTED

### `extract_w_of_z.py`
Extracts w(z) from background files
- Columns: z, rho_ridder, p_ridder
- Computes w = p/rho

### `extract_s8_quick.py`
Computes S₈ from CLASS outputs
- σ₈ from P(k) via top-hat window
- Ω_m from parameters
- S₈ = σ₈ √(Ω_m / 0.3)

### `extract_cmb_shoulder.py`
CMB residuals and soft shoulder detection
- Loads TT/EE/TE spectra
- Computes ΔCℓ/Cℓ
- Measures width of deviations

---

## 3. Validation Tests Needed

Based on your framework, here's what we need to implement:

### A. Analytic Limit Checks (C-level unit tests)

**Small-θ tail:**
```c
// Test: V_tail(θ→0) ~ ½ Λ_tail^4 θ² for n_tail=1
double theta_small = 1e-6;
double V_code = V_tail_theta(theta_small, params);
double V_analytic = 0.5 * pow(params->Lambda_tail, 4) * theta_small * theta_small;
assert(fabs(V_code - V_analytic) / V_analytic < 1e-6);
```

**Shelf interior:**
```c
// Test: W(θ) ≈ 1 when theta_low < θ < theta_high
double theta_mid = (params->theta_EDE_low + params->theta_EDE_high) / 2.0;
double W = W_EDE(theta_mid, params);
assert(fabs(W - 1.0) < 0.01);  // W should be ~1 in window center
```

**Plateau at large θ:**
```c
// Test: V_plateau ~ Λ_inf^4 |θ|/θ0 for |θ| >> θ0
double theta_large = params->theta0_inf * 10.0;
double V_code = V_plateau_theta(theta_large, params);
double F_expected = theta_large / params->theta0_inf;  // Linear approximation
double V_analytic = pow(params->Lambda_inf, 4) * F_expected;
// Should be within factor of 2 (rough check for turn-on function)
assert(V_code / V_analytic > 0.5 && V_code / V_analytic < 2.0);
```

### B. Derivative Consistency (Finite Difference)

```c
// Test derivatives via finite difference
double theta = 1.5;  // Test point
double delta = 1e-8;

// Analytic
double V, dV, d2V;
V_unified_theta_and_derivs(theta, params, &V, &dV, &d2V);

// Finite difference
double V_plus = V_unified_theta(theta + delta, params);
double V_minus = V_unified_theta(theta - delta, params);
double dV_FD = (V_plus - V_minus) / (2.0 * delta);

double rel_error = fabs(dV - dV_FD) / fabs(dV);
assert(rel_error < 1e-6);
```

### C. Unit Conversion Cross-Check

Compare to stock CLASS quintessence:
```c
// Set up simple V = ½ m² φ² in both Ridder and quintessence modules
// Both should give same H(z) for same initial Ω_φ
```

### D. ΛCDM Recovery Tests

**Test 1: Ridder completely off**
```ini
use_ridder = no
→ H(z), Ω_m, CMB Cℓ must match pure ΛCDM to ~1e-6
```

**Test 2: Tail near minimum (θ ≈ 0)**
```ini
use_ridder = yes
ridder_use_tail = yes
ridder_use_shelf = no
ridder_use_plateau = no
theta_i_ridder = 0.01  # Near minimum
Lambda_tail tuned for Omega_Lambda ~ 0.69
→ Should reproduce ΛCDM H(z) and CMB
```

**Test 3: Shelf-only matches v2 EDE**
```ini
use_ridder = yes  
ridder_use_tail = no
ridder_use_shelf = yes
ridder_use_plateau = no
# Set shelf params to match old v2 potential
→ Background ρ_ridder(z) and CMB should match v2 runs
```

### E. Convergence Tests

```python
# Run same .ini with different tolerances
tolerances = [1e-3, 1e-6, 1e-9]
results = []

for tol in tolerances:
    ini['tol_background_integration'] = tol
    run_class(ini)
    results.append(extract_H_z(output))

# Check convergence
for i in range(len(results)-1):
    diff = max(abs(results[i] - results[i+1]))
    assert diff < tol[i]  # Should converge at tol level
```

---

## 4. Specific Code Sections to Verify

### Unit Conversions in background.c

```c
// From your code:
double eV_to_Mpc_inv = 1.5633836731e29;  // Check this value
double M_Pl_eV = 2.435e27;                // Reduced Planck mass

double factor_V = (eV_to_Mpc_inv * eV_to_Mpc_inv) / (3.0 * M_Pl_eV * M_Pl_eV);
double factor_rho = 1.0 / (3.0 * M_Pl_eV * M_Pl_eV);

// Verify:
// φ in eV, φ' in eV/Mpc
// Kinetic: ½(φ')² = eV²/Mpc²
// With eV→Mpc conversion: → Mpc⁻²
// Potential: V in eV⁴
// With factor_V: V × (eV/Mpc)² / M_Pl² → Mpc⁻²

// Both kinetic and potential should have same units after conversion
```

### Klein-Gordon Equation

```c
// φ'' + 3H φ' + a² dV/dφ = source_terms

// Verify signs and factors of a and H
// Check that dV/dφ has correct unit conversion
// Verify damping term coefficient (should be 3H, not 2H)
```

### CDM Coupling

```c
// Should only affect ρ_cdm_effective, not the Ridder evolution itself
// Gaussian in log(1+z):
double coupling = 1.0 + beta * exp(-0.5 * pow((log(1+z) - log(1+zc))/sigma_z, 2));
rho_cdm_eff = rho_cdm_base * coupling;

// Verify this doesn't feed back into φ' equation
```

---

## 5. Requested File Contents

I can provide the full contents of:
- background.h (struct definitions)
- input.c (Ridder parameter parsing section)  
- background.c (Ridder evolution and unit conversion)
- perturbations.c (Ridder perturbation setup)
- All three Python analysis scripts

Which would you like to see first?

---

## 6. Immediate Action Items

1. ✅ **Created validation framework** (`validate_ridder_potential.py`)

2. **Next: Implement C-level unit tests**
   - Create `test/test_ridder_derivatives.c`
   - Create `test/test_ridder_limits.c`
   - Add to Makefile test target

3. **Run regression tests**
   - ΛCDM recovery
   - Tail-only = Λ
   - Shelf-only = v2 EDE

4. **Cross-check units**
   - Compare to CLASS quintessence module
   - Verify eV^4 → Mpc^-2 conversions

5. **Document validation**
   - Create `VALIDATION_REPORT.md` with all test results
   - Include plots of w(z), H(z) comparisons

---

**Would you like me to:**
A. Provide full contents of background.h, input.c, background.c (Ridder sections)?
B. Implement the C-level unit tests first?
C. Fix and re-run the Python validation suite?
D. Create a detailed validation notebook with all checks?

