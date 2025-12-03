# Tier 5 Strategy: Modern Dataset Validation

## Overview

Tier 5 datasets answer three questions:
1. **Geometric shift**: Is the ~1% r_s reduction consistent with DESI BAO?
2. **High-ℓ CMB**: Does the model remain consistent with damping tail (ACT DR6)?
3. **Growth suppression**: Does S8 suppression align with weak lensing (DES Y3)?

---

## Phase 1: DESI Y1 BAO + Pantheon+ (Essential)

### What We Test

**DESI Y1 BAO**
- Constrains D_M(z)/r_s, H(z)r_s at multiple redshifts
- Question: Is ~1% r_s reduction consistent with DESI distances?
- Look for: r_s sitting ~1% below ΛCDM with overlapping errors

**Pantheon+**
- Constrains relative D_L(z) from z~0.01 to z~2
- Question: Does late-time H(z) pass SN residuals test?
- Look for: Residuals μ_model - μ_ΛCDM at ≲0.02 mag level

### Chains Needed

| World | ΛCDM | CPL | EDE | Purpose |
|-------|------|-----|-----|---------|
| Planck + BAO + DESI | ✅ | ✅ | ✅ | Core DESI test |
| Planck + BAO + DESI + Pantheon+ | ✅ | ✅ | ✅ | Full distance ladder |

**Samples**: 4 chains × N~1000, R-1 < 0.01, ESS > 2000

### Plots to Generate

1. **Sound horizon comparison**: Posterior for r_s across models
2. **H(z) and w(z)**: Show CPL uses late-time freedom, EDE uses geometry
3. **SN residuals**: Δμ(z) for each model vs best-fit ΛCDM

---

## Phase 2: ACT DR6 (Damping Tail)

### What We Test

- High-ℓ TT/EE at ℓ > 1000
- Sensitivity to phase shifts from EDE shoulder at z~3000
- Question: Does EDE remain consistent with damping tail?

### Chains Needed

| World | ΛCDM | CPL | EDE | Purpose |
|-------|------|-----|-----|---------|
| Planck + BAO + SH0ES + ACT DR6 | ✅ | ✅ | ✅ | Shoulder hunt |

**Samples**: Same as Phase 1

### Plots to Generate

1. **Residual power spectra**: ΔC_ℓ/C_ℓ^ΛCDM for ℓ~600-3000
2. **Phase shift diagnostic**: Oscillations indicating acoustic phase shift
3. **Statement**: "Consistent with current data, motivates CMB-S4"

---

## Phase 3: DES Y3 (S8 Confirmation)

### What We Test

- 3x2pt: lensing + clustering at z < 1
- S8 = σ8(Ω_m/0.3)^0.5
- Question: Does EDE's S8~0.79 overlap DES better than ΛCDM's S8~0.83?

### Chains Needed

| World | ΛCDM | CPL | EDE | Purpose |
|-------|------|-----|-----|---------|
| Planck + BAO + SH0ES + DES Y3 | ✅ | ✅ | ✅ | Growth test |

**Samples**: Same as Phase 1

### Plots to Generate

1. **S8 forest plot**: All models vs DES/KiDS/HSC bands
2. **Growth factor**: σ8(z) or fσ8(z) over 0 < z < 1

---

## "Nice to Have" (Appendix)

| Dataset | Use | Method |
|---------|-----|--------|
| KiDS-1000 | External S8 prior | Forest plot overlap |
| HSC Y3 | External S8 prior | Forest plot overlap |
| eBOSS Lyα | High-z BAO | Δχ² check |

---

## Paper Story

1. **Tier 10**: EDE sits on Pareto front at equal k
2. **Tier 5 DESI+Pantheon+**: r_s shift consistent with latest distances
3. **Tier 5 ACT**: No conflict with damping tail → CMB-S4 target
4. **Tier 5 DES Y3**: Growth suppression matches lensing

> "The geometric footprint of the shoulder in r_s, H(z), and the damping tail is consistent with the best current data. The growth footprint in S8 lines up with DES, KiDS, and HSC."

---

## Likelihood Availability

| Dataset | Cobaya Name | Status |
|---------|-------------|--------|
| DESI Y1 BAO | `bao.desi_2024_bao_all` | ✅ Ready |
| Pantheon+ | `sn.pantheonplus` | ✅ Ready |
| Pantheon+ w/ SH0ES | `sn.pantheonplusshoes` | ✅ Ready |
| ACT DR6 | `pyactlike` | ❌ Need install |
| DES Y3 3x2pt | External | ❌ Need setup |

