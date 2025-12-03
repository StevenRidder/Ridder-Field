#!/usr/bin/env python3
"""
scan_v3_EDE_24point.py - V3 EDE-only 24-point scan

Scans (z_c, sigma_lna) to map the EDE parameter space.
Tail is DISABLED (Lambda_tail=0) due to calibration issues.

Grid: 6 z_c × 4 sigma_lna = 24 points
"""

import os
import sys
import json
import subprocess
import numpy as np
from pathlib import Path
import time

# =============================================================================
# CONFIGURATION
# =============================================================================

REPO_ROOT = Path(__file__).parent
BUTTON_SCRIPT = REPO_ROOT / "run_unified_model_v3.py"
OUTPUT_DIR = REPO_ROOT / "scan_v3_EDE_24point"

# Scan grid: 6 z_c × 4 sigma_lna = 24 points
Z_C_VALUES = [2000, 2500, 3000, 3500, 4000, 4500]
SIGMA_LNA_VALUES = [0.2, 0.3, 0.4, 0.5]

# Fixed parameters
LAMBDA_TAIL_MEV = 0.0  # DISABLED due to late-time domination bug
F_AXION = 0.40  # Placeholder (not used in v3, but required by button API)

# Constraints
CONSTRAINTS = {
    "H0_min": 70.0,
    "H0_max": 74.0,
    "f_EDE_min": 0.05,
    "f_EDE_max": 0.18,
}

# =============================================================================
# SCAN EXECUTION
# =============================================================================

def run_v3_point(z_c, sigma_lna, output_json):
    """Run v3 button for one point"""
    cmd = [
        sys.executable,
        str(BUTTON_SCRIPT),
        "--Lambda_tail_meV", str(LAMBDA_TAIL_MEV),
        "--f_axion", str(F_AXION),
        "--z_c", str(z_c),
        "--sigma_lna", str(sigma_lna),
        "--mode", "quick",
        "--output_json", str(output_json)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            check=False
        )
        
        if result.returncode != 0:
            print(f"    ✗ Failed: {result.stderr[:200]}")
            return None
        
        with open(output_json, 'r') as f:
            data = json.load(f)
        
        return data
    
    except subprocess.TimeoutExpired:
        print(f"    ✗ Timeout")
        return None
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return None

def classify_point(obs, constraints):
    """Check if point meets constraints"""
    H0 = obs.get("H0_km_s_Mpc", 67.36)
    f_EDE = obs.get("f_EDE_peak", 0.0)
    
    H0_ok = constraints["H0_min"] <= H0 <= constraints["H0_max"]
    f_EDE_ok = constraints["f_EDE_min"] <= f_EDE <= constraints["f_EDE_max"]
    
    if H0_ok and f_EDE_ok:
        return "viable"
    elif H0_ok or f_EDE_ok:
        return "partial"
    else:
        return "ruled_out"

# =============================================================================
# MAIN SCAN
# =============================================================================

def main():
    print("=" * 70)
    print("V3 EDE-ONLY - 24-POINT SCAN")
    print("=" * 70)
    print()
    print(f"Grid: {len(Z_C_VALUES)} z_c × {len(SIGMA_LNA_VALUES)} sigma_lna")
    print(f"Total points: {len(Z_C_VALUES) * len(SIGMA_LNA_VALUES)}")
    print(f"Tail: DISABLED (Lambda_tail=0)")
    print()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    point_idx = 0
    for z_c in Z_C_VALUES:
        for sigma_lna in SIGMA_LNA_VALUES:
            point_idx += 1
            print(f"[{point_idx:2d}/24] z_c={z_c:.0f}, sigma_lna={sigma_lna:.1f}")
            
            output_json = OUTPUT_DIR / f"point_zc{z_c:.0f}_sig{sigma_lna*10:.0f}.json"
            t0 = time.time()
            data = run_v3_point(z_c, sigma_lna, output_json)
            dt = time.time() - t0
            
            if data is None:
                print(f"    ⏱  {dt:.1f}s")
                print()
                continue
            
            obs = data.get("observables", {})
            v3_params = data.get("v3_params", {})
            
            H0 = obs.get("H0_km_s_Mpc", 67.36)
            f_EDE = obs.get("f_EDE_peak", 0.0)
            z_peak = obs.get("z_peak", 0.0)
            Lambda_EDE = v3_params.get("Lambda_EDE_eV", 0.0)
            
            status = classify_point(obs, CONSTRAINTS)
            
            result = {
                "z_c": z_c,
                "sigma_lna": sigma_lna,
                "Lambda_EDE_eV": Lambda_EDE,
                "H0": H0,
                "f_EDE": f_EDE,
                "z_peak": z_peak,
                "status": status,
                "runtime_s": dt
            }
            results.append(result)
            
            status_symbol = {"viable": "✓", "partial": "~", "ruled_out": "✗"}[status]
            print(f"    {status_symbol} Lambda_EDE={Lambda_EDE:.3f} eV, H0={H0:.2f}, f_EDE={f_EDE:.3f}, z_peak={z_peak:.0f}")
            print(f"    ⏱  {dt:.1f}s")
            print()
    
    # Save results
    results_file = OUTPUT_DIR / "scan_24point_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print("=" * 70)
    print("SCAN COMPLETE")
    print("=" * 70)
    print()
    
    viable = [r for r in results if r["status"] == "viable"]
    partial = [r for r in results if r["status"] == "partial"]
    ruled_out = [r for r in results if r["status"] == "ruled_out"]
    
    print(f"Viable:    {len(viable):2d} / 24")
    print(f"Partial:   {len(partial):2d} / 24")
    print(f"Ruled out: {len(ruled_out):2d} / 24")
    print()
    
    if viable:
        print("VIABLE POINTS:")
        for r in viable:
            print(f"  z_c={r['z_c']:.0f}, sigma_lna={r['sigma_lna']:.1f}")
            print(f"    Lambda_EDE={r['Lambda_EDE_eV']:.3f} eV, H0={r['H0']:.2f}, f_EDE={r['f_EDE']:.3f}")
    else:
        print("⚠ No viable points found")
    
    print()
    print(f"Results saved to {results_file}")

if __name__ == "__main__":
    main()

