# Diagnostic Results: Peak Redshift Investigation

**Date:** November 24, 2025  
**Status:** Physics issue identified - field behaves as late dark energy

---

## Tests Performed

### Test 1: Baseline (Original narrow window)
```ini
ridder_zc_min = 500.0
ridder_zc_max = 10000.0
theta_i = 1.5
f_axion = 2.435e27 eV (M_Pl)
c_slow = 1.0
```
**Result:** Lambda = 4.85×10¹³ eV, f_peak = 0.098, **z_peak = 500.0** (at boundary!)

---

### Test 2: Widened window, baseline c_slow
```ini
ridder_zc_min = 10.0     ← Widened to see lower z
ridder_zc_max = 20000.0
theta_i = 1.5
f_axion = 2.435e27 eV
c_slow = 1.0
```
**Result:** Lambda = 2.70×10¹² eV, f_peak = 0.102, **z_peak = 10.0** (NEW boundary!)

**Finding:** Peak moved from z=500 → z=10 when floor dropped. Peak wants to be at **z < 10**.

---

### Test 3: Increased c_slow (try to push onset earlier)
```ini
ridder_zc_min = 10.0
ridder_zc_max = 20000.0
theta_i = 1.5
f_axion = 2.435e27 eV
c_slow = 3.0            ← 3x larger initial velocity
```
**Result:** Lambda = 2.70×10¹² eV, f_peak = 0.102, **z_peak = 10.0** (UNCHANGED!)

**Finding:** c_slow has **NO effect** on peak redshift. Not the right knob.

---

### Test 4: Decreased f (try to increase m_eff)
```ini
ridder_zc_min = 10.0
ridder_zc_max = 20000.0
theta_i = 1.5
f_axion = 1.0e20 eV     ← 7 orders of magnitude smaller!
c_slow = 3.0
```
**Result:** Lambda = 2.70×10¹² eV, f_peak = 0.102, **z_peak = 10.0** (UNCHANGED!)

**Finding:** Changing f by 10⁷ had **NO effect**. Lambda identical.

---

## Physics Interpretation

### What This Means

**The field is behaving as LATE dark energy, not Early Dark Energy:**

1. **Peak wants to be at z << 10** (possibly z ~ 1-5, or even z=0)
2. **Neither c_slow nor f** are moving the peak redshift
3. **Lambda adjusts** to maintain f_EDE = 10%, but the TIMING is wrong

### Why This Happens

For the cosine-monodromy potential `V = Λ⁴ [1-cos(φ/f)]³`:

**Effective mass:** m_eff ~ V'' ~ Λ²/f

**For field to roll at redshift z:**
```
m_eff ~ H(z)

Λ²/f ~ H₀ √(Ω_m (1+z)³ + Ω_Λ)
```

**Current parameters:**
- Λ ~ 2.7×10¹² eV (from shooter)
- f ~ 2.4×10²⁷ eV (M_Pl) or 10²⁰ eV (test)
- m_eff ~ (2.7×10¹²)² / f ~ 3×10⁻³ eV (for f=M_Pl) or 7×10⁴ eV (for f=10²⁰)

**Compare to H:**
- H(z=3000) ~ 10⁻²⁰ eV (in eV units, after conversion)
- H(z=10) ~ 10⁻²⁴ eV
- H(z=0) ~ 10⁻³³ eV

**Problem:** Even with f=10²⁰, m_eff ~ 10⁴ eV is STILL enormous compared to H in eV units. This doesn't make sense...

---

## Hypothesis: Unit Conversion Issue?

**Suspicion:** The slow-roll ICs might have a unit mismatch.

Current slow-roll formula in code:
```c
phi'_ini = - c_slow * a_ini * (dV/dφ) / (3 H_ini)
```

Where:
- dV/dφ is in eV³ (from potential)
- H is in Mpc⁻¹ (CLASS units)
- phi' should be in eV/Mpc (conformal time derivative)

**If units are mismatched**, the initial velocity could be way too small, causing the field to freeze and only roll at very late times when H drops enough.

---

## Alternative Hypothesis: Potential Shape Issue

The cosine potential [1-cos(θ)]³ might intrinsically give late-rolling behavior for θ ~ π/2 (where we're scanning).

**Potential features:**
- Minimum at θ = 0
- Maximum (hilltop) at θ = π
- Inflection at θ ~ π/2

For θ_i = 1.5 ≈ 0.48π, we're close to the inflection point where V'' is small, leading to very gradual rolling.

---

## Recommended Next Steps

### Option A: Check Slow-Roll IC Units (Most Likely)
Audit the unit conversions in `background_initial_conditions`:
```c
phi'_ini = - c_slow * a_ini * dV_dphi / (3.0 * H_ini);
```

**Questions:**
1. Is dV_dphi in the right units (should be eV³ → eV/Mpc after conversion)?
2. Is H_ini in Mpc⁻¹?
3. Is the factor of `a_ini` correct for conformal time derivatives?

### Option B: Try Different θ_i Range
Test θ_i much closer to minimum or maximum:
- θ_i = 0.5 (near minimum, steeper V'')
- θ_i = 2.8 (near hilltop, but risky - V'' < 0)

### Option C: Switch Potential Form
Try a simpler potential that's known to work for EDE:
- Pure quadratic: V = ½ m² φ²
- Pure cosine: V = Λ⁴ [1-cos(φ/f)] (n=1, not n=3)

### Option D: Disable Slow-Roll ICs Temporarily
Set phi'_ini = 0 manually (old behavior) and see if timing changes. This would confirm whether slow-roll ICs are the issue.

---

## Summary

**What works:**
- ✅ Shooter converges reliably
- ✅ Achieves target f_EDE = 10%
- ✅ Lambda scales sensibly with parameters

**What doesn't work:**
- ✗ Peak occurs at z < 10 (late dark energy, not EDE)
- ✗ Changing c_slow has no effect
- ✗ Changing f by 10⁷ has no effect
- ✗ θ_i scan showed all peaks at z=500 (window artifact)

**Root cause:** Almost certainly a **unit conversion or IC scaling issue** in the slow-roll formula, causing the field to start with far too little kinetic energy and remain frozen until very late times.

---

**Recommended action:** Debug slow-roll ICs before continuing physics scans.

