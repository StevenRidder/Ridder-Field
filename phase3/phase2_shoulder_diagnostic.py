#!/usr/bin/env python3
"""
Phase 2: ACT DR6 Shoulder Diagnostic

This script computes and visualizes the CMB power spectrum residuals
between ΛCDM and EDE to look for the "soft shoulder" signature.

The EDE field injects energy around z ~ 3000, causing:
1. A slight phase shift in acoustic peaks
2. Amplitude modulation in the damping tail (ℓ > 1000)
3. The characteristic "shoulder" pattern in residuals

Usage:
    python3 phase2_shoulder_diagnostic.py
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Try to import classy
try:
    from classy import Class
    HAS_CLASS = True
except ImportError:
    HAS_CLASS = False
    print("Warning: classy not available. Using pre-computed spectra if available.")


def get_best_fit_params(chain_file):
    """Extract best-fit parameters from MCMC chain."""
    if not Path(chain_file).exists():
        return None
    
    data = np.loadtxt(chain_file, skiprows=1)
    if len(data) == 0:
        return None
    
    # Find minimum -logpost (column 2)
    best_idx = np.argmin(data[:, 1])
    
    # Read header to get parameter names
    with open(chain_file) as f:
        header = f.readline().strip('#').strip().split()
    
    params = {}
    for i, name in enumerate(header):
        if i < len(data[best_idx]):
            params[name] = data[best_idx, i]
    
    return params


def compute_cls_lcdm(params, lmax=4000):
    """Compute Cl's for ΛCDM."""
    if not HAS_CLASS:
        return None, None, None, None
    
    cosmo = Class()
    
    # Handle CAMB parameters (cosmomc_theta) or CLASS parameters
    if 'cosmomc_theta' in params:
        # Convert CAMB theta to CLASS H0 (approximate)
        theta = params['cosmomc_theta']
        # Rough conversion: H0 ≈ 100 * theta / 0.0104 * 67.4
        H0_approx = 100 * theta / 0.0104 * 67.4
        A_s = params.get('As', 2.1e-9)
        ombh2 = params.get('ombh2', 0.02237)
        omch2 = params.get('omch2', 0.12)
        ns = params.get('ns', 0.9649)
        tau = params.get('tau', 0.0544)
    else:
        H0_approx = params.get('H0', 68.9)
        A_s = params.get('A_s', 2.1e-9)
        ombh2 = params.get('omega_b', 0.02237)
        omch2 = params.get('omega_cdm', 0.12)
        ns = params.get('n_s', 0.9649)
        tau = params.get('tau_reio', 0.0544)
    
    # Set ΛCDM parameters
    cosmo.set({
        'output': 'tCl,pCl,lCl',
        'lensing': 'yes',
        'l_max_scalars': lmax + 500,
        'gauge': 'newtonian',
        'A_s': A_s,
        'n_s': ns,
        'H0': H0_approx,
        'omega_b': ombh2,
        'omega_cdm': omch2,
        'tau_reio': tau,
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
    """Compute Cl's for EDE (Ridder field)."""
    if not HAS_CLASS:
        return None, None, None, None
    
    cosmo = Class()
    
    # Handle CAMB or CLASS parameters
    if 'cosmomc_theta' in params:
        theta = params['cosmomc_theta']
        H0_approx = 100 * theta / 0.0104 * 70.0  # EDE typically higher H0
        A_s = params.get('As', 2.1e-9)
        ombh2 = params.get('ombh2', 0.02237)
        omch2 = params.get('omch2', 0.12)
        ns = params.get('ns', 0.9649)
        tau = params.get('tau', 0.0544)
    else:
        H0_approx = params.get('H0', 70.1)
        A_s = params.get('A_s', 2.1e-9)
        ombh2 = params.get('omega_b', 0.02237)
        omch2 = params.get('omega_cdm', 0.12)
        ns = params.get('n_s', 0.9649)
        tau = params.get('tau_reio', 0.0544)
    
    # Set EDE parameters
    cosmo.set({
        'output': 'tCl,pCl,lCl',
        'lensing': 'yes',
        'l_max_scalars': lmax + 500,
        'gauge': 'newtonian',
        'A_s': A_s,
        'n_s': ns,
        'H0': H0_approx,
        'omega_b': ombh2,
        'omega_cdm': omch2,
        'tau_reio': tau,
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
    
    # Convert to D_ell = ell(ell+1)Cl/(2pi) in μK²
    factor = ell * (ell + 1) / (2 * np.pi) * (2.7255e6)**2
    
    tt = cls['tt'] * factor
    ee = cls['ee'] * factor
    te = cls['te'] * factor
    
    cosmo.struct_cleanup()
    cosmo.empty()
    
    return ell, tt, ee, te


def plot_residuals(ell, tt_lcdm, tt_ede, ee_lcdm, ee_ede, output_file='phase2_shoulder.png'):
    """
    Plot fractional residuals: (EDE - ΛCDM) / ΛCDM
    
    The "soft shoulder" will appear as:
    - Oscillating pattern in residuals (phase shift)
    - Systematic offset in damping tail (amplitude change)
    """
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Filter to valid ℓ range
    mask = (ell >= 2) & (ell <= 3500)
    ell = ell[mask]
    tt_lcdm = tt_lcdm[mask]
    tt_ede = tt_ede[mask]
    ee_lcdm = ee_lcdm[mask]
    ee_ede = ee_ede[mask]
    
    # Compute fractional residuals
    delta_tt = (tt_ede - tt_lcdm) / tt_lcdm
    delta_ee = (ee_ede - ee_lcdm) / ee_lcdm
    
    # Top left: TT power spectra
    ax = axes[0, 0]
    ax.semilogy(ell, tt_lcdm, 'b-', label='ΛCDM', alpha=0.8)
    ax.semilogy(ell, tt_ede, 'r-', label='EDE (Ridder)', alpha=0.8)
    ax.set_xlabel(r'$\ell$')
    ax.set_ylabel(r'$D_\ell^{TT}$ [$\mu K^2$]')
    ax.set_title('TT Power Spectrum')
    ax.legend()
    ax.set_xlim(2, 3500)
    ax.axvline(600, color='gray', linestyle='--', alpha=0.5, label='ACT range start')
    
    # Top right: EE power spectra
    ax = axes[0, 1]
    ax.semilogy(ell, ee_lcdm, 'b-', label='ΛCDM', alpha=0.8)
    ax.semilogy(ell, ee_ede, 'r-', label='EDE (Ridder)', alpha=0.8)
    ax.set_xlabel(r'$\ell$')
    ax.set_ylabel(r'$D_\ell^{EE}$ [$\mu K^2$]')
    ax.set_title('EE Power Spectrum')
    ax.legend()
    ax.set_xlim(2, 3500)
    ax.axvline(600, color='gray', linestyle='--', alpha=0.5)
    
    # Bottom left: TT residuals (THE KEY DIAGNOSTIC)
    ax = axes[1, 0]
    ax.plot(ell, delta_tt * 100, 'k-', linewidth=0.8)
    ax.axhline(0, color='blue', linestyle='--', alpha=0.5)
    ax.fill_between(ell, -0.5, 0.5, color='green', alpha=0.2, label='~0.5% ACT precision')
    ax.set_xlabel(r'$\ell$')
    ax.set_ylabel(r'$\Delta D_\ell^{TT} / D_\ell^{TT}$ [%]')
    ax.set_title('TT Fractional Residuals (EDE - ΛCDM) / ΛCDM')
    ax.set_xlim(600, 3500)
    ax.set_ylim(-3, 3)
    ax.axvline(1000, color='orange', linestyle=':', alpha=0.7, label='Damping tail')
    ax.legend()
    
    # Highlight the "shoulder" region
    shoulder_mask = (ell >= 800) & (ell <= 1500)
    if np.any(shoulder_mask):
        ax.fill_between(ell[shoulder_mask], -3, 3, color='red', alpha=0.1, label='Shoulder region')
    
    # Bottom right: EE residuals
    ax = axes[1, 1]
    ax.plot(ell, delta_ee * 100, 'k-', linewidth=0.8)
    ax.axhline(0, color='blue', linestyle='--', alpha=0.5)
    ax.fill_between(ell, -1, 1, color='green', alpha=0.2, label='~1% ACT precision')
    ax.set_xlabel(r'$\ell$')
    ax.set_ylabel(r'$\Delta D_\ell^{EE} / D_\ell^{EE}$ [%]')
    ax.set_title('EE Fractional Residuals (EDE - ΛCDM) / ΛCDM')
    ax.set_xlim(600, 3500)
    ax.set_ylim(-5, 5)
    ax.axvline(1000, color='orange', linestyle=':', alpha=0.7)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def analyze_shoulder_signature(ell, delta_tt, ell_min=800, ell_max=1500):
    """
    Quantify the shoulder signature in the damping tail.
    
    Returns:
        mean_offset: Average residual in shoulder region (%)
        rms_oscillation: RMS of oscillating component (%)
        peak_positions: ℓ values where residuals peak (phase info)
    """
    mask = (ell >= ell_min) & (ell <= ell_max)
    ell_shoulder = ell[mask]
    delta_shoulder = delta_tt[mask] * 100  # Convert to %
    
    # Mean offset
    mean_offset = np.mean(delta_shoulder)
    
    # Remove mean to get oscillating component
    oscillation = delta_shoulder - mean_offset
    rms_oscillation = np.std(oscillation)
    
    # Find peaks (phase shift signature)
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(np.abs(delta_shoulder), distance=50)
    peak_positions = ell_shoulder[peaks] if len(peaks) > 0 else []
    
    return {
        'mean_offset_percent': mean_offset,
        'rms_oscillation_percent': rms_oscillation,
        'peak_ell_values': list(peak_positions),
        'ell_range': (ell_min, ell_max)
    }


def main():
    print("=" * 70)
    print("Phase 2: ACT DR6 Shoulder Diagnostic")
    print("=" * 70)
    
    chains_dir = Path('chains')
    
    # Try to load best-fit parameters from Phase 2 chains
    lcdm_chain = chains_dir / 'phase2_act_lcdm.1.txt'
    ede_chain = chains_dir / 'phase2_act_ede.1.txt'
    
    # Also try Tier 5 EDE chain as proxy
    tier5_ede_chain = chains_dir / 'tier5_ede_shoes_predesi.1.txt'
    
    # Default parameters (Tier 5 results) if chains not available
    lcdm_params = {
        'A_s': 2.1e-9,
        'n_s': 0.9649,
        'H0': 68.9,
        'omega_b': 0.02237,
        'omega_cdm': 0.12,
        'tau_reio': 0.0544,
    }
    
    ede_params = {
        'A_s': 2.1e-9,
        'n_s': 0.9649,
        'H0': 70.1,  # EDE pushes H0 up
        'omega_b': 0.02237,
        'omega_cdm': 0.12,
        'tau_reio': 0.0544,
        'Lambda_EDE_ridder': 1.0,
    }
    
    # Try to load from Phase 2 ACT chains
    if lcdm_chain.exists():
        loaded = get_best_fit_params(str(lcdm_chain))
        if loaded:
            print(f"✓ Loaded Phase 2 ACT LCDM params from {lcdm_chain}")
            lcdm_params.update(loaded)
    
    if ede_chain.exists():
        loaded = get_best_fit_params(str(ede_chain))
        if loaded:
            print(f"✓ Loaded Phase 2 ACT EDE params from {ede_chain}")
            ede_params.update(loaded)
    elif tier5_ede_chain.exists():
        # Use Tier 5 EDE as proxy (similar likelihoods: Planck + BAO + SH0ES)
        loaded = get_best_fit_params(str(tier5_ede_chain))
        if loaded:
            print(f"✓ Using Tier 5 EDE params as proxy (Phase 2 ACT EDE not available)")
            # Extract relevant parameters
            if 'H0' in loaded:
                ede_params['H0'] = loaded['H0']
            if 'A_s' in loaded:
                ede_params['A_s'] = loaded['A_s']
            if 'n_s' in loaded:
                ede_params['n_s'] = loaded['n_s']
            if 'omega_b' in loaded:
                ede_params['omega_b'] = loaded['omega_b']
            if 'omega_cdm' in loaded:
                ede_params['omega_cdm'] = loaded['omega_cdm']
            if 'tau_reio' in loaded:
                ede_params['tau_reio'] = loaded['tau_reio']
            if 'Lambda_EDE_ridder' in loaded:
                ede_params['Lambda_EDE_ridder'] = loaded['Lambda_EDE_ridder']
    
    print("\nΛCDM parameters:")
    for k, v in lcdm_params.items():
        if k in ['H0', 'n_s', 'omega_b', 'omega_cdm', 'tau_reio']:
            print(f"  {k}: {v}")
    
    print("\nEDE parameters:")
    for k, v in ede_params.items():
        if k in ['H0', 'n_s', 'omega_b', 'omega_cdm', 'tau_reio', 'Lambda_EDE_ridder']:
            print(f"  {k}: {v}")
    
    if not HAS_CLASS:
        print("\n⚠️  CLASS not available. Cannot compute power spectra.")
        print("    Install the custom Ridder-modified CLASS to generate diagnostics.")
        return
    
    print("\nComputing ΛCDM power spectra...")
    ell, tt_lcdm, ee_lcdm, te_lcdm = compute_cls_lcdm(lcdm_params)
    
    print("Computing EDE power spectra...")
    _, tt_ede, ee_ede, te_ede = compute_cls_ede(ede_params)
    
    print("\nGenerating residual plots...")
    plot_residuals(ell, tt_lcdm, tt_ede, ee_lcdm, ee_ede, 'phase2_shoulder.png')
    
    # Analyze shoulder signature
    mask = (ell >= 2) & (ell <= 3500)
    delta_tt = (tt_ede[mask] - tt_lcdm[mask]) / tt_lcdm[mask]
    
    signature = analyze_shoulder_signature(ell[mask], delta_tt)
    
    print("\n" + "=" * 70)
    print("SHOULDER SIGNATURE ANALYSIS")
    print("=" * 70)
    print(f"ℓ range analyzed: {signature['ell_range']}")
    print(f"Mean offset: {signature['mean_offset_percent']:.2f}%")
    print(f"RMS oscillation: {signature['rms_oscillation_percent']:.2f}%")
    if signature['peak_ell_values']:
        print(f"Peak positions: {signature['peak_ell_values'][:5]}")
    
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    
    if abs(signature['mean_offset_percent']) < 0.5:
        print("✓ Mean offset < 0.5%: Consistent with ACT TT precision")
    else:
        print("⚠ Mean offset > 0.5%: May be detectable by ACT")
    
    if signature['rms_oscillation_percent'] < 1.0:
        print("✓ RMS oscillation < 1%: Phase shift within noise")
    else:
        print("⚠ RMS oscillation > 1%: Phase shift may be visible")
    
    print("\nThe 'soft shoulder' pattern represents early energy injection")
    print("from the Ridder field around z ~ 3000. ACT DR6 provides the")
    print("precision to constrain this, but CMB-S4 will be definitive.")


if __name__ == '__main__':
    main()
