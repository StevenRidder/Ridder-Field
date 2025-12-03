# Phase 2 Implementation Status

**Date:** December 2024  
**Status:** Background Evolution Complete, Ready for Perturbations

---

## ✅ Completed: Background Evolution

### 1. **Header File (`include/background.h`)**
- ✅ Added Ridder field parameters:
  - `Lambda_EDE_ridder`: EDE energy scale [eV]
  - `f_axion_ridder`: Decay constant [eV]
  - `theta_i_ridder`: Initial misalignment angle [radians]
  - `beta_ridder`: DM coupling strength (dimensionless)
  - `n_ridder`: Potential power (typically 3)
- ✅ Added state variable indices:
  - `index_bg_phi_ridder`, `index_bg_phi_prime_ridder`
  - `index_bg_rho_ridder`, `index_bg_p_ridder`
  - `index_bi_phi_ridder`, `index_bi_phi_prime_ridder`
- ✅ Added switching surface flags:
  - `ridder_fluid_mode`: TRUE when in fluid approximation
  - `z_osc_ridder`: Redshift where oscillations begin
  - `w_eff_ridder`: Effective equation of state after switching
- ✅ Added function declarations: `V_ridder()`, `dV_ridder()`, `ddV_ridder()`

### 2. **Input Parameters (`source/input.c`)**
- ✅ Added parameter reading for all Ridder field parameters
- ✅ Added validation: `Lambda_EDE_ridder >= 0`, `f_axion_ridder >= 0`
- ✅ Automatic `has_ridder` flag setting

### 3. **Potential Functions (`source/background.c`)**
- ✅ `V_ridder()`: Implements `Λ^4 * [1 - cos(φ/f)]^n`
- ✅ `dV_ridder()`: First derivative (for Klein-Gordon equation)
- ✅ `ddV_ridder()`: Second derivative (for effective mass calculation)

### 4. **Background Evolution (`source/background.c`)**
- ✅ Energy density and pressure computation in `background_functions()`
- ✅ Klein-Gordon evolution in `background_derivs()`:
  - Standard evolution: `dφ/dlna = φ'/(aH)`
  - With coupling: `dφ'/dlna = -2φ' - (a/H)dV - (a/H)*β*ρ_DM/M_Pl`
- ✅ Initial conditions: Field starts Hubble-frozen with displacement `θ_i`
- ✅ Switching surface logic:
  - Detects when `3H < m_eff` (rapid oscillations)
  - Switches to fluid approximation with `w_eff = 0` (matter-like)
  - Freezes field evolution after switching

### 5. **Testing**
- ✅ Created test files: `test_ridder_lcdm.ini` and `test_ridder_ede.ini`
- ✅ Verified compilation: CLASS builds successfully
- ✅ Verified basic execution: Both test cases run without errors

---

## 🔄 In Progress / Known Issues

### 1. **Unit Conversions**
- ⚠️ **Status**: Partially implemented, needs verification
- **Issue**: CLASS uses Mpc units internally, but Ridder field parameters are in eV
- **Current**: Approximate conversions implemented, but may need refinement
- **Action**: Test against Phase 1 Python results to verify unit consistency

### 2. **CDM Coupling**
- ⚠️ **Status**: Field evolution affected, but CDM density not modified
- **Issue**: CDM density is computed from `Omega0_cdm`, not integrated
- **Current**: Coupling term affects Ridder field evolution only
- **Action**: Make `rho_cdm` an integration variable when `beta != 0` (similar to `dcdm`)

### 3. **Fluid Mode Energy Density Evolution**
- ⚠️ **Status**: Field frozen, but energy density evolution needs refinement
- **Issue**: After switching to fluid mode, `rho_ridder` should evolve as `a^{-3(1+w_eff)}`
- **Current**: Energy density computed from frozen field values
- **Action**: Make `rho_ridder` an integration variable when `ridder_fluid_mode == TRUE`

---

## 📋 Next Steps: Perturbation Equations

### 1. **Modify `source/perturbations.c`**
- [ ] Add Ridder field perturbation variables:
  - `delta_phi_ridder`: Field perturbation
  - `delta_phi_prime_ridder`: Field velocity perturbation
  - `delta_rho_ridder`: Energy density perturbation
  - `delta_p_ridder`: Pressure perturbation
- [ ] Implement perturbation evolution equations:
  - Klein-Gordon perturbation equation
  - Energy-momentum conservation for Ridder field
  - Coupling to DM perturbations
- [ ] Add to metric perturbation sources

### 2. **CMB Power Spectrum**
- [ ] Verify CMB temperature and polarization spectra
- [ ] Compare with ΛCDM baseline
- [ ] Check for numerical stability

### 3. **Matter Power Spectrum**
- [ ] Verify `P(k,z)` calculation
- [ ] Check growth factor evolution
- [ ] Validate against Phase 1 results

### 4. **Validation**
- [ ] Compare `H(z)` with Phase 1 Python results
- [ ] Verify sound horizon `r_s` reduction (EDE effect)
- [ ] Check `S_8` evolution (DM coupling effect)

---

## 📝 Test Files

### `test_ridder_lcdm.ini`
- **Purpose**: Verify ΛCDM baseline (Lambda_EDE = 0)
- **Expected**: Should reproduce standard CLASS results
- **Status**: ✅ Runs successfully

### `test_ridder_ede.ini`
- **Purpose**: Test EDE mode (Lambda_EDE > 0)
- **Expected**: Should show EDE effects (reduced `r_s`, modified `H(z)`)
- **Status**: ✅ Runs successfully

---

## 🔧 Compilation

```bash
cd phase2/class
make clean
make
```

**Status**: ✅ Compiles successfully

---

## 📚 References

- Theory definition: `docs/RIDDER_THEORY_LAGRANGIAN.md`
- Phase 2 roadmap: `phase2/PHASE2_ROADMAP.md`
- Figure specifications: `phase2/paper/FIGURES_SPEC.md`
- Paper draft: `phase2/paper/ridder_cosmology_paper.tex`

---

## 🎯 Phase 2 Goals

1. ✅ **Lock theory in paper language** - COMPLETE
2. ✅ **Specify and implement numerics (background)** - COMPLETE
3. ⏳ **Specify and implement numerics (perturbations)** - IN PROGRESS
4. ✅ **Decide figures and tables** - COMPLETE
5. ⏳ **Generate figures and tables** - PENDING (requires perturbations)

---

**Next Milestone**: Implement perturbation equations in `perturbations.c`

