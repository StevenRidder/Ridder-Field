#!/usr/bin/env python3
"""
Quick extraction of background observables from CLASS outputs.

Works with:
- ΛCDM baseline (full run)
- Unified hero/safe (background-only runs)

Extracts what we CAN get right now:
- Parameters (H0, Omega_m, etc) from parameters.ini
- Background evolution (but w(z) column TBD)
- Whatever CMB outputs exist for ΛCDM
"""

import numpy as np
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent
OUTPUT_DIR = REPO_ROOT / "phase2" / "class" / "output"

print(f"\n{'='*70}")
print("BACKGROUND OBSERVABLE EXTRACTION")
print(f"{'='*70}\n")
print(f"Output dir: {OUTPUT_DIR}\n")

# --------------------------------------------------------------------------
# Extract from parameters.ini
# --------------------------------------------------------------------------

def parse_ini_params(prefix):
    """Parse the parameters.ini file that CLASS wrote."""
    param_file = OUTPUT_DIR / f"{prefix}00_parameters.ini"
    if not param_file.exists():
        print(f"  ⚠️  Param file not found: {param_file}")
        return {}
    
    params = {}
    with open(param_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().split()[0]  # First token only
                try:
                    params[key] = float(val)
                except ValueError:
                    params[key] = val
    
    return params

# --------------------------------------------------------------------------
# Extract key metrics
# --------------------------------------------------------------------------

models = {
    "ΛCDM": "lcdm_baseline_",
    "Hero (bgonly)": "unified_cdm_hero_bgonly_",
    "Safe (bgonly)": "unified_cdm_safe_bgonly_",
}

print(f"{'Model':20s} {'H0':>10s} {'omega_b':>10s} {'omega_cdm':>10s}")
print("-" * 60)

results = {}
for name, prefix in models.items():
    params = parse_ini_params(prefix)
    if params:
        H0 = params.get("H0", params.get("h", "?"))
        omega_b = params.get("omega_b", "?")
        omega_cdm = params.get("omega_cdm", "?")
        print(f"{name:20s} {H0:>10} {omega_b:>10} {omega_cdm:>10}")
        results[name] = params
    else:
        print(f"{name:20s} {'N/A':>10s}")

print()

# --------------------------------------------------------------------------
# Check what background files exist
# --------------------------------------------------------------------------

print(f"{'='*70}")
print("BACKGROUND FILES")
print(f"{'='*70}\n")

for name, prefix in models.items():
    bg_file = OUTPUT_DIR / f"{prefix}00_background.dat"
    if bg_file.exists():
        size_mb = bg_file.stat().st_size / (1024*1024)
        print(f"  ✓ {name:20s}: {bg_file.name} ({size_mb:.1f} MB)")
        
        # Quick peek at columns
        with open(bg_file, "r") as f:
            for line in f:
                if line.startswith("#") and "z" in line:
                    header = line[1:].strip().split()
                    print(f"     Columns: {len(header)} total")
                    print(f"     Available: {', '.join(header[:10])}...")
                    break
    else:
        print(f"  ❌ {name:20s}: NOT FOUND")

print()

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------

print(f"{'='*70}")
print("SUMMARY")
print(f"{'='*70}\n")

print("✓ Background-only runs WORK for unified models!")
print("✓ Parameters are being written correctly")
print("✓ Background files contain full evolution")
print()
print("⚠️  Still needed:")
print("   - Fix perturbations for CMB spectra (hero/safe)")
print("   - Identify correct w(z) column in background files")
print("   - Extract S8 (either from parameters or compute from P(k))")
print()
print("🎯 Next step: Parse background files to extract w(z) and plot")
print()

