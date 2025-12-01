# Data & Figures Plan: What to Keep vs Recreate

**Created:** Dec 1, 2025  
**Status:** After triangular tension discovery

---

## Executive Summary

The triangular tension discovery changes the story but NOT most of the underlying data. The main changes are:
1. **Numbers** in text/tables need updating to reflect component breakdown
2. **New table** (chi2_breakdown) added - DONE
3. **Some figures** need regenerating with updated numbers/captions
4. **Most chain data** is VALID and should be kept

---

## ✅ DATA TO KEEP (Chain Results)

These chains are converged and their physics is correct:

| Chain | Samples | Status | Use For |
|-------|---------|--------|---------|
| tier5_ede_shoes_predesi | 2001 | ✅ KEEP | Main pre-DESI result |
| tier5_lcdm_shoes_predesi | 2165 | ✅ KEEP | Baseline |
| tier5_ede_shoes_desi | 2036 | ✅ KEEP | +DESI comparison |
| tier5_lcdm_shoes_desi | 2009 | ✅ KEEP | +DESI baseline |
| tier5_ede_des_y1 | 2014 | ✅ KEEP | Growth world |
| tier5_lcdm_des_y1 | 2023 | ✅ KEEP | Growth baseline |
| tier5_*_trgb_* | 1600-1900 | ✅ KEEP | TRGB worlds |
| planck_only_* | Running | ⏳ WAIT | Planck-only breakdown |

**Key insight:** The "-10.1" vs "-4.5" discrepancy was NOT a chain error. It was:
- Old chains had different likelihood setup
- New chains with correct setup show -4.5
- The triangular tension explains WHY: +19 high-ℓ, -18 low-ℓ, -3.5 SH0ES

---

## 🔄 FIGURES TO UPDATE/REGENERATE

### Figures Needing Caption/Value Updates Only

| Figure | Current File | What to Update |
|--------|--------------|----------------|
| Fig 1: Tension reduction | paper_tension_reduction.png | Caption text only |
| Fig 3: Cross-world | paper_cross_world.png | Caption reference to new Δχ² |
| Fig 4: Forest plot | paper_forest_plot.png | Caption updated ✅ |
| Fig 5: H0-χ² tradeoff | paper_h0_chi2_tradeoff.png | Caption updated ✅ |

### Figures That May Need Regeneration

| Figure | File | Why | Priority |
|--------|------|-----|----------|
| Pareto front plots | ??? | Update Δχ² values in plot | 🟡 Medium |
| AIC/BIC comparison | ??? | New numbers | 🟡 Medium |

### NEW Figures Needed

| Figure | Description | Priority |
|--------|-------------|----------|
| **Triangular tension schematic** | Diagram showing Planck high-ℓ vs low-ℓ EE vs SH0ES | 🔴 High |
| **χ² component bar chart** | Side-by-side pre-DESI vs +DESI breakdown | 🔴 High |
| **Parameter shift diagram** | How Lambda_EDE and n_s change with DESI | 🟡 Medium |

---

## 📊 TABLES STATUS

### ✅ Updated Tables

| Table | Status | New Values |
|-------|--------|------------|
| tab:pareto_shoes | ✅ Updated | Δχ² = -4.5, H₀ = 69.7 |
| tab:aic_bic | ✅ Updated | Δχ² = -4.5, AIC = -0.5, BIC = +11.3 |
| tab:summary_grid | ✅ Updated | Consistent with -4.5 |
| **tab:chi2_breakdown** | ✅ NEW | Component-level Δχ² |

### Tables to Verify

| Table | Contains | Check |
|-------|----------|-------|
| tab:tier5_running | Tier 5 results | May need updating with final numbers |
| tab:desi_stress | DESI stress tests | Values appear ok |
| tab:desi_geometry | Geometry tests | Values appear ok |
| tab:act_residuals | ACT diagnostics | Already corrected |

---

## 📈 CHAIN DATA ANALYSIS PLAN

### What We Have (Tier 5 Converged)

```
Pre-DESI SH0ES World:
  EDE:  H₀ = 69.7, S₈ = 0.82, Δχ² = -4.5 (via component breakdown)
  ΛCDM: H₀ = 68.3, S₈ = 0.83, Δχ² = 0 (reference)

+DESI SH0ES World:
  EDE:  H₀ = 69.5, S₈ = 0.82, Δχ² = +10.8 (net)
  ΛCDM: H₀ = 68.5, S₈ = 0.82, Δχ² = 0 (reference)
  
Component Breakdown (Key Finding!):
  Pre-DESI:
    - Planck high-ℓ TTTEEE: +18.9
    - Planck low-ℓ EE: -15.2
    - Planck low-ℓ TT: -3.3
    - SH0ES: -3.5
    - BAO: -0.5
  +DESI:
    - Planck high-ℓ TTTEEE: +16.9 (stable!)
    - Planck low-ℓ EE: -0.4 (LOST!)
    - Planck low-ℓ TT: -1.5
    - SH0ES: -6.2
    - DESI: +0.2 (NEUTRAL!)
```

### What's Running Now

```
Planck-Only World (Step B verification):
  EDE: 232 samples (running)
  ΛCDM: 433 samples (running)
  Target: 1500 samples (~30-60 min remaining)
  Purpose: Confirm +17 high-ℓ tax is physical, not numerical
```

### What We DON'T Need to Re-run

1. **Tier 5 SH0ES chains** - Already have 2000+ samples, numbers are good
2. **TRGB chains** - Secondary worlds, current samples sufficient
3. **Growth (DES Y1) chains** - Have 2000+ samples
4. **Old "Tier 10" style chains** - Superseded by Tier 5 component analysis

---

## 🎯 IMMEDIATE ACTIONS

### Today (While Planck-only runs)
1. ✅ Update tables (DONE)
2. ✅ Expand bibliography (DONE)
3. ⏳ Wait for Planck-only chains (~1 hour)
4. 📝 Draft triangular tension figure concept

### Tomorrow
1. Analyze Planck-only results when ready
2. Generate triangular tension schematic figure
3. Generate χ² component bar chart
4. Final pass on paper consistency

### Before Submission
1. Verify all figures match updated text
2. Run LaTeX compilation, check for errors
3. Update Overleaf upload folder
4. Final bibliography check

---

## 📁 FILE ORGANIZATION

### Figures Directory Status
```
phase2/paper/figures/
  ├── paper_tension_reduction.png    # Keep, update caption only
  ├── paper_cross_world.png          # Keep, update caption only  
  ├── paper_forest_plot.png          # Keep, caption updated
  ├── paper_h0_chi2_tradeoff.png     # Keep, caption updated
  ├── paper_pareto_3d.png            # Keep or regenerate
  ├── phase2_shoulder.png            # ACT shoulder - keep
  └── [NEW] triangular_tension.png   # Need to create
  └── [NEW] chi2_components.png      # Need to create
```

---

## Summary: The Data Story

**What Changed:** Our understanding, not the data itself.

The chains we ran ARE correct. The "-10.1" vs "-4.5" difference is because:
- Earlier runs used slightly different likelihood configurations
- Current Tier 5 runs with proper component tracking show -4.5
- The triangular tension (high-ℓ tax vs low-ℓ benefit vs SH0ES) was ALWAYS there
- We just didn't have the component breakdown to see it clearly

**What to Keep:** All Tier 5 chain data
**What to Update:** Text, tables, some figure captions
**What to Create:** New figures showing the triangular tension
