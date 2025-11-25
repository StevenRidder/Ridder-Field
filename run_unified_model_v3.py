#!/usr/bin/env python3
"""
run_unified_model_v3.py - V3 Canonical Unified Model Button

Usage:
    python3 run_unified_model_v3.py --Lambda_tail_meV 16.0 --f_axion 0.40 --mode full
    python3 run_unified_model_v3.py --preset unified_compromise --mode quick
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
import shutil
import numpy as np
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

CLASS_PATH = Path(__file__).parent / "phase2/class"
CLASS_BINARY = CLASS_PATH / "class"
OUTPUT_DIR = CLASS_PATH / "output"
TEMPLATE_INI = CLASS_PATH / "explanatory.ini"

# V3 Canonical defaults
V3_DEFAULTS = {
    "f_eV": 1.0e26,
    "z_c": 3000.0,  # EDE peak redshift
    "sigma_lna": 0.3,  # Temporal width in log(a)
    "theta_E_center": 2.4,
    "sigma_E": 0.4,
    "n_EDE": 2.0,
    "theta_T_center": 0.0,
    "alpha_tail": 1.0,
    "n_tail": 1.0,
    "Lambda_floor_eV": 0.0,
}

# Presets
PRESETS = {
    # === BASELINE ===
    "lcdm_baseline": {
        "Lambda_tail_meV": 0.0, 
        "f_axion": 0.0,
        "description": "Pure ΛCDM (no EDE, no tail)"
    },
    
    # === TRGB BRANCH (H0 ~ 69-70 km/s/Mpc) ===
    "v3_trgb_branch": {
        "Lambda_tail_meV": 1.2,  # Calibrated: H0 = 69.33 (tail-only)
        "f_axion": 0.25,         # Moderate EDE (f_EDE ~ 0.10)
        "description": "TRGB-aligned: H0~70 (Freedman et al. 69.8±1.7)"
    },
    
    # === SH0ES BRANCH (H0 ~ 72-73 km/s/Mpc) ===
    "v3_shoes_branch": {
        "Lambda_tail_meV": 1.6,  # Calibrated: H0 = 73.19 (tail-only)
        "f_axion": 0.40,         # Strong EDE (f_EDE ~ 0.17)
        "description": "SH0ES-targeted: H0~73 (Riess et al. 73.04±1.04)"
    },
    
    # === LEGACY v2-like presets (kept for comparison) ===
    "unified_compromise": {"Lambda_tail_meV": 16.0, "f_axion": 0.40},
    "unified_hero": {"Lambda_tail_meV": 20.0, "f_axion": 0.45},
}

# =============================================================================
# MAPPING: Button inputs → v3 parameters
# =============================================================================

def map_button_to_v3(Lambda_tail_meV, f_axion):
    """
    Map button inputs (Lambda_tail_meV, f_axion) to v3 parameter dict.
    
    Returns:
        dict: v3 parameters ready for INI generation
    """
    params = V3_DEFAULTS.copy()
    
    # Tail side: direct mapping
    params["Lambda_tail_eV"] = Lambda_tail_meV * 1e-3  # meV → eV
    
    # EDE side: f_axion → f_EDE_target via linear mapping
    # f_axion ∈ [0.25, 0.45] → f_EDE_target ∈ [0.08, 0.20]
    # Center: f_axion=0.35 → f_EDE_target=0.14
    f_EDE_target = 0.14 + 0.6 * (f_axion - 0.35)
    f_EDE_target = max(0.05, min(0.20, f_EDE_target))  # clamp
    
    params["f_EDE_target"] = f_EDE_target
    
    # Lambda_EDE will be solved by shooting routine (see below)
    # For now, use a reasonable guess
    params["Lambda_EDE_eV"] = 1e-2  # Will be calibrated
    
    # Component toggles
    params["use_EDE"] = 1 if f_axion > 0.0 else 0
    params["use_tail"] = 1 if Lambda_tail_meV > 0.0 else 0
    params["use_floor"] = 0  # Floor is part of tail in v3
    
    return params

# =============================================================================
# SHOOTING: Solve Lambda_EDE for target f_EDE
# =============================================================================

def run_class_background_only(ini_path):
    """Run CLASS with background only, return background.dat path"""
    try:
        result = subprocess.run(
            [str(CLASS_BINARY), str(ini_path)],
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
            cwd=CLASS_PATH  # Run from CLASS directory so relative paths work
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"CLASS failed: {e.stderr[:200]}", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("CLASS timeout", file=sys.stderr)
        return False

def extract_f_EDE_peak(background_file):
    """Extract peak f_EDE from background file"""
    try:
        if not Path(background_file).exists():
            print(f"Background file not found: {background_file}", file=sys.stderr)
            return 0.0, 0.0
            
        data = np.loadtxt(background_file)
        z = data[:, 0]
        rho_ridder = data[:, 14]
        rho_tot = data[:, 19]
        
        # Compute f_ridder = rho_ridder / rho_tot
        f_ridder = rho_ridder / rho_tot
        
        # Find peak in z range [1000, 10000]
        mask = (z >= 1000) & (z <= 10000)
        if not np.any(mask):
            print(f"No points in z range [1000, 10000]", file=sys.stderr)
            return 0.0, 0.0
        
        idx_max = np.argmax(f_ridder[mask])
        z_peak = z[mask][idx_max]
        f_peak = f_ridder[mask][idx_max]
        
        return f_peak, z_peak
    except Exception as e:
        print(f"Error extracting f_EDE from {background_file}: {e}", file=sys.stderr)
        return 0.0, 0.0

def bool_to_yesno(val):
    """Convert Python bool or int to CLASS yes/no"""
    if isinstance(val, (int, float)):
        return "yes" if val != 0 else "no"
    return "yes" if val else "no"

def write_ini_for_shooting(Lambda_EDE_eV, v3_params, mode="background_only"):
    """Generate temporary INI for shooting iteration"""
    ini_content = f"""
# V3 shooting iteration INI
output = 
write background = yes

# Standard cosmology
h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544

# Gauge (required for Ridder field)
gauge = newtonian

# Ridder v3 unified field
use_ridder = yes
ridder_model_type = v3_canon

# Field normalization
ridder_f_eV = {v3_params['f_eV']:.6e}

# EDE bump (NOTE: C code calls this "shelf")
ridder_use_shelf = {bool_to_yesno(v3_params['use_EDE'])}
ridder_Lambda_EDE_eV = {Lambda_EDE_eV:.6e}
ridder_a_c = {1.0 / (1.0 + v3_params['z_c']):.6e}
ridder_sigma_lna = {v3_params['sigma_lna']:.6f}
ridder_theta_E_center = {v3_params['theta_E_center']}
ridder_sigma_E = {v3_params['sigma_E']}
ridder_n_EDE = {v3_params['n_EDE']}

# Tail
ridder_use_tail = {bool_to_yesno(v3_params['use_tail'])}
ridder_Lambda_tail_eV = {v3_params['Lambda_tail_eV']:.6e}
ridder_alpha_tail = {v3_params['alpha_tail']}
ridder_theta_T_center = {v3_params['theta_T_center']}
ridder_n_tail = {v3_params['n_tail']}

# Floor (v3: Lambda_floor absorbed into tail, no separate toggle)
ridder_Lambda_floor_eV = {v3_params['Lambda_floor_eV']:.6e}

# Initial conditions (Hubble-frozen)
theta_i_ridder = {v3_params['theta_E_center']}
ridder_c_slow = 0.0

# Output (relative path from CLASS working directory)
root = output/v3_shoot_test
"""
    
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False)
    tmp.write(ini_content)
    tmp.close()
    return tmp.name

def solve_Lambda_EDE_for_target(f_target, v3_params, max_iter=15, tol=0.005):
    """
    Bisection to find Lambda_EDE that yields f_EDE_peak ≈ f_target
    
    Returns:
        (Lambda_EDE_eV, f_achieved, z_peak)
    """
    print(f"Shooting for f_EDE = {f_target:.3f}...")
    
    # V3 with time window + field bump is VERY efficient
    # Lambda ~ 0.01-0.1 eV gives f_EDE ~ 0.01-0.20
    Lambda_min = 0.001  # eV
    Lambda_max = 0.5    # eV
    
    for iteration in range(max_iter):
        Lambda_mid = 0.5 * (Lambda_min + Lambda_max)
        
        # Generate INI
        ini_path = write_ini_for_shooting(Lambda_mid, v3_params)
        
        # Run CLASS
        success = run_class_background_only(ini_path)
        
        if not success:
            print(f"  [iter {iteration}] Lambda={Lambda_mid:.3e} - CLASS failed", file=sys.stderr)
            os.unlink(ini_path)
            continue
        
        # Extract f_EDE (find latest v3_shoot_test file)
        bg_files = list(OUTPUT_DIR.glob("v3_shoot_test*_background.dat"))
        if not bg_files:
            print(f"  [iter {iteration}] No background file found!", file=sys.stderr)
            os.unlink(ini_path)
            continue
        bg_file = max(bg_files, key=lambda p: p.stat().st_mtime)  # Latest file
        f_mid, z_peak = extract_f_EDE_peak(bg_file)
        
        os.unlink(ini_path)
        
        print(f"  [iter {iteration}] Lambda={Lambda_mid:.3e} → f_EDE={f_mid:.4f} (target={f_target:.4f})")
        
        # Check convergence
        if abs(f_mid - f_target) < tol:
            print(f"✓ Converged: Lambda_EDE = {Lambda_mid:.3e} eV")
            return Lambda_mid, f_mid, z_peak
        
        # Bisect
        if f_mid > f_target:
            Lambda_max = Lambda_mid
        else:
            Lambda_min = Lambda_mid
    
    # Max iterations reached
    Lambda_final = 0.5 * (Lambda_min + Lambda_max)
    print(f"⚠ Max iterations reached. Using Lambda_EDE = {Lambda_final:.3e} eV")
    return Lambda_final, f_mid, z_peak

# =============================================================================
# FULL RUN: Generate INI, run CLASS, extract observables
# =============================================================================

def write_full_ini(v3_params, mode="full"):
    """Write full INI for production run"""
    
    outputs = {
        "quick": "tCl",
        "full": "tCl,pCl,lCl,mPk"
    }
    
    ini_content = f"""
# V3 Canonical Unified Model - Production Run
output = {outputs.get(mode, "tCl")}
write background = yes
lensing = no

# Standard cosmology
h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544

# Gauge (required for Ridder field)
gauge = newtonian

# Ridder v3 unified field
use_ridder = yes
ridder_model_type = v3_canon

# Field normalization
ridder_f_eV = {v3_params['f_eV']:.6e}

# EDE bump (NOTE: C code calls this "shelf")
ridder_use_shelf = {bool_to_yesno(v3_params['use_EDE'])}
ridder_Lambda_EDE_eV = {v3_params['Lambda_EDE_eV']:.6e}
ridder_a_c = {1.0 / (1.0 + v3_params['z_c']):.6e}
ridder_sigma_lna = {v3_params['sigma_lna']:.6f}
ridder_theta_E_center = {v3_params['theta_E_center']}
ridder_sigma_E = {v3_params['sigma_E']}
ridder_n_EDE = {v3_params['n_EDE']}

# Tail
ridder_use_tail = {bool_to_yesno(v3_params['use_tail'])}
ridder_Lambda_tail_eV = {v3_params['Lambda_tail_eV']:.6e}
ridder_alpha_tail = {v3_params['alpha_tail']}
ridder_theta_T_center = {v3_params['theta_T_center']}
ridder_n_tail = {v3_params['n_tail']}

# Floor (v3: Lambda_floor absorbed into tail, no separate toggle)
ridder_Lambda_floor_eV = {v3_params['Lambda_floor_eV']:.6e}

# Initial conditions
theta_i_ridder = {v3_params['theta_E_center']}
ridder_c_slow = 0.0

# Output (relative path from CLASS working directory)
root = output/v3_run
"""
    
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False)
    tmp.write(ini_content)
    tmp.close()
    return tmp.name

def run_class_full(ini_path):
    """Run CLASS and return success status"""
    try:
        result = subprocess.run(
            [str(CLASS_BINARY), str(ini_path)],
            capture_output=True,
            text=True,
            timeout=300,
            check=True,
            cwd=CLASS_PATH  # Run from CLASS directory
        )
        return True, result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout + e.stderr
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"

def extract_observables(bg_file, mode="full"):
    """Extract observables from CLASS output"""
    try:
        data = np.loadtxt(bg_file)
        
        # Columns: z, proper_time, conf_time, H[1/Mpc], comov_dist, ang_diam_dist, ...
        # Check shape
        if data.shape[1] < 20:
            print(f"WARNING: background file has only {data.shape[1]} columns, expected 20+", file=sys.stderr)
        
        z = data[:, 0]
        H_Mpc = data[:, 3]  # H in 1/Mpc
        
        # Convert H from 1/Mpc to km/s/Mpc: H_km_s_Mpc = H_Mpc * c_km_s
        c_km_s = 299792.458  # km/s
        H = H_Mpc * c_km_s
        
        # Find rho_ridder column (may vary depending on CLASS configuration)
        # Typical columns after basic ones: rho_g, rho_b, rho_cdm, rho_lambda, rho_ur, rho_ncdm, ..., rho_ridder
        # For now, try column 14 and 19, but be defensive
        try:
            if data.shape[1] > 19:
                rho_ridder = data[:, 14]
                rho_tot = data[:, 19]
            else:
                # Fallback: can't compute f_EDE
                rho_ridder = np.zeros_like(z)
                rho_tot = np.ones_like(z)
        except IndexError:
            rho_ridder = np.zeros_like(z)
            rho_tot = np.ones_like(z)
        
        # H0
        idx_0 = np.argmin(np.abs(z))
        H0 = H[idx_0]
        
        # f_EDE peak
        f_ridder = rho_ridder / rho_tot
        mask = (z >= 1000) & (z <= 10000)
        if np.any(mask) and np.max(f_ridder[mask]) > 1e-6:
            idx_max = np.argmax(f_ridder[mask])
            f_EDE_peak = f_ridder[mask][idx_max]
            z_peak = z[mask][idx_max]
        else:
            f_EDE_peak = 0.0
            z_peak = 0.0
        
        # w(z) at late times (placeholder, would need p_ridder column)
        w_samples = []
        for z_check in [0.0, 1.0, 2.0]:
            idx = np.argmin(np.abs(z - z_check))
            w_samples.append({"z": float(z[idx]), "w": -1.0})
        
        return {
            "H0_km_s_Mpc": float(H0),
            "f_EDE_peak": float(f_EDE_peak),
            "z_peak": float(z_peak),
            "w_samples": w_samples
        }
    except Exception as e:
        print(f"Error extracting observables from {bg_file}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {}

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="V3 Unified Model Button")
    parser.add_argument("--Lambda_tail_meV", type=float, help="Tail energy scale [meV]")
    parser.add_argument("--f_axion", type=float, help="EDE strength parameter")
    parser.add_argument("--z_c", type=float, help="EDE peak redshift (overrides default)")
    parser.add_argument("--sigma_lna", type=float, help="EDE time window width (overrides default)")
    parser.add_argument("--preset", type=str, choices=list(PRESETS.keys()), help="Use preset configuration")
    parser.add_argument("--mode", type=str, choices=["quick", "full"], default="quick", help="Run mode")
    parser.add_argument("--output_json", type=str, help="Output JSON file path")
    parser.add_argument("--skip_shooting", action="store_true", help="Skip Lambda_EDE shooting (for testing)")
    
    args = parser.parse_args()
    
    # Resolve preset or explicit inputs
    if args.preset:
        Lambda_tail_meV = PRESETS[args.preset]["Lambda_tail_meV"]
        f_axion = PRESETS[args.preset]["f_axion"]
        preset_name = args.preset
    elif args.Lambda_tail_meV is not None and args.f_axion is not None:
        Lambda_tail_meV = args.Lambda_tail_meV
        f_axion = args.f_axion
        preset_name = None
    else:
        print("Error: Must specify either --preset or both --Lambda_tail_meV and --f_axion", file=sys.stderr)
        sys.exit(1)
    
    print("="*70)
    print("V3 CANONICAL UNIFIED MODEL")
    print("="*70)
    print(f"Inputs: Lambda_tail={Lambda_tail_meV:.1f} meV, f_axion={f_axion:.2f}")
    if preset_name:
        print(f"Preset: {preset_name}")
    print(f"Mode: {args.mode}")
    print()
    
    # Map to v3 parameters
    v3_params = map_button_to_v3(Lambda_tail_meV, f_axion)
    
    # Apply overrides if provided
    if args.z_c is not None:
        v3_params["z_c"] = args.z_c
    if args.sigma_lna is not None:
        v3_params["sigma_lna"] = args.sigma_lna
    
    # Shoot for Lambda_EDE (if EDE is active)
    if v3_params["use_EDE"] and not args.skip_shooting:
        Lambda_EDE, f_achieved, z_peak = solve_Lambda_EDE_for_target(
            v3_params["f_EDE_target"], 
            v3_params
        )
        v3_params["Lambda_EDE_eV"] = Lambda_EDE
    else:
        f_achieved = 0.0
        z_peak = 0.0
    
    # Write full INI and run CLASS
    ini_path = write_full_ini(v3_params, mode=args.mode)
    print()
    print("Running CLASS...")
    success, output = run_class_full(ini_path)
    
    if not success:
        print("CLASS FAILED:", file=sys.stderr)
        print(output, file=sys.stderr)
        # Save failed INI for debugging
        debug_ini = OUTPUT_DIR / "debug_failed.ini"
        shutil.copy(ini_path, debug_ini)
        print(f"Failed INI saved to {debug_ini}", file=sys.stderr)
        os.unlink(ini_path)
        sys.exit(1)
    
    print("✓ CLASS completed")
    # Save successful INI for debugging
    debug_ini = OUTPUT_DIR / "debug_success.ini"
    shutil.copy(ini_path, debug_ini)
    # os.unlink(ini_path)  # Keep for debugging
    
    # Extract observables (find latest v3_run file)
    bg_files = list(OUTPUT_DIR.glob("v3_run*_background.dat"))
    if not bg_files:
        print("ERROR: No background file found!", file=sys.stderr)
        sys.exit(1)
    bg_file = max(bg_files, key=lambda p: p.stat().st_mtime)  # Latest file
    observables = extract_observables(bg_file, mode=args.mode)
    
    # Build JSON summary
    summary = {
        "input": {
            "preset": preset_name,
            "Lambda_tail_meV": Lambda_tail_meV,
            "f_axion": f_axion,
            "mode": args.mode,
            "potential_version": "v3"
        },
        "v3_params": {
            "f_eV": v3_params["f_eV"],
            "Lambda_EDE_eV": v3_params["Lambda_EDE_eV"],
            "Lambda_tail_eV": v3_params["Lambda_tail_eV"],
            "theta_E_center": v3_params["theta_E_center"],
            "sigma_E": v3_params["sigma_E"],
            "n_EDE": v3_params["n_EDE"],
            "alpha_tail": v3_params["alpha_tail"],
            "n_tail": v3_params["n_tail"]
        },
        "observables": observables
    }
    
    # Output
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\nResults saved to {args.output_json}")
    else:
        print("\nRESULTS:")
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()

