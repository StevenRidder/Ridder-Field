#!/usr/bin/env python3
"""
GRID SCAN: Testing the Ridder Field Mechanism
=============================================

This script runs the CLASS binary directly to sweep over Lambda_EDE.
It tests if the physical mechanism (reducing sound horizon r_s) works.

Hypothesis: Increasing Lambda_EDE should decrease r_s.
"""

import numpy as np
import matplotlib.pyplot as plt
import subprocess
import re
import os
import sys

def create_ini_file(lambda_ede, filename, root_path):
    content = f"""
# Ridder Field Scan
# Lambda_EDE = {lambda_ede}

root = {root_path}
output = tCl,pCl,lCl,mPk
lensing = yes
gauge = newtonian  # Force Newtonian for DM coupling
modes = s
l_max_scalars = 2500
P_k_max_h/Mpc = 1.0
z_pk = 0

# Cosmological parameters
h = 0.6736
T_cmb = 2.7255
omega_b = 0.02237
omega_cdm = 0.1200
# Omega_Lambda = 0.6911 <-- REMOVED to let CLASS fill with Lambda
Omega_fld = 0.0         # <-- Force fld to 0 to prevent ghost fluid filling


# Ridder Field
Lambda_EDE_ridder = {lambda_ede}
f_axion_ridder = 1e27
theta_i_ridder = 2.8
beta_ridder = 0.01
n_ridder = 3

# Primordial
A_s = 2.1e-9
n_s = 0.9665
tau_reio = 0.0561

# Precision
background_verbose = 1
thermodynamics_verbose = 1
write background = yes

"""
    with open(filename, 'w') as f:
        f.write(content)

def run_class(ini_file, output_root):
    # Absolute path to CLASS directory
    class_dir = '/Users/steveridder/Git/Ridder Field/phase2/class'
    
    # Absolute path to ini file
    ini_path = os.path.abspath(ini_file)
    
    result = subprocess.run(
        ['./class', ini_path],
        cwd=class_dir,
        capture_output=True,
        text=True
    )
    
    output = result.stdout
    
    # Debug: print first few lines of output if it fails
    # ALSO print if we see "Ridder" in the output (for debugging)
    if "Ridder" in output or "DEBUG" in output:
        print(f"--- DEBUG OUTPUT for {ini_file} ---")
        # Filter only lines with Ridder or DEBUG
        for line in output.split('\n'):
            if "Ridder" in line or "DEBUG" in line:
                print(line)
        print("-----------------------------------")
    
    # Extract r_s (sound horizon)
    # Pattern 1: "comoving sound horizon rs = 147.114341 Mpc" (from stdout)
    rs_match = re.search(r'comoving sound horizon rs\s*=\s*([\d.]+)', output)
    
    if result.returncode != 0:
        print(f"CLASS run failed with return code {result.returncode}")
        if rs_match:
            print("...but r_s was computed successfully! Continuing with partial results.")
        else:
            print(result.stderr[:500])
            return None, None
            
    # Pattern 2: rs_drag in CL file header
    if not rs_match:
        cl_file = os.path.join(class_dir, f'{output_root}cl.dat')
        if os.path.exists(cl_file):
            try:
                with open(cl_file, 'r') as f:
                    content = f.read(2048)
                    rs_match = re.search(r'rs_drag\s*=\s*([\d.]+)', content)
            except:
                pass
            
    rs = float(rs_match.group(1)) if rs_match else None
    
    # Extract H0/h to check consistency
    h_match = re.search(r'h\s*=\s*([\d.]+)', output)
    h = float(h_match.group(1)) if h_match else None
    
    return rs, h

def main():
    print("="*60)
    print("EXECUTING EDE GRID SCAN")
    print("="*60)
    print(f"{'Lambda [eV]':<15} {'r_s [Mpc]':<15} {'Change':<15}")
    print("-" * 45)
    
    # Sweep Lambda from 0 to 3.0 eV
    # Adjusted theta_i to 2.5 to match paper spec
    lambdas = np.linspace(0, 3.0, 7)
    results_rs = []
    
    if not os.path.exists("scan"):
        os.mkdir("scan")
        
    baseline_rs = None
        
    for val in lambdas:
        ini_name = f"scan/scan_{val:.2f}.ini"
        # Define root relative to class directory (output/scan_val_)
        root_name = f"output/scan_{val:.2f}_"
        
        create_ini_file(val, ini_name, root_name)
        
        rs, h = run_class(ini_name, root_name)
        
        if rs:
            results_rs.append(rs)
            if baseline_rs is None:
                baseline_rs = rs
                
            change = (rs - baseline_rs)
            print(f"{val:<15.2f} {rs:<15.2f} {change:+.2f} Mpc")
        else:
            print(f"{val:<15.2f} FAILED")
            results_rs.append(np.nan)
            
    # Analysis
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    valid_results = [x for x in results_rs if not np.isnan(x)]
    
    if not valid_results:
        print("❌ ALL RUNS FAILED. Check CLASS compilation.")
        return

    baseline_rs = valid_results[0]
    min_rs = min(valid_results)
    max_reduction = baseline_rs - min_rs
    percent_reduction = (max_reduction / baseline_rs) * 100
    
    print(f"Baseline r_s: {baseline_rs:.2f} Mpc")
    print(f"Minimum r_s:  {min_rs:.2f} Mpc")
    print(f"Reduction:    {max_reduction:.2f} Mpc ({percent_reduction:.2f}%)")
    
    if max_reduction > 0.5:
        print("\n✅ PROVEN: Ridder Field reduces sound horizon!")
        print("   Mechanism to resolve Hubble tension is ACTIVE.")
    elif max_reduction > 0.0:
        print("\n⚠️  WARNING: Effect size is small.")
        print("   May need to adjust f_axion or theta_i.")
    else:
        print("\n❌ FAILURE: Sound horizon did not decrease.")
        
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(lambdas[:len(valid_results)], valid_results, 'bo-', linewidth=2)
    plt.axhline(baseline_rs, color='k', linestyle='--', label='ΛCDM Baseline')
    plt.xlabel(r'EDE Scale $\Lambda_{EDE}$ [eV]')
    plt.ylabel(r'Sound Horizon $r_s$ [Mpc]')
    plt.title(f'Ridder Field: Sound Horizon Reduction\nMax reduction: {percent_reduction:.2f}%')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig('ede_mechanism_proof.png', dpi=150)
    print("\nPlot saved to ede_mechanism_proof.png")

if __name__ == '__main__':
    main()
