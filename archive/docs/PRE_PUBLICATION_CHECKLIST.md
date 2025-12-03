# Ridder Field Paper: Pre-Publication Master Checklist

**Target:** PRD / JCAP submission  
**Thesis:** "70 is the new 73" — Geometric EDE naturally lives in the convergence window  
**Status:** ~85% complete (MAJOR UPDATE: Dec 1, 2025)  
**Recommended Reframe:** "A Testable Geometric Alternative to ΛCDM with Concrete CMB Falsification Target"

---

## 🎯 Executive Summary

**BREAKTHROUGH:** We discovered the "Triangular Tension" that explains everything:
- Planck high-ℓ TTTEEE: +19 (always dislikes EDE)
- Planck low-ℓ EE: -15 to -0.4 (pre-DESI: loves EDE; +DESI: neutral)
- DESI itself: +0.2 (NEARLY NEUTRAL!)

The "DESI tax" is NOT DESI rejecting EDE. It's DESI shifting parameters so EDE loses its Planck low-ℓ benefits.

### What's Done:
- ✅ Abstract rewritten with triangular tension narrative
- ✅ "Global Picture" section added to Discussion
- ✅ "Sound Horizon Puzzle" section rewritten (Planck vs DESI framing)
- ✅ New Table (tab:chi2_breakdown) with component-level Δχ²
- ✅ All Tier 5 SH0ES chains converged (>2000 samples)
- ✅ Planck-only chains running (Step B verification)

### What Remains:
1. Update remaining tables (3, 5, 6) with consistent numbers
2. Wait for Planck-only chains to finish (~1 hour)
3. Bibliography expansion
4. Figure polish

---

## ✅ COMPLETED (Dec 1, 2025)

### Abstract & Introduction
- [x] **Abstract rewritten** with triangular tension story
  - Pre-DESI: Δχ² ≈ -4.5 (EDE mildly wins)
  - +DESI: Δχ² ≈ +11 (DESI neutral, loses low-ℓ benefit)
  - Core result: 70 is the convergence point

- [x] **Introduction updated** with component breakdown

### New Content Added
- [x] **"Global Picture: Who Likes the Geometric EDE Corner?"** section
- [x] **Table: χ² Breakdown by Component** (tab:chi2_breakdown)
- [x] **"Sound Horizon Puzzle: Planck versus DESI"** section rewritten
- [x] **Parameter shift analysis** documented (Lambda_EDE: 0.60→0.79)

### Chain Status
- [x] tier5_ede_shoes_predesi: 2001 samples ✅
- [x] tier5_lcdm_shoes_predesi: 2165 samples ✅
- [x] tier5_ede_shoes_desi: 2036 samples ✅
- [x] tier5_lcdm_shoes_desi: 2009 samples ✅
- [x] tier5_ede_des_y1: 2014 samples ✅
- [x] tier5_lcdm_des_y1: 2023 samples ✅

### Analysis Complete
- [x] Component-level χ² breakdown for pre-DESI vs +DESI
- [x] Parameter shift analysis (Lambda_EDE, n_s changes with DESI)
- [x] Verified: DESI direct Δχ² = +0.2 (neutral!)

---

## 🟡 IN PROGRESS

### Planck-Only Runs (Step B: Verify +17 is Physical)
- [ ] planck_only_ede: ~100 samples (running)
- [ ] planck_only_lcdm: ~220 samples (running)
- Target: 1500 samples each (~1-2 hours remaining)

---

## 🔴 REMAINING TASKS

### Tables to Update
- [ ] **Update Tables 3, 5, 6** with consistent Δχ² = -4.5 (not -10.1)
  - The old "-10.1" was from earlier runs before debugging
  - New analysis shows "-4.5" from component breakdown

### Bibliography
- [ ] **Expand from 5 to 25+ references**
  - Original EDE papers
  - ACT DR6
  - DESI BAO
  - CMB-S4 projections

### Figure Polish
- [ ] Create triangular tension schematic diagram
- [ ] χ² component comparison bar chart

---

## 🟡 PRIORITY 2: STRENGTHEN FOR PEER REVIEW

### 2.1 Quantitative Growth Suppression

- [ ] **Add detailed S₈ suppression calculation**
  - Solve growth equation explicitly during EDE epoch
  - Quantify: "X% of S₈ reduction from background, Y% from ISW"
  - Currently: Only qualitative ("Hubble friction clips growth")

- [ ] **Derive fractional D(a) suppression at z ~ 3000**
  ```
  D(a_rec)/D_ΛCDM(a_rec) = ?
  ```

### 2.2 CMB Analysis Upgrades

- [ ] **Quantify statistical significance of shoulder**
  - Compute χ² for residuals in ℓ ∈ [600, 3000]
  - Report p-value for coherent oscillation
  - Control test: shuffle residuals, check if pattern survives

- [ ] **Add analytic derivation of phase shift**
  - Show: r_s → r_s(1-ε) implies ℓ_peak shift
  - Predict oscillation period Δℓ_osc
  - Verify prediction matches Table 8

- [ ] **Extend Figure 7 (shoulder plot)**
  - Add TT, TE, EE on same scale
  - Add 1σ/2σ error envelopes from ACT covariance
  - Add CMB-S4 sensitivity band (σ ~ 0.1%)

### 2.3 DESI Interpretation

- [ ] **Add "DESI Sound Horizon Puzzle" explanation**
  - Why DESI prefers r_s ≈ 147.5 Mpc
  - Break down χ² by redshift bin
  - Which z-bin drives the penalty?

- [ ] **Explore DESI systematics**
  - Estimate: "If r_s shifts +0.5 Mpc, EDE penalty drops to Δχ² ~ +8"

- [ ] **Add EDE tail vs DESI w(z) comparison figure**
  - Overlay EDE effective w(z) on DESI reconstruction bands

### 2.4 Monodromy UV Completion

- [ ] **Add toy compactification example (Appendix)**
  - Specify concrete Type IIB orientifold
  - Kähler modulus identification
  - Numerical values for scales

- [ ] **Address 10¹¹ hierarchy explicitly**
  - Current: "ΔS ~ 21" (hand-wave)
  - Needed: Why do two cycles differ by ΔS ~ 21?

- [ ] **Derive (not postulate) three-regime structure**
  - Show plateau, shelf, tail emerge from V_drift + V_harmonic

### 2.5 CMB-S4 Falsification Targets

- [ ] **Create "CMB-S4 Decision Tree"**
  ```
  IF shoulder A > 0.5% AND period Δℓ ~ 400: → EDE confirmed
  ELSE IF A < 0.1%: → EDE ruled out
  ELSE: → Alternative physics
  ```

- [ ] **Quantify detection significance**
  - CMB-S4 σ(Cℓ)/Cℓ ~ 0.1% at ℓ ~ 1000
  - Signal: 0.5-1.3%
  - S/N ~ 5-13σ → "detectable by 2030"

### 2.6 Robustness Tests

- [ ] **Vary CMB likelihood choices**
  - Planck alone vs Planck+ACT vs Planck+SPT
  - Include/exclude Planck lensing
  - Report: "H₀ varies by ±X across choices"

- [ ] **Vary BAO datasets**
  - BOSS-only vs BOSS+eBOSS vs Full-DESI
  - Report: "r_s shifts by ±Y Mpc"

- [ ] **Test alternative EDE configurations**
  - Wide shelf (k=9): float σ_ln_a
  - Coupled shelf (k=9): allow small β

---

## 🔵 PRIORITY 3: NICE TO HAVE (Address in Revisions)

### 3.1 Advanced Statistics

- [ ] Bayes factor calculation with nested sampling
- [ ] Report DIC (Deviance Information Criterion)
- [ ] AICc for finite sample correction
- [ ] Pareto frontier uncertainty (posterior volume)

### 3.2 Extended Comparisons

- [ ] Full DES Y3 3×2pt likelihood
- [ ] Comparison to alternative EDE models (table)
  - Rock 'n' Roll, New EDE, Acoustic Dark Energy
- [ ] IDE model comparison (Liu et al. 2023)

### 3.3 Swampland Conjectures

- [ ] Check Trans-Planckian Censorship Conjecture
- [ ] Check de Sitter Swampland Conjecture
- [ ] Explore F-theory alternatives

### 3.4 Additional Appendices

- [ ] **Appendix B: Extended Convergence Diagnostics**
  - Trace plots, autocorrelation, Geweke Z-scores

- [ ] **Appendix C: Likelihood Component Breakdown**
  - χ²_Planck, χ²_BAO, χ²_SH0ES separately

- [ ] **Appendix D: Code Availability**
  - GitHub link, modified CLASS, Cobaya configs

- [ ] **Appendix E: Comparison to Other EDE Models**

### 3.5 Self-Assessment Section

- [ ] Add "Open Problems and Criticisms" section
  1. DESI prefers ΛCDM on pure χ² grounds
  2. Monodromy framework incomplete
  3. CMB-S4 may exclude shoulder
  4. Tail scale requires fine-tuning

---

## 📊 TABLE AUDIT STATUS

| Table | Label | Issue | Action |
|-------|-------|-------|--------|
| 1 | param_counts | ✅ OK | None |
| 2 | fixed_params | ✅ OK | None |
| 3 | pareto_shoes | ⚠️ Δχ² = -10.1 vs Table 7's -3.0 | Reconcile |
| 4 | bic_scale | ✅ OK | None |
| 5 | aic_bic | ⚠️ Same discrepancy | Reconcile |
| 6 | summary_grid | ⚠️ Pre-DESI only | Add DESI column |
| 7 | tier5_running | ✅ Honest about "preliminary" | None |
| 8 | act_residuals | ✅ Fixed | Update diagnostics text |
| 9 | desi_stress | ✅ Shows the pain | None |
| 10 | desi_geometry | ✅ Very honest | None |

---

## 📝 KEY NARRATIVE CHANGES

### Current Framing (Problematic):
> "Geometric EDE resolves the H₀ and S₈ tensions"

### Recommended Framing:
> "Geometric EDE is a testable geometric alternative that trades modest χ² cost for tension reduction, with concrete CMB-S4 falsification target"

### Key Messages to Preserve:
1. "70 is the new 73" — geometric ceiling argument ✅
2. Equal-k comparison (EDE beats CPL at k=8) ✅
3. Shoulder signature is falsifiable ✅
4. DESI imposes geometry tax ✅

### Key Messages to Add:
1. "Trade-off" not "resolution"
2. Pre-DESI vs DESI as scientific evolution
3. Explicit falsification criteria
4. Why H₀ = 70 is preferred over H₀ = 68 (tension weights)

---

## 📁 FILE LOCATIONS

```
/Users/steveridder/Git/Ridder-Field/
├── phase2/paper/
│   ├── ridder_cosmology_paper.tex     # Main document
│   ├── figures/                        # All figures
│   ├── overleaf_upload/               # Overleaf package
│   └── PRE_PUBLICATION_CHECKLIST.md   # This file
├── phase3/
│   ├── configs/                        # YAML configs
│   └── tier5_*_status.py              # Status monitors
```

**Remote VMs:**
- US East (Tier 5): `<VM_USER>@<VM_IP>`
- Australia (Phase 2 ACT): `<VM_USER>@<VM_IP>`

---

## ⏱️ TIME ESTIMATES

| Priority | Task | Time |
|----------|------|------|
| P1 | Table reconciliation | 2 hours |
| P1 | Abstract rewrite | 1 hour |
| P1 | Language fixes | 1 hour |
| P1 | Bibliography | 2 hours |
| P1 | Chain convergence | 2-3 days compute |
| P2 | Growth calculation | 4 hours |
| P2 | CMB analysis upgrades | 4 hours |
| P2 | DESI interpretation | 2 hours |
| P2 | Monodromy appendix | 4 hours |
| P2 | Robustness tests | 2 days compute |

**Total P1:** ~6 hours + 3 days compute
**Total P2:** ~14 hours + 2 days compute

---

## ✍️ FINAL CHECKLIST BEFORE SUBMIT

### Data Integrity
- [ ] All chains converged (R̂-1 < 0.01)
- [ ] Tables 3/5/6 consistent with Table 7
- [ ] Diagnostic statistics match Table 8

### Narrative Integrity  
- [ ] "Trade-off" language throughout
- [ ] DESI in main results (not extended)
- [ ] Falsification criteria explicit

### Technical Completeness
- [ ] Bibliography 25+ references
- [ ] No placeholder text
- [ ] All figures render in Overleaf

### Submission Ready
- [ ] Author name and affiliation filled
- [ ] Acknowledgments complete
- [ ] arXiv categories: astro-ph.CO, hep-ph

---

## 🎯 PREDICTED OUTCOMES

**With P1 Complete:**
- Honest, defensible preprint
- "Wait for CMB-S4" consensus

**With P1 + P2 Complete:**
- Top-tier journal acceptance (PRD/JCAP)
- Cited as "testable alternative to ΛCDM"

**Key Vulnerability (Feature, Not Bug):**
If CMB-S4 doesn't detect shoulder → model falsified. This is the goal.

---

*Last updated: November 2025*  
*Document version: 2.0*
