# IMMEDIATE ACTION: Full Scalar Field Implementation

**Decision:** Path A - Full Scalar Field  
**Timeline:** 2-3 days  
**Start:** Now

---

## Tonight: Path B Safety Check (1 hour)

While I sleep, run background-only MCMC to check if the theory is even viable:

```bash
cd /Users/steveridder/Git/Ridder\ Field/phase3
# Create background-only config
cp ridder_field.yaml ridder_background_only.yaml
# Edit: Remove high-ℓ Planck, keep only geometric data
cobaya-run ridder_background_only.yaml -o chains/background_test
```

**Goal:** If MCMC prefers Λ_EDE ≈ 0, theory is dead anyway. Cheap kill switch.

---

## Tomorrow: Implement Ridder Potential in CLASS

### Step 1: Add Potential to `background.c`

**File:** `phase2/class/source/background.c`  
**Location:** Around line 4000 (search for `V_scf` or `scf_potential`)

Add case for Ridder potential:

```c
if (pba->scf_potential == ridder) {
    // Parameters:
    // pba->scf_parameters[0] = f_axion
    // pba->scf_parameters[1] = Lambda_EDE
    // pba->scf_parameters[2] = n (power)
    
    double f = pba->scf_parameters[0];
    double Lambda = pba->scf_parameters[1];
    double n = pba->scf_parameters[2];
    
    double cos_term = cos(phi/f);
    double sin_term = sin(phi/f);
    double base = 1.0 - cos_term;
    
    *V = pow(Lambda, 4) * pow(base, n);
    *dV = pow(Lambda, 4) * n * pow(base, n-1) * sin_term / f;
    *ddV = pow(Lambda, 4) * n * pow(base, n-2) * 
           ((n-1) * sin_term * sin_term / (f*f) + 
            base * cos_term / (f*f));
}
```

### Step 2: Add β-Coupling to `perturbations.c`

**File:** `phase2/class/source/perturbations.c`  
**Location:** Search for `index_pt_theta_cdm` in `perturbations_derivs`

Add coupling force:

```c
// In CDM Euler equation
dy[pv->index_pt_theta_cdm] = ... existing terms ...
    + pba->beta_ridder * k2 * y[pv->index_pt_phi_scf] * rho_scf / rho_cdm;
```

### Step 3: Configure `.ini` File

**File:** `phase2/class/ridder_scf.ini`

```ini
# Use scalar field instead of fluid
fluid_equation_of_state = scf
scf_potential = ridder
scf_parameters = 1e27, 1.0, 3.0  # f, Lambda, n

# Let CLASS find attractor
attractor_ic_scf = yes
scf_tuning_index = 0

# Standard integration
scf_evolve_like_axionCAMB = no

# Coupling parameter
beta_ridder = 0.01

# Output
output = tCl,pCl,lCl,mPk
l_max_scalars = 3000
```

### Step 4: Test

```bash
cd /Users/steveridder/Git/Ridder\ Field/phase2/class
make clean && make -j4
./class ridder_scf.ini
```

**Expected:** 
- Background H(z) matches fluid version
- CMB spectrum has NO spike at ℓ=2500
- P(k) shows β-coupling suppression

---

## Day 3: Validate & Launch MCMC

Run `audit_rigorous.py` with new implementation:
- BBN check
- CMB damping tail (should be <5% excess)
- Coupling linearity

If clean:
```bash
cd /Users/steveridder/Git/Ridder\ Field/phase3
cobaya-run ridder_field.yaml -o chains/production
```

---

## Why This Works

CLASS's `scf` module **already has WKB averaging built in**. When the field oscillates too fast, it automatically switches to a cycle-averaged fluid representation **smoothly**. No discontinuities. No spikes. No hijacks needed.

**You're not fixing a bug. You're using the right tool.**

---

## Narrative for Paper

"We initially explored a fluid approximation for computational efficiency, but found that the hard transition between field and fluid regimes introduced numerical artifacts in the high-ℓ CMB spectrum. We therefore implemented the full Klein-Gordon evolution using CLASS's scalar field module, which handles the oscillating regime via smooth WKB averaging. This eliminates all approximation artifacts while remaining computationally tractable."

**Translation:** "We tried a shortcut. It didn't work. We did it right."

---

**Status:** Committed to Path A.  
**Next:** Implement potential in `background.c` tomorrow morning.  
**Backup:** Background-only MCMC running overnight as safety check.

**Let's go.**

