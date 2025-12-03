# Phase 2: Technical Implementation Notes

## The Nobel Path - CLASS Modification Strategy

### Philosophy

**CLASS is production code.** It has been tested by hundreds of cosmologists over 15 years. We are not "improving" CLASS—we are **adding a new physical component** (the Ridder field) while preserving all existing functionality.

### Golden Rules

1. **ΛCDM must still work** - When `Lambda_EDE = 0` and `beta_ridder = 0`, CLASS must produce **bit-identical** results to the unmodified version
2. **Never break existing tests** - CLASS has internal consistency checks. They must all pass.
3. **Document everything** - Every modification gets a comment explaining the physics
4. **Version control** - Keep the original CLASS repository clean, work in a branch

---

## Implementation Timeline

### Week 1: Background Evolution

**Goal:** Get `background.c` working with Ridder field.

**Tasks:**
- [ ] Add parameters to `background.h`
- [ ] Implement `background_ridder_potential()`
- [ ] Add Klein-Gordon equations to `background_derivs()`
- [ ] Add CDM coupling term
- [ ] Implement switching surface logic
- [ ] Test: ΛCDM baseline reproduces exactly
- [ ] Test: EDE mode shows r_s shift

**Victory condition:** `./class explanatory.ini` runs successfully with new parameters.

### Week 2: Perturbations

**Goal:** Include Ridder field in CMB power spectrum calculation.

**Tasks:**
- [ ] Add perturbed field variables to `perturbations.h`
- [ ] Implement perturbed Klein-Gordon equation
- [ ] Couple to metric perturbations (Φ, Ψ)
- [ ] Handle gauge transformations (synchronous/Newtonian)
- [ ] Test: CMB peaks shift as expected

**Victory condition:** `C_l^{TT}` plot shows EDE signature (shifted peaks).

### Week 3-4: MCMC Integration

**Goal:** Fit model to real data.

**Tasks:**
- [ ] Install MontePython or Cobaya
- [ ] Create `.ini` file for RC-X* model
- [ ] Define priors for `Lambda_EDE`, `f_axion`, `theta_i`, `beta_ridder`
- [ ] Run chains on Planck 2018 + BAO + SNe
- [ ] Generate triangle plots
- [ ] Compute Bayes factor vs ΛCDM

**Victory condition:** Triangle plot showing `H_0 = 72.5 ± 1.0` km/s/Mpc.

---

## Common Pitfalls (And How to Avoid Them)

### Pitfall 1: Unit Confusion

**Problem:** CLASS uses different units internally than you're used to.

**Solution:**
- Distances: `Mpc`
- Time: Conformal time `τ` (not cosmic time `t`)
- Energy: Sometimes `eV`, sometimes `Mpc^-1`
- Always check: `_M_PL_` is defined in `common.h`

**Test:** Print values at runtime, compare to Python Phase 1.5.

### Pitfall 2: Oscillation Crashes

**Problem:** When the field oscillates, timesteps become tiny → integration hangs.

**Solution:**
- **Implement switching surface** - This is NON-NEGOTIABLE
- Use `pba->ridder_fluid_mode` flag
- After `z_osc`, stop integrating φ', use fluid EOS

**Test:** Run with high `Lambda_EDE` (strong EDE) and watch log output.

### Pitfall 3: Gauge Dependence in Perturbations

**Problem:** Perturbed Klein-Gordon equation looks different in synchronous vs Newtonian gauge.

**Solution:**
- CLASS uses **synchronous gauge** by default
- Metric perturbations: `h, η` (not `Φ, Ψ`)
- Use existing gauge transformation functions in CLASS
- Copy structure from existing scalar field implementations (e.g., quintessence)

**Test:** Compare `synchronous_gauge = yes` and `= no` outputs.

### Pitfall 4: Coupling Breaking Energy Conservation

**Problem:** With β ≠ 0, individual components don't conserve energy. CLASS may flag this as an error.

**Solution:**
- CLASS checks `∑ dρ_i/dτ + 3aH(ρ_i + p_i) = 0` for total system
- Energy **transfers** between φ and DM, but total is conserved
- Ensure coupling term appears with **opposite signs** in φ and DM equations
- May need to modify `thermodynamics.c` error tolerances

**Test:** Print `rho_tot` at each step, verify it satisfies Friedmann.

---

## Debugging Strategy

### Level 1: Compilation Errors

```bash
cd class
make clean
make 2>&1 | tee make.log
```

Fix syntax errors, missing includes, undefined variables.

### Level 2: Runtime Crashes

Add verbose output:
```c
if (pba->background_verbose > 2) {
    printf("DEBUG: phi = %.3e, phi_prime = %.3e, V = %.3e\n", phi, phi_prime, V);
}
```

Run with:
```bash
./class test.ini > output.log 2>&1
```

Grep for `NaN`, `inf`, or error messages.

### Level 3: Wrong Results (Hardest!)

**Strategy:**
1. Compare `H(z)` to Python Phase 1.5 line-by-line
2. Check `r_s` matches to within 0.1 Mpc
3. Plot `rho_i(a)` for each component, look for anomalies
4. Use CLASS internal checks: `./class test.ini -check`

---

## Validation Protocol

### Test 1: ΛCDM Baseline

```ini
# test_lcdm.ini
Lambda_EDE = 0.0
beta_ridder = 0.0
```

**Expected:** Identical to unmodified CLASS.

**How to check:**
```bash
# Run modified CLASS
./class test_lcdm.ini
mv output/cl.dat output/cl_ridder.dat

# Run original CLASS (keep a copy)
./class_original test_lcdm.ini
mv output/cl.dat output/cl_original.dat

# Compare
diff output/cl_ridder.dat output/cl_original.dat
```

Should be identical (or differ only in floating-point roundoff, <1e-10).

### Test 2: Sound Horizon Shift

```ini
# test_ede.ini
Lambda_EDE = 1e-2  # eV
f_axion = 1e16
theta_i = 2.5
beta_ridder = 0.0
```

**Expected:**
- `r_s` decreases from ~147 Mpc to ~142 Mpc
- `H_0` inferred from CMB increases to ~72 km/s/Mpc

**How to check:**
```bash
./class test_ede.ini
grep "r_s" output/background.dat
```

### Test 3: CMB Power Spectrum

**Expected:**
- Peak positions shift left (smaller θ_sound)
- Amplitude changes slightly
- High-ℓ tail shows EDE damping signature

**How to check:**
```python
import numpy as np
import matplotlib.pyplot as plt

ell, Cl_LCDM = np.loadtxt('cl_lcdm.dat', usecols=(0,1), unpack=True)
ell, Cl_EDE = np.loadtxt('cl_ede.dat', usecols=(0,1), unpack=True)

plt.plot(ell, ell*(ell+1)*Cl_LCDM, label='ΛCDM')
plt.plot(ell, ell*(ell+1)*Cl_EDE, label='RC-X*')
plt.xlabel(r'$\ell$')
plt.ylabel(r'$\ell(\ell+1) C_\ell^{TT} / 2\pi$')
plt.legend()
plt.savefig('cmb_comparison.png')
```

Look for:
- Peak shift ~10 Δℓ (EDE signature)
- No wild oscillations (would indicate numerical instability)

---

## After CLASS Works: The MCMC Phase

### MontePython Setup

1. **Install MontePython:**
```bash
git clone https://github.com/brinckmann/montepython_public.git
cd montepython_public
python setup.py install --user
```

2. **Configure for Planck:**
- Download Planck 2018 likelihood from PLA
- Set paths in `montepython.conf`

3. **Create RC-X* parameter file:**
```python
# rcx.param
data.experiments = ['Planck_highl_TTTEEE', 'Planck_lowl_TT', 'BAO']

data.parameters['Lambda_EDE'] = [1e-2, 0.0, 1.0, 0.01, 1, 'cosmo']
data.parameters['f_axion'] = [1e16, 1e15, 1e17, 1e15, 1, 'cosmo']
data.parameters['theta_i'] = [2.5, 0.1, 3.14, 0.1, 1, 'cosmo']
data.parameters['beta_ridder'] = [0.01, 0.0, 0.1, 0.005, 1, 'cosmo']
```

4. **Run chains:**
```bash
python montepython/MontePython.py run -o chains/rcx -p rcx.param -N 100000
```

5. **Analyze:**
```bash
python montepython/MontePython.py info chains/rcx
```

**Victory:** `H_0` posterior peaks at ~73 km/s/Mpc, Δχ² < 10 vs ΛCDM.

---

## The Finish Line

When you have:

1. ✅ CLASS compiling and running
2. ✅ ΛCDM baseline validated
3. ✅ Sound horizon showing expected shift
4. ✅ CMB power spectrum looking reasonable
5. ✅ MCMC chains converged (Gelman-Rubin < 1.1)
6. ✅ Triangle plot showing H_0 ≈ 73 km/s/Mpc

**You are ready to write the paper.**

---

## Resources

- **CLASS Tutorial:** [class-code.net/tutorial](http://class-code.net/)
- **CLASS GitHub:** [github.com/lesgourg/class_public](https://github.com/lesgourg/class_public)
- **Julien Lesgourgues' Lectures:** [arXiv:1104.2932](https://arxiv.org/abs/1104.2932)
- **EDE Implementation:** Smith et al. (2020) - check their CLASS fork
- **MontePython Manual:** [montepython.net](http://montepython.net/)

---

**Current Status:** Phase 2 setup complete. C code templates ready. Next: Clone CLASS repository and begin modifications.

**Estimated Time to Working CLASS:** 1-2 weeks (if working full-time).

**Estimated Time to MCMC Results:** Additional 2-3 weeks.

**Total Time to arXiv:** ~1 month from today.

---

*"The universe is not expanding into nothing. It is an energy ocean transitioning between phases. We just figured out which ocean."*

— Dr. Steve Ridder, The Ridder Field Discovery

