# Phase 2: Complete Implementation Roadmap

**Date:** November 20, 2025  
**Status:** Ready to Begin  
**Goal:** Move from Phase 1 proof-of-concept to Phase 2 (CLASS implementation + paper preparation)

---

## Overview

Phase 2 has three main buckets (as specified in the user's description):

1. **Lock the theory in "paper language"** ✅
2. **Specify and implement the numerics (CLASS/CAMB, MCMC)** 🔄
3. **Decide what figures and tables go in the paper** ✅

---

## Bucket 1: Lock Theory in Paper Language ✅

### Status: COMPLETE
- Full paper draft provided in user's description
- Theory is well-defined and consistent
- Action: Convert to clean LaTeX format

### Deliverables:
- [x] Paper structure defined
- [x] LaTeX document created (`paper/ridder_cosmology_paper.tex`)
- [x] All equations properly formatted
- [x] References section prepared (bib file needed)
- [x] Abstract finalized

---

## Bucket 2: Specify and Implement Numerics 🔄

### 2.1 CLASS Implementation

**Current Status:** Setup scripts ready, C code templates prepared

**Tasks:**
1. **Clone and compile CLASS**
   - [ ] Run `setup_class.py` to clone CLASS
   - [ ] Verify compilation succeeds
   - [ ] Create backup (`class_original`)

2. **Modify `include/background.h`**
   - [ ] Add Ridder field structure members
   - [ ] Add parameter fields (Lambda_EDE, f_axion, theta_i, beta_ridder)
   - [ ] Add index fields for background variables

3. **Modify `source/input.c`**
   - [ ] Add parameter parsing for Ridder field parameters
   - [ ] Add validation checks
   - [ ] Set default values

4. **Modify `source/background.c`**
   - [ ] Add `background_ridder_potential()` function
   - [ ] Add `background_ridder_initial_conditions()` function
   - [ ] Modify `background_derivs()` to include Klein-Gordon equation
   - [ ] Add dark matter coupling term
   - [ ] Implement switching surface logic
   - [ ] Add Ridder field to Friedmann equation

5. **Modify `source/perturbations.c`**
   - [ ] Add perturbed Klein-Gordon equation
   - [ ] Add coupling to metric perturbations
   - [ ] Modify dark matter perturbation equations
   - [ ] Handle gauge transformations

6. **Validation**
   - [ ] Test: ΛCDM baseline (Lambda_EDE=0, beta=0) reproduces exactly
   - [ ] Test: Sound horizon r_s ≈ 147 Mpc for baseline
   - [ ] Test: EDE mode shows r_s shift to ~142 Mpc
   - [ ] Test: No crashes at switching surface
   - [ ] Test: CMB power spectrum looks reasonable

**Timeline:** 2-3 weeks

### 2.2 MCMC Setup (Phase 3 Preview)

**Tools:**
- MontePython or Cobaya
- Planck 2018 data
- BAO data (BOSS, eBOSS, DESI)
- Pantheon+ SNe Ia

**Parameters to Fit:**
- Standard: `Omega_b h^2`, `Omega_c h^2`, `h`, `n_s`, `A_s`, `tau`
- Ridder: `Lambda_EDE`, `f_axion`, `theta_i`, `beta_ridder`

**Timeline:** 2-3 weeks after CLASS works

---

## Bucket 3: Figures and Tables Specification ✅

### Required Figures (from user's description)

#### Figure 1: Potential and Background Evolution
- **Purpose:** Visualize "one field, three phases"
- **Content:**
  - Plot V(φ) showing:
    - Inflationary plateau region
    - EDE bump near φ ~ f
    - Final minimum at φ₀
  - Overplot schematic trajectory φ(a) marking:
    - Inflation
    - Reheating
    - EDE epoch
    - Late-time settling
- **File:** `figures/fig1_potential_trajectory.pdf`

#### Figure 2: EDE Fraction vs Redshift
- **Purpose:** Show EDE contribution over time
- **Content:**
  - Plot f_EDE(z) = ρ_φ(z)/ρ_tot(z) for best-fit RC-X*
  - Compare to ΛCDM (zero line)
  - Show peak around z_c ~ 3000 at f_EDE ~ 0.07
- **File:** `figures/fig2_ede_fraction.pdf`

#### Figure 3: H₀ and CMB Compatibility
- **Purpose:** Main "anomaly-solving" claim
- **Content:**
  - Corner plot or 2D contours showing:
    - H₀ vs f_EDE
    - RC-X* vs ΛCDM posteriors
  - Show that with f_EDE ≈ 0.07, H₀ moves toward local values
- **File:** `figures/fig3_h0_contours.pdf`

#### Figure 4: Growth Factor or P(k,z) Kink
- **Purpose:** Show coupling signature
- **Content:**
  - Plot linear growth factor D(z) or matter power spectrum P(k,z) at a few redshifts
  - Show small, localized deviation from ΛCDM around redshift where φ leaves EDE shelf
  - Overlay forecast error bars for Euclid or LSST
- **File:** `figures/fig4_growth_kink.pdf`

#### Figure 5: n_s - r Plane
- **Purpose:** Inflation prediction
- **Content:**
  - Show n_s - r contours from Planck+BK
  - Mark RC-X* plateau prediction point (n_s ≈ 0.965, r ~ 4×10⁻³)
  - Show forecast contours for LiteBIRD or CMB-S4
- **File:** `figures/fig5_ns_r_plane.pdf`

#### Figure 6 (Optional): Stochastic GW from EDE Transition
- **Purpose:** LISA connection
- **Content:**
  - Plot predicted GW spectrum in LISA band
  - Show amplitude and peak frequency dependence on f_EDE
- **File:** `figures/fig6_gw_spectrum.pdf`

### Required Tables

#### Table 1: Parameter Summary
- Standard cosmological parameters
- Ridder field parameters
- Best-fit values and uncertainties

#### Table 2: Observables Comparison
- H₀, r_s, σ₈, n_s, r
- ΛCDM vs RC-X* predictions
- Current tensions

---

## Implementation Order

### Week 1-2: CLASS Background
1. Clone and compile CLASS
2. Modify `background.h` and `input.c`
3. Implement background evolution in `background.c`
4. Validate ΛCDM baseline

### Week 3: CLASS Perturbations
1. Modify `perturbations.c`
2. Test CMB power spectrum
3. Validate against known results

### Week 4: Paper Preparation
1. Convert paper draft to LaTeX
2. Create figure placeholders
3. Write figure generation scripts
4. Prepare tables

### Week 5-6: MCMC (Phase 3)
1. Set up MontePython/Cobaya
2. Run chains
3. Generate triangle plots
4. Analyze results

---

## Success Criteria

### Phase 2 Complete When:
- [ ] CLASS compiles and runs with Ridder field
- [ ] ΛCDM baseline reproduces exactly
- [ ] EDE mode shows expected r_s shift
- [ ] CMB power spectrum computed successfully
- [ ] Paper draft in LaTeX format
- [ ] Figure specifications complete
- [ ] All code documented

### Ready for Phase 3 When:
- [ ] CLASS fully validated
- [ ] Paper structure complete
- [ ] Figure generation scripts ready
- [ ] MCMC interface prepared

---

## Files Structure

```
phase2/
├── PHASE2_ROADMAP.md          # This file
├── paper/
│   ├── ridder_cosmology_paper.tex
│   ├── figures/
│   │   ├── fig1_potential_trajectory.pdf
│   │   ├── fig2_ede_fraction.pdf
│   │   ├── fig3_h0_contours.pdf
│   │   ├── fig4_growth_kink.pdf
│   │   ├── fig5_ns_r_plane.pdf
│   │   └── fig6_gw_spectrum.pdf
│   └── tables/
│       ├── table1_parameters.tex
│       └── table2_observables.tex
├── class/                      # CLASS repository (to be cloned)
├── scripts/
│   ├── generate_figures.py
│   └── run_validation.py
└── [existing setup files]
```

---

## Next Immediate Actions

1. **Create LaTeX paper** (`paper/ridder_cosmology_paper.tex`)
2. **Create figure specifications** (`paper/FIGURES_SPEC.md`)
3. **Set up CLASS** (run `setup_class.py`)
4. **Begin background.c modifications**

---

**Status:** Phase 2 roadmap complete. Ready to begin implementation.

