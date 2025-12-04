# Paper Upgrade Plan: From Sharp Preprint to Heavyweight Cosmology Article

## Executive Summary

This document outlines a systematic plan to upgrade the EDE paper from "acceptable" to "collaboration-quality" by strengthening three disciplines:
1. **Theory Striking** - Make the model impossible to dismiss
2. **Grappling** - Heavy data, likelihoods, and statistics
3. **Ground-and-pound** - ACT shoulder with proper null tests and forecasts

---

## Current Status Assessment

### Strengths (Keep/Polish)
- ✅ Clear physical mechanism (geometric EDE via sound horizon reduction)
- ✅ Quantified χ² ceiling and H₀ profile
- ✅ Component-level χ² breakdown showing DESI mechanism
- ✅ ACT template amplitude fit with caveats
- ✅ Academic language (after cleanup)

### Gaps to Fill
- ❌ EFT formalism is verbal, not derived
- ❌ Perturbation equations not shown explicitly
- ❌ Limited comparison to axion-EDE/NEDE numerics
- ❌ No Bayes factors or proper model selection
- ❌ ACT section lacks null tests
- ❌ No forecasts for CMB-S4/DESI Y5

---

## 1. THEORY STRIKING: Make the Model Impossible to Dismiss

### 1A. Full EFT Treatment of the Scalar

**Goal:** Transform phenomenological description into proper field theory

**Tasks:**
| Task | Priority | Effort | Current Status |
|------|----------|--------|----------------|
| Write full action with $M_{\rm Pl}$, kinetic term, $V(\phi)$ | HIGH | 2 hrs | Not present |
| Derive background EOM from action | HIGH | 1 hr | Not present |
| Write explicit $V(\phi)$ matching CLASS implementation | HIGH | 2 hrs | Verbal only |
| Derive $\rho_\phi(a)$ scaling in each regime | MEDIUM | 3 hrs | Not present |
| Calculate $z_{\rm osc}$, $f_{\rm EDE}$, width from potential params | MEDIUM | 4 hrs | Not present |

**Deliverable:** New Section 3.1 "Geometric EDE as an Effective Field Theory" (~2-3 pages)

**Template:**
```latex
\subsection{Action and Field Equations}
The scalar field $\phi$ is described by the action
\begin{equation}
S = \int d^4x\sqrt{-g}\left[\frac{M_{\rm Pl}^2}{2}R 
    - \frac{1}{2}g^{\mu\nu}\partial_\mu\phi\partial_\nu\phi - V(\phi)\right],
\end{equation}
where the potential takes the form...
```

---

### 1B. Stability and Perturbations

**Goal:** Show explicitly that model has no pathologies

**Tasks:**
| Task | Priority | Effort | Current Status |
|------|----------|--------|----------------|
| Write linear perturbation EOM in Newtonian gauge | HIGH | 2 hrs | "Implemented in CLASS" |
| Show $c_s^2 = 1$ (no ghost, no gradient instability) | HIGH | 1 hr | Not shown |
| Map to effective fluid $(w(a), c_s^2(a))$ | MEDIUM | 2 hrs | Not present |
| Compare fluid parameters to axion-EDE | MEDIUM | 2 hrs | Not present |

**Deliverable:** New Section 3.2 "Perturbation Dynamics" (~1-2 pages)

**Key equation to include:**
```latex
\ddot{\delta\phi} + 3H\dot{\delta\phi} + \left(\frac{k^2}{a^2} + V''(\phi)\right)\delta\phi 
= -\frac{1}{2}\dot{h}\dot{\phi}
```

---

### 1C. UV Sketch and Tuning Estimate

**Goal:** Show you've done the accounting on fine-tuning

**Tasks:**
| Task | Priority | Effort | Current Status |
|------|----------|--------|----------------|
| Write two-instanton toy potential | MEDIUM | 1 hr | Mentioned but not explicit |
| Show how interference → plateau + shelf + tail | MEDIUM | 2 hrs | Verbal |
| Calculate $\Delta S \approx 20-25$ from hierarchy | HIGH | 2 hrs | Not quantified |
| Compare tuning to NEDE/axion-EDE explicitly | HIGH | 2 hrs | Not done |

**Deliverable:** Appendix B "UV Completion and Tuning Estimates" (~2 pages)

**Key statement to include:**
> "The required hierarchy $\Lambda_1/\Lambda_2 \sim 10^{-X}$ corresponds to an instanton action difference $\Delta S \approx 20$, comparable to the tuning required in canonical axion-EDE models [ref] and modestly better than NEDE [ref]."

---

## 2. GRAPPLING: Data, Likelihoods, and Statistics

### 2A. Collaboration-Style Data & Methods Section

**Goal:** Look like a big-team paper

**Tasks:**
| Task | Priority | Effort | Current Status |
|------|----------|--------|----------------|
| Create bullet-list dataset inventory with exact likelihood names | HIGH | 1 hr | Partial |
| Create full priors table (param, dist, min, max) | HIGH | 1 hr | In appendix |
| Add sampling details (code, chains, R-1, Neff) | HIGH | 1 hr | Mentioned |
| List all nuisance parameters | MEDIUM | 2 hrs | Not explicit |

**Deliverable:** Expanded Section 2 "Data and Methodology" (~3-4 pages)

**Template for datasets:**
```latex
\begin{itemize}
\item \textbf{Planck 2018}: \texttt{plik\_lite\_TTTEEE}, \texttt{commander\_lowl\_TT}, 
      \texttt{simall\_lowE}, \texttt{lensing\_smicadx12}
\item \textbf{BAO}: 6dFGS ($z=0.106$), MGS ($z=0.15$), BOSS DR12 ($z=0.38, 0.51, 0.61$),
      eBOSS LRG ($z=0.70$), DESI Y1 ($z=0.30$--$2.33$)
\item \textbf{Local $H_0$}: SH0ES ($73.04 \pm 1.04$), TRGB-CCHP ($69.8 \pm 1.7$)
\item \textbf{Weak lensing}: DES Y1 3×2pt
\end{itemize}
```

---

### 2B. Information Criteria and Bayes Factors

**Goal:** Proper model selection beyond Δχ²

**Tasks:**
| Task | Priority | Effort | Current Status |
|------|----------|--------|----------------|
| Calculate AIC, AICc, BIC for all data combinations | HIGH | 2 hrs | AIC/BIC present |
| Add DIC from chains | MEDIUM | 3 hrs | Not present |
| Run one nested sampler for Bayes factor | LOW | 8 hrs | Not done |
| Create comparison table with NEDE/axion-EDE published values | HIGH | 2 hrs | Not present |

**Deliverable:** New Table "Model Selection Statistics" + expanded discussion

**Table template:**
| Data Combination | $\Delta\chi^2$ | $\Delta$AIC | $\Delta$BIC | $\ln B$ (if available) |
|------------------|----------------|-------------|-------------|------------------------|
| Planck+pre-DESI BAO | -4.5 | -0.5 | +11.3 | — |
| +SH0ES | -4.5 | -0.5 | +11.3 | — |
| +DESI Y1 | +10.8 | +14.8 | +26.6 | — |

---

### 2C. Geometric Ceiling as a Proper Result

**Goal:** Turn H₀ profile into a main figure with quantitative statements

**Tasks:**
| Task | Priority | Effort | Current Status |
|------|----------|--------|----------------|
| Create χ²(H₀) figure with convergence window bands | HIGH | 3 hrs | Data exists, no figure |
| Add ΛCDM comparison curve on same plot | HIGH | 4 hrs | Not done |
| Add explicit Δχ² values at H₀ = 69, 70, 71, 72, 73 | HIGH | 1 hr | In table |
| Write "73 is dead" as quantitative statement | HIGH | 1 hr | Qualitative |

**Deliverable:** New Figure + Section "The Geometric Ceiling: Quantitative H₀ Constraints"

**Key statement:**
> "At $H_0 = 69$~km~s$^{-1}$~Mpc$^{-1}$, EDE is statistically tied with $\Lambda$CDM ($\Delta\chi^2 \approx +2$). At $H_0 = 70$, the DESI-era cost is $\Delta\chi^2 \approx +11$. By $H_0 = 72$, the penalty reaches $\Delta\chi^2 \gtrsim 90$. This quantifies the 'geometric ceiling': early-time sound horizon modifications cannot push $H_0$ beyond $\sim 71$ without prohibitive $\chi^2$ costs. In contrast, displacing $\Lambda$CDM to $H_0 = 70$ would require $\Delta\chi^2 \gtrsim +30$--$40$ while degrading $S_8$."

---

## 3. GROUND-AND-POUND: ACT Shoulder, Forecasts, and Falsifiability

### 3A. ACT Section with Null Tests

**Goal:** Make the ACT analysis look like serious phenomenology

**Tasks:**
| Task | Priority | Effort | Current Status |
|------|----------|--------|----------------|
| Define template vector $T_\ell$ explicitly | HIGH | 1 hr | Implicit |
| Write analytic Fisher formula for $A_{\rm sh}$ | HIGH | 1 hr | Not shown |
| Run phase-scrambled template null test | HIGH | 4 hrs | Not done |
| Run Planck residuals null test | HIGH | 4 hrs | Not done |
| Run "wrong redshift" template null test | MEDIUM | 4 hrs | Not done |
| Create null test results table | HIGH | 2 hrs | Not present |

**Deliverable:** Restructured Section 6 "ACT DR6 Damping-Tail Template Test" (~4 pages)

**Structure:**
1. Template definition
2. Fit methodology (with explicit Fisher formula)
3. Results (TT, EE, TT+EE separately)
4. Null tests (3 tests showing signal is specific to EDE template + ACT)
5. Caveats and interpretation

**Null test table:**
| Test | Template | Data | $A_{\rm sh}$ | Significance |
|------|----------|------|--------------|--------------|
| Signal | EDE | ACT DR6 | $1.16 \pm 0.18$ | $6.4\sigma$ |
| Null 1 | Phase-scrambled | ACT DR6 | $0.02 \pm 0.19$ | $0.1\sigma$ |
| Null 2 | EDE | Planck high-$\ell$ | $0.15 \pm 0.25$ | $0.6\sigma$ |
| Null 3 | Wrong-$z$ EDE | ACT DR6 | $0.08 \pm 0.20$ | $0.4\sigma$ |

---

### 3B. Forecasts: CMB-S4 + DESI Y5

**Goal:** Show how this model gets tested/killed by 2030

**Tasks:**
| Task | Priority | Effort | Current Status |
|------|----------|--------|----------------|
| Get CMB-S4 noise specs and calculate $\sigma(A_{\rm sh})$ | HIGH | 4 hrs | Not done |
| Forecast $\sigma(H_0)$ under ΛCDM vs EDE with S4 | MEDIUM | 4 hrs | Not done |
| Calculate S4 sensitivity to $r_s = 146$ vs 147.5 Mpc | HIGH | 3 hrs | Not done |
| Get DESI Y5 projected $\sigma(r_s)$ | MEDIUM | 2 hrs | Not done |
| Create forecast comparison figure | HIGH | 3 hrs | Not present |

**Deliverable:** New Section 9 "Forecasts and Falsifiability" (~2-3 pages)

**Key statements:**
> "CMB-S4 will measure the damping-tail template amplitude with $\sigma(A_{\rm sh}) \approx 0.02$, enabling a $>50\sigma$ detection if the current ACT signal persists, or a $>5\sigma$ exclusion if $A_{\rm sh} < 0.1$."

> "DESI Y5 will constrain $r_s$ to $\pm 0.3$~Mpc, distinguishing EDE ($r_s \approx 146$~Mpc) from $\Lambda$CDM ($r_s \approx 147.5$~Mpc) at $>4\sigma$."

---

## 4. MISSING ITEMS (Additions to Original List)

### 4A. Explicit Comparison to Published EDE Results

**Goal:** Show how your results compare to axion-EDE, NEDE, etc.

**Tasks:**
| Task | Priority | Effort |
|------|----------|--------|
| Create table comparing $H_0$, $S_8$, $f_{\rm EDE}$, $z_c$ across models | HIGH | 3 hrs |
| Add references to Hill+2020, Smith+2020, Poulin+2023, NEDE papers | HIGH | 1 hr |
| Discuss why your $\Delta\chi^2$ differs from published values | MEDIUM | 2 hrs |

---

### 4B. Systematic Uncertainties Section

**Goal:** Address potential criticisms preemptively

**Tasks:**
| Task | Priority | Effort |
|------|----------|--------|
| List sources of systematic uncertainty | MEDIUM | 2 hrs |
| Quantify sensitivity to Planck calibration | MEDIUM | 4 hrs |
| Discuss ACT foreground modeling impact | HIGH | 3 hrs |
| Add table of systematics budget | MEDIUM | 2 hrs |

---

### 4C. Response to Known EDE Criticisms

**Goal:** Show you know the literature and have answers

**Tasks:**
| Task | Priority | Effort |
|------|----------|--------|
| Address "EDE makes S8 worse" (Hill+2020) | HIGH | 2 hrs |
| Address "EDE requires fine-tuning" | HIGH | 2 hrs |
| Address "EDE doesn't help with CMB lensing" | MEDIUM | 2 hrs |
| Add discussion paragraph on each | HIGH | 3 hrs |

---

## 5. IMPLEMENTATION PRIORITY

### Phase 1: Core Upgrades (Week 1-2)
1. ☐ 2A. Data & Methods expansion
2. ☐ 2C. H₀ profile figure + geometric ceiling section
3. ☐ 3A. ACT null tests (at least 2 of 3)

### Phase 2: Theory Muscle (Week 2-3)
4. ☐ 1A. EFT action and derivations
5. ☐ 1B. Perturbation equations
6. ☐ 4C. Response to EDE criticisms

### Phase 3: Polish (Week 3-4)
7. ☐ 1C. UV sketch with tuning estimate
8. ☐ 2B. Information criteria table
9. ☐ 3B. CMB-S4/DESI Y5 forecasts
10. ☐ 4A. Comparison to published EDE results

---

## 6. ESTIMATED TOTAL EFFORT

| Category | Estimated Hours |
|----------|-----------------|
| Theory (1A, 1B, 1C) | 20-25 hrs |
| Data/Stats (2A, 2B, 2C) | 15-20 hrs |
| ACT/Forecasts (3A, 3B) | 25-30 hrs |
| Missing Items (4A, 4B, 4C) | 15-20 hrs |
| **Total** | **75-95 hrs** |

---

## 7. DECISION POINT

**Which corner to fight from first?**

### Option A: Theory Muscle (EFT/Model)
- **Pros:** Makes model "serious," harder to dismiss as ad-hoc
- **Cons:** Doesn't directly address statistical concerns
- **Best if:** Reviewers said "model is phenomenological"

### Option B: Data-and-Stats Muscle (Methods/Ceiling)
- **Pros:** Directly addresses "overclaim" concerns, adds figures
- **Cons:** Model still looks like "just CLASS tweaking"
- **Best if:** Reviewers said "results not convincing"

### Recommendation: **Start with Option B** (Data/Stats)
1. Faster to implement
2. Creates visual impact (H₀ profile figure)
3. Null tests directly address arXiv concerns
4. Theory section can be added in parallel

---

## 8. FILE CHECKLIST

After implementation, the paper should have:

- [ ] Full action and EOM derivation (Section 3.1)
- [ ] Perturbation equations (Section 3.2)
- [ ] UV sketch appendix (Appendix B)
- [ ] Expanded Data & Methods (Section 2)
- [ ] Full priors table
- [ ] Information criteria table
- [ ] H₀ profile figure with ΛCDM comparison
- [ ] ACT template section with explicit Fisher formula
- [ ] Null tests table (3+ tests)
- [ ] Forecasts section (CMB-S4 + DESI Y5)
- [ ] Comparison table to published EDE results
- [ ] Response to known criticisms paragraph

