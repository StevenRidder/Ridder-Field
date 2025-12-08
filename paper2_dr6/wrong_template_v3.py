#!/usr/bin/env python3
"""Wrong-Template Null Tests v3"""
import numpy as np
import os
from scipy import linalg

T_CMB = 2.7255e6
T_CMB_SQ = T_CMB ** 2

from act_dr6_mflike import ACTDR6MFLike

def load_best_fit(chain_file):
    with open(chain_file) as f:
        header = f.readline().strip().replace('# ', '').split()
    data = np.loadtxt(chain_file)
    mlp_idx = header.index('minuslogpost')
    best_idx = np.argmin(data[:, mlp_idx])
    return {col: data[best_idx, i] for i, col in enumerate(header)}

def compute_bp(params, lik, lam=None):
    from classy import Class
    H0 = params.get('H0', 68)
    ob = params.get('omega_b', 0.022)
    oc = params.get('omega_cdm', 0.12)
    tau = params.get('tau_reio', 0.054)
    ns = params.get('n_s', 0.965)
    As = 1e-10 * np.exp(params['logA']) if 'logA' in params else 2.1e-9
    
    cp = {
        'output': 'tCl pCl lCl',
        'l_max_scalars': 8502,
        'lensing': 'yes',
        'gauge': 'newtonian',
        'recombination': 'recfast',
        'non_linear': 'none',
        'H0': H0,
        'omega_b': ob,
        'omega_cdm': oc,
        'tau_reio': tau,
        'n_s': ns,
        'A_s': As,
    }
    if lam and lam > 0:
        cp.update({
            'Lambda_EDE_ridder': lam,
            'f_axion_ridder': 1e27,
            'theta_i_ridder': 2.0,
            'beta_ridder': 0,
            'n_ridder': 3,
        })
    
    c = Class()
    c.set(cp)
    try:
        c.compute()
    except:
        return None
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
    try:
        return lik._get_ps_vec(lik._get_rotated_spectra(dls, **cal))
    except:
        return None

def fit(r, t, C):
    try:
        Ci = linalg.inv(C)
    except:
        Ci = linalg.pinv(C)
    n = t @ (Ci @ r)
    d = t @ (Ci @ t)
    if d <= 0:
        return 0, 99, 0
    return n / d, np.sqrt(1 / d), -(n / d) ** 2 * d

def main():
    cd = os.path.expanduser('~/Ridder-Field/paper2_dr6/chains')
    pl = load_best_fit(cd + '/prod_p0b_dr6_lcdm.1.txt')
    pe = load_best_fit(cd + '/prod_p2_dr6_ede.1.txt')
    lam0 = pe.get('Lambda_EDE_ridder', 0.11)

    print('=' * 70)
    print('WRONG-TEMPLATE NULL TESTS (FIXED: same cosmology)')
    print('=' * 70)
    print('Correct Lambda = %.4f' % lam0)

    lik = ACTDR6MFLike({})
    d = np.array(lik.data_vec)
    Cov = np.array(lik.cov)

    # Use LCDM cosmology for baseline
    Cl = compute_bp(pl, lik)
    
    # Use ACTUAL EDE best-fit (full cosmology including EDE) for correct template
    Ce = compute_bp(pe, lik)
    if Cl is None or Ce is None:
        print('ERROR computing baselines')
        return

    res = d - Cl
    t0 = Ce - Cl
    A, s, dx = fit(res, t0, Cov)

    print('')
    print('%-30s %8s %12s %8s %6s' % ('Template', 'Lambda', 'A_sh', 'dchi2', 'Sig'))
    print('-' * 70)
    print('%-30s %8.4f %5.2f+/-%.2f %8.0f %5.1fs' % ('*** CORRECT ***', lam0, A, s, dx, abs(A/s)))

    for lam in [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.16, 0.18]:
        if abs(lam - lam0) < 0.015:
            continue
        C = compute_bp(pl, lik, lam)
        if C is None:
            print('%-30s %8.4f %12s' % ('Wrong z_c', lam, 'FAILED'))
            continue
        t = C - Cl
        A, s, dx = fit(res, t, Cov)
        print('%-30s %8.4f %5.2f+/-%.2f %8.0f %5.1fs' % ('Wrong z_c', lam, A, s, dx, abs(A/s)))

    print('-' * 70)

if __name__ == '__main__':
    main()

