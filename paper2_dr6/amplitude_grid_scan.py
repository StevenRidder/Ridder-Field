#!/usr/bin/env python3
"""
Amplitude Grid Scan: Test if radiation decay tolerates higher f_peak

THE KEY HYPOTHESIS:
- The data preferred f_peak ≈ 0.6% under "kinetic decay" physics (w≈1)
- With "radiation decay" (w=1/3, via α-branching), the data might tolerate f_peak ≈ 5-8%
- If so, we're back in business for H₀ ≈ 71 km/s/Mpc

WHAT THIS SCRIPT DOES:
1. Forces f_peak = 2%, 4%, 6%, 8%, 10% by varying Lambda_EDE_ridder
2. Runs with α=0 (no decay) and α=0.5 (maximal radiation branching)
3. Compares r_s, H₀, and χ² between the two cases
4. If χ² doesn't explode at higher f_peak with α=0.5, the "island" exists!

Author: Ridder EDE Analysis Pipeline
Date: December 2025
"""

import os
import sys
import numpy as np
import subprocess
import tempfile
from pathlib import Path

# Path to CLASS executable
CLASS_PATH = Path(__file__).parent.parent / "phase2" / "class" / "class"

def create_ini_file(
    Lambda_EDE_eV: float,
    alpha_ridder_to_dr: float = 0.0,
    z_ridder_decay: float = 3500.0,
    Gamma_decay_ridder: float = 0.0,
    output_dir: str = "output"
) -> str:
    """Create a CLASS .ini file for a given configuration."""
    
    ini_content = f"""
# ================================================
# Ridder EDE Amplitude Grid Scan Configuration
# ================================================
# Lambda_EDE = {Lambda_EDE_eV:.3e} eV
# alpha_ridder_to_dr = {alpha_ridder_to_dr}
# Gamma_decay_ridder = {Gamma_decay_ridder}
# ================================================

# Output
root = {output_dir}/ridder_test
write background = yes
write thermodynamics = yes

# Background parameters (Planck 2018 baseline)
h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
tau_reio = 0.0544

# Ridder field configuration
Lambda_EDE_ridder = {Lambda_EDE_eV}
f_axion_ridder = 1.0e+27
theta_i_ridder = 1.0
n_ridder = 3
beta_ridder = 0.0

# Dark radiation decay options
alpha_ridder_to_dr = {alpha_ridder_to_dr}
z_ridder_decay = {z_ridder_decay}
Gamma_decay_ridder = {Gamma_decay_ridder}

# Ridder control
ridder_force_damping = 1.0
ridder_freeze_phi = no
use_ridder_shooting = no

# Numerical precision
tol_background_integration = 1e-10
background_verbose = 1

# CMB settings (minimal for speed)
output = mPk
l_max_scalars = 2500
"""
    return ini_content


def run_class(ini_file: str) -> dict:
    """Run CLASS and parse the output."""
    
    result = subprocess.run(
        [str(CLASS_PATH), ini_file],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    output = result.stdout + result.stderr
    
    # Parse key quantities from output
    parsed = {
        'success': result.returncode == 0,
        'output': output,
        'rs_drag': None,
        'H0': None,
        'f_peak': None,
        'rho_ridder_max': None,
    }
    
    # Look for key quantities in output
    for line in output.split('\n'):
        if 'r_s(z_drag)' in line or 'rs_drag' in line:
            try:
                parsed['rs_drag'] = float(line.split('=')[-1].strip().split()[0])
            except:
                pass
        if 'H0' in line and 'km' in line:
            try:
                parsed['H0'] = float(line.split('=')[-1].strip().split()[0])
            except:
                pass
        if 'f_ridder_peak' in line or 'f_peak' in line:
            try:
                parsed['f_peak'] = float(line.split('=')[-1].strip().split()[0])
            except:
                pass
        if 'rho_ridder_max' in line:
            try:
                parsed['rho_ridder_max'] = float(line.split('=')[-1].strip().split()[0])
            except:
                pass
    
    return parsed


def estimate_Lambda_for_fpeak(target_fpeak: float) -> float:
    """
    Rough estimate of Lambda_EDE needed for a given f_peak.
    
    Based on scaling: f_peak ∝ Lambda^4 / (3 M_Pl^2 H^2)
    At z~3500, H ~ 10^-28 eV, M_Pl ~ 2.4×10^27 eV
    
    For f_peak = 0.1 (10%), we need roughly Lambda ~ 10^13 eV
    This is a rough starting point; actual calibration needed.
    """
    # Calibration from existing runs:
    # Lambda = 0.2 eV → f_peak ~ 0.006 (0.6%)
    # We want: Lambda such that f_peak = target_fpeak
    
    # Rough scaling: f_peak ∝ Lambda^4
    # So Lambda_new / Lambda_ref = (f_new / f_ref)^(1/4)
    
    Lambda_ref = 0.2  # eV (from previous tests)
    f_ref = 0.006     # 0.6%
    
    Lambda_new = Lambda_ref * (target_fpeak / f_ref) ** 0.25
    
    return Lambda_new


def run_amplitude_grid():
    """Main grid scan: test f_peak = 2%, 4%, 6%, 8%, 10%."""
    
    print("=" * 70)
    print("RIDDER EDE AMPLITUDE GRID SCAN")
    print("Testing if radiation decay (α-branching) tolerates higher f_peak")
    print("=" * 70)
    print()
    
    # Target f_peak values
    target_fpeaks = [0.02, 0.04, 0.06, 0.08, 0.10]  # 2%, 4%, 6%, 8%, 10%
    
    # Decay configurations to test
    decay_configs = [
        {'name': 'No decay (α=0)', 'alpha': 0.0, 'Gamma': 0.0},
        {'name': 'α-branch (α=0.5)', 'alpha': 0.5, 'Gamma': 0.0},
        {'name': 'α-branch (α=1.0)', 'alpha': 1.0, 'Gamma': 0.0},
        {'name': 'Γ-decay (Γ=2)', 'alpha': 0.0, 'Gamma': 2.0},
        {'name': 'Γ-decay (Γ=4)', 'alpha': 0.0, 'Gamma': 4.0},
    ]
    
    results = []
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        
        for target_f in target_fpeaks:
            Lambda_est = estimate_Lambda_for_fpeak(target_f)
            
            print(f"\n{'='*60}")
            print(f"Target f_peak = {target_f*100:.0f}%")
            print(f"Estimated Lambda_EDE = {Lambda_est:.3e} eV")
            print(f"{'='*60}")
            
            for config in decay_configs:
                print(f"\n  Testing: {config['name']}...")
                
                # Create ini file
                ini_content = create_ini_file(
                    Lambda_EDE_eV=Lambda_est,
                    alpha_ridder_to_dr=config['alpha'],
                    Gamma_decay_ridder=config['Gamma'],
                    output_dir=str(output_dir)
                )
                
                ini_file = output_dir / f"test_{target_f}_{config['name'].replace(' ', '_')}.ini"
                ini_file.write_text(ini_content)
                
                # Run CLASS
                try:
                    result = run_class(str(ini_file))
                    
                    row = {
                        'target_fpeak': target_f,
                        'Lambda_EDE': Lambda_est,
                        'config': config['name'],
                        'alpha': config['alpha'],
                        'Gamma': config['Gamma'],
                        'success': result['success'],
                        'rs_drag': result.get('rs_drag'),
                        'H0': result.get('H0'),
                        'f_peak_actual': result.get('f_peak'),
                    }
                    results.append(row)
                    
                    status = "✓" if result['success'] else "✗"
                    rs = result.get('rs_drag', '?')
                    H0 = result.get('H0', '?')
                    print(f"    {status} rs_drag={rs}, H0={H0}")
                    
                except Exception as e:
                    print(f"    ✗ Error: {e}")
                    results.append({
                        'target_fpeak': target_f,
                        'Lambda_EDE': Lambda_est,
                        'config': config['name'],
                        'alpha': config['alpha'],
                        'Gamma': config['Gamma'],
                        'success': False,
                        'error': str(e)
                    })
    
    # Print summary table
    print("\n" + "=" * 80)
    print("SUMMARY: Amplitude Grid Scan Results")
    print("=" * 80)
    print(f"{'f_peak':>8} {'Config':>20} {'rs_drag':>10} {'H0':>10} {'Status':>8}")
    print("-" * 80)
    
    for row in results:
        f = row.get('target_fpeak', 0) * 100
        cfg = row.get('config', '?')[:20]
        rs = row.get('rs_drag', '?')
        H0 = row.get('H0', '?')
        status = '✓' if row.get('success') else '✗'
        
        rs_str = f"{rs:.2f}" if isinstance(rs, (int, float)) else str(rs)
        H0_str = f"{H0:.2f}" if isinstance(H0, (int, float)) else str(H0)
        
        print(f"{f:>7.0f}% {cfg:>20} {rs_str:>10} {H0_str:>10} {status:>8}")
    
    print("=" * 80)
    print()
    print("KEY QUESTION: Does χ² explode at f_peak=8-10% with α-branching?")
    print("If NOT → the 'island' exists and we can push H₀ toward 71!")
    print()
    
    return results


if __name__ == "__main__":
    # Check if CLASS exists
    if not CLASS_PATH.exists():
        print(f"ERROR: CLASS not found at {CLASS_PATH}")
        print("Please compile CLASS first: cd phase2/class && make")
        sys.exit(1)
    
    results = run_amplitude_grid()

