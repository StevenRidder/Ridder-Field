#!/usr/bin/env python3
"""
RIDDER UNIFIED MODEL SOLVER

This is not a parameter explorer. This is a decision system.

Model 1.0: Ridder unified scalar with fixed potential shape, fixed IC, 
           two free parameters (Lambda_tail, f_axion).

Every point is classified as:
  - VIABLE: passes all four buckets
  - TENSION_ONLY: passes A (helps tensions) but fails B, C, or D
  - RULED_OUT: fails hard constraints

The solver answers: Does this model survive confrontation with data?
"""

import subprocess
import numpy as np
import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# =============================================================================
# MODEL DEFINITION (FROZEN - DO NOT TOUCH)
# =============================================================================

MODEL_VERSION = "1.0"
MODEL_NAME = "Ridder Unified Scalar"

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

# =============================================================================
# HARD CONSTRAINTS (THE FOUR BUCKETS)
# =============================================================================

@dataclass
class Constraints:
    """Hard constraints that define viable vs ruled out."""
    
    # Bucket A: Tension relief targets
    H0_min: float = 71.0
    H0_max: float = 74.0
    S8_min: float = 0.70
    S8_max: float = 0.78
    
    # Bucket B: EDE sanity
    f_EDE_min: float = 0.05
    f_EDE_max: float = 0.25
    z_peak_min: float = 3000.0
    z_peak_max: float = 5000.0
    
    # Bucket C: CMB and BAO tolerances
    CMB_RMS_max: float = 0.20  # 20%
    BAO_frac_max: float = 0.03  # 3%
    
    # Bucket D: Late-time DE behavior
    w_z0_deviation_max: float = 0.01  # |w(z=0) + 1| <= 0.01
    w_z2_min: float = -1.02
    w_z2_max: float = -0.95

CONSTRAINTS = Constraints()

# =============================================================================
# JSON CONTRACT
# =============================================================================

@dataclass
class ModelOutput:
    """The full JSON contract for every model evaluation."""
    
    # Inputs
    Lambda_tail_meV: float
    f_axion: float
    
    # Tension metrics (Bucket A)
    H0: float
    S8: float
    sigma8: float
    Omega_m: float
    
    # EDE metrics (Bucket B)
    f_EDE: float
    z_peak: float
    
    # Consistency metrics (Bucket C)
    cmb_rms_tt: float
    bao_residual_035: float
    bao_residual_057: float
    
    # Late-time DE metrics (Bucket D)
    w_z0: float
    w_z2: float
    
    # Classification
    passes_H0_S8: bool = False
    passes_EDE: bool = False
    passes_CMB_BAO: bool = False
    passes_DE: bool = False
    status: str = "unknown"
    
    # Comparison to LCDM
    delta_chi2: float = 0.0

# =============================================================================
# CLASSIFIER
# =============================================================================

def classify(output: ModelOutput, c: Constraints = CONSTRAINTS) -> ModelOutput:
    """Apply hard constraints and classify the point."""
    
    # Bucket A: Tension relief
    output.passes_H0_S8 = (
        c.H0_min <= output.H0 <= c.H0_max and
        c.S8_min <= output.S8 <= c.S8_max
    )
    
    # Bucket B: EDE sanity
    output.passes_EDE = (
        c.f_EDE_min <= output.f_EDE <= c.f_EDE_max and
        c.z_peak_min <= output.z_peak <= c.z_peak_max
    )
    
    # Bucket C: CMB and BAO
    output.passes_CMB_BAO = (
        output.cmb_rms_tt <= c.CMB_RMS_max and
        output.bao_residual_035 <= c.BAO_frac_max and
        output.bao_residual_057 <= c.BAO_frac_max
    )
    
    # Bucket D: Late-time DE
    output.passes_DE = (
        abs(output.w_z0 + 1) <= c.w_z0_deviation_max and
        c.w_z2_min <= output.w_z2 <= c.w_z2_max
    )
    
    # Final classification
    if output.passes_H0_S8 and output.passes_EDE and output.passes_CMB_BAO and output.passes_DE:
        output.status = "VIABLE"
    elif output.passes_H0_S8:
        output.status = "TENSION_ONLY"
    else:
        output.status = "RULED_OUT"
    
    return output

# =============================================================================
# CLASS INTERFACE
# =============================================================================

CLASS_DIR = '/home/<VM_USER>/Ridder-Field/phase2/class'
OUTPUT_DIR = '/home/<VM_USER>/Ridder-Field/phase2/class/output/solver'

def create_ini(lambda_tail: float, f_axion: float, root: str) -> str:
    """Generate frozen model INI."""
    return f"""# Ridder Model {MODEL_VERSION}
# Lambda_tail={lambda_tail}meV, f_axion={f_axion}

H0 = 67.36
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842

use_ridder = yes
gauge = newtonian
ridder_model_type = unified

ridder_use_tail = yes
ridder_Lambda_tail_eV = {lambda_tail}e-3
ridder_alpha_tail = {FIXED_PARAMS['alpha_tail']}
ridder_n_tail = {FIXED_PARAMS['n_tail']}

ridder_use_shelf = yes
ridder_m_axion = {FIXED_PARAMS['m_axion']}
ridder_f_axion = {f_axion}
ridder_n_EDE = {FIXED_PARAMS['n_shelf']}
ridder_theta_EDE_low = {FIXED_PARAMS['theta_EDE_low']}
ridder_theta_EDE_high = {FIXED_PARAMS['theta_EDE_high']}
ridder_sigma_theta_EDE = {FIXED_PARAMS['sigma_EDE']}

ridder_use_plateau = no
ridder_f = {FIXED_PARAMS['ridder_f']}
theta_i_ridder = {FIXED_PARAMS['theta_i']}
beta_ridder = {FIXED_PARAMS['beta_ridder']}
ridder_c_slow = {FIXED_PARAMS['ridder_c_slow']}

output = tCl,mPk
write background = yes
l_max_scalars = 2500
root = {root}
"""

def run_class(ini_path: str) -> bool:
    """Run CLASS and return success."""
    result = subprocess.run(
        ['./class', ini_path],
        cwd=CLASS_DIR,
        capture_output=True,
        text=True,
        timeout=600
    )
    return result.returncode == 0

def extract_metrics(label: str, lcdm_label: str = "lcdm") -> Optional[ModelOutput]:
    """Extract all metrics from CLASS output."""
    try:
        bg_file = f"{OUTPUT_DIR}/{label}00_background.dat"
        cl_file = f"{OUTPUT_DIR}/{label}00_cl.dat"
        pk_file = f"{OUTPUT_DIR}/{label}00_pk.dat"
        lcdm_bg = f"{OUTPUT_DIR}/{lcdm_label}00_background.dat"
        lcdm_cl = f"{OUTPUT_DIR}/{lcdm_label}00_cl.dat"
        
        # Background
        data = np.loadtxt(bg_file)
        z = data[:, 0]
        H = data[:, 3]
        rho_ridder = data[:, 14]
        rho_tot = data[:, 19]
        D_comov = data[:, 4]
        p_ridder = data[:, 15]
        
        # f_EDE and z_peak
        f_ridder = rho_ridder / rho_tot
        idx_max = np.argmax(f_ridder)
        f_EDE = float(f_ridder[idx_max])
        z_peak = float(z[idx_max])
        
        # H0
        idx_0 = np.argmin(np.abs(z))
        H0 = float(H[idx_0] * 299792.458)
        
        # w(z) = p/rho
        w = p_ridder / rho_ridder
        w_z0 = float(np.interp(0.0, z[::-1], w[::-1]))
        w_z2 = float(np.interp(2.0, z[::-1], w[::-1]))
        
        # Omega_m (approximate)
        Omega_m = 0.315  # Planck value
        
        # S8 from P(k)
        pk_data = np.loadtxt(pk_file)
        k = pk_data[:, 0]
        Pk = pk_data[:, 1]
        R = 8.0
        x = k * R
        W = np.where(x > 0.01, 3 * (np.sin(x) - x * np.cos(x)) / x**3, 1.0)
        integrand = k**2 * Pk * W**2
        sigma8_sq = np.trapz(integrand, k) / (2 * np.pi**2)
        sigma8 = float(np.sqrt(sigma8_sq))
        S8 = float(sigma8 * np.sqrt(Omega_m / 0.3))
        
        # BAO residuals
        lcdm_data = np.loadtxt(lcdm_bg)
        z_lcdm = lcdm_data[:, 0]
        D_lcdm = lcdm_data[:, 4]
        
        D_035 = np.interp(0.35, z[::-1], D_comov[::-1])
        D_057 = np.interp(0.57, z[::-1], D_comov[::-1])
        D_lcdm_035 = np.interp(0.35, z_lcdm[::-1], D_lcdm[::-1])
        D_lcdm_057 = np.interp(0.57, z_lcdm[::-1], D_lcdm[::-1])
        
        bao_035 = float(abs(D_035 - D_lcdm_035) / D_lcdm_035)
        bao_057 = float(abs(D_057 - D_lcdm_057) / D_lcdm_057)
        
        # CMB RMS
        cl = np.loadtxt(cl_file)
        cl_lcdm = np.loadtxt(lcdm_cl)
        
        ell = cl[:, 0]
        TT = cl[:, 1]
        ell_lcdm = cl_lcdm[:, 0]
        TT_lcdm = cl_lcdm[:, 1]
        
        mask = (ell >= 30) & (ell <= 2000)
        ell_common = ell[mask]
        TT_interp = np.interp(ell_common, ell, TT)
        TT_lcdm_interp = np.interp(ell_common, ell_lcdm, TT_lcdm)
        
        residual = (TT_interp - TT_lcdm_interp) / TT_lcdm_interp
        cmb_rms = float(np.sqrt(np.mean(residual**2)))
        
        # Delta chi2 (simplified)
        chi2_H0 = ((H0 - 73.04) / 1.04)**2
        chi2_S8 = ((S8 - 0.766) / 0.020)**2
        chi2_lcdm_H0 = ((67.36 - 73.04) / 1.04)**2
        chi2_lcdm_S8 = ((0.834 - 0.766) / 0.020)**2
        delta_chi2 = (chi2_H0 + chi2_S8) - (chi2_lcdm_H0 + chi2_lcdm_S8)
        
        return ModelOutput(
            Lambda_tail_meV=0.0,  # Will be set by caller
            f_axion=0.0,
            H0=H0,
            S8=S8,
            sigma8=sigma8,
            Omega_m=Omega_m,
            f_EDE=f_EDE,
            z_peak=z_peak,
            cmb_rms_tt=cmb_rms,
            bao_residual_035=bao_035,
            bao_residual_057=bao_057,
            w_z0=w_z0,
            w_z2=w_z2,
            delta_chi2=float(delta_chi2),
        )
    except Exception as e:
        print(f"  Error extracting metrics: {e}")
        return None

# =============================================================================
# SOLVER
# =============================================================================

def solve(lambda_tail: float, f_axion: float) -> Optional[ModelOutput]:
    """Run the model at one point and return classified output."""
    
    label = f"L{int(lambda_tail)}_f{int(f_axion*100):02d}"
    root = f"{OUTPUT_DIR}/{label}"
    ini_path = f"{root}.ini"
    
    # Create INI
    ini_content = create_ini(lambda_tail, f_axion, root)
    with open(ini_path, 'w') as f:
        f.write(ini_content)
    
    # Run CLASS
    if not run_class(ini_path):
        return None
    
    # Extract metrics
    output = extract_metrics(label)
    if output is None:
        return None
    
    # Set inputs
    output.Lambda_tail_meV = lambda_tail
    output.f_axion = f_axion
    
    # Classify
    output = classify(output)
    
    return output

def run_lcdm_baseline():
    """Run LCDM baseline for comparison."""
    ini_content = f"""H0 = 67.36
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842

output = tCl,mPk
write background = yes
l_max_scalars = 2500
root = {OUTPUT_DIR}/lcdm
"""
    ini_path = f"{OUTPUT_DIR}/lcdm.ini"
    with open(ini_path, 'w') as f:
        f.write(ini_content)
    
    return run_class(ini_path)

# =============================================================================
# GRID SCAN
# =============================================================================

def scan_grid(lambda_values: List[float], f_values: List[float]) -> Dict:
    """Scan the 2D parameter space and classify every point."""
    
    print("=" * 70)
    print(f"RIDDER UNIFIED MODEL SOLVER v{MODEL_VERSION}")
    print("=" * 70)
    print(f"\nModel: {MODEL_NAME}")
    print(f"Free parameters: Lambda_tail (meV), f_axion")
    print(f"Grid: {len(lambda_values)} × {len(f_values)} = {len(lambda_values)*len(f_values)} points")
    
    print("\n--- HARD CONSTRAINTS ---")
    print(f"Bucket A (Tensions): {CONSTRAINTS.H0_min} ≤ H0 ≤ {CONSTRAINTS.H0_max}, "
          f"{CONSTRAINTS.S8_min} ≤ S8 ≤ {CONSTRAINTS.S8_max}")
    print(f"Bucket B (EDE): {CONSTRAINTS.f_EDE_min} ≤ f_EDE ≤ {CONSTRAINTS.f_EDE_max}, "
          f"{CONSTRAINTS.z_peak_min} ≤ z_peak ≤ {CONSTRAINTS.z_peak_max}")
    print(f"Bucket C (CMB/BAO): CMB_RMS ≤ {CONSTRAINTS.CMB_RMS_max*100:.0f}%, "
          f"BAO ≤ {CONSTRAINTS.BAO_frac_max*100:.0f}%")
    print(f"Bucket D (DE): |w(0)+1| ≤ {CONSTRAINTS.w_z0_deviation_max}, "
          f"{CONSTRAINTS.w_z2_min} ≤ w(2) ≤ {CONSTRAINTS.w_z2_max}")
    
    # Ensure LCDM baseline exists
    print("\nRunning LCDM baseline...")
    if not run_lcdm_baseline():
        print("ERROR: LCDM baseline failed!")
        return {}
    
    # Scan
    results = {
        'viable': [],
        'tension_only': [],
        'ruled_out': [],
        'failed': [],
    }
    
    total = len(lambda_values) * len(f_values)
    count = 0
    
    print(f"\n{'='*70}")
    print("SCANNING...")
    print(f"{'='*70}\n")
    
    for lambda_tail in lambda_values:
        for f_axion in f_values:
            count += 1
            
            output = solve(lambda_tail, f_axion)
            
            if output is None:
                print(f"[{count}/{total}] L={lambda_tail}, f={f_axion:.2f}: FAILED")
                results['failed'].append({'Lambda_tail': lambda_tail, 'f_axion': f_axion})
                continue
            
            # Status symbol
            symbols = {'VIABLE': '✓', 'TENSION_ONLY': '~', 'RULED_OUT': '✗'}
            sym = symbols.get(output.status, '?')
            
            # Bucket indicators
            A = 'A' if output.passes_H0_S8 else '-'
            B = 'B' if output.passes_EDE else '-'
            C = 'C' if output.passes_CMB_BAO else '-'
            D = 'D' if output.passes_DE else '-'
            
            print(f"[{count}/{total}] L={lambda_tail:2.0f} f={f_axion:.2f}: {sym} [{A}{B}{C}{D}] "
                  f"H0={output.H0:.1f} S8={output.S8:.2f} f_EDE={output.f_EDE:.2f} "
                  f"Δχ²={output.delta_chi2:+.1f}")
            
            # Store by status
            if output.status == 'VIABLE':
                results['viable'].append(asdict(output))
            elif output.status == 'TENSION_ONLY':
                results['tension_only'].append(asdict(output))
            else:
                results['ruled_out'].append(asdict(output))
    
    # Summary
    print(f"\n{'='*70}")
    print("FINAL VERDICT")
    print(f"{'='*70}")
    
    n_viable = len(results['viable'])
    n_tension = len(results['tension_only'])
    n_ruled = len(results['ruled_out'])
    n_failed = len(results['failed'])
    
    print(f"\nTotal: {total} points")
    print(f"  ✓ VIABLE (passes all): {n_viable}")
    print(f"  ~ TENSION_ONLY (helps tensions, fails elsewhere): {n_tension}")
    print(f"  ✗ RULED_OUT: {n_ruled}")
    print(f"  ? FAILED: {n_failed}")
    
    if n_viable > 0:
        print(f"\n--- VIABLE POINTS ---")
        print(f"{'Λ':>4} {'f':>5} {'H0':>6} {'S8':>5} {'f_EDE':>6} {'CMB%':>5} {'BAO%':>5} {'Δχ²':>6}")
        for v in sorted(results['viable'], key=lambda x: x['delta_chi2']):
            print(f"{v['Lambda_tail_meV']:>4.0f} {v['f_axion']:>5.2f} {v['H0']:>6.1f} "
                  f"{v['S8']:>5.2f} {v['f_EDE']:>6.2f} {v['cmb_rms_tt']*100:>5.1f} "
                  f"{max(v['bao_residual_035'], v['bao_residual_057'])*100:>5.1f} "
                  f"{v['delta_chi2']:>+6.1f}")
        
        best = min(results['viable'], key=lambda x: x['delta_chi2'])
        print(f"\n★ BEST VIABLE: Λ={best['Lambda_tail_meV']:.0f}meV, f={best['f_axion']:.2f}")
        print(f"  H0={best['H0']:.1f}, S8={best['S8']:.2f}, f_EDE={best['f_EDE']:.2f}")
        print(f"  CMB_RMS={best['cmb_rms_tt']*100:.1f}%, BAO={max(best['bao_residual_035'], best['bao_residual_057'])*100:.1f}%")
        print(f"  w(z=0)={best['w_z0']:.3f}, w(z=2)={best['w_z2']:.3f}")
        print(f"  Δχ²={best['delta_chi2']:+.1f} vs ΛCDM")
        print(f"\n>>> MODEL {MODEL_VERSION} SURVIVES: {n_viable} viable points found <<<")
    
    elif n_tension > 0:
        print(f"\n>>> MODEL {MODEL_VERSION} PARTIAL: Helps tensions but violates constraints <<<")
        print(f"    {n_tension} points help H0/S8 but fail EDE, CMB, BAO, or DE bounds")
        
        # Show best tension-only point
        best = min(results['tension_only'], key=lambda x: x['delta_chi2'])
        print(f"\n    Closest to viable: Λ={best['Lambda_tail_meV']:.0f}, f={best['f_axion']:.2f}")
        print(f"    H0={best['H0']:.1f}, S8={best['S8']:.2f}")
        print(f"    Failed: ", end="")
        fails = []
        if not best['passes_EDE']:
            fails.append(f"EDE (f={best['f_EDE']:.2f})")
        if not best['passes_CMB_BAO']:
            fails.append(f"CMB/BAO (CMB={best['cmb_rms_tt']*100:.0f}%)")
        if not best['passes_DE']:
            fails.append(f"DE (w0={best['w_z0']:.2f})")
        print(", ".join(fails))
    
    else:
        print(f"\n>>> MODEL {MODEL_VERSION} EXCLUDED: No points help tensions within constraints <<<")
    
    print(f"{'='*70}")
    
    # Save results
    output_file = f"{OUTPUT_DIR}/solver_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'model_version': MODEL_VERSION,
            'fixed_params': FIXED_PARAMS,
            'constraints': asdict(CONSTRAINTS),
            'grid': {'lambda_values': lambda_values, 'f_values': f_values},
            'results': results,
            'summary': {
                'viable': n_viable,
                'tension_only': n_tension,
                'ruled_out': n_ruled,
                'failed': n_failed,
            }
        }, f, indent=2)
    print(f"\nResults saved to: {output_file}")
    
    return results

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # The grid that matters
    LAMBDA_VALUES = [18, 20, 22, 24, 26, 28, 30]
    F_VALUES = [0.20, 0.25, 0.30, 0.35, 0.40]
    
    scan_grid(LAMBDA_VALUES, F_VALUES)

