# Paper Revision Plan: Updated Findings

## Summary of Discovery

Our independent analysis revealed that the claimed 7.4σ detection is largely **foreground contamination**:

| Analysis | A_sh | Error | Significance |
|----------|------|-------|--------------|
| Original paper | 1.61 | 0.22 | 7.4σ |
| ACT cleaned | -0.25 | 0.50 | 0.5σ |
| SPT-3G cleaned | 0.13 | 0.08 | 1.7σ |
| **Combined** | **0.12** | **0.08** | **1.6σ** |

**Key finding**: When ~18 μK² foreground (CIB) is subtracted from ACT at ℓ > 1500, the signal disappears. ACT and SPT-3G then **agree** at A_sh ~ 0.1.

---

## Required Changes

### 1. Title
**Old**: "A Template Test for Pre-Recombination Physics and a Resolution-Dependent Feature in the ACT DR6 Damping Tail"

**New**: "A Template Test for Pre-Recombination Physics in CMB Damping Tails: Lessons from ACT DR6 and SPT-3G"

### 2. Abstract
Complete rewrite acknowledging:
- The template test methodology (still valid)
- ACT raw result shows excess
- Foreground cleaning reveals no significant signal
- SPT-3G confirms null result
- Combined constraint: A_sh = 0.12 ± 0.08 (1.6σ)

### 3. Introduction  
- Keep the motivation for template tests
- Remove claims of detection
- Add discussion of foreground systematics
- Frame as methodology development + cautionary tale

### 4. New Section: Foreground Analysis
- Show ACT raw vs cleaned comparison
- Show SPT-3G analysis
- Demonstrate consistency when foregrounds removed
- Discuss CIB contamination at 150 GHz

### 5. Results Section
- Present cleaned ACT result: A_sh ~ 0 ± 0.5
- Present SPT-3G result: A_sh = 0.13 ± 0.08
- Combined constraint: A_sh = 0.12 ± 0.08
- No significant detection (1.6σ)

### 6. Discussion
- Acknowledge that initial analysis was contaminated
- Discuss importance of foreground cleaning
- Note that SPT-3G provides independent check
- Future prospects (SO, CMB-S4)

### 7. Conclusions
- Template test methodology is sound
- Current data show no significant EDE signal
- Foreground contamination is critical systematic
- Future high-resolution data needed

---

## Key Numbers to Update

| Old | New |
|-----|-----|
| A_sh = 1.61 ± 0.22 | A_sh = 0.12 ± 0.08 (combined) |
| 7.4σ detection | 1.6σ (not significant) |
| Δχ² = -474 | Δχ² ~ -3 to -4 |
| "ACT detects" | "No significant detection" |

---

## Files to Modify

1. `paper2_v2_anomaly.tex` - Main paper
2. `references.bib` - Add SPT-3G reference
3. Create new figure: `act_spt_comparison.pdf`

---

## Execution Order

1. ☐ Update abstract
2. ☐ Update introduction
3. ☐ Add foreground analysis section
4. ☐ Update results section
5. ☐ Update discussion
6. ☐ Update conclusions
7. ☐ Update figures/tables
8. ☐ Add SPT-3G reference

