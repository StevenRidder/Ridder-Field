#!/usr/bin/env python3
"""
Phase 1A: Analyze Beta Ladder Results

Extracts H₀, S₈, CMB chi-squared for each beta value.
Identifies optimal beta for balancing S₈ reduction with CMB fit.
"""

import numpy as np
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = REPO_ROOT / "phase2" / "class" / "output"
RESULTS_DIR = REPO_ROOT / "phase3_full_analysis" / "results"

# Reference values
RS_LCDM = 147.07923596941404  # From baseline
H0_INPUT = 67.36

print(f"\n{'='*70}")
print("PHASE 1A: BETA LADDER ANALYSIS")
print(f"{'='*70}\n")

# --------------------------------------------------------------------------
# Import existing extraction functions
# --------------------------------------------------------------------------

def compute_sigma8_from_pk(prefix):
    """Compute sigma8 from P(k) using top-hat window."""
    pk_file = OUTPUT_DIR / f"{prefix}00_pk.dat"
    if not pk_file.exists():
        pk_file = OUTPUT_DIR / f"{prefix}00_mPk.dat"
    if not pk_file.exists():
        return None
    
    data = np.loadtxt(pk_file)
    k = data[:, 0]
    P = data[:, 1]
    
    R = 8.0
    kR = k * R
    
    W = np.zeros_like(kR)
    mask = kR > 1e-4
    W[mask] = 3.0 * (np.sin(kR[mask]) - kR[mask] * np.cos(kR[mask])) / (kR[mask]**3)
    W[~mask] = 1.0 - (kR[~mask]**2) / 10.0
    
    integrand = k**2 * P * W**2
    sigma2 = np.trapz(integrand, k) / (2.0 * np.pi**2)
    
    return np.sqrt(sigma2)


def parse_params(prefix):
    """Parse parameters from CLASS output."""
    param_file = OUTPUT_DIR / f"{prefix}00_parameters.ini"
    if not param_file.exists():
        return {}
    
    params = {}
    with open(param_file, "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, val = line.split("=", 1)
                try:
                    params[key.strip()] = float(val.strip().split()[0])
                except ValueError:
                    params[key.strip()] = val.strip()
    
    return params


def compute_s8(prefix):
    """Compute S8 from sigma8 and Omega_m."""
    params = parse_params(prefix)
    sigma8 = compute_sigma8_from_pk(prefix)
    
    if sigma8 is None:
        return None, None, None
    
    omega_b = params.get("omega_b", 0.02237)
    omega_cdm = params.get("omega_cdm", 0.12)
    h = params.get("H0", H0_INPUT) / 100.0
    
    Omega_m = (omega_b + omega_cdm) / (h**2)
    S8 = sigma8 * np.sqrt(Omega_m / 0.3)
    
    return sigma8, Omega_m, S8


def compute_h0_eff(prefix):
    """Compute effective H0 from sound horizon."""
    bg_file = OUTPUT_DIR / f"{prefix}00_background.dat"
    if not bg_file.exists():
        return None, None
    
    # Read r_s from last line (final value at z=0 or thereabouts)
    data = np.loadtxt(bg_file)
    rs_model = data[-1, 7]  # Column 8 (0-indexed: 7) is comov.snd.hrz
    
    # H0_eff = H0_input × (r_s_LCDM / r_s_model)
    H0_eff = H0_INPUT * (RS_LCDM / rs_model)
    delta_H0 = H0_eff - H0_INPUT
    
    return H0_eff, delta_H0


def estimate_cmb_chi2(prefix):
    """
    Estimate CMB chi-squared as rough metric.
    
    For now, use RMS deviation as proxy.
    Full likelihood implementation in Phase 3.
    """
    cl_file = OUTPUT_DIR / f"{prefix}00_cl_lensed.dat"
    if not cl_file.exists():
        return None
    
    # Load unified and reference (Lambda=1.0, beta=0.05)
    data_unified = np.loadtxt(cl_file)
    
    ref_file = OUTPUT_DIR / "unified_baby_lambda1p0_00_cl_lensed.dat"
    if not ref_file.exists():
        # Use ΛCDM instead
        ref_file = OUTPUT_DIR / "lcdm_baseline_00_cl_lensed.dat"
    
    if ref_file.exists():
        data_ref = np.loadtxt(ref_file)
        
        # Compare TT at ell > 30 (avoid low-ell where both have issues)
        ell_unified = data_unified[:, 0]
        TT_unified = data_unified[:, 1]
        
        ell_ref = data_ref[:, 0]
        TT_ref = data_ref[:, 1]
        
        # Interpolate to common ell grid
        mask = (ell_unified >= 30) & (ell_unified <= 2000)
        ell_common = ell_unified[mask]
        TT_unified_subset = TT_unified[mask]
        TT_ref_interp = np.interp(ell_common, ell_ref, TT_ref)
        
        # Fractional RMS
        frac_diff = (TT_unified_subset - TT_ref_interp) / TT_ref_interp
        rms = np.sqrt(np.mean(frac_diff**2)) * 100  # percent
        
        # Rough chi-squared estimate (assuming 1% errors)
        chi2_approx = np.sum((frac_diff * 100)**2)
        
        return {"rms_tt": rms, "chi2_approx": chi2_approx}
    
    return None


# --------------------------------------------------------------------------
# Analyze each beta
# --------------------------------------------------------------------------

beta_values = [0.10, 0.15, 0.20]
results = []

print(f"{'Beta':>6s} {'H0_eff':>10s} {'ΔH0':>10s} {'σ₈':>10s} {'S₈':>10s} {'ΔS₈':>10s} {'CMB RMS':>10s}")
print("-" * 70)

lcdm_s8 = 0.8415  # From previous extraction

for beta in beta_values:
    prefix = f"unified_beta{str(beta).replace('.', 'p')}_"
    
    # Check if outputs exist
    bg_file = OUTPUT_DIR / f"{prefix}00_background.dat"
    if not bg_file.exists():
        print(f"{beta:6.2f} {'---':>10s} {'---':>10s} {'---':>10s} {'---':>10s} {'---':>10s} {'MISSING':>10s}")
        continue
    
    # Extract observables
    H0_eff, delta_H0 = compute_h0_eff(prefix)
    sigma8, Omega_m, S8 = compute_s8(prefix)
    cmb_metrics = estimate_cmb_chi2(prefix)
    
    if H0_eff and S8:
        delta_S8 = S8 - lcdm_s8
        cmb_rms = cmb_metrics["rms_tt"] if cmb_metrics else None
        
        print(f"{beta:6.2f} {H0_eff:10.4f} {delta_H0:+10.4f} {sigma8:10.4f} {S8:10.4f} {delta_S8:+10.4f} {cmb_rms:10.2f}%")
        
        results.append({
            "beta": beta,
            "H0_eff": H0_eff,
            "delta_H0": delta_H0,
            "sigma8": sigma8,
            "Omega_m": Omega_m,
            "S8": S8,
            "delta_S8": delta_S8,
            "cmb_rms_tt": cmb_rms,
            "cmb_chi2_approx": cmb_metrics["chi2_approx"] if cmb_metrics else None,
        })

print()

# --------------------------------------------------------------------------
# Identify optimal configuration
# --------------------------------------------------------------------------

if len(results) > 0:
    print(f"{'='*70}")
    print("OPTIMIZATION ASSESSMENT")
    print(f"{'='*70}\n")
    
    # Score each configuration
    for r in results:
        # Goal: Maximize |ΔH0|, moderate |ΔS8| (target -0.034), minimize CMB RMS
        
        # Normalize scores (0-1)
        h0_score = abs(r["delta_H0"]) / 5.0  # Target ~3-5 km/s/Mpc
        s8_score = 1.0 - abs(abs(r["delta_S8"]) - 0.034) / 0.034  # Target -0.034
        cmb_score = 1.0 - (r["cmb_rms_tt"] / 50.0) if r["cmb_rms_tt"] else 0.0  # Target <20%
        
        # Weighted combination
        total_score = 0.3 * h0_score + 0.4 * s8_score + 0.3 * cmb_score
        
        r["h0_score"] = h0_score
        r["s8_score"] = s8_score
        r["cmb_score"] = cmb_score
        r["total_score"] = total_score
    
    # Sort by total score
    results_sorted = sorted(results, key=lambda x: x["total_score"], reverse=True)
    
    print("Ranked configurations:")
    print(f"{'Rank':>4s} {'Beta':>6s} {'Total':>8s} {'H0':>6s} {'S8':>6s} {'CMB':>6s}")
    print("-" * 40)
    
    for i, r in enumerate(results_sorted, 1):
        print(f"{i:4d} {r['beta']:6.2f} {r['total_score']:8.3f} {r['h0_score']:6.3f} {r['s8_score']:6.3f} {r['cmb_score']:6.3f}")
    
    print()
    
    # Best configuration
    best = results_sorted[0]
    print(f"🏆 OPTIMAL: beta = {best['beta']:.2f}")
    print(f"   ΔH₀ = {best['delta_H0']:+.4f} km/s/Mpc")
    print(f"   ΔS₈ = {best['delta_S8']:+.4f} ({abs(best['delta_S8'])/0.068*100:.1f}% of tension)")
    print(f"   CMB RMS = {best['cmb_rms_tt']:.2f}%")
    print()
    
    # Save results
    output_file = RESULTS_DIR / "beta_ladder_analysis.json"
    with open(output_file, "w") as f:
        json.dump({
            "results": results,
            "optimal": best,
            "timestamp": str(np.datetime64('now')),
        }, f, indent=2)
    
    print(f"✓ Results saved to {output_file}")
    
else:
    print("⚠️  No successful runs to analyze")

print()
print(f"{'='*70}")
print("PHASE 1A COMPLETE")
print(f"{'='*70}\n")
print("Next steps:")
print("  1. Review optimal beta configuration")
print("  2. Proceed to Phase 1B: Tail activation")
print("  3. Proceed to Phase 1C: Lambda ladder (if needed)")
print()

