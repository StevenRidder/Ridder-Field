#!/usr/bin/env python3
"""
Extract and plot CMB "soft shoulder" from unified model.

Compares TT, EE, TE spectra:
- ΛCDM baseline
- Unified (Lambda=1.0, beta=0.05)
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent
OUTPUT_DIR = REPO_ROOT / "phase2" / "class" / "output"

print(f"\n{'='*70}")
print("CMB RESIDUAL EXTRACTION - 'SOFT SHOULDER' SIGNATURE")
print(f"{'='*70}\n")

# --------------------------------------------------------------------------
# Load CMB spectra
# --------------------------------------------------------------------------

def load_cl(prefix):
    """Load CMB spectra from CLASS output."""
    # Try lensed file first (most complete)
    cl_file = OUTPUT_DIR / f"{prefix}00_cl_lensed.dat"
    if not cl_file.exists():
        cl_file = OUTPUT_DIR / f"{prefix}00_cl.dat"
    
    if not cl_file.exists():
        print(f"  ⚠️  Cl file not found: {cl_file}")
        return None
    
    # Read header to find columns
    with open(cl_file, "r") as f:
        for line in f:
            if line.startswith("#") and "TT" in line:
                header = line[1:].strip().split()
                break
        else:
            print(f"  ⚠️  No header found")
            return None
    
    # Load data
    data = np.loadtxt(cl_file)
    
    # Find column indices
    try:
        l_idx = next(i for i, h in enumerate(header) if "l" in h.lower() and len(h) <= 2)
    except StopIteration:
        l_idx = 0
    
    ell = data[:, l_idx].astype(int)
    
    # Find TT, EE, TE, BB
    result = {"ell": ell}
    
    for spec_name in ["TT", "EE", "TE", "BB"]:
        try:
            idx = next(i for i, h in enumerate(header) if spec_name in h.upper())
            result[spec_name] = data[:, idx]
        except StopIteration:
            result[spec_name] = None
    
    return result


# Load spectra
print("Loading ΛCDM ... ", end="", flush=True)
lcdm = load_cl("lcdm_baseline_")
if lcdm:
    print(f"✓ {len(lcdm['ell'])} points, ℓ ∈ [{lcdm['ell'][0]}, {lcdm['ell'][-1]}]")
else:
    print("❌ FAILED")

print("Loading Unified ... ", end="", flush=True)
unified = load_cl("unified_baby_lambda1p0_")
if unified:
    print(f"✓ {len(unified['ell'])} points, ℓ ∈ [{unified['ell'][0]}, {unified['ell'][-1]}]")
else:
    print("❌ FAILED")

if not lcdm or not unified:
    print("\n⚠️  Cannot proceed without both spectra")
    exit(1)

print()

# --------------------------------------------------------------------------
# Compute residuals
# --------------------------------------------------------------------------

print(f"{'='*70}")
print("COMPUTING RESIDUALS")
print(f"{'='*70}\n")

# Interpolate to common ℓ grid
ell_common = unified["ell"]

residuals = {"ell": ell_common}

for spec in ["TT", "EE", "TE"]:
    if lcdm[spec] is not None and unified[spec] is not None:
        # Interpolate ΛCDM to unified grid
        lcdm_interp = np.interp(ell_common, lcdm["ell"], lcdm[spec])
        
        # Compute fractional residual
        # Avoid division by zero (TE can cross zero)
        mask = np.abs(lcdm_interp) > 1e-20
        frac_res = np.zeros_like(ell_common, dtype=float)
        frac_res[mask] = (unified[spec][mask] - lcdm_interp[mask]) / np.abs(lcdm_interp[mask])
        
        residuals[spec] = frac_res * 100  # Convert to percent
        
        # Statistics
        max_dev = np.max(np.abs(frac_res[mask])) * 100
        rms_dev = np.sqrt(np.mean((frac_res[mask])**2)) * 100
        
        print(f"{spec:3s}: Max |ΔCℓ/Cℓ| = {max_dev:6.2f}%, RMS = {rms_dev:6.2f}%")
        
        # Find ℓ range where |deviation| > 1%
        big_mask = np.abs(frac_res) > 0.01
        if np.any(big_mask):
            ell_range = ell_common[big_mask]
            print(f"     Deviation > 1% for ℓ ∈ [{ell_range[0]}, {ell_range[-1]}]")

print()

# --------------------------------------------------------------------------
# Create plots
# --------------------------------------------------------------------------

print(f"{'='*70}")
print("CREATING PLOTS")
print(f"{'='*70}\n")

# Plot 1: TT residuals
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

for i, (spec, ax) in enumerate(zip(["TT", "EE", "TE"], axes)):
    if spec in residuals and residuals[spec] is not None:
        ax.plot(residuals["ell"], residuals[spec], 'b-', linewidth=1.5, alpha=0.8)
        ax.axhline(0, color='gray', linestyle=':', alpha=0.5)
        ax.axhline(1, color='red', linestyle='--', alpha=0.3, label='±1%')
        ax.axhline(-1, color='red', linestyle='--', alpha=0.3)
        
        ax.set_ylabel(f'ΔC$_\\ell^{{{spec}}}$ / C$_\\ell^{{{spec}}}$ [%]', fontsize=12)
        ax.set_xlim(2, 2000)
        ax.set_ylim(-5, 5)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        # Highlight "shoulder" region if present
        big_mask = np.abs(residuals[spec]) > 1.0
        if np.any(big_mask):
            ell_shoulder = residuals["ell"][big_mask]
            ax.axvspan(ell_shoulder[0], ell_shoulder[-1], alpha=0.1, color='yellow', 
                      label='Deviation > 1%')

axes[-1].set_xlabel('Multipole ℓ', fontsize=12)
axes[0].set_title('CMB Residuals: Unified vs ΛCDM\n"Soft Shoulder" Signature', fontsize=14, fontweight='bold')

plt.tight_layout()
output_file = REPO_ROOT / "cmb_residuals_unified.png"
plt.savefig(output_file, dpi=150)
print(f"✓ Saved: {output_file}")

# Plot 2: Zoomed view on "shoulder" region
fig, ax = plt.subplots(figsize=(10, 6))

for spec, color, style in [("TT", "blue", "-"), ("EE", "red", "--"), ("TE", "green", ":")]:
    if spec in residuals and residuals[spec] is not None:
        ax.plot(residuals["ell"], residuals[spec], 
               color=color, linestyle=style, linewidth=2, 
               label=spec, alpha=0.8)

ax.axhline(0, color='gray', linestyle=':', alpha=0.5)
ax.axhline(1, color='gray', linestyle='--', alpha=0.3)
ax.axhline(-1, color='gray', linestyle='--', alpha=0.3)

ax.set_xlabel('Multipole ℓ', fontsize=14)
ax.set_ylabel('ΔCℓ / Cℓ [%]', fontsize=14)
ax.set_xlim(10, 1000)
ax.set_ylim(-3, 3)
ax.set_xscale('log')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=12, loc='best')
ax.set_title('CMB "Soft Shoulder": Unified vs ΛCDM', fontsize=16, fontweight='bold')

plt.tight_layout()
output_file = REPO_ROOT / "cmb_shoulder_zoom.png"
plt.savefig(output_file, dpi=150)
print(f"✓ Saved: {output_file}")

print()

# --------------------------------------------------------------------------
# Assessment
# --------------------------------------------------------------------------

print(f"{'='*70}")
print("ASSESSMENT: 'SOFT SHOULDER' vs SHARP SPIKE")
print(f"{'='*70}\n")

for spec in ["TT", "EE", "TE"]:
    if spec in residuals and residuals[spec] is not None:
        res = residuals[spec]
        ell = residuals["ell"]
        
        # Find peak deviation
        idx_max = np.argmax(np.abs(res))
        ell_peak = ell[idx_max]
        res_peak = res[idx_max]
        
        # Measure width at half maximum
        mask_big = np.abs(res) > np.abs(res_peak) / 2
        if np.sum(mask_big) > 1:
            ell_width = ell[mask_big][-1] - ell[mask_big][0]
        else:
            ell_width = 0
        
        print(f"{spec}:")
        print(f"  Peak: {res_peak:+.2f}% at ℓ = {ell_peak}")
        print(f"  Width: Δℓ ~ {ell_width} (at half-max)")
        
        # Classify
        if ell_width > 100:
            print(f"  → ✅ BROAD 'soft shoulder' (Δℓ > 100)")
        elif ell_width > 50:
            print(f"  → ⚠️  Moderate width (50 < Δℓ < 100)")
        else:
            print(f"  → ❌ Narrow spike (Δℓ < 50)")
        print()

print("INTERPRETATION:")
print("  If deviations are BROAD (Δℓ > 100): Consistent with 'soft shoulder' narrative")
print("  If deviations are SHARP (Δℓ < 50): More like traditional EDE spike")
print()

print(f"{'='*70}")
print("DONE")
print(f"{'='*70}\n")

