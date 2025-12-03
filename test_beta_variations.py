#!/usr/bin/env python3
"""
Test different beta configurations:
1. Wider boost (sigma_z = 0.6)
2. Larger amplitude (beta = 0.2, 0.5)
3. Different peak location (z_c = 1500, closer to drag)
"""

import subprocess
import numpy as np

def test_beta_config(beta_val, sigma_z=0.3, z_c=3276):
    """Test a specific beta configuration."""
    # Need to modify background.c for each config
    # For now, just test different beta amplitudes
    
    ini_content = f"""# Beta variation test
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
root = output/beta_var_{beta_val}_
"""
    
    ini_file = f"beta_var_{beta_val}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini_content)
    
    result = subprocess.run(
        ['./phase2/class/class', ini_file],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode != 0:
        return None
    
    # Extract r_s
    import glob
    bg_files = glob.glob(f"output/beta_var_{beta_val}_*_background.dat")
    if not bg_files:
        return None
    
    data = np.loadtxt(bg_files[0])
    z = data[:, 0]
    rs = data[:, 7]
    
    idx_drag = np.argmin(np.abs(z - 1060.0))
    return rs[idx_drag]

print("="*70)
print("BETA AMPLITUDE SCAN")
print("="*70)
print("Goal: Test if larger beta gives proportional r_s shift")
print()

rs_lcdm = 147.079129
h0_input = 67.36

beta_values = [0.0, 0.05, 0.10, 0.20, 0.50]

results = []

for beta in beta_values:
    print(f"▶ beta = {beta:.2f}")
    
    rs_drag = test_beta_config(beta)
    
    if rs_drag is None:
        print("  ❌ Failed")
        continue
    
    delta_rs_pct = (rs_drag - rs_lcdm) / rs_lcdm * 100
    h0_eff = h0_input * (rs_lcdm / rs_drag)
    delta_h0 = h0_eff - h0_input
    
    print(f"  r_s      = {rs_drag:.6f} Mpc")
    print(f"  Δr_s/r_s = {delta_rs_pct:+.3f}%")
    print(f"  ΔH₀      = {delta_h0:+.4f} km/s/Mpc")
    print()
    
    results.append({'beta': beta, 'rs': rs_drag, 'delta_h0': delta_h0})

print("="*70)
print("SCALING ANALYSIS")
print("="*70)

if len(results) >= 2:
    baseline = results[0]
    
    print(f"{'beta':<8} {'Δr_s/r_s':<12} {'ΔH₀ total':<15} {'ΔH₀ from beta':<15}")
    print("-"*70)
    
    for r in results:
        delta_rs_pct = (r['rs'] - rs_lcdm) / rs_lcdm * 100
        delta_h0_from_beta = r['delta_h0'] - baseline['delta_h0']
        
        print(f"{r['beta']:<8.2f} {delta_rs_pct:>+11.3f}% {r['delta_h0']:>+14.4f} {delta_h0_from_beta:>+14.4f}")
    
    print()
    print("CONCLUSION:")
    
    if len(results) >= 3:
        # Check if effect scales
        beta_ratio = results[2]['beta'] / results[1]['beta']
        effect_ratio = (results[2]['delta_h0'] - baseline['delta_h0']) / (results[1]['delta_h0'] - baseline['delta_h0'])
        
        print(f"  Beta ratio (0.10/0.05): {beta_ratio:.1f}×")
        print(f"  Effect ratio:           {effect_ratio:.1f}×")
        
        if abs(effect_ratio - beta_ratio) < 0.2:
            print("  ✅ Effect scales linearly with beta")
        else:
            print("  ⚠️  Non-linear scaling")
        
        # Check maximum achievable
        if len(results) >= 4:
            max_beta = results[-1]['beta']
            max_boost = results[-1]['delta_h0'] - baseline['delta_h0']
            
            print()
            print(f"  Maximum tested: beta={max_beta}, boost={max_boost:+.2f} km/s/Mpc")
            
            if max_boost < 0.5:
                print("  ❌ Even at high beta, boost is < 0.5 km/s/Mpc")
                print("     Radiation boost pattern has limited leverage on r_s.")
            elif max_boost >= 1.0:
                print("  ✅ At high beta, boost ≥ 1.0 km/s/Mpc - worth exploring!")
            else:
                print("  ⚠️  Modest boost (0.5-1.0 km/s/Mpc) - marginal improvement")

print("="*70)

