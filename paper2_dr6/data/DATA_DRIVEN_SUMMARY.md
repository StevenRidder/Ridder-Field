# Data-Driven Analysis Summary (CORRECTED)
## Computed on VM with Real ACT DR4 Data and CLASS

Date: Wed Dec 10 13:05:51 -10 2025

---

## 1. ACT DR4 TT Residuals vs Planck 2018 ΛCDM

### Correct Statistics:
- **Total bins**: 40 (ℓ = 600 to 4126)
- **Total Σ(D-M)/σ**: +3.5 → significance **+0.55σ** (no overall excess)
- **χ²**: 60.5 for 40 dof (χ²/dof = 1.51)

### Breakdown by ℓ Range:

| ℓ Range | Σ(D-M)/σ | Significance | Data/Model Ratio |
|---------|----------|--------------|------------------|
| 600-1000 | +3.6 | +1.3σ | 1.043 (4.3% above) |
| 1000-1500 | −2.9 | −0.9σ | 0.974 (2.6% below) |
| **1500-2000** | **+4.9** | **+1.6σ** | **1.012 (1.2% above)** |
| 2000-3000 | +3.1 | +1.1σ | 1.009 (0.9% above) |
| 3000-5000 | −5.3 | −2.6σ | 0.916 (8.4% below) |

### Notable Outlier Bins (|SNR| > 2):
- ℓ=1000: −2.37σ
- ℓ=1200: −2.35σ
- ℓ=1550: −2.77σ
- ℓ=1600: +2.50σ
- ℓ=1950: +2.52σ

### Key Finding:
**The soft shoulder region (ℓ=1500-2000) shows +1.6σ positive residual**
- This is mildly consistent with enhanced power in the damping tail
- But not statistically significant on its own

---

## 2. Previous Error Corrected

My earlier claim of −2.4σ mean residual was WRONG because:
1. I used inverse-variance weighted mean
2. This is dominated by high-ℓ bins with tiny errors
3. High-ℓ bins (>3000) are noise-dominated and show deficits

**Correct statistic**: Sum of (D-M)/σ = +3.5 for 40 bins → +0.55σ

---

## 3. CLASS Predictions: EDE-like (H0=71) vs ΛCDM (H0=67.4)

| ℓ Range | TT Change | EE Change |
|---------|-----------|-----------|
| 500-1000 | −2.55% | +5.34% |
| 1000-1500 | −0.69% | −2.62% |
| 1500-2000 | −4.07% | −0.79% |
| 2000-2500 | −6.49% | −4.01% |
| 2500-3000 | −6.36% | −8.45% |

### Lensing:
| L Range | C_L^φφ Change |
|---------|---------------|
| 100-500 | +13.5% |

### Parameters:
- σ8: 0.823 → 0.897 (+9.0%)

---

## 4. Revised Conclusions

1. **Soft shoulder region shows mild positive residual**: +1.6σ in ℓ=1500-2000
   - Consistent with excess power, but not significant
   
2. **High-ℓ tail shows deficit**: −2.6σ in ℓ>3000
   - Data falls off faster than Planck ΛCDM predicts
   
3. **Overall**: No significant total excess (+0.55σ)

4. **EDE theory issue remains**: 
   - EDE predicts LESS power in damping tail (not more)
   - EDE increases σ8 (worsens S8 tension)

---

## Files:
- `data_driven_residuals.txt` - Per-bin residual data
- `lensing_predictions.txt` - CLASS predictions
