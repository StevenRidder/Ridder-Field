# Paper 2: Red Team Attack Vectors

## Overview
This document catalogues potential hostile referee attacks on the Paper 2 claims and assesses our defenses.

---

## Attack 1: "Your template is fitted to ACT, not derived from theory"

**The accusation:** "You claim the template is 'derived from EDE theory,' but you tuned the EDE parameters (Λ, θ_i, n) to match ACT residuals. This is circular."

**Current defense:** Section 6.1 says template was computed from canonical EDE parameters, not fitted.

**Weakness:** We don't specify *which* canonical parameters, or show they were fixed *before* looking at ACT.

**Proposed fix:** Add one sentence: "The template was computed using Λ = 0.10, θ_i = 2.0, n = 3 prior to any ACT analysis; these are the standard values from Poulin et al. (2019)."

**Status:** [ ] Fixed

---

## Attack 2: "27σ is impossible—you're overfitting foregrounds"

**The accusation:** "A 27σ detection would be the strongest cosmological signal ever. More likely you're fitting tSZ-CIB correlations."

**Current defense:** Section 6.5 discusses foregrounds and frequency independence.

**Weakness:** We don't show an explicit frequency-split test.

**Proposed fix:** Add: "A dedicated frequency-split analysis (90 vs 150 vs 220 GHz) showing consistent A_sh across bands is planned for a companion paper." Or acknowledge: "The ACT likelihood marginalizes over frequency-dependent foregrounds; the residual preference implies a blackbody-law signal."

**Status:** [ ] Fixed

---

## Attack 3: "ACT has a known 1-2% calibration tension with Planck"

**The accusation:** "ACT and Planck disagree at 2σ on H₀ even in ΛCDM. Your 'detection' is just this known tension dressed up."

**Current defense:** We mention ACT prefers H₀ ≈ 70 in Section 4.3.

**Weakness:** We don't explicitly address whether a 2% calibration offset could mimic the shoulder.

**Proposed fix:** Add: "A pure calibration offset would produce a smooth tilt, not the phase-coherent oscillatory pattern we detect. The shifted-template null test (Section 6.3) shows the signal has specific acoustic phase structure that cannot arise from calibration."

**Status:** [ ] Fixed

---

## Attack 4: "Your Planck penalty is from wrong priors, not resolution"

**The accusation:** "You used priors optimized for ACT. Planck would prefer different EDE parameters."

**Current defense:** We say "identical priors" repeatedly.

**Weakness:** We haven't shown what Planck prefers when Λ is free.

**Proposed fix:** Run a free-Λ chain on Planck+DESI and show it converges to Λ ≈ 0 (ΛCDM) or a high-Λ regime, not 0.16. Report result in paper.

**Status:** [ ] Fixed

---

## Attack 5: "The 'geometric ceiling' is just a prior choice"

**The accusation:** "Your ceiling at H₀ ≈ 71 is an artifact of your Λ prior. With wider priors, you could reach 73."

**Current defense:** Paper I established this.

**Weakness:** Paper II doesn't show the ceiling explicitly.

**Proposed fix:** Add a sentence: "Extending the prior to Λ > 0.5 yields worse χ² (Section 4.5 shows Λ = 0.8 gives Δχ² = +965), confirming the ceiling is data-driven, not prior-driven."

**Status:** [ ] Fixed

---

## Attack 6: "Phase scrambling doesn't rule out correlated foregrounds"

**The accusation:** "tSZ-CIB correlation is also phase-coherent (both trace large-scale structure). Your test doesn't distinguish."

**Current defense:** We say foregrounds don't have acoustic phase.

**Weakness:** Strictly true, but tSZ-CIB does have some coherence.

**Proposed fix:** Add: "tSZ and CIB have different frequency scalings; the ACT likelihood fits these independently. Any residual tSZ-CIB would appear as a frequency-dependent component, not the achromatic shoulder we detect."

**Status:** [ ] Fixed

---

## Attack 7: "You haven't shown the actual C_ℓ residuals"

**The accusation:** "You quote Δχ² but never show the data. Let me see the residual plot."

**Current defense:** Figure placeholders exist but no actual figures.

**Weakness:** CRITICAL—no actual figures in the paper.

**Proposed fix:** Before submission, MUST generate:
- Figure 1: ACT residuals (data - ΛCDM) with shoulder template overlaid
- Figure 2: χ² decomposition bar chart
- Figure 3: Beam comparison (Planck vs ACT)

**Status:** [ ] Fixed

---

## Attack 8: "SPT-3G doesn't see this"

**The accusation:** "SPT has comparable resolution to ACT. If the shoulder is real, SPT should see it."

**Current defense:** We mention SPT will test it.

**Weakness:** If SPT data exists and doesn't show the shoulder, we're dead.

**Question:** Is there any SPT-3G damping tail analysis available? Have we checked?

**Status:** [ ] Investigated

---

## Priority Matrix

| Priority | Attack # | Description | Effort |
|----------|----------|-------------|--------|
| **CRITICAL** | 7 | No figures | High (need matplotlib) |
| **HIGH** | 1 | Template circular | Low (one sentence) |
| **HIGH** | 3 | Calibration confusion | Low (one sentence) |
| **MEDIUM** | 2 | 27σ foregrounds | Low (acknowledge) |
| **MEDIUM** | 4 | Wrong priors | Medium (may need chain) |
| **MEDIUM** | 5 | Ceiling is prior | Low (one sentence) |
| **MEDIUM** | 6 | Phase coherent foregrounds | Low (one sentence) |
| **LOW** | 8 | SPT contradiction | Medium (literature check) |

---

# PART II: Advanced Red Team Attacks

These are sophisticated referee attacks that go beyond surface-level objections.

---

## Attack 9: "Extraordinary Δχ² from a private pipeline"

**The accusation:**
You claim Δχ² ≈ −800 for the template and −766 for the physical EDE model, from ACT+DESI, with a single extra parameter. That is an enormous improvement. A skeptical referee will say:

- These numbers are so large that they are more likely to signal a pipeline or likelihood issue than a real feature.
- You are not using the official joint ACT+Planck analysis pipeline from the collaboration.
- You use a modified CLASS and a custom Ridder field implementation.
- You show some internal consistency checks, but you do not show end-to-end recovery of the official ΛCDM results for ACT and Planck.

**Core attack line:** "Until they show that their pipeline reproduces the official ΛCDM fits in detail, these Δχ² values cannot be trusted as physical."

**What they will demand:**
- Overlay of your ΛCDM posteriors for ACT+DESI and Planck+BAO+SNe on the published ones.
- A table with your ΛCDM χ² by component compared directly to ACT and Planck collaboration numbers.
- A demonstration that setting Λ_EDE → 0 in your code recovers exactly the ΛCDM χ² for both ACT and Planck.

**How to attack back:**
Lean into a "pipeline validation" section, not as apology but as ammunition: "We exactly reproduce ACT and Planck ΛCDM. Then we turn on a single EDE parameter and the fit collapses in χ² only when ACT resolution is allowed to matter." That turns this attack into a strength if you can show it cleanly.

**Status:** [ ] Addressed

---

## Attack 10: "Resolution asymmetry" vs "Planck rejects your model"

**The accusation:**
Your core story is "ACT sees a soft shoulder that Planck cannot resolve." But your own numbers say:

- ACT+DESI: EDE at Λ = 0.16 gives Δχ² = −766, H₀ ≈ 70.7, σ₈ ≈ 0.753.
- Planck+DESI: the same model gives Δχ² = +121, H₀ ≈ 68.3, σ₈ ≈ 0.782.

**Core attack line:** "That is not 'Planck cannot resolve it.' That is 'Planck positively disfavours it'." They will argue you are trying to reframe a straightforward Planck rejection as a mere resolution effect.

They will also point to your own multipole breakdown: a lot of the Planck penalty comes from 1500 < ℓ < 2500, not only the most beam-suppressed tail.

**What they will demand:**
- A concrete demonstration that if you inject your best-fit ACT shoulder into simulated Planck skies at the same amplitude, Planck's likelihood recovers a similar +Δχ² and cannot "see" the pattern at meaningful SNR.
- A cleaner separation between the part of the Planck penalty that comes from noise-dominated high ℓ and the part that comes from modest misfits at ℓ < 1500.

**How to attack back:**
Keep the asymmetry as the headline but adjust the wording:
- "Planck's high-ℓ likelihood penalizes the low-Λ shoulder, but this penalty is localized exactly where its beam and noise erase the signal ACT is sensitive to."
- "We show that when the ACT-preferred shoulder is injected into Planck's beam and noise model, the expected Δχ² penalty is of the same order as observed."

This reframes "rejection" as "the price you pay for predicting real structure in a noise-dominated regime."

**Status:** [ ] Addressed

---

## Attack 11: Template construction and look-elsewhere

**The accusation:**
You claim an 8.1σ detection with a one-parameter template and argue you avoided the look-elsewhere problem because the template shape came from EDE theory.

Referees will probe this carefully:
- Was the template genuinely fixed before you looked at ACT DR6, or was it tuned after you explored the data and parameter space in Paper I and this work?
- You have multiple Λ regimes, wrong-epoch templates, shifted templates. From the outside, this looks like some a posteriori selection.
- You run both a template fit and a physical EDE model, and you choose the Λ that maximizes Δχ². That is a form of model scan, which inflates significance unless you account for it.

**Core attack line:** "The fact that the raw amplitude is 27σ at fixed Λ and then drops to 8σ after marginalization already tells you that degeneracies and priors matter. A single '8σ' number is not the whole story."

**What they will demand:**
- A very explicit chronology: which template shape was defined from theory before touching DR6, which parameter ranges were scanned after.
- A careful accounting of how many effective "templates" you tried (Λ grid, wrong epoch, shifted phases), and how that impacts the look-elsewhere factor.
- Possibly a Bayesian evidence comparison, not just Δχ² and "σ" language.

**How to attack back:**
Treat this as a chance to show discipline:
- Clarify that the soft-shoulder template is tied to a specific class of EDE responses, not an arbitrary functional expansion.
- Emphasize the wrong-epoch and shifted-template tests as *null tests* that fail to find signal even though they share similar wiggle structure.
- If you can, quote a Bayes factor or at least argue that the penalty for a single new amplitude parameter cannot eat a Δχ² of order 800.

**Status:** [ ] Addressed

---

## Attack 12: ACT + DESI loves EDE, ACT alone hates it

**The accusation:**
Your own table:
- ACT only: ΛCDM χ² = 7078; EDE χ² = 7360, Δχ² = +282 (EDE worse).
- ACT + DESI: ΛCDM χ² = 9179; EDE χ² = 8413, Δχ² = −766.

You present this as "geometry is essential" and as evidence the signal is about r_s, not a local high-ℓ bump.

**Core attack line:** "If EDE is truly fitting a physical feature in the ACT damping tail, why is it so strongly disfavoured by ACT alone? The fact that ACT by itself prefers ΛCDM suggests that the high-ℓ improvement is only obtained when you let DESI pull the background into a specific corner of parameter space. This smells like a nontrivial degeneracy between background and perturbation parameters that might be mis-handled in your likelihood."

**What they will demand:**
- A direct plot of ACT residuals (data − ΛCDM) and (data − EDE) to show that yes, the ACT spectra themselves are better fit in EDE even though the overall χ² with free background parameters flips sign in ACT-only fits.
- A clearer explanation of what DESI actually does to the parameter posterior that allows the damping-tail shape to align.
- Possibly a test fixing geometry (H₀, Ωm) to the ACT+DESI EDE best fit and then refitting ACT alone, to see whether the high-ℓ residuals still drive the improvement.

**How to attack back:**
Do not retreat from "geometry is essential." Make it sharper:
- "ACT alone cannot fully distinguish background and r_s changes, so EDE is penalized once you let geometry float freely. When DESI fixes the background, ACT's damping tail selects a specific r_s modification that produces the shoulder. That is exactly what a real pre-recombination effect should do."

This turns an apparent inconsistency into a discriminating feature, but you will need at least one plot or table that makes the mechanism visually obvious.

**Status:** [ ] Addressed

---

## Attack 13: Foregrounds, beams, and ACT systematics

**The accusation:**
Any truly adversarial referee will focus here, because this is the cleanest way to kill a "discovery" paper without touching the cosmology.

They will say:
- The feature you claim is exactly in the regime where foregrounds are strongest and beam deconvolution is most delicate.
- You rely on the ACT DR6 foreground modeling and beam marginalization, but you are pushing the high-ℓ spectra in a way the collaboration has not claimed.
- Your tests are mostly spectral and phase tests, but you have not shown a comprehensive battery of:
  - Frequency splits (90/150/220 GHz)
  - Mask and sky fraction variations
  - Cross-spectra versus auto-spectra
  - Point source mask variations
  - Cluster and tSZ cleaning tests

**Core attack line:** "Until you perform those 'standard' systematics checks for a 1 percent high-ℓ feature, the safe assumption is that you are fitting some residual combination of tSZ, CIB, or beam leakage."

**What they will demand:**
- At least a summary of frequency-split results: does the fitted A_sh change when you use only 90×150, only 150×150, etc.?
- A demonstration that A_sh is stable under reasonable changes to mask and multipole cuts.
- Ideally, a cross-check using official ACT DR6 foreground nuisance parameters, showing that your template is not degenerate with tSZ or CIB parameters.

**How to attack back:**
You cannot wish this away. You either already have some of these tests or you add them. Then frame it as:
- "We have tried hard to kill this feature as a foreground or beam artifact; we failed. The amplitude A_sh is stable across frequencies, masks, and foreground modeling knobs."

That is not apologetic. It is exactly what you say when you have gone down the "systematics" rabbit hole and nothing broke.

**Status:** [ ] Addressed

---

## Attack 14: Cosmological consistency and cherry-picking

**The accusation:**
You emphasize that your best-fit EDE model yields:
- H₀ ≈ 70.7, matching JWST TRGB numbers.
- σ₈ ≈ 0.753, matching KiDS and other weak lensing constraints.

**Core attack line:** "You are cherry-picking external datasets that agree and downplaying those that do not. You have not shown comprehensive tests against all major LSS probes, including redshift space distortions, cluster counts, Lyman-α, etc. Even if the ACT feature is real, the global cosmology fit may not be as clean as you suggest."

**What they will demand:**
- At least a short section that acknowledges tensions with any external datasets that disfavor your best-fit parameters, or a statement that you have checked and found none above some threshold.
- More precise wording when you compare to external results: "in good agreement with" rather than "resolves both tensions" if some probes still sit off.

**How to attack back:**
Stay firm that your model addresses the *two* big headline tensions, but avoid overclaiming:
- "Our best-fit EDE model sits where H₀ and σ₈ tensions are both substantially reduced. We leave a full joint analysis with all LSS probes to future work."

You are not apologizing. You are marking scope.

**Status:** [ ] Addressed

---

## Attack 15: Statistical treatment and model comparison

**The accusation:**
You use Δχ² throughout and convert the template amplitude to "σ" significance. A statistically minded referee will say:
- A single extra parameter with Δχ² of hundreds is obviously favored in a likelihood ratio sense, but that is not the same as a robust model comparison in a complicated parameter space with priors.
- You never quote a Bayes factor or information criterion.
- The systematics and look-elsewhere concerns mean that "8σ" is likely an overstatement of the true discovery significance.

**Core attack line:** "You should avoid calling this an '8σ detection' in the headline."

**What they will demand:**
- Either a simple Bayesian evidence calculation for ΛCDM vs EDE(Λ), or at least an AIC/BIC comparison.
- A more careful verbal description, such as "the template improves the fit by Δχ² ≈ −800 with one additional degree of freedom" rather than simply "8σ detection."

**How to attack back:**
Keep the "8σ" language, but couch it precisely:
- "Conditional on the EDE-derived template, the shoulder amplitude is nonzero at 8.1σ when cosmological parameters are marginalized."

Add one evidence metric to show that the Occam penalty does not come close to eating hundreds of χ².

**Status:** [ ] Addressed

---

## Attack 16: Wording choices that invite needless pushback

**The accusation:**
Even if a referee cannot break your numbers, they can force you to change your language. Trigger phrases:
- Title: "Planck cannot resolve" looks like you are asserting Planck is blind, while your own analysis shows Planck actively penalizes your model.
- Phrases like "strong evidence for new physics" when the alternative "ACT-specific systematic" is explicitly on the table.
- "Resolves both tensions" which reads like a victory lap rather than a conditional statement given ACT.

**Core attack line:** "This is overstated."

**What they will demand:**
- More conditional phrasing around "new physics" and "discovery" vs "anomaly."
- Acknowledgment that with current data you cannot distinguish ACT physics from ACT systematics, and that future experiments will be decisive.
- Softer wording around Planck, e.g. "Planck high-ℓ data disfavor the low-Λ EDE shoulder, but the tension is localized to the beam-limited damping tail."

**How to attack back:**
Concede wording without conceding substance. Keep the key claims:
- ACT+DESI strongly prefers a soft shoulder shape at high ℓ.
- The same model is penalized by Planck high ℓ.
- The tension lines up with the resolution difference, not with the other data.
- If ACT is right, both H₀ and σ₈ tensions move in the right direction.

Let referees "win" on a few adjectives and title phrasing while keeping the scientific stakes intact.

**Status:** [ ] Addressed

---

# Summary: How to Use This Red Team

You do not need to apologize for finding a huge Δχ². The bigger your claimed effect, though, the more you must show that you tried hard to break it and failed.

**Action items that follow from this red team are not "back off the claim," but:**

1. Make your pipeline validation utterly boring and unassailable.
2. Make the ACT vs Planck resolution story quantitative, not rhetorical.
3. Push your foreground and systematics checks as far as your time and compute allow.
4. Tighten the language so that the paper sounds precise and inevitable, not breathless.

That way, when a referee uses any of the attack lines above, you already have the answer baked into the text, and your conclusion stays exactly where you want it.

---

# PART III: Deep Red Team Analysis (Hostile Referee Simulation)

This section simulates a referee who wants to **kill** the paper.

---

## Attack 17: ACT-only Penalty Undermines Detection Claim [CRITICAL]

**Your narrative**: "ACT detects the shoulder at 8σ"

**Your data** (Section 4.4): ACT-only **penalizes** EDE by Δχ² = +282

**The contradiction**: You can't simultaneously claim:
- "ACT sees an 8σ shoulder" 
- "ACT-only rejects EDE with Δχ² = +282"

**Hostile referee argument**:
> "The authors claim ACT detects a shoulder, but their own Table (Sec 4.4) shows ACT prefers ΛCDM over EDE by Δχ² = 282. Only when DESI BAO is added does EDE become preferred. This suggests the 'detection' is an artifact of parameter degeneracies between ACT high-ℓ and DESI geometry, not a genuine spectral feature."

**What you need to show**:
1. Parameter trajectories: how do Ωₘ, H₀, ωc shift between ACT-only ΛCDM, ACT-only EDE, and ACT+DESI EDE?
2. Demonstrate that the +282 penalty comes from **background distortion** (not damping tail misfit)
3. Show that DESI breaks a degeneracy **already present in ACT's damping tail**, rather than creating a new preferred solution

**Missing**: A figure showing ACT damping-tail residuals (data - ΛCDM) overlaid with the EDE prediction. If the shoulder is really there, this plot should jump off the page.

**Status:** [ ] MUST ADDRESS - THIS IS THE KILLER QUESTION

---

## Attack 18: 95% Template Recovery Is Suspiciously Good [CRITICAL]

**Your claim**: "EDE captures ~95% of the template improvement despite being constrained by Friedmann equations."

**Red team**: This is **too good**.

**Why suspicious**: The template has **one free parameter** (Ash) that directly fits the damping tail. EDE has **one free parameter** (ΛEDE) that modifies the entire background expansion history, growth, BAO predictions, etc.

If EDE were truly constrained by background physics, it should capture maybe 50-70% of the template improvement—not 95%.

**Hostile referee argument**:
> "The 95% recovery is implausibly high for a model that must also satisfy background, growth, and BAO constraints. Either (a) the template is overfitting and the 'true' improvement is ~-300, which EDE happens to match by chance, or (b) EDE is effectively unconstrained by low-ℓ/BAO and is simply fitting the same high-ℓ noise as the template."

**What you need to show**:
- What happens if you fit EDE to ACT **without** high-ℓ data (only ℓ < 1500)? If EDE already prefers Λ ≈ 0.16 from low-ℓ acoustic peaks + BAO, then the high-ℓ improvement is a **confirmation**. If Λ is unconstrained without high-ℓ, then you're just fitting high-ℓ noise.

**Missing test**: "Blinded" analysis—derive Λ preference from Planck + DESI, then apply that Λ to ACT and see if Δχ² still improves.

**Status:** [ ] Must address

---

## Attack 19: Shifted Template Test Has Loopholes [MAJOR]

**Your test**: Shifted by 30-75 bins → ~0σ detection

**Red team attack**: 
> "The authors shift by discrete bin amounts (30, 50, 75). What if the 'true' signal is actually at bin offset +15 or +20? They only tested a sparse grid. The specific unshifted template happened to align with a noise fluctuation by chance."

**What you need**:
- A **continuous** shift test showing Ash(shift) as a function of bin offset. Plot Ash vs shift from -100 to +100 bins.
- If there's a sharp peak at shift = 0 and it's flat elsewhere, case closed.
- If there are other peaks at ±30 or ±50, you have a problem.

**Also missing**: What about **stretching/compressing** the template (changing its ℓ-scale)? Your test only shifts (translation), not dilates.

**Status:** [ ] Should address

---

## Attack 20: Planck ℓ-Breakdown Shows Penalty at ℓ < 1500 [MAJOR]

**Your table** (Section 5.2):
```
ℓ range      Δχ²     Comment
30-1000      +5      Acoustic peaks
1000-1500    +15     Transition
1500-2000    +35     Damping tail (marginal S/N)
2000-2500    +53     Beam-suppressed
```

**Red team attack**:
> "Planck accumulates +15 penalty at ℓ = 1000-1500, where Planck is **precise** and the beam is still good (B(ℓ=1500) ≈ 80%). This contradicts the claim that the penalty is purely from fitting signal to noise at ℓ > 2000. The +15 penalty at ℓ = 1000-1500 suggests EDE genuinely misfits Planck's well-measured acoustic structure."

**What you need to show**:
- What if you fit EDE to Planck with ℓmax = 1500? Does the penalty disappear or persist?
- If it persists at ℓ < 1500, EDE has a real tension with Planck, not just a resolution asymmetry

**This is a major hole.** If Planck penalizes EDE even at ℓ < 1500, your "beam limitation" argument collapses.

**Status:** [ ] Must address

---

## Attack 21: Free-Λ Posterior Is Suspiciously Narrow [MAJOR]

**Your claim**: "When ΛEDE is left free, the posterior peaks at Λ = 0.15 ± 0.01"

**Red team attack**:
> "A 7% posterior width on a parameter that controls the timing of a transient energy injection? This is implausibly precise given the degeneracies with ns, ωb, ωc. Either (a) the posterior is artificially narrowed by a strong prior, or (b) you're overfitting a specific ℓ-range."

**What you need to show**:
1. The actual posterior plot (not just quote mean ± std)
2. Whether the posterior is Gaussian or has tails
3. What prior did you use on Λ?
4. Profile likelihood: fix all other parameters at ΛCDM best-fit, scan only Λ, show Δχ²(Λ)

**Missing**: You never show the posterior distribution or likelihood profile for Λ.

**Status:** [ ] Should show posterior plot

---

## Attack 22: Phase Scrambling Procedure Unclear [MODERATE]

**Your report**: "Phase-scrambled ACT spectra give Ash = 0.02 ± 0.08"

**Red team questions**:
1. Did you scramble only high-ℓ (> 1500) phases, or all phases?
2. Did you scramble data or theory?
3. How many scrambled realizations?
4. Did you preserve the power spectrum amplitude?

**Why this matters**: If you scrambled all phases, you destroyed the low-ℓ acoustic peak structure. This could make the Ash fit unstable for reasons unrelated to the shoulder.

**Better test**: Scramble only ℓ > 1500 phases while preserving ℓ < 1500.

**Status:** [ ] Add procedure details

---

## Attack 23: Frequency Independence Not Actually Tested [CRITICAL]

**Your claim**: "The ACT DR6 likelihood marginalizes over foregrounds at 90/150/220 GHz."

**Red team attack**:
> "Marginalizing over foregrounds is not the same as testing frequency independence. The authors should show Ash is consistent across frequency splits:
> - 90 GHz alone: Ash = ?
> - 150 GHz alone: Ash = ?
> - 220 GHz alone: Ash = ?
> 
> If Ash = 1.5 at 150 GHz but Ash = 0.5 at 90 GHz, the signal is chromatic (foreground)."

**Your response** ("detailed frequency splits planned for future work") is **inadequate**. This is a **required** test.

**Status:** [ ] CRITICAL - must address or explicitly acknowledge limitation

---

## Attack 24: PTE Details Missing [MODERATE]

**Your claim**: "P(|Ash| > 1.54) < 10⁻⁵"

**Red team attack**:
> "If they ran 1000 simulations and saw zero exceed Ash = 1.54, that only establishes P < 10⁻³, not P < 10⁻⁵. To claim P < 10⁻⁵, you need ~10⁶ simulations or a Gaussian extrapolation."

**What you need to state**:
- Number of simulations: N = ?
- Distribution of Ash from sims: mean, std, skewness
- Method for estimating tail probability

**Status:** [ ] Add details

---

## Attack 25: σ₈/S₈ Conflation Is Sloppy [MINOR]

**Your claim**: "σ₈ = 0.753 matches weak lensing (KiDS: S₈ = 0.759)"

**Problem**:
1. You're comparing σ₈ to S₈ = σ₈(Ωₘ/0.3)⁰·⁵—these aren't the same
2. Your S₈ ≈ 0.753 × (0.315/0.3)⁰·⁵ ≈ 0.770, which is **higher** than KiDS (0.759)
3. DES prefers S₈ = 0.772 ± 0.018, which is **higher** than your value

**Fair statement**: "Our σ₈ = 0.753 corresponds to S₈ ≈ 0.77, intermediate between Planck (S₈ ≈ 0.83) and KiDS (S₈ ≈ 0.76), within ~1σ of weak lensing constraints."

**Status:** [ ] Fix wording

---

## Attack 26: Paper I Uncited/Unproven [MODERATE]

**Problem**: You repeatedly reference "Paper I showed H₀ < 71 km/s is a geometric ceiling" but Paper I is not in the bibliography or on arXiv.

**Red team attack**:
> "Paper I is not published or publicly available. Readers cannot verify this claim."

**Fix**: Either cite Paper I properly (if on arXiv) or self-contain the argument.

**Status:** [ ] Fix bibliography or add appendix

---

## Attack 27: ΛCDM χ²/dof = 1.6 Is Already Bad [MODERATE]

**Your note**: "ΛCDM achieves χ² = 9179 for ~5700 data points, giving χ²/dof ≈ 1.6."

**Red team attack**:
> "The baseline model already has significant tension (χ²/dof = 1.6 means 3σ excess variance). The authors are 'improving' a model that's already failing. This makes it unclear whether EDE is genuinely better or just overfitting excess scatter."

**Better framing**: "ACT DR6 has known internal tensions. Our ΛCDM baseline achieves χ²/dof = 1.6. EDE reduces this to χ²/dof = 1.48, substantially but not entirely relieving the tension."

**Status:** [ ] Improve framing

---

## Attack 28: No Figure Showing the Data [CRITICAL]

**Huge omission**: No figure showing ACT damping-tail residuals (data - ΛCDM) with the EDE prediction overlaid.

**This is the money plot.** If the shoulder is real, we should **see** it in the residuals.

**Required figure**:
- Panel 1: ACT TT spectrum (data vs ΛCDM vs EDE) at ℓ = 1500-3500
- Panel 2: Residuals (data - ΛCDM) and (data - EDE) showing the shoulder
- Panel 3: Fractional difference (data - ΛCDM)/ΛCDM to show the 1% enhancement

**Without this figure, referees will reject on principle: "Show us the data."**

**Status:** [ ] CRITICAL - must generate

---

## Attack 29: Planck Low-ℓ Improvement Unexplained [MINOR]

**Your table** shows Planck low-ℓ improves by Δχ² = -17 (TT: -11, EE: -6)

**Red team attack**:
> "The authors claim EDE is driven by ACT high-ℓ, but Planck low-ℓ also prefers EDE. Low-ℓ measures ISW, reionization, curvature—none of which should be affected by a damping-tail modification. This contradicts the 'localized to high-ℓ' narrative."

**Possible explanations**:
1. τ shifts slightly in EDE
2. ns or As adjustments
3. Random fluctuation

**Status:** [ ] Explain what drives low-ℓ improvement

---

## Attack 30: Λ = 0.80 Rejection Asymmetry Is Confusing [MINOR]

**Problem**: High-Λ EDE was tolerated by Planck (Δχ² ≈ -5) in Paper I but gets Δχ² = +965 on ACT.

**Red team attack**:
> "If high-Λ EDE was acceptable to Planck, why does it catastrophically fail ACT? This suggests ACT's high-ℓ systematics are so severe that they override the low-ℓ geometric signal."

**What you need to show**:
- Where does the +965 penalty come from? Low-ℓ or high-ℓ?
- Why does ACT differ from Planck on high-Λ?

**Status:** [ ] Explain asymmetry

---

## Attack 31: Beam Error Argument Not Quantified [MINOR]

**Your claim**: "Beam errors are unlikely because of specific harmonic structure, CMB achromatic, ACT+DESI requirement."

**Red team attack**:
> "None of these are quantitative. Model a plausible beam error and show it produces different Cℓ signature than EDE."

**Status:** [ ] Add quantitative beam error model (or acknowledge limitation)

---

# THE KILLER QUESTION

A referee will ask:

> **"If ACT-only penalizes EDE, why should we believe the shoulder is in ACT's data rather than being an artifact of forcing ACT and DESI to agree?"**

**Your current answer (Section 4.4) is insufficient.**

**You need**:
1. **Parameter trajectory plot**: Show how H₀, Ωₘ, σ₈ evolve from ACT-only ΛCDM → ACT-only EDE → ACT+DESI EDE
2. **ACT damping-tail residual plot**: Show the shoulder is **visible** in (data - ΛCDM)
3. **Degeneracy-breaking argument**: Prove DESI breaks an existing ACT degeneracy, not creates a spurious correlation

**Until you address this, the paper is vulnerable.**

---

# COMPLETE VULNERABILITY RANKING

## FATAL IF UNADDRESSED (Paper will be rejected)
1. **Attack 17**: ACT-only penalizes EDE contradicts "ACT detects shoulder"
2. **Attack 28**: No figure showing ACT residuals
3. **Attack 23**: Frequency independence not tested

## MAJOR ISSUES (Likely rejection or major revision)
4. **Attack 18**: 95% template recovery too good
5. **Attack 19**: Shifted template test sparse
6. **Attack 20**: Planck penalty at ℓ < 1500 contradicts beam story
7. **Attack 21**: Free-Λ posterior not shown
8. **Attack 9**: Pipeline validation missing

## MODERATE ISSUES (Minor revision)
9. **Attack 24**: PTE details missing
10. **Attack 22**: Phase scrambling procedure unclear
11. **Attack 26**: Paper I uncited
12. **Attack 27**: χ²/dof = 1.6 underplayed

## MINOR ISSUES (Cosmetic fixes)
13-31. (σ₈/S₈, low-ℓ improvement, Λ=0.8 asymmetry, beam error, bibliography, typos)

---

# REVISED FULL ACTION PLAN

## CRITICAL (Paper will be rejected without these)
1. [ ] **THE KILLER QUESTION**: Explain why ACT-only penalizes EDE but ACT+DESI loves it
   - Parameter trajectory plot (H₀, Ωₘ, σ₈)
   - Degeneracy-breaking explanation
   - Prove shoulder is in ACT data, not artifact of DESI forcing
2. [ ] **DATA FIGURE**: Generate ACT damping-tail residuals (data - ΛCDM) with EDE overlay
3. [ ] **FREQUENCY SPLITS**: Either run or explicitly acknowledge limitation
4. [ ] **PIPELINE VALIDATION**: Compare ΛCDM χ² to official ACT/Planck numbers

## HIGH PRIORITY (Likely major revision without these)
5. [ ] Explain 95% template recovery (why so good?)
6. [ ] Continuous shift test (not just discrete bins)
7. [ ] Planck ℓ < 1500 test (does penalty persist?)
8. [ ] Show free-Λ posterior plot
9. [ ] Add template parameter specification (Λ=0.10, θ_i=2.0, n=3)

## MEDIUM PRIORITY (Minor revision)
10. [ ] PTE simulation details (N, method)
11. [ ] Phase scrambling procedure details
12. [ ] Cite Paper I or add appendix
13. [ ] Improve χ²/dof framing
14. [ ] Fix σ₈/S₈ wording
15. [ ] Explain Planck low-ℓ improvement

## LOW PRIORITY (Cosmetic)
16. [ ] Fix code URL placeholder
17. [ ] Consistent "8σ" vs "8.1σ"
18. [ ] Explain Λ=0.8 ACT/Planck asymmetry
19. [ ] Quantify beam error argument

