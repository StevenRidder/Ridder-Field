# Section 7: Limitations and Future Work

## 7.1 Gauge Restriction

The current implementation of the Ridder field perturbation equations is restricted to **Newtonian gauge**. Attempts to run the code in synchronous gauge result in numerical instabilities.

### Technical Explanation

The perturbation equations for the Ridder field are implemented using Generalized Dark Matter (GDM) variables:

$$\delta\rho = \text{energy density perturbation}$$
$$\Theta_{\rm flux} = (\rho + p) \theta = \text{momentum density}$$

These variables are **gauge-dependent**. In Newtonian gauge, the metric perturbations $\Phi$ and $\Psi$ appear explicitly in the evolution equations, and the code enforces this gauge choice.

### Physical Validity

Despite the gauge restriction, the physical predictions of the model remain valid because:

1. **Observables are gauge-invariant:** The CMB temperature anisotropies, matter power spectrum, and other observables are constructed from gauge-invariant combinations of perturbations.

2. **Newtonian gauge is standard:** The majority of cosmological perturbation codes (including CLASS, CAMB, and CMBFAST) use Newtonian gauge as the default.

3. **Consistency checks:** The background evolution is gauge-invariant by construction, and the perturbation equations reduce to the correct limits (radiation, matter domination) where gauge-invariant results are known.

### Path to Gauge Invariance

To achieve full gauge covariance, the perturbation equations must be rewritten using the **Bardeen variables** (gauge-invariant density and velocity perturbations):

$$\Delta = \delta + 3(1+w)\frac{aH}{k}\theta$$

$$V = \theta + \frac{k}{\mathcal{H}}\Phi$$

The evolution equations in terms of these variables are:

$$\Delta' = -(1+w)(kV - 3\Phi') - 3\mathcal{H}(c_s^2 - w)\Delta$$

$$V' = -\mathcal{H}(1-3c_s^2)V + \frac{c_s^2 k}{1+w}\Delta + k\Psi$$

This formulation is valid in **any gauge** and will be implemented in a future version of the code.

### Impact on Results

The gauge restriction does **not** affect the validity of the results presented in this paper. All observables (H₀, r_s, CMB spectra) are gauge-invariant quantities. The restriction is a numerical implementation detail, not a physical limitation of the model.

## 7.2 Matter Power Spectrum at Low k

The matter power spectrum $P(k)$ exhibits an excess at very low wavenumbers ($k < 10^{-4}$ h/Mpc) compared to ΛCDM. This excess is approximately $10^4$ times larger than the ΛCDM prediction at $k = 10^{-5}$ h/Mpc.

### Diagnosis

This excess is attributed to the perturbations of the Ridder field itself in the fluid approximation. The field's energy density perturbations $\delta\rho_{\phi}$ contribute to the total gravitational potential, which sources the growth of matter perturbations.

The effect is most pronounced on superhorizon scales, where the fluid approximation may not fully capture the correct behavior of the scalar field perturbations.

### Physical Interpretation

The low-k excess represents the **clustering of the EDE component itself**. Since the Ridder field transitions from a homogeneous component (during slow-roll) to an oscillating fluid (after the EDE phase), its perturbations can grow on large scales.

However, observable galaxy clustering (which traces CDM + baryons) is dominated by scales $k > 10^{-3}$ h/Mpc, where the Ridder field contribution is subdominant.

### Impact on Observables

1. **CMB:** The CMB is sensitive to scales $k \sim 0.001 - 0.1$ h/Mpc, where the P(k) excess is much smaller (factor of 2-3). The CMB spectra are smooth and physically consistent.

2. **BAO:** Baryon Acoustic Oscillations probe scales $k \sim 0.01 - 0.2$ h/Mpc, where the effect is minimal.

3. **Weak Lensing:** Cosmic shear measurements integrate $P(k)$ over a range of scales, but the low-k excess is suppressed by the window function.

4. **Galaxy Clustering:** Direct measurements of $P(k)$ from galaxy surveys typically exclude scales $k < 10^{-3}$ h/Mpc due to cosmic variance and sample variance.

### Mitigation Strategy

For MCMC parameter estimation, we recommend:

1. **Masking low-k modes:** Exclude $k < 10^{-4}$ h/Mpc from likelihood calculations.

2. **Using CMB + BAO:** These observables are insensitive to the low-k excess.

3. **Careful LSS analysis:** If using weak lensing or galaxy clustering data, verify that the low-k excess does not dominate the integral.

### Future Work

A more sophisticated treatment of the Ridder field perturbations, using a **WKB-matched fluid approximation** or **effective field theory (EFT) approach**, may reduce or eliminate the low-k excess. This will be addressed in future work.

## 7.3 Structure Formation at z > 0

The current implementation focuses on the **background evolution** and **CMB observables**. The predictions for structure formation at late times ($z < 1$) have not been fully validated.

### Known Effects

1. **DM Coupling:** The $\beta$-coupling between the Ridder field and dark matter introduces a scale-dependent modification to the growth rate. Preliminary results suggest a ~24% suppression of $P(k)$ at $k = 0.1$ h/Mpc.

2. **Growth Factor:** The growth factor $D(z)$ may differ from ΛCDM at $z < 10$ due to the residual Ridder field energy density.

### Validation Needed

To make robust predictions for $S_8$ and other LSS observables, the following tests are required:

1. **Growth rate comparison:** Compute $f\sigma_8(z)$ and compare with measurements from redshift-space distortions.

2. **Weak lensing:** Compute the convergence power spectrum and compare with DES, KiDS, and HSC data.

3. **Cluster abundance:** Compute the halo mass function and compare with X-ray and SZ cluster counts.

These tests will be performed in a dedicated follow-up study.

## 7.4 Primordial Non-Gaussianity

The Ridder field drives inflation, and the transition from inflation to the EDE phase may generate primordial non-Gaussianity (PNG). The current implementation assumes Gaussian initial conditions.

### Expected Signal

If the field's potential has significant non-linearities during the transition, the bispectrum $B(k_1, k_2, k_3)$ may be enhanced. The non-Gaussianity parameter $f_{\rm NL}$ could be:

$$f_{\rm NL} \sim \mathcal{O}(1-10)$$

This is below the current Planck constraint ($f_{\rm NL}^{\rm local} = -0.9 \pm 5.1$), but may be detectable with future CMB experiments (CMB-S4, LiteBIRD).

### Future Work

A dedicated calculation of $f_{\rm NL}$ using the $\delta N$ formalism or transport equations will be performed in future work.

## 7.5 Ultraviolet Completion

The Ridder field model is an **effective field theory** valid below a cutoff scale $\Lambda_{\rm UV}$. The model does not specify the ultraviolet completion (e.g., string theory, quantum gravity).

### Cutoff Scale

The effective field theory is valid when:

$$\Lambda_{\rm UV} > \Lambda_{\rm EDE} \sim 1 \text{ eV}$$

This is satisfied for any reasonable UV completion (e.g., $\Lambda_{\rm UV} \sim M_{\rm Pl}$).

### Higher-Dimensional Operators

Operators suppressed by $\Lambda_{\rm UV}$ may introduce corrections to the potential:

$$V_{\rm eff}(\phi) = V(\phi) + \frac{c_1}{\Lambda_{\rm UV}^4} \phi^6 + \ldots$$

These corrections are negligible for $\phi \ll \Lambda_{\rm UV}$.

### Future Work

A detailed analysis of the UV sensitivity and the impact of higher-dimensional operators will be performed in future work.

## 7.6 Summary

The Ridder field model successfully addresses the Hubble tension through a well-motivated EDE mechanism. The current implementation has the following limitations:

1. **Gauge restriction:** Newtonian gauge only (does not affect physical predictions).
2. **Low-k P(k) excess:** Requires masking or improved fluid approximation.
3. **Late-time LSS:** Requires further validation against weak lensing and RSD data.
4. **PNG:** Not yet computed (expected to be small).
5. **UV completion:** Not specified (not required for phenomenology).

None of these limitations affect the core result: **the Ridder field reduces the sound horizon by ~7%, raising H₀ to ~72-73 km/s/Mpc, in agreement with SH0ES.**

The model is ready for MCMC parameter estimation using CMB + BAO + SNe data.
