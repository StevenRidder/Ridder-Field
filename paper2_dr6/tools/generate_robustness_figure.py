#!/usr/bin/env python3
"""
Generate robustness figure: PTE histogram + phase scrambling comparison
"""

import numpy as np
import matplotlib.pyplot as plt

# Load PTE results
pte_data = np.loadtxt("proper_pte_histogram.txt")
A_sh_centers = pte_data[:, 0]
pte_pdf = pte_data[:, 1]

# Load phase scrambling results
with open("phase_scrambling_results.txt", 'r') as f:
    for line in f:
        if line.startswith("A_correct"):
            A_correct = float(line.split("=")[1])
        elif line.startswith("A_scrambled_mean"):
            A_scr_mean = float(line.split("=")[1])
        elif line.startswith("A_scrambled_std"):
            A_scr_std = float(line.split("=")[1])

# Observed value
A_obs = 1.54

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Panel (a): PTE histogram
ax1.fill_between(A_sh_centers, pte_pdf, alpha=0.4, color='steelblue', 
                  label=r'$\Lambda$CDM sims (N=10,000)')
ax1.axvline(A_obs, color='crimson', lw=2.5, ls='--', 
            label=f'Observed: $A_{{\\rm sh}} = {A_obs:.2f}$')
ax1.axvline(-A_obs, color='crimson', lw=2.5, ls='--', alpha=0.5)

# Add Gaussian fit
x = np.linspace(-0.8, 0.8, 200)
sigma = 0.152
gaussian = np.exp(-x**2 / (2*sigma**2)) / (sigma * np.sqrt(2*np.pi))
ax1.plot(x, gaussian, 'k--', alpha=0.5, lw=1.5, label=f'Gaussian ($\\sigma = {sigma:.3f}$)')

ax1.set_xlabel(r'$A_{\rm sh}$', fontsize=14)
ax1.set_ylabel('Probability density', fontsize=14)
ax1.set_title(r'(a) PTE: $P < 10^{-4}$, $z = 10.1\sigma$', fontsize=14)
ax1.set_xlim(-0.8, 0.8)
ax1.legend(loc='upper right', fontsize=11)
ax1.set_ylim(bottom=0)

# Add arrow pointing to observed value (off scale)
ax1.annotate('', xy=(0.75, 0.5), xytext=(0.75, 2),
            arrowprops=dict(arrowstyle='->', color='crimson', lw=2),
            fontsize=12)
ax1.text(0.62, 2.1, f'Observed\n$A_{{\\rm sh}} = {A_obs}$\n(off scale)', 
         fontsize=10, color='crimson', ha='center')

# Panel (b): Phase scrambling
# Show distribution of scrambled A_sh values
scrambled_x = np.linspace(-0.6, 0.6, 100)
scrambled_pdf = np.exp(-scrambled_x**2 / (2*A_scr_std**2)) / (A_scr_std * np.sqrt(2*np.pi))

ax2.fill_between(scrambled_x, scrambled_pdf, alpha=0.4, color='gray',
                 label=f'Scrambled templates (N=1000)\n$\\langle A_{{\\rm sh}}\\rangle = {A_scr_mean:.3f} \\pm {A_scr_std:.3f}$')
ax2.axvline(A_correct, color='forestgreen', lw=2.5, ls='-', 
            label=f'Correct phase: $A_{{\\rm sh}} = {A_correct:.2f}$')

ax2.set_xlabel(r'$A_{\rm sh}$', fontsize=14)
ax2.set_ylabel('Probability density', fontsize=14)
ax2.set_title(r'(b) Phase coherence: $z = 10.5\sigma$', fontsize=14)
ax2.set_xlim(-0.6, 2.0)
ax2.legend(loc='upper right', fontsize=11)
ax2.set_ylim(bottom=0)

# Add arrow for correct phase
ax2.annotate('', xy=(A_correct, 0.3), xytext=(A_correct, 2.0),
            arrowprops=dict(arrowstyle='->', color='forestgreen', lw=2))

plt.tight_layout()
plt.savefig("figures/robustness_tests.pdf", dpi=300, bbox_inches='tight')
plt.savefig("figures/robustness_tests.png", dpi=150, bbox_inches='tight')
print("Saved figures/robustness_tests.pdf and .png")
