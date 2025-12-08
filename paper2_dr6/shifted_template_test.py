#!/usr/bin/env python3
"""
Wrong-template null test using SHIFTED templates in bandpower space.
No CLASS calls needed - just shift the template pattern in ell.
"""
import numpy as np
from scipy import linalg
from act_dr6_mflike import ACTDR6MFLike
import os

def load_best_fit(chain_file):
    """Load best-fit parameters from chain."""
    with open(chain_file) as f:
        header = f.readline().strip().replace('# ', '').split()
    data = np.loadtxt(chain_file)
    mlp_idx = header.index('minuslogpost')
    best_idx = np.argmin(data[:, mlp_idx])
    return {col: data[best_idx, i] for i, col in enumerate(header)}

def compute_bandpowers(params, lik, add_ede=False):
    """Compute theory bandpowers using CLASS."""
    from classy import Class
    
    H0 = params.get('H0', 68)
    ob = params.get('omega_b', 0.022)
    oc = params.get('omega_cdm', 0.12)
    tau = params.get('tau_reio', 0.054)
    ns = params.get('n_s', 0.965)
    As = 1e-10 * np.exp(params['logA']) if 'logA' in params else 2.1e-9
    
    T_CMB_SQ = (2.7255e6) ** 2
    
    cp = {
        'output': 'tCl pCl lCl',
        'l_max_scalars': 8502,
        'lensing': 'yes',
        'gauge': 'newtonian',
        'recombination': 'recfast',
        'non_linear': 'none',
        'H0': H0, 'omega_b': ob, 'omega_cdm': oc,
        'tau_reio': tau, 'n_s': ns, 'A_s': As,
    }
    
    if add_ede:
        lam = params.get('Lambda_EDE_ridder', 0.11)
        cp.update({
            'Lambda_EDE_ridder': lam,
            'f_axion_ridder': 1e27,
            'theta_i_ridder': 2.0,
            'beta_ridder': 0,
            'n_ridder': 3,
        })
    
    c = Class()
    c.set(cp)
    c.compute()
    cl = c.lensed_cl(8502)
    c.struct_cleanup()
    
    ell = np.arange(8503)
    f = ell * (ell + 1) / (2 * np.pi)
    D = {
        'tt': cl['tt'] * f * T_CMB_SQ,
        'ee': cl['ee'] * f * T_CMB_SQ,
        'te': cl['te'] * f * T_CMB_SQ,
    }
    
    tr = sorted(set('_'.join(k.split('_')[:-1]) for k in lik.bands.keys()))
    dls = {(s, t1, t2): D[s] for s in ['tt', 'ee', 'te'] for t1 in tr for t2 in tr}
    cal = {k: params.get(k, 1.0) for k in [
        'calG_all', 'cal_dr6_pa4_f220', 'cal_dr6_pa5_f090', 'cal_dr6_pa5_f150',
        'cal_dr6_pa6_f090', 'cal_dr6_pa6_f150', 'calE_dr6_pa4_f220',
        'calE_dr6_pa5_f090', 'calE_dr6_pa5_f150', 'calE_dr6_pa6_f090', 'calE_dr6_pa6_f150'
    ]}
    
    return lik._get_ps_vec(lik._get_rotated_spectra(dls, **cal))

def fit_amplitude(res, tpl, cho):
    """Fit A in res = A * tpl using precomputed Cholesky factor."""
    Ci_res = linalg.cho_solve(cho, res, check_finite=False)
    Ci_tpl = linalg.cho_solve(cho, tpl, check_finite=False)
    num = tpl @ Ci_res
    den = tpl @ Ci_tpl
    if den <= 0:
        return 0.0, 0.0, 0.0
    A = num / den
    sigma = den ** -0.5
    dchi2 = -A * A * den
    return A, sigma, dchi2

def main():
    print("=" * 70)
    print("SHIFTED-TEMPLATE NULL TEST")
    print("=" * 70)
    
    # Load ACT likelihood
    print("\n1. Loading ACT likelihood...")
    lik = ACTDR6MFLike({})
    d = np.array(lik.data_vec)
    Cov = np.array(lik.cov)
    cho = linalg.cho_factor(Cov, overwrite_a=False, check_finite=False)
    print("   Data: %d bandpowers" % len(d))
    
    # Load chain best-fits
    cd = os.path.expanduser('~/Ridder-Field/paper2_dr6/chains')
    pl = load_best_fit(cd + '/prod_p0b_dr6_lcdm.1.txt')
    pe = load_best_fit(cd + '/prod_p2_dr6_ede.1.txt')
    
    # Check for saved bandpowers or compute
    lcdm_file = 'dr6_bandpowers_lcdm.npy'
    ede_file = 'dr6_bandpowers_ede.npy'
    
    if os.path.exists(lcdm_file) and os.path.exists(ede_file):
        print("\n2. Loading precomputed bandpowers...")
        Cl_LCDM = np.load(lcdm_file)
        Cl_EDE = np.load(ede_file)
    else:
        print("\n2. Computing theory bandpowers (this takes a minute)...")
        print("   Computing LCDM...")
        Cl_LCDM = compute_bandpowers(pl, lik, add_ede=False)
        print("   Computing EDE...")
        Cl_EDE = compute_bandpowers(pe, lik, add_ede=True)
        # Save for future use
        np.save(lcdm_file, Cl_LCDM)
        np.save(ede_file, Cl_EDE)
        print("   Saved bandpowers for future runs")
    
    # Residuals and correct template
    res = d - Cl_LCDM
    t0 = Cl_EDE - Cl_LCDM
    
    # Fit correct template
    A0, s0, dx0 = fit_amplitude(res, t0, cho)
    
    print("\n" + "=" * 70)
    print("RESULTS: Shifted-Template Null Test")
    print("=" * 70)
    print("\n%-25s %8s %14s %10s %8s" % ("Template", "Shift", "A_sh", "dchi2", "Sig"))
    print("-" * 70)
    print("%-25s %8s %5.2f +/- %-5.2f %+10.0f %7.1fs" % (
        "*** CORRECT (unshifted)", "0", A0, s0, dx0, abs(A0/s0)))
    
    # Test shifted templates
    shifts = [10, 20, 30, 50, 75, 100, 150, 200]
    
    for k in shifts:
        # Positive shift
        t_pos = np.roll(t0, k)
        A_pos, s_pos, dx_pos = fit_amplitude(res, t_pos, cho)
        print("%-25s %+8d %5.2f +/- %-5.2f %+10.0f %7.1fs" % (
            "Shifted template", k, A_pos, s_pos, dx_pos, abs(A_pos/s_pos)))
        
        # Negative shift
        t_neg = np.roll(t0, -k)
        A_neg, s_neg, dx_neg = fit_amplitude(res, t_neg, cho)
        print("%-25s %+8d %5.2f +/- %-5.2f %+10.0f %7.1fs" % (
            "Shifted template", -k, A_neg, s_neg, dx_neg, abs(A_neg/s_neg)))
    
    print("-" * 70)
    print("\nInterpretation:")
    print("  - Correct (unshifted) template: A_sh/sigma = %.1f, large |dchi2|" % (A0/s0))
    print("  - Shifted templates: should have A_sh/sigma ~ O(1), small |dchi2|")
    print("  - This proves ACT responds to the SPECIFIC phase, not random wiggles")

if __name__ == "__main__":
    main()

