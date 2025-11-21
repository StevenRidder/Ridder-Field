# FINAL RESTORATION REPORT: What We're Missing

**Date:** November 21, 2025  
**Status:** ⚠️ **INCOMPLETE - Missing Critical Implementation**

---

## Executive Summary

After extensive analysis of the old thread data and documentation, I have identified **what was actually implemented** vs what I restored. The current implementation is **fundamentally incomplete**.

### What I Did (WRONG Approach)
- Modified `V_scf()`, `dV_scf()`, `ddV_scf()` to check `has_ridder` flag
- Set initial conditions based on `has_ridder`
- Used generic scf infrastructure

### What Was ACTUALLY Done (CORRECT Approach)
- **Added `scf_pot_ridder` as a NEW potential type enum**
- **Registered it in `background_potential()` switch statement**
- **Used CLASS's built-in tuning mechanism** (`scf_tuning_index = 1`)
- **Let CLASS compute initial conditions** (`attractor_ic_scf = yes`)
- **Added coupling terms to `perturbations.c`**

---

## The Missing Implementation

### 1. File: `include/background.h`

**MISSING:** Ridder potential enum registration

```c
enum scf_potential {
    scf_pot_alp,
    scf_pot_pol_free,
    scf_pot_exp_free,
    scf_pot_ridder,        // <--- THIS IS MISSING!
    scf_pot_double_alp
};
```

### 2. File: `source/input.c`

**MISSING:** Potential name parser

```c
// In the scf_potential reading block
if (strstr(string2,"ridder") != NULL) {
    pba->scf_potential = scf_pot_ridder;
}
```

### 3. File: `source/background.c`

**MISSING:** Proper potential registration in `background_potential()` function

The correct implementation should be in a **switch statement**, not in the individual V_scf/dV_scf functions!

```c
// In background_potential() function
case scf_pot_ridder:
    {
        // Get parameters
        double f = pba->scf_parameters[0];      // Decay constant (Planck units)
        double Lambda = pba->scf_parameters[1]; // Energy scale (Planck units)
        double n = pba->scf_parameters[2];      // Power law index
        
        // Compute potential: V = Λ^4 * [1 - cos(φ/f)]^n
        double arg = phi / f;
        double cos_a = cos(arg);
        double sin_a = sin(arg);
        double one_m_cos = 1.0 - cos_a;
        if (one_m_cos < 1.e-16) one_m_cos = 1.e-16;
        
        double V0 = pow(Lambda, 4);
        
        *V = V0 * pow(one_m_cos, n);
        *dV = (V0 * n / f) * pow(one_m_cos, n-1.0) * sin_a;
        
        // d²V/dφ²
        double t1 = pow(one_m_cos, n-1.0) * cos_a;
        double t2 = (n-1.0) * pow(one_m_cos, n-2.0) * sin_a * sin_a;
        *ddV = (V0 * n / (f*f)) * (t1 + t2);
    }
    break;
```

### 4. File: `source/perturbations.c`

**COMPLETELY MISSING:** The 3-term coupling implementation

```c
// In perturbations_derivs()

// 1. CDM Continuity (Energy Exchange)
if (pba->has_cdm == _TRUE_ && pba->has_scf == _TRUE_ && pba->beta_ridder != 0.) {
    dy[pv->index_pt_delta_cdm] += pba->beta_ridder * phi_prime_bg * y[pv->index_pt_phi_scf];
}

// 2. CDM Euler (Momentum Drag)
if (pba->has_cdm == _TRUE_ && pba->has_scf == _TRUE_ && pba->beta_ridder != 0.) {
    dy[pv->index_pt_theta_cdm] += pba->beta_ridder * k2 * y[pv->index_pt_phi_scf];
}

// 3. Scalar Field KG (Backreaction)
if (pba->has_scf == _TRUE_ && pba->has_cdm == _TRUE_ && pba->beta_ridder != 0.) {
    double rho_cdm = ppw->pvecback[pba->index_bg_rho_cdm];
    dy[pv->index_pt_phi_prime_scf] -= pba->beta_ridder * a2 * rho_cdm * y[pv->index_pt_delta_cdm];
}
```

---

## The Correct .ini File Configuration

Based on the old thread, the working configuration was:

```ini
# Standard cosmology
h = 0.72
omega_b = 0.02237
omega_cdm = 0.120
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.054

# Scalar field activation
use_scf = yes
scf_potential = ridder

# Parameters: [f, Lambda, n]
# f = 0.4 (in Planck units, corresponds to ~1e27 eV)
# Lambda = 1.0e-9 (CLASS will tune this)
# n = 3.0 (potential power)
scf_parameters = 0.4, 1.0e-9, 3.0

# Tuning mode
scf_tuning_index = 1        # Tune Lambda (index 1)
Omega_scf = 0.10            # Target 10% EDE
attractor_ic_scf = yes      # Let CLASS compute ICs

# Initial conditions (CLASS computes these with attractor)
scf_phi_ini = 0.8           # theta_i * f = 2.0 * 0.4
scf_phi_prime_ini = 0.0

# Coupling
beta_ridder = 0.01

# Output
output = tCl, mPk
l_max_scalars = 3000
```

---

## Why My Implementation Failed

### Problem 1: Wrong Architecture
I modified the **output** functions (`V_scf`, `dV_scf`, `ddV_scf`) instead of the **input** function (`background_potential`).

CLASS's architecture:
- `background_potential()` is called ONCE to set up the potential
- `V_scf()`, `dV_scf()`, `ddV_scf()` are **helper functions** that get called by the generic potential

### Problem 2: Wrong Units
I was setting φ_i = f * θ_i = 1e27 * 2.1 in eV, but CLASS expects **Planck units** where M_Pl = 1.

Correct conversion:
- f_physical = 1e27 eV
- M_Pl = 2.435e27 eV  
- f_Planck = f_physical / M_Pl = 1e27 / 2.435e27 ≈ 0.4

### Problem 3: Wrong Initialization
I was trying to manually set initial conditions, but the working implementation used **`attractor_ic_scf = yes`** to let CLASS compute them automatically based on the potential shape.

### Problem 4: Missing Perturbations
The coupling to CDM (which gives the S₈ suppression) was **completely missing** from my implementation.

---

## The "Safe Mode" Discovery

From the old thread, they discovered a **"Redline"** at θ_i ≈ 2.3:

| θ_i | Status | CMB Excess | H₀ |
|-----|--------|------------|-----|
| 2.0 | ✅ Safe | ~10% | ~70.5 km/s/Mpc |
| 2.1 | ✅ Safe | ~12% | ~71.0 km/s/Mpc |
| 2.2 | ⚠️ Yellow | ~15% | ~71.5 km/s/Mpc |
| 2.3 | 🔴 Redline | ~18% | ~72.0 km/s/Mpc |
| 2.4+ | ❌ Explosion | >100% | N/A |

**Physical Interpretation:** Above θ_i = 2.3, the field oscillations resonate with the acoustic oscillations of the photon-baryon plasma, creating a "CMB catastrophe."

---

## Expected Results (from SMOKE_TEST_RESULTS.md)

With correct implementation at θ_i = 2.1, β = 0.01:

- **Sound Horizon:** r_s = 139.06 Mpc (±0.3)
- **f_EDE Peak:** 0.1546 (15.46%) at z ≈ 6697
- **H₀:** ~71.0 km/s/Mpc (inferred from r_s)
- **CMB Excess:** ~12% at ℓ = 2000-3000
- **S₈ Suppression:** ~15% at k = 0.1 h/Mpc

---

## What Needs to Be Done

### Immediate Actions:

1. **Add `scf_pot_ridder` enum** to `background.h`
2. **Add potential parser** to `input.c`
3. **Implement `case scf_pot_ridder:`** in `background_potential()` in `background.c`
4. **Remove my hacks** from `V_scf()`, `dV_scf()`, `ddV_scf()`
5. **Add 3-term coupling** to `perturbations.c`
6. **Update .ini file** to use `scf_potential = ridder`

### Testing Protocol:

1. Run with θ_i = 2.0, β = 0.0 (baseline)
2. Check r_s ≈ 139-140 Mpc
3. Check f_EDE ≈ 0.10-0.15
4. Run with θ_i = 2.1, β = 0.01 (full model)
5. Check S₈ suppression in P(k)

---

## The Mathematical Framework

### Potential (Correct Formula)
$$V(\phi) = \Lambda^4 \left[1 - \cos\left(\frac{\phi}{f}\right)\right]^n$$

where:
- φ is in Planck units (M_Pl = 1)
- f ≈ 0.4 (Planck units) ≈ 1e27 eV (physical)
- Λ ≈ 1e-9 (Planck units, tuned by CLASS)
- n = 3 (potential shape)

### Initial Conditions
$$\phi_i = f \cdot \theta_i$$
$$\phi'_i = 0$$

For θ_i = 2.1, f = 0.4:
$$\phi_i = 0.4 \times 2.1 = 0.84 \text{ (Planck units)}$$

### Coupling Terms
**CDM Continuity:**
$$\dot{\delta}_c = -\theta_c - \frac{1}{2}\dot{h} + \beta \dot{\phi} \delta\phi$$

**CDM Euler:**
$$\dot{\theta}_c = -H\theta_c + k^2\psi + \beta k^2 \delta\phi$$

**Scalar KG:**
$$\ddot{\delta\phi} + 2H\dot{\delta\phi} + (k^2 + a^2 V'')\\delta\phi = -\dot{\phi}\dot{h} - \beta a^2 \rho_c \delta_c$$

---

## Conclusion

**Current Status:** The implementation is **architecturally wrong**. I was modifying the wrong functions and using the wrong approach.

**What's Needed:** A complete rewrite following the CLASS native architecture:
1. Register new potential type
2. Implement in `background_potential()` switch
3. Add perturbation coupling
4. Use CLASS's built-in tuning

**Estimated Time:** 2-3 hours to implement correctly

**Expected Outcome:** With correct implementation, should match documented results:
- r_s = 139.06 Mpc
- f_EDE = 15.46%
- H₀ = 71.0 km/s/Mpc
- S₈ suppression = 15%

---

## Recommendation

**DO NOT proceed with MCMC** until the implementation is corrected. The current code is running but producing wrong physics.

**Next Step:** Implement the proper `scf_pot_ridder` architecture as described above, following the exact pattern used by `scf_pot_alp` and other existing potentials in CLASS.

