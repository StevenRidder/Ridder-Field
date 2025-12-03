#!/usr/bin/env python3
"""
Track 2: Template Amplitude Measurement
=======================================
Fits the soft shoulder template amplitude to ACT DR6 data.

This gives you: A_sh, σ(A_sh), and S/N for the shoulder detection.
"""
import numpy as np
import sys
import os
from scipy import linalg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Try to import cobaya/classy for spectrum computation
try:
    from cobaya.model import get_model
    from classy import Class
    HAS_CLASS = True
except ImportError:
    HAS_CLASS = False
    print("Warning: classy not available. Will need pre-computed spectra.")

def load_act_data_and_cov():
    """
    Load ACT DR6 bandpower data and covariance matrix.
    
    Returns:
        d: data vector (bandpowers)
        Cov: covariance matrix
        ell_eff: effective multipoles for each band
        band_info: dict with TT/EE info
    """
    # Try to load from ACT likelihood directory
    act_data_path = os.path.expanduser("~/.local/share/cobaya/data/data/act_dr6")
    
    # Alternative paths
    possible_paths = [
        act_data_path,
        "/home/<VM_USER>/.local/share/cobaya/data/data/act_dr6",
        os.path.join(os.path.dirname(__file__), "../data/act_dr6"),
    ]
    
    # Try to find ACT data
    # This will depend on how ACT likelihood stores data
    # For now, we'll need to extract from the likelihood itself
    
    print("Loading ACT data...")
    print("Note: This requires ACT likelihood to be installed")
    print("We'll extract data from the likelihood object")
    
    # Placeholder - will need to be implemented based on ACT likelihood structure
    return None, None, None, None

def compute_spectra_from_class(params_lcdm, params_ede, lmax=4000):
    """
    Compute C_ell spectra using CLASS.
    
    Args:
        params_lcdm: dict of LCDM parameters
        params_ede: dict of EDE parameters  
        lmax: maximum multipole
    
    Returns:
        ell: array of multipoles
        Cl_TT_LCDM: TT spectrum for LCDM
        Cl_EE_LCDM: EE spectrum for LCDM
        Cl_TT_EDE: TT spectrum for EDE
        Cl_EE_EDE: EE spectrum for EDE
    """
    if not HAS_CLASS:
        raise ImportError("classy not available. Cannot compute spectra.")
    
    print("Computing LCDM spectrum...")
    cosmo_lcdm = Class()
    
    # Set LCDM parameters
    cosmo_lcdm.set({
        'output': 'tCl pCl lCl',
        'l_max_scalars': lmax,
        'lensing': 'yes',
        'A_s': params_lcdm.get('A_s', 2e-9),
        'n_s': params_lcdm.get('n_s', 0.965),
        'H0': params_lcdm.get('H0', 68),
        'omega_b': params_lcdm.get('omega_b', 0.022),
        'omega_cdm': params_lcdm.get('omega_cdm', 0.12),
        'tau_reio': params_lcdm.get('tau_reio', 0.054),
    })
    
    cosmo_lcdm.compute()
    cl_lcdm = cosmo_lcdm.lensed_cl(lmax)
    cosmo_lcdm.struct_cleanup()
    
    print("Computing EDE spectrum...")
    cosmo_ede = Class()
    
    # Set EDE parameters
    cosmo_ede.set({
        'output': 'tCl pCl lCl',
        'l_max_scalars': lmax,
        'lensing': 'yes',
        'A_s': params_ede.get('A_s', 2e-9),
        'n_s': params_ede.get('n_s', 0.965),
        'H0': params_ede.get('H0', 70),
        'omega_b': params_ede.get('omega_b', 0.022),
        'omega_cdm': params_ede.get('omega_cdm', 0.117),
        'tau_reio': params_ede.get('tau_reio', 0.054),
        # Ridder field parameters
        'Lambda_EDE_ridder': params_ede.get('Lambda_EDE_ridder', 0.8),
        'f_axion_ridder': 1.0e+27,
        'theta_i_ridder': 1.0,
        'beta_ridder': 0.0,
        'n_ridder': 3,
    })
    
    cosmo_ede.compute()
    cl_ede = cosmo_ede.lensed_cl(lmax)
    cosmo_ede.struct_cleanup()
    
    ell = np.arange(lmax + 1)
    
    # Extract TT and EE (multiply by ell*(ell+1)/(2*pi) for plotting)
    Cl_TT_LCDM = cl_lcdm['tt'] * ell * (ell + 1) / (2 * np.pi)
    Cl_EE_LCDM = cl_ede['ee'] * ell * (ell + 1) / (2 * np.pi)
    Cl_TT_EDE = cl_ede['tt'] * ell * (ell + 1) / (2 * np.pi)
    Cl_EE_EDE = cl_ede['ee'] * ell * (ell + 1) / (2 * np.pi)
    
    return ell, Cl_TT_LCDM, Cl_EE_LCDM, Cl_TT_EDE, Cl_EE_EDE

def apply_act_windows(Cl_ell, windows):
    """
    Apply ACT window functions to convert C_ell to bandpowers.
    
    Args:
        Cl_ell: C_ell spectrum (array)
        windows: window function matrix (N_bands x N_ell)
    
    Returns:
        C_band: bandpower vector
    """
    return windows @ Cl_ell

def fit_template_amplitude(r, t, Cov):
    """
    Fit template amplitude using optimal linear estimator.
    
    Args:
        r: residual vector (data - LCDM theory)
        t: template vector (EDE - LCDM in bandpower space)
        Cov: covariance matrix
    
    Returns:
        A_hat: best-fit amplitude
        sigma_A: uncertainty on amplitude
        S_N: signal-to-noise ratio
    """
    # Invert covariance
    try:
        Cov_inv = linalg.inv(Cov)
    except linalg.LinAlgError:
        # Use pseudo-inverse if singular
        Cov_inv = linalg.pinv(Cov)
    
    # Optimal linear estimator
    num = t @ (Cov_inv @ r)
    den = t @ (Cov_inv @ t)
    
    A_hat = num / den
    sigma_A = np.sqrt(1.0 / den)
    S_N = A_hat / sigma_A
    
    return A_hat, sigma_A, S_N

def load_params_from_chain(chain_file, model='lcdm'):
    """
    Load best-fit parameters from a chain file.
    
    Args:
        chain_file: path to chain .txt file
        model: 'lcdm' or 'ede'
    
    Returns:
        params: dict of parameter values
    """
    data = np.loadtxt(chain_file)
    
    # Get header
    with open(chain_file, 'r') as f:
        header = f.readline()
        if header.startswith('#'):
            cols = header[1:].strip().split()
        else:
            raise ValueError("Chain file missing header")
    
    # Find best-fit (minimum -logpost)
    mlp_idx = cols.index('minuslogpost')
    best_idx = np.argmin(data[:, mlp_idx])
    
    params = {}
    for i, col in enumerate(cols):
        if col in ['H0', 'n_s', 'omega_b', 'omega_cdm', 'tau_reio', 'A_s', 'Lambda_EDE_ridder']:
            params[col] = data[best_idx, i]
    
    # Convert logA to A_s if needed
    if 'logA' in cols and 'A_s' not in params:
        logA_idx = cols.index('logA')
        params['A_s'] = 1e-10 * np.exp(data[best_idx, logA_idx])
    
    return params

def main():
    """
    Main analysis: Template amplitude fit to ACT data.
    """
    print("=" * 70)
    print("TEMPLATE AMPLITUDE FIT: Soft Shoulder Detection")
    print("=" * 70)
    
    # Step 1: Load best-fit parameters from chains
    chain_dir = os.path.expanduser("~/Ridder-Field/phase3/chains")
    
    lcdm_chain = os.path.join(chain_dir, "act_world_lcdm_c1.1.txt")
    ede_chain = os.path.join(chain_dir, "act_world_ede_c1.1.txt")
    
    if not os.path.exists(lcdm_chain):
        print(f"\nERROR: LCDM chain not found: {lcdm_chain}")
        print("Run Track 1 chains first!")
        return
    
    if not os.path.exists(ede_chain):
        print(f"\nERROR: EDE chain not found: {ede_chain}")
        print("Run Track 1 chains first!")
        return
    
    print("\nStep 1: Loading best-fit parameters...")
    params_lcdm = load_params_from_chain(lcdm_chain, 'lcdm')
    params_ede = load_params_from_chain(ede_chain, 'ede')
    
    print(f"  LCDM: H0={params_lcdm.get('H0', 'N/A'):.2f}, n_s={params_lcdm.get('n_s', 'N/A'):.3f}")
    print(f"  EDE:  H0={params_ede.get('H0', 'N/A'):.2f}, Λ_EDE={params_ede.get('Lambda_EDE_ridder', 'N/A'):.3f}")
    
    # Step 2: Compute spectra
    if HAS_CLASS:
        print("\nStep 2: Computing C_ell spectra with CLASS...")
        ell, Cl_TT_LCDM, Cl_EE_LCDM, Cl_TT_EDE, Cl_EE_EDE = compute_spectra_from_class(
            params_lcdm, params_ede, lmax=4000
        )
        
        # Define template
        DeltaCl_TT = Cl_TT_EDE - Cl_TT_LCDM
        DeltaCl_EE = Cl_EE_EDE - Cl_EE_LCDM
        
        print("  Template defined: ΔC_ell = C_ell(EDE) - C_ell(LCDM)")
    else:
        print("\nStep 2: CLASS not available. Need pre-computed spectra.")
        print("  Please provide C_ell files or install classy.")
        return
    
    # Step 3: Load ACT data and windows
    print("\nStep 3: Loading ACT DR6 data and window functions...")
    d, Cov, ell_eff, band_info = load_act_data_and_cov()
    
    if d is None:
        print("  ERROR: Could not load ACT data.")
        print("  This requires the ACT likelihood to be properly installed.")
        print("  You may need to extract data from the likelihood object directly.")
        return
    
    # Step 4: Apply ACT windows to get bandpower predictions
    print("\nStep 4: Applying ACT window functions...")
    # This requires the actual ACT window function files
    # For now, placeholder
    
    # Step 5: Build residual and template vectors
    print("\nStep 5: Building residual and template vectors...")
    # r = d - C_b_LCDM
    # t = DeltaC_b
    
    # Step 6: Fit amplitude
    print("\nStep 6: Fitting template amplitude...")
    # A_hat, sigma_A, S_N = fit_template_amplitude(r, t, Cov)
    
    # Step 7: Report results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    # print(f"A_sh = {A_hat:.3f} ± {sigma_A:.3f}")
    # print(f"S/N = {S_N:.2f}")
    # 
    # if abs(A_hat - 1.0) < 2 * sigma_A:
    #     print("\n✅ SHOULDER DETECTED: A_sh consistent with Ridder field prediction!")
    # elif abs(A_hat) < 2 * sigma_A:
    #     print("\n📊 ACT NEUTRAL: Consistent with both LCDM and EDE")
    # else:
    #     print("\n❌ NO SHOULDER: ACT disfavors the predicted pattern")
    
    print("\nNote: Full implementation requires ACT window functions and data extraction.")
    print("See ACT likelihood documentation for data access methods.")

if __name__ == "__main__":
    main()
