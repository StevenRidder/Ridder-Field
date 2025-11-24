# V2 to Unified Potential: Parameter Mapping

**Purpose:** Document how v2 "best CDM" benchmarks map into unified potential parameters  
**Goal:** Verify unified mode can reproduce v2 results before adding inflation

---

## V2 Best Configurations (Phase 2.5)

From CDM coupling optimization grid search:

### Safe Configuration
```
Lambda_EDE_ridder = 1.5 eV
theta_i_ridder = 1.0
n_ridder = 3
beta_ridder = 0.15
beta_z_c = 3000.0
beta_sigma_z = 0.5
```

**Results:**
- ΔH₀ = +3.14 km/s/Mpc (65% tension reduction)
- Max CMB Δ = 37.1%
- **Use for:** Safe MCMC starting point

### Hero Configuration
```
Lambda_EDE_ridder = 1.5 eV
theta_i_ridder = 1.0
n_ridder = 3
beta_ridder = 0.20
beta_z_c = 3000.0
beta_sigma_z = 0.5
```

**Results:**
- ΔH₀ = +3.49 km/s/Mpc (70% tension reduction)
- Max CMB Δ = 40.0%
- **Use for:** Maximum leverage MCMC target

---

## Unified Potential Structure

```
V(θ) = V_tail(θ) + V_shelf(θ) + V_plateau(θ)
```

### Tail (Late Dark Energy)
```c
V_tail = Lambda_tail^4 * [1 - cos(θ)]^n_tail
```

**Purpose:** Present-day dark energy (Ω_Λ ~ 0.7, w ~ -1)

### Shelf (Early Dark Energy)
```c
V_shelf = Lambda_EDE^4 * W(θ) * [1 - cos(θ)]^n_EDE

where W(θ) = tanh window centered on [theta_EDE_low, theta_EDE_high]
```

**Purpose:** Transient EDE bump at z~3000 ← **v2 benchmarks constrain this**

### Plateau (Inflation)
```c
V_plateau = Lambda_inf^4 * chi(θ) * F(θ)

where chi(θ) = window that turns on at large |θ|
```

**Purpose:** High-energy inflation epoch (to be explored later)

---

## Parameter Mapping: V2 → Unified

### Global Field Properties

| V2 Parameter | Unified Parameter | Value | Notes |
|--------------|-------------------|-------|-------|
| `f_axion_ridder` | `ridder_f` | 2.435e27 eV | M_Pl, same in both |
| N/A | `ridder_model_type` | `unified` | Switch to unified mode |

### Tail Parameters (Late DE)

| V2 Behavior | Unified Parameter | Value | Notes |
|-------------|-------------------|-------|-------|
| Implicit tail | `ridder_use_tail` | yes | Always on |
| (not explicit) | `ridder_Lambda_tail_eV` | 2.3e-3 | meV scale for Ω_Λ |
| `n_ridder = 3` | `ridder_n_tail` | 3.0 | Same power |

### Shelf Parameters (EDE) ← **KEY MAPPING**

| V2 Parameter | Unified Parameter | Value | Explanation |
|--------------|-------------------|-------|-------------|
| N/A | `ridder_use_shelf` | yes | EDE active |
| `Lambda_EDE_ridder` | `ridder_Lambda_EDE_eV` | 1.5 | **Direct 1:1 mapping** |
| `n_ridder` | `ridder_n_EDE` | 3.0 | **Direct 1:1 mapping** |
| `theta_i_ridder` | (sets field IC) | 1.0 | Field starts here |
| (implicit) | `ridder_theta_EDE_low` | 0.5 | **Window lower edge** |
| (implicit) | `ridder_theta_EDE_high` | 2.0 | **Window upper edge** |
| (implicit) | `ridder_sigma_theta_EDE` | 0.2 | **Window smoothing** |

**Rationale for window parameters:**
- V2 field rolls from θ_i ~ 1.0 toward θ ~ 0
- EDE active while θ ∈ [0.5, 2.0] (field crossing this range)
- Smooth tanh edges with width 0.2 (gentle turn-on/off)

### CDM Coupling Parameters

| V2 Parameter | Unified Parameter | Safe Value | Hero Value | Notes |
|--------------|-------------------|------------|------------|-------|
| `beta_ridder` | `beta_ridder` | 0.15 | 0.20 | **Same parameter** |
| `beta_z_c` | `beta_z_c` | 3000.0 | 3000.0 | **Same parameter** |
| `beta_sigma_z` | `beta_sigma_z` | 0.5 | 0.5 | **Same parameter** |

**Key insight:** CDM coupling is ORTHOGONAL to potential choice. Same functional form, same parameters.

### Plateau Parameters (Inflation) - NOT USED YET

| Parameter | Default | Status |
|-----------|---------|--------|
| `ridder_use_plateau` | no | OFF for EDE runs |
| `ridder_Lambda_inf_eV` | 1.0e-3 | Will tune later |
| `ridder_theta0_inf` | 5.0 | Will tune later |
| `ridder_theta_inf_on` | 8.0 | Will tune later |
| `ridder_sigma_inf` | 1.0 | Will tune later |
| `ridder_n_inf` | 1.0 | Will tune later |

---

## Expected Results: Unified vs V2

### Safe Configuration (β=0.15)

**V2 Results:**
- ΔH₀ = +3.14 km/s/Mpc
- z_peak ≈ 3000
- f_peak ≈ 13-15%
- Max CMB Δ = 37.1%
- RMS CMB Δ = 18.2%

**Unified SHOULD match within ~1-2%:**
- Unified shelf with window [0.5, 2.0] should activate at same epoch
- Same Lambda, same n, same CDM coupling → same physics
- Small differences possible due to window shape vs v2 rolloff

### Hero Configuration (β=0.20)

**V2 Results:**
- ΔH₀ = +3.49 km/s/Mpc
- z_peak ≈ 3000
- f_peak ≈ 13-15%
- Max CMB Δ = 40.0%
- RMS CMB Δ = 21.1%

**Unified SHOULD match within ~1-2%:**
- Same mapping logic as safe config
- Higher beta → stronger H₀ shift, maintained

---

## Verification Tests

### Test 1: Tail-Only (Sanity Check)
**Config:** `ridder_use_tail=yes`, `ridder_use_shelf=no`, `beta_ridder=0.0`

**Expected:**
- Ω_Λ ≈ 0.7
- w₀ ≈ -1.0
- No EDE bump
- H₀ = 67.36 (input value, no shift)

### Test 2: Shelf + CDM (Safe) - **KEY TEST**
**Config:** `unified_cdm_safe.ini`

**Expected:**
- ΔH₀ ≈ +3.14 km/s/Mpc (match v2 safe)
- Max CMB Δ ≈ 37% (match v2)
- z_peak ≈ 3000
- f_peak ≈ 13-15%

**Success criteria:** Match v2 within 5%

### Test 3: Shelf + CDM (Hero) - **KEY TEST**
**Config:** `unified_cdm_hero.ini`

**Expected:**
- ΔH₀ ≈ +3.49 km/s/Mpc (match v2 hero)
- Max CMB Δ ≈ 40% (match v2)
- z_peak ≈ 3000
- f_peak ≈ 13-15%

**Success criteria:** Match v2 within 5%

---

## INI Files Created

- `unified_cdm_safe.ini` - Safe config (β=0.15)
- `unified_cdm_hero.ini` - Hero config (β=0.20)
- Both map v2 benchmarks to unified parameters

---

## Implementation Notes

### What Changes in Code

**Defaults in input.c:**
```c
/* Safe default: unified with hero CDM */
pba->ridder_unified.Lambda_EDE = 1.5;
pba->ridder_unified.n_EDE = 3.0;
pba->ridder_unified.theta_EDE_low = 0.5;
pba->ridder_unified.theta_EDE_high = 2.0;
pba->ridder_unified.sigma_theta_EDE = 0.2;

/* CDM coupling defaults */
if (pba->ridder_unified.model_type == ridder_model_unified) {
    pba->beta_ridder = 0.20;  // Hero default
    pba->beta_z_c = 3000.0;
    pba->beta_sigma_z = 0.5;
}
```

**User can override:**
- Set `beta_ridder = 0.15` for safe config
- Adjust shelf window if needed
- All v2 knobs still accessible

### What Stays the Same

- CDM coupling functional form (unchanged)
- Background integration (same equations)
- Perturbation treatment (same method)
- All analysis scripts (same inputs/outputs)

---

## Success Criteria

**Unified mode is validated when:**

✅ Tail-only matches late-DE expectations (Ω_Λ ~ 0.7)  
✅ Safe config matches v2 safe within 5% (all observables)  
✅ Hero config matches v2 hero within 5% (all observables)  
✅ Simple_ede mode still works (v2 unchanged)

**Then we're ready for:**
- Inflation parameter exploration (turn on plateau)
- Full unified MCMC (all three regimes)
- "One field from inflation to heat death" narrative

---

## Quick Reference: File Locations

**INI configs:**
- `unified_cdm_safe.ini` - Conservative benchmark
- `unified_cdm_hero.ini` - Maximum leverage

**Code files:**
- `phase2/class/include/background.h` - Structs and enums
- `phase2/class/source/ridder_unified_potential.c` - Physics
- `phase2/class/source/input.c` - Parameter reading (TODO: add defaults)
- `phase2/class/source/background.c` - Integration hook (TODO: add branch)

**Test script:**
- `test_unified_vs_v2.py` - Automated verification

---

**STATUS:** Mapping complete, configs created, awaiting code integration (Steps 2 & 4)

