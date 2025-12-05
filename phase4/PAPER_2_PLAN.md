# Paper 2: Full Marginalized ACT Analysis

## The Core Question

**Paper 1 showed a "civil war" in the data:**

| Dataset | χ² change with EDE | Interpretation |
|---------|-------------------|----------------|
| ACT DR6 | **−12** (prefers EDE) | Sees the damping-tail shoulder |
| Planck High-L | **+19** (penalizes EDE) | Doesn't see it |

**Both measure ℓ > 1000. They can't both be right.**

Paper 2 has **one job**: resolve the Planck High-ℓ vs. ACT conflict that Paper 1 exposed but couldn't explain.

---

## The Three Possible Stories

### Story 1: "ACT is Right, Planck High-ℓ Has Issues"

**What Run D would show:**
- Without Planck High-ℓ: H₀ → 72-73, A_sh stays ~1.0, Δχ² improves significantly
- The "ceiling" disappears or shifts to H₀ ~ 73

**Paper 2 claim:**
> "The geometric ceiling was an artifact of Planck High-ℓ systematics. ACT independently confirms the EDE damping-tail signature, allowing H₀ to reach the SH0ES value. The Planck vs ACT discrepancy in the damping tail is the real bottleneck."

**Importance:** This would be **MAJOR** — it means EDE can actually solve the Hubble tension to H₀ ~ 73, and identifies a specific data conflict that CMB-S4 must resolve.

---

### Story 2: "Planck is Right, ACT Saw Noise"

**What Run D would show:**
- Without Planck High-ℓ: H₀ stays ~70-71 (ceiling persists)
- A_sh drops significantly when marginalized
- The ACT "preference" was just parameter degeneracies

**Paper 2 claim:**
> "The geometric ceiling is robust. ACT's apparent preference for EDE was a conditional artifact. When properly marginalized, both datasets agree: early-time modifications can't push H₀ above ~71."

**Importance:** This **strengthens Paper 1** — the ceiling is real physics, not a dataset choice.

---

### Story 3: "They're Both Right — Different ℓ Sensitivity"

**What Run D would show:**
- Moderate changes: H₀ → 71-72 (ceiling softens but doesn't break)
- A_sh stays significant but lower (~0.6-0.8)
- The signal is narrower in ℓ-space than expected

**Paper 2 claim:**
> "Planck and ACT are sensitive to slightly different features. The EDE signature has ℓ-dependent structure that ACT captures better. The ceiling softens to H₀ ~ 72, and the resolution requires CMB-S4's continuous ℓ coverage."

**Importance:** Middle ground — updates Paper 1's ceiling, frames CMB-S4 as critical.

---

## The Decision Table

| If H₀ goes to... | And A_sh... | Then... |
|------------------|-------------|---------|
| **~73** | Stays ~1.0 | **Story 1**: ACT is right, Planck High-ℓ wrong |
| **~70-71** | Drops to <0.5 | **Story 2**: Planck is right, ACT noise |
| **~71-72** | Stays ~0.7-0.9 | **Story 3**: Both partially right |

---

## Why This Doesn't "Blow Up" Paper 1

Paper 1's central claims are **conditional**:
- "**With Planck + BAO + DESI**, there's a ceiling at H₀ ~ 71"
- "ACT shows preliminary conditional evidence for the damping-tail signature"

These are **true statements** regardless of Run D's outcome.

Paper 2 answers: **"Where does that ceiling come from — the EDE physics or the Planck data?"**

| If the ceiling... | Paper 1 is... | Because... |
|-------------------|---------------|------------|
| Persists (Story 2) | **Validated** | It's fundamental physics |
| Breaks (Story 1) | **Deepened** | You've identified the dataset creating the constraint |

Story 1 is arguably **more important** because it:
1. Shows EDE can reach H₀ ~ 73 (solves the tension fully)
2. Identifies Planck High-ℓ as having potential issues
3. Makes CMB-S4 a decisive test

---

## Draft Abstracts (Depending on Outcome)

### If Story 1 (Ceiling Breaks):
> "We show that the H₀ ~ 71 'geometric ceiling' reported in Paper 1 arises from tension between Planck High-ℓ and ACT DR6 in the damping tail, not from intrinsic EDE constraints. When analyzed with ACT + Planck Low-ℓ alone, EDE naturally reaches H₀ = 72.8 ± 0.6 km/s/Mpc with Δχ² = −8, consistent with SH0ES. The damping-tail signature persists at A_sh = 1.02 ± 0.15 when properly marginalized. This identifies the Planck vs ACT discrepancy as the limiting factor for early-time H₀ solutions and establishes CMB-S4 as the definitive arbiter."

### If Story 2 (Ceiling Holds):
> "We confirm that the H₀ ~ 71 geometric ceiling is robust to dataset choice. Removing Planck High-ℓ and analyzing ACT + Planck Low-ℓ alone yields H₀ = 70.4 ± 0.8 km/s/Mpc, confirming that early-time sound-horizon modifications cannot reach the SH0ES value of H₀ ~ 73. The ACT damping-tail correlation weakens under full marginalization (A_sh = 0.42 ± 0.22), indicating the conditional evidence in Paper 1 was parameter-dependent. This establishes fundamental limits on early-time solutions to the Hubble tension."

---

## Roadmap (Your Routing Guide)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PAPER 2 DECISION TREE                        │
└─────────────────────────────────────────────────────────────────┘

Step 1: Run C (Planck-only control) ← CURRENTLY RUNNING
        ↓
        Get: H₀, ωcdm, A_sh baseline WITHOUT ACT
        ↓
Step 2: Run A (Add ACT to EDE model)
        ↓
        Compare: Does H₀ shift? Does A_sh increase?
        ↓
        ┌──────────────────┬──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   A_sh > 3σ          A_sh ~ 2σ          A_sh < 1σ
   (ACT wins)         (Uncertain)        (Planck wins)
        │                  │                  │
        ▼                  ▼                  ▼
   "Shoulder is      "Need CMB-S4"      "Paper 1 ACT
    real, Planck                         claim was
    has systematics"                     overstated"

Step 3: Run B (Template-only, model-agnostic check)
        ↓
        If A_sh > 0 in pure ΛCDM: Feature is real
        If A_sh ~ 0 in pure ΛCDM: Feature is EDE-specific
```

---

## Current Status

| Run | Config | Status | Purpose |
|-----|--------|--------|---------|
| C | `run_control_planck_only.yaml` | 🟢 Running | Baseline EDE without ACT |
| A | `run_a_ede_marginalized.yaml` | ⏳ Pending | Full EDE with ACT (main result) |
| B | `run_b_lcdm_template.yaml` | ⏳ Pending | ΛCDM + A_sh template (model-agnostic) |
| **D** | `run_d_kill_switch.yaml` | ⏳ **CRITICAL** | **ACT + Planck Low-L + BAO (NO Planck High-L)** |

---

## The "Kill Switch" Run (Run D)

> **Referee's Key Test**: Drop Planck High-L entirely and see if the ceiling shatters.

### The Hypothesis

The geometric ceiling at H₀ ~ 71 exists because Planck High-L's χ² penalty (+19) blocks higher values. If we remove Planck High-L:

```
Before (with Planck High-L):    H₀ ceiling ~ 71
After (without Planck High-L):  H₀ could reach 72-73 ???
```

### Run D Configuration

```yaml
# run_d_kill_switch.yaml
# THE CRITICAL TEST: What happens without Planck High-L?

likelihood:
  # Planck LOW-L ONLY (no High-L!)
  planck_2018_lowl.TT:
  planck_2018_lowl.EE:
  # NO planck_2018_highl_plik.TTTEEE!
  
  # ACT DR6 (this becomes the damping-tail anchor)
  act_dr6_mflike:
  
  # BAO
  bao.sixdf_2011_bao:
  bao.sdss_dr7_mgs:
  bao.sdss_dr12_consensus_bao:
  likelihoods.desi_y1_bao.DESI_Y1_BAO:
  
  # Supernovae
  sn.pantheonplus:
```

### What We're Testing

| If Run D shows... | Interpretation |
|-------------------|----------------|
| H₀ ~ 71 (same as Run A) | Ceiling is model-dependent, not dataset-dependent |
| H₀ ~ 72-73 | **Ceiling SHATTERS** - Planck High-L was the constraint! |
| H₀ ~ 69-70 | ACT alone doesn't push H₀ up much |

### Why This Matters

**If the ceiling moves when Planck High-L is dropped:**
- The "geometric ceiling" is actually a "Planck High-L ceiling"
- ACT and Planck are fighting over the damping tail
- This is a **major result** about dataset tensions, not just EDE

### Visualization: The Ceiling as Curve Intersection

```
χ²
 │
 │    Planck High-L          ACT + SH0ES
 │        curve                curve
 │          │                    │
 │          │\                  /│
 │          │ \                / │
 │          │  \    ____      /  │
 │          │   \__/    \____/   │
 │          │      "Ceiling"     │
 │          │        ↓           │
 └──────────┼────────┼───────────┼──────── H₀
           67       71          73

The "ceiling" at 71 is where Planck High-L becomes too expensive.
Remove Planck High-L → ceiling vanishes → minimum shifts right.
```

### Monitoring Commands
```bash
# Quick status
./quick_status.sh

# Detailed analysis (once samples exist)
python3 show_chain_stats.py

# Watch logs
tail -f chains/*.log
```

---

## The Planck vs ACT Tension

### Why This Matters

The geometric ceiling at H₀ ~ 71 exists **because we trust Planck High-L**.

If Paper 2 shows:
- ACT strongly prefers the shoulder (A_sh > 3σ)
- AND Planck High-L continues to penalize it

Then we face a choice:
1. **Trust Planck**: The ACT signal is a noise fluctuation
2. **Trust ACT**: Planck High-L has calibration/beam systematics at ℓ > 1500

### What Each Run Tests

| Run | Question Answered |
|-----|-------------------|
| C (Planck-only) | Where does EDE land without ACT's input? |
| A (Planck+ACT) | Does ACT pull the posterior toward the shoulder? |
| B (Template-only) | Is the feature real even without committing to EDE physics? |

---

## How These Runs Support Paper 2

### Run C (Control) → Table 1, Baseline
- **Purpose**: Establish EDE parameter values **without** ACT data
- **Key outputs**: H₀, S₈, Λ_EDE, r_s from Planck+BAO+DESI only
- **Paper use**: Shows where EDE parameters land before ACT enters

### Run A (Main Result) → Core Claim
- **Purpose**: Full marginalized A_sh significance **with** ACT
- **Key outputs**: 
  - A_sh (derived from EDE model)
  - σ(A_sh) after marginalizing over cosmology + EDE
  - Shift in H₀, S₈ when ACT is included
- **Paper use**: The central result: "A_sh = X ± Y (Zσ) after full marginalization"

### Run B (Model-Agnostic) → Robustness Check
- **Purpose**: Does ACT see "something shoulder-like" even without EDE?
- **Key outputs**: A_sh as free parameter in ΛCDM
- **Paper use**: If A_sh > 0 even in ΛCDM, the feature is real (not EDE-dependent)

---

## What We're Testing

| Hypothesis | How Run A Tests It | How Run B Tests It |
|------------|-------------------|-------------------|
| "The 6.4σ survives marginalization" | Measure σ(A_sh) with all params free | N/A |
| "ACT prefers a shoulder" | Compare χ² with/without A_sh | A_sh > 0 in ΛCDM? |
| "EDE parameters shift with ACT" | Compare Run A to Run C | N/A |
| "The feature is model-independent" | N/A | A_sh value in ΛCDM |

---

## Expected Outcomes

### Optimistic (Strong Paper)
- Run A: A_sh = 1.0 ± 0.25 (4σ)
- Run B: A_sh = 0.8 ± 0.3 (confirming feature exists)
- Claim: "Marginalized significance remains >3σ; feature is robust"

### Neutral (Still Publishable)
- Run A: A_sh = 0.8 ± 0.4 (2σ)
- Run B: A_sh = 0.5 ± 0.4
- Claim: "Significance reduces as expected; CMB-S4 needed for confirmation"

### Negative (Important Result)
- Run A: A_sh = 0.3 ± 0.4 (<1σ)
- Run B: A_sh = 0.0 ± 0.3
- Claim: "Conditional 6.4σ was a look-elsewhere artifact; updating Paper 1"

---

## Kill-Shot Purpose

> **Goal of Paper 2**  
> Quantify the *fully marginalized* significance of the Geometric EDE damping-tail shoulder in ACT DR6, and check whether it is consistent across data combinations.

This paper answers the referee's obvious question:

> "What happens to the ACT shoulder when you marginalize over everything?"

---

## Working Title

> *The CMB Damping-Tail Shoulder after Marginalization: ACT DR6 Constraints on Geometric Early Dark Energy*

## Core Claim

> "After marginalizing over cosmological, EDE, and ACT nuisance parameters, we find a nonzero shoulder amplitude at Xσ, consistent with the Geometric EDE prediction from Ridder (2025)."

**Note**: No need to re-argue H₀ and S₈. Just reference the PRD paper.

---

## Scope

### In Scope
- Planck 2018 TTTEEE + low-ℓ TT/EE
- ACT DR6 TT+TE+EE with official mflike likelihood
- DESI Y1 BAO (optional, as consistency check)
- Same Geometric EDE model as PRD paper
- A_sh treated two ways:
  1. As a **derived** quantity from the EDE model
  2. As a **pure template amplitude** in a phenomenological run

### Out of Scope
- No new DES, S₈, or H₀ stress tests
- No new monodromy or UV theory work
- No SPT or CMB-S4 forecasts

Point back to Paper 1 for geometry. Leave SPT/CMB-S4 for later papers.

---

## Section Outline

### 1. Introduction

**Paragraph 1**: Remind reader of H₀/S₈ context and Geometric EDE from PRD paper.

**Paragraph 2**: Summarize the soft shoulder prediction and conditional 6.4σ ACT detection in Paper 1.

**Paragraph 3**: State the problem:
> "In this work we perform a fully marginalized analysis of the damping-tail shoulder in ACT DR6, allowing cosmological parameters, EDE parameters, and ACT nuisance parameters to vary, and quantify the robustness of the shoulder amplitude."

**Paragraph 4**: Three questions we answer:
1. Is A_sh still nonzero after full marginalization?
2. How stable is A_sh across data combinations (Planck+ACT vs Planck+ACT+DESI)?
3. Does allowing A_sh to float push background parameters in a problematic way?

---

### 2. Method

#### 2.1 Model and Template
- Brief recap of Geometric EDE and origin of the shoulder template
- Explicit definition of A_sh (normalization, ℓ-range, sign)

#### 2.2 Likelihoods and Data Combinations

| Likelihood | Details |
|------------|---------|
| Planck 2018 | plik_lite TTTEEE, commander low-ℓ TT, simall low-ℓ EE |
| ACT DR6 | mflike TT+TE+EE, ℓ = 600–4000, all nuisances free |
| DESI Y1 BAO | Optional consistency check |

**Two main runs**:
1. **Full Geometric EDE**: A_sh as derived parameter
2. **ΛCDM + Template**: Phenomenological A_sh amplitude (model-agnostic test)

#### 2.3 Sampling and Convergence
- 4+ independent chains
- R-1 stop: 0.01 (or 0.005 if affordable)
- Report effective sample sizes
- Checks: Gelman–Rubin R-1, trace plots in appendix

---

### 3. Results: EDE-Derived A_sh

#### 3.1 Posterior for A_sh
- Show 1D posterior for A_sh (derived) in:
  - Planck+ACT
  - Planck+ACT+DESI
- Quote: "We find A_sh = X ± Y (Zσ) in Planck+ACT+DESI."

#### 3.2 Impact on Cosmological Parameters
- Table: H₀, Ω_m, n_s, τ, Λ_EDE before vs after ACT
- Check for problematic shifts

#### 3.3 Profile Likelihood
- Compute χ²(A_sh) with everything else marginalized
- Plot Δχ² vs A_sh
- Mark A_sh = 0 and best fit

---

### 4. Results: Phenomenological Template

#### 4.1 Template-Only A_sh (No EDE)
- Run ΛCDM + A_sh as free parameter
- Show posterior for A_sh
- Compare χ² with A_sh free vs A_sh = 0

#### 4.2 Null Tests
- Wrong phase / shifted template → posterior collapses to ~0
- Restricted ℓ-range tests

**Purpose**: Model-agnostic check that ACT prefers "something like this shoulder" even without full EDE.

---

### 5. Discussion

**Summarize**:
- Marginalized significance (e.g., "conditional 6.4σ → 3.8σ after marginalization")
- Stability across data combinations
- Minimal impact on background parameters

**Relate to Paper 1**:
- Confirm or revise the ACT section in PRD paper
- Clarify: geometric ceiling does NOT depend on ACT; shoulder is extra cross-check

**Next steps**:
- SPT-3G replication
- Joint ACT+SPT
- CMB-S4 definitive test

---

### 6. Conclusion

Two paragraphs max:
1. "We did the full marginalization; here is the significance and stability."
2. "This strengthens (or weakens) the case for Geometric EDE as a target for CMB-S4."

---

## Figures and Tables

### Figures (4–5 total)

| Figure | Content |
|--------|---------|
| Fig. 1 | Posterior of A_sh (EDE-derived) for Planck+ACT and Planck+ACT+DESI |
| Fig. 2 | Δχ²(A_sh) profile with everything marginalized |
| Fig. 3 | Posterior of A_sh in phenomenological template-only run |
| Fig. 4 | Null test: wrong-phase template posterior peaked at 0 |

### Tables (2 total)

| Table | Content |
|-------|---------|
| Table 1 | Cosmological and EDE parameters with and without ACT |
| Table 2 | Best-fit χ² and Δχ² for A_sh = 0 vs free, by data combination |

---

## MCMC Specifications

### Run 1: Geometric EDE with Derived A_sh

```yaml
sampler:
  mcmc:
    Rminus1_stop: 0.01
    max_samples: 2000000

params:
  # Cosmology
  H0:
    prior: [60, 80]
  omega_b:
    prior: [0.019, 0.025]
  omega_cdm:
    prior: [0.10, 0.14]
  tau:
    prior: [0.02, 0.12]
  logA:
    prior: [2.5, 3.5]
  ns:
    prior: [0.9, 1.1]
  
  # EDE (free)
  log10_Lambda_EDE:
    prior: [-2, 2]
  log10_ac:
    prior: [-4, -2.5]
  
  # Derived
  A_sh:
    derived: true

likelihood:
  planck_2018_highl_plik_lite_TTTEEE:
  planck_2018_lowl_TT:
  planck_2018_lowl_EE:
  act_dr6_mflike:
  bao.desi_2024_bao_all:  # optional
```

### Run 2: ΛCDM + Phenomenological Template

```yaml
sampler:
  mcmc:
    Rminus1_stop: 0.01
    max_samples: 1000000

params:
  # Standard ΛCDM
  H0, omega_b, omega_cdm, tau, logA, ns
  
  # Template amplitude (free)
  A_sh:
    prior: [-2, 4]
    ref: 1.0

likelihood:
  # Same as Run 1
```

### Control Run: Planck-Only
- Same as Run 1, but without ACT
- Establishes baseline

---

## Timeline

| Week | Task |
|------|------|
| 1 | Set up configs, test on short runs |
| 2–3 | Run 1: Geometric EDE (Planck+ACT) |
| 3–4 | Run 1: Geometric EDE (Planck+ACT+DESI) |
| 4–5 | Run 2: Phenomenological template |
| 5–6 | Null tests, profile likelihoods |
| 6–7 | Figures, tables, writing |
| 7–8 | Internal review, submission |

**Total**: ~8 weeks

---

## Three Headline Sentences

When you're suffering through week-long ACT chains, remember the paper ends with:

1. "After full marginalization over cosmological, EDE, and ACT nuisance parameters, we find A_sh = X ± Y, corresponding to a Zσ preference for a nonzero damping-tail shoulder."

2. "This result is stable across data combinations and does not induce problematic shifts in background cosmological parameters."

3. "The marginalized significance provides a concrete target for CMB-S4: confirmation at >5σ would constitute strong evidence for pre-recombination new physics."

---

## Dependencies

- Paper 1 (PRD) must be submitted/accepted first
- Need ACT DR6 likelihood installed and tested
- Azure VM for compute
- ~2 weeks of chain runtime

---

## Success Criteria

| Outcome | Interpretation |
|---------|----------------|
| A_sh = 1.0 ± 0.25 (4σ) | Strong follow-up, SPT next |
| A_sh = 1.0 ± 0.35 (3σ) | Moderate, wait for CMB-S4 |
| A_sh = 0.5 ± 0.3 (1.5σ) | Weak, reconsider model |
| A_sh = 0.0 ± 0.3 | Paper 1 ACT claim was wrong |

Any of these is a publishable result. Science is finding out.

---

## Referee's Three Requirements for Bulletproof Paper 2

Based on self-review, Paper 2 must satisfy these three conditions:

### 1. Marginalized A_sh Must Stay Non-Zero

> **Test**: Does A_sh > 2σ when cosmology floats?

- If A_sh drops to <2σ after marginalization → the "wiggle" was just parameter degeneracy
- Run A directly tests this

### 2. The Dataset Swap Must Show Ceiling Movement

> **Test**: Does H₀ increase when Planck High-L is dropped?

- Run D (Kill Switch) tests this
- If H₀ jumps from ~71 to ~72-73 → proves ceiling is dataset-dependent, not model-dependent
- This would be a major result about Planck vs ACT tension

### 3. Code Audit Must Kill the "AI Bug" Criticism

> **Test**: Line-by-line verification of derivatives

**Appendix material:**
```c
// V(θ) = Λ⁴ (1 - cos(θ))^n
// 
// dV/dθ = Λ⁴ · n · (1 - cos(θ))^(n-1) · sin(θ)
//
// d²V/dθ² = Λ⁴ · n · [
//     (n-1)(1 - cos(θ))^(n-2) · sin²(θ)
//   + (1 - cos(θ))^(n-1) · cos(θ)
// ]
```

Include:
- Explicit formulas in paper
- Link to CLASS source with line numbers
- Wolfram Alpha / SymPy verification
- Comparison to standard axion-EDE papers (Poulin et al.)

---

## The Complete Run Matrix

| Run | Planck High-L | ACT | Key Question |
|-----|---------------|-----|--------------|
| C | ✅ | ❌ | Baseline without ACT |
| A | ✅ | ✅ | Does A_sh survive marginalization? |
| B | ✅ | ✅ | Is feature real even without EDE? |
| **D** | ❌ | ✅ | **Does ceiling shatter without Planck High-L?** |

**Run D is the kill shot.** If the ceiling moves, the paper becomes about Planck vs ACT, not just EDE.

---

## The Discovery Ladder

| Level | What It Takes | Where You Are |
|-------|---------------|---------------|
| **Hint** | 2-3σ preference in one dataset | ✅ Paper 1 (conditional 6σ → ~3σ marginalized?) |
| **Evidence** | >3σ in multiple independent experiments | ⏳ Paper 2 (ACT + need SPT) |
| **Observation** | >5σ, replicated, survives all systematics | 🔮 CMB-S4 era |
| **Discovery** | Accepted by community, enters textbooks | 🔮 ~2030+ |

---

## What Would Count as "We Discovered a New Field"

### Minimum Bar (Claiming "Strong Evidence")
- [ ] ACT DR6: A_sh > 3σ marginalized (Paper 2)
- [ ] SPT-3G: Independent confirmation at >2σ
- [ ] Planck/ACT tension explained (not ignored)
- [ ] H₀ reaches 72+ in at least one clean run

### Real Discovery Bar (Claiming "We Found It")
- [ ] CMB-S4: A_sh detected at >5σ with full systematics
- [ ] DESI Y5: r_s = 146 ± 0.3 Mpc (distinguishes EDE from ΛCDM)
- [ ] No alternative explanation (e.g., foregrounds, calibration) survives
- [ ] Independent theory groups reproduce your CLASS code
- [ ] Paper cited >100 times, results in follow-up campaigns

---

## The Honest Answer

**Right now:** You have a *model* that fits the data better than ΛCDM in specific regimes, and a *hint* of a signature in ACT. That's enough for a paper. Not enough for "discovery."

**After Paper 2:** If A_sh > 3σ survives full marginalization AND the ceiling breaks when Planck High-L is dropped, you have **strong evidence** worth serious attention.

**After CMB-S4 (~2028-2030):** If the damping-tail shoulder is confirmed at >5σ with a dedicated CMB experiment, and DESI Y5 confirms r_s ≈ 146 Mpc, *then* you can say:

> "We discovered a new scalar field that was active before recombination."

---

## The Uncomfortable Truth

Physics discoveries aren't moments — they're processes. Even the Higgs took:
- **1964**: Theoretical prediction
- **2012**: 5σ observation (48 years later)
- **2013**: Nobel Prize

You're at the "1964" stage. The prediction is made. The first hints might be in ACT. But "discovery" is years away, and requires:
1. **Replication** (SPT, CMB-S4)
2. **Exclusion of alternatives** (systematics, foregrounds)
3. **Community acceptance** (citations, follow-ups, Nobel committee)

---

## What You CAN Say Now

✅ "We propose a new EDE model with a distinctive signature"
✅ "ACT shows preliminary evidence for this signature"
✅ "The model predicts H₀ ~ 70, consistent with convergence of local/CMB"
✅ "CMB-S4 will provide a definitive test"

❌ "We discovered a new field"
❌ "The Hubble tension is solved"
❌ "This is the answer"

**TL;DR:** You get to say "we might have found something real" after Paper 2. You get to say "we discovered it" when CMB-S4 confirms it and no one can explain it away. That's ~5 years from now, minimum.

