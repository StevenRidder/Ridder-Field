#!/usr/bin/env python3
"""
Quick A/B test: Compare r_s with and without α-branching
"""
import subprocess
import tempfile
import os

CLASS = "/Users/steveridder/Git/Ridder-Field/phase2/class/class"
OUTPUT_DIR = "/Users/steveridder/Git/Ridder-Field/phase2/class/output"

def run_class(name, alpha, gamma=0.0, Lambda=0.2):
    """Run CLASS and extract r_s at recombination."""
    
    ini = f"""
root = {OUTPUT_DIR}/{name}
write background = yes

h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
tau_reio = 0.0544

Lambda_EDE_ridder = {Lambda}
f_axion_ridder = 1.0e+27
theta_i_ridder = 1.0
n_ridder = 3
beta_ridder = 0.0

alpha_ridder_to_dr = {alpha}
z_ridder_decay = 3500
Gamma_decay_ridder = {gamma}

ridder_force_damping = 1.0
ridder_freeze_phi = no
use_ridder_shooting = 0

output = 
background_verbose = 0
gauge = newtonian
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(ini)
        ini_file = f.name
    
    try:
        result = subprocess.run([CLASS, ini_file], capture_output=True, text=True, timeout=120)
        
        # Read background file and get r_s near z=1100
        bg_file = f"{OUTPUT_DIR}/{name}00_background.dat"
        if os.path.exists(bg_file):
            with open(bg_file) as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.split()
                    z = float(parts[0])
                    if 1090 < z < 1110:
                        r_s = float(parts[7])  # Column 8 is sound horizon
                        return r_s
        
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        os.unlink(ini_file)


print("=" * 60)
print("SOUND HORIZON COMPARISON: α-branching effect")
print("=" * 60)
print()

# Run tests
results = {}

# Baseline: no decay
print("Running: α=0 (baseline)...")
results['alpha_0'] = run_class('cmp_alpha0', alpha=0.0)
print(f"  r_s(z≈1100) = {results['alpha_0']:.4f} Mpc" if results['alpha_0'] else "  FAILED")

# α = 0.3
print("Running: α=0.3...")
results['alpha_03'] = run_class('cmp_alpha03', alpha=0.3)
print(f"  r_s(z≈1100) = {results['alpha_03']:.4f} Mpc" if results['alpha_03'] else "  FAILED")

# α = 0.5
print("Running: α=0.5...")
results['alpha_05'] = run_class('cmp_alpha05', alpha=0.5)
print(f"  r_s(z≈1100) = {results['alpha_05']:.4f} Mpc" if results['alpha_05'] else "  FAILED")

# α = 1.0 (full conversion)
print("Running: α=1.0 (full conversion)...")
results['alpha_10'] = run_class('cmp_alpha10', alpha=1.0)
print(f"  r_s(z≈1100) = {results['alpha_10']:.4f} Mpc" if results['alpha_10'] else "  FAILED")

# Γ = 2.0 (kinetic friction)
print("Running: Γ=2.0 (kinetic friction)...")
results['gamma_2'] = run_class('cmp_gamma2', alpha=0.0, gamma=2.0)
print(f"  r_s(z≈1100) = {results['gamma_2']:.4f} Mpc" if results['gamma_2'] else "  FAILED")

# Γ = 4.0
print("Running: Γ=4.0...")
results['gamma_4'] = run_class('cmp_gamma4', alpha=0.0, gamma=4.0)
print(f"  r_s(z≈1100) = {results['gamma_4']:.4f} Mpc" if results['gamma_4'] else "  FAILED")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)

baseline = results.get('alpha_0')
if baseline:
    print(f"{'Config':<20} {'r_s (Mpc)':<15} {'Δr_s (Mpc)':<15} {'Δr_s/r_s':<10}")
    print("-" * 60)
    for name, r_s in results.items():
        if r_s:
            delta = r_s - baseline
            frac = delta / baseline * 100
            print(f"{name:<20} {r_s:<15.4f} {delta:<+15.4f} {frac:>+8.3f}%")

print()
print("INTERPRETATION:")
print("- Negative Δr_s → smaller sound horizon → higher inferred H₀")
print("- Need Δr_s/r_s ≈ -3% to get ΔH₀ ≈ +2 km/s/Mpc")

