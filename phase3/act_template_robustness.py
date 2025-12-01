#!/usr/bin/env python3
"""
ACT Template Fit Robustness Checks
==================================
Uses the SAME methodology as act_template_fit.py but adds subset fits:
1. TT-only fit
2. EE-only fit  
3. Restricted ℓ range (600 < ℓ < 2500)
"""

import numpy as np
import sys
import os
from scipy import linalg

# =============================================
# CRITICAL: CLASS returns dimensionless C_ell
# (normalized by T_CMB²). Must convert to μK²!
# =============================================
T_CMB = 2.7255e6  # μK (2.7255 K in microKelvin)
T_CMB_SQ = T_CMB ** 2  # 7.428e12 μK² - REQUIRED for proper units!

# Import ACT likelihood
try:
    from act_dr6_mflike import ACTDR6MFLike
    HAS_ACT = True
except ImportError:
    HAS_ACT = False
    print("Warning: ACT likelihood not available")


def load_best_fit_from_chain(chain_file):
    """Load best-fit parameters from chain file, including ACT calibration params."""
    data = np.loadtxt(chain_file)
    
    with open(chain_file, 'r') as f:
        header = f.readline()
        cols = header[1:].strip().split() if header.startswith('#') else None
    
    if cols is None:
        raise ValueError("Chain file missing header")
    
    mlp_idx = cols.index('minuslogpost')
    best_idx = np.argmin(data[:, mlp_idx])
    
    params = {}
    # Cosmological parameters
    for i, col in enumerate(cols):
        if col in ['H0', 'n_s', 'omega_b', 'omega_cdm', 'tau_reio', 'Lambda_EDE_ridder']:
            params[col] = data[best_idx, i]
    
    # ACT calibration parameters
    act_cal_keys = ['calG_all', 'cal_dr6_pa4_f220', 'cal_dr6_pa5_f090', 'cal_dr6_pa5_f150',
                    'cal_dr6_pa6_f090', 'cal_dr6_pa6_f150', 'calE_dr6_pa4_f220',
                    'calE_dr6_pa5_f090', 'calE_dr6_pa5_f150', 'calE_dr6_pa6_f090',
                    'calE_dr6_pa6_f150']
    for key in act_cal_keys:
        if key in cols:
            params[key] = data[best_idx, cols.index(key)]
        else:
            params[key] = 1.0  # Default
    
    # Get A_s from logA
    if 'logA' in cols:
        logA_idx = cols.index('logA')
        params['A_s'] = 1e-10 * np.exp(data[best_idx, logA_idx])
    
    return params


def compute_bandpowers_from_class(params, likelihood):
    """
    Compute ACT bandpowers using CLASS + ACT likelihood's internal methods.
    EXACTLY the same as act_template_fit.py
    """
    from classy import Class
    
    # Get required lmax from likelihood
    if hasattr(likelihood, 'l_bpws'):
        required_lmax = int(np.max(likelihood.l_bpws)) + 1
    else:
        required_lmax = 8502
    
    # Set up CLASS
    cosmo = Class()
    
    class_params = {
        'output': 'tCl pCl lCl',
        'l_max_scalars': required_lmax,
        'lensing': 'yes',
        'gauge': 'newtonian',
        'recombination': 'recfast',
        'non_linear': 'none',
        'A_s': params.get('A_s', 2e-9),
        'n_s': params.get('n_s', 0.965),
        'H0': params.get('H0', 68),
        'omega_b': params.get('omega_b', 0.022),
        'omega_cdm': params.get('omega_cdm', 0.12),
        'tau_reio': params.get('tau_reio', 0.054),
    }
    
    # Add EDE parameters if present
    if 'Lambda_EDE_ridder' in params:
        lambda_val = params['Lambda_EDE_ridder']
        class_params.update({
            'Lambda_EDE_ridder': lambda_val,
            'f_axion_ridder': 1.0e+27,
            'theta_i_ridder': 1.0,
            'beta_ridder': 0.0,
            'n_ridder': 3,
        })
    
    cosmo.set(class_params)
    try:
        cosmo.compute()
    except Exception as e:
        print(f"  ERROR: CLASS computation failed: {e}")
        return None
    
    cl = cosmo.lensed_cl(required_lmax)
    cosmo.struct_cleanup()
    
    # Convert to D_ell in μK²
    ell = np.arange(required_lmax + 1)
    factor = ell * (ell + 1) / (2 * np.pi)
    
    D_ell = {}
    D_ell['tt'] = cl['tt'] * factor * T_CMB_SQ
    D_ell['ee'] = cl['ee'] * factor * T_CMB_SQ
    D_ell['te'] = cl['te'] * factor * T_CMB_SQ
    
    # Get all unique tracers from ACT bands
    tracers = set()
    for band_key in likelihood.bands.keys():
        parts = band_key.split('_')
        tracer = '_'.join(parts[:-1])
        tracers.add(tracer)
    tracers = sorted(list(tracers))
    
    # Create dls_dict with ALL tracer combinations
    dls_dict = {}
    for spec in ['tt', 'ee', 'te']:
        for t1 in tracers:
            for t2 in tracers:
                dls_dict[(spec, t1, t2)] = D_ell[spec]
    
    # Get ACT calibration parameters from params dict
    act_params = {}
    for key in ['calG_all', 'cal_dr6_pa4_f220', 'cal_dr6_pa5_f090', 'cal_dr6_pa5_f150',
                'cal_dr6_pa6_f090', 'cal_dr6_pa6_f150', 'calE_dr6_pa4_f220',
                'calE_dr6_pa5_f090', 'calE_dr6_pa5_f150', 'calE_dr6_pa6_f090',
                'calE_dr6_pa6_f150']:
        act_params[key] = params.get(key, 1.0)
    
    # Use ACT likelihood's internal pipeline
    try:
        rotated = likelihood._get_rotated_spectra(dls_dict, **act_params)
        C_b = likelihood._get_ps_vec(rotated)
        return C_b
    except Exception as e:
        print(f"  ERROR: Could not convert to bandpowers: {e}")
        return None


def fit_amplitude(r, t, Cov, mask=None):
    """
    Fit template amplitude: r = A_sh * t + noise
    """
    if mask is not None:
        r = r[mask]
        t = t[mask]
        Cov = Cov[np.ix_(mask, mask)]
    
    try:
        Cov_inv = linalg.inv(Cov)
    except linalg.LinAlgError:
        Cov_inv = linalg.pinv(Cov)
    
    num = t @ (Cov_inv @ r)
    den = t @ (Cov_inv @ t)
    
    A_hat = num / den
    sigma_A = np.sqrt(1.0 / den) if den > 0 else np.inf
    chi2_improvement = A_hat**2 * den
    
    return A_hat, sigma_A, chi2_improvement


def get_spectrum_masks_from_bands(likelihood, n_total):
    """
    Identify which bandpowers are TT vs EE from ACT likelihood bands structure.
    """
    tt_mask = np.zeros(n_total, dtype=bool)
    ee_mask = np.zeros(n_total, dtype=bool)
    te_mask = np.zeros(n_total, dtype=bool)
    ell_b = np.zeros(n_total)
    
    # Get ell values from likelihood
    if hasattr(likelihood, 'ell_b'):
        ell_b = np.array(likelihood.ell_b)
    else:
        # Estimate
        ell_b = np.linspace(600, 4000, n_total)
    
    # Parse bands structure
    idx = 0
    if hasattr(likelihood, 'bands'):
        for band_key in sorted(likelihood.bands.keys()):
            band_data = likelihood.bands[band_key]
            n_bp = len(band_data) if hasattr(band_data, '__len__') else 1
            
            # Extract spectrum type from band key
            # Format: dr6_pa5_f090_dr6_pa5_f090_tt
            parts = band_key.split('_')
            spec_type = parts[-1] if parts[-1] in ['tt', 'ee', 'te'] else 'unknown'
            
            end_idx = min(idx + n_bp, n_total)
            if spec_type == 'tt':
                tt_mask[idx:end_idx] = True
            elif spec_type == 'ee':
                ee_mask[idx:end_idx] = True
            elif spec_type == 'te':
                te_mask[idx:end_idx] = True
            
            idx = end_idx
    
    return tt_mask, ee_mask, te_mask, ell_b


def run_robustness_checks():
    """Run all robustness checks."""
    
    print("=" * 70)
    print("ACT TEMPLATE FIT ROBUSTNESS CHECKS")
    print("=" * 70)
    
    if not HAS_ACT:
        print("ERROR: ACT likelihood not available")
        return None
    
    # Load parameters from chains (same as act_template_fit.py)
    chain_dir = os.path.expanduser("~/Ridder-Field/phase3/chains")
    
    lcdm_files = sorted([f for f in os.listdir(chain_dir) if 'act_world_lcdm' in f and f.endswith('.1.txt')])
    ede_files = sorted([f for f in os.listdir(chain_dir) if 'act_world_ede' in f and f.endswith('.1.txt')])
    
    if not lcdm_files or not ede_files:
        print(f"\nERROR: Need both LCDM and EDE chains!")
        print(f"  LCDM: {len(lcdm_files)} files")
        print(f"  EDE: {len(ede_files)} files")
        return None
    
    print(f"\n1. Loading best-fit parameters from chains...")
    params_lcdm = load_best_fit_from_chain(os.path.join(chain_dir, lcdm_files[0]))
    params_ede = load_best_fit_from_chain(os.path.join(chain_dir, ede_files[0]))
    
    print(f"   LCDM: H0={params_lcdm.get('H0', 'N/A'):.2f}")
    print(f"   EDE:  H0={params_ede.get('H0', 'N/A'):.2f}, Λ={params_ede.get('Lambda_EDE_ridder', 'N/A'):.3f}")
    
    # Initialize likelihood
    print("\n2. Initializing ACT likelihood...")
    likelihood = ACTDR6MFLike({})
    
    d = np.array(likelihood.data_vec)
    Cov = np.array(likelihood.cov)
    print(f"   Data vector: {len(d)} bandpowers")
    print(f"   Covariance: {Cov.shape}")
    
    # Get spectrum masks
    print("\n3. Identifying spectrum types...")
    tt_mask, ee_mask, te_mask, ell_b = get_spectrum_masks_from_bands(likelihood, len(d))
    print(f"   TT bandpowers: {tt_mask.sum()}")
    print(f"   EE bandpowers: {ee_mask.sum()}")
    print(f"   TE bandpowers: {te_mask.sum()}")
    print(f"   ell range: [{ell_b.min():.0f}, {ell_b.max():.0f}]")
    
    # Compute theory bandpowers
    print("\n4. Computing theory bandpowers...")
    print("   ΛCDM...")
    C_b_lcdm = compute_bandpowers_from_class(params_lcdm, likelihood)
    print("   EDE...")
    C_b_ede = compute_bandpowers_from_class(params_ede, likelihood)
    
    if C_b_lcdm is None or C_b_ede is None:
        print("ERROR: Failed to compute bandpowers")
        return None
    
    # Compute residual and template
    residual = d - C_b_lcdm
    template = C_b_ede - C_b_lcdm
    
    print(f"\n   Template stats:")
    print(f"     Max |template|: {np.max(np.abs(template)):.2f} μK²")
    print(f"     Mean |template|: {np.mean(np.abs(template)):.2f} μK²")
    
    # =========================================
    # FIT 1: Full TT+EE (baseline)
    # =========================================
    print("\n" + "=" * 70)
    print("FIT 1: Full TT+EE (baseline)")
    print("=" * 70)
    
    A_full, sigma_full, chi2_full = fit_amplitude(residual, template, Cov)
    SN_full = A_full / sigma_full
    
    print(f"  A_sh = {A_full:.3f} ± {sigma_full:.3f}")
    print(f"  S/N = {SN_full:.2f}")
    print(f"  Δχ² = {chi2_full:.1f}")
    
    # =========================================
    # FIT 2: TT-only
    # =========================================
    print("\n" + "=" * 70)
    print("FIT 2: TT-only")
    print("=" * 70)
    
    if tt_mask.sum() > 10:
        A_tt, sigma_tt, chi2_tt = fit_amplitude(residual, template, Cov, mask=tt_mask)
        SN_tt = A_tt / sigma_tt
        print(f"  N_bandpowers = {tt_mask.sum()}")
        print(f"  A_sh = {A_tt:.3f} ± {sigma_tt:.3f}")
        print(f"  S/N = {SN_tt:.2f}")
        print(f"  Δχ² = {chi2_tt:.1f}")
    else:
        A_tt, sigma_tt, chi2_tt = np.nan, np.nan, np.nan
        SN_tt = np.nan
        print("  (Insufficient TT bandpowers)")
    
    # =========================================
    # FIT 3: EE-only
    # =========================================
    print("\n" + "=" * 70)
    print("FIT 3: EE-only")
    print("=" * 70)
    
    if ee_mask.sum() > 10:
        A_ee, sigma_ee, chi2_ee = fit_amplitude(residual, template, Cov, mask=ee_mask)
        SN_ee = A_ee / sigma_ee
        print(f"  N_bandpowers = {ee_mask.sum()}")
        print(f"  A_sh = {A_ee:.3f} ± {sigma_ee:.3f}")
        print(f"  S/N = {SN_ee:.2f}")
        print(f"  Δχ² = {chi2_ee:.1f}")
    else:
        A_ee, sigma_ee, chi2_ee = np.nan, np.nan, np.nan
        SN_ee = np.nan
        print("  (Insufficient EE bandpowers)")
    
    # =========================================
    # FIT 4: Restricted ℓ range (600 < ℓ < 2500)
    # =========================================
    print("\n" + "=" * 70)
    print("FIT 4: Restricted ℓ range (600 < ℓ < 2500)")
    print("=" * 70)
    
    ell_mask = (ell_b >= 600) & (ell_b <= 2500)
    
    if ell_mask.sum() > 10:
        A_ell, sigma_ell, chi2_ell = fit_amplitude(residual, template, Cov, mask=ell_mask)
        SN_ell = A_ell / sigma_ell
        print(f"  N_bandpowers = {ell_mask.sum()}")
        print(f"  A_sh = {A_ell:.3f} ± {sigma_ell:.3f}")
        print(f"  S/N = {SN_ell:.2f}")
        print(f"  Δχ² = {chi2_ell:.1f}")
    else:
        A_ell, sigma_ell, chi2_ell = np.nan, np.nan, np.nan
        SN_ell = np.nan
        print("  (Insufficient bandpowers in range)")
    
    # =========================================
    # FIT 5: High-ℓ only (ℓ > 2000)
    # =========================================
    print("\n" + "=" * 70)
    print("FIT 5: High-ℓ only (ℓ > 2000)")
    print("=" * 70)
    
    high_ell_mask = ell_b > 2000
    
    if high_ell_mask.sum() > 10:
        A_high, sigma_high, chi2_high = fit_amplitude(residual, template, Cov, mask=high_ell_mask)
        SN_high = A_high / sigma_high
        print(f"  N_bandpowers = {high_ell_mask.sum()}")
        print(f"  A_sh = {A_high:.3f} ± {sigma_high:.3f}")
        print(f"  S/N = {SN_high:.2f}")
        print(f"  Δχ² = {chi2_high:.1f}")
    else:
        A_high, sigma_high, chi2_high = np.nan, np.nan, np.nan
        SN_high = np.nan
        print("  (Insufficient high-ℓ bandpowers)")
    
    # =========================================
    # SUMMARY TABLE
    # =========================================
    print("\n" + "=" * 70)
    print("SUMMARY: ROBUSTNESS CHECKS")
    print("=" * 70)
    
    def fmt(x, prec=2):
        if np.isnan(x):
            return "   ---"
        return f"{x:7.{prec}f}"
    
    print(f"""
┌──────────────────────────┬─────────────┬─────────────┬──────────┬──────────┐
│  Subset                  │   A_sh      │   σ(A_sh)   │   S/N    │   Δχ²    │
├──────────────────────────┼─────────────┼─────────────┼──────────┼──────────┤
│  Full TT+EE (baseline)   │ {fmt(A_full)} │ {fmt(sigma_full)} │ {fmt(SN_full, 1)} │ {fmt(chi2_full, 1)} │
│  TT-only                 │ {fmt(A_tt)} │ {fmt(sigma_tt)} │ {fmt(SN_tt, 1)} │ {fmt(chi2_tt, 1)} │
│  EE-only                 │ {fmt(A_ee)} │ {fmt(sigma_ee)} │ {fmt(SN_ee, 1)} │ {fmt(chi2_ee, 1)} │
│  ℓ ∈ [600, 2500]         │ {fmt(A_ell)} │ {fmt(sigma_ell)} │ {fmt(SN_ell, 1)} │ {fmt(chi2_ell, 1)} │
│  ℓ > 2000 only           │ {fmt(A_high)} │ {fmt(sigma_high)} │ {fmt(SN_high, 1)} │ {fmt(chi2_high, 1)} │
└──────────────────────────┴─────────────┴─────────────┴──────────┴──────────┘
""")
    
    # Interpretation
    print("INTERPRETATION:")
    print("-" * 70)
    
    if not np.isnan(A_tt) and not np.isnan(A_ee):
        diff = abs(A_tt - A_ee)
        combined_sigma = np.sqrt(sigma_tt**2 + sigma_ee**2)
        tension = diff / combined_sigma
        print(f"  TT vs EE consistency: {tension:.1f}σ difference")
        if tension < 2:
            print("    ✓ TT and EE amplitudes are consistent within 2σ")
        else:
            print("    ⚠ TT and EE show some tension")
    
    if not np.isnan(A_ell):
        diff_ell = abs(A_full - A_ell)
        print(f"  Full vs ℓ-restricted: Δ(A_sh) = {diff_ell:.2f}")
        if diff_ell < sigma_full:
            print("    ✓ Detection not dominated by extreme ℓ values")
    
    # Check if baseline is consistent with A_sh ~ 1
    if abs(A_full - 1.0) < 2 * sigma_full:
        print(f"\n  ✓ Baseline A_sh = {A_full:.2f} ± {sigma_full:.2f} is consistent with prediction (A_sh=1)")
    else:
        print(f"\n  Note: Baseline A_sh = {A_full:.2f} differs from prediction by {abs(A_full-1)/sigma_full:.1f}σ")
    
    return {
        'full': (A_full, sigma_full, chi2_full),
        'tt': (A_tt, sigma_tt, chi2_tt),
        'ee': (A_ee, sigma_ee, chi2_ee),
        'ell_restricted': (A_ell, sigma_ell, chi2_ell),
        'high_ell': (A_high, sigma_high, chi2_high),
    }


if __name__ == '__main__':
    results = run_robustness_checks()
