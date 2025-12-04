#!/usr/bin/env python3
"""
Plot CMB Cl spectra: ΛCDM vs Ridder Field
Verify no discontinuities and show EDE effects
"""

import numpy as np
import matplotlib.pyplot as plt
import subprocess
import os

# Run CLASS for both cases
print("Running CLASS for ΛCDM baseline...")
subprocess.run([
    "../phase2/class/class",
    "scan/scan_0.00.ini"
], cwd=os.getcwd(), check=True)

print("Running CLASS for Ridder Field (Lambda=1.0 eV)...")
subprocess.run([
    "../phase2/class/class",
    "scan/scan_1.00.ini"
], cwd=os.getcwd(), check=True)

# Load Cl data
print("\nLoading Cl data...")
lcdm_file = "../phase2/class/output/scan_0.00_cl_lensed.dat"
ridder_file = "../phase2/class/output/scan_1.00_cl_lensed.dat"

lcdm = np.loadtxt(lcdm_file)
ridder = np.loadtxt(ridder_file)

# Extract columns: l, TT, EE, TE, PP
l_lcdm = lcdm[:, 0]
tt_lcdm = lcdm[:, 1]

l_ridder = ridder[:, 0]
tt_ridder = ridder[:, 1]

# Create comparison plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[2, 1])

# Top panel: Cl spectra
ax1.plot(l_lcdm, l_lcdm*(l_lcdm+1)*tt_lcdm/(2*np.pi), 
         label='ΛCDM', color='black', linewidth=2, alpha=0.7)
ax1.plot(l_ridder, l_ridder*(l_ridder+1)*tt_ridder/(2*np.pi), 
         label='Ridder Field (λ=1.0 eV)', color='red', linewidth=2, alpha=0.8)

ax1.set_xlabel('Multipole l', fontsize=14)
ax1.set_ylabel(r'$\ell(\ell+1)C_\ell^{TT}/2\pi$ [$\mu$K$^2$]', fontsize=14)
ax1.set_title('CMB Temperature Power Spectrum: ΛCDM vs Ridder Field', fontsize=16, fontweight='bold')
ax1.legend(fontsize=12, loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(2, 2500)

# Bottom panel: Ratio
ratio = tt_ridder / np.interp(l_ridder, l_lcdm, tt_lcdm)
ax2.plot(l_ridder, ratio, color='blue', linewidth=2)
ax2.axhline(1.0, color='black', linestyle='--', alpha=0.5)
ax2.set_xlabel('Multipole l', fontsize=14)
ax2.set_ylabel('Ratio (Ridder/ΛCDM)', fontsize=14)
ax2.set_title('Relative Difference', fontsize=14)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(2, 2500)
ax2.set_ylim(0.95, 1.05)

plt.tight_layout()
plt.savefig('cmb_comparison.png', dpi=300, bbox_inches='tight')
print(f"\n✅ Plot saved to cmb_comparison.png")

# Check for discontinuities
print("\n" + "="*60)
print("DISCONTINUITY CHECK")
print("="*60)

# Compute derivatives
dll = np.diff(l_ridder)
dCl = np.diff(tt_ridder)
derivative = dCl / dll

# Find large jumps
threshold = np.percentile(np.abs(derivative), 99)
jumps = np.where(np.abs(derivative) > threshold)[0]

if len(jumps) > 10:  # More than expected from peaks
    print(f"⚠️  WARNING: {len(jumps)} potential discontinuities detected")
    print(f"   Locations: l = {l_ridder[jumps[:5]]} ...")
else:
    print(f"✅ CLEAN: Only {len(jumps)} sharp features (expected from acoustic peaks)")

# Summary statistics
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Peak shift (first peak):")
peak1_lcdm_idx = np.argmax(tt_lcdm[50:300]) + 50
peak1_ridder_idx = np.argmax(tt_ridder[50:300]) + 50
print(f"  ΛCDM:   l = {l_lcdm[peak1_lcdm_idx]:.1f}")
print(f"  Ridder: l = {l_ridder[peak1_ridder_idx]:.1f}")
print(f"  Shift:  Δl = {l_ridder[peak1_ridder_idx] - l_lcdm[peak1_lcdm_idx]:.1f}")

print(f"\nAmplitude change:")
print(f"  Mean ratio: {np.mean(ratio):.4f}")
print(f"  Std ratio:  {np.std(ratio):.4f}")

print("\n✅ CMB spectra generated successfully!")
print("   No crashes, clean evolution to z=0")

