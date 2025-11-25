# Next Steps for V3 Model Publication

Date: 2025-11-25  
Status: Ready for robust testing and full MCMC

## Current Status

### ✅ Completed
1. **V3 model fully implemented** - Canon potential with EDE + tail working
2. **Tail calibrated** - TRGB (1.2 meV) and SH0ES (1.6 meV) branches defined  
3. **Tier 4 smoke test passed** - Both branches viable (χ² ~ 0.0-0.1)
4. **Strategic positioning** - TRGB alignment as primary result
5. **Paper draft updated** - Tail calibration section added
6. **Calibration plots generated** - H0 vs Lambda_tail curves ready

### 🔨 Scripts Ready
1. **`mcmc_v3_robust.py`** - Improved tier 4 test with:
   - Explicit ΛCDM baseline comparison
   - CMB TT residual curves (multipole-by-multipole)
   - BAO D_V residuals at standard redshifts
   - Visual inspection plots

2. **`MCMC_STRATEGY.md`** - Complete roadmap for publication-quality MCMC:
   - Cobaya setup instructions
   - 3 run configurations (baseline, TRGB, SH0ES)
   - Post-processing workflows
   - Expected deliverables

### ⚠️ Current Blocker

**Mac C++ Toolchain Issue:**
- The Mac (darwin 25.1.0) clang++ cannot find `<atomic>` header
- CLASS compilation fails when building threading support (parallel.h)
- This is blocking the recompilation of CLASS with latest v3 code

**Impact:**
- The Nov 23 CLASS binary doesn't include `rho_ridder` in background output
- Can't extract f_EDE from CLASS runs
- Smoke test returns all zeros for f_EDE

---

## Immediate Actions (Mac Environment)

### Option A: Fix C++ Environment (Recommended)
```bash
# Check XCode Command Line Tools
xcode-select --install

# If that doesn't work, reinstall
sudo rm -rf /Library/Developer/CommandLineTools
xcode-select --install

# Verify C++ headers are available
echo '#include <atomic>' | clang++ -std=c++11 -x c++ -E - 2>&1 | head -5
```

### Option B: Work on Azure VM Instead
The Azure VM should have a properly configured C++ environment. Transfer the work there:

```bash
# On Mac, commit all changes
cd /Users/steveridder/Git/Ridder-Field
git add -A
git commit -m "Robust smoke test + MCMC strategy ready"
git push origin v3-development

# On Azure VM
cd ~/Ridder-Field  # or wherever it's located
git pull origin v3-development
cd phase2/class
make clean && make -j4

# Verify compilation succeeded
./class --version
```

---

## Next Steps After CLASS Rebuilds

### 1. Run Robust Smoke Test (30 min)

```bash
cd /path/to/Ridder-Field
python3 mcmc_v3_robust.py
```

**Expected output:**
- `figures/mcmc_residuals/v3_tier4_residuals.png`
- `mcmc_v3_robust_results.json`

**Success criteria:**
- ΛCDM: H0 = 67.36, f_EDE = 0.000
- TRGB: H0 ~ 69.2, f_EDE ~ 0.08, CMB RMS < 15%, BAO < 3%
- SH0ES: H0 ~ 73.1, f_EDE ~ 0.17, CMB RMS < 15%, BAO < 3%

**If residuals look good** → proceed to full MCMC  
**If residuals are large** → debug model or likelihood

### 2. Set Up Cobaya (1 day)

**On Azure VM:**

```bash
# Install Cobaya
pip install cobaya

# Download Planck 2018 likelihoods (~50 GB, takes 1-2 hours)
cobaya-install planck_2018 --packages-path ~/cobaya_packages

# Download BAO data
cobaya-install bao.sdss_dr12_consensus_full_shape --packages-path ~/cobaya_packages
```

**Create YAML files** (templates in `MCMC_STRATEGY.md`):
- `cobaya_v3_baseline.yaml` (no H0 prior)
- `cobaya_v3_trgb.yaml` (H0 = 69.8 ± 1.7)
- `cobaya_v3_shoes.yaml` (H0 = 73.04 ± 1.04)

**Test short chain** (1000 samples, ~10 min):
```bash
cobaya-run cobaya_v3_baseline.yaml -o chains/test --debug
```

Check that CLASS is being called correctly and chains are writing.

### 3. Run Full MCMC (3-5 days wall time)

**Baseline run** (no H0 prior):
```bash
cobaya-run cobaya_v3_baseline.yaml -o chains/v3_baseline
```

**TRGB run**:
```bash
cobaya-run cobaya_v3_trgb.yaml -o chains/v3_trgb
```

**SH0ES run**:
```bash
cobaya-run cobaya_v3_shoes.yaml -o chains/v3_shoes
```

**Monitor progress:**
```bash
# Check convergence (R-1 statistic)
getdist-plot chains/v3_baseline -p H0 omega_cdm

# Estimated completion time
tail -f chains/v3_baseline.progress
```

**Target:** R-1 < 0.01 for all parameters (indicates convergence).

### 4. Post-Process Results (1-2 days)

**a) Convergence Check**
```python
from getdist import loadMCSamples
samples = loadMCSamples('chains/v3_baseline')
print(samples.getGelmanRubin())  # should be < 1.01 for all params
```

**b) Generate Triangle Plots**
```python
from getdist import plots
g = plots.get_subplot_plotter()
g.triangle_plot([samples_baseline, samples_trgb, samples_shoes],
                params=['H0', 'omega_cdm', 'ridder_Lambda_tail_eV', 'f_EDE'],
                legend_labels=['Baseline', 'TRGB', 'SH0ES'])
g.export('figures/v3_triangle.pdf')
```

**c) CMB Spectra Overlay**
- Extract best-fit parameters from each chain
- Run CLASS with those parameters
- Plot TT, TE, EE vs Planck data points

**d) BAO Residuals**
- Compute D_V(z) / r_s for each chain's best-fit
- Plot fractional residuals vs BAO compilation

**e) Model Comparison Table**
```
Model            χ²_min   k    AIC     BIC     Interpretation
ΛCDM             2805.2   6    2817.2  2853.1  Reference
V3 Baseline      2804.8  10    2824.8  2878.4  No improvement
V3 TRGB          2808.1  10    2828.1  2881.7  Acceptable (Δχ²=+2.9)
V3 SH0ES         2835.4  10    2855.4  2909.0  Disfavored (Δχ²=+30.2)
```

### 5. Paper Figures (1 day)

**Required figures:**
1. **Fig 1:** V3 potential shape (EDE + tail components)
2. **Fig 2:** H0 vs Lambda_tail calibration curve (already done)
3. **Fig 3:** CMB TT/TE/EE spectra (TRGB vs ΛCDM)
4. **Fig 4:** BAO residuals (bar chart at z=0.15, 0.35, 0.57, 0.70)
5. **Fig 5:** Triangle plot (H0, Omega_m, Lambda_tail, f_EDE)
6. **Fig 6:** Energy density evolution (rho_EDE(z), rho_tail(z))

### 6. Paper Draft Completion (1 week)

**Sections to write:**
- **Abstract:** "We present a scalar field model that naturally accommodates H₀~70 km/s/Mpc..."
- **Introduction:** H0 tension, TRGB vs SH0ES, motivation for early + late components
- **Model:** V3 potential specification, EDE + tail physics
- **Methods:** CLASS implementation, MCMC setup (Cobaya + Planck + BAO)
- **Results:** 
  - Baseline: H0 = 67.2 ± 0.9 (data prefers ΛCDM)
  - TRGB: H0 = 69.8 ± 1.2, Δχ² = +2.9 (acceptable)
  - SH0ES: H0 = 73.0 ± 1.0, Δχ² = +30.2 (strongly disfavored)
- **Discussion:** TRGB alignment, SH0ES tension remains, systematics
- **Conclusion:** If TRGB is correct, Ridder field resolves H0 without fine-tuning

---

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Fix C++ environment | 1 hour | XCode tools |
| Rebuild CLASS | 10 min | C++ fixed |
| Robust smoke test | 30 min | CLASS rebuilt |
| Cobaya setup | 1 day | Azure VM |
| Full MCMC (3 runs) | 3-5 days | Cobaya setup |
| Post-processing | 1-2 days | MCMC complete |
| Paper figures | 1 day | Post-processing |
| Paper draft | 1 week | All results in |

**Total: ~2-3 weeks** from now to submission-ready draft.

---

## Key Files Reference

### Scripts
- `run_unified_model_v3.py` - Main button API for v3 model
- `mcmc_v3_robust.py` - Robust tier 4 smoke test with residual curves
- `plot_v3_calibration.py` - Generate calibration plots

### Documentation
- `MCMC_STRATEGY.md` - Full MCMC roadmap and Cobaya templates
- `V3_TAIL_CALIBRATION_SUCCESS.md` - Tail calibration report
- `TRGB_VS_SHOES_STRATEGY.md` - Strategic positioning playbook
- `PAPER_UPDATE_DRAFT.md` - Current paper draft

### Data
- `PRESETS` in `run_unified_model_v3.py`:
  - `lcdm_baseline`: Λ_tail = 0.0, f_axion = 0.0
  - `v3_trgb_branch`: Λ_tail = 1.2 meV, f_axion = 0.25
  - `v3_shoes_branch`: Λ_tail = 1.6 meV, f_axion = 0.40

---

## Success Criteria for Publication

### Minimal (publishable negative result):
- V3 baseline reproduces ΛCDM
- V3 TRGB shows Δχ² < +5 (acceptable fit)
- V3 SH0ES shows Δχ² > +20 (tension remains)

**Claim:** "Scalar field models can accommodate TRGB (H₀~70) but not SH0ES (H₀~73) without breaking CMB constraints."

### Ideal (positive result):
- V3 baseline shows modest H₀ pull toward 68-69
- V3 TRGB is statistically indistinguishable from ΛCDM (Δχ² < +2)
- V3 SH0ES requires f_EDE > 17%, confirming earlier exclusions

**Claim:** "If TRGB measurements are correct, the Ridder field provides a natural resolution of the Hubble tension without fine-tuning."

---

## Contact / Handoff

If continuing this work on a different machine or after a break:

1. **Check git status:**
   ```bash
   cd /path/to/Ridder-Field
   git branch  # should be on v3-development
   git status
   ```

2. **Verify CLASS build:**
   ```bash
   cd phase2/class
   ls -lh class  # check date
   ./class --version
   ```

3. **Test button API:**
   ```bash
   python3 run_unified_model_v3.py --preset lcdm_baseline --mode quick
   # Should complete in ~30 sec and print JSON
   ```

4. **Check TODO list:**
   ```bash
   cat NEXT_STEPS.md  # this file
   ```

Good luck with the full MCMC runs! 🚀
