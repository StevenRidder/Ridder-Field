# EDE Parameterization Fix - November 30, 2025

## Problem Summary

All previous EDE (Early Dark Energy) MCMC chains were using **incorrect parameter names** that CLASS did not recognize. This resulted in:

1. **EDE being effectively disabled** (Lambda_EDE_ridder = 0 by default)
2. **Wrong parameters being sampled** (shape instead of amplitude)
3. **Invalid Δχ² results** - The claimed improvements were meaningless

## Root Cause

### What the configs tried to use (WRONG):
```yaml
params:
  ridder_Lambda_EDE_eV:   # ❌ CLASS ignores this!
    prior: {min: ...}
  ridder_a_c:             # ❌ CLASS ignores this!
    prior: {min: ...}
  theta_i_ridder:         # ❌ This should be FIXED, not sampled
    prior: {min: ...}
  beta_ridder:            # ❌ This should be FIXED, not sampled
    prior: {min: ...}
```

### What CLASS actually accepts:
```yaml
# In extra_args (fixed):
Lambda_EDE_ridder   # Energy scale Λ⁴ in potential V(φ)
f_axion_ridder      # Decay constant f
theta_i_ridder      # Initial angle θᵢ (shape parameter)
beta_ridder         # DM coupling β (shape parameter)
n_ridder            # Potential exponent n
```

### What was actually happening:
- `ridder_Lambda_EDE_eV` and `ridder_a_c` were IGNORED by CLASS
- `Lambda_EDE_ridder` defaulted to 0.0, disabling the Ridder field entirely
- Chains were varying shape parameters (θᵢ, β) while keeping amplitude at zero
- This means **no EDE physics was ever computed**

## The Fix

### Correct parameterization (per the paper's physics):

**SAMPLE amplitude:**
```yaml
params:
  Lambda_EDE_ridder:
    prior: {min: 0.1, max: 3.0}
    ref: 1.0
    proposal: 0.2
    latex: \Lambda_{EDE}
```

**FIX shape in extra_args:**
```yaml
theory:
  classy:
    extra_args:
      n_ridder: 3
      theta_i_ridder: 1.0
      beta_ridder: 0.0
      f_axion_ridder: 1.0e+27
```

### How to run chains with custom CLASS:
```bash
# Use the wrapper script that sets PYTHONPATH:
./run_ede_chain.sh configs/tier5_ede_shoes_predesi.yaml
```

## Archived Files

Files with incorrect parameterization have been moved to:
```
archive/wrong_parameterization_20251130/
├── README.txt
├── configs/           # Old incorrect YAML configs
└── *.log             # Old log files
```

**DO NOT use these for any analysis - the results are invalid.**

## Physics Reference

The Ridder potential is:
```
V(φ) = Λ⁴ × [1 - cos(φ/f)]ⁿ
```

Where:
- `Lambda_EDE_ridder` (Λ) - **Energy scale** - controls amplitude of EDE shelf
- `f_axion_ridder` (f) - **Decay constant** - controls timing via mass scale
- `theta_i_ridder` (θᵢ) - **Initial angle** - shape parameter
- `n_ridder` (n) - **Exponent** - shape parameter (typically 3)
- `beta_ridder` (β) - **DM coupling** - typically 0

The initial field value is: `φ₀ = f × θᵢ`

**Note:** The paper's `a_c` (critical scale factor) and `f_EDE` (EDE fraction) are **emergent properties** computed by CLASS, not direct inputs. The timing is implicitly controlled by Λ and f.

## Verification

When running correctly, logs should show:
```
DEBUG: Ridder field ENABLED. Lambda = 1.000000e+00
RIDDER SWITCHING: z_osc = XXXX.XX, a_osc = X.XXXXXXe-XX
```

If Lambda = 0 or Ridder messages don't appear, the EDE is disabled!

## Contact

This fix was identified and implemented on 2025-11-30.
The issue affected all Tier 5/9/10 EDE results prior to this date.
