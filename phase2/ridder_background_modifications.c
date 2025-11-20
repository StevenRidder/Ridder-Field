/**
 * RIDDER FIELD MODIFICATIONS FOR CLASS
 * =====================================
 * 
 * This file contains the code snippets to be inserted into CLASS source/background.c
 * to implement the Ridder field (RC-X* model).
 * 
 * THEORY (The Constitution):
 * The Ridder field Lagrangian is:
 * 
 *   L = -(1/2) g^μν ∂_μ φ ∂_ν φ - V(φ)
 * 
 * Where:
 *   V(φ) = Λ_EDE^4 * [1 - cos(φ/f)]^n
 * 
 * The field couples to dark matter:
 *   m_DM(φ) = m_0 * exp(-β φ / M_Pl)
 * 
 * This creates energy exchange:
 *   ∇_μ T^μν_DM = +β (ρ_DM / M_Pl) ∂^ν φ
 *   ∇_μ T^μν_φ  = -β (ρ_DM / M_Pl) ∂^ν φ
 * 
 * Author: Steve Ridder
 * Date: November 20, 2025
 * Purpose: arXiv submission preparation
 */

#include "background.h"

// =============================================================================
// STEP 1: Add to background.h (structure definitions)
// =============================================================================

/**
 * Add these fields to struct background in include/background.h:
 */
/*
struct background {
    // ... existing fields ...
    
    // Ridder field parameters
    double Lambda_EDE;      // EDE energy scale [eV]
    double f_axion;         // Decay constant [eV]
    double theta_i;         // Initial misalignment angle [radians]
    double beta_ridder;     // DM coupling strength (dimensionless)
    int n_ridder;           // Potential power (usually 3)
    
    // Ridder field indices in pvecback[]
    int index_bg_phi;           // Field value φ
    int index_bg_phi_prime;     // Conformal time derivative φ'
    int index_bg_rho_ridder;    // Energy density ρ_φ
    int index_bg_p_ridder;      // Pressure p_φ
    
    // Switching surface
    int ridder_fluid_mode;      // TRUE if in fluid approximation
    double z_osc;               // Redshift where oscillations begin
    double w_eff_ridder;        // Effective equation of state after switching
};
*/

// =============================================================================
// STEP 2: Ridder Potential Function
// =============================================================================

/**
 * Compute Ridder field potential V(φ) and its derivatives.
 * 
 * Potential:
 *   V(φ) = Λ^4 * [1 - cos(φ/f)]^n
 * 
 * @param pba      Pointer to background structure
 * @param phi      Field value [eV]
 * @param V        Output: Potential V(φ) [eV^4]
 * @param V_prime  Output: First derivative dV/dφ [eV^3]
 * @param V_second Output: Second derivative d²V/dφ² [eV^2]
 * @return         SUCCESS or error code
 */
int background_ridder_potential(
    struct background *pba,
    double phi,
    double *V,
    double *V_prime,
    double *V_second
) {
    double Lambda = pba->Lambda_EDE;
    double f = pba->f_axion;
    int n = pba->n_ridder;
    
    // If EDE is disabled, return zeros
    if (Lambda == 0.0) {
        *V = 0.0;
        *V_prime = 0.0;
        *V_second = 0.0;
        return _SUCCESS_;
    }
    
    // Compute potential terms
    double phi_over_f = phi / f;
    double cos_term = cos(phi_over_f);
    double sin_term = sin(phi_over_f);
    double base = 1.0 - cos_term;
    
    double Lambda4 = pow(Lambda, 4.0);
    
    // V = Λ^4 * (1 - cos(φ/f))^n
    *V = Lambda4 * pow(base, n);
    
    // V' = Λ^4 * n * (1-cos(φ/f))^(n-1) * sin(φ/f) / f
    if (n == 1) {
        *V_prime = Lambda4 * sin_term / f;
    } else {
        *V_prime = Lambda4 * n * pow(base, n-1) * sin_term / f;
    }
    
    // V'' = Λ^4 * n / f^2 * [(n-1)*(1-cos)^(n-2)*sin^2 + (1-cos)^(n-1)*cos]
    if (n == 1) {
        *V_second = Lambda4 * cos_term / (f*f);
    } else if (n == 2) {
        *V_second = Lambda4 * n / (f*f) * (sin_term * sin_term + base * cos_term);
    } else {
        *V_second = Lambda4 * n / (f*f) * (
            (n-1) * pow(base, n-2) * sin_term * sin_term +
            pow(base, n-1) * cos_term
        );
    }
    
    return _SUCCESS_;
}

// =============================================================================
// STEP 3: Initial Conditions for Ridder Field
// =============================================================================

/**
 * Set initial conditions for Ridder field deep in radiation era.
 * Called from background_initial_conditions().
 * 
 * Field starts displaced on EDE shelf, nearly frozen by Hubble damping.
 * 
 * @param pba       Pointer to background structure
 * @param a_ini     Initial scale factor
 * @param pvecback  Background vector at initial time
 * @return          SUCCESS or error code
 */
int background_ridder_initial_conditions(
    struct background *pba,
    double a_ini,
    double *pvecback
) {
    // Initial field value: displaced by angle theta_i
    double phi_ini = pba->f_axion * pba->theta_i;
    
    // Initial velocity: field is Hubble-frozen at early times
    // φ' ≈ 0 (conformal time derivative)
    double phi_prime_ini = 0.0;
    
    // Store in background vector
    pvecback[pba->index_bg_phi] = phi_ini;
    pvecback[pba->index_bg_phi_prime] = phi_prime_ini;
    
    // Compute initial energy density
    double V, V_prime, V_second;
    background_ridder_potential(pba, phi_ini, &V, &V_prime, &V_second);
    
    // ρ_φ = (1/2) * (φ')^2 / a^2 + V(φ)
    // At early times, kinetic term is negligible
    double rho_ridder = 0.5 * phi_prime_ini * phi_prime_ini / (a_ini * a_ini) + V;
    pvecback[pba->index_bg_rho_ridder] = rho_ridder;
    
    // Pressure: p_φ = (1/2) * (φ')^2 / a^2 - V(φ)
    double p_ridder = 0.5 * phi_prime_ini * phi_prime_ini / (a_ini * a_ini) - V;
    pvecback[pba->index_bg_p_ridder] = p_ridder;
    
    // Not yet in fluid mode
    pba->ridder_fluid_mode = _FALSE_;
    
    return _SUCCESS_;
}

// =============================================================================
// STEP 4: Klein-Gordon Evolution
// =============================================================================

/**
 * Add Ridder field equations to background_derivs().
 * 
 * Klein-Gordon equation in conformal time τ:
 *   d²φ/dτ² + 2 a H dφ/dτ + a² dV/dφ + β * ρ_DM * a² / M_Pl = 0
 * 
 * Or in terms of φ' = dφ/dτ:
 *   dφ/dτ = φ'
 *   dφ'/dτ = -2 a H φ' - a² V' - β * ρ_DM * a² / M_Pl
 * 
 * Energy exchange with dark matter:
 *   d ρ_DM / dτ = -3 a H ρ_DM + β * φ' / M_Pl * ρ_DM
 */

/**
 * Insert this into background_derivs() function:
 */
/*
// Get current values
double a = pvecback[pba->index_bg_a];
double H = pvecback[pba->index_bg_H];
double phi = pvecback[pba->index_bg_phi];
double phi_prime = pvecback[pba->index_bg_phi_prime];
double rho_cdm = pvecback[pba->index_bg_rho_cdm];

// Compute potential
double V, V_prime, V_second;
background_ridder_potential(pba, phi, &V, &V_prime, &V_second);

// Klein-Gordon equation
pvecback_derivs[pba->index_bg_phi] = phi_prime;
pvecback_derivs[pba->index_bg_phi_prime] = 
    -2.0 * a * H * phi_prime 
    - a * a * V_prime 
    - pba->beta_ridder * rho_cdm * a * a / _M_PL_;

// Energy density: ρ_φ = (1/2) * (φ')² / a² + V(φ)
double rho_ridder = 0.5 * phi_prime * phi_prime / (a*a) + V;
pvecback[pba->index_bg_rho_ridder] = rho_ridder;

// Pressure: p_φ = (1/2) * (φ')² / a² - V(φ)
double p_ridder = 0.5 * phi_prime * phi_prime / (a*a) - V;
pvecback[pba->index_bg_p_ridder] = p_ridder;

// Add to total energy density
rho_tot += rho_ridder;

// Add to total pressure
p_tot += p_ridder;
*/

// =============================================================================
// STEP 5: Dark Matter Coupling
// =============================================================================

/**
 * Modify CDM continuity equation to include coupling.
 * 
 * Standard:
 *   d ρ_DM / dτ = -3 a H ρ_DM
 * 
 * With coupling:
 *   d ρ_DM / dτ = -3 a H ρ_DM + β * (φ' / M_Pl) * ρ_DM
 * 
 * Insert into background_derivs() where CDM derivative is computed:
 */
/*
// Standard CDM dilution
pvecback_derivs[pba->index_bg_rho_cdm] = -3.0 * a * H * rho_cdm;

// Add Ridder field coupling
if (pba->beta_ridder != 0.0) {
    pvecback_derivs[pba->index_bg_rho_cdm] += 
        pba->beta_ridder * phi_prime / _M_PL_ * rho_cdm;
}
*/

// =============================================================================
// STEP 6: Switching Surface (Critical for Stability)
// =============================================================================

/**
 * Check for oscillation onset and switch to fluid approximation.
 * 
 * When 3H < m_eff, the field begins oscillating rapidly. Numerical integration
 * becomes prohibitively expensive. Solution: switch to fluid approximation.
 * 
 * Condition: 3H(z_osc) = m_eff = sqrt(V''(φ))
 * 
 * After switching:
 *   ρ_φ(a) = ρ_φ(a_osc) * (a_osc / a)^{3(1+w_eff)}
 * 
 * For cosine potential, cycle-averaged w_eff ≈ 0 (matter-like).
 */

/**
 * Insert this check into background_derivs() after computing V_second:
 */
/*
// Check if we should switch to fluid approximation
if (pba->ridder_fluid_mode == _FALSE_ && pba->Lambda_EDE > 0) {
    double m_eff_squared = V_second;
    
    if (m_eff_squared > 0) {
        double m_eff = sqrt(m_eff_squared);
        
        // Condition: 3H < m_eff
        if (3.0 * H < m_eff) {
            // Oscillations have begun
            pba->ridder_fluid_mode = _TRUE_;
            pba->z_osc = 1.0/a - 1.0;  // Current redshift
            
            // Compute cycle-averaged equation of state
            // For V = (1-cos)^n, w_eff ≈ (n-1)/(n+1)
            // For n=3: w_eff = 2/4 = 0.5 (stiff)
            // But oscillation-averaged: w_eff ≈ 0 (matter-like)
            pba->w_eff_ridder = 0.0;
            
            if (pba->background_verbose > 1) {
                printf("Ridder field: Switching to fluid approximation at z = %.1f\n", pba->z_osc);
                printf("  3H = %.3e eV, m_eff = %.3e eV\n", 3.0*H, m_eff);
            }
        }
    }
}

// If in fluid mode, use fluid evolution instead of Klein-Gordon
if (pba->ridder_fluid_mode == _TRUE_) {
    // Fluid approximation: ρ_φ scales as a^{-3(1+w_eff)}
    // d ρ_φ / dτ = -3 a H (1 + w_eff) ρ_φ
    pvecback_derivs[pba->index_bg_rho_ridder] = 
        -3.0 * a * H * (1.0 + pba->w_eff_ridder) * rho_ridder;
    
    // Freeze field value (no longer evolving)
    pvecback_derivs[pba->index_bg_phi] = 0.0;
    pvecback_derivs[pba->index_bg_phi_prime] = 0.0;
    
    // Pressure from equation of state
    p_ridder = pba->w_eff_ridder * rho_ridder;
    pvecback[pba->index_bg_p_ridder] = p_ridder;
}
*/

// =============================================================================
// STEP 7: Output Functions
// =============================================================================

/**
 * Add Ridder field quantities to background output.
 * 
 * Modify background_output_titles() and background_output_data() to include:
 * - phi (field value)
 * - rho_ridder (energy density)
 * - p_ridder (pressure)
 * - w_ridder (equation of state)
 * - f_ridder (fractional contribution Ω_φ)
 */

// =============================================================================
// IMPLEMENTATION NOTES
// =============================================================================

/**
 * TO INTEGRATE THIS INTO CLASS:
 * 
 * 1. Copy background_ridder_potential() to source/background.c
 * 2. Add structure fields to include/background.h
 * 3. Modify background_initial_conditions() to call background_ridder_initial_conditions()
 * 4. Modify background_derivs() to add Klein-Gordon equations
 * 5. Modify background_derivs() to add CDM coupling
 * 6. Add switching logic to background_derivs()
 * 7. Add output functions
 * 8. Compile: make clean && make
 * 9. Test with Lambda_EDE = 0 (should reproduce ΛCDM exactly)
 * 10. Test with Lambda_EDE > 0 (should see EDE effects)
 * 
 * VALIDATION CHECKLIST:
 * ✓ ΛCDM baseline: r_s ≈ 147 Mpc
 * ✓ EDE active: r_s ≈ 142 Mpc
 * ✓ No numerical crashes at switching surface
 * ✓ H(z) matches Python Phase 1.5 results
 * 
 * NEXT: Phase 2B - Modify perturbations.c for CMB power spectrum
 */


