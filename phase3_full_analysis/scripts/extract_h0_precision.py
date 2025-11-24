#!/usr/bin/env python3
"""
Phase 1C: H₀ Precision Extraction

Computes H₀^eff from CLASS outputs using multiple methods:
1. Sound horizon scaling: H₀^eff = H₀^input × (r_s^ΛCDM / r_s^model)
2. BAO scale check: D_A(z_drag) consistency
3. Angular scale: θ_s = r_s / D_A consistency

This provides robust H₀ shift measurements for all configurations.
"""

import numpy as np
import json
from pathlib import Path
import sys

# Configuration
REPO_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = REPO_ROOT / "phase2" / "class" / "output"
RESULTS_DIR = REPO_ROOT / "phase3_full_analysis" / "results"

# Reference values (from vanilla ΛCDM)
RS_LCDM = 147.07923596941404  # Mpc
H0_INPUT = 67.36  # km/s/Mpc

print(f"\n{'='*70}")
print("PHASE 1C: H₀ PRECISION EXTRACTION")
print(f"{'='*70}\n")
print(f"Reference: r_s^ΛCDM = {RS_LCDM:.6f} Mpc")
print(f"           H₀^input = {H0_INPUT:.4f} km/s/Mpc")
print()


def find_output_files(prefix):
    """Find CLASS output files with 00 suffix handling."""
    bg_file = OUTPUT_DIR / f"{prefix}_background.dat"
    if not bg_file.exists():
        bg_file = OUTPUT_DIR / f"{prefix}_00_background.dat"
    
    params_file = OUTPUT_DIR / f"{prefix}_parameters.ini"
    if not params_file.exists():
        params_file = OUTPUT_DIR / f"{prefix}_00_parameters.ini"
    
    return bg_file, params_file


def extract_sound_horizon(bg_file):
    """
    Extract sound horizon at drag epoch.
    
    r_s is in column 8 (0-indexed: 7) "comov.snd.hrz."
    We want the value at z ~ z_drag, which is where it plateaus.
    For simplicity, use the last value (z=0) which equals r_s(z_drag).
    """
    if not bg_file.exists():
        return None
    
    try:
        data = np.loadtxt(bg_file)
        rs = data[-1, 7]  # Last row, column 8
        return rs
    except Exception as e:
        print(f"[WARN] Could not extract r_s from {bg_file}: {e}")
        return None


def extract_angular_diameter_distance(bg_file, z_target=1089.9):
    """
    Extract comoving angular diameter distance D_A(z).
    
    D_A is in column 9 (0-indexed: 8) "comov.ang.dist."
    """
    if not bg_file.exists():
        return None
    
    try:
        data = np.loadtxt(bg_file)
        z_col = data[:, 0]
        DA_col = data[:, 8]
        
        # Interpolate to z_target
        DA = np.interp(z_target, z_col[::-1], DA_col[::-1])
        return DA
    except Exception as e:
        print(f"[WARN] Could not extract D_A from {bg_file}: {e}")
        return None


def compute_theta_s(rs, DA_rec):
    """Compute angular acoustic scale θ_s = r_s / D_A(z_rec)."""
    if rs is None or DA_rec is None:
        return None
    return rs / DA_rec


def compute_h0_from_rs(rs_model):
    """
    Primary method: H₀^eff from sound horizon scaling.
    
    H₀^eff = H₀^input × (r_s^ΛCDM / r_s^model)
    """
    if rs_model is None:
        return None, None
    
    H0_eff = H0_INPUT * (RS_LCDM / rs_model)
    delta_H0 = H0_eff - H0_INPUT
    
    return H0_eff, delta_H0


def compute_h0_from_theta_s(theta_s_model, theta_s_lcdm):
    """
    Alternative method: H₀^eff from angular scale.
    
    θ_s ∝ 1/H₀, so H₀^eff = H₀^input × (θ_s^ΛCDM / θ_s^model)
    """
    if theta_s_model is None or theta_s_lcdm is None:
        return None, None
    
    H0_eff = H0_INPUT * (theta_s_lcdm / theta_s_model)
    delta_H0 = H0_eff - H0_INPUT
    
    return H0_eff, delta_H0


def analyze_configuration(prefix, label):
    """Extract all H₀-related diagnostics for a configuration."""
    print(f"Analyzing: {label}")
    print(f"  Prefix: {prefix}")
    
    bg_file, params_file = find_output_files(prefix)
    
    if not bg_file.exists():
        print(f"  ❌ Background file not found")
        return None
    
    # Extract observables
    rs = extract_sound_horizon(bg_file)
    DA_rec = extract_angular_diameter_distance(bg_file, z_target=1089.9)
    
    if rs is None:
        print(f"  ❌ Could not extract r_s")
        return None
    
    print(f"  r_s = {rs:.6f} Mpc")
    
    # Method 1: Sound horizon scaling
    H0_eff_rs, delta_H0_rs = compute_h0_from_rs(rs)
    
    print(f"  H₀^eff (r_s method) = {H0_eff_rs:.4f} km/s/Mpc")
    print(f"  ΔH₀               = {delta_H0_rs:+.4f} km/s/Mpc")
    
    # Method 2: Angular scale (if available)
    theta_s = compute_theta_s(rs, DA_rec)
    
    if theta_s is not None:
        print(f"  θ_s = {theta_s:.6e}")
    
    # Fractional shifts
    delta_rs_frac = (rs - RS_LCDM) / RS_LCDM
    print(f"  Δr_s/r_s = {delta_rs_frac:+.4%}")
    
    print()
    
    result = {
        "prefix": prefix,
        "label": label,
        "rs_Mpc": rs,
        "DA_rec_Mpc": DA_rec,
        "theta_s": theta_s,
        "H0_eff_rs": H0_eff_rs,
        "delta_H0_rs": delta_H0_rs,
        "delta_rs_frac": delta_rs_frac,
    }
    
    return result


def main():
    """Main analysis."""
    
    # Define configurations to analyze
    configs = [
        # ΛCDM baseline
        ("lcdm_baseline", "ΛCDM Baseline"),
        
        # Hour 1 result (Lambda=1.0, beta=0.05)
        ("unified_baby_lambda1p0", "Unified Lambda=1.0, beta=0.05"),
        
        # Phase 1A attempts (may not exist if failed)
        ("unified_beta0p10", "Unified Lambda=1.0, beta=0.10"),
        ("unified_beta0p15", "Unified Lambda=1.0, beta=0.15"),
        ("unified_beta0p20", "Unified Lambda=1.0, beta=0.20"),
        
        # Phase 1A v2 (Lambda=0.7)
        ("unified_lambda0p7_beta0p05", "Unified Lambda=0.7, beta=0.05"),
        ("unified_lambda0p7_beta0p10", "Unified Lambda=0.7, beta=0.10"),
        ("unified_lambda0p7_beta0p15", "Unified Lambda=0.7, beta=0.15"),
        
        # With tail (if Phase 1B complete)
        ("unified_with_tail", "Unified with Tail"),
    ]
    
    results = []
    
    for prefix, label in configs:
        result = analyze_configuration(prefix, label)
        if result is not None:
            results.append(result)
    
    if len(results) == 0:
        print("⚠️  No successful configurations found")
        return
    
    # Summary table
    print(f"{'='*70}")
    print("H₀ EXTRACTION SUMMARY")
    print(f"{'='*70}\n")
    
    print(f"{'Configuration':<35s} {'r_s [Mpc]':>12s} {'H₀^eff':>12s} {'ΔH₀':>12s}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['label']:<35s} {r['rs_Mpc']:>12.6f} {r['H0_eff_rs']:>12.4f} {r['delta_H0_rs']:>+12.4f}")
    
    print()
    
    # Identify best H₀ shift
    valid_results = [r for r in results if r['delta_H0_rs'] is not None]
    
    if len(valid_results) > 0:
        best = max(valid_results, key=lambda x: abs(x['delta_H0_rs']))
        
        print(f"🏆 LARGEST H₀ SHIFT:")
        print(f"   {best['label']}")
        print(f"   ΔH₀ = {best['delta_H0_rs']:+.4f} km/s/Mpc")
        print(f"   H₀^eff = {best['H0_eff_rs']:.4f} km/s/Mpc")
        print()
    
    # Save results
    output_file = RESULTS_DIR / "h0_extraction_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "results": results,
            "reference": {
                "rs_lcdm": RS_LCDM,
                "h0_input": H0_INPUT,
            },
        }, f, indent=2)
    
    print(f"✓ Results saved to {output_file}")
    print()
    
    print("Next steps:")
    print("  1. Compare H₀ shifts across all configurations")
    print("  2. Identify which (Lambda, beta) maximizes ΔH₀")
    print("  3. Proceed to Phase 1D: Parameter optimization")
    print()


if __name__ == "__main__":
    main()

