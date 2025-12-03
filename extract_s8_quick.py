#!/usr/bin/env python3
"""
Quick S8 extraction from stable unified point.

Compares:
- ΛCDM baseline
- Unified baby (Lambda=1.0, beta=0.05)
"""

import numpy as np
from pathlib import Path
import sys

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent
OUTPUT_DIR = REPO_ROOT / "phase2" / "class" / "output"

print(f"\n{'='*70}")
print("S8 EXTRACTION - UNIFIED vs ΛCDM")
print(f"{'='*70}\n")

# --------------------------------------------------------------------------
# Parse parameters.ini for sigma8 and Omega_m
# --------------------------------------------------------------------------

def parse_params(prefix):
    """Parse CLASS parameters output."""
    param_file = OUTPUT_DIR / f"{prefix}00_parameters.ini"
    if not param_file.exists():
        print(f"  ⚠️  File not found: {param_file}")
        return None
    
    params = {}
    with open(param_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().split()[0]
                try:
                    params[key] = float(val)
                except ValueError:
                    params[key] = val
    
    return params


def compute_omega_m(params):
    """Compute Omega_m = Omega_b + Omega_cdm."""
    omega_b = params.get("omega_b", 0)
    omega_cdm = params.get("omega_cdm", 0)
    h = params.get("H0", params.get("h", 67.36)) / 100.0
    
    Omega_b = omega_b / (h**2)
    Omega_cdm = omega_cdm / (h**2)
    Omega_m = Omega_b + Omega_cdm
    
    return Omega_m


def compute_sigma8_from_pk(prefix):
    """
    Compute sigma8 from matter power spectrum if not in parameters.
    
    Uses top-hat window function at R = 8 Mpc/h.
    """
    pk_file = OUTPUT_DIR / f"{prefix}00_pk.dat"
    if not pk_file.exists():
        pk_file = OUTPUT_DIR / f"{prefix}00_mPk.dat"
    if not pk_file.exists():
        return None
    
    # Load P(k)
    data = np.loadtxt(pk_file)
    k = data[:, 0]  # k in h/Mpc
    P = data[:, 1]  # P(k) in (Mpc/h)^3
    
    # Top-hat window function W(kR) = 3*(sin(kR) - kR*cos(kR))/(kR)^3
    R = 8.0  # Mpc/h
    kR = k * R
    
    # Avoid division by zero
    W = np.zeros_like(kR)
    mask = kR > 1e-4
    W[mask] = 3.0 * (np.sin(kR[mask]) - kR[mask] * np.cos(kR[mask])) / (kR[mask]**3)
    W[~mask] = 1.0 - (kR[~mask]**2) / 10.0  # Taylor expansion for small kR
    
    # Integrate sigma^2 = 1/(2π^2) * ∫ k^2 P(k) W^2(kR) dk
    integrand = k**2 * P * W**2
    sigma2 = np.trapz(integrand, k) / (2.0 * np.pi**2)
    sigma8 = np.sqrt(sigma2)
    
    return sigma8


# --------------------------------------------------------------------------
# Extract for each model
# --------------------------------------------------------------------------

models = {
    "ΛCDM": "lcdm_baseline_",
    "Unified (Λ=1.0)": "unified_baby_lambda1p0_",
}

results = {}

for name, prefix in models.items():
    print(f"{name:20s} ... ", end="", flush=True)
    
    params = parse_params(prefix)
    if params is None:
        print("❌ Parameters not found")
        continue
    
    # Try to get sigma8 from parameters
    sigma8 = params.get("sigma8")
    
    # If not available, compute from P(k)
    if sigma8 is None:
        print("σ₈ not in params, computing from P(k) ... ", end="", flush=True)
        sigma8 = compute_sigma8_from_pk(prefix)
        if sigma8 is None:
            print("❌ P(k) also not found")
            continue
    
    # Compute Omega_m
    Omega_m = compute_omega_m(params)
    
    # Compute S8 = sigma8 * sqrt(Omega_m / 0.3)
    S8 = sigma8 * np.sqrt(Omega_m / 0.3)
    
    print(f"σ₈={sigma8:.4f}, Ω_m={Omega_m:.4f}, S₈={S8:.4f}")
    
    results[name] = {
        "sigma8": sigma8,
        "Omega_m": Omega_m,
        "S8": S8,
    }

print()

# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------

if len(results) >= 2:
    print(f"{'='*70}")
    print("COMPARISON")
    print(f"{'='*70}\n")
    
    lcdm = results.get("ΛCDM")
    unified = results.get("Unified (Λ=1.0)")
    
    if lcdm and unified:
        delta_sigma8 = unified["sigma8"] - lcdm["sigma8"]
        delta_S8 = unified["S8"] - lcdm["S8"]
        
        print(f"{'Quantity':20s} {'ΛCDM':>12s} {'Unified':>12s} {'Δ':>12s}")
        print("-" * 60)
        print(f"{'σ₈':20s} {lcdm['sigma8']:12.4f} {unified['sigma8']:12.4f} {delta_sigma8:+12.4f}")
        print(f"{'Ω_m':20s} {lcdm['Omega_m']:12.4f} {unified['Omega_m']:12.4f} {unified['Omega_m']-lcdm['Omega_m']:+12.4f}")
        print(f"{'S₈':20s} {lcdm['S8']:12.4f} {unified['S8']:12.4f} {delta_S8:+12.4f}")
        print()
        
        # Context
        print("CONTEXT:")
        print(f"  Planck 2018:        S₈ = 0.834 ± 0.016")
        print(f"  Weak lensing (KiDS): S₈ = 0.766 ± 0.020")
        print(f"  Tension:            ΔS₈ ~ 0.068 (3.4σ)")
        print()
        
        # Assessment
        if delta_S8 < 0:
            reduction_pct = abs(delta_S8) / 0.068 * 100
            print(f"RESULT:")
            print(f"  Unified model reduces S₈ by {abs(delta_S8):.4f}")
            print(f"  This is {reduction_pct:.1f}% of the full tension")
            print()
            
            if reduction_pct > 50:
                print("  ✅ Significant reduction (>50% of tension)")
            elif reduction_pct > 25:
                print("  ⚠️  Moderate reduction (25-50% of tension)")
            else:
                print("  ⚠️  Small reduction (<25% of tension)")
        else:
            print(f"RESULT:")
            print(f"  ⚠️  Unified model INCREASES S₈ by {delta_S8:.4f}")
            print(f"  This moves AWAY from weak lensing data")
        
        print()

print(f"{'='*70}")
print("DONE")
print(f"{'='*70}\n")

