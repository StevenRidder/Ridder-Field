#!/usr/bin/env python3
"""
DISTANCE PRIORS SANITY CHECK
============================
Compare Track 2 Ridder tail vs ΛCDM for key distance quantities.

Uses published distance prior values as rough σ_ref for sanity check.
NOT a full likelihood - just checking we're not off by 10-20%.

Reference values from:
- Planck 2018 (arXiv:1807.06209)
- BAO compilation (BOSS, eBOSS)
"""

import numpy as np
from pathlib import Path

# Reference values and errors (approximate, for sanity check only)
# From Planck 2018 + BAO compilations
REFS = {
    'r_s_drag': {'val': 147.09, 'err': 0.26, 'unit': 'Mpc'},  # Sound horizon at drag
    'D_A_star': {'val': 12.89, 'err': 0.03, 'unit': 'Gpc'},   # Angular diameter distance at z*
    'H_0.35': {'val': 81.2, 'err': 2.4, 'unit': 'km/s/Mpc'},  # H(z=0.35) * r_d/r_d,fid
    'H_0.57': {'val': 96.8, 'err': 3.4, 'unit': 'km/s/Mpc'},  # H(z=0.57)
    'D_V_0.35': {'val': 1356, 'err': 25, 'unit': 'Mpc'},      # D_V(z=0.35)
    'D_V_0.57': {'val': 2028, 'err': 20, 'unit': 'Mpc'},      # D_V(z=0.57)
}

def load_background(filepath):
    """Load CLASS background file."""
    return np.loadtxt(filepath)

def find_z_index(bg, z_target, tol=0.1):
    """Find index closest to target redshift."""
    z = bg[:, 0]
    # Find closest
    idx = np.argmin(np.abs(z - z_target))
    if np.abs(z[idx] - z_target) > tol * z_target:
        print(f"Warning: Closest z to {z_target} is {z[idx]}")
    return idx

def compute_quantities(bg_file):
    """Extract distance quantities from background file."""
    bg = load_background(bg_file)
    
    # Column indices (0-indexed)
    # 0=z, 3=H, 5=D_A (angular diameter), 7=r_s (sound horizon)
    z = bg[:, 0]
    H = bg[:, 3] * 299792.458  # Convert 1/Mpc to km/s/Mpc
    D_A = bg[:, 5]  # Mpc
    r_s = bg[:, 7]  # Comoving sound horizon in Mpc
    
    results = {}
    
    # Sound horizon at drag (z ~ 1060)
    # Look for z closest to 1060
    z_drag = 1060
    idx_drag = find_z_index(bg, z_drag, tol=0.05)
    results['r_s_drag'] = r_s[idx_drag]
    
    # Angular diameter distance at recombination (z* ~ 1090)
    z_star = 1090
    idx_star = find_z_index(bg, z_star, tol=0.05)
    results['D_A_star'] = D_A[idx_star] / 1000  # Convert to Gpc
    
    # H(z) at BAO redshifts
    for z_bao in [0.35, 0.57, 0.80]:
        idx = find_z_index(bg, z_bao, tol=0.1)
        key = f'H_{z_bao:.2f}'
        results[key] = H[idx]
    
    # D_V(z) = [z * D_A^2 * c/H]^(1/3) - volume averaged distance
    c = 299792.458  # km/s
    for z_bao in [0.35, 0.57, 0.80]:
        idx = find_z_index(bg, z_bao, tol=0.1)
        D_A_z = D_A[idx]
        H_z = H[idx]
        D_V = (z_bao * D_A_z**2 * c / H_z)**(1/3)
        key = f'D_V_{z_bao:.2f}'
        results[key] = D_V
    
    # H0 (z=0, last row)
    results['H0'] = H[-1]
    
    return results

def print_comparison(lcdm_results, ridder_results):
    """Print comparison table."""
    print("=" * 80)
    print("DISTANCE PRIORS SANITY CHECK: Track 2 vs ΛCDM")
    print("=" * 80)
    print(f"{'Quantity':<15} {'ΛCDM':>12} {'Ridder':>12} {'Δ':>10} {'Δ/σ':>8} {'Status':<8}")
    print("-" * 80)
    
    all_ok = True
    
    for key in ['r_s_drag', 'D_A_star', 'H0']:
        lcdm_val = lcdm_results.get(key, np.nan)
        ridder_val = ridder_results.get(key, np.nan)
        delta = ridder_val - lcdm_val
        
        ref = REFS.get(key, {'err': abs(lcdm_val) * 0.05})  # 5% default
        sigma = ref.get('err', abs(lcdm_val) * 0.05)
        delta_sigma = delta / sigma if sigma > 0 else np.nan
        
        status = "✓" if abs(delta_sigma) < 3 else "⚠️"
        if abs(delta_sigma) > 5:
            status = "❌"
            all_ok = False
        
        print(f"{key:<15} {lcdm_val:>12.2f} {ridder_val:>12.2f} {delta:>+10.2f} {delta_sigma:>+8.1f}σ {status:<8}")
    
    print("-" * 80)
    print("BAO Distance Measures:")
    print("-" * 80)
    
    for z_bao in [0.35, 0.57]:
        h_key = f'H_{z_bao:.2f}'
        dv_key = f'D_V_{z_bao:.2f}'
        
        for key in [h_key, dv_key]:
            lcdm_val = lcdm_results.get(key, np.nan)
            ridder_val = ridder_results.get(key, np.nan)
            delta = ridder_val - lcdm_val
            pct = 100 * delta / lcdm_val if lcdm_val != 0 else np.nan
            
            status = "✓" if abs(pct) < 5 else "⚠️"
            if abs(pct) > 10:
                status = "❌"
                all_ok = False
            
            print(f"{key:<15} {lcdm_val:>12.2f} {ridder_val:>12.2f} {delta:>+10.2f} ({pct:>+5.1f}%) {status:<8}")
    
    print("=" * 80)
    
    if all_ok:
        print("✅ ALL DISTANCE PRIORS WITHIN ACCEPTABLE RANGE")
    else:
        print("⚠️  SOME QUANTITIES SHOW LARGE DEVIATIONS - INVESTIGATE")
    
    print("=" * 80)
    
    return all_ok

def main():
    output_dir = Path("output")
    
    # Check files exist
    lcdm_file = output_dir / "lcdm_baseline00_background.dat"
    ridder_file = output_dir / "track2_minimal00_background.dat"
    
    if not lcdm_file.exists():
        print(f"ERROR: {lcdm_file} not found. Run run_track2_benchmark.py first.")
        return 1
    
    if not ridder_file.exists():
        print(f"ERROR: {ridder_file} not found. Run run_track2_benchmark.py first.")
        return 1
    
    print("Loading ΛCDM background...")
    lcdm_results = compute_quantities(lcdm_file)
    
    print("Loading Ridder tail background...")
    ridder_results = compute_quantities(ridder_file)
    
    print()
    ok = print_comparison(lcdm_results, ridder_results)
    
    return 0 if ok else 1

if __name__ == "__main__":
    exit(main())

