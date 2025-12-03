#!/usr/bin/env python3
"""
scan_v3_24point.py - 24-point v3 canonical model scan

Scans Lambda_tail and f_axion to map:
- H0, S8, f_EDE, z_peak
- CMB residuals (low-ℓ, acoustic, damping)
- BAO residuals
- w(z) at z=0, 0.5, 1.0, 2.0

Goal: Find viable region where all constraints are met.
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
OUTPUT_DIR = REPO_ROOT / "scan_v3_24point"
CLASS_PATH = REPO_ROOT / "phase2/class"

# Scan grid: 6 Lambda_tail × 4 f_axion = 24 points
LAMBDA_TAIL_VALUES = [12.0, 14.0, 16.0, 18.0, 20.0, 22.0]  # meV
F_AXION_VALUES = [0.25, 0.30, 0.35, 0.40]

# Constraints (from Model 1.0 lessons)
CONSTRAINTS = {
    "H0_min": 70.0,           # km/s/Mpc
    "H0_max": 74.0,
    "S8_min": 0.72,
    "S8_max": 0.80,
    "f_EDE_min": 0.05,
    "f_EDE_max": 0.18,        # Standard EDE upper bound
    "z_peak_min": 2000.0,
    "z_peak_max": 6000.0,
    "CMB_TT_RMS_max": 0.20,   # 20% RMS
    "BAO_frac_max": 0.03,     # 3% fractional error
    "w0_min": -1.1,
    "w0_max": -0.85,
}

# =============================================================================
# SCAN EXECUTION
# =============================================================================

def run_v3_point(Lambda_tail_meV, f_axion, output_json):
    """Run v3 button for one point"""
    cmd = [
        sys.executable,
        str(BUTTON_SCRIPT),
        "--Lambda_tail_meV", str(Lambda_tail_meV),
        "--f_axion", str(f_axion),
        "--mode", "full",
        "--output_json", str(output_json)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 min per point
            check=False
        )
        
        if result.returncode != 0:
            print(f"    ✗ CLASS failed: {result.stderr[:200]}")
            return None
        
        # Load JSON
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
    """
    Classify point as:
    - "viable": All constraints met
    - "tension_help": Helps H0/S8 but breaks something
    - "ruled_out": Fails basic observables
    """
    flags = {}
    
    # Extract observables
    H0 = obs.get("H0", 67.36)
    S8 = obs.get("S8", 0.83)
    f_EDE = obs.get("f_EDE_peak", 0.0)
    z_peak = obs.get("z_peak", 0.0)
    w0 = obs.get("w_z0", -1.0)
    
    # CMB RMS (if available)
    cmb_rms = obs.get("CMB_TT_RMS", 1.0)
    
    # BAO residual (if available)
    bao_frac = obs.get("BAO_frac_error", 1.0)
    
    # Check each constraint
    flags["H0_ok"] = constraints["H0_min"] <= H0 <= constraints["H0_max"]
    flags["S8_ok"] = constraints["S8_min"] <= S8 <= constraints["S8_max"]
    flags["f_EDE_ok"] = constraints["f_EDE_min"] <= f_EDE <= constraints["f_EDE_max"]
    flags["z_peak_ok"] = constraints["z_peak_min"] <= z_peak <= constraints["z_peak_max"]
    flags["CMB_ok"] = cmb_rms <= constraints["CMB_TT_RMS_max"]
    flags["BAO_ok"] = bao_frac <= constraints["BAO_frac_max"]
    flags["w0_ok"] = constraints["w0_min"] <= w0 <= constraints["w0_max"]
    
    # Classify
    if all(flags.values()):
        status = "viable"
    elif flags["H0_ok"] or flags["S8_ok"]:
        status = "tension_help"
    else:
        status = "ruled_out"
    
    return status, flags

# =============================================================================
# MAIN SCAN
# =============================================================================

def main():
    print("=" * 70)
    print("V3 CANONICAL MODEL - 24-POINT SCAN")
    print("=" * 70)
    print()
    print(f"Grid: {len(LAMBDA_TAIL_VALUES)} Lambda_tail × {len(F_AXION_VALUES)} f_axion")
    print(f"Total points: {len(LAMBDA_TAIL_VALUES) * len(F_AXION_VALUES)}")
    print()
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Results storage
    results = []
    
    # Scan grid
    point_idx = 0
    for Lambda_tail in LAMBDA_TAIL_VALUES:
        for f_axion in F_AXION_VALUES:
            point_idx += 1
            print(f"[{point_idx:2d}/24] Lambda_tail={Lambda_tail:.1f} meV, f_axion={f_axion:.2f}")
            
            # Run v3 button
            output_json = OUTPUT_DIR / f"point_L{Lambda_tail:.0f}_f{f_axion*100:.0f}.json"
            t0 = time.time()
            data = run_v3_point(Lambda_tail, f_axion, output_json)
            dt = time.time() - t0
            
            if data is None:
                print(f"    ⏱  {dt:.1f}s")
                print()
                continue
            
            # Extract key observables
            obs = data.get("observables", {})
            H0 = obs.get("H0", 67.36)
            S8 = obs.get("S8", 0.83)
            f_EDE = obs.get("f_EDE_peak", 0.0)
            z_peak = obs.get("z_peak", 0.0)
            
            # Classify
            status, flags = classify_point(obs, CONSTRAINTS)
            
            # Store result
            result = {
                "Lambda_tail_meV": Lambda_tail,
                "f_axion": f_axion,
                "H0": H0,
                "S8": S8,
                "f_EDE": f_EDE,
                "z_peak": z_peak,
                "status": status,
                "flags": flags,
                "runtime_s": dt
            }
            results.append(result)
            
            # Print summary
            status_symbol = {"viable": "✓", "tension_help": "~", "ruled_out": "✗"}[status]
            print(f"    {status_symbol} H0={H0:.2f}, S8={S8:.3f}, f_EDE={f_EDE:.3f}, z_peak={z_peak:.0f}")
            print(f"    ⏱  {dt:.1f}s")
            print()
    
    # Save full results
    results_file = OUTPUT_DIR / "scan_24point_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print("=" * 70)
    print("SCAN COMPLETE")
    print("=" * 70)
    print()
    
    # Summary statistics
    viable = [r for r in results if r["status"] == "viable"]
    tension_help = [r for r in results if r["status"] == "tension_help"]
    ruled_out = [r for r in results if r["status"] == "ruled_out"]
    
    print(f"Viable:       {len(viable):2d} / 24")
    print(f"Tension help: {len(tension_help):2d} / 24")
    print(f"Ruled out:    {len(ruled_out):2d} / 24")
    print()
    
    if viable:
        print("VIABLE POINTS:")
        for r in viable:
            print(f"  Lambda_tail={r['Lambda_tail_meV']:.1f} meV, f_axion={r['f_axion']:.2f}")
            print(f"    H0={r['H0']:.2f}, S8={r['S8']:.3f}, f_EDE={r['f_EDE']:.3f}")
    else:
        print("⚠ No viable points found in grid")
        print()
        
        if tension_help:
            print("Best tension-help points:")
            # Sort by H0 descending
            tension_help_sorted = sorted(tension_help, key=lambda x: x["H0"], reverse=True)
            for r in tension_help_sorted[:3]:
                print(f"  Lambda_tail={r['Lambda_tail_meV']:.1f} meV, f_axion={r['f_axion']:.2f}")
                print(f"    H0={r['H0']:.2f}, S8={r['S8']:.3f}, f_EDE={r['f_EDE']:.3f}")
                # Show which flags failed
                failed = [k for k, v in r["flags"].items() if not v]
                print(f"    Failed: {', '.join(failed)}")
    
    print()
    print(f"Results saved to {results_file}")

if __name__ == "__main__":
    main()

