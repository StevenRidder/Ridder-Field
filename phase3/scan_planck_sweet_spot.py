#!/usr/bin/env python3
"""
Quick scan to find EDE parameters that minimize Planck penalty.
Uses the current converged chains to map parameter space.
"""
import numpy as np
import os

CHAIN_DIR = os.path.expanduser("~/Ridder-Field/phase3/chains")

def load_chain_full(chain_file):
    """Load full chain with all columns"""
    with open(chain_file, "r") as f:
        header = f.readline().strip()
    if header.startswith("#"):
        header = header[1:]
    cols = header.split()
    col_map = {c.strip(): i for i, c in enumerate(cols)}
    
    data = np.loadtxt(chain_file)
    if len(data.shape) == 1:
        data = data.reshape(1, -1)
    
    return cols, col_map, data

# Load the EDE chain
ede_file = f"{CHAIN_DIR}/tier5_ede_desi_convergence.1.txt"
lcdm_file = f"{CHAIN_DIR}/tier5_lcdm_desi_unconstrained.1.txt"

if not os.path.exists(ede_file):
    print("EDE chain not found")
    exit(1)

cols, col_map, ede_data = load_chain_full(ede_file)
_, lcdm_col_map, lcdm_data = load_chain_full(lcdm_file)

# Get LCDM reference chi2
lcdm_best_idx = np.argmin(lcdm_data[:, lcdm_col_map["chi2"]])
lcdm_planck_hl = lcdm_data[lcdm_best_idx, lcdm_col_map["chi2__planck_2018_highl_plik.TTTEEE"]]
lcdm_chi2 = lcdm_data[lcdm_best_idx, lcdm_col_map["chi2"]]

print("="*90)
print("PARAMETER SCAN: Finding Planck-friendly EDE sweet spot")
print("="*90)
print(f"\nLΛCDM reference: Planck high-l χ² = {lcdm_planck_hl:.1f}, total χ² = {lcdm_chi2:.1f}")
print(f"\nEDE chain has {len(ede_data)} samples")

# Check if we have EDE parameters
if "theta_i_ridder" in col_map:
    theta_i = ede_data[:, col_map["theta_i_ridder"]]
    print(f"   theta_i_ridder range: {theta_i.min():.3f} - {theta_i.max():.3f}")
else:
    print("   theta_i_ridder not found in chain")
    theta_i = None

if "beta_ridder" in col_map:
    beta = ede_data[:, col_map["beta_ridder"]]
    print(f"   beta_ridder range: {beta.min():.3f} - {beta.max():.3f}")
else:
    print("   beta_ridder not found in chain")
    beta = None

# Extract key quantities
H0 = ede_data[:, col_map["H0"]]
rs = ede_data[:, col_map["rs_drag"]]
chi2_total = ede_data[:, col_map["chi2"]]
chi2_planck_hl = ede_data[:, col_map["chi2__planck_2018_highl_plik.TTTEEE"]]
chi2_desi = ede_data[:, col_map["chi2__likelihoods.desi_y1_bao.DESI_Y1_BAO"]]

# Compute deltas
delta_chi2_total = chi2_total - lcdm_chi2
delta_chi2_planck = chi2_planck_hl - lcdm_planck_hl

print(f"\n{'='*90}")
print("CORRELATION ANALYSIS")
print("="*90)

# Find samples with best Planck fit
best_planck_idx = np.argsort(chi2_planck_hl)[:10]
worst_planck_idx = np.argsort(chi2_planck_hl)[-10:]

print(f"\n10 BEST Planck samples:")
print(f"{'idx':>5} {'H0':>7} {'r_s':>7} {'Δχ²_Pl':>8} {'Δχ²_tot':>9} {'χ²_DESI':>8}")
print("-"*50)
for idx in best_planck_idx:
    print(f"{idx:>5} {H0[idx]:>7.2f} {rs[idx]:>7.1f} {delta_chi2_planck[idx]:>+8.1f} {delta_chi2_total[idx]:>+9.1f} {chi2_desi[idx]:>8.1f}")

print(f"\n10 WORST Planck samples:")
print(f"{'idx':>5} {'H0':>7} {'r_s':>7} {'Δχ²_Pl':>8} {'Δχ²_tot':>9} {'χ²_DESI':>8}")
print("-"*50)
for idx in worst_planck_idx:
    print(f"{idx:>5} {H0[idx]:>7.2f} {rs[idx]:>7.1f} {delta_chi2_planck[idx]:>+8.1f} {delta_chi2_total[idx]:>+9.1f} {chi2_desi[idx]:>8.1f}")

# Correlation between r_s shift and Planck penalty
rs_shift = (rs - 147.3) / 147.3 * 100  # percent shift from Planck value
corr_rs_planck = np.corrcoef(rs_shift, delta_chi2_planck)[0, 1]

print(f"\n{'='*90}")
print("KEY CORRELATIONS")
print("="*90)
print(f"Correlation(r_s shift, Δχ²_Planck) = {corr_rs_planck:.3f}")
print(f"Correlation(H0, Δχ²_Planck) = {np.corrcoef(H0, delta_chi2_planck)[0, 1]:.3f}")

# Find the "Pareto frontier" - best tradeoff between H0 and Δχ²
print(f"\n{'='*90}")
print("PARETO FRONTIER: Best H0 at each Δχ² level")
print("="*90)

chi2_bins = [20, 40, 60, 80, 100, 150, 200]
print(f"{'Δχ² < X':>10} {'Best H0':>8} {'at r_s':>8} {'actual Δχ²':>12}")
print("-"*45)

for threshold in chi2_bins:
    mask = delta_chi2_total < threshold
    if mask.sum() > 0:
        best_H0_idx = np.argmax(H0[mask])
        actual_idx = np.where(mask)[0][best_H0_idx]
        print(f"{'<'+str(threshold):>10} {H0[actual_idx]:>8.2f} {rs[actual_idx]:>8.1f} {delta_chi2_total[actual_idx]:>+12.1f}")
    else:
        print(f"{'<'+str(threshold):>10} {'---':>8} {'---':>8} {'no samples':>12}")

print(f"\n{'='*90}")
print("VERDICT")
print("="*90)

# Best achievable
best_total_idx = np.argmin(chi2_total)
print(f"\nBest total χ²: Δχ² = {delta_chi2_total[best_total_idx]:+.1f} at H0 = {H0[best_total_idx]:.2f}, r_s = {rs[best_total_idx]:.1f}")

# Best H0 with reasonable penalty
reasonable_mask = delta_chi2_total < 50
if reasonable_mask.sum() > 0:
    best_H0_reasonable = np.argmax(H0[reasonable_mask])
    idx = np.where(reasonable_mask)[0][best_H0_reasonable]
    print(f"Best H0 with Δχ² < 50: H0 = {H0[idx]:.2f} at Δχ² = {delta_chi2_total[idx]:+.1f}")
else:
    print("No samples with Δχ² < 50 found - Planck penalty is fundamental")

min_penalty = delta_chi2_total.min()
print(f"\nMinimum achievable Δχ² in current chain: {min_penalty:+.1f}")
if min_penalty > 50:
    print("⚠️  Even the best EDE sample has Δχ² > 50 - this is likely a fundamental Planck limit")
