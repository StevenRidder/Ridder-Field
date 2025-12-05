# Paper 2: Full Marginalized ACT Analysis

## Current Status

| Run | Config | Status | Purpose |
|-----|--------|--------|---------|
| C | `run_control_planck_only.yaml` | 🟢 Running | Baseline EDE without ACT |
| A | `run_a_ede_marginalized.yaml` | ⏳ Pending | Full EDE with ACT (main result) |
| B | `run_b_lcdm_template.yaml` | ⏳ Pending | ΛCDM + A_sh template (model-agnostic) |

### Monitoring Commands
```bash
# Quick status
./quick_status.sh

# Detailed analysis
python check_chain_status.py

# Watch logs
tail -f chains/*.log
```

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

