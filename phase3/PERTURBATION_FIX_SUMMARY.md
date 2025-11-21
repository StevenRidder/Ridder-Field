# Perturbation Crash: Root Cause Analysis

## Status
**Background**: ✅ WORKING (14% $r_s$ reduction achieved)  
**Perturbations**: ❌ CRASHING ("Step size too small" at $\tau \sim 65-207$ Mpc, $z \sim 1500-100$)

## Root Cause
The Ridder field switches to fluid mode at **z_osc = 5304** ($a = 1.88 \times 10^{-4}$, $\tau \sim 50$ Mpc).  
The perturbation integrator starts at $\tau \sim 10-15$ Mpc and crashes at $\tau \sim 65$ Mpc, which is **after** the switching point.

This means:
1. The field is already oscillating when perturbations start
2. The fluid approximation is active in background
3. But perturbations are still using field equations (Klein-Gordon) which are stiff

## Attempted Fixes
1. ✅ Unit conversions for $V''$ and $V'$ in perturbations
2. ✅ Adiabatic initial conditions when starting in fluid mode
3. ✅ Smooth transition using `tanh` → Still crashes
4. ⚠️ Hard switch to fluid equations → Not yet tested

## Next Step
Replace smooth transition with **hard switch** matching background logic:
- If `a > a_osc_ridder`: use fluid equations
- Else: use Klein-Gordon

The crash interval `[65:207]` Mpc is entirely in the fluid regime, so the integrator should never see the stiff field equations.

## Hypothesis
The smooth transition (`tanh` blend) creates artificial stiffness because it mixes two fundamentally different equation types. A clean, discontinuous switch (like background uses) should work because:
1. Variables are reinterpreted at the boundary (field → fluid)
2. Initial conditions already account for this
3. Background proves this works

## Implementation
File: `perturbations.c`, line ~9535  
Replace lines 9537-9582 (smooth transition block) with simple `if/else` based on `a > pba->a_osc_ridder`.

