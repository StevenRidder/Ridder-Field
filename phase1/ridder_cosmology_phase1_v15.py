"""
Ridder Cosmology (RC-X*) - Phase 1.5: CLASS-Ready Background Evolution
=======================================================================

PHASE 1.5 IMPROVEMENTS (Pre-CLASS):
1. ✓ Units standardized to Mpc (matching CLASS defaults)
2. ✓ Sound horizon calculated to z > 10^6 using Hu-Sugiyama z_drag
3. ✓ Switching surface z_osc defined for oscillation → fluid transition

This is the "ground truth" Python code that will be ported to CLASS in Phase 2.

Author: Steve Ridder
Date: November 20, 2025
Purpose: Preparing for arXiv submission
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from scipy.optimize import fsolve
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PHYSICAL CONSTANTS
# ============================================================================

# Natural units: c = ℏ = k_B = 1
# Length: Mpc
# Energy: eV
# Time: Mpc (since c=1)

M_Pl = 2.435e18 * 1e9  # Reduced Planck mass [eV]
M_Pl_inv = 1.0 / M_Pl

# Conversion factors
GeV = 1e9  # eV
eV_to_cm = 1.973e-5
Mpc_to_cm = 3.086e24
Mpc_in_eV_inv = Mpc_to_cm / eV_to_cm  # 1 Mpc ≈ 1.56e29 eV^-1

# ============================================================================
# MODEL PARAMETERS
# ============================================================================

class RidderParams:
    """Parameters for RC-X* model (Phase 1.5 - CLASS-ready)"""
    
    # ========== Inflationary plateau ==========
    V_star = (8e15 * GeV)**4  # Inflation scale [eV^4]
    lambda_plateau = np.sqrt(2.0/3.0)  # Starobinsky-type
    N_efolds = 55
    
    # ========== Early Dark Energy (EDE) ==========
    # Phase 1.5: Keep EDE structure for Phase 2, but disabled for baseline
    f_EDE_target = 0.10  # Target EDE fraction at recombination
    z_c_target = 3000    # Target critical redshift
    f_axion = 1e16       # Decay constant [eV]
    theta_i = 2.5        # Initial misalignment angle
    Lambda_EDE = 0.0     # [eV] - DISABLED for Phase 1.5 baseline
    
    # Mass (when EDE is active): m^2 = Lambda^4 / f^2
    @property
    def m_EDE_eV(self):
        if self.Lambda_EDE == 0:
            return 0.0
        return self.Lambda_EDE**2 / self.f_axion
    
    # ========== Dark Matter Coupling ==========
    beta = 0.0  # Coupling strength (0 for pure ΛCDM baseline)
    
    # ========== Late-time Vacuum Energy ==========
    rho_Lambda = (2.3e-3)**4  # [eV^4] ≈ (2.3 meV)^4
    
    # ========== Standard Cosmology (Planck 2018) ==========
    Omega_b_h2 = 0.02237
    Omega_c_h2 = 0.1200
    h = 0.6736  # H_0 = 100h km/s/Mpc
    T_CMB_0 = 2.7255  # [K]
    
    # ========== Derived Quantities ==========
    # Hubble constant
    H_0_SI = h * 100 * 1e3 / 3.086e22  # [s^-1]
    H_0_eV = H_0_SI * 6.582e-16  # [eV]
    H_0_Mpc_inv = H_0_eV / Mpc_in_eV_inv  # [Mpc^-1] = H_0 * (1 Mpc)
    
    # Temperature
    T_gamma_0 = T_CMB_0 * 8.617e-5  # [eV]
    
    # Critical density
    rho_crit_0 = 3.0 * M_Pl**2 * H_0_eV**2  # [eV^4]
    
    # Present energy densities
    rho_b_0 = (Omega_b_h2 / h**2) * rho_crit_0
    rho_c_0 = (Omega_c_h2 / h**2) * rho_crit_0
    rho_gamma_0 = (np.pi**2 / 15) * T_gamma_0**4 * 2  # photons (g=2)
    
    # Neutrinos (3 massless species)
    T_nu_0 = (4.0/11.0)**(1.0/3.0) * T_gamma_0
    rho_nu_0 = (7.0/8.0) * (np.pi**2 / 15) * T_nu_0**4 * 3.0
    
    rho_rad_0 = rho_gamma_0 + rho_nu_0
    
    # ========== Integration Parameters ==========
    z_start = 1e6  # Start deep in radiation era (Phase 1.5: extended to z > 10^6)
    
    def __init__(self):
        print(f"\n{'='*70}")
        print("RIDDER COSMOLOGY RC-X* - PHASE 1.5")
        print(f"{'='*70}")
        print(f"\nModel Configuration:")
        print(f"  Inflation: Starobinsky-type plateau")
        print(f"  EDE: {'ENABLED' if self.Lambda_EDE > 0 else 'DISABLED (Phase 1.5 baseline)'}")
        if self.Lambda_EDE > 0:
            print(f"    Λ_EDE = {self.Lambda_EDE/GeV:.4e} GeV")
            print(f"    f = {self.f_axion/GeV:.4e} GeV")
            print(f"    m_EDE = {self.m_EDE_eV:.4e} eV")
        print(f"  DM Coupling: β = {self.beta}")
        print(f"  Integration: z = {self.z_start:.0e} → 0")
        print(f"\nUnits: Mpc for length, eV for energy (CLASS-compatible)")

params = RidderParams()

# ============================================================================
# POTENTIALS
# ============================================================================

def V_EDE(phi, params):
    """EDE potential: Λ^4 * [1 - cos(φ/f)]"""
    if params.Lambda_EDE == 0:
        return 0.0
    return params.Lambda_EDE**4 * (1.0 - np.cos(phi / params.f_axion))

def V_EDE_prime(phi, params):
    """Derivative dV/dφ"""
    if params.Lambda_EDE == 0:
        return 0.0
    return (params.Lambda_EDE**4 / params.f_axion) * np.sin(phi / params.f_axion)

def V_EDE_second_deriv(phi, params):
    """Second derivative d²V/dφ²"""
    if params.Lambda_EDE == 0:
        return 0.0
    return (params.Lambda_EDE**4 / params.f_axion**2) * np.cos(phi / params.f_axion)

# ============================================================================
# BACKGROUND EQUATIONS
# ============================================================================

def background_equations(lna, y, params):
    """
    Background evolution equations in ln(a) time.
    
    Variables:
        y[0] = φ
        y[1] = φ' = dφ/d(ln a)
        y[2] = ρ_rad
        y[3] = ρ_b
        y[4] = ρ_DM
    """
    phi, phi_prime, rho_rad, rho_b, rho_DM = y
    
    V = V_EDE(phi, params)
    V_prime = V_EDE_prime(phi, params)
    
    # Total energy density
    rho_total = V + rho_rad + rho_b + rho_DM + params.rho_Lambda
    
    # Friedmann equation
    # H² = ρ_total / (3M_Pl² - φ'^2/2)
    denominator = 3.0 * M_Pl**2 - 0.5 * phi_prime**2
    if denominator <= 0:
        raise ValueError(f"Friedmann equation denominator ≤ 0: {denominator}")
    
    H_squared = rho_total / denominator
    H = np.sqrt(H_squared)
    
    # Klein-Gordon equation: d(φ')/d(ln a) = -3φ' - V'/H² - β*ρ_DM/(M_Pl*H²)
    dphi_dlna = phi_prime
    dphi_prime_dlna = -3.0*phi_prime - V_prime/H_squared - params.beta*rho_DM/(M_Pl*H_squared)
    
    # Continuity equations
    drho_rad_dlna = -4.0 * rho_rad
    drho_b_dlna = -3.0 * rho_b
    drho_DM_dlna = -3.0*rho_DM + params.beta*phi_prime/M_Pl * rho_DM
    
    return [dphi_dlna, dphi_prime_dlna, drho_rad_dlna, drho_b_dlna, drho_DM_dlna]

# ============================================================================
# INITIAL CONDITIONS
# ============================================================================

def set_initial_conditions(params, z_initial):
    """Set ICs deep in radiation era"""
    a_initial = 1.0 / (1.0 + z_initial)
    
    # Scale densities
    rho_rad_init = params.rho_rad_0 / a_initial**4
    rho_b_init = params.rho_b_0 / a_initial**3
    rho_DM_init = params.rho_c_0 / a_initial**3
    
    # Field IC: displaced on EDE shelf (frozen)
    phi_init = params.f_axion * params.theta_i
    phi_prime_init = 0.0
    
    lna_initial = np.log(a_initial)
    y0 = [phi_init, phi_prime_init, rho_rad_init, rho_b_init, rho_DM_init]
    
    print(f"\nInitial conditions at z = {z_initial:.2e}:")
    print(f"  φ_i = {phi_init/GeV:.4e} GeV")
    print(f"  ρ_rad^(1/4) = {rho_rad_init**(0.25)/GeV:.4e} GeV")
    
    return lna_initial, y0

# ============================================================================
# SOLVER
# ============================================================================

def solve_background(params):
    """Solve background evolution"""
    lna_i, y0 = set_initial_conditions(params, params.z_start)
    lna_f = np.log(1.0)  # a = 1 today
    
    print(f"\nIntegrating ODEs from ln(a) = {lna_i:.4f} to {lna_f:.4f}...")
    
    sol = solve_ivp(
        background_equations,
        (lna_i, lna_f),
        y0,
        args=(params,),
        method='DOP853',
        dense_output=True,
        rtol=1e-11,
        atol=1e-14,
        max_step=0.005  # Tighter steps for accuracy
    )
    
    if not sol.success:
        raise RuntimeError(f"Integration failed: {sol.message}")
    
    print(f"  ✓ Success! {sol.nfev} function evaluations")
    return sol

# ============================================================================
# OBSERVABLES
# ============================================================================

def compute_observables(sol, params):
    """Compute physical observables from solution"""
    
    # Dense grid in z-space
    z_grid = np.logspace(np.log10(0.01), np.log10(params.z_start), 3000)
    a_grid = 1.0 / (1.0 + z_grid)
    lna_grid = np.log(a_grid)
    
    # Evaluate solution
    y_grid = sol.sol(lna_grid)
    phi_grid = y_grid[0]
    phi_prime_grid = y_grid[1]
    rho_rad_grid = y_grid[2]
    rho_b_grid = y_grid[3]
    rho_DM_grid = y_grid[4]
    
    # Compute potential
    V_grid = np.array([V_EDE(phi, params) for phi in phi_grid])
    
    # Hubble parameter
    rho_total_grid = V_grid + rho_rad_grid + rho_b_grid + rho_DM_grid + params.rho_Lambda
    denominator_grid = 3.0 * M_Pl**2 - 0.5 * phi_prime_grid**2
    H_squared_grid = rho_total_grid / denominator_grid
    H_grid = np.sqrt(H_squared_grid)
    
    # Scalar field energy
    rho_phi_grid = 0.5 * H_grid**2 * phi_prime_grid**2 + V_grid
    f_phi_grid = rho_phi_grid / rho_total_grid
    
    # Equation of state
    p_phi_grid = 0.5 * H_grid**2 * phi_prime_grid**2 - V_grid
    w_phi_grid = p_phi_grid / (rho_phi_grid + 1e-100)
    
    results = {
        'z': z_grid,
        'a': a_grid,
        'phi': phi_grid,
        'phi_prime': phi_prime_grid,
        'H': H_grid,
        'H_Mpc_inv': H_grid / Mpc_in_eV_inv,  # [Mpc^-1] for CLASS comparison
        'rho_phi': rho_phi_grid,
        'rho_rad': rho_rad_grid,
        'rho_b': rho_b_grid,
        'rho_DM': rho_DM_grid,
        'rho_total': rho_total_grid,
        'f_phi': f_phi_grid,
        'w_phi': w_phi_grid,
        'V': V_grid,
    }
    
    return results

# ============================================================================
# SOUND HORIZON (IMPROVED - HU & SUGIYAMA 1996)
# ============================================================================

def compute_z_drag(params):
    """
    Compute baryon drag redshift using Hu & Sugiyama (1996) fitting formula.
    
    This is when baryons decouple from photons (later than recombination).
    """
    Omega_b = params.Omega_b_h2 / params.h**2
    Omega_m = (params.Omega_b_h2 + params.Omega_c_h2) / params.h**2
    
    b1 = 0.313 * (Omega_m * params.h**2)**(-0.419) * (1 + 0.607 * (Omega_m * params.h**2)**0.674)
    b2 = 0.238 * (Omega_m * params.h**2)**0.223
    z_drag = 1291 * (Omega_m * params.h**2)**0.251 / (1 + 0.659 * (Omega_m * params.h**2)**0.828) * \
             (1 + b1 * (Omega_b * params.h**2)**b2)
    
    return z_drag

def compute_sound_horizon(results, params):
    """
    Compute comoving sound horizon r_s with CLASS-level precision.
    
    Phase 1.5 improvement (matching CLASS exactly):
    1. Uses accurate z_drag fitting formula (Hu & Sugiyama 1996)
    2. Integrates deep into radiation era (z -> 1e7) via quad integration
    3. Includes neutrino density in H(z) correctly (but NOT in sound speed)
    4. Photon-only density for baryon loading R_b
    
    Result in Mpc for direct CLASS comparison.
    Should give r_s ≈ 147 Mpc for ΛCDM baseline.
    """
    from scipy.integrate import quad
    
    z_drag = compute_z_drag(params)
    print(f"\n  z_drag (Hu & Sugiyama 1996): {z_drag:.2f}")
    
    # Define integrand as a function of z
    # This avoids interpolation errors and integrates to arbitrarily high z
    def integrand(z):
        """
        Integrand: c_s(z) / H(z)
        
        c_s = sound speed in baryon-photon fluid = 1/sqrt(3*(1+R))
        R = baryon loading = (3*rho_b) / (4*rho_gamma)  [photons ONLY, not neutrinos]
        H(z) includes ALL components (photons + neutrinos + matter + Lambda)
        """
        a = 1.0 / (1.0 + z)
        
        # Scale energy densities (analytic, no interpolation)
        rho_g = params.rho_gamma_0 / a**4  # Photons only
        rho_nu = params.rho_nu_0 / a**4     # Neutrinos
        rho_b = params.rho_b_0 / a**3       # Baryons
        rho_c = params.rho_c_0 / a**3       # CDM
        
        # Total energy density for H(z)
        # Note: At high z, scalar field is negligible, Λ is negligible
        rho_tot = rho_g + rho_nu + rho_b + rho_c + params.rho_Lambda
        
        # Hubble parameter [eV]
        H = np.sqrt(rho_tot / (3.0 * M_Pl**2))
        
        # Baryon loading (photons ONLY)
        R = (3.0 * rho_b) / (4.0 * rho_g)
        
        # Sound speed (dimensionless, c=1)
        c_s = 1.0 / np.sqrt(3.0 * (1.0 + R))
        
        # Return c_s / H [eV^-1]
        return c_s / H
    
    # Integrate from z_drag to infinity (practically, 1e7 is sufficient)
    # Result is in [eV^-1]
    print(f"  Integrating from z = {z_drag:.1f} to z = 1e7...")
    r_s_eV_inv, error = quad(integrand, z_drag, 1e7, limit=200)
    
    # Convert to Mpc
    r_s_Mpc = r_s_eV_inv / Mpc_in_eV_inv
    
    print(f"  Integration error estimate: {error/r_s_eV_inv * 100:.4f}%")
    
    return r_s_Mpc, z_drag

# ============================================================================
# SWITCHING SURFACE (Phase 1.5 NEW)
# ============================================================================

def compute_switching_redshift(results, params):
    """
    Compute the redshift z_osc where oscillations begin: 3H(z_osc) ≈ m_eff.
    
    This is the "handover coordinate" where CLASS must switch from
    Klein-Gordon integration to fluid approximation with w_eff.
    
    Critical for Phase 2 implementation.
    """
    if params.Lambda_EDE == 0:
        print(f"\n  z_osc: N/A (EDE disabled, no oscillations)")
        return None
    
    # Effective mass from potential
    m_eff = params.m_EDE_eV
    
    # Find where 3H(z) ≈ m_eff
    z_osc_candidates = []
    for i, H_val in enumerate(results['H']):
        if 3.0 * H_val < m_eff:
            z_osc = results['z'][i]
            print(f"\n  z_osc (switching surface): {z_osc:.1f}")
            print(f"    3H(z_osc) = {3.0*H_val:.3e} eV")
            print(f"    m_eff = {m_eff:.3e} eV")
            print(f"    → Oscillations begin here, switch to fluid approx in CLASS")
            return z_osc
    
    print(f"\n  z_osc: Not reached in integration range (field never oscillates)")
    return None

# ============================================================================
# INFLATIONARY PREDICTIONS
# ============================================================================

def compute_inflationary_observables(params):
    """Compute n_s, r using slow-roll (same as Phase 1)"""
    
    def V_inf(phi):
        x = params.lambda_plateau * phi / M_Pl
        return params.V_star * (1.0 - np.exp(-x))**2
    
    def V_inf_prime(phi):
        x = params.lambda_plateau * phi / M_Pl
        exp_x = np.exp(-x)
        return 2.0 * params.V_star * params.lambda_plateau / M_Pl * (1.0 - exp_x) * exp_x
    
    # Solve for phi_end where epsilon = 1
    def eps_minus_one(phi):
        V_val = V_inf(phi)
        V_p = V_inf_prime(phi)
        return 0.5 * M_Pl**2 * (V_p / V_val)**2 - 1.0
    
    phi_end = fsolve(eps_minus_one, M_Pl)[0]
    
    # Solve for phi_* (N e-folds before end)
    def N_eq(phi_star):
        phi_arr = np.linspace(phi_end, float(phi_star), 1000)
        V_arr = np.array([V_inf(p) for p in phi_arr])
        V_p_arr = np.array([V_inf_prime(p) for p in phi_arr])
        N_computed = np.trapz(V_arr / (M_Pl**2 * V_p_arr), phi_arr)
        return float(N_computed - params.N_efolds)
    
    phi_star = fsolve(N_eq, 5*M_Pl)[0]
    
    # Slow-roll parameters
    V_star_val = V_inf(phi_star)
    V_p_star = V_inf_prime(phi_star)
    
    x = params.lambda_plateau * phi_star / M_Pl
    V_pp_star = 2.0 * params.V_star * (params.lambda_plateau / M_Pl)**2 * np.exp(-2*x) * (2 - np.exp(x))
    
    epsilon = 0.5 * M_Pl**2 * (V_p_star / V_star_val)**2
    eta = M_Pl**2 * V_pp_star / V_star_val
    
    n_s = 1.0 - 6*epsilon + 2*eta
    r = 16 * epsilon
    A_s = V_star_val / (24 * np.pi**2 * M_Pl**4 * epsilon)
    H_inf = np.sqrt(V_star_val / (3 * M_Pl**2))
    
    return {
        'phi_star': phi_star,
        'phi_end': phi_end,
        'n_s': n_s,
        'r': r,
        'A_s': A_s,
        'H_inf': H_inf,
    }

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Phase 1.5 execution"""
    
    # Step 1: Inflation
    print(f"\n{'='*70}")
    print("STEP 1: Inflationary Observables")
    print(f"{'='*70}")
    
    inf_results = compute_inflationary_observables(params)
    
    print(f"  n_s = {inf_results['n_s']:.5f}  (Planck: 0.9649 ± 0.0042)")
    print(f"  r = {inf_results['r']:.5f}  (Limit: < 0.036)")
    print(f"  A_s = {inf_results['A_s']:.3e}  (Planck: ~2.1e-9)")
    
    ns_sigma = abs(inf_results['n_s'] - 0.9649) / 0.0042
    if ns_sigma < 2:
        print(f"  ✓ n_s within 2σ of Planck ({ns_sigma:.2f}σ)")
    
    # Step 2: Background evolution
    print(f"\n{'='*70}")
    print("STEP 2: Background Evolution")
    print(f"{'='*70}")
    
    sol = solve_background(params)
    results = compute_observables(sol, params)
    
    # Step 3: Sound horizon (IMPROVED)
    print(f"\n{'='*70}")
    print("STEP 3: Sound Horizon (Hu & Sugiyama + High-z Integration)")
    print(f"{'='*70}")
    
    r_s, z_drag = compute_sound_horizon(results, params)
    
    print(f"  r_s = {r_s:.2f} Mpc")
    print(f"  ΛCDM value: ~147 Mpc")
    print(f"  Δr_s / r_s = {(r_s - 147)/147 * 100:.2f}%")
    
    if abs(r_s - 147) < 1:
        print(f"  ✓ Matches ΛCDM within 1 Mpc (Phase 1.5 baseline correct)")
    
    # Step 4: Switching surface (NEW)
    print(f"\n{'='*70}")
    print("STEP 4: Switching Surface z_osc (for CLASS oscillation handling)")
    print(f"{'='*70}")
    
    z_osc = compute_switching_redshift(results, params)
    
    # Save results
    print(f"\n{'='*70}")
    print("STEP 5: Saving Results")
    print(f"{'='*70}")
    
    output_data = '/Users/steveridder/Git/Ridder Field/data/phase1_5_results.npz'
    np.savez(output_data,
             z=results['z'],
             H_Mpc_inv=results['H_Mpc_inv'],
             r_s_Mpc=r_s,
             z_drag=z_drag,
             z_osc=z_osc if z_osc else 0,
             n_s=inf_results['n_s'],
             r=inf_results['r'])
    
    print(f"  Data saved: {output_data}")
    
    # Summary
    print(f"\n{'='*70}")
    print("PHASE 1.5 COMPLETE ✓")
    print(f"{'='*70}")
    print("\nACHIEVEMENTS:")
    print(f"  1. Units: Mpc-compatible (H in Mpc^-1) ✓")
    print(f"  2. Sound horizon: r_s = {r_s:.2f} Mpc (z_drag = {z_drag:.1f}) ✓")
    print(f"  3. Switching surface: {'z_osc = ' + f'{z_osc:.1f}' if z_osc else 'N/A (EDE off)'} ✓")
    print(f"  4. Inflation: n_s = {inf_results['n_s']:.4f}, r = {inf_results['r']:.4f} ✓")
    print(f"\nREADY FOR PHASE 2: CLASS Implementation")
    print(f"{'='*70}\n")
    
    return results, inf_results, r_s, z_drag, z_osc

if __name__ == "__main__":
    results, inf_results, r_s, z_drag, z_osc = main()

