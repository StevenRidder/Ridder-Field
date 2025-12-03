#!/usr/bin/env python3
"""
Complete analysis of unified Ridder models vs ΛCDM baseline.

Extracts:
1. S₈ = σ₈ √(Ω_m / 0.3)
2. w(z) evolution
3. EE/TE "soft shoulder" in CMB polarization

Compares:
- ΛCDM baseline
- Unified hero (β=0.20, σ_z=0.5)
- Unified safe (β=0.15, σ_z=0.5)
"""

import numpy as np
import subprocess
import sys
from pathlib import Path
import json

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent
CLASS_DIR = REPO_ROOT / "phase2" / "class"
OUTPUT_DIR = CLASS_DIR / "output"

MODELS = {
    "lcdm": {
        "ini": REPO_ROOT / "lambdaCDM_baseline.ini",
        "root": "lcdm_baseline_",
        "label": "ΛCDM",
        "color": "black",
    },
    "hero": {
        "ini": REPO_ROOT / "unified_cdm_hero.ini",
        "root": "unified_cdm_hero_",
        "label": "Unified Hero (β=0.20)",
        "color": "red",
    },
    "safe": {
        "ini": REPO_ROOT / "unified_cdm_safe.ini",
        "root": "unified_cdm_safe_",
        "label": "Unified Safe (β=0.15)",
        "color": "blue",
    },
}

# --------------------------------------------------------------------------
# Run CLASS
# --------------------------------------------------------------------------

def run_class_for_all(skip_if_exists=False):
    """Run CLASS for all three models."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for name, cfg in MODELS.items():
        print(f"\n{'='*70}")
        print(f"Running CLASS for {cfg['label']}")
        print(f"{'='*70}")
        
        # Check if outputs already exist
        bg_file = OUTPUT_DIR / f"{cfg['root']}background.dat"
        if skip_if_exists and bg_file.exists():
            print(f"  ✓ Outputs exist, skipping...")
            continue
        
        # Run CLASS
        cmd = [str(CLASS_DIR / "class"), str(cfg["ini"])]
        print(f"  $ {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            cwd=CLASS_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        
        if result.returncode != 0:
            print(f"  ❌ CLASS failed for {name}!")
            print("  --- Output ---")
            print(result.stdout[-2000:])  # Last 2000 chars
            print("\n  Continuing anyway to process other models...")
        else:
            print(f"  ✓ CLASS completed successfully")

# --------------------------------------------------------------------------
# Extract S₈
# --------------------------------------------------------------------------

def parse_parameters_file(root_prefix):
    """
    Parse CLASS parameters output to get σ₈ and Ω_m.
    
    CLASS writes these to:
    - output/<root>parameters.ini  (some versions)
    - OR in the .ini file itself if write parameters updates it
    - OR we need to parse from stdout/log
    
    Fallback: compute from P(k) if needed.
    """
    # Try common parameter file locations
    candidates = [
        OUTPUT_DIR / f"{root_prefix}parameters.ini",
        OUTPUT_DIR / f"{root_prefix}00_parameters.ini",
        OUTPUT_DIR / f"{root_prefix}.param",
    ]
    
    sigma8 = None
    omega_m = None
    omega_b = None
    omega_cdm = None
    
    for param_file in candidates:
        if not param_file.exists():
            continue
        
        with open(param_file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().split()[0]  # Take first token
                    
                    try:
                        if key == "sigma8":
                            sigma8 = float(val)
                        elif key == "Omega_m":
                            omega_m = float(val)
                        elif key == "omega_b":
                            omega_b = float(val)
                        elif key == "omega_cdm":
                            omega_cdm = float(val)
                    except ValueError:
                        continue
        
        if sigma8 is not None:
            break
    
    # If we got omega_b and omega_cdm but not Omega_m, compute it
    # Omega_m ≈ (omega_b + omega_cdm) / h^2
    # For now, we'll need h too, but let's see if we can extract Omega_m directly
    
    if sigma8 is None:
        print(f"    ⚠️  Could not find sigma8 in {candidates}")
        return None, None, None
    
    if omega_m is None and omega_b is not None and omega_cdm is not None:
        # Approximate: assume h = 0.6736
        h = 0.6736
        omega_m = omega_b + omega_cdm
        Omega_m = omega_m / (h**2)
        omega_m = Omega_m
    
    if omega_m is None:
        print(f"    ⚠️  Could not find Omega_m in {candidates}")
        return sigma8, None, None
    
    # Compute S₈
    S8 = sigma8 * np.sqrt(omega_m / 0.3)
    
    return sigma8, omega_m, S8


def extract_S8_for_all():
    """Extract S₈ for all models."""
    print(f"\n{'='*70}")
    print("EXTRACTING S₈")
    print(f"{'='*70}\n")
    
    results = {}
    for name, cfg in MODELS.items():
        print(f"{cfg['label']:25s} ... ", end="", flush=True)
        sigma8, omega_m, S8 = parse_parameters_file(cfg["root"])
        
        if S8 is not None:
            print(f"σ₈={sigma8:.4f}, Ω_m={omega_m:.4f}, S₈={S8:.4f}")
            results[name] = {"sigma8": sigma8, "Omega_m": omega_m, "S8": S8}
        else:
            print("❌ Failed to extract")
            results[name] = None
    
    return results

# --------------------------------------------------------------------------
# Extract w(z)
# --------------------------------------------------------------------------

def load_background_w(root_prefix):
    """
    Load w(z) from background file.
    
    Background file has columns (varies by version):
    # z  a  H  ...  w_fld  (w_fld is for fluid component)
    
    We need to find the column that corresponds to dark energy EOS.
    """
    bg_file = OUTPUT_DIR / f"{root_prefix}background.dat"
    if not bg_file.exists():
        # Try with 00 suffix
        bg_file = OUTPUT_DIR / f"{root_prefix}00_background.dat"
    
    if not bg_file.exists():
        print(f"    ⚠️  Background file not found: {bg_file}")
        return None, None
    
    # Read header to find column indices
    with open(bg_file, "r") as f:
        for line in f:
            if line.startswith("#") and "z" in line:
                header = line[1:].strip().split()
                break
        else:
            print(f"    ⚠️  No header found in {bg_file}")
            return None, None
    
    # Find z column (usually first) and w column
    try:
        z_idx = header.index("z")
    except ValueError:
        z_idx = 0  # Assume first column
    
    # Look for w_fld, w_tot, or similar
    w_idx = None
    for candidate in ["w_fld", "(w_fld+delta_fld)", "w_tot", "w", "w_de"]:
        try:
            w_idx = header.index(candidate)
            break
        except ValueError:
            continue
    
    if w_idx is None:
        print(f"    ⚠️  Could not find w column in header: {header}")
        # Try to guess: often it's near the end
        w_idx = -3  # Common position
    
    # Load data
    data = np.loadtxt(bg_file)
    z = data[:, z_idx]
    w = data[:, w_idx]
    
    return z, w


def extract_w_for_all():
    """Extract w(z) for all models."""
    print(f"\n{'='*70}")
    print("EXTRACTING w(z)")
    print(f"{'='*70}\n")
    
    results = {}
    for name, cfg in MODELS.items():
        print(f"{cfg['label']:25s} ... ", end="", flush=True)
        z, w = load_background_w(cfg["root"])
        
        if z is not None:
            # Sample at a few key redshifts
            z_samples = [0, 0.5, 1.0, 2.0]
            w_samples = [np.interp(zs, z, w) for zs in z_samples]
            print(f"w(z=0)={w_samples[0]:.4f}, w(z=1)={w_samples[2]:.4f}")
            results[name] = {"z": z, "w": w}
        else:
            print("❌ Failed to extract")
            results[name] = None
    
    return results

# --------------------------------------------------------------------------
# Extract EE/TE
# --------------------------------------------------------------------------

def load_cl_polarization(root_prefix):
    """
    Load EE and TE from CLASS output.
    
    CLASS writes polarization to separate files or combined:
    - *_cl.dat (TT, sometimes includes TE)
    - *_cl_lensed.dat (lensed TT)
    - Separate EE/TE/BB files in some versions
    
    Check for *_lensed.dat first (most complete).
    """
    # Try lensed file first (has everything)
    cl_file = OUTPUT_DIR / f"{root_prefix}cl_lensed.dat"
    if not cl_file.exists():
        cl_file = OUTPUT_DIR / f"{root_prefix}00_cl_lensed.dat"
    if not cl_file.exists():
        cl_file = OUTPUT_DIR / f"{root_prefix}cl.dat"
    if not cl_file.exists():
        cl_file = OUTPUT_DIR / f"{root_prefix}00_cl.dat"
    
    if not cl_file.exists():
        print(f"    ⚠️  Cl file not found")
        return None, None, None, None
    
    # Read header
    with open(cl_file, "r") as f:
        for line in f:
            if line.startswith("#") and "l" in line.lower():
                header = line[1:].strip().split()
                break
        else:
            print(f"    ⚠️  No header in {cl_file}")
            return None, None, None, None
    
    # Find column indices
    try:
        l_idx = header.index("l")
    except ValueError:
        l_idx = 0
    
    # Look for TT, EE, TE
    tt_idx = None
    ee_idx = None
    te_idx = None
    
    for i, col in enumerate(header):
        col_lower = col.lower()
        if "tt" in col_lower:
            tt_idx = i
        elif "ee" in col_lower:
            ee_idx = i
        elif "te" in col_lower:
            te_idx = i
    
    # Load data
    data = np.loadtxt(cl_file)
    ell = data[:, l_idx]
    
    TT = data[:, tt_idx] if tt_idx is not None else None
    EE = data[:, ee_idx] if ee_idx is not None else None
    TE = data[:, te_idx] if te_idx is not None else None
    
    return ell, TT, EE, TE


def extract_cl_for_all():
    """Extract Cl for all models."""
    print(f"\n{'='*70}")
    print("EXTRACTING Cℓ (TT, EE, TE)")
    print(f"{'='*70}\n")
    
    results = {}
    for name, cfg in MODELS.items():
        print(f"{cfg['label']:25s} ... ", end="", flush=True)
        ell, TT, EE, TE = load_cl_polarization(cfg["root"])
        
        if ell is not None:
            status = []
            if TT is not None:
                status.append("TT")
            if EE is not None:
                status.append("EE")
            if TE is not None:
                status.append("TE")
            print(f"✓ Loaded {', '.join(status)} for ℓ ∈ [{ell[0]:.0f}, {ell[-1]:.0f}]")
            results[name] = {"ell": ell, "TT": TT, "EE": EE, "TE": TE}
        else:
            print("❌ Failed to extract")
            results[name] = None
    
    return results

# --------------------------------------------------------------------------
# Create summary report
# --------------------------------------------------------------------------

def create_summary_report(s8_data, w_data, cl_data):
    """Create a summary JSON and text report."""
    
    # Text summary
    print(f"\n{'='*70}")
    print("SUMMARY REPORT")
    print(f"{'='*70}\n")
    
    # S₈ comparison
    if s8_data.get("lcdm") and s8_data.get("hero"):
        lcdm_s8 = s8_data["lcdm"]["S8"]
        hero_s8 = s8_data["hero"]["S8"]
        safe_s8 = s8_data["safe"]["S8"] if s8_data.get("safe") else None
        
        print("S₈ VALUES:")
        print(f"  ΛCDM:        S₈ = {lcdm_s8:.4f}")
        print(f"  Unified Hero: S₈ = {hero_s8:.4f}  (ΔS₈ = {hero_s8 - lcdm_s8:+.4f})")
        if safe_s8:
            print(f"  Unified Safe: S₈ = {safe_s8:.4f}  (ΔS₈ = {safe_s8 - lcdm_s8:+.4f})")
        print()
    
    # w(z) at key redshifts
    if w_data.get("lcdm") and w_data.get("hero"):
        print("w(z) AT KEY REDSHIFTS:")
        for z_sample in [0, 0.5, 1.0, 2.0]:
            print(f"  z = {z_sample:.1f}:")
            for name in ["lcdm", "hero", "safe"]:
                if w_data.get(name):
                    z_arr = w_data[name]["z"]
                    w_arr = w_data[name]["w"]
                    w_val = np.interp(z_sample, z_arr, w_arr)
                    print(f"    {MODELS[name]['label']:20s}: w = {w_val:.4f}")
        print()
    
    # EE/TE residuals
    if cl_data.get("lcdm") and cl_data.get("hero"):
        print("EE/TE SOFT SHOULDER:")
        lcdm_ee = cl_data["lcdm"]["EE"]
        hero_ee = cl_data["hero"]["EE"]
        
        if lcdm_ee is not None and hero_ee is not None:
            # Find ℓ range where deviation is > 1%
            ell = cl_data["lcdm"]["ell"]
            frac_diff = np.abs((hero_ee - lcdm_ee) / lcdm_ee)
            
            # Find ℓ range where |ΔEE/EE| > 0.01
            mask = frac_diff > 0.01
            if np.any(mask):
                ell_range = ell[mask]
                print(f"  EE deviation > 1% for ℓ ∈ [{ell_range[0]:.0f}, {ell_range[-1]:.0f}]")
                max_dev = np.max(frac_diff[mask]) * 100
                print(f"  Max fractional deviation: {max_dev:.1f}%")
            else:
                print(f"  No significant EE deviation detected")
        
        # Same for TE
        lcdm_te = cl_data["lcdm"]["TE"]
        hero_te = cl_data["hero"]["TE"]
        
        if lcdm_te is not None and hero_te is not None:
            frac_diff = np.abs((hero_te - lcdm_te) / np.abs(lcdm_te))
            mask = frac_diff > 0.01
            if np.any(mask):
                ell_range = ell[mask]
                print(f"  TE deviation > 1% for ℓ ∈ [{ell_range[0]:.0f}, {ell_range[-1]:.0f}]")
                max_dev = np.max(frac_diff[mask]) * 100
                print(f"  Max fractional deviation: {max_dev:.1f}%")
            else:
                print(f"  No significant TE deviation detected")
        print()
    
    # Save JSON
    output = {
        "S8": s8_data,
        "w_samples": {},
        "cl_summary": {},
    }
    
    # Sample w(z) at key points for JSON
    for name in ["lcdm", "hero", "safe"]:
        if w_data.get(name):
            z_arr = w_data[name]["z"]
            w_arr = w_data[name]["w"]
            output["w_samples"][name] = {
                f"z_{z:.1f}": float(np.interp(z, z_arr, w_arr))
                for z in [0, 0.5, 1.0, 2.0, 5.0, 10.0]
            }
    
    json_file = REPO_ROOT / "unified_observables_summary.json"
    with open(json_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Saved summary to {json_file}")

# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    print(f"\n{'#'*70}")
    print("# UNIFIED RIDDER OBSERVABLE EXTRACTION")
    print(f"{'#'*70}\n")
    print(f"Repo root: {REPO_ROOT}")
    print(f"CLASS dir: {CLASS_DIR}")
    print(f"Output dir: {OUTPUT_DIR}")
    
    # 1. Run CLASS for all models
    run_class_for_all(skip_if_exists=False)
    
    # 2. Extract observables
    s8_data = extract_S8_for_all()
    w_data = extract_w_for_all()
    cl_data = extract_cl_for_all()
    
    # 3. Create summary
    create_summary_report(s8_data, w_data, cl_data)
    
    print(f"\n{'='*70}")
    print("DONE!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()

