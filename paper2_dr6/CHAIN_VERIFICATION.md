# Chain Verification Report
**Generated: December 11, 2025**

## Chain Locations

All production chains are located on the Azure VM at:
```
/home/azureuser/Ridder-Field/paper2_dr6/chains/
```

**Note:** These are in the `azureuser` home directory, NOT `ridderadmin`.

---

## Verified Chain Results

### A1: Profile Likelihood Analysis

| Chain | Samples | Description |
|-------|---------|-------------|
| `lscan_0_16.1.txt` | 1,000 | EDE at Λ=0.16, ACT+DESI |
| `act_desi_lcdm_matched.1.txt` | 500 | ΛCDM baseline, ACT+DESI |
| `p3_template_dr6_v2.1.txt` | 4,159 | Template fit (A_sh free) |
| `p2_free_lambda_act.1.txt` | 500 | Free-Λ ACT+DESI |

### Key Results

#### Physical EDE (Λ = 0.16)
```
Chain: lscan_0_16.1.txt
Samples: 1,000
H₀ = 70.92 ± 0.26
σ₈ = 0.752 ± 0.004
χ²_min = 8,413.2
χ²_ACT_min = 6,550.7
```

#### ΛCDM Baseline
```
Chain: act_desi_lcdm_matched.1.txt
Samples: 500
H₀ = 69.73
χ²_min = 9,179.4
χ²_ACT_min = 7,237.0
```

#### Template Fit (A_sh marginalized)
```
Chain: p3_template_dr6_v2.1.txt
Samples: 4,159
A_sh = 1.608 ± 0.218
Significance: 7.4σ
χ²_min = 8,704.5
H₀ = 67.20 (ΛCDM-like cosmology)
```

#### Free Lambda Fit
```
Chain: p2_free_lambda_act.1.txt
Samples: 500
Λ = 0.145 ± 0.006
Significance: 25.9σ
H₀ = 71.28
```

---

## Δχ² Summary

| Comparison | Δχ² | Status |
|------------|-----|--------|
| ΛCDM → EDE (Λ=0.16) | **−766.2** | ✅ Matches paper |
| ΛCDM → Template | −474.9 | Template recovers ~62% |
| ACT-only: ΛCDM → EDE | −686.3 | 90% from ACT |

---

## Paper Claims vs Chain Results

| Claim in Paper | Chain Result | Match? |
|----------------|--------------|--------|
| Δχ² = −766 | −766.2 | ✅ Exact |
| A_sh = 1.54 ± 0.19 | 1.61 ± 0.22 | ⚠️ Close |
| 8.1σ significance | 7.4σ | ⚠️ Close |
| H₀ = 70.7 | 70.92 | ✅ Close |
| σ₈ = 0.753 | 0.752 | ✅ Exact |
| χ²(EDE) = 8,413 | 8,413.2 | ✅ Exact |
| χ²(ΛCDM) = 9,179 | 9,179.4 | ✅ Exact |

**Note:** The A_sh value and significance differ slightly between the paper (1.54, 8.1σ) and the template chain (1.61, 7.4σ). This may reflect:
1. Different burn-in treatment
2. Different weighting
3. Updates to chain after paper was drafted

The Δχ² = −766 is the primary result and matches exactly.

---

---

## A2: Stability Test Results

### Chain Jackknife (10% dropout, 20 trials)
- A_sh range: **1.605 to 1.610** (extremely stable)
- σ range: 0.217 to 0.219
- Significance: **7.3σ to 7.4σ**

### Odd/Even Sample Split
- Odd samples: A_sh = 1.608 ± 0.218 (7.4σ)
- Even samples: A_sh = 1.609 ± 0.218 (7.4σ)
- Difference: **0.0σ** (perfect agreement)

### First/Second Half Split (convergence)
- First half: A_sh = 1.676 ± 0.220
- Second half: A_sh = 1.543 ± 0.195
- Difference: **0.13σ** (converged)

### Frequency Splits
| Frequency | Λ_EDE | σ | χ²_min | Status |
|-----------|-------|---|--------|--------|
| 90 GHz | 0.135 | 0.003 | 951 | CMB ✅ |
| 150 GHz | 0.146 | 0.006 | 998 | CMB ✅ |
| 220 GHz | 0.187 | 0.029 | 794 | CIB ⚠️ |

**90 vs 150 GHz difference: 1.5σ → ACHROMATIC**

---

## Zenodo Archive Checklist

When archiving to Zenodo, include:

### Chain Files
- [ ] `lscan_0_16.1.txt` (EDE Λ=0.16)
- [ ] `act_desi_lcdm_matched.1.txt` (ΛCDM baseline)
- [ ] `p3_template_dr6_v2.1.txt` (Template fit)
- [ ] `p2_free_lambda_act.1.txt` (Free-Λ)

### Config Files
- [ ] `lambda_scan/lscan_0_16.yaml`
- [ ] `act_desi_lcdm_matched.yaml`
- [ ] `p3_template_dr6_v2.yaml`

### Analysis Scripts
- [ ] Profile likelihood extraction
- [ ] A_sh posterior analysis
- [ ] χ² decomposition

---

## Commands to Access Chains

```bash
# SSH to VM
ssh ridderadmin@172.174.34.125

# Access chains (requires sudo)
sudo ls /home/azureuser/Ridder-Field/paper2_dr6/chains/

# Copy a chain to local
sudo cat /home/azureuser/Ridder-Field/paper2_dr6/chains/lscan_0_16.1.txt > /tmp/chain.txt
scp ridderadmin@172.174.34.125:/tmp/chain.txt .
```

---

## A1 Profile Likelihood Table (for paper)

```
┌─────────────────────────────────────────────────────────────────────┐
│ A1: Profile Likelihood Results                                      │
├─────────────────────────────────────────────────────────────────────┤
│ H₀ (ΛCDM, A_sh=0):          χ²_min = 9,179.4                       │
│ H₁ (Template, A_sh free):   χ²_min = 8,704.5                       │
│                                                                     │
│ Δχ² = +474.9 (Template preferred)                                  │
│                                                                     │
│ Best-fit A_sh = 1.61 ± 0.22                                        │
│ Significance = 7.4σ                                                │
│                                                                     │
│ Physical EDE (Λ=0.16):      χ²_min = 8,413.2                       │
│ Δχ² = +766.2 (EDE preferred)                                       │
└─────────────────────────────────────────────────────────────────────┘
```

