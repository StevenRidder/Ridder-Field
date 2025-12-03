#!/usr/bin/env python3
"""
Scan m_axion to understand z_peak vs m relationship.
Goal: Find m that gives z_peak ~ 3500
"""

import subprocess
import os
import re
import sys

# Configuration
VM_HOST = "<VM_USER>@172.174.34.125"
CLASS_BIN = "./phase2/class/class"
BASE_INI = "axiclass_anchor_proper.ini"
WORK_DIR = "~/Ridder-Field"

def run_class_with_m(m_axion, f_axion=0.0002):
    """Run CLASS with given m_axion and extract f_peak, z_peak"""
    
    # Create temporary INI with modified m_axion
    ini_content = f"""
# Scan point: m_axion = {m_axion}
H0 = 67.36
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842
gauge = newtonian

use_ridder = yes
ridder_model_type = unified
ridder_use_tail = no
ridder_use_shelf = yes
ridder_use_plateau = no

ridder_Lambda_EDE_eV = 1.0
theta_i_ridder = 2.72
ridder_n_EDE = 3.0
ridder_m_axion = {m_axion}
ridder_f_axion = {f_axion}
ridder_f = {f_axion * 2.435e27}

ridder_theta_EDE_low = 0.1
ridder_theta_EDE_high = 4.0
ridder_sigma_theta_EDE = 0.3
beta_ridder = 0.0

ridder_use_shooting_EDE = no  # Disable shooting for scan

output = tCl
write background = yes
background_verbose = 1
root = output/scan_m_{m_axion:.0f}_
tol_background_integration = 1e-5
"""
    
    # Write temp INI
    cmd = f'ssh {VM_HOST} "cd {WORK_DIR} && cat > scan_temp.ini << \'EOF\'\n{ini_content}\nEOF"'
    subprocess.run(cmd, shell=True, capture_output=True)
    
    # Run CLASS
    cmd = f'ssh {VM_HOST} "cd {WORK_DIR} && timeout 120 {CLASS_BIN} scan_temp.ini 2>&1"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout + result.stderr
    
    # Check for errors
    if "Error" in output and "age =" not in output:
        return None, None, None, f"Error: {output[-200:]}"
    
    # Extract f_peak and z_peak from Python script
    cmd = f'ssh {VM_HOST} "cd {WORK_DIR} && python3 extract_f_peak.py output/scan_m_{m_axion:.0f}_00_background.dat 2>/dev/null"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Parse output
    f_peak = None
    z_peak = None
    for line in result.stdout.split('\n'):
        if 'f_peak' in line and '=' in line:
            try:
                f_peak = float(line.split('=')[1].strip())
            except:
                pass
        if 'z_peak' in line and '=' in line:
            try:
                z_peak = float(line.split('=')[1].strip())
            except:
                pass
    
    return m_axion, f_peak, z_peak, "OK"


def main():
    print("=" * 70)
    print("SCAN: m_axion vs z_peak (fixed f_axion = 0.0002 M_Pl)")
    print("=" * 70)
    print(f"{'m_axion (H0)':>15} {'f_peak':>12} {'z_peak':>15} {'Status':>10}")
    print("-" * 70)
    
    # Test a range of m values
    m_values = [10, 30, 50, 70, 100, 150, 200, 300, 500, 1000, 3000, 10000]
    
    for m in m_values:
        m_out, f_peak, z_peak, status = run_class_with_m(m)
        
        if f_peak is not None:
            print(f"{m:>15.0f} {f_peak:>12.4e} {z_peak:>15.4e} {status:>10}")
        else:
            print(f"{m:>15.0f} {'N/A':>12} {'N/A':>15} {status[-20:]:>10}")
    
    print("-" * 70)
    print("Goal: Find m where z_peak ~ 3500")


if __name__ == "__main__":
    main()

