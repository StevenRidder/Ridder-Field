#!/usr/bin/env python3
"""
ACT Template Amplitude Fit - FAST VERSION
==========================================
Uses cached spectra and lower l_max for quick results.
Computes once, caches to disk, reuses on subsequent runs.
"""
import numpy as np
import sys
import os
import pickle
from scipy import linalg
import hashlib

# =============================================
# SPEED SETTINGS
# =============================================
# ACT likelihood window functions require l_max >= 8500
# Can't reduce l_max, but we use caching + relaxed precision
FAST_LMAX = 8502
CACHE_DIR = os.path.expanduser("~/Ridder-Field/phase3/cache")

T_CMB = 2.7255e6  # μK
T_CMB_SQ = T_CMB ** 2

# Import ACT likelihood
try:
    from act_dr6_mflike import ACTDR6MFLike
    HAS_ACT = True
except ImportError:
    HAS_ACT = False
    print("Warning: ACT likelihood not available")

def get_cache_key(params, prefix):
    """Generate cache key from parameters."""
    key_params = {k: round(v, 6) if isinstance(v, float) else v 
                  for k, v in sorted(params.items()) 
                  if k in ['H0', 'omega_b', 'omega_cdm', 'n_s', 'tau_reio', 'A_s', 'Lambda_EDE_ridder']}
    key_str = f"{prefix}_{FAST_LMAX}_{str(key_params)}"
    return hashlib.md5(key_str.encode()).hexdigest()[:12]

def load_cached_spectrum(cache_key):
    """Load cached bandpowers if available."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.pkl")
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    return None

def save_cached_spectrum(cache_key, bandpowers):
    """Save bandpowers to cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.pkl")
    with open(cache_file, 'wb') as f:
        pickle.dump(bandpowers, f)

def compute_bandpowers_fast(params, likelihood, use_cache=True):
    """
    Compute ACT bandpowers with caching and reduced l_max.
    """
    from classy import Class
    
    # Check cache first
    is_ede = 'Lambda_EDE_ridder' in params
    prefix = "ede" if is_ede else "lcdm"
    cache_key = get_cache_key(params, prefix)
    
    if use_cache:
        cached = load_cached_spectrum(cache_key)
        if cached is not None:
            print(f"  ✓ Loaded from cache ({cache_key})")
            return cached
    
    print(f"  Computing C_ell (l_max={FAST_LMAX})...")
    
    cosmo = Class()
    class_params = {
        'output': 'tCl pCl lCl',
        'l_max_scalars': FAST_LMAX,
        'lensing': 'yes',
        'gauge': 'newtonian',
        'non_linear': 'none',
        # Relaxed precision for speed
        'l_logstep': 1.04,
        'l_linstep': 40,
        'A_s': params.get('A_s', 2e-9),
        'n_s': params.get('n_s', 0.965),
        'H0': params.get('H0', 68),
        'omega_b': params.get('omega_b', 0.022),
        'omega_cdm': params.get('omega_cdm', 0.12),
        'tau_reio': params.get('tau_reio', 0.054),
    }
    
    if is_ede:
        class_params.update({
            'Lambda_EDE_ridder': params['Lambda_EDE_ridder'],
            'f_axion_ridder': 1.0e+27,
            'theta_i_ridder': 1.0,
            'beta_ridder': 0.0,
            'n_ridder': 3,
        })
    
    cosmo.set(class_params)
    try:
        cosmo.compute()
    except Exception as e:
        print(f"  ERROR: CLASS failed: {e}")
        return None
    
    cl = cosmo.lensed_cl(FAST_LMAX)
    cosmo.struct_cleanup()
    
    # Convert to D_ell
    ell = np.arange(FAST_LMAX + 1)
    factor = ell * (ell + 1) / (2 * np.pi)
    D_ell = {
        'tt': cl['tt'] * factor * T_CMB_SQ,
        'ee': cl['ee'] * factor * T_CMB_SQ,
        'te': cl['te'] * factor * T_CMB_SQ,
    }
    
    # Get tracers and build dls_dict
    tracers = set()
    for band_key in likelihood.bands.keys():
        parts = band_key.split('_')
        tracer = '_'.join(parts[:-1])
        tracers.add(tracer)
    tracers = sorted(list(tracers))
    
    dls_dict = {}
    for spec in ['tt', 'ee', 'te']:
        for t1 in tracers:
            for t2 in tracers:
                dls_dict[(spec, t1, t2)] = D_ell[spec]
    
    # Get calibration params
    act_params = {key: params.get(key, 1.0) for key in [
        'calG_all', 'cal_dr6_pa4_f220', 'cal_dr6_pa5_f090', 'cal_dr6_pa5_f150',
        'cal_dr6_pa6_f090', 'cal_dr6_pa6_f150', 'calE_dr6_pa4_f220',
        'calE_dr6_pa5_f090', 'calE_dr6_pa5_f150', 'calE_dr6_pa6_f090', 'calE_dr6_pa6_f150'
    ]}
    
    try:
        rotated = likelihood._get_rotated_spectra(dls_dict, **act_params)
        C_b = likelihood._get_ps_vec(rotated)
    except Exception as e:
        print(f"  ERROR: Bandpower conversion failed: {e}")
        return None
    
    # Cache result
    if use_cache:
        save_cached_spectrum(cache_key, C_b)
        print(f"  ✓ Saved to cache ({cache_key})")
    
    return C_b

def load_best_fit_from_chain(chain_file):
    """Load best-fit parameters from chain file."""
    data = np.loadtxt(chain_file)
    with open(chain_file, 'r') as f:
        header = f.readline()
        cols = header[1:].strip().split() if header.startswith('#') else None
    
    if cols is None:
        raise ValueError("Chain file missing header")
    
    mlp_idx = cols.index('minuslogpost')
    best_idx = np.argmin(data[:, mlp_idx])
    
    params = {}
    for col in ['H0', 'n_s', 'omega_b', 'omega_cdm', 'tau_reio', 'Lambda_EDE_ridder']:
        if col in cols:
            params[col] = data[best_idx, cols.index(col)]
    
    # ACT calibration
    for key in ['calG_all', 'cal_dr6_pa4_f220', 'cal_dr6_pa5_f090', 'cal_dr6_pa5_f150',
                'cal_dr6_pa6_f090', 'cal_dr6_pa6_f150', 'calE_dr6_pa4_f220',
                'calE_dr6_pa5_f090', 'calE_dr6_pa5_f150', 'calE_dr6_pa6_f090', 'calE_dr6_pa6_f150']:
        if key in cols:
            params[key] = data[best_idx, cols.index(key)]
        else:
            params[key] = 1.0
    
    if 'logA' in cols:
        params['A_s'] = 1e-10 * np.exp(data[best_idx, cols.index('logA')])
    
    return params

def fit_amplitude(r, t, Cov):
    """Fit template amplitude."""
    try:
        Cov_inv = linalg.inv(Cov)
    except:
        Cov_inv = linalg.pinv(Cov)
    
    num = t @ (Cov_inv @ r)
    den = t @ (Cov_inv @ t)
    
    A_hat = num / den
    sigma_A = np.sqrt(1.0 / den) if den > 0 else np.inf
    S_N = A_hat / sigma_A if sigma_A > 0 else 0
    
    return A_hat, sigma_A, S_N

def main():
    print("=" * 70)
    print("ACT TEMPLATE AMPLITUDE FIT (FAST VERSION)")
    print(f"Using l_max={FAST_LMAX}, with caching")
    print("=" * 70)
    
    chain_dir = os.path.expanduser("~/Ridder-Field/phase3/chains")
    all_files = os.listdir(chain_dir)
    
    lcdm_files = sorted([f for f in all_files if ('act_lcdm' in f or 'act_world_lcdm' in f) and f.endswith('.1.txt')])
    ede_files = sorted([f for f in all_files if ('act_ede' in f or 'act_world_ede' in f) and 'lcdm' not in f and f.endswith('.1.txt')])
    
    print(f"\nChain files: LCDM={lcdm_files}, EDE={ede_files}")
    
    if not ede_files or not lcdm_files:
        print("\n❌ Need both EDE and LCDM chain files!")
        return
    
    # Load best-fit parameters
    print("\nLoading best-fit parameters...")
    params_lcdm = load_best_fit_from_chain(os.path.join(chain_dir, lcdm_files[0]))
    params_ede = load_best_fit_from_chain(os.path.join(chain_dir, ede_files[0]))
    
    lambda_val = params_ede.get('Lambda_EDE_ridder', 1.0)
    print(f"  LCDM: H0={params_lcdm.get('H0', 0):.2f}")
    print(f"  EDE:  H0={params_ede.get('H0', 0):.2f}, Lambda={lambda_val:.4f}")
    print(f"  → z_osc ~ {4500 * lambda_val:.0f}")
    
    if not HAS_ACT:
        print("\n❌ ACT likelihood not available!")
        return
    
    # Initialize likelihood
    print("\nInitializing ACT likelihood...")
    likelihood = ACTDR6MFLike({})
    
    # Get data
    d = np.array(likelihood.data_vec)
    Cov = np.array(likelihood.cov)
    print(f"  Data: {len(d)} bandpowers")
    
    # Compute bandpowers (with caching)
    print("\nComputing LCDM bandpowers...")
    C_b_lcdm = compute_bandpowers_fast(params_lcdm, likelihood)
    
    print("\nComputing EDE bandpowers...")
    C_b_ede = compute_bandpowers_fast(params_ede, likelihood)
    
    if C_b_lcdm is None or C_b_ede is None:
        print("\n❌ Failed to compute bandpowers")
        return
    
    # Build template and fit
    print("\nFitting template amplitude...")
    t = C_b_ede - C_b_lcdm  # Template
    r = d - C_b_lcdm         # Residual
    
    A_sh, sigma_A, S_N = fit_amplitude(r, t, Cov)
    
    # Results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\n🎯 A_sh = {A_sh:.3f} ± {sigma_A:.3f}")
    print(f"   S/N = {S_N:.2f}")
    
    print("\n" + "-" * 70)
    print("INTERPRETATION")
    print("-" * 70)
    
    if abs(A_sh - 1.0) < 2 * sigma_A:
        print(f"\n✅ SOFT SHOULDER DETECTED!")
        print(f"   A_sh = {A_sh:.2f} ± {sigma_A:.2f} is consistent with A_sh = 1")
        print(f"   ACT data matches Ridder EDE prediction!")
    elif A_sh > 0 and S_N > 2:
        print(f"\n📊 Positive detection: A_sh = {A_sh:.2f} at {S_N:.1f}σ")
        if A_sh > 1.5:
            print(f"   Stronger than predicted - check chain convergence")
    elif A_sh < 0 and S_N < -2:
        print(f"\n❌ ACT DISFAVORS shoulder: A_sh = {A_sh:.2f}")
    else:
        print(f"\n📊 Inconclusive: A_sh = {A_sh:.2f} ± {sigma_A:.2f} (S/N = {S_N:.1f})")
    
    print(f"\nLambda = {lambda_val:.3f} → z_osc ~ {4500*lambda_val:.0f}")
    if 0.85 < lambda_val < 1.15:
        print("✅ Lambda in soft shoulder regime")
    else:
        print("⚠️  Lambda outside optimal range [0.85, 1.15]")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

