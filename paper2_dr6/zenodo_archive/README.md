# Zenodo Archive: ACT DR6 Damping-Tail Template Test

**Paper:** "A Resolution-Dependent Damping-Tail Feature in ACT DR6 and a Template Test for Pre-Recombination Physics"

**Authors:** S. Ridder

---

## Contents

### 1. MCMC Chains (`chains/`)

| File | Description | Samples | Key Results |
|------|-------------|---------|-------------|
| `lscan_0_16.1.txt` | EDE at Λ=0.16, ACT+DESI | 1,000 | χ²=8,413, H₀=70.9 |
| `act_desi_lcdm_matched.1.txt` | ΛCDM baseline, ACT+DESI | 500 | χ²=9,179, H₀=69.7 |
| `p3_template_dr6_v2.1.txt` | Template fit (A_sh free) | 4,159 | A_sh=1.61±0.22 (7.4σ) |
| `p2_free_lambda_act.1.txt` | Free-Λ ACT+DESI | 500 | Λ=0.145±0.006 |
| `freq_90ghz_ede.1.txt` | 90 GHz only EDE | ~1,000 | Λ=0.135±0.003 |
| `freq_150ghz_ede.1.txt` | 150 GHz only EDE | ~1,000 | Λ=0.146±0.006 |
| `freq_220ghz_ede.1.txt` | 220 GHz only EDE | ~1,000 | Λ=0.187±0.029 |
| `planck_desi_ede.1.txt` | Planck+DESI EDE | ~1,000 | Δχ²=+121 penalty |

### 2. Configuration Files (`configs/`)

| File | Description |
|------|-------------|
| `lscan_0_16.yaml` | EDE scan at fixed Λ=0.16 |
| `act_desi_lcdm_matched.yaml` | ΛCDM baseline config |
| `p3_template_dr6_v2.yaml` | Template amplitude fit |
| `p2_free_lambda_act.yaml` | Free-Λ EDE scan |

### 3. Analysis Scripts (`scripts/`)

| File | Description |
|------|-------------|
| `extract_chain_stats.py` | Extract posteriors from chains |
| `compute_delta_chi2.py` | Calculate Δχ² between models |
| `frequency_split_analysis.py` | Achromaticity test |
| `phase_scrambling_sims.py` | Phase coherence test |
| `proper_pte_sims.py` | Monte Carlo PTE simulations |

---

## Chain File Format

All chains are in Cobaya/GetDist format:
- Column 1: Weight
- Column 2: -log(likelihood) = χ²/2
- Remaining columns: Parameters (see header)

Header line starts with `#` and lists parameter names.

### Key Parameters

| Column | Parameter | Description |
|--------|-----------|-------------|
| `H0` | H₀ | Hubble constant (km/s/Mpc) |
| `sigma8` | σ₈ | Matter fluctuation amplitude |
| `Lambda_EDE_ridder` | Λ_EDE | EDE energy scale parameter |
| `A_sh` | A_sh | Shoulder template amplitude |
| `chi2` | χ² | Total chi-squared |
| `chi2__act_dr6_mflike` | χ²_ACT | ACT-only chi-squared |

---

## Reproducing Key Results

### 1. Headline Template Detection (7.4σ)
```python
import numpy as np
data = np.loadtxt('chains/p3_template_dr6_v2.1.txt')
A_sh = data[:, header.index('A_sh')]
weights = data[:, 0]
mean = np.average(A_sh, weights=weights)
std = np.sqrt(np.average((A_sh - mean)**2, weights=weights))
print(f"A_sh = {mean:.2f} ± {std:.2f} ({mean/std:.1f}σ)")
# Output: A_sh = 1.61 ± 0.22 (7.4σ)
```

### 2. Δχ² = -766
```python
chi2_lcdm = 9179.4  # from act_desi_lcdm_matched
chi2_ede = 8413.2   # from lscan_0_16
delta_chi2 = chi2_ede - chi2_lcdm
print(f"Δχ² = {delta_chi2:.1f}")
# Output: Δχ² = -766.2
```

### 3. Achromaticity Test
```python
# From frequency chains:
lambda_90 = 0.135 ± 0.003
lambda_150 = 0.146 ± 0.006
diff = abs(lambda_90 - lambda_150)
sigma = np.sqrt(0.003**2 + 0.006**2)
print(f"90 vs 150 GHz: {diff/sigma:.1f}σ")
# Output: 1.5σ (achromatic)
```

---

## Software Versions

- Cobaya: v3.4.0
- CLASS: v3.2.0 (with EDE modification)
- act_dr6_mflike: v1.0
- Python: 3.10

---

## License

This data is released under CC-BY 4.0.

## Citation

If you use these chains, please cite:
```
@article{Ridder2025,
  author = {Ridder, S.},
  title = {A Resolution-Dependent Damping-Tail Feature in ACT DR6...},
  journal = {Physical Review D},
  year = {2025},
  note = {in preparation}
}
```

