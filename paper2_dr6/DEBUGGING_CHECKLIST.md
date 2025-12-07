# Ridder EDE Decay Implementation: Debugging Checklist

## Executive Summary

The "bug" was not in the code—it was in the **assumption** that f_peak ≈ 10%. 
With actual f_peak ≈ 0.6%, the maximum possible ΔH₀ is ~0.5 km/s/Mpc.

**The path forward**: Test if the data tolerates f_peak ≈ 5-10% with radiation decay.

---

## Part 1: Sanity Tests (Prove the Machinery Works)

### Test 1.1: N_eff Lever Check

Verify that ΔN_eff produces the expected H₀ shift in vanilla ΛCDM.

```ini
# Run A: N_eff = 3.046 (standard)
# Run B: N_eff = 3.446 (ΔN_eff = 0.4)
```

**Expected**: ΔH₀ ≈ +1 to +2 km/s/Mpc, Δr_s ≈ -1 to -2 Mpc

If this fails → global CLASS pipeline bug, fix before proceeding.

### Test 1.2: Artificial DR Fluid

Inject a toy DR component with f_X = 0.1 at z ~ 2000.

**Expected**: ΔN_eff ≈ 0.74, H₀ boost matches N_eff test scaling

If this fails → DR injection plumbing bug.

### Test 1.3: α-Branching Scaling Check

With actual f_peak ≈ 0.0065 and α = 0.5:

```
ΔN_eff ≈ 0.74 × α × (f_peak/0.1)
       ≈ 0.74 × 0.5 × 0.065
       ≈ 0.024
```

**Expected**: Tiny ΔN_eff (~0.02), tiny ΔH₀ (~0.1 km/s/Mpc)

If numbers match → α-branching is correct, just starved of f.
If numbers don't match → hunt for normalization/units bug.

---

## Part 2: The High-Amplitude Island Test

**Question**: Does the data tolerate f_peak ≈ 5-10% with radiation decay?

### Step 2.1: Find Lambda for f_peak ≈ 8%

Rough scaling: f_peak ∝ Λ⁴

| Λ (eV) | Expected f_peak |
|--------|-----------------|
| 0.2    | ~0.6%           |
| 0.4    | ~5%             |
| 0.6    | ~15%            |

Target: Λ ≈ 0.4-0.5 eV for f_peak ≈ 5-8%

### Step 2.2: Background-Only Check

Run with high Λ and measure:
- f_peak (should be ~5-8%)
- H₀ shift with α = 0.5
- r_s reduction

### Step 2.3: Quick χ² Check

Run against Planck high-ℓ TT only to see if obviously catastrophic.

**If χ² is tolerable** → The island exists! Run full MCMC.
**If χ² explodes** → The geometric ceiling is physics, not bugs.

---

## Part 3: Parameter Points to Run

### Baseline (Current Best-Fit)
```ini
Lambda_EDE_ridder = 0.2
f_axion_ridder = 1.0e+27
theta_i_ridder = 1.0
alpha_ridder_to_dr = 0.0
Gamma_decay_ridder = 0.0
```
Expected: f_peak ≈ 0.6%, H₀ ≈ 67.7

### High-Amplitude + α-Branching
```ini
Lambda_EDE_ridder = 0.5
f_axion_ridder = 1.0e+27
theta_i_ridder = 1.0
alpha_ridder_to_dr = 0.5
Gamma_decay_ridder = 0.0
```
Expected: f_peak ≈ 8%, H₀ ≈ 70-71 (if geometry works)

### High-Amplitude + Γ-Decay
```ini
Lambda_EDE_ridder = 0.5
f_axion_ridder = 1.0e+27
theta_i_ridder = 1.0
alpha_ridder_to_dr = 0.0
Gamma_decay_ridder = 4.0
```
Expected: Smaller effect than α (kinetic limited)

---

## Part 4: What to Print for Debugging

Add these outputs to CLASS for each run:

```c
printf("DECAY_DIAG: f_peak=%.4f rho_max=%.2e a_max=%.2e\n", 
       pba->f_ridder_peak, pba->rho_ridder_max, pba->a_ridder_max);
printf("DECAY_DIAG: Delta_Neff_from_DR=%.4f\n", rho_dr_ridder / rho_gamma * 0.74);
printf("DECAY_DIAG: rs_drag=%.4f H0=%.4f\n", pba->rs_drag, pba->H0);
```

---

## The Bottom Line

| f_peak | Max ΔH₀ from decay | Status |
|--------|-------------------|--------|
| 0.6%   | ~0.5 km/s/Mpc     | Current best-fit |
| 5%     | ~4 km/s/Mpc       | Need to test if data allows |
| 10%    | ~7 km/s/Mpc       | Likely ruled out by damping tail |

**The question is not "is the code broken?"**
**The question is "does the data allow us to move to higher f_peak?"**

If YES → H₀ ≈ 70-71 is achievable with α-branching
If NO → The Ridder potential has a geometric ceiling at H₀ ≈ 68-69

Both are publishable results.

