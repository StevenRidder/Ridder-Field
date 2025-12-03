#!/usr/bin/env python3
"""
Single-Point χ² Calculator

Tool 1 from V2_INCREMENTAL_PLAN.md

Purpose: Test CLASS parameters without running expensive MCMC.
Returns: χ², H₀, power spectra, and other observables.

Usage:
    python3 single_point_chi2.py --Lambda_EDE 0.6 --theta_i 2.17 --beta 0.035
    python3 single_point_chi2.py --lcdm  # Test ΛCDM baseline
"""

import argparse
import numpy as np
from cobaya.model import get_model
from cobaya.log import LoggedError
import sys

def create_model_info(Lambda_EDE=0.0, theta_i=2.0, beta=0.0, f_axion=1.0, n_ridder=3):
    """
    Create Cobaya model info dictionary for single-point evaluation.
    
    Parameters:
    -----------
    Lambda_EDE : float
        EDE energy scale (0 = ΛCDM)
    theta_i : float
        Initial field angle
    beta : float
        DM coupling strength
    f_axion : float
        Decay constant in eV
    n_ridder : int
        Potential power
    
    Returns:
    --------
    dict : Cobaya model info
    """
    
    info = {
        'theory': {
            'classy': {
                'extra_args': {
                    'output': 'tCl, mPk, lCl',
                    'l_max_scalars': 2508,
                    'lensing': 'yes',
                    'gauge': 'newtonian',
                    'non_linear': 'none',  # Disable non-linear corrections
                    
                    # Ridder V2 parameters
                    'Lambda_EDE_ridder': Lambda_EDE,
                    'theta_i_ridder': theta_i,
                    'beta_ridder': beta,
                    'f_axion_ridder': f_axion,
                    'n_ridder': n_ridder,
                }
            }
        },
        
        'likelihood': {
            'planck_2018_lowl.TT': None,
            'planck_2018_lowl.EE': None,
            'planck_2018_highl_plik.TTTEEE': None,
            'planck_2018_lensing.clik': None,
        },
        
        'params': {
            # Standard ΛCDM parameters (Planck 2018 best-fit)
            'A_s': 2.1e-9,
            'n_s': 0.965,
            'H0': 67.36,
            'omega_b': 0.02237,
            'omega_cdm': 0.1200,
            'tau_reio': 0.054,
            
            # Planck nuisance parameters (default values)
            'A_planck': 1.0,
            'calib_100T': 0.9992,
            'calib_217T': 0.9985,
            'A_pol': 1.0,
            'calib_100P': 1.021,
            'calib_143P': 0.966,
            'calib_217P': 1.04,
            'cib_index': -1.3,
            'A_cib_217': 67.0,
            'xi_sz_cib': 0.1,
            'A_sz': 7.0,
            'ksz_norm': 0.0,
            'gal545_A_100': 7.0,
            'gal545_A_143': 9.0,
            'gal545_A_143_217': 21.0,
            'gal545_A_217': 80.0,
            'A_sbpx_100_100_TT': 1.0,
            'A_sbpx_143_143_TT': 1.0,
            'A_sbpx_143_217_TT': 1.0,
            'A_sbpx_217_217_TT': 1.0,
            'ps_A_100_100': 257.0,
            'ps_A_143_143': 47.0,
            'ps_A_143_217': 40.0,
            'ps_A_217_217': 104.0,
            'galf_TE_index': -2.4,
            'galf_TE_A_100': 0.13,
            'galf_TE_A_100_143': 0.13,
            'galf_TE_A_100_217': 0.46,
            'galf_TE_A_143': 0.207,
            'galf_TE_A_143_217': 0.69,
            'galf_TE_A_217': 1.938,
            'galf_EE_index': -2.4,
            'galf_EE_A_100': 0.055,
            'galf_EE_A_100_143': 0.04,
            'galf_EE_A_100_217': 0.094,
            'galf_EE_A_143': 0.086,
            'galf_EE_A_143_217': 0.21,
            'galf_EE_A_217': 0.7,
            'A_cnoise_e2e_100_100_EE': 1.0,
            'A_cnoise_e2e_143_143_EE': 1.0,
            'A_cnoise_e2e_217_217_EE': 1.0,
            'A_sbpx_100_100_EE': 1.0,
            'A_sbpx_100_143_EE': 1.0,
            'A_sbpx_100_217_EE': 1.0,
            'A_sbpx_143_143_EE': 1.0,
            'A_sbpx_143_217_EE': 1.0,
            'A_sbpx_217_217_EE': 1.0,
        }
    }
    
    return info


def test_single_point(Lambda_EDE=0.0, theta_i=2.0, beta=0.0, f_axion=1.0, n_ridder=3, verbose=True):
    """
    Test a single point in parameter space.
    
    Returns:
    --------
    dict : Results containing chi2, H0, and other observables
    """
    
    if verbose:
        print("="*70)
        print("SINGLE-POINT χ² TEST")
        print("="*70)
        print(f"Parameters:")
        print(f"  Lambda_EDE = {Lambda_EDE}")
        print(f"  theta_i    = {theta_i}")
        print(f"  beta       = {beta}")
        print(f"  f_axion    = {f_axion} eV")
        print(f"  n_ridder   = {n_ridder}")
        print("")
    
    # Create model
    info = create_model_info(Lambda_EDE, theta_i, beta, f_axion, n_ridder)
    
    try:
        model = get_model(info)
    except LoggedError as e:
        print(f"❌ FAILED: Could not create model")
        print(f"   Error: {e}")
        return {'success': False, 'error': str(e)}
    
    # Get point to evaluate (Planck 2018 best-fit + Ridder params)
    point = {
        'A_s': 2.1e-9,
        'n_s': 0.965,
        'H0': 67.36,
        'omega_b': 0.02237,
        'omega_cdm': 0.1200,
        'tau_reio': 0.054,
    }
    
    if verbose:
        print("Computing χ²...")
    
    try:
        # Compute log-likelihood
        loglike = model.loglike(point)
        chi2 = -2 * loglike[0]
        
        # Get derived parameters
        derived = model.provider.get_param('H0')
        H0 = derived if derived is not None else point['H0']
        
        if verbose:
            print("")
            print("="*70)
            print("RESULTS")
            print("="*70)
            print(f"χ² = {chi2:.2f}")
            print(f"H₀ = {H0:.2f} km/s/Mpc")
            print("")
            
            # Interpret results
            if Lambda_EDE == 0.0:
                print("✅ ΛCDM baseline")
                if chi2 < 2800:
                    print(f"   χ² < 2800 → Good fit")
                else:
                    print(f"   ⚠️  χ² > 2800 → Poor fit")
            else:
                print("✅ V2 model")
                if chi2 < 2800:
                    print(f"   χ² < 2800 → Good fit")
                else:
                    print(f"   ⚠️  χ² > 2800 → Poor fit (model breaks CMB)")
            
            print("="*70)
        
        return {
            'success': True,
            'chi2': chi2,
            'H0': H0,
            'Lambda_EDE': Lambda_EDE,
            'theta_i': theta_i,
            'beta': beta,
        }
        
    except Exception as e:
        print(f"❌ FAILED: Could not compute χ²")
        print(f"   Error: {e}")
        return {'success': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Single-point χ² calculator for V2 validation')
    parser.add_argument('--Lambda_EDE', type=float, default=0.0, help='EDE energy scale (default: 0.0 = ΛCDM)')
    parser.add_argument('--theta_i', type=float, default=2.0, help='Initial field angle (default: 2.0)')
    parser.add_argument('--beta', type=float, default=0.0, help='DM coupling strength (default: 0.0)')
    parser.add_argument('--f_axion', type=float, default=1.0, help='Decay constant in eV (default: 1.0)')
    parser.add_argument('--n_ridder', type=int, default=3, help='Potential power (default: 3)')
    parser.add_argument('--lcdm', action='store_true', help='Test ΛCDM baseline (Lambda_EDE=0)')
    parser.add_argument('--v2_smoke', action='store_true', help='Test V2 with smoke test parameters')
    parser.add_argument('--compare', action='store_true', help='Compare V2 to ΛCDM')
    
    args = parser.parse_args()
    
    if args.lcdm:
        # Test ΛCDM baseline
        result = test_single_point(Lambda_EDE=0.0, theta_i=2.0, beta=0.0)
        
    elif args.v2_smoke:
        # Test V2 with smoke test parameters
        result = test_single_point(Lambda_EDE=0.6, theta_i=2.17, beta=0.035)
        
    elif args.compare:
        # Compare V2 to ΛCDM
        print("\n" + "="*70)
        print("COMPARISON TEST: V2 vs ΛCDM")
        print("="*70 + "\n")
        
        # Test ΛCDM
        print("1. Testing ΛCDM baseline...")
        lcdm_result = test_single_point(Lambda_EDE=0.0, theta_i=2.0, beta=0.0, verbose=True)
        
        print("\n")
        
        # Test V2
        print("2. Testing V2 model...")
        v2_result = test_single_point(Lambda_EDE=0.6, theta_i=2.17, beta=0.035, verbose=True)
        
        # Compare
        if lcdm_result['success'] and v2_result['success']:
            delta_chi2 = v2_result['chi2'] - lcdm_result['chi2']
            delta_H0 = v2_result['H0'] - lcdm_result['H0']
            
            print("\n" + "="*70)
            print("COMPARISON SUMMARY")
            print("="*70)
            print(f"ΛCDM: χ² = {lcdm_result['chi2']:.2f}, H₀ = {lcdm_result['H0']:.2f} km/s/Mpc")
            print(f"V2:   χ² = {v2_result['chi2']:.2f}, H₀ = {v2_result['H0']:.2f} km/s/Mpc")
            print("")
            print(f"Δχ² = {delta_chi2:+.2f}")
            print(f"ΔH₀ = {delta_H0:+.2f} km/s/Mpc")
            print("")
            
            # Interpret
            if abs(delta_chi2) < 10:
                print("✅ PASS: Δχ² < 10 (V2 doesn't break CMB)")
            else:
                print("❌ FAIL: Δχ² > 10 (V2 breaks CMB)")
            
            if delta_H0 > 0:
                print(f"✅ H₀ increases by {delta_H0:.2f} km/s/Mpc (expected for EDE)")
            else:
                print(f"⚠️  H₀ decreases (unexpected)")
            
            print("="*70)
        
    else:
        # Test with user-specified parameters
        result = test_single_point(
            Lambda_EDE=args.Lambda_EDE,
            theta_i=args.theta_i,
            beta=args.beta,
            f_axion=args.f_axion,
            n_ridder=args.n_ridder
        )
    
    # Exit with appropriate code
    if result['success']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()

