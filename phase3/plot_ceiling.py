#!/usr/bin/env python3
"""Generate publication-quality ceiling figure."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os

def load_chain_simple(fname):
    """Load chain and get best chi2."""
    try:
        with open(fname, "r") as f:
            header = f.readline().strip()
        if header.startswith("#"):
            header = header[1:]
        cols = header.split()
        col_map = {c.strip(): i for i, c in enumerate(cols)}
        data = np.loadtxt(fname)
        if len(data.shape) == 1:
            data = data.reshape(1, -1)
        if len(data) == 0:
            return None
        best_idx = np.argmin(data[:, col_map["minuslogpost"]])
        return 2 * data[best_idx, col_map["minuslogpost"]]
    except:
        return None

# Load REF
ref_file = "chains/tier5_lcdm_shoes_desi.1.txt"
ref_chi2 = load_chain_simple(ref_file)
if not ref_chi2:
    print("ERROR: Could not load REF chain")
    sys.exit(1)

# Load all H0 values
h0_values = []
delta_chi2_values = []

for h0 in [68.5, 69, 69.5, 70, 70.5, 71, 71.5, 72]:
    chain_file = f"chains/tier5_ede_shoes_desi_h0_fixed_{h0}.1.txt"
    if not os.path.exists(chain_file):
        continue
    
    chi2 = load_chain_simple(chain_file)
    if chi2 is None:
        continue
    
    h0_values.append(h0)
    delta_chi2_values.append(chi2 - ref_chi2)

if len(h0_values) < 4:
    print(f"ERROR: Need at least 4 data points, found {len(h0_values)}")
    sys.exit(1)

h0_values = np.array(h0_values)
delta_chi2_values = np.array(delta_chi2_values)

# Sort by H0
sort_idx = np.argsort(h0_values)
h0_values = h0_values[sort_idx]
delta_chi2_values = delta_chi2_values[sort_idx]

# Interpolate for smooth curve
h0_interp = np.linspace(h0_values.min() - 0.2, h0_values.max() + 0.2, 200)
if len(h0_values) >= 4:
    f_interp = interp1d(h0_values, delta_chi2_values, kind='cubic', 
                        bounds_error=False, fill_value='extrapolate')
    delta_interp = f_interp(h0_interp)
else:
    f_interp = interp1d(h0_values, delta_chi2_values, kind='linear',
                        bounds_error=False, fill_value='extrapolate')
    delta_interp = f_interp(h0_interp)

# Create figure
fig, ax = plt.subplots(figsize=(12, 8))

# Plot interpolated curve
ax.plot(h0_interp, delta_interp, 'k-', lw=3, label='Combined constraint', zorder=5)

# Mark data points
ax.scatter(h0_values, delta_chi2_values, s=300, c='red', zorder=10,
           edgecolor='k', linewidth=2.5, label='MCMC results')

# Significance thresholds
ax.axhline(1, color='gray', ls='--', alpha=0.5, lw=1.5, label='1σ')
ax.axhline(4, color='gray', ls='--', alpha=0.5, lw=1.5, label='2σ')
ax.axhline(9, color='orange', ls='--', lw=2, label='3σ')
ax.axhline(25, color='red', ls='--', lw=2, label='5σ')

# Find ceiling (where delta_chi2 crosses 9 = 3σ)
ceiling_idx = np.where(delta_interp >= 9)[0]
if len(ceiling_idx) > 0:
    ceiling_h0 = h0_interp[ceiling_idx[0]]
    ax.axvline(ceiling_h0, color='blue', ls=':', lw=3, 
               label=f'Geometric ceiling (H₀ ≈ {ceiling_h0:.1f})', alpha=0.8)

# Mark external measurements
ax.axvspan(73.04 - 1.04, 73.04 + 1.04, alpha=0.2, color='green',
           label='SH0ES (unreachable)', zorder=1)
ax.axvspan(69.8 - 1.7, 69.8 + 1.7, alpha=0.2, color='cyan',
           label='JWST/TRGB', zorder=1)

# Labels
ax.set_xlabel('$H_0$ [km s$^{-1}$ Mpc$^{-1}$]', fontsize=18)
ax.set_ylabel('$\Delta\chi^2$ vs $\Lambda$CDM', fontsize=18)
ax.set_title('The Geometric Ceiling on $H_0$', fontsize=20, weight='bold')

ax.set_xlim(68, 73.5)
ax.set_ylim(-2, min(120, delta_chi2_values.max() * 1.1))

ax.legend(fontsize=12, loc='upper left', framealpha=0.9)
ax.grid(alpha=0.3, zorder=0)

# Annotate key points
if 69 in h0_values:
    idx = np.where(h0_values == 69)[0][0]
    ax.annotate('EDE optimum\n$H_0 = 69$ km/s/Mpc',
                xy=(69, delta_chi2_values[idx]), xytext=(68.2, 15),
                arrowprops=dict(arrowstyle='->', lw=2, color='blue'),
                fontsize=12, ha='center', color='blue')

if 70 in h0_values:
    idx = np.where(h0_values == 70)[0][0]
    ax.annotate('At ceiling\n$H_0 = 70$ km/s/Mpc\n$(3.8\sigma)$',
                xy=(70, delta_chi2_values[idx]), xytext=(70.3, 35),
                arrowprops=dict(arrowstyle='->', lw=2, color='red'),
                fontsize=12, ha='center', color='red')

if 72 in h0_values:
    idx = np.where(h0_values == 72)[0][0]
    ax.annotate('Strongly\nrejected',
                xy=(72, delta_chi2_values[idx]), xytext=(72.2, delta_chi2_values[idx] - 15),
                arrowprops=dict(arrowstyle='->', lw=2, color='red'),
                fontsize=12, ha='center', color='red')

plt.tight_layout()
plt.savefig('geometric_ceiling.pdf', dpi=300, bbox_inches='tight')
plt.savefig('geometric_ceiling.png', dpi=300, bbox_inches='tight')
print("Saved: geometric_ceiling.pdf and geometric_ceiling.png")
