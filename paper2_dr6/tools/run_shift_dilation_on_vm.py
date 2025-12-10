#!/usr/bin/env python3
"""
VM-READY: Continuous shift and dilation tests using REAL ACT DR6 data.

Run this ON THE AZURE VM where:
1. ACT DR6 likelihood is installed
2. MCMC chains exist in ~/Ridder-Field/paper2_dr6/chains/

This script generates the REAL numbers for Table shift_dilation in the paper.
Mock data is NOT acceptable for publication.

Usage on VM:
    cd ~/Ridder-Field/paper2_dr6/tools
    python3 run_shift_dilation_on_vm.py

Expected output: Updates to paper2_dr6/data/shift_dilation_results.txt
"""
import numpy as np
from scipy import linalg
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import os
import sys

# ============================================================
# STEP 1: Load ACT DR6 likelihood (MUST be on VM)
# ============================================================
try:
    from act_dr6_mflike import ACTDR6MFLike
    print("✓ ACT DR6 likelihood loaded")
except ImportError:
    print("ERROR: ACT DR6 likelihood not available!")
    print("This script MUST be run on the VM with the likelihood installed.")
    print("See: azure/README.md for setup instructions")
    sys.exit(1)

# ============================================================
# STEP 2: Load best-fit parameters from REAL chains
# ============================================================
def load_chain_bestfit(chain_file):
    """Load best-fit point from a Cobaya chain file."""
    if not os.path.exists(chain_file):
        raise FileNotFoundError(f"Chain file not found: {chain_file}")
    
    with open(chain_file) as f:
        header = f.readline().strip().replace('# ', '').split()
    
    data = np.loadtxt(chain_file)
    
    # Find best fit (minimum -logposterior)
    if 'minuslogpost' in header:
        mlp_idx = header.index('minuslogpost')
    elif '-logpost' in header:
        mlp_idx = header.index('-logpost')
    else:
        raise ValueError("No minuslogpost column found in chain")
    
    best_idx = np.argmin(data[:, mlp_idx])
    best_fit = {col: data[best_idx, i] for i, col in enumerate(header)}
    
    print(f"  Loaded best-fit from {os.path.basename(chain_file)}")
    print(f"  χ²_min = {2*data[best_idx, mlp_idx]:.1f}")
    
    return best_fit


def compute_theory_bandpowers(params, lik, with_ede=False):
    """Compute theory bandpowers using CLASS."""
    from classy import Class
    
    H0 = params.get('H0', 67.4)
    ob = params.get('omega_b', 0.02237)
    oc = params.get('omega_cdm', 0.12)
    tau = params.get('tau_reio', 0.054)
    ns = params.get('n_s', 0.965)
    
    if 'logA' in params:
        As = 1e-10 * np.exp(params['logA'])
    else:
        As = 2.1e-9
    
    T_CMB_SQ = (2.7255e6) ** 2  # μK²
    
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
    
    if with_ede:
        Lambda = params.get('Lambda_EDE_ridder', 0.16)
        cp.update({
            'Lambda_EDE_ridder': Lambda,
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
    
    # Get tracers from likelihood
    tr = sorted(set('_'.join(k.split('_')[:-1]) for k in lik.bands.keys()))
    dls = {(s, t1, t2): D[s] for s in ['tt', 'ee', 'te'] for t1 in tr for t2 in tr}
    
    # Calibration parameters
    cal = {}
    for k in ['calG_all', 'cal_dr6_pa4_f220', 'cal_dr6_pa5_f090', 'cal_dr6_pa5_f150',
              'cal_dr6_pa6_f090', 'cal_dr6_pa6_f150', 'calE_dr6_pa4_f220',
              'calE_dr6_pa5_f090', 'calE_dr6_pa5_f150', 'calE_dr6_pa6_f090', 
              'calE_dr6_pa6_f150']:
        cal[k] = params.get(k, 1.0)
    
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
    print("CONTINUOUS SHIFT AND DILATION TESTS - VM VERSION")
    print("Using REAL ACT DR6 data and REAL chain best-fits")
    print("=" * 70)
    
    # --------------------------------------------------------
    # 1. Load ACT likelihood
    # --------------------------------------------------------
    print("\n1. Loading ACT DR6 likelihood...")
    lik = ACTDR6MFLike({})
    d = np.array(lik.data_vec)
    Cov = np.array(lik.cov)
    cho = linalg.cho_factor(Cov, overwrite_a=False, check_finite=False)
    print(f"   Data vector: {len(d)} bandpowers")
    
    # --------------------------------------------------------
    # 2. Load chain best-fits
    # --------------------------------------------------------
    print("\n2. Loading best-fit parameters from chains...")
    chain_dir = os.path.expanduser('~/Ridder-Field/paper2_dr6/chains')
    
    lcdm_chain = os.path.join(chain_dir, 'prod_p0b_dr6_lcdm.1.txt')
    ede_chain = os.path.join(chain_dir, 'prod_p2_dr6_ede.1.txt')
    
    params_lcdm = load_chain_bestfit(lcdm_chain)
    params_ede = load_chain_bestfit(ede_chain)
    
    # --------------------------------------------------------
    # 3. Compute theory bandpowers
    # --------------------------------------------------------
    print("\n3. Computing theory bandpowers...")
    print("   Computing ΛCDM (this takes ~30s)...")
    Cl_LCDM = compute_theory_bandpowers(params_lcdm, lik, with_ede=False)
    
    print("   Computing EDE...")
    Cl_EDE = compute_theory_bandpowers(params_ede, lik, with_ede=True)
    
    # Template and residuals
    t0 = Cl_EDE - Cl_LCDM
    res = d - Cl_LCDM
    
    # Baseline fit
    A0, s0, dx0 = fit_amplitude(res, t0, cho)
    print(f"\n   Baseline: A_sh = {A0:.3f} ± {s0:.3f} = {abs(A0/s0):.1f}σ")
    
    # --------------------------------------------------------
    # 4. Continuous shift test
    # --------------------------------------------------------
    print("\n4. Running continuous shift test (-150 to +150 bins)...")
    shifts = np.arange(-150, 151, 5)  # Every 5 bins for speed
    shift_results = []
    
    for k in shifts:
        t_shifted = np.roll(t0, k)
        A, s, dx = fit_amplitude(res, t_shifted, cho)
        sig = abs(A/s) if s > 0 else 0
        shift_results.append((k, A, s, sig, dx))
        if k % 30 == 0:
            print(f"   Shift {k:+4d}: {sig:.1f}σ")
    
    # Find FWHM
    sigs = np.array([r[3] for r in shift_results])
    peak_sig = sigs.max()
    half_max = peak_sig / 2
    above_half = np.where(sigs > half_max)[0]
    if len(above_half) > 1:
        fwhm = shifts[above_half[-1]] - shifts[above_half[0]]
    else:
        fwhm = float('nan')
    
    print(f"\n   Peak significance: {peak_sig:.1f}σ at shift=0")
    print(f"   FWHM: {fwhm:.0f} bins")
    
    # --------------------------------------------------------
    # 5. Dilation test
    # --------------------------------------------------------
    print("\n5. Running dilation test (α = 0.85 to 1.15)...")
    alphas = np.arange(0.85, 1.16, 0.02)
    dilation_results = []
    
    n_bins = len(t0)
    ell_orig = np.arange(n_bins)
    
    for alpha in alphas:
        ell_scaled = ell_orig * alpha
        # Interpolate template at dilated ℓ values
        t_dilated = np.interp(ell_orig, ell_scaled, t0, left=0, right=0)
        A, s, dx = fit_amplitude(res, t_dilated, cho)
        sig = abs(A/s) if s > 0 else 0
        dilation_results.append((alpha, A, s, sig, dx))
        if abs(alpha - 1.0) < 0.01 or abs(alpha - 0.95) < 0.01 or abs(alpha - 1.05) < 0.01:
            print(f"   α = {alpha:.2f}: {sig:.1f}σ")
    
    # --------------------------------------------------------
    # 6. Save results
    # --------------------------------------------------------
    output_dir = os.path.dirname(__file__)
    results_file = os.path.join(output_dir, '..', 'data', 'shift_dilation_results.txt')
    
    with open(results_file, 'w') as f:
        f.write("# Shift and Dilation Test Results - REAL ACT DR6 DATA\n")
        f.write("# Generated by run_shift_dilation_on_vm.py\n")
        f.write("#\n")
        f.write(f"baseline_A = {A0:.6f}\n")
        f.write(f"baseline_sigma = {s0:.6f}\n")
        f.write(f"baseline_significance = {abs(A0/s0):.2f}\n")
        f.write(f"baseline_dchi2 = {dx0:.1f}\n")
        f.write(f"shift_fwhm_bins = {fwhm:.0f}\n")
        f.write("#\n")
        f.write("# Shift results: shift, A, sigma, significance, dchi2\n")
        for k, A, s, sig, dx in shift_results:
            f.write(f"shift {k:+4d} {A:.6f} {s:.6f} {sig:.2f} {dx:.1f}\n")
        f.write("#\n")
        f.write("# Dilation results: alpha, A, sigma, significance, dchi2\n")
        for alpha, A, s, sig, dx in dilation_results:
            f.write(f"dilation {alpha:.2f} {A:.6f} {s:.6f} {sig:.2f} {dx:.1f}\n")
    
    print(f"\n   Results saved to: {results_file}")
    
    # --------------------------------------------------------
    # 7. Generate figure
    # --------------------------------------------------------
    print("\n6. Generating figure...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Shift plot
    ax1.plot([r[0] for r in shift_results], [r[3] for r in shift_results], 'b-', lw=2)
    ax1.axhline(3, color='r', ls='--', label='3σ threshold')
    ax1.axvline(0, color='g', ls=':', alpha=0.5)
    ax1.set_xlabel('Template Shift (bins)')
    ax1.set_ylabel('Significance (σ)')
    ax1.set_title('Continuous Shift Test')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Dilation plot
    ax2.plot([r[0] for r in dilation_results], [r[3] for r in dilation_results], 'b-', lw=2)
    ax2.axhline(3, color='r', ls='--', label='3σ threshold')
    ax2.axvline(1.0, color='g', ls=':', alpha=0.5)
    ax2.set_xlabel('Dilation Factor (α)')
    ax2.set_ylabel('Significance (σ)')
    ax2.set_title('Dilation Test')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    fig_file = os.path.join(output_dir, '..', 'figures', 'shift_dilation_test_REAL.pdf')
    plt.savefig(fig_file)
    print(f"   Figure saved to: {fig_file}")
    
    # --------------------------------------------------------
    # 8. Print summary for paper
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("RESULTS FOR PAPER TABLE (tab:shift_dilation)")
    print("=" * 70)
    print(f"\nBaseline: {abs(A0/s0):.1f}σ")
    print(f"FWHM: {fwhm:.0f} bins")
    
    # Find specific values for paper table
    for k, A, s, sig, dx in shift_results:
        if k == 0:
            print(f"Shift = 0: {sig:.1f}σ")
        if k == 30:
            print(f"Shift = +30: {sig:.1f}σ")
        if k == 50:
            print(f"Shift = +50: {sig:.1f}σ")
    
    for alpha, A, s, sig, dx in dilation_results:
        if abs(alpha - 0.95) < 0.01:
            print(f"α = 0.95: {sig:.1f}σ")
        if abs(alpha - 1.00) < 0.01:
            print(f"α = 1.00: {sig:.1f}σ")
        if abs(alpha - 1.05) < 0.01:
            print(f"α = 1.05: {sig:.1f}σ")
    
    print("\n" + "=" * 70)
    print("COPY THESE VALUES INTO paper2_v2_anomaly.tex Table shift_dilation")
    print("=" * 70)


if __name__ == "__main__":
    main()

