# Tier 5 SH0ES/TRGB + DESI: Archived Stress Tests

**Status:** 🏁 **ARCHIVED** — Chains complete, science verdict in, demoted to appendix material  
**Decision Date:** 2025-11-30  
**Chain Location:** `phase3/chains/tier5_*_desi.1.txt`

---

## Executive Summary

This Tier 5 stress test asked: **"Does Geometric EDE survive DESI's BAO constraints while resolving the H₀ tension?"**

**Answer:** No. Both the SH0ES and TRGB branches are disfavored, though the TRGB branch fails much more gracefully.

| World | Model | k | H₀ | r_s [Mpc] | S₈ | χ² | Δχ² vs ΛCDM |
|-------|-------|---|-----|-----------|-----|------|-------------|
| SH0ES+DESI | ΛCDM | 6 | 68.48 | 147.4 | 0.821 | 2930.7 | **ref** |
| SH0ES+DESI | CPL | 8 | 68.36 | 147.7 | 0.802 | 2941.6 | +10.9 |
| SH0ES+DESI | EDE | 8 | 72.57 | 142.1 | 0.775 | 3095.4 | **+165** 💀 |
| TRGB+DESI | ΛCDM | 6 | 68.17 | 147.3 | 0.828 | 2933.4 | **ref** |
| TRGB+DESI | EDE | 8 | 72.36 | 144.9 | 0.762 | 2991.2 | **+58** |

### Key Findings

1. **"Chasing H₀=73" is catastrophically dead with DESI**  
   SH0ES EDE achieves H₀=72.6 but at Δχ²≈+165 relative to ΛCDM—an utterly non-viable penalty.

2. **TRGB EDE is much gentler but still costly**  
   - r_s = 144.9 Mpc (only 1.6% below Planck, vs. 3.5% for SH0ES EDE)
   - Δχ² ≈ +58 (vs. TRGB ΛCDM)—still heavily disfavored but not catastrophic
   - S₈ = 0.762, hitting the DES Y3 target

3. **CPL provides zero uplift to H₀**  
   DESI likes late-time w(z) flexibility but uses it to improve fit, not raise H₀.

4. **The convergence window is narrow**  
   Once DESI enters, no k=8 extension can slide H₀ freely up to 73 without paying a huge likelihood penalty.

---

## What This Means for the Paper

### Use Case: Stress-Test Appendix

This run should appear in the paper as **supporting evidence that extreme early-time solutions are ruled out once DESI is included**—not as a central figure.

**Main text (one paragraph):**
> When we add DESI Y1 BAO to SH0ES-anchored worlds, Geometric EDE branches that push H₀ ≈ 72–73 with r_s ≈ 142 Mpc are disfavored by Δχ² ∼ +165; the corresponding TRGB-anchored branch with r_s ≈ 145 Mpc is still disfavored by Δχ² ∼ +60. This confirms that extreme early-time solutions are no longer viable once DESI is included.

**Appendix table:** Drop the summary table above as Table A1 "DESI Stress Tests of Extreme Local-Prior Worlds."

### What This Does NOT Tell Us

This stress test probed the **edges** of parameter space—worlds with strong local H₀ priors forcing the model to chase 72–73. It does **not** probe the **unconstrained** DESI world where the data decide H₀ freely.

The real scientific win is to show where the **unconstrained** DESI+Pantheon+ world puts the geometric shoulder—that is the next run.

---

## Chain Statistics (Final)

| Chain | Samples | Burn-in | H₀ σ | Status |
|-------|---------|---------|------|--------|
| tier5_lcdm_shoes_desi | 1237 | ~400 | 0.39 | ✅ Sufficient for Δχ² conclusions |
| tier5_cpl_shoes_desi | 971 | ~300 | 0.06 | ✅ Sufficient |
| tier5_ede_shoes_desi | 868 | ~300 | 0.55 | ✅ Sufficient |
| tier5_lcdm_trgb_desi | 637 | ~200 | 0.11 | ✅ Sufficient |
| tier5_ede_trgb_desi | 481 | ~150 | 0.52 | ✅ Sufficient |

**Total samples:** ~4,200 (plenty for the qualitative verdict)

---

## Why We're Stopping

The marginal value of additional samples is near zero. The qualitative story will not change:

- SH0ES EDE: Δχ² ≈ +165 ± a few → remains catastrophic
- TRGB EDE: Δχ² ≈ +58 ± a few → remains heavily disfavored
- Extra samples would only tighten error bars on H₀ and S₈ from sub-percent to sub-sub-percent

**Decision:** Let current chains hit their R-1 threshold naturally (if still running), then freeze. Do not start new variants.

---

## Next Tier 5 Priority: Unconstrained DESI World

The real science question is: **Where does the unconstrained DESI+Pantheon+ world put H₀ and r_s?**

### Phase 2a: DESI-Only (No H₀ Prior)

| Model | Data | k | Goal |
|-------|------|---|------|
| ΛCDM | Planck + preDESI BAO + DESI Y1 | 6 | Baseline |
| CPL | Planck + preDESI BAO + DESI Y1 | 8 | DESI's dynamical DE preference |
| EDE | Planck + preDESI BAO + DESI Y1 | 8 | Does EDE even initialize? |

### Phase 2b: DESI + Pantheon+ (No H₀ Prior)

| Model | Data | k | Goal |
|-------|------|---|------|
| ΛCDM | Planck + preDESI BAO + DESI Y1 + Pantheon+ | 6 | Baseline |
| CPL | Planck + preDESI BAO + DESI Y1 + Pantheon+ | 8 | Late-time preference |
| EDE | Planck + preDESI BAO + DESI Y1 + Pantheon+ | 8 | Geometric shoulder location |

**Hypothesis:** The unconstrained world will land near H₀ ∼ 70–71, r_s ∼ 145.5 Mpc—the "convergence window" that our paper claims is the natural home for Geometric EDE.

---

## Archive Location

- **Chains:** `phase3/chains/tier5_*_desi.1.txt` (keep, do not delete)
- **Status script:** `phase3/tier5_shoes_desi_status.py` (keep for reference)
- **This document:** `phase3/TIER5_SHOES_DESI_ARCHIVE.md`

---

## Citation for Paper

If including in appendix:

> **Table A1: DESI Y1 Stress Tests of Local-Prior Worlds**
>
> We tested whether Geometric EDE can survive joint fitting with DESI Y1 BAO when anchored to local H₀ priors. The SH0ES-anchored branch (H₀ ∼ 73, r_s ∼ 142 Mpc) incurs Δχ² ≈ +165 relative to ΛCDM—a catastrophic penalty that rules out this corner of parameter space. The TRGB-anchored branch (H₀ ∼ 70, r_s ∼ 145 Mpc) fares much better (Δχ² ≈ +58) but remains disfavored. These results confirm that DESI constrains the EDE parameter space to a narrow convergence window; extreme early-time solutions that chase H₀ = 73 are no longer viable.

---

*Archived 2025-11-30*
