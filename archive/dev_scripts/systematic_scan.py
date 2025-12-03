#!/usr/bin/env python3
"""
SYSTEMATIC SCAN: Ridder Unified Model

This is NOT parameter pecking. This is a controlled search over a frozen model.

Fixed: potential shape, n_tail, n_shelf, theta_i, window params, mass, f, c_slow
Free: Lambda_tail, f_axion (2D parameter space)

Each point is classified as VIABLE, NEAR-MISS, or EXCLUDED based on hard constraints.
A χ² is computed to compare against ΛCDM.
"""

import subprocess
import numpy as np
import json
import os
from datetime import datetime

# =============================================================================
# MODEL DEFINITION (FROZEN)
# =============================================================================

FIXED_PARAMS = {
    'n_tail': 1.0,
    'n_shelf': 3.0,
    'alpha_tail': 1.0,
    'theta_i': 2.5,
    'theta_EDE_low': 0.5,
    'theta_EDE_high': 3.5,
    'sigma_EDE': 0.5,
    'm_axion': 7e4,
    'ridder_f': 7.305e26,
    'ridder_c_slow': 0.0,
    'beta_ridder': 0.0,
}

# Free parameter grid
LAMBDA_TAIL_VALUES = [15, 18, 20, 22, 25, 28, 30, 32, 35]  # meV
F_AXION_VALUES = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]

# =============================================================================
# HARD CONSTRAINTS
# =============================================================================

CONSTRAINTS = {
    'f_EDE_min': 0.05,
    'f_EDE_max': 0.20,
    'z_peak_min': 2000,
    'z_peak_max': 5000,
    'CMB_RMS_max': 0.20,  # 20%
    'BAO_frac_max': 0.03,  # 3%
}

# Targets (soft goals, used in χ²)
TARGETS = {
    'H0_target': 73.04,  # SH0ES
    'H0_sigma': 1.04,
    'S8_target': 0.766,  # KiDS-1000
    'S8_sigma': 0.020,
}

# ΛCDM reference values
LCDM = {
    'H0': 67.36,
    'S8': 0.834,
    'f_EDE': 0.0,
}

# =============================================================================
# PATHS
# =============================================================================

CLASS_DIR = '/home/<VM_USER>/Ridder-Field/phase2/class'
OUTPUT_DIR = '/home/<VM_USER>/Ridder-Field/phase2/class/output/systematic'

# =============================================================================
# INI GENERATION
# =============================================================================

def create_ini(lambda_tail, f_axion, output_root):
    """Generate INI for a frozen model point."""
    return f"""# Systematic scan: Lambda={lambda_tail}meV, f_axion={f_axion}
# FROZEN MODEL - see MODEL_DEFINITION.md

H0 = 67.36
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842

use_ridder = yes
gauge = newtonian
ridder_model_type = unified

# TAIL (fixed shape, variable scale)
ridder_use_tail = yes
ridder_Lambda_tail_eV = {lambda_tail}e-3
ridder_alpha_tail = {FIXED_PARAMS['alpha_tail']}
ridder_n_tail = {FIXED_PARAMS['n_tail']}

# SHELF (fixed shape, variable amplitude)
ridder_use_shelf = yes
ridder_m_axion = {FIXED_PARAMS['m_axion']}
ridder_f_axion = {f_axion}
ridder_n_EDE = {FIXED_PARAMS['n_shelf']}
ridder_theta_EDE_low = {FIXED_PARAMS['theta_EDE_low']}
ridder_theta_EDE_high = {FIXED_PARAMS['theta_EDE_high']}
ridder_sigma_theta_EDE = {FIXED_PARAMS['sigma_EDE']}

ridder_use_plateau = no

# FIXED IC and field params
ridder_f = {FIXED_PARAMS['ridder_f']}
theta_i_ridder = {FIXED_PARAMS['theta_i']}
beta_ridder = {FIXED_PARAMS['beta_ridder']}
ridder_c_slow = {FIXED_PARAMS['ridder_c_slow']}

output = tCl,mPk
write background = yes
l_max_scalars = 2500
root = {output_root}
"""

# =============================================================================
# METRIC EXTRACTION
# =============================================================================

def extract_metrics(bg_file, cl_file, pk_file, lcdm_bg_file, lcdm_cl_file):
    """Extract all metrics from CLASS output."""
    metrics = {}
    
    try:
        # Background data
        data = np.loadtxt(bg_file)
        z = data[:, 0]
        H = data[:, 3]
        rho_ridder = data[:, 14]
        rho_tot = data[:, 19]
        D_comov = data[:, 4]
        
        # f_EDE and z_peak
        f_ridder = rho_ridder / rho_tot
        idx_max = np.argmax(f_ridder)
        metrics['f_EDE'] = f_ridder[idx_max]
        metrics['z_peak'] = z[idx_max]
        
        # H0
        idx_0 = np.argmin(np.abs(z))
        metrics['H0'] = H[idx_0] * 299792.458
        
        # S8 (simplified - from P(k))
        try:
            pk_data = np.loadtxt(pk_file)
            k = pk_data[:, 0]
            Pk = pk_data[:, 1]
            R = 8.0
            x = k * R
            W = np.where(x > 0.01, 3 * (np.sin(x) - x * np.cos(x)) / x**3, 1.0)
            integrand = k**2 * Pk * W**2
            sigma8_sq = np.trapz(integrand, k) / (2 * np.pi**2)
            sigma8 = np.sqrt(sigma8_sq)
            Omega_m = 0.315
            metrics['S8'] = sigma8 * np.sqrt(Omega_m / 0.3)
        except:
            metrics['S8'] = 0.84
        
        # BAO distances
        try:
            lcdm_data = np.loadtxt(lcdm_bg_file)
            z_lcdm = lcdm_data[:, 0]
            D_comov_lcdm = lcdm_data[:, 4]
            
            bao_residuals = []
            for z_bao in [0.35, 0.57]:
                D = np.interp(z_bao, z[::-1], D_comov[::-1])
                D_lcdm = np.interp(z_bao, z_lcdm[::-1], D_comov_lcdm[::-1])
                bao_residuals.append(abs(D - D_lcdm) / D_lcdm)
            metrics['BAO_frac_max'] = max(bao_residuals)
        except:
            metrics['BAO_frac_max'] = 0.10
        
        # CMB TT RMS (ℓ=30-2000)
        try:
            cl = np.loadtxt(cl_file)
            cl_lcdm = np.loadtxt(lcdm_cl_file)
            
            ell = cl[:, 0]
            TT = cl[:, 1]
            ell_lcdm = cl_lcdm[:, 0]
            TT_lcdm = cl_lcdm[:, 1]
            
            # Interpolate to common grid
            ell_common = ell[(ell >= 30) & (ell <= 2000)]
            TT_interp = np.interp(ell_common, ell, TT)
            TT_lcdm_interp = np.interp(ell_common, ell_lcdm, TT_lcdm)
            
            # RMS fractional residual
            residual = (TT_interp - TT_lcdm_interp) / TT_lcdm_interp
            metrics['CMB_RMS'] = np.sqrt(np.mean(residual**2))
        except:
            metrics['CMB_RMS'] = 0.50
        
    except Exception as e:
        metrics = {'error': str(e)}
    
    return metrics

# =============================================================================
# χ² COMPUTATION
# =============================================================================

def compute_chi2(metrics):
    """Compute χ² against data."""
    chi2 = {}
    
    # H0 (SH0ES)
    chi2['H0'] = ((metrics['H0'] - TARGETS['H0_target']) / TARGETS['H0_sigma'])**2
    
    # S8 (KiDS)
    chi2['S8'] = ((metrics['S8'] - TARGETS['S8_target']) / TARGETS['S8_sigma'])**2
    
    # CMB (rough proxy)
    chi2['CMB'] = (metrics['CMB_RMS'] / 0.05)**2
    
    # BAO
    chi2['BAO'] = (metrics['BAO_frac_max'] / 0.01)**2
    
    chi2['total'] = chi2['H0'] + chi2['S8'] + chi2['CMB'] + chi2['BAO']
    
    return chi2

def compute_lcdm_chi2():
    """Compute χ² for ΛCDM."""
    chi2 = {}
    chi2['H0'] = ((LCDM['H0'] - TARGETS['H0_target']) / TARGETS['H0_sigma'])**2
    chi2['S8'] = ((LCDM['S8'] - TARGETS['S8_target']) / TARGETS['S8_sigma'])**2
    chi2['CMB'] = 0.0  # LCDM is the reference
    chi2['BAO'] = 0.0
    chi2['total'] = chi2['H0'] + chi2['S8']
    return chi2

# =============================================================================
# CLASSIFICATION
# =============================================================================

def classify_point(metrics):
    """Classify point as VIABLE, NEAR-MISS, or EXCLUDED."""
    violations = []
    
    # f_EDE bounds
    if metrics['f_EDE'] < CONSTRAINTS['f_EDE_min']:
        violations.append(('f_EDE_low', metrics['f_EDE'] / CONSTRAINTS['f_EDE_min']))
    if metrics['f_EDE'] > CONSTRAINTS['f_EDE_max']:
        violations.append(('f_EDE_high', metrics['f_EDE'] / CONSTRAINTS['f_EDE_max']))
    
    # z_peak bounds
    if metrics['z_peak'] < CONSTRAINTS['z_peak_min']:
        violations.append(('z_peak_low', metrics['z_peak'] / CONSTRAINTS['z_peak_min']))
    if metrics['z_peak'] > CONSTRAINTS['z_peak_max']:
        violations.append(('z_peak_high', CONSTRAINTS['z_peak_max'] / metrics['z_peak']))
    
    # CMB RMS
    if metrics['CMB_RMS'] > CONSTRAINTS['CMB_RMS_max']:
        violations.append(('CMB_RMS', metrics['CMB_RMS'] / CONSTRAINTS['CMB_RMS_max']))
    
    # BAO
    if metrics['BAO_frac_max'] > CONSTRAINTS['BAO_frac_max']:
        violations.append(('BAO', metrics['BAO_frac_max'] / CONSTRAINTS['BAO_frac_max']))
    
    if len(violations) == 0:
        # Check if it helps tensions
        helps_H0 = metrics['H0'] > 70.5
        helps_S8 = metrics['S8'] < 0.78
        if helps_H0 or helps_S8:
            return 'VIABLE', violations
        else:
            return 'VIABLE_NO_HELP', violations
    
    # Check severity of violations
    max_violation = max(v[1] for v in violations)
    if max_violation < 1.5:  # < 50% over threshold
        return 'NEAR-MISS', violations
    else:
        return 'EXCLUDED', violations

# =============================================================================
# MAIN SCAN
# =============================================================================

def main():
    print("=" * 70)
    print("SYSTEMATIC SCAN: Ridder Unified Model")
    print("=" * 70)
    print(f"\nFrozen model with {len(LAMBDA_TAIL_VALUES)}×{len(F_AXION_VALUES)} = "
          f"{len(LAMBDA_TAIL_VALUES) * len(F_AXION_VALUES)} points")
    print(f"\nConstraints:")
    print(f"  f_EDE: [{CONSTRAINTS['f_EDE_min']}, {CONSTRAINTS['f_EDE_max']}]")
    print(f"  z_peak: [{CONSTRAINTS['z_peak_min']}, {CONSTRAINTS['z_peak_max']}]")
    print(f"  CMB RMS: < {CONSTRAINTS['CMB_RMS_max']*100:.0f}%")
    print(f"  BAO frac: < {CONSTRAINTS['BAO_frac_max']*100:.0f}%")
    
    # ΛCDM reference χ²
    lcdm_chi2 = compute_lcdm_chi2()
    print(f"\nΛCDM reference χ² = {lcdm_chi2['total']:.1f}")
    print(f"  (H0: {lcdm_chi2['H0']:.1f}, S8: {lcdm_chi2['S8']:.1f})")
    
    results = []
    viable = []
    near_miss = []
    excluded = []
    
    total = len(LAMBDA_TAIL_VALUES) * len(F_AXION_VALUES)
    count = 0
    
    print(f"\n{'='*70}")
    print("SCANNING...")
    print(f"{'='*70}\n")
    
    for lambda_tail in LAMBDA_TAIL_VALUES:
        for f_axion in F_AXION_VALUES:
            count += 1
            label = f"L{lambda_tail}_f{int(f_axion*100):02d}"
            
            # Create INI
            ini_content = create_ini(lambda_tail, f_axion, f"{OUTPUT_DIR}/{label}")
            ini_path = f"{OUTPUT_DIR}/{label}.ini"
            
            with open(ini_path, 'w') as f:
                f.write(ini_content)
            
            # Run CLASS
            result = subprocess.run(
                ['./class', ini_path],
                cwd=CLASS_DIR,
                capture_output=True, text=True, timeout=600
            )
            
            if result.returncode != 0:
                print(f"[{count}/{total}] {label}: FAILED")
                continue
            
            # Extract metrics
            bg_file = f"{OUTPUT_DIR}/{label}00_background.dat"
            cl_file = f"{OUTPUT_DIR}/{label}00_cl.dat"
            pk_file = f"{OUTPUT_DIR}/{label}00_pk.dat"
            lcdm_bg = f"{OUTPUT_DIR}/lcdm00_background.dat"
            lcdm_cl = f"{OUTPUT_DIR}/lcdm00_cl.dat"
            
            metrics = extract_metrics(bg_file, cl_file, pk_file, lcdm_bg, lcdm_cl)
            
            if 'error' in metrics:
                print(f"[{count}/{total}] {label}: ERROR - {metrics['error']}")
                continue
            
            # Compute χ² and classify
            chi2 = compute_chi2(metrics)
            classification, violations = classify_point(metrics)
            
            result_entry = {
                'lambda_tail': lambda_tail,
                'f_axion': f_axion,
                'H0': metrics['H0'],
                'S8': metrics['S8'],
                'f_EDE': metrics['f_EDE'],
                'z_peak': metrics['z_peak'],
                'CMB_RMS': metrics['CMB_RMS'],
                'BAO_frac': metrics['BAO_frac_max'],
                'chi2_total': chi2['total'],
                'chi2_H0': chi2['H0'],
                'chi2_S8': chi2['S8'],
                'classification': classification,
                'violations': violations,
                'delta_chi2': chi2['total'] - lcdm_chi2['total'],
            }
            results.append(result_entry)
            
            # Classify
            if classification.startswith('VIABLE'):
                viable.append(result_entry)
            elif classification == 'NEAR-MISS':
                near_miss.append(result_entry)
            else:
                excluded.append(result_entry)
            
            # Status
            status_sym = {'VIABLE': '✓', 'VIABLE_NO_HELP': '○', 
                          'NEAR-MISS': '~', 'EXCLUDED': '✗'}
            print(f"[{count}/{total}] {label}: {status_sym.get(classification, '?')} "
                  f"H0={metrics['H0']:.1f} S8={metrics['S8']:.2f} "
                  f"f_EDE={metrics['f_EDE']:.2f} Δχ²={chi2['total'] - lcdm_chi2['total']:+.1f}")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"\nTotal points: {len(results)}")
    print(f"  VIABLE: {len(viable)}")
    print(f"  NEAR-MISS: {len(near_miss)}")
    print(f"  EXCLUDED: {len(excluded)}")
    
    if viable:
        print(f"\n--- VIABLE POINTS ---")
        print(f"{'Λ':>5} {'f':>5} {'H0':>6} {'S8':>5} {'f_EDE':>6} {'Δχ²':>7}")
        for v in sorted(viable, key=lambda x: x['delta_chi2']):
            print(f"{v['lambda_tail']:>5} {v['f_axion']:>5.2f} {v['H0']:>6.1f} "
                  f"{v['S8']:>5.2f} {v['f_EDE']:>6.2f} {v['delta_chi2']:>+7.1f}")
    
    if near_miss:
        print(f"\n--- NEAR-MISS POINTS (might be salvageable) ---")
        print(f"{'Λ':>5} {'f':>5} {'H0':>6} {'S8':>5} {'f_EDE':>6} {'Violations':>20}")
        for n in sorted(near_miss, key=lambda x: x['delta_chi2'])[:10]:
            viol_str = ', '.join([v[0] for v in n['violations']])
            print(f"{n['lambda_tail']:>5} {n['f_axion']:>5.2f} {n['H0']:>6.1f} "
                  f"{n['S8']:>5.2f} {n['f_EDE']:>6.2f} {viol_str:>20}")
    
    # Save results
    output_file = f"{OUTPUT_DIR}/systematic_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'fixed_params': FIXED_PARAMS,
            'constraints': CONSTRAINTS,
            'targets': TARGETS,
            'lcdm_chi2': lcdm_chi2,
            'results': results,
            'summary': {
                'viable': len(viable),
                'near_miss': len(near_miss),
                'excluded': len(excluded),
            }
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Final verdict
    print(f"\n{'='*70}")
    if viable:
        best = min(viable, key=lambda x: x['delta_chi2'])
        print(f"VERDICT: Model has {len(viable)} viable points!")
        print(f"Best: Λ={best['lambda_tail']}meV, f={best['f_axion']:.2f}")
        print(f"       H0={best['H0']:.1f}, S8={best['S8']:.2f}, Δχ²={best['delta_chi2']:+.1f}")
    elif near_miss:
        print(f"VERDICT: No viable points, but {len(near_miss)} near-misses.")
        print("Consider relaxing constraints or modifying potential shape.")
    else:
        print(f"VERDICT: Model excluded. All {len(excluded)} points fail constraints.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

