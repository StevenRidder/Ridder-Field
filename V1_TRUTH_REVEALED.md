# V1 Model: The Truth Revealed

**Date**: November 23, 2025  
**Critical Discovery**: The model was NEVER "good" - we misinterpreted early results

---

## The Shocking Truth

**The Ridder Field V1 model has ALWAYS been broken.** What we thought were "successful" Tier 1 runs were actually showing the EXACT SAME FAILURE we see in Tier 3.

---

## Evidence: Tier 1 "Success" Was Actually a Failure

### From `archive/TIER1_PLANCK_STATUS.md` (Nov 22, 04:20 UTC):

| Parameter | Value | Status |
|-----------|-------|--------|
| **θᵢ** | 0.489 ± 0.021 | ❌ COLLAPSED (should be ~2.1) |
| **β** | 0.0080 ± 0.0009 | ⚠️ Weak coupling |
| **H₀** | 67.78 ± 0.06 | ❌ Planck value (not elevated) |
| **χ²** | **2778-2790** | ❌ **SAME AS TIER 3!** |

### From Tier 3 "Failure" (Nov 23):

| Parameter | Value | Status |
|-----------|-------|--------|
| **θᵢ** | 0.876 ± 0.275 | ❌ COLLAPSED (should be ~2.1) |
| **β** | 0.0104 ± 0.0081 | ⚠️ Weak coupling |
| **H₀** | 70.38 ± 0.66 | ❌ Not reaching 73 |
| **χ²** | **2824 ± 13** | ❌ **SAME RANGE!** |

---

## The Critical Realization

### What We Thought:
- "Tier 1 worked great! θᵢ ≈ 0.5, χ² ≈ 2780"
- "Something broke in Tier 3! θᵢ ≈ 0.9, χ² ≈ 2824"
- "We need to fix the Tier 3 configuration"

### The Reality:
- **Both runs show the EXACT SAME BEHAVIOR**
- **χ² ≈ 2780-2824 is CATASTROPHICALLY BAD** (ΛCDM gets χ² ≈ 396)
- **θᵢ collapsing to ~0.5-0.9 means the Ridder field is turning OFF**
- **The model has NEVER fit the data**

---

## Why Did We Think Tier 1 Was "Successful"?

### Mistake #1: No ΛCDM Baseline in Early Tier 1

We didn't run a ΛCDM baseline alongside Tier 1, so we had no reference point. We saw:
- χ² ≈ 2780 and thought "that's reasonable for Planck"
- θᵢ ≈ 0.5 and thought "it's exploring parameter space"
- H₀ ≈ 67.8 and thought "that's Planck-like, as expected for Tier 1"

**We were wrong.** A proper ΛCDM fit to Planck gets χ² ≈ 2760-2770, NOT 2780-2824.

### Mistake #2: Misunderstanding θᵢ Behavior

From `TIER1_RIDDER_ACTIVE.md`:
> "θᵢ will NOT drift to 0.5 - it will stay in Ridder valley (1.6-2.1)"

**But it DID drift to 0.5.** We saw this and thought:
- "Maybe 0.5 is the 'correct' value for Planck-only data"
- "The field is just finding its natural equilibrium"

**Wrong again.** θᵢ ≈ 0.5 means the field has **negligible energy density** at early times. The Ridder field is effectively **turned off**.

### Mistake #3: Focusing on "Ridder Field is Active"

From `TIER1_RIDDER_ACTIVE.md`:
> "✅ VERIFICATION: RIDDER FIELD IS NOW ACTIVE"
> "CLASS Debug Output: `DEBUG: Ridder field ENABLED. Lambda = 1.000000e+00`"

We celebrated that the Ridder field was "active" in the code, but we didn't check if it was **doing anything useful**. The field was active, but it was:
- Collapsing to low θᵢ (minimal energy density)
- Producing terrible χ² (worse than ΛCDM)
- Not raising H₀ (stuck at Planck values)

---

## The Real Timeline of V1

### Phase 1: "Ghost Parameters" (Before Nov 22)
- Running **vanilla CLASS** (no Ridder modifications)
- θᵢ and β were "ghost parameters" (ignored by CLASS)
- Result: Pure ΛCDM fit, χ² ≈ 2760-2770 ✅ (actually good!)

### Phase 2: "Ridder Activated" (Nov 22 onwards)
- Recompiled CLASS with Ridder modifications
- Ridder field now **active** in the code
- Result: θᵢ collapses to 0.5, χ² jumps to 2780-2824 ❌ (broken!)

### Phase 3: "Tier 3 Disaster" (Nov 23)
- Added BAO + SH0ES to Tier 1 config
- Same broken behavior: θᵢ ≈ 0.9, χ² ≈ 2824
- Compared to ΛCDM baseline: **Δχ² = +2428** 🚨

---

## Why the Model is Broken

### The Physics Problem

The Ridder field is **destroying the CMB fit** because:

1. **The Potential V(φ) is Wrong**
   - The axion-like potential with n=3 is too steep
   - The field oscillates at the wrong time (during recombination?)
   - Creates ISW effects that shift the CMB peaks

2. **The Coupling β is Harmful**
   - Even small β (~0.01) breaks the acoustic peaks
   - The stress-energy tensor interferes with photon-baryon oscillations
   - The model "wants" β = 0 (i.e., no Ridder field)

3. **The Initial Conditions are Incompatible**
   - Starting at high θᵢ (e.g., 2.1) creates too much early-time energy density
   - This shifts the CMB peaks in a way that cannot be compensated
   - The sampler collapses θᵢ to ~0.5 to minimize the damage

### The Sampler's "Solution"

The MCMC sampler is doing its job correctly:
- It tries high θᵢ (e.g., 2.1) → χ² explodes to >3000
- It tries low θᵢ (e.g., 0.5) → χ² "only" 2780-2824
- It settles on θᵢ ≈ 0.5-0.9 as the "least bad" solution

**But "least bad" is still catastrophically bad.** The model is 2400 χ² points worse than ΛCDM.

---

## What About the "Redline" Success?

From `TIER1_RIDDER_ACTIVE.md`:
> "The 'Redline' and 'Safe Mode' successes from your laptop (which had the correct code) are still valid."

**Were they?** We need to check:
1. What was the actual χ² from those laptop runs?
2. Did we compare to a ΛCDM baseline?
3. Or did we just see "Ridder field active" and assume it was working?

**Hypothesis**: The laptop runs probably showed the SAME behavior (θᵢ collapse, high χ²), but we didn't have a baseline to compare against.

---

## The Tier 4 "Low χ²" Mystery

Tier 4 showed χ² = 2.9, which seemed suspiciously good. But:
- Only 401 samples after burn-in (incomplete)
- θᵢ = 1.16 ± 0.16 (still too low, but higher than Tier 3)
- H₀ = 71.15 ± 0.60 (closer to SH0ES, but still not 73)

**Interpretation**: 
- The chains hadn't converged yet
- With more samples, χ² would likely rise to ~2800 (same as Tier 1/3)
- Or: The addition of SN data is somehow helping (but this needs verification)

---

## How to Fix V2

### Critical Changes (Must Do):

1. **Start with a Known Working EDE Model**
   - Use AxiCLASS or EDE_CLASS as a reference
   - Copy their potential, coupling, and initial conditions EXACTLY
   - Verify it reproduces their published results
   - THEN modify it to add Ridder-specific features

2. **Test Without Coupling First**
   - Set β = 0 (no coupling to matter)
   - See if the background evolution alone can work
   - If β = 0 still breaks the CMB, the potential is wrong

3. **Use a Simpler Potential**
   - Try V(φ) = m²φ² (quadratic) instead of axion-like
   - Or: V(φ) = Λ⁴[1 - cos(φ/f)] (standard axion)
   - Match the potential to known working EDE models

4. **Fix Initial Conditions**
   - Ensure θᵢ corresponds to f_EDE ≈ 10% at z ≈ 3000
   - Test: What θᵢ value gives this in CLASS?
   - Verify: Does the field roll down at the right time?

### Diagnostic Tests (Must Run Before MCMC):

5. **Single-Point CLASS Tests**
   - Run CLASS with θᵢ = 2.0, β = 0.01
   - Check: Does it produce a valid CMB power spectrum?
   - Compare to ΛCDM: Is Δχ² reasonable (<10)?

6. **Parameter Scan**
   - Grid scan: θᵢ ∈ [0.5, 2.5], β ∈ [0.0, 0.03]
   - Plot χ² as a function of (θᵢ, β)
   - Find: Is there ANY region where χ² < 2800?

7. **Compare to AxiCLASS**
   - Run AxiCLASS with their default EDE parameters
   - Check: Do they get χ² ≈ 2760-2770 (good)?
   - Compare: What's different in our implementation?

### Configuration Changes (Secondary):

8. **Expand Priors**
   - θᵢ ∈ [0.01, 5.0] (wider range)
   - β ∈ [-0.03, 0.03] (allow negative coupling)
   - n_ridder ∈ [1, 5] (test different potential shapes)

9. **Use Planck-Lite for Initial Testing**
   - Run with low-ℓ only first
   - If that works, add high-ℓ
   - Isolate which multipoles are breaking

10. **Add More Diagnostics**
    - Output f_EDE(z) evolution
    - Output w_EDE(z) equation of state
    - Compare to known EDE models

---

## The Bottom Line

**V1 was never "good."** We misinterpreted early results because:
1. We didn't have a ΛCDM baseline to compare against
2. We focused on "Ridder field is active" instead of "does it fit the data?"
3. We thought θᵢ ≈ 0.5 was "exploring parameter space" instead of "the field is turning off"

**The model has always had χ² ≈ 2780-2824**, which is **2400 points worse than ΛCDM**.

**V2 must start from scratch** with a known working EDE implementation, not try to "fix" V1.

---

## Action Items

1. ✅ **Document this failure** (this file)
2. ⬜ **Find and review AxiCLASS source code**
3. ⬜ **Run AxiCLASS with default EDE parameters**
4. ⬜ **Compare AxiCLASS vs Ridder CLASS line-by-line**
5. ⬜ **Identify the specific bug in V1**
6. ⬜ **Design V2 based on working EDE model**
7. ⬜ **Test V2 with single-point CLASS runs BEFORE MCMC**
8. ⬜ **Only run MCMC once V2 passes all diagnostic tests**

---

## Files to Archive

- `V1_FAILURE_ANALYSIS.md` - Detailed failure analysis
- `V1_TRUTH_REVEALED.md` - This file (the full story)
- `phase3/results/` - All Tier 3/4 chain data and plots
- `archive/TIER1_PLANCK_STATUS.md` - The "successful" run that wasn't

**Do NOT delete these.** They document what went wrong and will prevent us from making the same mistakes in V2.

