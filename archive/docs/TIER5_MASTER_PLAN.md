# Tier 5 Master Plan: Final Evidence for Geometric EDE

**Created:** 2025-11-30  
**Status:** 🚀 Phase 1 Ready to Launch

---

## Executive Summary

Tier 5 answers three critical questions that complete the paper:

| Phase | Dataset | Question | Status |
|-------|---------|----------|--------|
| **1** | DESI Y1 + Pantheon+ | Is the ~1% r_s reduction allowed by distance data? | 🟡 Ready |
| **2** | ACT DR6 | Does the model survive high-ℓ CMB structure? | ⏳ After Phase 1 |
| **3** | DES Y3 | Does growth suppression match weak lensing? | ⏳ After Phase 2 |

**Chain Standard:** 3 chains per model, 1500-2500 samples each, R̂-1 < 0.01

---

## Phase 1: DESI Y1 BAO + Pantheon+ (Essential)

### What We're Testing

**DESI Y1 BAO:**
- Does the posterior for r_s sit ~1% below ΛCDM value?
- Do DESI BAO points align with EDE prediction at shifted r_s?
- Does χ² remain competitive with ΛCDM?

**Pantheon+:**
- Does the EDE late-time tail pass SN residuals test?
- Are residuals μ_model(z) - μ_ΛCDM(z) at ≲0.02 mag level?

### Chains Required

**World A: Planck + preDESI BAO + DESI Y1** (no H₀ prior)

| Model | k | Config | Samples/chain | Target |
|-------|---|--------|---------------|--------|
| ΛCDM | 6 | `tier5_lcdm_desi.yaml` | 1500-2000 | Baseline |
| CPL | 8 | `tier5_cpl_desi.yaml` | 1500-2000 | Equal-k comparison |
| EDE | 8 | `tier5_ede_desi.yaml` | 2000-2500 | Main result |

**World B: World A + Pantheon+**

| Model | k | Config | Samples/chain | Target |
|-------|---|--------|---------------|--------|
| ΛCDM | 6 | `tier5_lcdm_desi_pantheon.yaml` | 1500-2000 | Baseline |
| CPL | 8 | `tier5_cpl_desi_pantheon.yaml` | 1500-2000 | Equal-k comparison |
| EDE | 8 | `tier5_ede_desi_pantheon.yaml` | 2000-2500 | Main result |

### Convergence Targets

- **R̂ - 1 < 0.01** for H₀, S₈, Ω_m, r_s, f_EDE, z_c
- **R̂ - 1 < 0.02** for nuisance parameters
- **ESS ≥ 1500** for H₀, S₈
- **ESS ≥ 1000** for EDE parameters

### Paper Plots from Phase 1

1. **Sound horizon comparison** — r_s posterior for ΛCDM vs CPL vs EDE
2. **H(z) and w(z) reconstruction** — Show EDE leaves w(z) ~ -1 at z < 1
3. **Pantheon+ residuals** — Δμ(z) for all three models

---

## Phase 2: ACT DR6 (Damping Tail)

### What We're Testing

- Does Geometric EDE remain consistent with high-ℓ ACT data?
- Are spectral distortions from the shoulder within current noise?
- Can we show the "soft shoulder" signature?

### Chains Required

**World C: Planck + preDESI BAO + SH0ES + ACT DR6**

| Model | k | Config | Samples/chain | Priority |
|-------|---|--------|---------------|----------|
| ΛCDM | 6 | `tier5_lcdm_act.yaml` | 1500 | Essential |
| EDE | 8 | `tier5_ede_act.yaml` | 2000-2500 | Essential |
| CPL | 8 | (optional) | 1500 | Nice to have |

### Paper Plots from Phase 2

1. **Residual power spectra** — ΔC_ℓ/C_ℓ^ΛCDM for ℓ = 600-3000
2. **ACT error overlay** — Show distortions sit within error envelope
3. **Phase shift diagnostic** — Qualitative oscillation pattern

---

## Phase 3: DES Y3 (Growth/S₈)

### What We're Testing

- Does Geometric EDE S₈ ≈ 0.79 sit closer to DES/KiDS/HSC?
- Is there consistent suppression of growth without breaking distances?

### Chains Required

**World D: Planck + preDESI BAO + SH0ES + DES Y3 3x2pt**

| Model | k | Config | Samples/chain | Priority |
|-------|---|--------|---------------|----------|
| ΛCDM | 6 | `tier5_lcdm_des.yaml` | 1500-2000 | Essential |
| EDE | 8 | `tier5_ede_des.yaml` | 2000-2500 | Essential |
| CPL | 8 | (optional) | 1500-2000 | Nice to have |

### Paper Plots from Phase 3

1. **S₈ forest plot** — Compare ΛCDM, EDE with DES/KiDS/HSC bands
2. **Growth factor D(z)** — Show suppression matches lensing surveys

---

## Priority Ranking (If Compute Limited)

**Non-negotiable:**
1. ΛCDM vs EDE in DESI+Pantheon (World B) — geometry story
2. ΛCDM vs EDE in DES Y3 (World D) — growth story
3. ΛCDM vs EDE in ACT (World C) — soft shoulder consistency

**Nice to have:**
4. CPL in DESI+Pantheon — equal-k fairness
5. CPL in DES Y3 — S₈ comparison
6. DESI-only world (World A) — intermediate check

---

## Launch Commands

### Phase 1: DESI Y1 + Pantheon+
```bash
ssh <VM_USER>@<VM_IP> "cd ~/Ridder-Field/phase3 && bash launch_tier5_phase1.sh"
```

### Monitor Progress
```bash
ssh <VM_USER>@<VM_IP> "cd ~/Ridder-Field/phase3 && python3 tier5_phase1_status.py"
```

---

## Timeline Estimate

| Phase | Chains | Est. Time | Status |
|-------|--------|-----------|--------|
| Phase 1a (DESI only) | 9 | 12-24 hrs | Ready |
| Phase 1b (+ Pantheon) | 9 | 12-24 hrs | Ready |
| Phase 2 (ACT) | 6-9 | 24-48 hrs | Configs needed |
| Phase 3 (DES) | 6-9 | 24-48 hrs | Configs needed |

**Total:** ~4-6 days of VM compute for publication-quality Tier 5

---

## What This Proves in the Paper

Once complete, Tier 5 establishes:

1. **DESI + Pantheon+:** The implied r_s shift and late-time H(z) are consistent with the latest distance data

2. **ACT DR6:** The soft shoulder does not conflict with high-ℓ CMB damping tail measurements

3. **DES Y3:** The model's growth suppression naturally lands in the lensing-preferred S₈ band

**Key message:** Geometric EDE sits on the Pareto front across ALL major modern datasets, not just Planck+BAO+SH0ES.

---

## Archived: Phase 0 (SH0ES/TRGB + DESI Stress Tests)

**Status:** ✅ Complete, archived to `TIER5_SHOES_DESI_ARCHIVE.md`

**Verdict:** SH0ES EDE dead (Δχ²=+165), TRGB EDE costly (Δχ²=+58)

**Paper use:** One paragraph in §VIII + Table A1 in Appendix
