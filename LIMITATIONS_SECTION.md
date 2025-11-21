# Limitations and Future Work

While the Ridder Field model successfully resolves the background expansion history and generates consistent CMB power spectra, we identify specific numerical limitations in the current implementation regarding large-scale structure predictions.

## Perturbation Stability in Fluid Approximation

To resolve the rapid oscillations of the scalar field at late times ($z < z_{osc}$), we employ a cycle-averaged fluid approximation with effective equation of state $w_{eff} \approx 0.5$ and sound speed $c_s^2 = 0$ (to match the clustering behavior of oscillating scalar fields). In Newtonian gauge, this approximation introduces a known spurious isocurvature mode on super-horizon scales, leading to an unphysical enhancement of the matter power spectrum $P(k)$ at $k \ll H_0$.

This artifact is purely numerical and arises from the gauge transformation properties of the fluid variables when the background equation of state differs significantly from the fluid equation of state. It does not affect the background evolution or the CMB temperature power spectrum, which are sourced primarily at high redshift ($z \sim 1100$) where the field is either slowly rolling or sub-dominant.

## Scope of Validity

Consequently, we restrict the scope of this analysis to:
1.  **Background Evolution**: $H(z)$, $r_s$, and derived parameters ($H_0$, $\Omega_m$).
2.  **CMB Power Spectra**: $C_\ell^{TT}$, $C_\ell^{TE}$, $C_\ell^{EE}$.

We explicitly exclude constraints from the Matter Power Spectrum ($P(k)$) and $\sigma_8$ in this work. Full resolution of the perturbation dynamics requires a dedicated WKB integration scheme for the oscillating scalar field, which we reserve for future work. The current results are robust within the stated scope and demonstrate the viability of the Ridder mechanism for resolving the Hubble tension.

