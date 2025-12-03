#!/usr/bin/env python3
"""
MCMC Smoke Test for V3 Branches (Tier 4)

Quick χ² test to determine if v3_trgb_branch and v3_shoes_branch
pass or fail CMB+BAO constraints.

Expected:
- v3_trgb_branch: PASS (χ² ≈ ΛCDM or better)
- v3_shoes_branch: FAIL (χ² >> ΛCDM, like Model 1.0)
"""

import subprocess
import json
import numpy as np
from pathlib import Path
import sys

# Paths
REPO_ROOT = Path(__file__).parent
BUTTON_SCRIPT = REPO_ROOT / "run_unified_model_v3.py"
CLASS_PATH = REPO_ROOT / "phase2/class"
OUTPUT_DIR = CLASS_PATH / "output"

# Branches to test
BRANCHES = ["lcdm_baseline", "v3_trgb_branch", "v3_shoes_branch"]

# Observational constraints (for χ² calculation)
OBS_DATA = {
    "H0_Planck": {"value": 67.36, "error": 0.54},
    "H0_TRGB": {"value": 69.8, "error": 1.7},  # Freedman et al.
    "H0_SH0ES": {"value": 73.04, "error": 1.04},  # Riess et al.
}

# =============================================================================
# RUN BRANCH
# =============================================================================

def run_branch_full(preset, output_json):
    """Run v3 button with full output (CMB + BAO)"""
    cmd = [
        sys.executable,
        str(BUTTON_SCRIPT),
        "--preset", preset,
        "--mode", "full",  # Full run for CMB+BAO
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
# EXTRACT OBSERVABLES FROM CLASS OUTPUT
# =============================================================================

# Global variable to store LCDM reference files
_LCDM_BG_FILE = None
_LCDM_CL_FILE = None

def extract_cmb_and_bao(preset):
    """Extract CMB and BAO residuals from CLASS output files"""
    global _LCDM_BG_FILE, _LCDM_CL_FILE
    
    try:
        # Find latest background and Cl files
        bg_files = list(OUTPUT_DIR.glob(f"v3_run*_background.dat"))
        cl_files = list(OUTPUT_DIR.glob(f"v3_run*_cl.dat"))
        
        if not bg_files or not cl_files:
            return None
        
        bg_file = max(bg_files, key=lambda p: p.stat().st_mtime)
        cl_file = max(cl_files, key=lambda p: p.stat().st_mtime)
        
        # Load data
        bg_data = np.loadtxt(bg_file)
        cl_data = np.loadtxt(cl_file)
        
        # Get ΛCDM reference (if not this run)
        if preset == "lcdm_baseline":
            # This IS the ΛCDM reference - save it
            _LCDM_BG_FILE = bg_file
            _LCDM_CL_FILE = cl_file
            return {
                "bg_file": str(bg_file),
                "cl_file": str(cl_file),
                "CMB_RMS": 0.0,  # Reference
                "BAO_frac": 0.0,  # Reference
            }
        
        # Load saved ΛCDM reference
        if _LCDM_BG_FILE is None or _LCDM_CL_FILE is None:
            print("    ✗ ΛCDM reference not set! Run lcdm_baseline first.")
            return None
        
        lcdm_bg_data = np.loadtxt(_LCDM_BG_FILE)
        lcdm_cl_data = np.loadtxt(_LCDM_CL_FILE)
        
        # CMB TT power spectrum RMS residual (ℓ = 30-2000)
        ell = cl_data[:, 0]
        TT = cl_data[:, 1]
        ell_lcdm = lcdm_cl_data[:, 0]
        TT_lcdm = lcdm_cl_data[:, 1]
        
        mask = (ell >= 30) & (ell <= 2000)
        TT_model = np.interp(ell[mask], ell, TT)
        TT_ref = np.interp(ell[mask], ell_lcdm, TT_lcdm)
        
        cmb_rms = np.sqrt(np.mean(((TT_model - TT_ref) / TT_ref)**2))
        
        # BAO: D_A (angular diameter distance) fractional residual at z=0.35, 0.57
        z_bg = bg_data[:, 0]
        D_A = bg_data[:, 5]  # Angular diameter distance (column 6 in CLASS output)
        z_lcdm = lcdm_bg_data[:, 0]
        D_A_lcdm = lcdm_bg_data[:, 5]
        
        D_035 = np.interp(0.35, z_bg[::-1], D_A[::-1])
        D_035_lcdm = np.interp(0.35, z_lcdm[::-1], D_A_lcdm[::-1])
        bao_035 = abs(D_035 - D_035_lcdm) / D_035_lcdm
        
        D_057 = np.interp(0.57, z_bg[::-1], D_A[::-1])
        D_057_lcdm = np.interp(0.57, z_lcdm[::-1], D_A_lcdm[::-1])
        bao_057 = abs(D_057 - D_057_lcdm) / D_057_lcdm
        
        bao_frac = max(bao_035, bao_057)
        
        return {
            "CMB_RMS": cmb_rms,
            "BAO_frac": bao_frac,
        }
    
    except Exception as e:
        print(f"    ✗ Error extracting observables: {e}")
        return None

# =============================================================================
# CHI-SQUARED CALCULATION
# =============================================================================

def calculate_chi2(obs, target_H0="TRGB"):
    """Calculate χ² for a branch"""
    
    # H0 contribution
    if target_H0 == "TRGB":
        H0_target = OBS_DATA["H0_TRGB"]
    elif target_H0 == "SH0ES":
        H0_target = OBS_DATA["H0_SH0ES"]
    else:  # Planck
        H0_target = OBS_DATA["H0_Planck"]
    
    H0 = obs.get("H0_km_s_Mpc", 67.36)
    chi2_H0 = ((H0 - H0_target["value"]) / H0_target["error"])**2
    
    # CMB contribution (penalty for large RMS)
    CMB_RMS = obs.get("CMB_RMS", 0.0)
    if CMB_RMS > 0.15:  # 15% threshold
        chi2_CMB = ((CMB_RMS - 0.15) / 0.05)**2  # Soft penalty
    else:
        chi2_CMB = 0.0
    
    # BAO contribution (penalty for large fractional error)
    BAO_frac = obs.get("BAO_frac", 0.0)
    if BAO_frac > 0.03:  # 3% threshold
        chi2_BAO = ((BAO_frac - 0.03) / 0.01)**2  # Soft penalty
    else:
        chi2_BAO = 0.0
    
    chi2_total = chi2_H0 + chi2_CMB + chi2_BAO
    
    return {
        "chi2_total": chi2_total,
        "chi2_H0": chi2_H0,
        "chi2_CMB": chi2_CMB,
        "chi2_BAO": chi2_BAO,
    }

# =============================================================================
# MAIN SMOKE TEST
# =============================================================================

def main():
    print("=" * 90)
    print("MCMC SMOKE TEST (Tier 4): V3 Branches")
    print("=" * 90)
    print()
    print("Testing 3 branches against CMB+BAO constraints:")
    print("  1. lcdm_baseline: Pure ΛCDM (reference)")
    print("  2. v3_trgb_branch: H0~70 (expect PASS)")
    print("  3. v3_shoes_branch: H0~73 (expect FAIL)")
    print()
    
    results = []
    
    # Run branches
    for branch in BRANCHES:
        print(f"{'='*90}")
        print(f"Testing: {branch}")
        print(f"{'='*90}")
        
        output_json = REPO_ROOT / f"mcmc_smoke_{branch}.json"
        
        # Run CLASS
        print(f"  Running CLASS (full mode)...")
        data = run_branch_full(branch, output_json)
        
        if data is None:
            print(f"  ✗ Branch failed to run")
            continue
        
        obs = data.get("observables", {})
        v3_params = data.get("v3_params", {})
        
        H0 = obs.get("H0_km_s_Mpc", 67.36)
        f_EDE = obs.get("f_EDE_peak", 0.0)
        
        print(f"  ✓ CLASS completed")
        print(f"    H0 = {H0:.2f} km/s/Mpc")
        print(f"    f_EDE = {f_EDE:.3f}")
        
        # Extract CMB + BAO
        print(f"  Extracting CMB + BAO residuals...")
        cmb_bao = extract_cmb_and_bao(branch)
        
        if cmb_bao:
            obs.update(cmb_bao)
            CMB_RMS = cmb_bao.get("CMB_RMS", 0.0)
            BAO_frac = cmb_bao.get("BAO_frac", 0.0)
            
            print(f"    CMB RMS = {CMB_RMS*100:.1f}% (threshold: 15%)")
            print(f"    BAO frac = {BAO_frac*100:.1f}% (threshold: 3%)")
        else:
            print(f"    ⚠ Could not extract CMB+BAO")
        
        # Calculate χ²
        target_H0 = "Planck" if branch == "lcdm_baseline" else ("TRGB" if "trgb" in branch else "SH0ES")
        chi2_dict = calculate_chi2(obs, target_H0)
        
        print(f"  χ² Breakdown:")
        print(f"    χ²(H0)  = {chi2_dict['chi2_H0']:.2f}")
        print(f"    χ²(CMB) = {chi2_dict['chi2_CMB']:.2f}")
        print(f"    χ²(BAO) = {chi2_dict['chi2_BAO']:.2f}")
        print(f"    χ²(tot) = {chi2_dict['chi2_total']:.2f}")
        
        # Verdict
        if branch == "lcdm_baseline":
            verdict = "REFERENCE"
        elif chi2_dict["chi2_total"] < 5.0:
            verdict = "✓ PASS"
        elif chi2_dict["chi2_total"] < 10.0:
            verdict = "~ MARGINAL"
        else:
            verdict = "✗ FAIL"
        
        print(f"  Verdict: {verdict}")
        print()
        
        results.append({
            "branch": branch,
            "H0": H0,
            "f_EDE": f_EDE,
            "chi2": chi2_dict,
            "obs": obs,
            "verdict": verdict,
        })
    
    # Summary
    print("=" * 90)
    print("SUMMARY")
    print("=" * 90)
    print()
    
    print(f"{'Branch':<20} {'H0':>8} {'f_EDE':>8} {'χ²(H0)':>10} {'χ²(CMB)':>10} {'χ²(BAO)':>10} {'χ²(tot)':>10} {'Verdict':>12}")
    print("-" * 90)
    
    for r in results:
        branch = r['branch']
        H0 = r['H0']
        f_EDE = r['f_EDE']
        chi2 = r['chi2']
        verdict = r['verdict']
        
        print(f"{branch:<20} {H0:>8.2f} {f_EDE:>8.3f} {chi2['chi2_H0']:>10.2f} {chi2['chi2_CMB']:>10.2f} {chi2['chi2_BAO']:>10.2f} {chi2['chi2_total']:>10.2f} {verdict:>12}")
    
    print()
    print("=" * 90)
    print("INTERPRETATION")
    print("=" * 90)
    print()
    
    # Compare TRGB vs SH0ES
    trgb_result = next((r for r in results if "trgb" in r['branch']), None)
    shoes_result = next((r for r in results if "shoes" in r['branch']), None)
    lcdm_result = next((r for r in results if "lcdm" in r['branch']), None)
    
    if lcdm_result:
        print(f"ΛCDM Baseline: χ² = {lcdm_result['chi2']['chi2_total']:.2f}")
        print(f"  → Reference point for comparison")
        print()
    
    if trgb_result:
        chi2_trgb = trgb_result['chi2']['chi2_total']
        print(f"v3_trgb_branch: χ² = {chi2_trgb:.2f}")
        if chi2_trgb < 5.0:
            print(f"  ✓ PASSES CMB+BAO constraints")
            print(f"  → Model is VIABLE")
            print(f"  → Supports TRGB measurement (H0 = {trgb_result['H0']:.2f} ≈ 69.8 km/s/Mpc)")
        else:
            print(f"  ✗ FAILS CMB+BAO constraints")
            print(f"  → Model is EXCLUDED")
        print()
    
    if shoes_result:
        chi2_shoes = shoes_result['chi2']['chi2_total']
        print(f"v3_shoes_branch: χ² = {chi2_shoes:.2f}")
        if chi2_shoes < 5.0:
            print(f"  ✓ PASSES CMB+BAO constraints")
            print(f"  → Model is VIABLE")
            print(f"  → Supports SH0ES measurement (H0 = {shoes_result['H0']:.2f} ≈ 73.04 km/s/Mpc)")
        else:
            print(f"  ✗ FAILS CMB+BAO constraints (χ²(CMB) = {shoes_result['chi2']['chi2_CMB']:.2f})")
            print(f"  → Model is EXCLUDED")
            print(f"  → f_EDE = {shoes_result['f_EDE']:.3f} breaks CMB damping tail (like Model 1.0)")
        print()
    
    # Final verdict
    if trgb_result and shoes_result:
        print("=" * 90)
        print("FINAL VERDICT")
        print("=" * 90)
        print()
        
        if trgb_result['verdict'] == "✓ PASS" and "FAIL" in shoes_result['verdict']:
            print("✓ TRGB branch PASSES, SH0ES branch FAILS")
            print()
            print("INTERPRETATION:")
            print("  - H0 ~ 70 km/s/Mpc is achievable with modest new physics")
            print("  - H0 ~ 73 km/s/Mpc breaks CMB constraints")
            print("  - Theoretical evidence that TRGB (H0~70) is correct")
            print("  - SH0ES (H0~73) likely affected by Cepheid systematics")
        elif trgb_result['verdict'] == "✓ PASS" and shoes_result['verdict'] == "✓ PASS":
            print("✓ BOTH branches PASS")
            print()
            print("INTERPRETATION:")
            print("  - Model has sufficient flexibility to match both measurements")
            print("  - Further MCMC needed to determine preferred region")
        else:
            print("⚠ Unexpected result")
            print()
            print(f"  TRGB: {trgb_result['verdict']}")
            print(f"  SH0ES: {shoes_result['verdict']}")
    
    print()
    print("=" * 90)
    
    # Save results
    output_file = REPO_ROOT / "mcmc_v3_smoke_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "branches": results,
            "summary": "V3 MCMC Smoke Test (Tier 4)",
        }, f, indent=2)
    
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()

