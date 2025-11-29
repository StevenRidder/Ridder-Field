#!/usr/bin/env python3
"""Tier 5 Chain Status Dashboard"""

import os
import glob
import numpy as np

def load_chain(path):
    """Load chain and compute summary stats."""
    try:
        data = np.loadtxt(path)
        if len(data) < 10:
            return None
        
        # Columns: weight, -logpost, params...
        weights = data[:, 0]
        chi2 = 2 * data[:, 1]  # -logpost to chi2
        
        # Find H0, S8, rdrag columns (typically 3, derived)
        # This depends on your param order
        n_samples = len(weights)
        mean_chi2 = np.average(chi2, weights=weights)
        best_chi2 = chi2.min()
        
        # Try to get H0 (usually column 3 or 4)
        h0_col = 3 if data.shape[1] > 3 else None
        h0 = np.average(data[:, h0_col], weights=weights) if h0_col else None
        
        return {
            "n": n_samples,
            "chi2": best_chi2,
            "mean_chi2": mean_chi2,
            "H0": h0
        }
    except Exception as e:
        return None

def main():
    print("=" * 60)
    print("TIER 5 STATUS: Modern Dataset Validation")
    print("=" * 60)
    
    # Find all tier5 chains
    chain_files = sorted(glob.glob("chains/tier5*.1.txt"))
    
    if not chain_files:
        print("\nNo Tier 5 chains found yet.")
        print("Run: bash tier5_launch.sh")
        return
    
    # Group by phase
    phases = {
        "Phase 1a (DESI only)": [],
        "Phase 1b (DESI+Pantheon+)": [],
        "Phase 2 (ACT)": [],
        "Phase 3 (DES)": []
    }
    
    for f in chain_files:
        name = os.path.basename(f).replace(".1.txt", "")
        if "desi_pantheon" in name:
            phases["Phase 1b (DESI+Pantheon+)"].append(f)
        elif "desi" in name:
            phases["Phase 1a (DESI only)"].append(f)
        elif "act" in name:
            phases["Phase 2 (ACT)"].append(f)
        elif "des" in name:
            phases["Phase 3 (DES)"].append(f)
    
    for phase, files in phases.items():
        if not files:
            continue
        
        print(f"\n{phase}:")
        print("-" * 50)
        print(f"{'Chain':<30} {'N':>6} {'χ²':>8} {'H0':>6}")
        print("-" * 50)
        
        for f in files:
            name = os.path.basename(f).replace(".1.txt", "").replace("tier5_", "")
            data = load_chain(f)
            
            if data:
                h0_str = f"{data['H0']:.1f}" if data['H0'] else "---"
                print(f"{name:<30} {data['n']:>6} {data['chi2']:>8.1f} {h0_str:>6}")
            else:
                print(f"{name:<30} {'starting...':>20}")
    
    print("\n" + "=" * 60)
    
    # Check running processes
    import subprocess
    result = subprocess.run(["pgrep", "-c", "cobaya"], capture_output=True, text=True)
    n_running = int(result.stdout.strip()) if result.returncode == 0 else 0
    print(f"Cobaya processes running: {n_running}")

if __name__ == "__main__":
    main()

