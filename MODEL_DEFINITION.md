# Ridder Unified Model: Frozen Definition

## 1. The Model (FIXED - do not touch)

### Potential Form
```
V(θ) = V_tail(θ) + V_shelf(θ)

V_tail = Λ_tail⁴ × [1 + α × (1 - cos θ)^n_tail]
V_shelf = Λ_EDE⁴ × W(θ) × (1 - cos θ)^n_shelf
```

### Fixed Parameters (constants of the theory)
| Parameter | Value | Reason |
|-----------|-------|--------|
| n_tail | 1.0 | Simplest shape |
| n_shelf | 3.0 | Standard EDE |
| α_tail | 1.0 | Simplest tail |
| θ_i | 2.5 | Initial angle |
| θ_EDE_low | 0.5 | Shelf window |
| θ_EDE_high | 3.5 | Shelf window |
| σ_EDE | 0.5 | Shelf smoothness |
| m_axion | 7×10⁴ | Mass parameter |
| ridder_f | 7.305×10²⁶ | Decay constant |
| ridder_c_slow | 0.0 | Frozen IC |
| β_ridder | 0.0 | No CDM coupling |

### Free Parameters (the 2D space we explore)
| Parameter | Range | Physics |
|-----------|-------|---------|
| Λ_tail | 15-35 meV | Late-time DE scale |
| f_axion | 0.15-0.45 | EDE amplitude |

---

## 2. Hard Constraints (must be satisfied)

| Constraint | Threshold | Source |
|------------|-----------|--------|
| f_EDE | 0.05 ≤ f_EDE ≤ 0.20 | Standard EDE literature |
| CMB TT RMS (ℓ=30-2000) | ≤ 20% | Planck precision |
| BAO D_V fractional | ≤ 3% at z=0.35, 0.57 | BOSS/eBOSS |
| z_peak | 2000 ≤ z_peak ≤ 5000 | EDE timing |

---

## 3. Target Observables

| Observable | ΛCDM | Target | Source |
|------------|------|--------|--------|
| H₀ | 67.36 | ≥70.5 | SH0ES tension |
| S₈ | 0.834 | ≤0.78 | KiDS/DES tension |

---

## 4. χ² Definition

```
χ²_total = χ²_H0 + χ²_S8 + χ²_BAO + χ²_CMB

χ²_H0 = [(H0 - 73.04) / 1.04]²     # SH0ES prior
χ²_S8 = [(S8 - 0.766) / 0.020]²   # KiDS-1000
χ²_BAO = Σ [(D_V - D_V_data) / σ_D]²
χ²_CMB = (RMS_TT / 0.05)²         # Rough proxy
```

---

## 5. Classification of Points

- **VIABLE**: All constraints satisfied AND (H0 > 70.5 OR S8 < 0.78)
- **NEAR-MISS**: One constraint violated by < 50%
- **EXCLUDED**: Any constraint violated by > 50%

---

## Date: 2024-11-25
## Commit: [current HEAD]

