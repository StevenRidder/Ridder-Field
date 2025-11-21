#!/usr/bin/env python3
"""Plot Matter Power Spectrum and Ratio (Growth Kink)"""
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# Load data
# Find latest files
lcdm_files = sorted(glob.glob('../phase2/class/output/scan_0.00_*_pk.dat'), key=os.path.getmtime)
ridder_files = sorted(glob.glob('../phase2/class/output/scan_1.00_*_pk.dat'), key=os.path.getmtime)

if not lcdm_files or not ridder_files:
    print("Error: Could not find P(k) files.")
    exit(1)

lcdm_file = lcdm_files[-1]
ridder_file = ridder_files[-1]

print(f"Using LCDM: {lcdm_file}")
print(f"Using Ridder: {ridder_file}")

lcdm = np.loadtxt(lcdm_file)
ridder = np.loadtxt(ridder_file)

k_lcdm, pk_lcdm = lcdm[:, 0], lcdm[:, 1]
k_ridder, pk_ridder = ridder[:, 0], ridder[:, 1]

# Interpolate to common k
k_common = np.logspace(np.log10(max(k_lcdm.min(), k_ridder.min())), 
                       np.log10(min(k_lcdm.max(), k_ridder.max())), 500)

pk_lcdm_interp = np.interp(k_common, k_lcdm, pk_lcdm)
pk_ridder_interp = np.interp(k_common, k_ridder, pk_ridder)

ratio = pk_ridder_interp / pk_lcdm_interp

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), height_ratios=[2, 1])

# Top: P(k)
ax1.loglog(k_lcdm, pk_lcdm, 'k-', label='ΛCDM', lw=2, alpha=0.7)
ax1.loglog(k_ridder, pk_ridder, 'r-', label='Ridder (λ=1.0 eV)', lw=2)
ax1.set_ylabel(r'$P(k)$ [Mpc/h]$^3$', fontsize=14)
ax1.set_title('Matter Power Spectrum', fontsize=16, fontweight='bold')
ax1.legend(fontsize=12)
ax1.grid(True, which='both', alpha=0.3)

# Bottom: Ratio
ax2.semilogx(k_common, ratio, 'b-', lw=2)
ax2.axhline(1.0, color='k', linestyle='--')
ax2.set_xlabel(r'$k$ [h/Mpc]', fontsize=14)
ax2.set_ylabel(r'$P_{Ridder}(k) / P_{\Lambda CDM}(k)$', fontsize=14)
ax2.set_title('Growth Ratio (Should be < 1 for suppression)', fontsize=14)
ax2.grid(True, which='both', alpha=0.3)
# ax2.set_ylim(0.8, 1.2) # Auto scale to see explosion

# Mark the kink location (approximate)
# k ~ a_c H_c ~ 1/r_s ~ 0.01 h/Mpc
ax2.axvline(0.01, color='gray', linestyle=':', label='Horizon at transition')

plt.tight_layout()
plt.savefig('pk_comparison_v2.png', dpi=300)
print("✅ Plot saved: pk_comparison_v2.png")

# Stats
print(f"Ratio at k=1e-5: {ratio[0]:.2e}")
print(f"Ratio at k=0.1: {ratio[np.argmin(np.abs(k_common - 0.1))]:.2f}")
