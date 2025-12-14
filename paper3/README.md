# Paper 3: Unified Ridder Field - WINNING CONFIGURATION

## Results Summary (2024-12-14)

**Δχ² = -18.33** (xi_late model beats ΛCDM)

| Metric | xi_late | ΛCDM | Delta |
|--------|---------|------|-------|
| Total χ² | 3827.17 | 3845.50 | **-18.33** |
| H₀ | 69.73 | 69.05 | +0.68 |
| w₀ | -1.01 | -1.0 | phantom |
| S₈ | ~0.82 | ~0.87 | -0.05 |

### Per-Likelihood Breakdown
```
chi2__planck_2018_highl_plik.TTTEEE:  -18.24  ← THE WIN
chi2__sn.pantheon:                    +0.39   (neutral)
chi2__bao.desi_2024_bao_all:          +0.14   (neutral)
chi2__planck_2018_lowl.EE:            -0.33   
chi2__planck_2018_lensing.clik:       -0.29   
```

## Key Physics

1. **xi_late = 0.05**: Late-time DM-DE coupling reduces Ω_m at z<10
2. **w₀ = -1.01**: Very mild phantom lifts H₀ while keeping DESI happy
3. **H(z) crosses ΛCDM at z~0.5**: Explains why DESI BAO is neutral

## Files

- `configs/`: Cobaya YAML configurations for both chains
- `scripts/`: Validation and analysis scripts
- `class_mods/`: Modified CLASS source files with xi_late implementation
- `SYSTEMATIC_SEARCHES_PLAN.md`: Full validation protocol

## Running the Chains

```bash
# On VM with modified CLASS installed
cd ~/ridder_v2/late_time
cobaya-run xi_late_desi_v3.yaml -f
cobaya-run lcdm_desi_v3.yaml -f
```

## Validation

```bash
python3 ~/audit_chains.py \
  ~/ridder_v2/late_time/chains/lcdm_desi_v3.1.txt \
  ~/ridder_v2/late_time/chains/xi_late_desi_v3.1.txt \
  --burn 0.30 --tail 0.50
```
