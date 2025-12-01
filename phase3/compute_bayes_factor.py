#!/usr/bin/env python3
"""
Compute Bayes Factor for EDE vs ΛCDM using ACT high-ℓ data
==========================================================

Uses the template amplitude fit result: A_sh = 1.16 ± 0.18

Model comparison:
- M0 (ΛCDM): A_sh = 0 (no shoulder)
- M1 (EDE):  A_sh free, prediction A_sh = 1

Methods:
1. Likelihood ratio / χ² difference
2. Savage-Dickey density ratio
3. BIC approximation
"""

import numpy as np
from scipy import stats
from scipy.special import erfc

print("=" * 70)
print("BAYES FACTOR: EDE vs ΛCDM (ACT high-ℓ)")
print("=" * 70)

# Template fit results
A_sh = 1.16
sigma_A = 0.18
N_data = 1651  # ACT bandpowers

print(f"\nTemplate fit result: A_sh = {A_sh:.3f} ± {sigma_A:.3f}")
print(f"Number of ACT bandpowers: {N_data}")

# ============================================================
# METHOD 1: χ² difference (likelihood ratio)
# ============================================================
print("\n" + "-" * 70)
print("METHOD 1: χ² / Likelihood Ratio")
print("-" * 70)

# χ² for ΛCDM (A_sh = 0)
chi2_lcdm = (A_sh / sigma_A) ** 2
print(f"  χ²(ΛCDM, A_sh=0) = ({A_sh}/{sigma_A})² = {chi2_lcdm:.2f}")

# χ² for best-fit EDE (A_sh = A_hat)
chi2_ede = 0  # By definition, best-fit has χ² = 0 in the A_sh direction
print(f"  χ²(EDE, A_sh=best) = 0 (by definition)")

# Δχ² = χ²(ΛCDM) - χ²(EDE)
delta_chi2 = chi2_lcdm - chi2_ede
print(f"  Δχ² = {delta_chi2:.2f}")

# Convert to likelihood ratio
# L(EDE)/L(ΛCDM) = exp(-Δχ²/2)
# But we want L(M1)/L(M0) where M0 is ΛCDM
likelihood_ratio = np.exp(delta_chi2 / 2)
print(f"  Likelihood ratio L(EDE)/L(ΛCDM) = exp({delta_chi2:.1f}/2) = {likelihood_ratio:.2e}")

# p-value for ΛCDM
p_value = 1 - stats.chi2.cdf(chi2_lcdm, df=1)
significance = stats.norm.isf(p_value / 2)  # Two-sided
print(f"  p-value for ΛCDM: {p_value:.2e}")
print(f"  Significance: {significance:.1f}σ")

# ============================================================
# METHOD 2: Savage-Dickey Density Ratio
# ============================================================
print("\n" + "-" * 70)
print("METHOD 2: Savage-Dickey Density Ratio")
print("-" * 70)

# For nested models: BF_01 = π(θ₀|M1) / P(θ₀|D,M1)
# Where θ₀ is the nested value (A_sh = 0 for ΛCDM)

# Assume flat prior on A_sh in [-5, 5] (width = 10)
prior_width = 10.0
prior_at_zero = 1.0 / prior_width
print(f"  Prior: Flat on A_sh ∈ [-5, 5], π(0) = {prior_at_zero:.3f}")

# Posterior at A_sh = 0 (Gaussian with mean A_sh, std sigma_A)
posterior_at_zero = stats.norm.pdf(0, loc=A_sh, scale=sigma_A)
print(f"  Posterior: N({A_sh:.3f}, {sigma_A:.3f}), P(0|D) = {posterior_at_zero:.6e}")

# Savage-Dickey ratio: BF_01 = π(0)/P(0|D)
# This gives evidence for M0 (ΛCDM) vs M1 (EDE)
BF_01_SD = prior_at_zero / posterior_at_zero
BF_10_SD = 1 / BF_01_SD  # Evidence for EDE vs ΛCDM
print(f"  BF(ΛCDM/EDE) = {BF_01_SD:.2e}")
print(f"  BF(EDE/ΛCDM) = {BF_10_SD:.2e}")

# ============================================================
# METHOD 3: BIC Approximation
# ============================================================
print("\n" + "-" * 70)
print("METHOD 3: BIC Approximation")
print("-" * 70)

# BIC = χ² + k*ln(N)
# ΔBIC = Δχ² - Δk*ln(N)  (EDE has 1 extra parameter)
k_diff = 1  # EDE has one more parameter (A_sh)
delta_BIC = -delta_chi2 + k_diff * np.log(N_data)
print(f"  ΔBIC = -Δχ² + Δk*ln(N) = -{delta_chi2:.1f} + {k_diff}*ln({N_data})")
print(f"  ΔBIC = {delta_BIC:.2f}")

# BF ≈ exp(-ΔBIC/2)
# Positive ΔBIC favors simpler model (ΛCDM)
# Negative ΔBIC favors complex model (EDE)
BF_BIC = np.exp(-delta_BIC / 2)
print(f"  BF(EDE/ΛCDM) ≈ exp(-ΔBIC/2) = {BF_BIC:.2e}")

# ============================================================
# METHOD 4: AIC Approximation
# ============================================================
print("\n" + "-" * 70)
print("METHOD 4: AIC Approximation")
print("-" * 70)

# AIC = χ² + 2k
# ΔAIC = Δχ² - 2*Δk
delta_AIC = -delta_chi2 + 2 * k_diff
print(f"  ΔAIC = -Δχ² + 2*Δk = -{delta_chi2:.1f} + 2*{k_diff}")
print(f"  ΔAIC = {delta_AIC:.2f}")

# Akaike weight ratio
AIC_weight_ratio = np.exp(-delta_AIC / 2)
print(f"  Akaike weight ratio (EDE/ΛCDM) = {AIC_weight_ratio:.2e}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY: Bayes Factor for EDE vs ΛCDM")
print("=" * 70)

print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│  Method                          │  BF(EDE/ΛCDM)    │  Interpretation│
├─────────────────────────────────────────────────────────────────────┤
│  Likelihood ratio (χ² diff)      │  {likelihood_ratio:12.2e}  │  VERY STRONG   │
│  Savage-Dickey (flat prior)      │  {BF_10_SD:12.2e}  │  VERY STRONG   │
│  BIC approximation               │  {BF_BIC:12.2e}  │  {'STRONG' if BF_BIC > 10 else 'MODERATE'}       │
│  AIC approximation               │  {AIC_weight_ratio:12.2e}  │  VERY STRONG   │
└─────────────────────────────────────────────────────────────────────┘
""")

# Interpretation scale (Kass & Raftery 1995)
print("Interpretation scale (Kass & Raftery 1995):")
print("  BF < 1:      Evidence against EDE")
print("  1 < BF < 3:  Not worth more than a bare mention")
print("  3 < BF < 10: Positive evidence")
print("  10 < BF < 30: Strong evidence")
print("  30 < BF < 100: Very strong evidence")
print("  BF > 100:    Decisive evidence")

print("\n" + "-" * 70)
print("VERDICT")
print("-" * 70)

# Use the most conservative estimate (BIC, which penalizes extra parameters)
if BF_BIC > 100:
    verdict = "DECISIVE"
elif BF_BIC > 30:
    verdict = "VERY STRONG"
elif BF_BIC > 10:
    verdict = "STRONG"
elif BF_BIC > 3:
    verdict = "POSITIVE"
else:
    verdict = "WEAK"

print(f"""
Using the most conservative method (BIC):
  
  BF(EDE/ΛCDM) = {BF_BIC:.1f}
  
  ➜ {verdict} EVIDENCE for EDE over ΛCDM in ACT high-ℓ data

Key numbers:
  • Δχ² = {delta_chi2:.1f} (EDE improves fit by {delta_chi2:.1f} in χ²)
  • This costs 1 extra parameter
  • Net: ΔBIC = {delta_BIC:.1f} (negative = favors EDE)
  • Significance: {significance:.1f}σ rejection of ΛCDM
""")

# Consistency check with Ridder prediction
print("-" * 70)
print("CONSISTENCY WITH RIDDER PREDICTION")
print("-" * 70)

# Test A_sh = 1 (Ridder prediction)
chi2_ridder = ((A_sh - 1.0) / sigma_A) ** 2
p_ridder = 1 - stats.chi2.cdf(chi2_ridder, df=1)
print(f"  A_sh = {A_sh:.3f}, Ridder predicts A_sh = 1.0")
print(f"  Deviation: ({A_sh:.3f} - 1.0) / {sigma_A:.3f} = {(A_sh-1)/sigma_A:.2f}σ")
print(f"  χ²(Ridder) = {chi2_ridder:.2f}")
print(f"  p-value: {p_ridder:.3f}")
print(f"  ➜ Ridder prediction is CONSISTENT with data ({(A_sh-1)/sigma_A:.1f}σ)")
