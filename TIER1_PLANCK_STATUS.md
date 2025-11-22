# Tier 1 Planck MCMC Status Report
**Generated:** 2025-11-22 04:20 UTC  
**Runtime:** ~27 minutes  
**Config:** `ridder_tier1_planck.yaml`

---

## Executive Summary

✅ **MCMC is running successfully**  
- Process active (PID: 131216)
- Using 4 CPU cores (392% CPU usage)
- Memory: 1.9%
- Log file: 51MB and growing

---

## Progress

- **Samples collected:** 83
- **Target:** 400 max_samples
- **Progress:** 20.8% complete
- **Chain file:** `output/tier1_planck.1.txt` (58KB)

---

## Parameter Exploration

### Cosmological Parameters (last 10 samples)
| Parameter | Mean | Std | Range |
|-----------|------|-----|-------|
| `logA` | 3.0521 | 0.0041 | [3.0447, 3.0574] |
| `n_s` | 0.9589 | 0.0008 | [0.9575, 0.9601] |
| `H0` | 67.78 | 0.06 | [67.69, 67.85] |
| `omega_b` | 0.0224 | 0.0000 | [0.0224, 0.0224] |
| `omega_cdm` | 0.1211 | 0.0002 | [0.1208, 0.1213] |
| `tau_reio` | 0.0584 | 0.0022 | [0.0550, 0.0618] |

### Ridder Field Parameters (last 10 samples)
| Parameter | Mean | Std | Range |
|-----------|------|-----|-------|
| `theta_i_ridder` | 0.489 | 0.021 | [0.465, 0.541] |
| `beta_ridder` | 0.0080 | 0.0009 | [0.0064, 0.0091] |

**Key Observations:**
- `theta_i_ridder` is exploring around **0.49** (well below the prior max of 2.3)
- `beta_ridder` is small but non-zero (**~0.008**)
- Standard cosmological parameters are in reasonable ranges
- `H0` is around **67.8 km/s/Mpc** (Planck-like, not elevated)

---

## Likelihood Performance

- **Best χ²:** 2778.01
- **Current χ²:** 2787.86
- **Mean χ² (last 10):** 2789.90

**Likelihood breakdown (from chain):**
- `planck_2018_lowl.TT`: ~24
- `planck_2018_lowl.EE`: ~396
- `planck_2018_highl_plik.TTTEEE`: ~2350-2400
- `planck_2018_lensing.clik`: ~8-9

---

## Sampler Behavior

- **Method:** MCMC with drag sampler (enabled)
- **Proposal:** Auto-learned covariance matrix
- **Acceptance pattern:** Many dragging steps are being accepted/rejected, but overall chain is progressing
- **Total weight:** 391 (across 83 samples)
- **Mean weight per sample:** 4.71
- **Max weight:** 18

---

## Issues/Warnings

⚠️ **One error detected:**
- `[classy] No (compiled) installation of 'classy'` - This appears to be an initialization warning, but the process continues and CLASS is being called successfully (evidenced by likelihood evaluations)

---

## What's Happening

1. **Sampler is exploring parameter space** - Parameters are moving around their reference values
2. **Likelihoods are being computed** - Planck likelihoods are evaluating successfully
3. **Chain is building** - 83 samples collected, averaging ~3.2 samples/minute
4. **No convergence yet** - Still in early exploration phase (20% of target)

---

## Expected Completion

At current rate (~3.2 samples/minute):
- **Time to 400 samples:** ~100 minutes total (73 minutes remaining)
- **Estimated completion:** ~05:30 UTC

---

## Files Generated

- `output/tier1_planck.1.txt` - Main chain file (58KB, 83 samples)
- `output/tier1_planck.log` - Full log (51MB)
- `output/tier1_planck.checkpoint` - Checkpoint file
- `output/tier1_planck.updated.yaml` - Updated config with learned proposal
- `output/tier1_planck.input.yaml` - Input config snapshot

---

## Next Steps

1. **Continue monitoring** - Run `./scripts/check_status.sh` periodically
2. **Wait for completion** - Let it run to 400 samples
3. **Analyze results** - Use `plot_results.py` or GetDist to analyze chains
4. **Check convergence** - Look for R-1 < 0.05 (target in config)

---

## Quick Commands

```bash
# Check status
cd ~/Ridder-Field/phase3
./scripts/check_status.sh ridder_tier1_planck tier1_planck

# Watch log
tail -f output/tier1_planck/log.txt

# Check chain
wc -l output/tier1_planck.1.txt
tail -5 output/tier1_planck.1.txt
```

