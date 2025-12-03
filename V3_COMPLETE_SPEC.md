# V3 Canonical Model - Complete Specification

**Date:** 2025-11-25  
**Status:** Implementation in progress

---

## 1. Mathematical Form

### Field Definition
```
θ ≡ φ / f
```
where `f` is a fixed decay constant in eV.

### Total Potential
```
V(φ, a) = V_Λ + V_EDE(θ, a) + V_tail(θ)
```

---

## 1.1 Cosmological Constant Floor

```
V_Λ = Λ_floor⁴
```

Choose `Λ_floor` to reproduce Planck ΛCDM background when EDE and tail are off.

---

## 1.2 EDE "Shelf" Term

Localized bump in both time and field space:

```
V_EDE(θ, a) = Λ_EDE⁴ · S(a; a_c, σ_ln a) · B(θ; θ_E, n_EDE)
```

**Time Window (Gaussian in log scale):**
```
S(a; a_c, σ_ln a) = exp[-(ln a - ln a_c)² / (2σ²_ln a)]
```
- `a_c`: Central scale factor (z_c = 1/a_c - 1)
- `σ_ln a`: Width of EDE episode in log scale

**Field Bump (Cosine-based):**
```
B(θ; θ_E, n_EDE) = [1 - cos(θ - θ_E)]^n_EDE
```
- `θ_E`: Field value during EDE episode
- `n_EDE`: Sharpness (larger = more peaked)

**EDE Parameters:**
- `Λ_EDE` [eV]: Amplitude
- `a_c` or `z_c`: Central redshift
- `σ_ln a`: Temporal width
- `θ_E`: Field center
- `n_EDE`: Power

**Diagnostics:**
```
f_EDE ≡ max_a [ρ_φ(a) / ρ_tot(a)]
z_peak: where maximum occurs
```

---

## 1.3 Tail Term

Late-time quintessence-like deformation:

```
V_tail(θ) = Λ_tail⁴ · [1 + α_tail · (1 - cos θ)^n_tail]
```

At `θ = 0`: `V_tail = Λ_tail⁴` (nonzero minimum)

**Tail Parameters:**
- `Λ_tail` [eV]: Energy scale
- `α_tail`: Modulation strength (dimensionless)
- `n_tail`: Power
- `θ_ini`: Initial field value

**V3 Base:** Set CDM coupling `β = 0` (coupling is future experiment)

---

## 2. Button API / JSON Contract

### 2.1 Command Line

```bash
python3 run_unified_model.py \
  --Lambda_EDE_eV 0.0015 \
  --a_c 3.3e-4 \
  --sigma_lna 0.3 \
  --theta_E 2.6 \
  --n_EDE 3 \
  --Lambda_tail_eV 0.0016 \
  --alpha_tail 1.0 \
  --n_tail 1 \
  --theta_ini 0.5 \
  --mode full
```

**Modes:**
- `quick`: Background + H0, S8, f_EDE, z_peak only
- `full`: Add power spectra, CMB/BAO residuals, plots

**Presets:**
```bash
python3 run_unified_model.py --preset unified_compromise_v3 --mode full
```

---

### 2.2 JSON Schema

```json
{
  "model_params": {
    "Lambda_EDE_eV": 0.0015,
    "a_c": 0.00033,
    "sigma_lna": 0.3,
    "theta_E": 2.6,
    "n_EDE": 3,
    "Lambda_tail_eV": 0.0016,
    "alpha_tail": 1.0,
    "n_tail": 1,
    "theta_ini": 0.5,
    "f_eV": 1.0e26
  },
  "primary_observables": {
    "H0": 71.2,
    "sigma8": 0.80,
    "S8": 0.76,
    "Omega_m": 0.28,
    "Omega_L": 0.72,
    "age_Gyr": 13.4
  },
  "ede_diagnostics": {
    "f_EDE_peak": 0.14,
    "z_peak": 3700.0,
    "rs_Mpc": 144.0,
    "rs_drag_Mpc": 147.0
  },
  "tail_diagnostics": {
    "Omega_ridder_z0": 0.06,
    "w_z0": -0.995,
    "w_z1": -0.993,
    "w_z2": -0.990
  },
  "bao_residuals": {
    "0.35": -0.035,
    "0.57": -0.042
  },
  "cmb_residuals": {
    "rms_lowL": 0.10,
    "rms_midL": 0.12,
    "rms_highL": 0.15,
    "max_abs": 0.24
  },
  "chi2": {
    "chi2_total": 21.5,
    "chi2_H0": 2.0,
    "chi2_S8": 0.8,
    "chi2_BAO": 4.5,
    "chi2_CMB": 14.2,
    "delta_chi2_vs_LCDM": -8.3
  },
  "meta": {
    "lcdm_reference": "lcdm_planck2018",
    "class_version": "ridder_v3",
    "run_id": "v3_scan_0017",
    "timestamp_utc": "2025-11-24T12:34:56Z",
    "mode": "full"
  }
}
```

---

## 3. First V3 Scan vs V1

### 3.1 Fix Tail (Conservative Track 2 Values)

```
Λ_tail = 1.6e-3 eV
α_tail = 1.0
n_tail = 1
θ_ini = 0.5
```

These gave H0 ~ 73, S8 ~ 0.75 in Track 2.

### 3.2 Scan EDE Parameters

**Grid (4 × 3 × 2 = 24 points):**
- `Λ_EDE ∈ {0.0008, 0.0012, 0.0016, 0.0020}` eV
- `z_c ∈ {2500, 3500, 4500}` → `a_c = 1/(1+z_c)`
- `σ_ln a ∈ {0.2, 0.3}`
- Fixed: `θ_E = 2.6`, `n_EDE = 3`

**For each point:**
1. Write `.ini` with v3 parameters
2. Run `run_unified_model.py --mode quick`
3. Get JSON, compute χ²
4. Record: H0, S8, f_EDE, z_peak, BAO, CMB, χ²

### 3.3 Selection Criteria (Same as V1)

**"Interesting v3 candidate" requires:**
- `0.05 ≤ f_EDE_peak ≤ 0.20`
- `2000 ≤ z_peak ≤ 5000`
- `H0 ≥ 70`
- `S8 ≤ 0.78`
- CMB RMS ≤ 20%
- BAO residuals ≤ 5%
- `Δχ² vs ΛCDM < 0`

**Comparison to V1:**
- If any v3 point meets criteria AND has better Δχ² than best v1: **"v3 beats v1"**
- If none meet criteria: **"v3 shape did not cure trade-off"**

**Key:** Same likelihood, same χ², same button. Only potential shape changes.

---

## 4. Implementation Checklist

- [ ] Update `ridder_v3_potential.c` with time-windowed EDE
- [ ] Add `ridder_model_v3_canon` to enum and input parser
- [ ] Update button `run_unified_model.py` for new CLI
- [ ] Implement full JSON schema
- [ ] Create `v3_first_scan.py` for 24-point grid
- [ ] Reuse `compute_chi2.py` from v1
- [ ] Test one point end-to-end
- [ ] Run full 24-point scan
- [ ] Compare to v1 smoke test results
- [ ] Document outcome

---

## 5. V3 vs V1 Key Differences

| Feature | V1 | V3 |
|---------|----|----|
| EDE time window | Gaussian in θ | Gaussian in ln(a) |
| EDE field shape | [1-cos(θ)]^n with tanh edges | [1-cos(θ-θ_E)]^n, centered |
| Tail | Same form | Same form |
| Parameters scanned | (Λ_tail, f_axion) | (Λ_EDE, z_c, σ_ln a) |
| Free parameters | 2 | 5 (but tail fixed for first scan) |
| Result | EXCLUDED | TBD |

---

**Next:** Implement time-windowed EDE, fix input parser, run 24-point scan.

