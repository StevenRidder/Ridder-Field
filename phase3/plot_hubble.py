#!/usr/bin/env python3
"""Plot Hubble Parameter Ratio (The Money Plot)"""
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# Load data
lcdm_file = '../phase2/class/output/scan_0.00_30_background.dat' # Verified baseline

# Find latest final run background file
tune_files = sorted(glob.glob('../phase2/class/output/final_run_*background.dat'), key=os.path.getmtime)
if not tune_files:
    print("Error: No final run background file found.")
    exit(1)
ridder_file = tune_files[-1]

print(f"Using LCDM: {lcdm_file}")
print(f"Using Ridder: {ridder_file}")

# Load data
# Columns: 1:z, 4:H [1/Mpc]
lcdm = np.loadtxt(lcdm_file)
ridder = np.loadtxt(ridder_file)

z_lcdm, H_lcdm = lcdm[:, 0], lcdm[:, 3]
z_ridder, H_ridder = ridder[:, 0], ridder[:, 3]

# Interpolate to common z
z_common = np.logspace(0, 5, 1000) # z=1 to z=100,000

H_lcdm_interp = np.interp(z_common, np.flip(z_lcdm), np.flip(H_lcdm))
H_ridder_interp = np.interp(z_common, np.flip(z_ridder), np.flip(H_ridder))

ratio = H_ridder_interp / H_lcdm_interp

# Plot
fig, ax = plt.subplots(figsize=(10, 6))

ax.semilogx(z_common, ratio, 'r-', lw=2.5, label='Ridder Field / ΛCDM')
ax.axhline(1.0, color='k', linestyle='--')

# Mark critical epochs
ax.axvline(3400, color='gray', linestyle=':', label='Matter-Radiation Equality')
ax.axvline(1100, color='gray', linestyle='--', label='Recombination')

ax.set_xlabel('Redshift $z$', fontsize=14)
ax.set_ylabel('$H(z)_{Ridder} / H(z)_{\Lambda CDM}$', fontsize=14)
ax.set_title('The "Hubble Bump": Early Dark Energy Injection', fontsize=16, fontweight='bold')
ax.legend(fontsize=12)
ax.grid(True, which='both', alpha=0.3)
ax.set_xlim(10, 20000)
ax.set_ylim(0.95, 1.20)

# Annotate the bump
bump_z = z_common[np.argmax(ratio)]
bump_val = np.max(ratio)
ax.annotate(f'EDE Peak\n$z \\approx {bump_z:.0f}$', xy=(bump_z, bump_val), xytext=(bump_z*2, bump_val+0.05),
            arrowprops=dict(facecolor='black', shrink=0.05), fontsize=12)

plt.tight_layout()
plt.savefig('final_hubble_ratio.png', dpi=300)
print("✅ Plot saved: final_hubble_ratio.png")
