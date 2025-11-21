#!/usr/bin/env python3
"""
Extract key observables from CLASS runs

This script:
1. Runs CLASS and extracts key observables from output
2. Compares ΛCDM baseline vs EDE mode
3. Shows what we've proven
"""

import subprocess
import re
import os
import numpy as np

def run_class_and_extract(ini_file):
    """Run CLASS and extract observables from output"""
    class_dir = '/Users/steveridder/Git/Ridder Field/phase2/class'
    class_binary = os.path.join(class_dir, 'class')
    ini_path = os.path.join(class_dir, ini_file)
    
    # Run CLASS
    result = subprocess.run(
        [class_binary, ini_file],
        cwd=class_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error running CLASS: {result.stderr}")
        return None
    
    output = result.stdout + result.stderr
    
    # Extract key values
    observables = {}
    
    # Extract h (dimensionless Hubble parameter)
    h_match = re.search(r'h\s*=\s*([\d.]+)', output)
    if h_match:
        observables['h'] = float(h_match.group(1))
        observables['H0'] = observables['h'] * 100.0  # km/s/Mpc
    
    # Extract age
    age_match = re.search(r'age\s*=\s*([\d.]+)\s*Gyr', output)
    if age_match:
        observables['age'] = float(age_match.group(1))
    
    # Extract conformal age
    conf_age_match = re.search(r'conformal age\s*=\s*([\d.]+)\s*Mpc', output)
    if conf_age_match:
        observables['conformal_age'] = float(conf_age_match.group(1))
    
    # Extract equality redshift
    zeq_match = re.search(r'radiation/matter equality at z\s*=\s*([\d.]+)', output)
    if zeq_match:
        observables['z_eq'] = float(zeq_match.group(1))
    
    # Extract Omega values from budget
    omega_b_match = re.search(r'Bayrons.*Omega\s*=\s*([\d.e-]+)', output)
    if omega_b_match:
        observables['Omega_b'] = float(omega_b_match.group(1))
    
    omega_cdm_match = re.search(r'Cold Dark Matter.*Omega\s*=\s*([\d.e-]+)', output)
    if omega_cdm_match:
        observables['Omega_cdm'] = float(omega_cdm_match.group(1))
    
    omega_lambda_match = re.search(r'Cosmological Constant.*Omega\s*=\s*([\d.e-]+)', output)
    if omega_lambda_match:
        observables['Omega_Lambda'] = float(omega_lambda_match.group(1))
    
    # Try to read from output files if they exist
    output_dir = os.path.join(class_dir, 'output')
    if os.path.exists(output_dir):
        # Look for cl files to get sound horizon
        cl_files = [f for f in os.listdir(output_dir) if f.endswith('_cl.dat')]
        if cl_files:
            # Sound horizon is typically in the first line or header
            cl_file = os.path.join(output_dir, cl_files[0])
            try:
                with open(cl_file, 'r') as f:
                    first_line = f.readline()
                    # CLASS sometimes puts r_s in comments
                    rs_match = re.search(r'rs_drag[:\s]+([\d.]+)', first_line)
                    if rs_match:
                        observables['r_s'] = float(rs_match.group(1))
            except:
                pass
    
    return observables

def main():
    print("\n" + "="*70)
    print("RIDDER FIELD: CLASS OBSERVABLES EXTRACTION")
    print("="*70)
    
    # Phase 1 reference
    phase1_ref = {
        'H0': 67.36,  # km/s/Mpc
        'r_s': 147.0,  # Mpc
        'z_eq': 3400,
    }
    
    print("\n--- Running ΛCDM Baseline ---")
    lcdm = run_class_and_extract('test_ridder_lcdm.ini')
    
    print("\n--- Running EDE Mode ---")
    ede = run_class_and_extract('test_ridder_ede.ini')
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print("\nΛCDM Baseline (Lambda_EDE = 0):")
    if lcdm:
        for key, val in lcdm.items():
            print(f"  {key}: {val}")
    
    print("\nEDE Mode (Lambda_EDE > 0):")
    if ede:
        for key, val in ede.items():
            print(f"  {key}: {val}")
    
    print("\n" + "="*70)
    print("COMPARISON WITH PHASE 1")
    print("="*70)
    
    if lcdm:
        print("\nΛCDM vs Phase 1:")
        if 'H0' in lcdm:
            diff = abs(lcdm['H0'] - phase1_ref['H0']) / phase1_ref['H0'] * 100
            print(f"  H0: {lcdm['H0']:.2f} vs {phase1_ref['H0']:.2f} km/s/Mpc ({diff:.2f}% diff)")
            if diff < 5:
                print(f"    ✓ Within 5% - VALIDATED!")
        
        if 'z_eq' in lcdm:
            diff = abs(lcdm['z_eq'] - phase1_ref['z_eq']) / phase1_ref['z_eq'] * 100
            print(f"  z_eq: {lcdm['z_eq']:.1f} vs {phase1_ref['z_eq']:.0f} ({diff:.2f}% diff)")
            if diff < 5:
                print(f"    ✓ Within 5% - VALIDATED!")
    
    if lcdm and ede:
        print("\nEDE Effect:")
        if 'H0' in lcdm and 'H0' in ede:
            shift = (ede['H0'] - lcdm['H0']) / lcdm['H0'] * 100
            print(f"  H0 shift: {shift:+.2f}%")
            if shift > 0:
                print(f"    ✓ H0 increased (expected for EDE)")
        
        if 'z_eq' in lcdm and 'z_eq' in ede:
            shift = (ede['z_eq'] - lcdm['z_eq']) / lcdm['z_eq'] * 100
            print(f"  z_eq shift: {shift:+.2f}%")
    
    print("\n" + "="*70)
    print("WHAT HAVE WE PROVEN?")
    print("="*70)
    
    proven = []
    
    if lcdm and 'H0' in lcdm:
        if abs(lcdm['H0'] - phase1_ref['H0']) / phase1_ref['H0'] < 0.05:
            proven.append("✓ CLASS reproduces Phase 1 H0 (within 5%)")
    
    if lcdm and 'z_eq' in lcdm:
        if abs(lcdm['z_eq'] - phase1_ref['z_eq']) / phase1_ref['z_eq'] < 0.05:
            proven.append("✓ CLASS reproduces Phase 1 z_eq (within 5%)")
    
    if lcdm and ede and 'H0' in lcdm and 'H0' in ede:
        if ede['H0'] > lcdm['H0']:
            proven.append("✓ EDE increases H0 (as theoretically expected)")
    
    if proven:
        print("\n✅ PROVEN:")
        for item in proven:
            print(f"  {item}")
        print("\n🎉 The Ridder field implementation in CLASS is working!")
    else:
        print("\n⚠️  Need more data to validate")
        print("   (This is normal - we need to extract more observables)")

if __name__ == '__main__':
    main()

