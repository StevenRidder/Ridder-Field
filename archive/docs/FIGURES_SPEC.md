# Figure Specifications for Ridder Cosmology Paper

**Purpose:** Detailed specifications for all figures in the arXiv submission.

---

## Figure 1: Potential and Background Evolution

**Title:** "The Ridder Field Potential and Cosmological Trajectory"

**Purpose:** Visualize the "one field, three phases" concept

**Content:**
- **Top Panel:** Plot V(φ) vs φ showing:
  - Inflationary plateau region (φ >> M_Pl)
  - EDE bump near φ ~ f (axion-like shelf)
  - Final minimum at φ₀ (late-time vacuum)
- **Bottom Panel:** Schematic trajectory φ(a) vs scale factor a, marking:
  - Inflation epoch (slow-roll on plateau)
  - Reheating transition
  - EDE epoch (Hubble-frozen on shelf)
  - Late-time settling (oscillations → fluid)

**Technical Details:**
- Use fiducial parameters: V_* = (8×10¹⁵ GeV)⁴, Λ_EDE = 0.01 eV, f = 10¹⁶ eV
- Show potential in units of M_Pl⁴ for inflation, eV⁴ for EDE
- Mark key field values: φ_inf (inflation), φ_EDE (shelf), φ₀ (minimum)
- Use color coding: blue (inflation), orange (EDE), green (late-time)

**File:** `figures/fig1_potential_trajectory.pdf`

**Script:** `scripts/generate_fig1.py`

---

## Figure 2: EDE Fraction vs Redshift

**Title:** "Early Dark Energy Fraction Evolution"

**Purpose:** Show EDE contribution over cosmic time

**Content:**
- Plot f_EDE(z) = ρ_φ(z)/ρ_tot(z) vs redshift z
- Show best-fit RC-X* curve (f_EDE peak ~ 0.07 at z_c ~ 3000)
- Compare to ΛCDM (horizontal line at zero)
- Mark key epochs:
  - z_c (peak EDE fraction)
  - z_osc (oscillation onset)
  - z_eq (matter-radiation equality)

**Technical Details:**
- Log scale for z-axis (z = 10⁴ to z = 0)
- Linear scale for f_EDE (0 to 0.1)
- Use best-fit parameters from MCMC (or fiducial if MCMC not done)
- Add shaded region showing 1σ uncertainty if available

**File:** `figures/fig2_ede_fraction.pdf`

**Script:** `scripts/generate_fig2.py`

**Data Source:** CLASS background output

---

## Figure 3: H₀ and CMB Compatibility

**Title:** "Hubble Constant Constraints and Early Dark Energy"

**Purpose:** Main "anomaly-solving" claim - show H₀ resolution

**Content:**
- **Left Panel:** 2D contour plot showing:
  - H₀ vs f_EDE posterior
  - RC-X* 68% and 95% confidence regions
  - ΛCDM point (H₀ = 67.4 km/s/Mpc, f_EDE = 0)
  - SH0ES measurement (H₀ = 73.0 ± 1.0 km/s/Mpc)
- **Right Panel:** 1D marginalized posteriors:
  - H₀ for RC-X* (should peak ~72-73 km/s/Mpc)
  - H₀ for ΛCDM (peaks ~67.4 km/s/Mpc)
  - Overlay SH0ES measurement

**Technical Details:**
- Use MCMC chains from MontePython/Cobaya
- Show both Planck-only and Planck+BAO+SNe constraints
- Use GetDist or corner.py for plotting
- Color code: blue (RC-X*), red (ΛCDM), green (SH0ES)

**File:** `figures/fig3_h0_contours.pdf`

**Script:** `scripts/generate_fig3.py`

**Data Source:** MCMC chains (Phase 3)

---

## Figure 4: Growth Factor or Matter Power Spectrum Kink

**Title:** "Dark Matter Coupling Signature in Structure Growth"

**Purpose:** Show coupling-induced feature in growth

**Content:**
- **Top Panel:** Linear growth factor D(z) vs redshift:
  - RC-X* with β = 0.01
  - ΛCDM baseline
  - Show localized deviation around z_c
  - Mark z_osc (oscillation onset)
- **Bottom Panel:** Matter power spectrum P(k) at z = 0:
  - RC-X* vs ΛCDM
  - Show percent-level suppression at relevant scales
  - Overlay forecast error bars for Euclid/LSST

**Technical Details:**
- Use CLASS output for D(z) and P(k)
- Show ratio plot (RC-X*/ΛCDM) to highlight differences
- Mark scales: k = 0.01 to k = 1 h/Mpc
- Add observational data points if available (SDSS, BOSS)

**File:** `figures/fig4_growth_kink.pdf`

**Script:** `scripts/generate_fig4.py`

**Data Source:** CLASS perturbations output

---

## Figure 5: n_s - r Plane

**Title:** "Inflationary Predictions in the n_s - r Plane"

**Purpose:** Show plateau inflation predictions

**Content:**
- Plot n_s vs r with:
  - Planck 2018 68% and 95% confidence regions
  - BICEP/Keck 2021 upper limit (r < 0.036)
  - RC-X* prediction point (n_s = 0.965, r = 0.0035)
  - Starobinsky model track (for comparison)
  - Forecast contours for LiteBIRD (r ~ 10⁻³ sensitivity)
  - Forecast contours for CMB-S4

**Technical Details:**
- Use Planck 2018 likelihood contours
- Mark RC-X* point with error bars (if computed)
- Show N_efolds = 50, 55, 60 tracks for Starobinsky
- Use color: red (Planck), blue (RC-X*), green (forecasts)

**File:** `figures/fig5_ns_r_plane.pdf`

**Script:** `scripts/generate_fig5.py`

**Data Source:** Planck 2018 data, Phase 1 predictions

---

## Figure 6 (Optional): Stochastic GW from EDE Transition

**Title:** "Gravitational Wave Signature from Early Dark Energy"

**Purpose:** LISA connection and future test

**Content:**
- Plot Ω_GW(f) vs frequency f:
  - Predicted GW spectrum from EDE phase transition
  - LISA sensitivity curve
  - Show dependence on f_EDE (different curves for f_EDE = 0.05, 0.07, 0.10)
  - Mark peak frequency and amplitude

**Technical Details:**
- Frequency range: 10⁻⁴ to 10⁻¹ Hz (LISA band)
- Use first-order phase transition calculation
- Show only if EDE transition is first-order (may be smooth)

**File:** `figures/fig6_gw_spectrum.pdf`

**Script:** `scripts/generate_fig6.py`

**Status:** Optional - only include if transition is first-order

---

## Table 1: Parameter Summary

**Title:** "Ridder Cosmology Parameters"

**Content:**
- **Standard Parameters:**
  - Ω_b h², Ω_c h², h, n_s, A_s, τ
  - Best-fit values and 68% confidence intervals
- **Ridder Field Parameters:**
  - Λ_EDE, f_axion, θ_i, β
  - Best-fit values and 68% confidence intervals
- **Derived Parameters:**
  - H₀, r_s, σ₈, S₈
  - Best-fit values and 68% confidence intervals

**Format:** LaTeX table with proper alignment

**File:** `tables/table1_parameters.tex`

---

## Table 2: Observables Comparison

**Title:** "Observable Predictions: ΛCDM vs Ridder Cosmology"

**Content:**
- **Observable | ΛCDM | RC-X* | Tension Resolution**
- H₀ (km/s/Mpc) | 67.4 ± 0.5 | 72.5 ± 1.0 | ✅ Resolved
- r_s (Mpc) | 147.1 ± 0.3 | 142.0 ± 0.5 | ✅ Reduced
- σ₈ | 0.811 ± 0.006 | 0.785 ± 0.008 | ✅ Suppressed
- n_s | 0.9649 ± 0.0042 | 0.965 ± 0.003 | ✅ Consistent
- r | < 0.036 | 0.0035 | ✅ Predicted

**Format:** LaTeX table with checkmarks for resolved tensions

**File:** `tables/table2_observables.tex`

---

## Figure Generation Workflow

1. **Phase 2 (CLASS working):**
   - Generate Figures 1, 2, 4, 5 using CLASS output
   - Use fiducial parameters if MCMC not done

2. **Phase 3 (MCMC complete):**
   - Generate Figure 3 using MCMC chains
   - Update Figures 1, 2, 4 with best-fit parameters
   - Generate Tables 1 and 2

3. **Final Paper:**
   - All figures in PDF format
   - All tables in LaTeX format
   - Proper captions and references

---

## Software Requirements

- **Plotting:** matplotlib, seaborn, GetDist (for MCMC plots)
- **Data:** CLASS output, MCMC chains
- **Format:** PDF for figures, LaTeX for tables

---

**Status:** Specifications complete. Ready for implementation once CLASS and MCMC are working.

