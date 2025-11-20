# Phase 2: CLASS Implementation Guide

**Goal:** Modify the Cosmic Linear Anisotropy Solving System (CLASS) to include the Ridder field.

## Prerequisites

✅ Phase 1.5 complete:
- Sound horizon r_s calculation validated (≈147 Mpc for ΛCDM baseline)
- Switching surface z_osc defined
- Units standardized to Mpc

## Step-by-Step Implementation

### 1. Clone CLASS Repository

```bash
cd "/Users/steveridder/Git/Ridder Field/phase2"
git clone https://github.com/lesgourg/class_public.git class
cd class
```

### 2. Understand CLASS Architecture

CLASS is organized into modules:
- **`source/input.c`**: Reads parameter files (`.ini` files)
- **`source/background.c`**: Solves background evolution (H(z), ρ_i(z))
- **`source/thermodynamics.c`**: Recombination, visibility function
- **`source/perturbations.c`**: Linear perturbations (δ_i, Θ_l, Φ, Ψ)
- **`source/primordial.c`**: Initial power spectrum
- **`source/spectra.c`**: CMB and matter power spectra

**We will modify:** `input.c`, `background.c`, and `perturbations.c`.

---

## 3. Modification Plan

### A. `source/input.c` - Add Ridder Field Parameters

**Purpose:** Teach CLASS to read our new parameters from `.ini` files.

**Parameters to add:**
```c
// Ridder field parameters
pba->Omega_ridder = 0.0;        // Initial fraction (will be computed)
pba->Lambda_EDE = 0.0;          // EDE energy scale [eV]
pba->f_axion = 1e16;            // Decay constant [eV]
pba->theta_i = 2.5;             // Initial misalignment angle
pba->beta_ridder = 0.0;         // DM coupling strength
pba->n_ridder = 3;              // Potential power (usually 3)
```

**Action:**
1. Locate the section where `Omega_Lambda`, `Omega_cdm`, etc. are read
2. Add similar parsing logic for `Omega_ridder`, `Lambda_EDE`, etc.
3. Add validation (e.g., `Lambda_EDE >= 0`, `f_axion > 0`)

---

### B. `source/background.c` - Implement Ridder Field Evolution

**Purpose:** Add the Ridder field to the background ODE system.

#### B.1: Define the Potential

In `background.c`, add a function to compute the Ridder potential:

```c
/**
 * Ridder field potential V(phi) and its derivatives
 */
int background_ridder_potential(
    struct background *pba,
    double phi,
    double *V,
    double *V_prime,
    double *V_second
) {
    double Lambda = pba->Lambda_EDE;
    double f = pba->f_axion;
    double n = pba->n_ridder;
    
    if (Lambda == 0.0) {
        *V = 0.0;
        *V_prime = 0.0;
        *V_second = 0.0;
        return _SUCCESS_;
    }
    
    double phi_over_f = phi / f;
    double cos_term = cos(phi_over_f);
    double sin_term = sin(phi_over_f);
    double base = 1.0 - cos_term;
    
    double Lambda4 = pow(Lambda, 4.0);
    
    // V = Lambda^4 * (1 - cos(phi/f))^n
    *V = Lambda4 * pow(base, n);
    
    // V' = Lambda^4 * n * (1-cos(phi/f))^(n-1) * sin(phi/f) / f
    *V_prime = Lambda4 * n * pow(base, n-1) * sin_term / f;
    
    // V'' = Lambda^4 * n * [(n-1)*(1-cos)^(n-2)*sin^2/f^2 + (1-cos)^(n-1)*cos/f^2]
    *V_second = Lambda4 * n / (f*f) * (
        (n-1) * pow(base, n-2) * sin_term * sin_term +
        pow(base, n-1) * cos_term
    );
    
    return _SUCCESS_;
}
```

#### B.2: Add Field Variables to ODE System

CLASS tracks variables in an array `pvecback`. Add:
- `pba->index_bg_phi` = φ
- `pba->index_bg_phi_prime` = φ' = dφ/dτ (conformal time derivative)
- `pba->index_bg_rho_ridder` = ρ_φ

#### B.3: Modify Background Evolution

In `background_derivs()`, add the Klein-Gordon equation:

```c
// Ridder field equation
// d^2 phi / d tau^2 + 2 a H d phi / d tau + a^2 dV/dphi + beta * rho_DM / M_Pl = 0

double phi = pvecback[pba->index_bg_phi];
double phi_prime = pvecback[pba->index_bg_phi_prime];

double V, V_prime, V_second;
background_ridder_potential(pba, phi, &V, &V_prime, &V_second);

double a = pvecback[pba->index_bg_a];
double H = pvecback[pba->index_bg_H];
double rho_cdm = pvecback[pba->index_bg_rho_cdm];

// phi'' = -2 a H phi' - a^2 V' - beta * rho_DM * a^2 / M_Pl
pvecback_derivs[pba->index_bg_phi] = phi_prime;
pvecback_derivs[pba->index_bg_phi_prime] = 
    -2.0 * a * H * phi_prime 
    - a*a * V_prime 
    - pba->beta_ridder * rho_cdm * a*a / M_Pl;
```

#### B.4: Add Coupling to Dark Matter

Modify the CDM continuity equation:

```c
// Standard: d rho_cdm / d tau = -3 a H rho_cdm
// With coupling: d rho_cdm / d tau = -3 a H rho_cdm + beta * phi_prime / M_Pl * rho_cdm

pvecback_derivs[pba->index_bg_rho_cdm] = 
    -3.0 * a * H * rho_cdm 
    + pba->beta_ridder * phi_prime / M_Pl * rho_cdm;
```

#### B.5: Include in Friedmann Equation

Add ρ_φ to total energy density:

```c
// rho_phi = (1/2) * phi_prime^2 / a^2 + V(phi)
double rho_ridder = 0.5 * phi_prime * phi_prime / (a*a) + V;
pvecback[pba->index_bg_rho_ridder] = rho_ridder;

// Add to rho_total
rho_tot += rho_ridder;
```

#### B.6: Switching Logic (Critical!)

**This is where the Nobel Path happens.**

When the field begins oscillating (`3H < m_eff`), stop integrating Klein-Gordon and switch to fluid approximation:

```c
// Check if oscillations have started
double m_eff_squared = V_second;
if (m_eff_squared > 0) {
    double m_eff = sqrt(m_eff_squared);
    if (3.0 * H < m_eff) {
        // Switch to fluid approximation
        pba->ridder_fluid_mode = _TRUE_;
        // Compute w_eff from potential shape
        double w_eff = 0.0;  // For cosine potential, averages to ~0
        // From now on: rho_ridder scales as a^{-3(1+w_eff)}
    }
}
```

---

### C. `source/perturbations.c` - Add Perturbed Klein-Gordon Equation

**Purpose:** Include the scalar field in CMB and matter power spectrum calculations.

Add perturbed field equations:
```c
// δφ'' + 2 a H δφ' + (k^2 + a^2 V'') δφ = source terms from metric perturbations
```

This is the most technically demanding part and requires careful gauge choice (synchronous or Newtonian).

---

## 4. Compilation and Testing

### Compile CLASS
```bash
cd class
make clean
make
```

### Test with ΛCDM
Create a test `.ini` file with Ridder field disabled:
```ini
# test_lambda_cdm.ini
Lambda_EDE = 0.0
beta_ridder = 0.0
```

Run:
```bash
./class test_lambda_cdm.ini
```

Should produce identical results to standard ΛCDM.

### Test with EDE
```ini
# test_ede.ini
Lambda_EDE = 1e-2  # eV
f_axion = 1e16     # eV
theta_i = 2.5
beta_ridder = 0.0
```

Check that:
- `r_s` decreases (should go from ~147 Mpc to ~142 Mpc)
- CMB peaks shift
- Matter power spectrum changes

---

## 5. Validation Checklist

- [ ] ΛCDM baseline reproduced exactly
- [ ] Sound horizon r_s matches Python Phase 1.5 calculation
- [ ] Switching surface handled smoothly (no numerical crashes)
- [ ] CMB C_l spectrum looks reasonable (no wild oscillations)
- [ ] Matter power spectrum P(k) shows expected suppression

---

## 6. Next: Phase 3 (MCMC)

Once CLASS runs successfully, interface it with **MontePython** or **Cobaya** to fit:
- Planck 2018 CMB data
- BAO measurements (BOSS, eBOSS)
- Pantheon+ SNe Ia

**Victory condition:** Triangle plot showing H_0 ≈ 73 km/s/Mpc with good χ².

---

## Resources

- **CLASS Documentation:** [class-code.net](https://github.com/lesgourg/class_public)
- **EDE Papers:**
  - Poulin et al. (2019): "Early Dark Energy can Resolve the Hubble Tension"
  - Smith et al. (2020): "Hints of Early Dark Energy in Planck Data"
- **Hu & Sugiyama (1996):** Sound horizon fitting formula
- **Riess et al. (2022):** SH0ES H_0 measurement

---

**Status:** Phase 2 setup complete. Ready to modify CLASS source code.

**Next action:** Edit `source/background.c` to add Ridder field potential and evolution equations.

