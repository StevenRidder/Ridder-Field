# Stress Test Plan: Breaking the Ridder Field Implementation

## Objective
Find every hole, weakness, and potential failure mode in the current implementation.

## Test Categories

### 1. PARAMETER SPACE EXTREMES
Test what happens at boundary conditions:

#### Test 1.1: Lambda → 0 (No EDE)
- **Expected**: Should reduce to ΛCDM
- **Risk**: Division by zero in potential functions
- **Status**: NEEDS TESTING

#### Test 1.2: Lambda → ∞ (Extreme EDE)
- **Expected**: Should crash or give unphysical results
- **Risk**: Overflow in V(φ) = Λ⁴
- **Status**: NEEDS TESTING

#### Test 1.3: f_axion → 0 (Narrow well)
- **Expected**: Oscillations at very high frequency
- **Risk**: Fluid approximation may break
- **Status**: NEEDS TESTING

#### Test 1.4: f_axion → ∞ (Wide well)
- **Expected**: No oscillations, field rolls slowly
- **Risk**: May never switch to fluid mode
- **Status**: NEEDS TESTING

#### Test 1.5: theta_i = 0 (No initial displacement)
- **Expected**: Field sits at minimum, no EDE
- **Risk**: Should work but needs verification
- **Status**: NEEDS TESTING

#### Test 1.6: theta_i = π (Maximum displacement)
- **Expected**: Maximum EDE effect
- **Risk**: May overshoot and cause negative densities
- **Status**: NEEDS TESTING

#### Test 1.7: beta = 0 (No DM coupling)
- **Expected**: Pure EDE, no growth effects
- **Risk**: Should work, needs verification
- **Status**: NEEDS TESTING

#### Test 1.8: beta → ∞ (Strong DM coupling)
- **Expected**: Unphysical, should crash
- **Risk**: Negative DM masses possible
- **Status**: NEEDS TESTING

### 2. NUMERICAL STABILITY
Test edge cases in integration:

#### Test 2.1: Very small k (superhorizon modes)
- **Expected**: Should match analytical predictions
- **Risk**: Division by k² in fluid equations
- **Status**: NEEDS TESTING

#### Test 2.2: Very large k (subhorizon modes)
- **Expected**: Should oscillate and damp
- **Risk**: Aliasing or numerical artifacts
- **Status**: NEEDS TESTING

#### Test 2.3: Switching surface timing
- **What if**: a_osc = 0 (never switches)?
- **What if**: a_osc = 1 (switches at z=0)?
- **Risk**: Uninitialized variables, division by zero
- **Status**: NEEDS TESTING

#### Test 2.4: w_eff edge cases
- **What if**: w_eff = -1 (cosmological constant)?
- **What if**: w_eff = 1 (stiff matter)?
- **Risk**: Division by (1+w) in fluid equations
- **Status**: NEEDS TESTING

### 3. PHYSICAL CONSISTENCY
Test conservation laws and physical constraints:

#### Test 3.1: Energy Conservation
- **Check**: ∑ρᵢ = const * a⁻⁴ (radiation) + a⁻³ (matter) + const (Λ)
- **Method**: Plot total energy density vs scale factor
- **Risk**: Leaking energy at switching surface
- **Status**: NEEDS TESTING

#### Test 3.2: Momentum Conservation
- **Check**: ∑(ρᵢ+pᵢ)θᵢ should evolve correctly
- **Method**: Check Einstein constraint equations
- **Risk**: Discontinuity in θ at switching
- **Status**: NEEDS TESTING

#### Test 3.3: Gauge Invariance
- **Check**: Results shouldn't depend on gauge choice
- **Method**: Run in synchronous vs Newtonian gauge
- **Risk**: Coupling terms may be gauge-dependent
- **Status**: **CRITICAL - We forced Newtonian gauge!**

#### Test 3.4: Initial Conditions Consistency
- **Check**: Adiabatic ICs should match radiation
- **Method**: Compare δ_ridder(z_ini) with δ_γ(z_ini)
- **Risk**: Mismatch could cause transients
- **Status**: NEEDS TESTING

### 4. COMPARISON WITH LITERATURE
Test against known EDE results:

#### Test 4.1: Reproduce Poulin et al. (2019)
- **Their result**: f_EDE ~ 10-12% at z ~ 3500
- **Our result**: Need to compute f_EDE(z)
- **Risk**: Our mechanism may be different
- **Status**: NEEDS TESTING

#### Test 4.2: Reproduce Smith et al. (2020)
- **Their result**: Δr_s ~ 5-7% for viable models
- **Our result**: 14.1% (may be too large!)
- **Risk**: **CONFIRMED ISSUE** - We overshoot
- **Status**: **NEEDS PARAMETER TUNING**

#### Test 4.3: Growth suppression amplitude
- **Expected**: ~5-10% suppression in P(k)
- **Method**: Compute P(k) ratio
- **Risk**: Our β coupling may give wrong amplitude
- **Status**: NEEDS TESTING

### 5. CODE CORRECTNESS
Test for implementation bugs:

#### Test 5.1: Unit Conversions
- **Check**: All eV ↔ Mpc conversions consistent
- **Method**: Dimensional analysis of every term
- **Risk**: Factor of 2π, h, or c errors
- **Status**: **PARTIALLY CHECKED** - needs full audit

#### Test 5.2: Index Bounds
- **Check**: No array out-of-bounds access
- **Method**: Run with valgrind or address sanitizer
- **Risk**: Segfault in production
- **Status**: NEEDS TESTING

#### Test 5.3: Uninitialized Variables
- **Check**: All variables initialized before use
- **Method**: Compile with -Wuninitialized
- **Risk**: Random values causing non-determinism
- **Status**: NEEDS TESTING

#### Test 5.4: Floating Point Exceptions
- **Check**: No NaN, Inf, or division by zero
- **Method**: Enable FPE traps
- **Risk**: Silent failures
- **Status**: NEEDS TESTING

### 6. STRESS TESTS
Push the code to breaking point:

#### Test 6.1: Long Integration Times
- **Method**: Run from z=10⁹ to z=0
- **Risk**: Accumulation of numerical errors
- **Status**: NEEDS TESTING

#### Test 6.2: High Precision Requirements
- **Method**: Set tolerance to 10⁻¹⁵
- **Risk**: May never converge
- **Status**: NEEDS TESTING

#### Test 6.3: Many k-modes
- **Method**: Compute C_l up to l=10000
- **Risk**: Memory overflow or slow performance
- **Status**: NEEDS TESTING

#### Test 6.4: Parallel Execution
- **Method**: Run with OpenMP on 32 cores
- **Risk**: Race conditions in shared variables
- **Status**: NEEDS TESTING

### 7. PHYSICAL PLAUSIBILITY
Test if results make physical sense:

#### Test 7.1: Causality
- **Check**: No superluminal propagation (c_s² ≤ 1)
- **Method**: Check sound speed in fluid mode
- **Risk**: We set c_s² = 0, should be safe
- **Status**: **PROBABLY OK** but needs verification

#### Test 7.2: Positivity
- **Check**: ρ > 0, ρ+p > 0 always
- **Method**: Monitor densities throughout evolution
- **Risk**: Negative densities → ghost instabilities
- **Status**: NEEDS TESTING

#### Test 7.3: Equation of State Bounds
- **Check**: -1 ≤ w ≤ 1 (for stable fluids)
- **Method**: Check w_eff = 0.5 is in bounds
- **Risk**: w > 1 → gradient instabilities
- **Status**: **OK** (w=0.5 is safe)

#### Test 7.4: Hubble Parameter
- **Check**: H > 0 always
- **Method**: Monitor H(z) throughout evolution
- **Risk**: H < 0 → time runs backwards!
- **Status**: NEEDS TESTING


