#!/usr/bin/env python3
"""
extract_f_peak.py - Ground truth f_EDE extractor

This is the REFERENCE implementation for computing f_peak and z_peak.
The C function ridder_get_f_peak should produce identical results.

Background file columns (from CLASS):
1: z
2: proper time [Gyr]
3: conf. time [Mpc]
4: H [1/Mpc]
5: comov. dist.
6: ang.diam.dist.
7: lum. dist.
8: comov.snd.hrz.
9: (.)rho_g
10: (.)rho_b
11: (.)rho_cdm
12: (.)rho_lambda
13: (.)rho_ur
14: (.)rho_crit
15: (.)rho_ridder
16: (.)p_ridder
17: phi_ridder
18: phi'_ridder
19: V_ridder
20: (.)rho_tot
21: (.)p_tot
22: (.)p_tot_prime
23: gr.fac. D
24: gr.fac. f
"""

import sys
import numpy as np

def extract_f_peak(background_file: str) -> tuple:
    """
    Extract peak f_ridder and z_peak from background file.
    
    f_ridder = rho_ridder / rho_crit  (column 15 / column 14)
    
    Returns:
        (f_peak, z_peak, a_peak)
    """
    # Load data, skip header lines
    data = []
    with open(background_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 20:
                try:
                    z = float(parts[0])
                    rho_crit = float(parts[13])  # column 14 (0-indexed: 13)
                    rho_ridder = float(parts[14])  # column 15 (0-indexed: 14)
                    rho_tot = float(parts[19])  # column 20 (0-indexed: 19)
                    data.append((z, rho_crit, rho_ridder, rho_tot))
                except (ValueError, IndexError):
                    continue
    
    if not data:
        print(f"ERROR: No valid data in {background_file}")
        return (0.0, 0.0, 0.0)
    
    # Convert to numpy arrays
    data = np.array(data)
    z_arr = data[:, 0]
    rho_crit_arr = data[:, 1]
    rho_ridder_arr = data[:, 2]
    rho_tot_arr = data[:, 3]
    
    # Compute f_ridder = rho_ridder / rho_tot
    # (Using rho_tot for fraction of total energy)
    with np.errstate(divide='ignore', invalid='ignore'):
        f_ridder = np.where(rho_tot_arr > 0, rho_ridder_arr / rho_tot_arr, 0.0)
    
    # Find peak
    idx_peak = np.argmax(f_ridder)
    f_peak = f_ridder[idx_peak]
    z_peak = z_arr[idx_peak]
    a_peak = 1.0 / (1.0 + z_peak) if z_peak > -1 else 0.0
    
    return (f_peak, z_peak, a_peak)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_f_peak.py <background_file>")
        print("\nWill search for latest axiclass_proper_v2_*_background.dat if no file specified")
        
        # Try to find latest file
        import glob
        import os
        files = glob.glob("output/axiclass_proper_v2_*_background.dat")
        if not files:
            files = glob.glob("*_background.dat")
        if files:
            background_file = max(files, key=os.path.getmtime)
            print(f"Using: {background_file}")
        else:
            print("No background files found!")
            return
    else:
        background_file = sys.argv[1]
    
    f_peak, z_peak, a_peak = extract_f_peak(background_file)
    
    print("=" * 60)
    print("PYTHON f_EDE EXTRACTION (Reference Implementation)")
    print("=" * 60)
    print(f"File: {background_file}")
    print(f"f_peak  = {f_peak:.6e}")
    print(f"z_peak  = {z_peak:.6e}")
    print(f"a_peak  = {a_peak:.6e}")
    print("=" * 60)
    print()
    print("C code should print IDENTICAL values.")
    print("If C differs, debug ridder_get_f_peak in background.c")


if __name__ == "__main__":
    main()

