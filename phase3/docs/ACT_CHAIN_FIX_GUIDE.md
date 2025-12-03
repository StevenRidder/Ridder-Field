# ACT Chain Fix Guide: Getting the Soft Shoulder Analysis Running

**Date**: 2025-12-02  
**Status**: Actionable fixes based on comprehensive audit  
**Goal**: Resume ACT+Planck EDE chains that are currently hanging

---

## Executive Summary

Your EDE chains are hanging due to a known numerical bug in the Ridder CLASS implementation (Issue #7). ΛCDM chains work fine because they don't trigger the Ridder field code path. The fix involves bypassing the random initial point search that triggers the hang, combined with correcting configuration mismatches between your playbook and your actual YAML files.

---

## Part 1: Understanding Why Chains Crash

### The Core Problem: Issue #7 (Documented in ACT_LIKELIHOOD_DEBUG.md)

When Cobaya starts an EDE chain, it needs to find a valid initial point in parameter space. It does this by:

1. Randomly sampling parameter values from priors
2. Calling CLASS to compute C_ℓ spectra
3. Checking if the posterior is finite
4. Repeating until it finds a valid point (up to `max_tries` attempts)

**The bug**: The Ridder CLASS implementation has a numerical stability issue when computing high multipole moments (l_max ≥ 1000) with EDE enabled. Instead of failing with an error, CLASS enters an infinite loop inside `compute()`.

**Evidence from your debugging**:

| Configuration | Result |
|--------------|--------|
| ΛCDM at l_max=7000 | ✓ Works (no Ridder code path) |
| EDE at l_max=7000 | ✗ Silent hang (Ridder integrator stuck) |
| EDE at l_max=100 | ✓ Works (but useless for ACT) |
| H0-fixed EDE | ✓ Works (per terminal output) |

The hang occurs in CLASS C code, specifically during the numerical integration of the Ridder field perturbations at high ℓ. This is NOT a YAML configuration problem and cannot be fixed by changing accuracy parameters.

### Why Your H0-Fixed Chains Work

Your terminal shows that H0-fixed chains are converging:

```
H0=69: Delta=+2.2 (Converging)
H0=70: Delta=+14.5 (Converging)
H0=71: Delta=+33.7 (Converging)
H0=72: Delta=+91.0 (Converging)
```

These work because fixing H0 constrains the parameter space enough that Cobaya's initial point search finds valid points more quickly. With fewer free parameters, there are fewer combinations that trigger the unstable numerical regime.

### Why Random Initial Points Hang

When Lambda_EDE_ridder is free with a wide prior [0.0, 2.5], random sampling can land on combinations where:

- Lambda is far from 1.0 (triggering different oscillation regimes)
- Combined with certain omega_cdm/H0 values that stress the integrator
- The Ridder field evolution becomes numerically stiff at high ℓ

The integrator doesn't crash—it just takes increasingly small timesteps forever.

---

## Part 2: The Fixes and Why They Work

### Fix 1: Provide a Good Starting Point (Bypass Random Search)

**What to do**: Create a starting point file with LCDM best-fit values plus Lambda_EDE_ridder = 1.0.

**Why this works**: 

The starting point workaround bypasses the random initial point search entirely. Instead of letting Cobaya randomly sample until it finds a valid point (which triggers the hang), you tell it exactly where to start.

The LCDM best-fit values are known to work (you have converged LCDM chains). Adding Lambda_EDE_ridder = 1.0 to these values puts you in the "safe" numerical regime where:

- z_osc ≈ 4500 (the correct soft shoulder regime)
- The Ridder field evolution is numerically stable
- CLASS completes without hanging

Your `ACT_DR6_playbook.md` already documents this workaround (line 458-460):

> **Workaround**: Provide a good starting point (e.g., LCDM best-fit + Lambda_EDE_ridder=1.0)

Once the chain starts from a valid point, it can explore the parameter space incrementally. Each MCMC step is a small perturbation from the current point, so you stay in the numerically stable regime.

**Implementation**: Use Cobaya's `ref` mechanism or a starting point file. The `ref` values in your config already point close to good values—the issue is that Cobaya ignores `ref` during initial point search and samples uniformly from `prior`.

---

### Fix 2: Tighten the Lambda Prior to [0.8, 1.2]

**What to do**: Change `act_world_ede.yaml` line 105 from:
```yaml
Lambda_EDE_ridder:
  prior: {min: 0.0, max: 2.5}  # CURRENT - too wide
```
to:
```yaml
Lambda_EDE_ridder:
  prior: {min: 0.8, max: 1.2}  # CORRECT - matches playbook
```

**Why this works**:

Your playbook Rule #6 (lines 74-82) explains:

> Do not widen this prior and do not shift it away from 1.0. Wider priors land in the wrong z-osc regime and destroy the shoulder (Issue #5).

The Lambda parameter controls when EDE becomes dynamical:

| Lambda | z_osc | Physical Regime |
|--------|-------|-----------------|
| 0.6 | ~2500 | Too late (post-recombination) |
| **0.8-1.2** | **3500-5500** | **CORRECT soft shoulder** |
| 1.5 | ~7000 | Too early |
| 2.0 | ~9500 | Wrong regime entirely |

With a wide prior [0.0, 2.5], two things go wrong:

1. **Initial point search**: Random sampling can land on Lambda values that trigger numerical instability
2. **Chain convergence**: Even if you get past the initial point, the chain might converge to Lambda ≈ 2.0 (wrong physics regime) because that's a local minimum in χ²

Your Issue #5 documentation (`ACT_LIKELIHOOD_DEBUG.md` lines 270-322) shows exactly this problem:

> ACT chains with wide Lambda_EDE prior [0.1, 3.0] converged to Lambda ≈ 1.96, giving z_osc = 9528 (EDE kicks in at z > 9000). Template fit: A_sh = -3.76 (ACT **disfavors** shoulder).

This is the WRONG EDE regime. You're not measuring the soft shoulder—you're measuring something else entirely.

The tight prior [0.8, 1.2] ensures:
- Initial point search stays in numerically stable regime
- Chains converge to the correct physics (z_osc ~ 4500)
- Template amplitude A_sh actually measures the soft shoulder

---

### Fix 3: Add the Missing Lensing Likelihood

**What to do**: Add `planck_2018_lensing.clik` to the likelihood block.

**Why this works**:

Your playbook Rule #7 (lines 86-92) specifies:

> For ACT+Planck analysis, always include:
> - planck_2018_lowl.TT
> - planck_2018_lowl.EE
> - planck_2018_highl_plik.TTTEEE
> - **planck_2018_lensing.clik** ← MISSING FROM YOUR CONFIG
> - act_dr6_mflike.ACTDR6MFLike

Your current `act_world_ede.yaml` (lines 44-52) omits the lensing likelihood with a comment:

```yaml
# CMB - NO LENSING (requests mPk which Ridder CLASS can't handle)
```

However, this comment may be outdated. The lensing likelihood provides important constraints on:
- The amplitude parameter A_s (breaking degeneracy with tau_reio)
- Late-time structure growth (relevant for S8 measurement)

If your Ridder CLASS truly can't handle the matter power spectrum request, you have two options:
1. Leave lensing out (current state) but acknowledge reduced constraining power
2. Implement mPk output in Ridder CLASS (requires C code changes)

For now, leaving lensing out is acceptable, but note that your playbook claims it should be included.

---

### Fix 4: Add Missing ACT Calibration Parameter

**What to do**: Add `calE_dr6_pa4_f220` to the params block.

**Why this works**:

Your playbook (lines 368-370) lists this parameter, but your config only has:
- calE_dr6_pa5_f090
- calE_dr6_pa5_f150
- calE_dr6_pa6_f090
- calE_dr6_pa6_f150

Missing: `calE_dr6_pa4_f220`

The ACT DR6 likelihood expects all calibration parameters. Missing one can cause silent failures where the likelihood returns incorrect values or fails to evaluate properly.

---

## Part 3: Why These Fixes Together Will Work

### The Chain of Causation

1. **EDE chains hang** → because CLASS hangs during initial point search
2. **CLASS hangs** → because random Lambda values trigger numerical instability
3. **Random Lambda values** → because wide prior allows sampling unstable regimes
4. **Starting point ignored** → because Cobaya samples from prior, not ref, during initial search

### The Fixes Break This Chain

1. **Tight Lambda prior [0.8, 1.2]** → random samples stay in stable regime
2. **Good starting point** → bypass random sampling entirely
3. **Complete config** → no missing parameters to cause silent failures

### Evidence This Will Work

**Evidence 1: H0-fixed chains work**

Your terminal shows H0-fixed EDE chains converging. This proves that when you constrain the parameter space (even by just fixing H0), CLASS can successfully compute EDE spectra at l_max=7000.

**Evidence 2: Your playbook's tight prior recommendation**

The tight prior [0.8, 1.2] was determined empirically through Issue #5 debugging. Chains with this prior converge to Lambda ≈ 1.04 (z_osc = 4729), which is exactly the soft shoulder regime.

**Evidence 3: LCDM chains work**

LCDM chains complete without hanging, proving the infrastructure (Cobaya, likelihoods, CLASS installation) is correct. The only difference is the Ridder field code path.

**Evidence 4: Your `act_template_fit.py` is ready**

The template fit code (lines 374-384) already validates the Lambda regime:

```python
lambda_val = params_ede.get('Lambda_EDE_ridder', 1.0)
if lambda_val < 0.7 or lambda_val > 1.3:
    print(f"\n⚠️  WARNING: Lambda = {lambda_val:.2f} is outside optimal range [0.8, 1.2]!")
```

This confirms the team already knows the correct regime—the config just needs to match.

---

## Part 4: Step-by-Step Fix Sequence

### Step 1: Create Starting Point File

Extract best-fit from your converged LCDM chain (`chains/act_world_lcdm_c*.1.txt`), then add Lambda_EDE_ridder = 1.0.

### Step 2: Update `configs/act_world_ede.yaml`

Changes needed:
- Lambda prior: [0.0, 2.5] → [0.8, 1.2]
- Add calE_dr6_pa4_f220 parameter
- (Optional) Add planck_2018_lensing.clik if mPk is now supported

### Step 3: Launch with Starting Point

Use Cobaya's override mechanism to inject the starting point, bypassing random search.

### Step 4: Monitor for Hang

If chains still hang, the starting point didn't prevent random exploration. In that case, you may need to:
- Use even tighter Lambda prior
- Fix the C code bug directly (requires touching perturbations.c or background.c)

---

## Part 5: Long-Term Fix (C Code Bug)

The real fix is to address the numerical instability in Ridder CLASS. Based on your Issue #7 documentation, the bug is likely in:

- `perturbations.c`: Ridder field perturbation evolution at high k/ℓ
- `background.c`: Ridder field background evolution causing downstream instability

Symptoms suggest the ODE integrator takes increasingly small timesteps without converging. Common causes:
- Stiff ODEs without appropriate solver switching
- Division by small numbers (phase oscillations)
- Accumulating numerical error in high-order multipoles

Until this C bug is fixed, the starting point + tight prior workaround is the production solution.

---

## Summary Table

| Fix | What | Why | Evidence |
|-----|------|-----|----------|
| Starting point | Seed with LCDM + Lambda=1.0 | Bypass random search that hangs | H0-fixed chains work |
| Tight Lambda prior | [0.8, 1.2] instead of [0.0, 2.5] | Stay in stable numerical regime | Issue #5 documented |
| Add calE_dr6_pa4_f220 | Missing ACT calibration param | Complete likelihood evaluation | Playbook lists it |
| (Optional) Add lensing | planck_2018_lensing.clik | Better constraints | Playbook requires it |

---

## Expected Outcome

After applying these fixes:

1. EDE chains will start without hanging
2. Chains will converge to Lambda ≈ 1.0 (z_osc ≈ 4500)
3. Template fit will measure A_sh for the actual soft shoulder
4. You'll get a proper comparison of Δχ²(ACT) between EDE and ΛCDM

This enables the Track 2 analysis: measuring whether ACT sees the predicted soft shoulder pattern at the 6.4σ level claimed in your paper draft.

---

**Last Updated**: 2025-12-02  
**Based On**: Audit of ACT_DR6_playbook.md, ACT_LIKELIHOOD_DEBUG.md, ACT_ANALYSIS_README.md, act_world_ede.yaml, act_world_lcdm.yaml, ridder_cosmology_paper.tex, terminal logs

