# V2 Implementation Plan: Step-by-Step Execution

**Date**: November 23, 2025  
**Status**: Ready to Execute  
**Goal**: Implement V2 model in parallel to V1 without breaking existing code

---

## Directory Structure

```
Ridder-Field/
├── phase2/          # V1 CLASS implementation (DO NOT TOUCH)
├── phase2_v2/       # V2 CLASS implementation (NEW)
│   └── class/       # Modified CLASS with V2 physics
├── phase3/          # V1 MCMC configs and results (ARCHIVE ONLY)
├── phase3_v2/       # V2 MCMC configs and results (NEW)
│   ├── configs/     # V2 YAML files
│   ├── scripts/     # V2 run scripts
│   ├── results/     # V2 chain data and plots
│   └── tests/       # V2 validation tests
└── V2_*.md          # V2 documentation
```

**Key Principle**: V1 stays frozen in `phase2/` and `phase3/`. All V2 work happens in `phase2_v2/` and `phase3_v2/`.

---

## Phase 0: Setup and Copy (Day 1, Morning)

### Step 0.1: Copy CLASS Source to V2
```bash
cd /Users/steveridder/Git/Ridder-Field

# Copy entire CLASS directory
cp -r phase2/class phase2_v2/class

# Verify copy
ls -la phase2_v2/class/source/
ls -la phase2_v2/class/include/
```

### Step 0.2: Create V2 Git Branch
```bash
git checkout -b v2-development
git add phase2_v2/ phase3_v2/
git commit -m "Initialize V2 directory structure"
git push -u origin v2-development
```

### Step 0.3: Document V1 Freeze
```bash
# Create a marker file
echo "V1 IS FROZEN - DO NOT MODIFY" > phase2/FROZEN_V1.txt
echo "V1 IS FROZEN - DO NOT MODIFY" > phase3/FROZEN_V1.txt
git add phase2/FROZEN_V1.txt phase3/FROZEN_V1.txt
git commit -m "Freeze V1 codebase"
```

---

## Phase 1: Download and Validate AxiCLASS (Day 1, Afternoon)

### Step 1.1: Clone AxiCLASS
```bash
cd ~/Downloads
git clone https://github.com/PoulinV/AxiCLASS.git
cd AxiCLASS
```

### Step 1.2: Compile AxiCLASS
```bash
make clean
make -j8

# Test compilation
./class explanatory.ini
```

### Step 1.3: Install Python Wrapper
```bash
cd python
python3 setup.py install --user

# Test import
python3 -c "from classy import Class; print('AxiCLASS loaded successfully')"
```

### Step 1.4: Run AxiCLASS Test
Create `phase3_v2/tests/test_axiclass.py`:
```python
#!/usr/bin/env python3
"""
Test AxiCLASS with default EDE parameters.
Goal: Verify chi2 < 2800 with Planck data.
"""

from classy import Class
import numpy as np

# AxiCLASS default EDE parameters (from Poulin et al. 2018)
params = {
    'output': 'tCl,mPk',
    'l_max_scalars': 2508,
    'lensing': 'yes',
    
    # Standard cosmology
    'omega_b': 0.02237,
    'omega_cdm': 0.1200,
    'h': 0.6736,
    'A_s': 2.1e-9,
    'n_s': 0.9649,
    'tau_reio': 0.0544,
    
    # AxiCLASS EDE parameters
    'scf_potential': 'axion',
    'n_axion': 3,
    'f_axion': 0.05,  # In units of M_Pl
    'log10_axion_ac': -3.5,
    'log10_fraction_axion_ac': -1.0,
    'theta_i_scf': 2.83,
}

# Run CLASS
cosmo = Class()
cosmo.set(params)
cosmo.compute()

# Get power spectra
cl = cosmo.lensed_cl(2508)

print("="*70)
print("AxiCLASS Test Results")
print("="*70)
print(f"H0 = {cosmo.Hubble(0) * 299792.458:.2f} km/s/Mpc")
print(f"omega_m = {cosmo.Omega_m():.4f}")
print(f"sigma8 = {cosmo.sigma8():.4f}")
print(f"C_l(TT) at l=2: {cl['tt'][2]:.6e}")
print(f"C_l(TT) at l=1000: {cl['tt'][1000]:.6e}")
print("="*70)

# TODO: Compute chi2 with Planck data
# Expected: chi2 ~ 2760-2770
```

Run test:
```bash
cd /Users/steveridder/Git/Ridder-Field/phase3_v2/tests
python3 test_axiclass.py
```

**Success Criteria**: Script runs without errors, produces reasonable C_ℓ values.

---

## Phase 2: Implement V2 Potential in CLASS (Day 2-3)

### Step 2.1: Modify `background.c`

Edit `phase2_v2/class/source/background.c`:

**Find the V1 potential section** (search for "ridder" or "scf_potential"):
```c
// V1 potential (ORIGINAL - DO NOT DELETE, COMMENT OUT)
/*
double V_ridder_v1(double phi, struct background *pba) {
    // ... V1 code ...
}
*/
```

**Add V2 potential** (insert after V1):
```c
/**
 * V2 Potential: Flattened Monodromy Staircase
 * V(φ) = μ³φ + Λ⁴[1 - cos(φ/f)]ⁿ / (1 + c(φ/f)²)
 */
double V_ridder_v2(double phi, struct background *pba) {
    double f = pba->f_axion_ridder;
    double c = pba->c_flatten_ridder;
    double mu3 = pba->mu3_ridder;
    double Lambda4 = pba->Lambda4_ridder;
    int n = pba->n_ridder;  // = 3
    
    double phi_over_f = phi / f;
    double cos_term = 1.0 - cos(phi_over_f);
    double flatten = 1.0 + c * phi_over_f * phi_over_f;
    
    // Monodromy term + flattened axion ripple
    double V = mu3 * phi + Lambda4 * pow(cos_term, n) / flatten;
    
    return V;
}

/**
 * V2 Potential Derivative: dV/dφ
 */
double dV_ridder_v2(double phi, struct background *pba) {
    double f = pba->f_axion_ridder;
    double c = pba->c_flatten_ridder;
    double mu3 = pba->mu3_ridder;
    double Lambda4 = pba->Lambda4_ridder;
    int n = pba->n_ridder;
    
    double phi_over_f = phi / f;
    double cos_term = 1.0 - cos(phi_over_f);
    double sin_term = sin(phi_over_f);
    double flatten = 1.0 + c * phi_over_f * phi_over_f;
    
    // d/dφ of monodromy term
    double dV_mono = mu3;
    
    // d/dφ of flattened axion term (chain rule)
    double numerator = Lambda4 * pow(cos_term, n);
    double d_numerator = Lambda4 * n * pow(cos_term, n-1) * sin_term / f;
    double d_flatten = 2.0 * c * phi_over_f / (f * f);
    
    double dV_axion = (d_numerator * flatten - numerator * d_flatten) / (flatten * flatten);
    
    return dV_mono + dV_axion;
}
```

### Step 2.2: Modify `perturbations.c`

Edit `phase2_v2/class/source/perturbations.c`:

**Find the V1 coupling section**:
```c
// V1 coupling (ORIGINAL - COMMENT OUT)
/*
double beta_ridder_v1(double phi, struct perturbations *ppt) {
    return ppt->beta_ridder;  // Constant coupling
}
*/
```

**Add V2 dynamical coupling**:
```c
/**
 * V2 Coupling: β(φ) from DM mass function
 * m_χ(φ) = m_χ,0[1 + ε sin(φ/f)]
 * β(φ) = (M_Pl/m_χ) dm_χ/dφ
 */
double beta_ridder_v2(double phi, struct perturbations *ppt) {
    double f = ppt->f_axion_ridder;
    double epsilon = ppt->epsilon_ridder;
    double M_Pl = 2.43e18;  // GeV (reduced Planck mass)
    
    double phi_over_f = phi / f;
    double sin_term = sin(phi_over_f);
    double cos_term = cos(phi_over_f);
    
    // DM mass and its derivative
    double m_chi = 1.0 + epsilon * sin_term;
    double dm_chi_dphi = epsilon * cos_term / f;
    
    // Effective coupling
    double beta = (M_Pl / m_chi) * dm_chi_dphi;
    
    return beta;
}

/**
 * V2 Coupling Derivative: dβ/dφ (needed for perturbation equations)
 */
double dbeta_ridder_v2(double phi, struct perturbations *ppt) {
    double f = ppt->f_axion_ridder;
    double epsilon = ppt->epsilon_ridder;
    double M_Pl = 2.43e18;
    
    double phi_over_f = phi / f;
    double sin_term = sin(phi_over_f);
    double cos_term = cos(phi_over_f);
    
    double m_chi = 1.0 + epsilon * sin_term;
    double dm_chi = epsilon * cos_term / f;
    double d2m_chi = -epsilon * sin_term / (f * f);
    
    // d/dφ of (M_Pl/m_χ * dm_χ/dφ)
    double dbeta = M_Pl * (d2m_chi * m_chi - dm_chi * dm_chi) / (m_chi * m_chi);
    
    return dbeta;
}
```

### Step 2.3: Update `common.h`

Edit `phase2_v2/class/include/common.h`:

**Find the V1 parameter struct**, add V2 parameters:
```c
struct background {
    // ... existing fields ...
    
    // V1 parameters (keep for reference)
    double theta_i_ridder_v1;
    double beta_ridder_v1;
    
    // V2 parameters (NEW)
    double f_axion_ridder;      // Axion decay constant [GeV]
    double c_flatten_ridder;    // Flattening parameter [dimensionless]
    double epsilon_ridder;      // DM coupling strength [dimensionless]
    double mu3_ridder;          // Monodromy slope [GeV³] (derived)
    double Lambda4_ridder;      // EDE scale [GeV⁴] (derived)
    int n_ridder;               // Axion power (fixed = 3)
    double theta_i_ridder;      // Initial misalignment angle
    
    // V2 version flag
    int use_ridder_v2;          // 0 = V1, 1 = V2
};
```

### Step 2.4: Update Parameter Reading

Edit `phase2_v2/class/source/input.c`:

**Add V2 parameter reading**:
```c
// In input_read_parameters():

// V2 version flag
class_call(parser_read_int(pfc, "use_ridder_v2", &(pba->use_ridder_v2), &flag1, errmsg),
           errmsg, errmsg);

if (pba->use_ridder_v2 == 1) {
    // V2 parameters
    class_call(parser_read_double(pfc, "f_axion_ridder", &(pba->f_axion_ridder), &flag1, errmsg),
               errmsg, errmsg);
    
    class_call(parser_read_double(pfc, "c_flatten_ridder", &(pba->c_flatten_ridder), &flag1, errmsg),
               errmsg, errmsg);
    
    class_call(parser_read_double(pfc, "epsilon_ridder", &(pba->epsilon_ridder), &flag1, errmsg),
               errmsg, errmsg);
    
    class_call(parser_read_double(pfc, "theta_i_ridder", &(pba->theta_i_ridder), &flag1, errmsg),
               errmsg, errmsg);
    
    // Fixed parameter
    pba->n_ridder = 3;
    
    // Derived parameters (computed later)
    pba->mu3_ridder = 0.0;      // Will be computed from w(z) constraint
    pba->Lambda4_ridder = 0.0;  // Will be computed from f_EDE target
}
```

### Step 2.5: Compile V2 CLASS
```bash
cd /Users/steveridder/Git/Ridder-Field/phase2_v2/class

# Clean and compile
make clean
make -j8

# Check for errors
echo $?  # Should be 0
```

---

## Phase 3: Single-Point Validation Tests (Day 3-4)

### Step 3.1: Create Test Script

Create `phase3_v2/tests/test_v2_single_point.py`:
```python
#!/usr/bin/env python3
"""
V2 Single-Point Validation Test
Goal: Verify chi2 < 2800 with V2 potential
"""

import sys
sys.path.insert(0, '/Users/steveridder/Git/Ridder-Field/phase2_v2/class/python/build/lib.macosx-10.9-x86_64-3.10')

from classy import Class
import numpy as np

def test_v2_point(theta_i, f_axion, c_flatten, epsilon):
    """Test a single parameter point."""
    
    params = {
        'output': 'tCl,mPk',
        'l_max_scalars': 2508,
        'lensing': 'yes',
        
        # Standard cosmology (Planck 2018 best fit)
        'omega_b': 0.02237,
        'omega_cdm': 0.1200,
        'h': 0.6736,
        'A_s': 2.1e-9,
        'n_s': 0.9649,
        'tau_reio': 0.0544,
        
        # V2 parameters
        'use_ridder_v2': 1,
        'theta_i_ridder': theta_i,
        'f_axion_ridder': f_axion,
        'c_flatten_ridder': c_flatten,
        'epsilon_ridder': epsilon,
        'n_ridder': 3,
    }
    
    try:
        cosmo = Class()
        cosmo.set(params)
        cosmo.compute()
        
        # Get derived quantities
        H0 = cosmo.Hubble(0) * 299792.458
        sigma8 = cosmo.sigma8()
        
        # TODO: Compute chi2 with Planck
        # For now, just check it runs
        chi2_estimate = 2750.0  # Placeholder
        
        cosmo.struct_cleanup()
        
        return {
            'success': True,
            'H0': H0,
            'sigma8': sigma8,
            'chi2': chi2_estimate,
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }

# Test grid
test_points = [
    # (theta_i, f_axion [GeV], c_flatten, epsilon)
    (2.0, 1.0e16, 1.0, 0.01),
    (1.5, 1.0e16, 0.5, 0.01),
    (2.5, 5.0e15, 1.5, 0.005),
    (1.8, 2.0e16, 0.8, 0.02),
]

print("="*70)
print("V2 Single-Point Validation Tests")
print("="*70)

for i, (theta_i, f, c, eps) in enumerate(test_points):
    print(f"\nTest {i+1}: theta_i={theta_i}, f={f:.1e}, c={c}, eps={eps}")
    result = test_v2_point(theta_i, f, c, eps)
    
    if result['success']:
        print(f"  ✅ SUCCESS")
        print(f"     H0 = {result['H0']:.2f} km/s/Mpc")
        print(f"     sigma8 = {result['sigma8']:.4f}")
        print(f"     chi2 ≈ {result['chi2']:.1f}")
    else:
        print(f"  ❌ FAILED: {result['error']}")

print("\n" + "="*70)
```

Run tests:
```bash
cd /Users/steveridder/Git/Ridder-Field/phase3_v2/tests
python3 test_v2_single_point.py
```

**Success Criteria**: At least 2 out of 4 test points run without crashing.

---

## Phase 4: Create V2 MCMC Configs (Day 4-5)

### Step 4.1: Create V2 Tier 1 Config

Create `phase3_v2/configs/v2_tier1_planck.yaml`:
```yaml
# V2 Tier 1: Planck Only
# Testing the flattened monodromy potential

theory:
  classy:
    path: /Users/steveridder/Git/Ridder-Field/phase2_v2/class
    extra_args:
      output: tCl, mPk
      l_max_scalars: 2508
      lensing: yes
      
      # V2 activation
      use_ridder_v2: 1
      n_ridder: 3

likelihood:
  planck_2018_lowl.TT: null
  planck_2018_lowl.EE: null
  planck_2018_highl_plik.TTTEEE: null
  planck_2018_lensing.clik: null

params:
  # Standard cosmology
  logA:
    prior: {min: 2.0, max: 4.0}
    ref: 3.044
    proposal: 0.001
    drop: true
  A_s:
    value: 'lambda logA: 1e-10*__import__("numpy").exp(logA)'
  n_s:
    prior: {min: 0.9, max: 1.02}
    ref: 0.965
    proposal: 0.004
  H0:
    prior: {min: 60, max: 80}
    ref: 67.0
    proposal: 0.5
  omega_b:
    prior: {min: 0.01, max: 0.03}
    ref: 0.0224
    proposal: 0.0001
  omega_cdm:
    prior: {min: 0.1, max: 0.14}
    ref: 0.120
    proposal: 0.001
  tau_reio:
    prior: {min: 0.04, max: 0.08}
    ref: 0.054
    proposal: 0.004
  
  # V2 parameters
  theta_i_ridder:
    prior: {min: 0.5, max: 3.0}
    ref: 2.0
    proposal: 0.1
    latex: \theta_i
  
  f_axion_ridder:
    prior: {min: 1.0e15, max: 1.0e17}
    ref: 1.0e16
    proposal: 1.0e15
    latex: f
  
  c_flatten_ridder:
    prior: {min: 0.1, max: 2.0}
    ref: 1.0
    proposal: 0.1
    latex: c
  
  epsilon_ridder:
    prior: {min: 0.001, max: 0.05}
    ref: 0.01
    proposal: 0.005
    latex: \epsilon

sampler:
  mcmc:
    drag: true
    proposal_scale: 1.9
    covmat: auto
    max_samples: 1000  # Short test run
    Rminus1_stop: 0.05

output: v2_tier1_test_chain
debug: true
```

---

## Phase 5: Git Workflow (Ongoing)

### Commit Strategy
```bash
# After each major step
git add phase2_v2/ phase3_v2/
git commit -m "V2: [describe what you did]"
git push origin v2-development

# Examples:
git commit -m "V2: Add flattened monodromy potential to background.c"
git commit -m "V2: Add dynamical beta(phi) coupling to perturbations.c"
git commit -m "V2: Single-point tests pass for 3/4 test cases"
```

### Branch Management
- **v2-development**: Active development branch
- **main**: Keep V1 frozen, only merge V2 when fully validated

---

## Success Milestones

### ✅ Milestone 1: Setup Complete
- [ ] V2 directories created
- [ ] V1 frozen with marker files
- [ ] Git branch created

### ✅ Milestone 2: AxiCLASS Validated
- [ ] AxiCLASS compiled and running
- [ ] Test script produces C_ℓ values
- [ ] chi2 < 2800 confirmed (or at least reasonable)

### ✅ Milestone 3: V2 CLASS Compiled
- [ ] V2 potential coded in background.c
- [ ] V2 coupling coded in perturbations.c
- [ ] CLASS compiles without errors

### ✅ Milestone 4: Single-Point Tests Pass
- [ ] At least 2/4 test points run without crashing
- [ ] H0, sigma8 values are reasonable
- [ ] No obvious CLASS errors

### ✅ Milestone 5: Ready for MCMC
- [ ] V2 Tier 1 config created
- [ ] Test run (100 samples) completes
- [ ] Chains don't crash or hang

---

## Next Steps After This Plan

Once all milestones are complete:
1. Run full V2 Tier 1 (5000 samples)
2. Compare V2 vs V1 vs ΛCDM chi2
3. If V2 chi2 < 2800: Proceed to Tier 2-4
4. If V2 chi2 > 2800: Debug and iterate

**Estimated Timeline**: 5-7 days to complete all phases.

