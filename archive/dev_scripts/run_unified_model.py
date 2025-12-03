#!/usr/bin/env python3
"""
UNIFIED MODEL: Single Button API
================================
One script that does everything:
1. Generate INI from parameters
2. Run CLASS
3. Extract all observables
4. Compute goodness scores
5. Emit JSON summary + plots

Usage:
  python3 run_unified_model.py --Lambda_tail 0.020 --f_axion 0.40
  python3 run_unified_model.py --Lambda_tail 0.018 --f_axion 0.35 --output results/
"""

import argparse
import subprocess
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime

CLASS_BIN = "phase2/class/class"
OUTPUT_DIR = Path("output")

# Reference values
R_S_LCDM = 147.04
H0_LCDM = 67.36
H0_SHOES = 73.0
S8_PLANCK = 0.834
S8_KIDS = 0.759

# Target values for scoring
H0_TARGET = 71.0
S8_TARGET = 0.76

# Scoring weights (roughly 1-sigma equivalent)
W_H0 = 1.0 / (1.0)**2      # 1 km/s/Mpc ~ 1 sigma
W_S8 = 1.0 / (0.02)**2     # 0.02 ~ 1 sigma  
W_CMB = 1.0 / (0.10)**2    # 10% RMS ~ 1 sigma
W_BAO = 1.0 / (0.03)**2    # 3% BAO error ~ 1 sigma

INI_TEMPLATE = """
output = tCl,pCl,mPk
root = {root}
H0 = 67.36
T_cmb = 2.7255
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842
k_pivot = 0.05

use_ridder = yes
ridder_model_type = unified
gauge = newtonian

ridder_use_tail = yes
ridder_Lambda_tail_eV = {lambda_tail}
ridder_alpha_tail = 1.0
ridder_n_tail = 1.0

ridder_use_shelf = yes
ridder_m_axion = 7e4
ridder_f_axion = {f_axion}
ridder_n_EDE = 3.0
ridder_theta_EDE_low = 0.5
ridder_theta_EDE_high = 3.5
ridder_sigma_theta_EDE = 0.5

ridder_use_plateau = no
ridder_f = 7.305e26
theta_i_ridder = 2.5
beta_ridder = 0.0
ridder_c_slow = 0.0

write background = yes
background_verbose = 0
l_max_scalars = 2500
P_k_max_h/Mpc = 1.7
"""

def run_class(ini_file, timeout=180):
    """Run CLASS and return success status."""
    result = subprocess.run(
        [CLASS_BIN, ini_file],
        capture_output=True, text=True, timeout=timeout
    )
    return result.returncode == 0, result.stderr

def load_background(bg_file):
    """Load background file with automatic column detection."""
    bg = np.loadtxt(bg_file)
    ncols = bg.shape[1]
    
    # Ridder runs have 24 columns
    if ncols >= 20:
        return {
            'z': bg[:, 0],
            'H': bg[:, 3] * 299792.458,
            'r_s': bg[:, 7],
            'rho_ridder': bg[:, 14],
            'p_ridder': bg[:, 15],
            'rho_tot': bg[:, 19],
            'rho_b': bg[:, 9],
            'rho_cdm': bg[:, 10],
            'rho_crit': bg[:, 13],
        }
    else:
        return {
            'z': bg[:, 0],
            'H': bg[:, 3] * 299792.458,
            'r_s': bg[:, 7],
            'rho_ridder': np.zeros_like(bg[:, 0]),
            'p_ridder': np.zeros_like(bg[:, 0]),
            'rho_tot': bg[:, 14],
            'rho_b': bg[:, 9],
            'rho_cdm': bg[:, 10],
            'rho_crit': bg[:, 13],
        }

def extract_all_observables(bg, pk_file, cl_file, cl_lcdm_file=None):
    """Extract all observables from CLASS output."""
    z = bg['z']
    
    # f_ridder
    valid = (bg['rho_tot'] > 0) & (bg['rho_ridder'] > 0)
    f_ridder = np.zeros_like(z)
    f_ridder[valid] = bg['rho_ridder'][valid] / bg['rho_tot'][valid]
    
    # EDE peak
    mask_ede = (z > 1000) & (z < 20000)
    if mask_ede.any():
        f_ede = f_ridder[mask_ede]
        z_ede = z[mask_ede]
        peak_idx = np.argmax(f_ede)
        f_peak = float(f_ede[peak_idx])
        z_peak = float(z_ede[peak_idx])
    else:
        f_peak, z_peak = 0.0, 0.0
    
    # Late-time
    f_late = float(f_ridder[-1])
    w_late = 0.0
    if bg['rho_ridder'][-1] > 1e-50:
        w_late = float(bg['p_ridder'][-1] / bg['rho_ridder'][-1])
    
    # r_s at drag
    idx_drag = np.argmin(np.abs(z - 1060))
    r_s_drag = float(bg['r_s'][idx_drag])
    
    # H0 via inverse r_s scaling
    H0_eff = H0_LCDM * (R_S_LCDM / r_s_drag)
    delta_rs = (r_s_drag - R_S_LCDM) / R_S_LCDM
    
    # Omega_m
    Omega_m = float((bg['rho_b'][-1] + bg['rho_cdm'][-1]) / bg['rho_crit'][-1])
    
    obs = {
        'H0': float(H0_eff),
        'delta_rs': float(delta_rs),
        'rs_Mpc': r_s_drag,
        'Omega_m': Omega_m,
        'f_EDE': f_peak,
        'z_peak': z_peak,
        'f_late': f_late,
        'w_late': w_late,
    }
    
    # S8 from P(k)
    if pk_file.exists():
        pk = np.loadtxt(pk_file)
        k, Pk = pk[:, 0], pk[:, 1]
        R = 8.0
        x = k * R
        W = np.where(x > 0.01, 3.0 * (np.sin(x) - x * np.cos(x)) / x**3, 1.0)
        sigma8 = np.sqrt(np.trapz(Pk * W**2 * k**2, k) / (2 * np.pi**2))
        S8 = sigma8 * np.sqrt(Omega_m / 0.3)
        obs['sigma8'] = float(sigma8)
        obs['S8'] = float(S8)
    
    # CMB diagnostics
    if cl_file.exists():
        cl = np.loadtxt(cl_file)
        ell = cl[:, 0]
        TT = cl[:, 1]
        obs['cmb_TT_peak_ell'] = float(ell[np.argmax(TT)])
        
        if cl_lcdm_file and cl_lcdm_file.exists():
            cl_lcdm = np.loadtxt(cl_lcdm_file)
            TT_lcdm = cl_lcdm[:, 1]
            residual = (TT - TT_lcdm) / TT_lcdm
            obs['cmb_max_residual'] = float(np.max(np.abs(residual)))
            obs['cmb_rms_residual'] = float(np.sqrt(np.mean(residual**2)))
    
    # BAO distances at key redshifts
    bao_residuals = {}
    for z_bao in [0.35, 0.57, 0.61]:
        idx = np.argmin(np.abs(z - z_bao))
        H_model = bg['H'][idx]
        # Compare to approximate LCDM values
        H_lcdm_approx = H0_LCDM * np.sqrt(0.3 * (1 + z_bao)**3 + 0.7)
        bao_residuals[str(z_bao)] = float((H_model - H_lcdm_approx) / H_lcdm_approx)
    obs['bao_residuals'] = bao_residuals
    
    return obs

def compute_goodness_score(obs):
    """Compute goodness score J (lower is better)."""
    H0 = obs.get('H0', H0_LCDM)
    S8 = obs.get('S8', S8_PLANCK)
    cmb_rms = obs.get('cmb_rms_residual', 0.5)
    
    # Average BAO residual
    bao_avg = 0.0
    if 'bao_residuals' in obs:
        bao_avg = np.mean([abs(v) for v in obs['bao_residuals'].values()])
    
    # Score components
    J_H0 = W_H0 * max(0, H0_TARGET - H0)**2  # Penalize if below target
    J_S8 = W_S8 * max(0, S8 - S8_TARGET)**2   # Penalize if above target
    J_CMB = W_CMB * cmb_rms**2
    J_BAO = W_BAO * bao_avg**2
    
    J_total = J_H0 + J_S8 + J_CMB + J_BAO
    
    return {
        'J_total': float(J_total),
        'J_H0': float(J_H0),
        'J_S8': float(J_S8),
        'J_CMB': float(J_CMB),
        'J_BAO': float(J_BAO),
    }

def run_unified_model(lambda_tail, f_axion, output_dir=None, run_lcdm=True):
    """
    Main entry point: run unified model with given parameters.
    Returns summary dict and saves to JSON.
    """
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
    else:
        output_dir = Path(".")
    
    tag = f"L{lambda_tail*1e3:.0f}_f{f_axion:.2f}".replace(".", "p")
    root = OUTPUT_DIR / f"unified_run_{tag}"
    
    # Generate INI
    ini = INI_TEMPLATE.format(
        root=root,
        lambda_tail=lambda_tail,
        f_axion=f_axion
    )
    ini_file = f"unified_run_{tag}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini)
    
    # Run LCDM baseline if needed
    cl_lcdm_file = None
    if run_lcdm:
        subprocess.run([CLASS_BIN, "lcdm_baseline.ini"], 
                      capture_output=True, timeout=180)
        cl_lcdm_file = OUTPUT_DIR / "lcdm_baseline00_cl.dat"
    
    # Run CLASS
    success, stderr = run_class(ini_file)
    os.remove(ini_file)
    
    if not success:
        return {
            'success': False,
            'error': stderr[:500],
            'config': {
                'Lambda_tail_meV': lambda_tail * 1e3,
                'f_axion': f_axion,
            }
        }
    
    # Load and analyze
    bg_file = Path(f"{root}00_background.dat")
    pk_file = Path(f"{root}00_pk.dat")
    cl_file = Path(f"{root}00_cl.dat")
    
    bg = load_background(bg_file)
    obs = extract_all_observables(bg, pk_file, cl_file, cl_lcdm_file)
    scores = compute_goodness_score(obs)
    
    # Assemble summary
    summary = {
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'config': {
            'Lambda_tail_meV': lambda_tail * 1e3,
            'f_axion': f_axion,
        },
        'observables': obs,
        'scores': scores,
        'targets_met': {
            'H0_above_71': obs.get('H0', 0) > 71,
            'S8_below_078': obs.get('S8', 1) < 0.78,
        }
    }
    
    # Save JSON
    json_file = output_dir / f"unified_summary_{tag}.json"
    with open(json_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary

def print_summary(summary):
    """Pretty-print the summary."""
    if not summary.get('success', False):
        print(f"❌ RUN FAILED: {summary.get('error', 'Unknown error')}")
        return
    
    cfg = summary['config']
    obs = summary['observables']
    scores = summary['scores']
    targets = summary['targets_met']
    
    print()
    print("=" * 60)
    print("UNIFIED MODEL SUMMARY")
    print("=" * 60)
    print(f"Config: Λ_tail = {cfg['Lambda_tail_meV']:.1f} meV, f_axion = {cfg['f_axion']:.2f}")
    print()
    
    print("### Observables ###")
    print(f"  H0          = {obs.get('H0', 0):.2f} km/s/Mpc")
    print(f"  S8          = {obs.get('S8', 0):.4f}")
    print(f"  Ω_m         = {obs.get('Omega_m', 0):.4f}")
    print(f"  f_EDE       = {obs.get('f_EDE', 0):.4f} at z = {obs.get('z_peak', 0):.0f}")
    print(f"  r_s         = {obs.get('rs_Mpc', 0):.2f} Mpc (Δ = {obs.get('delta_rs', 0)*100:.2f}%)")
    print(f"  f_late      = {obs.get('f_late', 0):.4f}")
    print()
    
    print("### Diagnostics ###")
    print(f"  CMB RMS residual = {obs.get('cmb_rms_residual', 0)*100:.1f}%")
    print(f"  CMB max residual = {obs.get('cmb_max_residual', 0)*100:.1f}%")
    if 'bao_residuals' in obs:
        print(f"  BAO residuals: ", end="")
        for z, r in obs['bao_residuals'].items():
            print(f"z={z}: {r*100:+.1f}%  ", end="")
        print()
    print()
    
    print("### Goodness Score ###")
    print(f"  J_total = {scores['J_total']:.2f}")
    print(f"    J_H0  = {scores['J_H0']:.2f}")
    print(f"    J_S8  = {scores['J_S8']:.2f}")
    print(f"    J_CMB = {scores['J_CMB']:.2f}")
    print(f"    J_BAO = {scores['J_BAO']:.2f}")
    print()
    
    print("### Targets ###")
    h0_status = "✓" if targets['H0_above_71'] else "✗"
    s8_status = "✓" if targets['S8_below_078'] else "✗"
    print(f"  H0 > 71: {h0_status}")
    print(f"  S8 < 0.78: {s8_status}")
    
    if targets['H0_above_71'] and targets['S8_below_078']:
        print()
        print("  ★ BOTH TARGETS MET ★")
    print()

def main():
    parser = argparse.ArgumentParser(description="Run unified Ridder model")
    parser.add_argument("--Lambda_tail", type=float, default=0.020,
                       help="Tail energy scale in eV (default: 0.020)")
    parser.add_argument("--f_axion", type=float, default=0.40,
                       help="Axion decay constant fraction (default: 0.40)")
    parser.add_argument("--output", type=str, default=None,
                       help="Output directory for results")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress output")
    args = parser.parse_args()
    
    if not args.quiet:
        print(f"Running unified model: Λ_tail = {args.Lambda_tail*1e3:.1f} meV, f_axion = {args.f_axion:.2f}")
    
    summary = run_unified_model(args.Lambda_tail, args.f_axion, args.output)
    
    if not args.quiet:
        print_summary(summary)
    
    return 0 if summary.get('success', False) else 1

if __name__ == "__main__":
    exit(main())

