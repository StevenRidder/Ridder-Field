# Walk-Back Pattern Fixes

## Problem Summary
The paper still has moments where we say something strong and then immediately undercut it. 
This gives referees the "discovery claim then retreat" feeling from Paper 1.

---

## Fix 1: Abstract (lines 63-67)
**Current (walk-back pattern):**
> "...but we do not use this model as a primary fit function and we do not claim that it is 
> favored once Planck high-ℓ data are included."

**Fix:** Replace with:
> "The same model is strongly disfavored when Planck high-ℓ data replace ACT, so we treat 
> this mapping as a diagnostic example rather than as evidence for that specific model. 
> Our primary result is the measurement of A_sh and the ACT–Planck asymmetry, which 
> upcoming high-resolution CMB experiments can test with independent data."

**Rationale:** States what the data show, not what we "do not claim".

---

## Fix 2: EDE Result Section (line 626)
**Current (claim then undercut):**
> "achieving both the best χ² and simultaneous resolution of the H₀ and σ₈ tensions"

**Fix:** Replace with:
> "it gives the best χ² and shifts H₀ and σ₈ toward the values preferred by late-time probes"

**Rationale:** Neutral description of what the fit does, not a claim about "resolving tensions".

---

## Fix 3: Discussion Opening - Compress Conditional Language
**Current:** "Conditional" appears 12 times across Discussion, including:
- Section title: "Discussion: Conditional Interpretation"
- Subsection: "Conditional implications for H₀ and σ₈"
- Subsection: "Derived parameters (conditional)"
- Subsection: "Conditional: The Λ = 0.16 parameter space"
- Plus repeated "conditional interpretation" phrases

**Fix:** 
1. Add ONE clear disclaimer at the start of Discussion
2. Remove "(conditional)" from subsection titles
3. Remove repeated "conditional interpretation" phrases in body text

**New Discussion opening:**
> "The core result of this paper is observational: ACT DR6 prefers a nonzero A_sh while 
> Planck prefers A_sh ≈ 0. In this section we explore what that measurement implies within 
> one concrete early-time model. These parameter-level numbers are illustrative: the same 
> EDE model is disfavored when Planck high-ℓ data replace ACT, so the mapping should not 
> be read as a global solution."

---

## Fix 4: Robustness Section - FALSE "We have not done X" (line 1543)
**Current (FALSE STATEMENT):**
> "We have not performed a dedicated frequency-split analysis in which the shoulder 
> amplitude A_sh is fitted independently to each frequency channel"

**Reality:** We HAVE a frequency-split table with 90/150/220 GHz results!

**Fix:** DELETE this entire "Explicit limitation" paragraph - it is a lie.

---

## Fix 5: "We cannot definitively distinguish" (line 1143)
**Current:**
> "We cannot definitively distinguish these interpretations with current data."

**Fix:** Replace with:
> "Current data admit both interpretations; SPT-3G and Simons Observatory will 
> distinguish them by repeating the same template test with independent systematics."

---

## Fix 6: "We do not claim the penalty is entirely explained" (line 1166)
**Current:**
> "We do not claim the penalty is entirely explained by noise-fitting, but ~60% arises..."

**Fix:** Replace with:
> "The penalty is not entirely explained by noise-fitting, but ~60% arises..."

---

## Fix 7: Conclusions - Remove "we do not adopt" language
**Current:**
> "Mapping A_sh onto a concrete early-time model inevitably brings in additional 
> assumptions and tension with Planck; we have shown how one such model projects 
> onto H₀ and σ₈, but we do not adopt it as a global solution."

**Fix:** Replace with three clean statements:
> "We have measured a specific, theory-predicted damping-tail pattern in ACT DR6 and 
> parameterized it with a single amplitude A_sh. ACT prefers A_sh = 1.54 ± 0.19, while 
> Planck prefers A_sh ≈ 0 and penalizes the ACT-preferred value. This tension is 
> concentrated in the beam-suppressed regime of the Planck spectra. A concrete early-time 
> model can reproduce the ACT signal and move H₀ and σ₈ toward late-time probes, but 
> fails when Planck high-ℓ data replace ACT. We therefore present the EDE mapping as 
> an example, and leave it to SPT-3G, Simons Observatory, and CMB-S4 to decide whether 
> the ACT damping-tail pattern is cosmological or experiment-specific."

---

## General Rule
Replace every instance of:
- "We do not claim that..." → "The data show that..."
- "We cannot definitively say..." → "Current data admit X; future data will decide Y"
- "We have not done X" → Either DO IT or move to a single "Future work" paragraph

---

## Status
- [x] Fix 1: Abstract - DONE
- [x] Fix 2: EDE Result "simultaneous resolution" - DONE
- [x] Fix 3: Discussion conditional compression - DONE
- [x] Fix 4: DELETE false "we have not done frequency-split" - DONE (was a lie!)
- [x] Fix 5: "We cannot definitively distinguish" - DONE
- [x] Fix 6: "We do not claim the penalty" - DONE
- [x] Fix 7: Conclusions rewrite - DONE

## All fixes implemented 2024-12-10

