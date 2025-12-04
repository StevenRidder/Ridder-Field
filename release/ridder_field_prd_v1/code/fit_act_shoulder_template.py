#!/usr/bin/env python3
"""
ACT Shoulder Template-Amplitude Fit

This script implements the template-amplitude analysis:
1. Define shoulder template S_ℓ from Planck-calibrated theory (EDE - ΛCDM)
2. Fit single amplitude α to ACT DR6 data
3. Report α, σ(α), and S/N

The template shape comes from Planck+BAO+SH0ES best-fits (NOT ACT).
ACT only measures the amplitude.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Try to import required modules
try:
    from classy import Class
    HAS_CLASS = True
except ImportError:
    HAS_CLASS = False
    print("Warning: classy not available. Need custom Ridder CLASS.")

try:
    import sacc
    HAS_SACC = True
except ImportError:
    HAS_SACC = False
    print("Warning: sacc not available for ACT data loading.")

REPO_ROOT = Path(__file__).parent
CHAIN_DIR = REPO_ROOT / "chains"


def get_best_fit_params(chain_file):
    """Extract best-fit parameters from MCMC chain."""
    if not chain_file.exists():
        return None
    
    try:
        data = np.loadtxt(chain_file, skiprows=1)
        if len(data) == 0:
            return None
        
        # Find minimum -logpost (column 1)
        best_idx = np.argmin(data[:, 1])
        
        # Read header
        with open(chain_file) as f:
            header = f.readline().strip('#').strip().split()
        
        params = {}
        for i, name in enumerate(header):
            if i < len(data[best_idx]):
                params[name] = data[best_idx, i]
        
        return params
    except Exception as e:
        print(f"Error loading {chain_file}: {e}")
        return None


def compute_cls_lcdm(params, lmax=4000):
    """Compute Cl's for ΛCDM using CLASS."""
    if not HAS_CLASS:
        return None, None, None, None
    
    cosmo = Class()
    
    # Set parameters
    cosmo.set({
        'output': 'tCl,pCl,lCl',
        'lensing': 'yes',
        'l_max_scalars': lmax + 500,
        'gauge': 'newtonian',
        'A_s': params.get('A_s', 2.1e-9),
        'n_s': params.get('n_s', 0.9649),
        'H0': params.get('H0', 68.9),
        'omega_b': params.get('omega_b', 0.02237),
        'omega_cdm': params.get('omega_cdm', 0.12),
        'tau_reio': params.get('tau_reio', 0.0544),
    })
    
    cosmo.compute()
    cls = cosmo.lensed_cl(lmax)
    ell = cls['ell']
    
    # Convert to D_ell = ell(ell+1)Cl/(2pi) in μK²
    factor = ell * (ell + 1) / (2 * np.pi) * (2.7255e6)**2
    
    tt = cls['tt'] * factor
    ee = cls['ee'] * factor
    te = cls['te'] * factor
    
    cosmo.struct_cleanup()
    cosmo.empty()
    
    return ell, tt, ee, te


def compute_cls_ede(params, lmax=4000):
    """Compute Cl's for EDE (Ridder field) using CLASS."""
    if not HAS_CLASS:
        return None, None, None, None
    
    cosmo = Class()
    
    # Set parameters
    cosmo.set({
        'output': 'tCl,pCl,lCl',
        'lensing': 'yes',
        'l_max_scalars': lmax + 500,
        'gauge': 'newtonian',
        'A_s': params.get('A_s', 2.1e-9),
        'n_s': params.get('n_s', 0.9649),
        'H0': params.get('H0', 70.1),
        'omega_b': params.get('omega_b', 0.02237),
        'omega_cdm': params.get('omega_cdm', 0.12),
        'tau_reio': params.get('tau_reio', 0.0544),
        # Ridder field parameters
        'Lambda_EDE_ridder': params.get('Lambda_EDE_ridder', 1.0),
        'n_ridder': 3,
        'theta_i_ridder': 1.0,
        'beta_ridder': 0.0,
        'f_axion_ridder': 1.0e27,
    })
    
    cosmo.compute()
    cls = cosmo.lensed_cl(lmax)
    ell = cls['ell']
    
    # Convert to D_ell
    factor = ell * (ell + 1) / (2 * np.pi) * (2.7255e6)**2
    
    tt = cls['tt'] * factor
    ee = cls['ee'] * factor
    te = cls['te'] * factor
    
    cosmo.struct_cleanup()
    cosmo.empty()
    
    return ell, tt, ee, te


def load_act_data():
    """Load ACT DR6 bandpowers and covariance."""
    # ACT data path (adjust as needed)
    act_data_path = Path.home() / ".local/share/cobaya/data/data/ACTDR6MFLike/v1.0"
    
    if not act_data_path.exists():
        print(f"Warning: ACT data not found at {act_data_path}")
        return None, None, None
    
    # Try to load SACC file
    sacc_files = list(act_data_path.glob("*.sacc"))
    if not sacc_files:
        print("Warning: No .sacc files found in ACT data directory")
        return None, None, None
    
    try:
        s = sacc.Sacc.load_fits(str(sacc_files[0]))
        
        # Extract TT, EE, TE bandpowers
        # This is simplified - actual implementation needs proper binning
        ell_act = []
        tt_act = []
        ee_act = []
        te_act = []
        
        # Get data points (simplified - need proper binning)
        for tr in s.tracers:
            if 'TT' in tr.name:
                ell_act.append(tr.ell)
                tt_act.append(tr.value)
            elif 'EE' in tr.name:
                ee_act.append(tr.value)
            elif 'TE' in tr.name:
                te_act.append(tr.value)
        
        # Get covariance
        cov = s.covariance.covmat
        
        return np.array(ell_act), np.array(tt_act), np.array(ee_act), np.array(te_act), cov
    
    except Exception as e:
        print(f"Error loading ACT data: {e}")
        return None, None, None, None, None


def fit_template_amplitude(ell_template, s_tt, s_ee, ell_act, d_tt, d_ee, cov, lmin=600, lmax=3000):
    """
    Fit amplitude α of template S_ℓ to ACT data.
    
    Model: C_ℓ(α) = C_ℓ^ΛCDM + α * S_ℓ
    
    Returns: α_best, σ_α, S/N
    """
    # Interpolate template to ACT ℓ grid
    mask_act = (ell_act >= lmin) & (ell_act <= lmax)
    ell_act_masked = ell_act[mask_act]
    
    # Interpolate template
    s_tt_interp = np.interp(ell_act_masked, ell_template, s_tt)
    s_ee_interp = np.interp(ell_act_masked, ell_template, s_ee)
    
    # Combine TT and EE into single vector
    s_vec = np.concatenate([s_tt_interp, s_ee_interp])
    d_vec = np.concatenate([d_tt[mask_act], d_ee[mask_act]])
    
    # Extract relevant covariance block
    n_act = len(ell_act_masked)
    cov_block = cov[:n_act*2, :n_act*2]  # Simplified - need proper indexing
    
    # Linear regression: α = (S^T C^-1 S)^-1 (S^T C^-1 d)
    cov_inv = np.linalg.inv(cov_block)
    
    alpha_best = (s_vec.T @ cov_inv @ d_vec) / (s_vec.T @ cov_inv @ s_vec)
    sigma_alpha = 1.0 / np.sqrt(s_vec.T @ cov_inv @ s_vec)
    snr = abs(alpha_best) / sigma_alpha
    
    return alpha_best, sigma_alpha, snr


def main():
    print("=" * 70)
    print("ACT SHOULDER TEMPLATE-AMPLITUDE FIT")
    print("=" * 70)
    
    # Load best-fit parameters from Planck-calibrated chains (NOT ACT chains)
    print("\n1. Loading Planck-calibrated best-fits...")
    
    # Try Tier 5 chains (Planck + BAO + SH0ES, no ACT)
    lcdm_chain = CHAIN_DIR / "tier5_lcdm_shoes_predesi.1.txt"
    ede_chain = CHAIN_DIR / "tier5_ede_shoes_predesi.1.txt"
    
    lcdm_params = get_best_fit_params(lcdm_chain)
    ede_params = get_best_fit_params(ede_chain)
    
    if not lcdm_params or not ede_params:
        print("Error: Could not load best-fit parameters")
        print(f"  LCDM chain: {lcdm_chain.exists()}")
        print(f"  EDE chain: {ede_chain.exists()}")
        return
    
    print(f"✓ Loaded LCDM best-fit: H0={lcdm_params.get('H0', 'N/A'):.2f}")
    print(f"✓ Loaded EDE best-fit: H0={ede_params.get('H0', 'N/A'):.2f}, Λ_EDE={ede_params.get('Lambda_EDE_ridder', 'N/A'):.2f}")
    
    # Compute spectra
    print("\n2. Computing Planck-calibrated spectra...")
    if not HAS_CLASS:
        print("Error: CLASS not available")
        return
    
    ell, tt_lcdm, ee_lcdm, te_lcdm = compute_cls_lcdm(lcdm_params, lmax=3000)
    _, tt_ede, ee_ede, te_ede = compute_cls_ede(ede_params, lmax=3000)
    
    # Define template: S_ℓ = C_ℓ^EDE - C_ℓ^ΛCDM
    print("\n3. Defining shoulder template S_ℓ...")
    mask = (ell >= 600) & (ell <= 3000)
    ell_template = ell[mask]
    
    s_tt = (tt_ede[mask] - tt_lcdm[mask])  # Template in μK²
    s_ee = (ee_ede[mask] - ee_lcdm[mask])
    
    print(f"  Template range: ℓ ∈ [{ell_template[0]}, {ell_template[-1]}]")
    print(f"  TT template RMS: {np.sqrt(np.mean(s_tt**2)):.2f} μK²")
    print(f"  EE template RMS: {np.sqrt(np.mean(s_ee**2)):.2f} μK²")
    
    # Load ACT data
    print("\n4. Loading ACT DR6 data...")
    act_result = load_act_data()
    
    if act_result[0] is None:
        print("  ⚠️  ACT data not available - using simulated analysis")
        print("  (Template fit requires actual ACT bandpowers)")
        print("\n  Template statistics:")
        print(f"    α = 1.0 corresponds to full Ridder shoulder")
        print(f"    α = 0.0 corresponds to pure ΛCDM")
        print(f"    Template amplitude: {np.max(np.abs(s_tt)):.2f} μK² at peak")
        return
    
    ell_act, tt_act, ee_act, te_act, cov = act_result
    
    # Fit amplitude
    print("\n5. Fitting template amplitude α to ACT data...")
    alpha_best, sigma_alpha, snr = fit_template_amplitude(
        ell_template, s_tt, s_ee, ell_act, tt_act, ee_act, cov
    )
    
    print("\n" + "=" * 70)
    print("TEMPLATE-AMPLITUDE FIT RESULTS")
    print("=" * 70)
    print(f"Best-fit amplitude: α = {alpha_best:.3f} ± {sigma_alpha:.3f}")
    print(f"Signal-to-noise: S/N = {snr:.2f}")
    print(f"\nInterpretation:")
    print(f"  α = 0.0: Pure ΛCDM (no shoulder)")
    print(f"  α = 1.0: Full Ridder shoulder (H₀ ≈ 70)")
    print(f"  α = {alpha_best:.3f}: ACT prefers {alpha_best:.1%} of full shoulder")
    
    if abs(alpha_best) < sigma_alpha:
        print(f"  → ACT is consistent with no shoulder (α ≈ 0)")
    elif abs(alpha_best - 1.0) < sigma_alpha:
        print(f"  → ACT is consistent with full shoulder (α ≈ 1)")
    else:
        print(f"  → ACT prefers intermediate amplitude")
    
    if snr > 2:
        print(f"  → S/N > 2: ACT shows preference for shoulder pattern")
    else:
        print(f"  → S/N < 2: Current ACT precision insufficient for detection")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
