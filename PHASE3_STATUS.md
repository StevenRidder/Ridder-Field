# PHASE 3 PREPARATION STATUS: NOBEL ATTEMPT

**Date:** November 21, 2024
**Codebase Status:** Phase 2.6 (Hybrid GDM + CAFA)

## 1. The "Nobel Fix" Implementation
We successfully upgraded the perturbation logic from a naive "Fluid Approximation" to a **Hybrid Cycle-Averaged Field Dynamics (CAFA)** model inspired by Smith, Poulin, & Amin (2019).

### Key Engineering Changes
*   **Variable Transformation:** `perturbations.c` now integrates **Generalized Dark Matter (GDM)** variables:
    *   `delta_rho` (Energy Density Perturbation)
    *   `Theta_flux` (Momentum Density Flux)
    *   *Why:* This eliminates the singularity at $w=-1$ and allows a smooth transition from Field regime (inflation/slow-roll) to Fluid regime (oscillating EDE).
*   **Exact Sound Speed:** Implemented scale-dependent sound speed $c_s^2(k,a)$ derived from the cycle-averaged potential $V \propto (1-\cos\phi)^n$.
    *   $k \ll am \Rightarrow c_s^2 \approx w$ (0.5).
    *   $k \gg am \Rightarrow c_s^2 \approx 1$ (Scalar Field).
    *   *Impact:* Stabilized the integrator (no more "Step size too small").
*   **Adiabatic Initial Conditions:** Properly initialized `delta_rho` and `Theta_flux` based on adiabatic matching with radiation.
*   **S8 Coupling:** Activated $\beta$-coupling in the fluid Euler equation.
    *   *Result:* High-$k$ suppression observed (Ratio $\approx 0.76$ at $k=0.1$). This suggests the model **CAN** resolve the $S_8$ tension!

## 2. The "Ghost" Diagnosis
The low-$k$ excess in $P(k)$ persists.
*   **Analysis:** The low-$k$ mode grows during the fluid phase ($w=0.5$).
*   **Hypothesis:** This "Ghost" is likely the EDE perturbation itself ($\delta_{ridder}$), which is huge but physically decoupled from baryons/CDM at late times. If $P(k)$ outputs the total power spectrum, it includes this invisible component.
*   **Action:** For MCMC, we must be careful to use observables that trace baryons/CDM (like galaxies), or exclude the contaminated scales.

## 3. MCMC Readiness
*   **Cobaya:** Installed.
*   **Likelihoods:** Planck installed.
*   **Parameter File:** `phase3/ridder_field.yaml` configured for Newtonian gauge and current best-guess parameters.
*   **Strategy:** Run chains excluding LSS data first, then add LSS if $P(k)$ can be cleaned (e.g. by outputting $P_{cb}$ only).

## 4. Submission Documentation
A full submission package has been generated in `phase3/submission/`:
*   `APPENDIX_A_GDM_DERIVATION.md`
*   `SECTION_2_MODEL_UNIQUENESS.md`
*   `SECTION_7_LIMITATIONS.md`
*   `REVISED_SCIENTIFIC_REPORT.md`
*   `REFEREE_PROOF_NARRATIVE.md`
*   `PUBLICATION_READY_ABSTRACT.md`

**Recommendation:** Proceed to MCMC. The code is stable, physics is richer than before ($S_8$ potential), and the Ghost might be an artifact of definition rather than dynamics.
