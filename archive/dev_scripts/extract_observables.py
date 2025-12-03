#!/usr/bin/env python3
"""
Extract key cosmological observables from CLASS output files.
"""

import numpy as np
import sys
import os

def extract_from_background(bg_file):
    """Extract H0, Omega_m, Omega_Lambda from background file."""
    if not os.path.exists(bg_file):
        return None
    
    data = np.loadtxt(bg_file)
    
    # Column 0: z (redshift)
    # Column 3: H [1/Mpc]
    # With Ridder: Column 14: (.)rho_ridder, Column 19: (.)rho_tot
    # Without Ridder: fewer columns
    
    # Find the row closest to z=0 (a=1)
    z_col = data[:, 0]
    idx_z0 = np.argmin(np.abs(z_col - 0.0))
    
    # H is in units of 1/Mpc, need to convert to km/s/Mpc
    # H [km/s/Mpc] = H [1/Mpc] × c [km/s]
    c_km_per_s = 299792.458  # speed of light in km/s
    H_Mpc_inv = data[idx_z0, 3]  # H in 1/Mpc (column 3)
    H0_km_s_Mpc = H_Mpc_inv * c_km_per_s
    
    # Check if we have Ridder columns (more than 19 columns)
    n_cols = data.shape[1]
    has_ridder = (n_cols >= 20)
    
    if has_ridder:
        # Extract component densities at z=0
        rho_ridder = data[idx_z0, 14]  # Column 14: (.)rho_ridder
        rho_tot = data[idx_z0, 19]     # Column 19: (.)rho_tot
        f_ridder_0 = rho_ridder / rho_tot if rho_tot > 0 else 0.0
    else:
        # No Ridder field in this output
        rho_ridder = 0.0
        rho_tot = data[idx_z0, 13]  # Column 13: (.)rho_crit for vanilla ΛCDM
        f_ridder_0 = 0.0
    
    return {
        'H0': H0_km_s_Mpc,
        'H_Mpc_inv': H_Mpc_inv,
        'z_at_extract': z_col[idx_z0],
        'f_ridder_0': f_ridder_0,
        'rho_ridder': rho_ridder,
        'rho_tot': rho_tot,
        'has_ridder': has_ridder
    }

def extract_from_cl(cl_file):
    """Extract CMB power spectrum peaks and amplitude."""
    if not os.path.exists(cl_file):
        return None
    
    data = np.loadtxt(cl_file)
    
    # Column 0: l
    # Column 1: TT
    # Column 2: EE  
    # Column 3: TE
    # (in units of [l(l+1)/2π] C_l in μK^2)
    
    ell = data[:, 0]
    TT = data[:, 1]
    
    # Find first acoustic peak (around l~220)
    mask_peak1 = (ell > 150) & (ell < 300)
    ell_peak1 = ell[mask_peak1][np.argmax(TT[mask_peak1])]
    TT_peak1 = np.max(TT[mask_peak1])
    
    # Average amplitude at high-l (damping tail, l > 1000)
    mask_highell = ell > 1000
    TT_highell_mean = np.mean(TT[mask_highell]) if np.any(mask_highell) else 0.0
    
    return {
        'ell_peak1': ell_peak1,
        'TT_peak1': TT_peak1,
        'TT_highell_mean': TT_highell_mean
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: extract_observables.py <output_prefix>")
        print("Example: extract_observables.py output/benchmark_lcdm_control_00")
        sys.exit(1)
    
    prefix = sys.argv[1]
    
    bg_file = f"{prefix}_background.dat"
    cl_file = f"{prefix}_cl.dat"
    
    print(f"Extracting observables from: {prefix}")
    print("=" * 60)
    
    # Background observables
    bg_obs = extract_from_background(bg_file)
    if bg_obs:
        print(f"H0 = {bg_obs['H0']:.4f} km/s/Mpc")
        print(f"H [Mpc^-1] = {bg_obs['H_Mpc_inv']:.6e}")
        print(f"z at extraction = {bg_obs['z_at_extract']:.6f}")
        if bg_obs['has_ridder']:
            print(f"f_ridder(z=0) = {bg_obs['f_ridder_0']:.6f}")
            print(f"rho_ridder(z=0) = {bg_obs['rho_ridder']:.6e} Mpc^-2")
        print(f"rho_tot(z=0) = {bg_obs['rho_tot']:.6e} Mpc^-2")
    else:
        print(f"Could not read background file: {bg_file}")
    
    print()
    
    # CMB observables
    cl_obs = extract_from_cl(cl_file)
    if cl_obs:
        print(f"First acoustic peak: l = {cl_obs['ell_peak1']:.0f}, TT = {cl_obs['TT_peak1']:.6e} [l(l+1)/2π units]")
        print(f"High-l mean (l>1000): TT = {cl_obs['TT_highell_mean']:.6e} [l(l+1)/2π units]")
    else:
        print(f"Could not read C_l file: {cl_file}")
    
    return bg_obs, cl_obs

if __name__ == "__main__":
    main()

