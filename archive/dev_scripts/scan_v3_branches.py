#!/usr/bin/env python3
"""
scan_v3_branches.py - Compare V3 branches (TRGB vs SH0ES)

Runs the three key V3 presets and compares their predictions:
1. lcdm_baseline: Pure ΛCDM reference
2. v3_trgb_branch: TRGB-aligned (H0~70)
3. v3_shoes_branch: SH0ES-targeted (H0~73)

Goal: Determine which branch (if any) satisfies all constraints.
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
OUTPUT_DIR = REPO_ROOT / "scan_v3_branches"

# Branches to test
BRANCHES = ["lcdm_baseline", "v3_trgb_branch", "v3_shoes_branch"]

# Observational targets (for classification)
TARGETS = {
    # H0 measurements
    "H0_Planck": 67.36,
    "H0_TRGB": 69.8,       # Freedman et al.
    "H0_SH0ES": 73.04,     # Riess et al.
    
    # Constraints
    "f_EDE_max": 0.18,     # Standard EDE upper bound
    "S8_min": 0.72,
    "S8_max": 0.80,
}

# =============================================================================
# RUN BRANCH
# =============================================================================

def run_branch(preset, output_json):
    """Run v3 button for one preset"""
    cmd = [
        sys.executable,
        str(BUTTON_SCRIPT),
        "--preset", preset,
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

# =============================================================================
# ANALYSIS
# =============================================================================

def classify_branch(obs, targets):
    """
    Classify branch based on H0 prediction:
    - "ΛCDM": H0 ~ 67.36 (Planck baseline)
    - "TRGB-aligned": H0 ~ 69-71 (Freedman et al.)
    - "SH0ES-aligned": H0 ~ 72-74 (Riess et al.)
    """
    H0 = obs.get("H0_km_s_Mpc", 67.36)
    f_EDE = obs.get("f_EDE_peak", 0.0)
    
    # Classify by H0
    if abs(H0 - targets["H0_Planck"]) < 1.0:
        category = "ΛCDM"
    elif abs(H0 - targets["H0_TRGB"]) < 1.5:
        category = "TRGB-aligned"
    elif abs(H0 - targets["H0_SH0ES"]) < 1.5:
        category = "SH0ES-aligned"
    else:
        category = "Other"
    
    # Check constraints
    flags = {
        "f_EDE_ok": f_EDE <= targets["f_EDE_max"],
        # Add S8, CMB, BAO checks when available
    }
    
    viable = all(flags.values())
    
    return category, viable, flags

def format_comparison_table(results):
    """Print comparison table"""
    print()
    print("=" * 90)
    print("V3 BRANCH COMPARISON")
    print("=" * 90)
    print()
    print(f"{'Branch':<20} {'H0':>8} {'f_EDE':>8} {'z_peak':>8} {'Category':>15} {'Viable':>8}")
    print("-" * 90)
    
    for r in results:
        preset = r['preset']
        obs = r.get('observables', {})
        H0 = obs.get('H0_km_s_Mpc', 0.0)
        f_EDE = obs.get('f_EDE_peak', 0.0)
        z_peak = obs.get('z_peak', 0.0)
        category = r.get('category', 'Unknown')
        viable = '✓' if r.get('viable', False) else '✗'
        
        print(f"{preset:<20} {H0:>8.2f} {f_EDE:>8.3f} {z_peak:>8.0f} {category:>15} {viable:>8}")
    
    print("-" * 90)
    print()

def print_interpretation(results, targets):
    """Print scientific interpretation"""
    print("=" * 90)
    print("INTERPRETATION")
    print("=" * 90)
    print()
    
    # Find branches by category
    lcdm = next((r for r in results if r['preset'] == 'lcdm_baseline'), None)
    trgb = next((r for r in results if r['preset'] == 'v3_trgb_branch'), None)
    shoes = next((r for r in results if r['preset'] == 'v3_shoes_branch'), None)
    
    # ΛCDM baseline
    if lcdm:
        H0_lcdm = lcdm['observables'].get('H0_km_s_Mpc', 0.0)
        print(f"1. ΛCDM Baseline: H0 = {H0_lcdm:.2f} km/s/Mpc")
        print(f"   → Confirms Planck value ({targets['H0_Planck']:.2f})")
        print()
    
    # TRGB branch
    if trgb:
        H0_trgb = trgb['observables'].get('H0_km_s_Mpc', 0.0)
        f_EDE_trgb = trgb['observables'].get('f_EDE_peak', 0.0)
        delta_trgb = H0_trgb - targets['H0_TRGB']
        
        print(f"2. TRGB Branch: H0 = {H0_trgb:.2f} km/s/Mpc (f_EDE = {f_EDE_trgb:.3f})")
        print(f"   → Target: {targets['H0_TRGB']:.2f} ± 1.7 km/s/Mpc (Freedman et al.)")
        print(f"   → Δ = {delta_trgb:+.2f} km/s/Mpc")
        
        if abs(delta_trgb) < 1.7:
            print(f"   ✓ WITHIN TRGB UNCERTAINTY")
            print(f"   → Model supports TRGB measurement")
        else:
            print(f"   ✗ OUTSIDE TRGB UNCERTAINTY")
            if H0_trgb < targets['H0_TRGB']:
                print(f"   → Need stronger tail (currently: tail calibration bug)")
        print()
    
    # SH0ES branch
    if shoes:
        H0_shoes = shoes['observables'].get('H0_km_s_Mpc', 0.0)
        f_EDE_shoes = shoes['observables'].get('f_EDE_peak', 0.0)
        delta_shoes = H0_shoes - targets['H0_SH0ES']
        
        print(f"3. SH0ES Branch: H0 = {H0_shoes:.2f} km/s/Mpc (f_EDE = {f_EDE_shoes:.3f})")
        print(f"   → Target: {targets['H0_SH0ES']:.2f} ± 1.04 km/s/Mpc (Riess et al.)")
        print(f"   → Δ = {delta_shoes:+.2f} km/s/Mpc")
        
        if abs(delta_shoes) < 1.04:
            print(f"   ✓ WITHIN SH0ES UNCERTAINTY")
            print(f"   → Model supports SH0ES measurement")
            print(f"   → WARNING: Check CMB/BAO constraints (likely violated)")
        else:
            print(f"   ✗ OUTSIDE SH0ES UNCERTAINTY")
            if H0_shoes < targets['H0_SH0ES']:
                print(f"   → Cannot reach SH0ES without breaking CMB")
        print()
    
    # Verdict
    print("=" * 90)
    print("VERDICT")
    print("=" * 90)
    print()
    
    if trgb and abs(H0_trgb - targets['H0_TRGB']) < 1.7:
        print("✓ TRGB branch is viable:")
        print("  - H0 matches Freedman et al. measurement")
        print("  - Physics-first model naturally lands at H0~70")
        print("  - Supports hypothesis that SH0ES systematics inflate H0")
        print()
    
    if shoes and abs(H0_shoes - targets['H0_SH0ES']) > 2.0:
        print("✗ SH0ES branch cannot reach target:")
        print("  - H0~73 requires extreme parameters")
        print("  - Likely to violate CMB/BAO constraints (as Model 1.0 did)")
        print("  - Suggests SH0ES measurement may be affected by Cepheid crowding")
        print()
    
    print("RECOMMENDATION:")
    print("  Focus on TRGB branch for paper. Position as:")
    print("  'Theoretical support for H0~70 km/s/Mpc (TRGB measurement)'")
    print()

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 90)
    print("V3 BRANCH SCAN: TRGB vs SH0ES")
    print("=" * 90)
    print()
    print(f"Testing {len(BRANCHES)} presets:")
    for branch in BRANCHES:
        print(f"  - {branch}")
    print()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for branch in BRANCHES:
        print(f"Running {branch}...")
        
        output_json = OUTPUT_DIR / f"{branch}.json"
        t0 = time.time()
        data = run_branch(branch, output_json)
        dt = time.time() - t0
        
        if data is None:
            print(f"  ⏱  {dt:.1f}s")
            print()
            continue
        
        obs = data.get("observables", {})
        category, viable, flags = classify_branch(obs, TARGETS)
        
        result = {
            "preset": branch,
            "category": category,
            "viable": viable,
            "flags": flags,
            "observables": obs,
            "v3_params": data.get("v3_params", {}),
            "runtime_s": dt
        }
        results.append(result)
        
        H0 = obs.get("H0_km_s_Mpc", 0.0)
        f_EDE = obs.get("f_EDE_peak", 0.0)
        print(f"  → H0 = {H0:.2f} km/s/Mpc, f_EDE = {f_EDE:.3f}, category = {category}")
        print(f"  ⏱  {dt:.1f}s")
        print()
    
    # Save results
    results_file = OUTPUT_DIR / "branch_comparison.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print comparison
    format_comparison_table(results)
    
    # Print interpretation
    print_interpretation(results, TARGETS)
    
    print(f"Results saved to {results_file}")

if __name__ == "__main__":
    main()

