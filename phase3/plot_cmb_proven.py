#!/usr/bin/env python3
"""Plot CMB TT Spectrum Comparison"""
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# Load data
# Find latest files
lcdm_files = sorted(glob.glob('../phase2/class/output/scan_0.00_*_cl.dat'), key=os.path.getmtime)
ridder_files = sorted(glob.glob('../phase2/class/output/scan_1.00_*_cl.dat'), key=os.path.getmtime)

if not lcdm_files or not ridder_files:
    print("Error: Could not find Cl files.")
    exit(1)

lcdm_file = lcdm_files[-1]
ridder_file = ridder_files[-1]

print(f"Using LCDM: {lcdm_file}")
print(f"Using Ridder: {ridder_file}")

# Load data (skip header)
lcdm = np.loadtxt(lcdm_file)
ridder = np.loadtxt(ridder_file)

l_lcdm, tt_lcdm = lcdm[:, 0], lcdm[:, 1]
l_ridder, tt_ridder = ridder[:, 0], ridder[:, 1]

# Conversion factor: dimensionless -> uK^2
# D_l = l(l+1)C_l/2pi. The file contains exactly this (dimensionless).
# To get uK^2, multiply by (T_cmb * 1e6)^2
T_cmb = 2.7255 # K
factor = (T_cmb * 1.e6)**2

tt_lcdm_uk = tt_lcdm * factor
tt_ridder_uk = tt_ridder * factor

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), height_ratios=[2, 1])

# Top: TT Spectrum
ax1.plot(l_lcdm, tt_lcdm_uk, 'k-', label='ΛCDM (Baseline)', lw=2, alpha=0.7)
ax1.plot(l_ridder, tt_ridder_uk, 'r-', label='Ridder (λ=1.0 eV)', lw=2)
ax1.set_ylabel(r'$\mathcal{D}_\ell^{TT}$ [$\mu K^2$]', fontsize=14)
ax1.set_title('CMB TT Power Spectrum', fontsize=16, fontweight='bold')
ax1.legend(fontsize=12)
ax1.grid(True, which='both', alpha=0.3)
ax1.set_xlim(2, 2500)

# Bottom: Residuals
# Interpolate to common l
l_common = np.arange(2, 2501)
tt_lcdm_interp = np.interp(l_common, l_lcdm, tt_lcdm_uk)
tt_ridder_interp = np.interp(l_common, l_ridder, tt_ridder_uk)

diff = tt_ridder_interp - tt_lcdm_interp
rel_diff = (tt_ridder_interp - tt_lcdm_interp) / tt_lcdm_interp

ax2.plot(l_common, rel_diff * 100, 'b-', lw=2)
ax2.axhline(0.0, color='k', linestyle='--')
ax2.set_xlabel(r'Multipole $\ell$', fontsize=14)
ax2.set_ylabel(r'Relative Change [%]', fontsize=14)
ax2.set_title('Relative Difference (Ridder - ΛCDM) / ΛCDM', fontsize=14)
ax2.grid(True, which='both', alpha=0.3)
ax2.set_xlim(2, 2500)

plt.tight_layout()
plt.savefig('cmb_comparison_proven.png', dpi=300)
print("✅ Plot saved: cmb_comparison_proven.png")

