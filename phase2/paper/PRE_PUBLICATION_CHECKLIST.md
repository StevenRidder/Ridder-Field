# Ridder Field Paper: Pre-Publication Master Checklist

**Target:** PRD / JCAP submission  
**Thesis:** "70 is the new 73" — Geometric EDE naturally lives in the convergence window  
**Status:** ~60% complete  
**Recommended Reframe:** "A Testable Geometric Alternative to ΛCDM with Concrete CMB Falsification Target"

---

## 🎯 Executive Summary

The paper is **structurally complete** but needs:
1. DESI promotion (not "extended analysis")
2. Table reconciliation (Δχ² = -10 vs -3 discrepancy)
3. ACT chain convergence (4-chain, R̂-1 < 0.01)
4. Honest reframing (trade-off, not resolution)
5. Bibliography expansion

---

## 🔴 PRIORITY 1: PUBLISH-BLOCKING (Must Complete Before arXiv)

### 1.1 Data Presentation Restructure

- [ ] **Move DESI from "Tier 5 Extended Analysis" to main results**
  - Currently buried in Section 5.4.1
  - Make Table 7 a primary result, not afterthought
  - Rename: "Section 5.2: DESI Integration" (not "extended")

- [ ] **Reconcile Tables 3/5/6 with Table 7**
  - Table 3: Δχ² = -10.1 (SH0ES pre-DESI)
  - Table 7: Δχ² = -3.0 (same world)
  - **This 7-unit discrepancy must be explained or fixed**

- [ ] **Add "How DESI Changed Everything" comparison table**
  ```
  Metric          | Pre-DESI | +DESI Y1 | Interpretation
  ----------------|----------|----------|----------------
  Δχ² (EDE)       | -10.1    | +18.1    | Penalty imposed
  H₀ (EDE)        | 70.6     | 69.9     | Modest reduction
  r_s preference  | Flexible | 147.5    | DESI constraint
  ```

### 1.2 Chain Convergence

- [ ] **Run full 4-chain MCMC for ACT world**
  - Current: "preliminary peek chains (single chain, ~1700 samples)"
  - Target: 4 chains × 2000 samples, R̂-1 < 0.01
  
- [ ] **Complete Tier 5 convergence for key worlds**
  | World | Model | Current N | Target N | Status |
  |-------|-------|-----------|----------|--------|
  | SH0ES Pre-DESI | ΛCDM | ~1100 | 2000+ | 🔴 |
  | SH0ES Pre-DESI | EDE | ~1700 | 2000+ | 🟡 |
  | SH0ES +DESI | Both | ~1200 | 2000+ | 🔴 |
  | Growth (DES Y1) | Both | ~1400-1800 | 2000+ | 🟡 |

### 1.3 Diagnostic Statistics Fix

- [ ] **Update ACT residual statistics (lines 801-806)**
  - Current (wrong): Mean +0.53%, RMS 0.50%
  - Recalculated from Table 8: Mean ~-0.1%, RMS ~1.3%
  
### 1.4 Abstract Rewrite

- [ ] **Rewrite abstract to lead with honest summary**
  ```
  Current problem: Promises "resolution" but buries DESI caveats
  
  Revised structure:
  - Para 1: Tension reduction (4.3σ → 2.3σ, 2.7σ → 1.1σ)
  - Para 2: Pre-DESI result (Δχ² = -10, better fit)
  - Para 3: DESI reality (Δχ² = +15-20, trade-off)
  - Para 4: Falsifiable prediction (shoulder, CMB-S4)
  ```

### 1.5 Language Correction

- [ ] **Replace "resolution" with "amelioration" or "trade-off" throughout**
  - Search: "resolving both tensions"
  - Replace: "reducing tension severity while maintaining statistical viability"

### 1.6 Bibliography Expansion

- [ ] **Expand from 5 to 25+ references**
  Must add:
  - Original EDE: Karwal & Kamionkowski 2016, Poulin et al. 2019
  - Rock 'n' Roll EDE: Agrawal et al. 2019
  - New EDE: Niedermann & Sloth 2020
  - ACT DR6: Madhavacheril et al. 2024
  - DESI BAO: DESI Collaboration 2024
  - CMB-S4 projections: Abazajian et al. 2022

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
- US East (Tier 5): `ridderadmin@172.191.4.60`
- Australia (Phase 2 ACT): `ridderadmin@20.58.129.33`

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
