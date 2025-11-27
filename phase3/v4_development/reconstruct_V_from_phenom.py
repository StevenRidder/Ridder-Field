#!/usr/bin/env python3
"""
STEP 2: Reconstruct V(φ) from phenomenological w(z), ρ_DE(z)

Given a chain with CPL parameters (w0, wa), this script:
1. Runs CLASS to get the background history
2. Extracts ρ_DE(z) and w_DE(z)
3. Reconstructs the scalar field potential V(φ)
4. Outputs numerical V(φ) for template fitting

Physics:
  ρ_φ = (1/2)φ̇² + V(φ)
  p_φ = (1/2)φ̇² - V(φ)
  w = p/ρ

  Therefore:
  (1/2)φ̇² = (1+w)/2 * ρ
  V = (1-w)/2 * ρ
"""

import numpy as np
import json
from pathlib import Path

def load_best_fit(chain_path):
    """Load best-fit parameters from a chain."""
    with open(chain_path) as f:
        header = f.readline().strip().replace("#", "").split()
    
    col_map = {name: i for i, name in enumerate(header)}
    data = np.loadtxt(chain_path)
    best_idx = np.argmin(data[:, 1])  # min minuslogpost
    
    return {name: data[best_idx, i] for name, i in col_map.items()}

def get_background_from_class(params):
    """Run CLASS and get background quantities."""
    import classy
    
    cosmo = classy.Class()
    class_params = {
        "H0": params.get("H0", 67.5),
        "omega_b": params.get("omega_b", 0.02237),
        "omega_cdm": params.get("omega_cdm", 0.1200),
        "A_s": params.get("A_s", 2.1e-9),
        "n_s": params.get("n_s", 0.9649),
        "tau_reio": params.get("tau_reio", 0.0544),
        "Omega_Lambda": 0,
        "fluid_equation_of_state": "CLP",
        "w0_fld": params.get("w0_fld", -1.0),
        "wa_fld": params.get("wa_fld", 0.0),
        "output": "tCl",
        "l_max_scalars": 100,
    }
    
    cosmo.set(class_params)
    cosmo.compute()
    
    bg = cosmo.get_background()
    
    # Extract relevant quantities
    z = bg["z"]
    a = 1.0 / (1.0 + z)
    H = bg["H [1/Mpc]"]
    
    # Dark energy density and equation of state
    # For fluid DE: rho_fld and w_fld should be in background
    rho_fld = bg.get("(.)rho_fld", np.zeros_like(z))
    
    # CPL equation of state
    w0 = params.get("w0_fld", -1.0)
    wa = params.get("wa_fld", 0.0)
    w_fld = w0 + wa * z / (1 + z)
    
    cosmo.struct_cleanup()
    cosmo.empty()
    
    return {
        "z": z,
        "a": a,
        "H": H,
        "rho_fld": rho_fld,
        "w_fld": w_fld,
    }

def reconstruct_field(bg_data):
    """
    Reconstruct φ(z) and V(φ) from ρ_DE(z) and w(z).
    
    (1/2)φ̇² = (1+w)/2 * ρ
    V = (1-w)/2 * ρ
    
    dφ/dz = φ̇ / (dz/dt) = φ̇ / (-H(1+z))
    """
    z = bg_data["z"]
    a = bg_data["a"]
    H = bg_data["H"]
    rho = bg_data["rho_fld"]
    w = bg_data["w_fld"]
    
    # Kinetic and potential energy
    kinetic = (1 + w) / 2 * rho  # (1/2)φ̇²
    V = (1 - w) / 2 * rho
    
    # φ̇ = sqrt(2 * kinetic)
    phi_dot = np.sqrt(2 * np.abs(kinetic)) * np.sign(kinetic)
    
    # dφ/dz = φ̇ / (-H(1+z))
    dphi_dz = phi_dot / (-H * (1 + z))
    
    # Integrate to get φ(z), starting from φ=0 at z=0
    # Use cumulative trapezoid from z=0 upward
    idx_sort = np.argsort(z)
    z_sorted = z[idx_sort]
    dphi_dz_sorted = dphi_dz[idx_sort]
    
    phi = np.zeros_like(z)
    for i in range(1, len(z_sorted)):
        phi[idx_sort[i]] = phi[idx_sort[i-1]] + np.trapz(
            dphi_dz_sorted[:i+1], z_sorted[:i+1]
        )
    
    return {
        "z": z,
        "phi": phi,
        "V": V,
        "kinetic": kinetic,
        "w": w,
        "rho": rho,
    }

def save_reconstruction(recon_data, output_path):
    """Save reconstruction to file for template fitting."""
    np.savez(output_path,
             z=recon_data["z"],
             phi=recon_data["phi"],
             V=recon_data["V"],
             w=recon_data["w"],
             rho=recon_data["rho"])
    print(f"Saved reconstruction to {output_path}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--chain", default="chains/tier6_phenom_shoes.1.txt",
                        help="Path to phenomenological chain")
    parser.add_argument("--output", default="v4_development/reconstructed_V.npz",
                        help="Output path for V(φ) data")
    args = parser.parse_args()
    
    base = Path(__file__).parent.parent
    chain_path = base / args.chain
    output_path = base / args.output
    
    print(f"Loading best fit from {chain_path}")
    params = load_best_fit(chain_path)
    
    print(f"Running CLASS with w0={params.get(w0_fld, -1):.3f}, wa={params.get(wa_fld, 0):.3f}")
    bg = get_background_from_class(params)
    
    print("Reconstructing V(φ)...")
    recon = reconstruct_field(bg)
    
    save_reconstruction(recon, output_path)
    
    # Print summary
    print("\nReconstruction summary:")
    print(f"  z range: {recon[z].min():.1f} to {recon[z].max():.1f}")
    print(f"  φ range: {recon[phi].min():.2e} to {recon[phi].max():.2e}")
    print(f"  V range: {recon[V].min():.2e} to {recon[V].max():.2e}")

if __name__ == "__main__":
    main()
