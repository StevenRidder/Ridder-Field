# Phase 2 Audit Report

## Objective
Execute a "clean Phase 2 run" of the Ridder Cosmology (RC-X*) model in CLASS, enabling MCMC in Phase 3. The goal is to produce a "real submission" quality paper with valid plots.

## Status Overview
- **Theory**: Locked. The full paper text (Sections 1-7) has been saved to `phase2/paper/ridder_cosmology_paper.tex`.
- **Background Physics**: **COMPLETE & VERIFIED**.
    - The Ridder field correctly transitions from inflation -> EDE -> Late Vacuum.
    - $r_s$ reduction confirmed (0.06% effect with unoptimized parameters).
    - Unit conversions fixed.
- **Perturbation Physics**: **INCOMPLETE / PATCHED**.
    - **Stability**: Current implementation uses a "hard cutoff" (freezing perturbations) when the field switches to fluid mode to prevent numerical crash ("Step size too small").
    - **Completeness**: **CRITICAL GAP**. The Dark Matter perturbation equations in `perturbations.c` do **not** yet include the coupling terms ($\beta \delta\phi'$). This means the "Growth Kink" (Figure 4) will not appear even if the code runs. The coupling is currently one-way (DM -> Scalar only).
    - **Impact**: This prevents the computation of the "Growth Kink" and full $C_l$ spectra. The "clean run" is blocked by both numerical instability and missing physics.
- **MCMC**: **READY**.
    - Cobaya framework is set up.
    - It can currently fit background observables ($H_0$, BAO), but not full CMB ($C_l$) due to the perturbation issue.

## File Audit
1.  `phase2/paper/ridder_cosmology_paper.tex`: **Locked**. Contains the canonical theory definition.
2.  `phase2/class/source/background.c`: **Verified**. Correctly implements $V(\phi)$, $m_\psi(\phi)$, and $\rho_{\rm DM}$ coupling. Unit conversions are correct.
3.  `phase2/class/source/perturbations.c`: **Needs Work**. 
    - Missing fluid approximation for stability.
    - Missing coupling terms in DM equations (lines 9294, 9302).
4.  `phase3/scan_ede.py`: **Functional**. Successfully runs grid scans and detects $r_s$ shifts, robust to CLASS exit codes.

## Action Plan for "Clean Run"
To achieve the user's goal of a "real submission" with valid figures:
1.  **Fix DM Coupling**: Modify `perturbations.c` to add the $\beta$ terms to `dy[index_pt_delta_cdm]` and `dy[index_pt_theta_cdm]`.
2.  **Fix Perturbation Stability**: Replace the "cutoff" with a proper **Fluid Approximation**. When $a > a_{osc}$, evolve $\delta\phi$ and $\theta_\phi$ using fluid equations.
3.  **Tune Parameters**: Shift $f$ to Planck scale ($10^{26}$ eV) and tune $\Lambda$ to maximize $f_{EDE}$ at $z_{eq}$.
4.  **Generate Figures**: Run the clean code to produce the exact plots described in the paper (Figures 1-4).
