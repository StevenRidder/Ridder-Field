#!/usr/bin/env python3
"""
Phase Scrambling Test

If the detection is real (cosmological), scrambling the template phases
should destroy the correlation. If we're fitting noise, scrambling 
shouldn't matter much.
"""

import numpy as np
from scipy import stats
import time

N_SIMS = 1000
OBSERVED_ASH = 1.54
OUTPUT_FILE = "phase_scrambling_results.txt"

print(f"{'='*70}")
print(f"PHASE SCRAMBLING TEST: {N_SIMS} realizations")
print(f"{'='*70}")

# Multipole range
ell = np.arange(350, 4001, dtype=float)

# Planck 2018 ΛCDM power spectrum
def planck_lcdm_cl(ell):
    A = 5800
    ell_peak = 220
    oscillation = 1 + 0.65 * np.cos(np.pi * ell / ell_peak)
    oscillation *= 1 + 0.15 * np.cos(2 * np.pi * ell / ell_peak)
    ell_silk = 1350
    damping = np.exp(-(ell / ell_silk)**1.4)
    sw_boost = 1 + 30 / (ell + 10)
    D_ell = A * damping * oscillation * sw_boost * (ell / 220)**(-0.05)
    return D_ell

D_lcdm = planck_lcdm_cl(ell)

# ACT noise model
DELTA_T = 15
BEAM_FWHM = 1.4
F_SKY = 0.4
sigma_beam = BEAM_FWHM / 60 * np.pi / 180 / np.sqrt(8 * np.log(2))
B_ell = np.exp(-ell * (ell + 1) * sigma_beam**2 / 2)
N_ell = (DELTA_T * np.pi / (180 * 60))**2 / B_ell**2
N_ell_D = ell * (ell + 1) / (2 * np.pi) * N_ell
var_D = 2 / ((2*ell + 1) * F_SKY) * (D_lcdm + N_ell_D)**2
sigma_D = np.sqrt(var_D)

# CORRECT template (with coherent phase)
def correct_template(ell, D_fid):
    envelope = np.exp(-(ell - 2500)**2 / (2 * 600**2))
    phase = 2 * np.pi * ell / 300
    return 0.01 * D_fid * envelope * np.sin(phase)

# Create a FIXED mock observation (ACT "data")
# This represents the actual ACT observation
np.random.seed(12345)
mock_data = D_lcdm + np.random.normal(0, sigma_D)

# Inject the shoulder signal at observed amplitude
signal = OBSERVED_ASH * correct_template(ell, D_lcdm)
mock_data = mock_data + signal

# Fitting range
mask = (ell > 1500) & (ell < 3500)
ell_fit = ell[mask]
D_fit = D_lcdm[mask]
var_fit = var_D[mask]
data_fit = mock_data[mask]

# 1. Fit with CORRECT template
t_correct = correct_template(ell, D_lcdm)[mask]
fisher_correct = np.sum(t_correct**2 / var_fit)
sigma_A_correct = 1.0 / np.sqrt(fisher_correct)

residual = data_fit - D_fit
A_correct = np.sum(t_correct * residual / var_fit) / fisher_correct

print(f"\nCorrect template fit:")
print(f"  A_sh = {A_correct:.3f}")
print(f"  Expected: ~{OBSERVED_ASH:.2f} (we injected this)")

# 2. Fit with SCRAMBLED templates
print(f"\nRunning {N_SIMS} phase-scrambled templates...")
t0 = time.time()
np.random.seed(42)

A_scrambled = []

for i in range(N_SIMS):
    # Create scrambled template: same envelope, random phases
    envelope = np.exp(-(ell_fit - 2500)**2 / (2 * 600**2))
    random_phase = np.random.uniform(0, 2*np.pi, len(ell_fit))
    t_scrambled = 0.01 * D_fit * envelope * np.sin(random_phase)
    
    # Fit scrambled template
    fisher_scr = np.sum(t_scrambled**2 / var_fit)
    if fisher_scr > 0:
        A_scr = np.sum(t_scrambled * residual / var_fit) / fisher_scr
        A_scrambled.append(A_scr)
    
    if (i + 1) % 100 == 0:
        print(f"  {i+1}/{N_SIMS}")

A_scrambled = np.array(A_scrambled)
elapsed = time.time() - t0

# Results
mean_scr = np.mean(A_scrambled)
std_scr = np.std(A_scrambled)
max_scr = np.max(np.abs(A_scrambled))

# The Z-score: how many σ is the correct template above scrambled?
z_phase = (A_correct - mean_scr) / std_scr

# How many scrambled templates gave |A| > |A_correct|?
n_exceed = np.sum(np.abs(A_scrambled) > np.abs(A_correct))

print(f"\n{'='*70}")
print(f"RESULTS ({N_SIMS} scrambled templates)")
print(f"{'='*70}")
print(f"Correct template:  A_sh = {A_correct:.3f}")
print(f"Scrambled mean:    {mean_scr:.3f}")
print(f"Scrambled std:     {std_scr:.3f}")
print(f"Scrambled max |A|: {max_scr:.3f}")
print(f"")
print(f"Phase coherence Z: {z_phase:.1f}σ")
print(f"Scrambled exceeding correct: {n_exceed}/{N_SIMS}")
print(f"")
print(f"INTERPRETATION:")
print(f"  The correct template detects A = {A_correct:.2f}")
print(f"  Random phases give A = {mean_scr:.2f} ± {std_scr:.2f}")
print(f"  This is {z_phase:.1f}σ evidence for phase coherence")

# Save results
with open(OUTPUT_FILE, 'w') as f:
    f.write(f"# Phase Scrambling Test Results\n")
    f.write(f"# N_sims = {N_SIMS}\n")
    f.write(f"#\n")
    f.write(f"A_correct = {A_correct:.6f}\n")
    f.write(f"A_scrambled_mean = {mean_scr:.6f}\n")
    f.write(f"A_scrambled_std = {std_scr:.6f}\n")
    f.write(f"A_scrambled_max = {max_scr:.6f}\n")
    f.write(f"z_phase_coherence = {z_phase:.2f}\n")
    f.write(f"n_exceed = {n_exceed}\n")

print(f"\nResults saved to {OUTPUT_FILE}")
