#!/usr/bin/env python3
"""
ACT Template Amplitude Fit
==========================
Extracts ACT DR6 data from likelihood and fits shoulder template amplitude.

This implements Track 2: Template measurement of the soft shoulder.
"""
import numpy as np
import sys
import os
from scipy import linalg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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

def extract_act_data_from_likelihood(likelihood=None):
    """
    Extract ACT bandpower data and covariance from the likelihood object.
    
    Args:
        likelihood: ACT likelihood object (if None, will create one)
    
    Returns:
        d: data vector
        Cov: covariance matrix
        ell_eff: effective multipoles
        windows: window functions (if available)
    """
    if not HAS_ACT:
        raise ImportError("ACT likelihood not available")
    
    if likelihood is None:
        print("Initializing ACT likelihood...")
        likelihood = ACTDR6MFLike({})
    else:
        print("Using provided ACT likelihood object...")
    
    # Try to access data
    # This depends on the ACT likelihood implementation
    # Common attributes: data, covariance, windows
    
    try:
        # ACT DR6 mflike stores data directly in attributes
        # Found: data_vec (1651,), cov (1651, 1651)
        
        # Get data vector
        if hasattr(likelihood, 'data_vec'):
            d = np.array(likelihood.data_vec)
            print(f"  Found data_vec: {d.shape}")
        elif hasattr(likelihood, 'data'):
            # data is a dict, try to extract vector
            data_dict = likelihood.data
            if isinstance(data_dict, dict):
                # Try to find the actual vector in the dict
                for key, val in data_dict.items():
                    if hasattr(val, 'shape') and len(val.shape) == 1:
                        d = np.array(val)
                        break
                else:
                    raise AttributeError("Cannot extract data vector from data dict")
            else:
                d = np.array(data_dict)
        else:
            raise AttributeError("Cannot find ACT data vector")
        
        # Get covariance
        if hasattr(likelihood, 'cov'):
            Cov = np.array(likelihood.cov)
            print(f"  Found covariance: {Cov.shape}")
        elif hasattr(likelihood, 'covariance'):
            Cov = np.array(likelihood.covariance)
        else:
            raise AttributeError("Cannot find ACT covariance")
        
        # Get window functions (Bbl matrices)
        windows = None
        if hasattr(likelihood, 'Bbl'):
            windows = likelihood.Bbl
            print(f"  Found Bbl windows: {type(windows)}")
        elif hasattr(likelihood, 'bandpower_windows'):
            windows = likelihood.bandpower_windows
        elif hasattr(likelihood, 'windows'):
            windows = likelihood.windows
        elif hasattr(likelihood, 'cov_Bbl_file') and likelihood.cov_Bbl_file:
            # Try to load from file
            try:
                import sacc
                sacc_data = sacc.Sacc.load_fits(likelihood.cov_Bbl_file)
                windows = sacc_data.get_bandpower_windows()
                print(f"  Loaded windows from file: {likelihood.cov_Bbl_file}")
            except:
                pass
        
        # Get effective ells
        ell_eff = None
        if hasattr(likelihood, 'ell'):
            ell_eff = likelihood.ell
        elif hasattr(likelihood, 'ell_eff'):
            ell_eff = likelihood.ell_eff
        
        # Get band information to understand TT/EE structure
        bands_info = None
        if hasattr(likelihood, 'bands'):
            bands_info = likelihood.bands
            print(f"  Found bands info: {len(bands_info)} bands")
        
        print(f"  Data vector: {len(d)} bandpowers")
        print(f"  Covariance: {Cov.shape}")
        if windows is not None:
            if hasattr(windows, 'shape'):
                print(f"  Windows: {windows.shape}")
            else:
                print(f"  Windows: {type(windows)}")
        else:
            print(f"  Windows: Not found (will use raw C_ell)")
        
        return d, Cov, ell_eff, windows
        
    except Exception as e:
        print(f"Error extracting ACT data: {e}")
        print("You may need to access ACT data files directly")
        return None, None, None, None

def compute_bandpowers_from_class(params, likelihood=None):
    """
    Compute ACT bandpowers from CLASS spectrum using ACT likelihood's internal method.
    Uses CLASS directly but with proper unit handling.
    """
    from classy import Class
    
    if likelihood is None:
        raise ValueError("Need ACT likelihood object for bandpower conversion")
    
    # Get required lmax from likelihood
    if hasattr(likelihood, 'l_bpws'):
        required_lmax = int(np.max(likelihood.l_bpws)) + 1
    else:
        required_lmax = 8502
    
    print(f"  Computing C_ell up to lmax={required_lmax}")
    
    # Set up CLASS - use same settings as chain configs
    cosmo = Class()
    
    class_params = {
        'output': 'tCl pCl lCl',
        'l_max_scalars': required_lmax,
        'lensing': 'yes',
        'gauge': 'newtonian',
        'recombination': 'recfast',  # Match chain config
        'non_linear': 'none',  # Match chain config
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
        print(f"  DEBUG: Using Lambda_EDE_ridder = {lambda_val:.6f}")
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
    
    # Get raw Cl (not lensed) and lens manually, or use lensed_cl
    # Try both to see which gives reasonable values
    try:
        cl_raw = cosmo.raw_cl(required_lmax)
        cl_lensed = cosmo.lensed_cl(required_lmax)
        # Use lensed (standard for CMB)
        cl = cl_lensed
    except:
        try:
            cl = cosmo.lensed_cl(required_lmax)
        except Exception as e:
            print(f"  ERROR: Failed to get Cl: {e}")
            cosmo.struct_cleanup()
            return None
    
    cosmo.struct_cleanup()
    
    # CLASS returns DIMENSIONLESS C_ell (normalized by T_CMB²)
    # Raw values are ~10^-10 to 10^-15 - this is correct!
    print(f"  DEBUG: Raw C_ell[100] = {cl['tt'][100]:.6e} (dimensionless)")
    print(f"  DEBUG: Raw C_ell[500] = {cl['tt'][500]:.6e} (dimensionless)")
    
    # Convert to D_ell in μK²:
    # D_ell = ell*(ell+1)/(2π) * C_ell * T_CMB²
    # Where T_CMB = 2.7255e6 μK, so T_CMB² = 7.428e12 μK²
    ell = np.arange(required_lmax + 1)
    factor = ell * (ell + 1) / (2 * np.pi)
    
    D_ell = {}
    D_ell['tt'] = cl['tt'] * factor * T_CMB_SQ
    D_ell['ee'] = cl['ee'] * factor * T_CMB_SQ
    D_ell['te'] = cl['te'] * factor * T_CMB_SQ
    
    # Now D_ell should be in μK² with reasonable values
    print(f"  DEBUG: D_ell[100] = {D_ell['tt'][100]:.2f} μK² (expected ~2000)")
    print(f"  DEBUG: D_ell[500] = {D_ell['tt'][500]:.2f} μK² (expected ~2500)")
    print(f"  DEBUG: Max D_ell = {np.max(D_ell['tt'][2:]):.2f} μK² (expected ~6000)")
    
    # Sanity check: D_ell should be order 1000 μK² - if not, something is wrong
    if D_ell['tt'][500] < 100 or D_ell['tt'][500] > 100000:
        print(f"  ⚠️  WARNING: D_ell values look wrong! Check T_CMB conversion.")
    else:
        print(f"  ✓ D_ell values look reasonable")
    
    # Get all unique tracers from ACT bands
    tracers = set()
    for band_key in likelihood.bands.keys():
        parts = band_key.split('_')
        tracer = '_'.join(parts[:-1])  # e.g., 'dr6_pa5_f150'
        tracers.add(tracer)
    tracers = sorted(list(tracers))
    
    # Create dls_dict with ALL tracer combinations (needed for cross-correlations)
    # Format: {(spectrum, tracer1, tracer2): D_ell_array}
    # ACT expects D_ell, not C_ell
    dls_dict = {}
    for spec in ['tt', 'ee', 'te']:
        for t1 in tracers:
            for t2 in tracers:
                # Use the appropriate D_ell spectrum
                dls_dict[(spec, t1, t2)] = D_ell[spec]
    
    # Get ACT calibration parameters
    act_params = {}
    for key in ['calG_all', 'cal_dr6_pa4_f220', 'cal_dr6_pa5_f090', 'cal_dr6_pa5_f150',
                'cal_dr6_pa6_f090', 'cal_dr6_pa6_f150', 'calE_dr6_pa4_f220',
                'calE_dr6_pa5_f090', 'calE_dr6_pa5_f150', 'calE_dr6_pa6_f090',
                'calE_dr6_pa6_f150']:
        act_params[key] = params.get(key, 1.0)  # Default calibration = 1.0
    
    # Use ACT likelihood's internal pipeline:
    # 1. _get_rotated_spectra: applies calibrations
    # 2. _get_ps_vec: converts to bandpowers (handles window functions)
    try:
        rotated = likelihood._get_rotated_spectra(dls_dict, **act_params)
        C_b = likelihood._get_ps_vec(rotated)
        print(f"  Converted to {len(C_b)} bandpowers using ACT window functions")
        return C_b
    except Exception as e:
        print(f"  ERROR: Could not convert to bandpowers: {e}")
        import traceback
        traceback.print_exc()
        return None

def fit_amplitude(r, t, Cov):
    """
    Fit template amplitude: r = A_sh * t + noise
    
    Returns: A_hat, sigma_A, S/N
    """
    try:
        Cov_inv = linalg.inv(Cov)
    except linalg.LinAlgError:
        Cov_inv = linalg.pinv(Cov)
    
    num = t @ (Cov_inv @ r)
    den = t @ (Cov_inv @ t)
    
    A_hat = num / den
    sigma_A = np.sqrt(1.0 / den) if den > 0 else np.inf
    S_N = A_hat / sigma_A if sigma_A > 0 else 0
    
    return A_hat, sigma_A, S_N

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
    
    # Handle logA -> A_s
    if 'logA' in cols:
        logA_idx = cols.index('logA')
        params['A_s'] = 1e-10 * np.exp(data[best_idx, logA_idx])
    
    return params

def main():
    print("=" * 70)
    print("ACT TEMPLATE AMPLITUDE FIT")
    print("=" * 70)
    
    # Load parameters from chains
    chain_dir = os.path.expanduser("~/Ridder-Field/phase3/chains")
    
    lcdm_files = sorted([f for f in os.listdir(chain_dir) if 'act_world_lcdm' in f and f.endswith('.1.txt')])
    ede_files = sorted([f for f in os.listdir(chain_dir) if 'act_world_ede' in f and f.endswith('.1.txt')])
    
    # Check if EDE chains are still in burn-in
    if not ede_files:
        print("\n⚠️  EDE ACT+Planck chains not ready yet (still in burn-in)")
        print(f"  Found LCDM: {len(lcdm_files)} files ✅")
        print(f"  Found EDE: {len(ede_files)} files ⏳")
        print("\n  EDE chains should finish burn-in in ~10-15 minutes.")
        print("  Check status with: bash check_chains.sh")
        print("\n  Alternatively, you can use tier5 chains for testing:")
        print("    python3 act_template_fit.py --use-tier5")
        return
    
    if not lcdm_files:
        print("\nERROR: Need LCDM ACT+Planck chains from Track 1!")
        print(f"  Looking in: {chain_dir}")
        print(f"  Found LCDM: {len(lcdm_files)} files")
        return
    
    print(f"\nLoading best-fit parameters from chains...")
    params_lcdm = load_best_fit_from_chain(os.path.join(chain_dir, lcdm_files[0]))
    params_ede = load_best_fit_from_chain(os.path.join(chain_dir, ede_files[0]))
    
    print(f"  LCDM: H0={params_lcdm.get('H0', 'N/A'):.2f}")
    print(f"  EDE:  H0={params_ede.get('H0', 'N/A'):.2f}, Λ={params_ede.get('Lambda_EDE_ridder', 'N/A'):.3f}")
    
    # Extract ACT data
    if not HAS_ACT:
        print("\nERROR: ACT likelihood not available!")
        print("Install act_dr6_mflike to proceed.")
        return
    
    print("\nExtracting ACT DR6 data from likelihood...")
    likelihood_obj = ACTDR6MFLike({})  # Initialize once, reuse for data and conversion
    d, Cov, ell_eff, windows = extract_act_data_from_likelihood(likelihood_obj)
    
    if d is None:
        print("Could not extract ACT data. Check likelihood installation.")
        return
    
    # Compute bandpowers using ACT's internal method (handles window functions)
    print("\nComputing LCDM bandpowers from CLASS...")
    C_b_lcdm = compute_bandpowers_from_class(params_lcdm, likelihood_obj)
    
    if C_b_lcdm is None:
        print("ERROR: Could not compute LCDM bandpowers")
        return
    
    print("Computing EDE bandpowers from CLASS...")
    C_b_ede = compute_bandpowers_from_class(params_ede, likelihood_obj)
    
    if C_b_ede is None:
        print("ERROR: Could not compute EDE bandpowers")
        return
    
    # Verify dimensions match (should all be 1651)
    if len(C_b_lcdm) != len(d) or len(C_b_ede) != len(d):
        print(f"ERROR: Dimension mismatch!")
        print(f"  ACT data: {len(d)}")
        print(f"  LCDM bandpowers: {len(C_b_lcdm)}")
        print(f"  EDE bandpowers: {len(C_b_ede)}")
        return
    
    print(f"\n✓ All vectors have length {len(d)} (bandpower space)")
    
    # DEBUG: Check bandpower values before template
    print("\nDEBUG: Bandpower comparison...")
    print(f"  LCDM bandpowers: min={np.min(C_b_lcdm):.6e}, max={np.max(C_b_lcdm):.6e}, mean={np.mean(C_b_lcdm):.6e}")
    print(f"  EDE bandpowers:  min={np.min(C_b_ede):.6e}, max={np.max(C_b_ede):.6e}, mean={np.mean(C_b_ede):.6e}")
    print(f"  ACT data:        min={np.min(d):.6e}, max={np.max(d):.6e}, mean={np.mean(d):.6e}")
    
    # Build template and residual in bandpower space
    print("\nBuilding shoulder template in bandpower space...")
    t = C_b_ede - C_b_lcdm  # Template: ΔC_b = C_b(EDE) - C_b(ΛCDM)
    r = d - C_b_lcdm         # Residual: r = d - C_b(ΛCDM)
    
    print(f"  Template vector length: {len(t)}")
    print(f"  Residual vector length: {len(r)}")
    print(f"  Covariance shape: {Cov.shape}")
    
    # DEBUG: Check template magnitude
    max_template_diff = np.max(np.abs(t))
    rms_template = np.sqrt(np.mean(t**2))
    mean_template = np.mean(np.abs(t))
    print(f"  DEBUG: Max |template|: {max_template_diff:.6e}")
    print(f"  DEBUG: Mean |template|: {mean_template:.6e}")
    print(f"  DEBUG: RMS template: {rms_template:.6e}")
    
    # Check relative difference
    rel_diff = np.max(np.abs(t)) / np.max(np.abs(C_b_lcdm))
    print(f"  DEBUG: Max relative diff: {rel_diff:.6e} (should be ~0.01-0.1 for 1% effect)")
    
    if max_template_diff < 1e-10:
        print("  ⚠️  WARNING: Template is essentially zero!")
        print("     This means EDE and LCDM bandpowers are identical.")
        print("     Possible causes:")
        print("     - Lambda value not activating field")
        print("     - Window function conversion issue")
        print("     - Parameter mismatch")
    elif max_template_diff > 1e6:
        print("  ⚠️  WARNING: Template is huge! Check units.")
    else:
        print(f"  ✓ Template magnitude looks reasonable")
    
    # DIAGNOSTIC CHECKS (before fitting)
    print("\n" + "=" * 70)
    print("DIAGNOSTIC CHECKS")
    print("=" * 70)
    print(f"||r||_2 = {np.linalg.norm(r):.6e}")
    print(f"||t||_2 = {np.linalg.norm(t):.6e}")
    print(f"||r||/||t|| = {np.linalg.norm(r)/np.linalg.norm(t):.6e}")
    
    # Check covariance conditioning
    evals, _ = np.linalg.eigh(Cov)
    print(f"Cov eigenvalue range: {evals.min():.6e} to {evals.max():.6e}")
    print(f"Cov condition number: {evals.max()/evals.min():.6e}")
    
    # Check residual statistics
    print(f"Residual mean: {np.mean(r):.6e}, std: {np.std(r):.6e}")
    print(f"Residual min/max: {np.min(r):.6e} / {np.max(r):.6e}")
    print(f"Template mean: {np.mean(t):.6e}, std: {np.std(t):.6e}")
    print(f"Template min/max: {np.min(t):.6e} / {np.max(t):.6e}")
    
    # Check for unit mismatch
    if np.linalg.norm(r) > 1e6 * np.linalg.norm(t):
        print("\n⚠️  WARNING: Residual norm >> Template norm")
        print("   Possible unit mismatch between data and theory!")
    if evals.max() / evals.min() > 1e12:
        print("\n⚠️  WARNING: Covariance is very ill-conditioned")
        print("   Will use Cholesky whitening with ridge regularization")
    
    # Fit amplitude
    print("\nFitting template amplitude...")
    A_sh, sigma_A, S_N = fit_amplitude(r, t, Cov)
    
    results = {'TT+EE': (A_sh, sigma_A, S_N)}
    print(f"  A_sh = {A_sh:.3f} ± {sigma_A:.3f}, S/N = {S_N:.2f}")
    
    # Report
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    if not results:
        print("\n❌ ERROR: Could not fit template amplitude")
        print("Check data format and window function application.")
        return
    
    # Print results for each spectrum
    for spec_type, (A, sigma, SN) in results.items():
        print(f"\n{spec_type}: A_sh = {A:.3f} ± {sigma:.3f}, S/N = {SN:.2f}")
    
    # Overall interpretation
    print("\n" + "-" * 70)
    print("INTERPRETATION")
    print("-" * 70)
    
    # Check if any spectrum shows detection
    detected = False
    neutral = False
    
    for spec_type, (A, sigma, SN) in results.items():
        if abs(A - 1.0) < 2 * sigma:
            print(f"\n✅ {spec_type}: SHOULDER DETECTED! (A_sh ≈ 1)")
            detected = True
        elif abs(A) < 2 * sigma:
            print(f"\n📊 {spec_type}: ACT NEUTRAL (consistent with both LCDM and EDE)")
            neutral = True
        elif abs(SN) > 2:
            if A < 0:
                print(f"\n❌ {spec_type}: ACT DISFAVORS shoulder pattern (A_sh < 0)")
            else:
                print(f"\n⚠️  {spec_type}: A_sh = {A:.2f} but inconsistent with prediction")
        else:
            print(f"\n📊 {spec_type}: Low significance (S/N = {SN:.2f})")
    
    if detected:
        print("\n🎯 CONCLUSION: Evidence for soft shoulder pattern in ACT data!")
    elif neutral:
        print("\n📊 CONCLUSION: ACT is consistent with predicted shoulder (not yet detected)")
    else:
        print("\n❓ CONCLUSION: Inconclusive - need more data or check implementation")

if __name__ == "__main__":
    main()
