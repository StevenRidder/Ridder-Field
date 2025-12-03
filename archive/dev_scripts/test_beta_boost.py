#!/usr/bin/env python3
"""
Quick A/B test: Does the radiation boost pattern change r_s and H0?
"""

import subprocess
import numpy as np
import os

def run_class_quick(beta_val):
    """Run CLASS with given beta, return r_s."""
    ini_content = f"""# Quick beta boost test
H0 = 67.36
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544

Lambda_EDE_ridder = 1.5
f_axion_ridder = 2.435e27
theta_i_ridder = 1.0
beta_ridder = {beta_val}
n_ridder = 3
ridder_c_slow = 1.0
ridder_freeze_phi = no
ridder_force_damping = 1.0

gauge = newtonian
write background = yes
root = output/beta_test_{beta_val}_
"""
    
    ini_file = f"beta_test_{beta_val}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini_content)
    
    result = subprocess.run(
        ['./phase2/class/class', ini_file],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode != 0:
        print(f"❌ Failed for beta={beta_val}")
        print(f"   Error: {result.stderr[:200]}")
        return None
    
    # Extract r_s from background file
    import glob
    bg_files = glob.glob(f"output/beta_test_{beta_val}_*_background.dat")
    if not bg_files:
        print(f"❌ No background file for beta={beta_val}")
        return None
    
    data = np.loadtxt(bg_files[0])
    z = data[:, 0]
    rs = data[:, 7]
    
    # r_s at z_drag ~ 1060
    idx_drag = np.argmin(np.abs(z - 1060.0))
    rs_drag = rs[idx_drag]
    
    return rs_drag, bg_files[0]

print("="*70)
print("BETA BOOST A/B TEST")
print("="*70)
print("Goal: Verify radiation boost changes r_s(z_drag)")
print()

# Reference
rs_lcdm = 147.079129
h0_input = 67.36

results = []

for beta in [0.0, 0.05]:
    print(f"▶ beta = {beta:.2f}")
    
    result = run_class_quick(beta)
    if result is None:
        print("  ❌ Skipping")
        print()
        continue
    
    rs_drag, bg_file = result
    
    delta_rs_pct = (rs_drag - rs_lcdm) / rs_lcdm * 100
    h0_eff = h0_input * (rs_lcdm / rs_drag)
    delta_h0 = h0_eff - h0_input
    
    print(f"  r_s(z_drag) = {rs_drag:.6f} Mpc")
    print(f"  Δr_s/r_s    = {delta_rs_pct:+.3f}%")
    print(f"  H₀^eff      = {h0_eff:.4f} km/s/Mpc")
    print(f"  ΔH₀         = {delta_h0:+.4f} km/s/Mpc")
    print()
    
    results.append({'beta': beta, 'rs': rs_drag, 'h0_eff': h0_eff, 'delta_h0': delta_h0})

print("="*70)
print("COMPARISON")
print("="*70)

if len(results) == 2:
    delta_rs_abs = results[1]['rs'] - results[0]['rs']
    delta_rs_pct = (delta_rs_abs / results[0]['rs']) * 100
    delta_h0_boost = results[1]['delta_h0'] - results[0]['delta_h0']
    
    print(f"Δr_s (beta=0.05 vs 0.0):  {delta_rs_abs:+.6f} Mpc ({delta_rs_pct:+.3f}%)")
    print(f"ΔH₀ boost from beta:      {delta_h0_boost:+.4f} km/s/Mpc")
    print()
    
    if abs(delta_rs_pct) > 0.1:
        print("✅ SUCCESS: Beta boost changes r_s significantly!")
        print(f"   The radiation boost pattern is working.")
        print(f"   Beta gives {delta_h0_boost:+.2f} km/s/Mpc additional shift.")
    else:
        print("❌ LIMITED: Beta boost too small to matter")
        print(f"   r_s changes by only {delta_rs_pct:.3f}%")

print("="*70)

