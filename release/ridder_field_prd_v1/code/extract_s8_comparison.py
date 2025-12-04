#!/usr/bin/env python3
"""Extract S8 values from Tier5 chains for comparison."""
import numpy as np
import sys

def load_chain(chain_file, max_samples=None):
    """Load chain and extract S8 statistics."""
    try:
        with open(chain_file, "r") as f:
            header = f.readline().strip()
        if header.startswith("#"):
            header = header[1:]
        cols = header.split()
        col_map = {c.strip(): i for i, c in enumerate(cols)}
        
        data = np.loadtxt(chain_file)
        if len(data.shape) == 1:
            data = data.reshape(1, -1)
        
        # Limit samples if requested
        if max_samples and len(data) > max_samples:
            data = data[:max_samples]
        
        if len(data) < 5:
            return None
        
        n_samples = len(data)
        
        # H0
        H0 = np.mean(data[:, col_map["H0"]])
        H0_std = np.std(data[:, col_map["H0"]])
        
        # S8 - try direct column first, then compute from sigma8 and Omega_m
        if "S8" in col_map:
            S8_vals = data[:, col_map["S8"]]
            # Check if values are reasonable (0.5-1.0)
            if np.all((S8_vals > 0.5) & (S8_vals < 1.0)):
                S8 = np.mean(S8_vals)
                S8_std = np.std(S8_vals)
            else:
                # S8 column has wrong values, compute from sigma8/Omega_m
                if "sigma8" in col_map and "Omega_m" in col_map:
                    S8_vals = data[:, col_map["sigma8"]] * np.sqrt(data[:, col_map["Omega_m"]] / 0.3)
                    S8 = np.mean(S8_vals)
                    S8_std = np.std(S8_vals)
                else:
                    S8, S8_std = np.nan, np.nan
        elif "sigma8" in col_map and "Omega_m" in col_map:
            S8_vals = data[:, col_map["sigma8"]] * np.sqrt(data[:, col_map["Omega_m"]] / 0.3)
            S8 = np.mean(S8_vals)
            S8_std = np.std(S8_vals)
        else:
            S8, S8_std = np.nan, np.nan
        
        # Best-fit point
        best_idx = np.argmin(data[:, col_map["minuslogpost"]])
        H0_best = data[best_idx, col_map["H0"]]
        if "S8" in col_map and np.all((data[:, col_map["S8"]] > 0.5) & (data[:, col_map["S8"]] < 1.0)):
            S8_best = data[best_idx, col_map["S8"]]
        elif "sigma8" in col_map and "Omega_m" in col_map:
            sig8_best = data[best_idx, col_map["sigma8"]]
            om_best = data[best_idx, col_map["Omega_m"]]
            S8_best = sig8_best * np.sqrt(om_best / 0.3)
        else:
            S8_best = np.nan
        
        # Also get sigma8 and Omega_m for diagnostics
        sigma8 = np.mean(data[:, col_map["sigma8"]]) if "sigma8" in col_map else np.nan
        Omega_m = np.mean(data[:, col_map["Omega_m"]]) if "Omega_m" in col_map else np.nan
        
        return {
            "n": n_samples,
            "H0": H0,
            "H0_std": H0_std,
            "H0_best": H0_best,
            "S8": S8,
            "S8_std": S8_std,
            "S8_best": S8_best,
            "sigma8": sigma8,
            "Omega_m": Omega_m,
            "minuslogpost_best": data[best_idx, col_map["minuslogpost"]],
        }
    except Exception as e:
        print(f"Error loading {chain_file}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import os
    
    # Chain files on server
    base_dir = os.path.expanduser("~/Ridder-Field/phase3/chains")
    ede_file = os.path.join(base_dir, "tier5_ede_shoes_predesi.1.txt")
    lcdm_file = os.path.join(base_dir, "tier5_lcdm_shoes_predesi.1.txt")
    
    print("=" * 80)
    print("S8 COMPARISON: Tier5 EDE vs LCDM (first 550 samples)")
    print("=" * 80)
    
    # Load EDE chain (first 550 samples)
    ede_data = load_chain(ede_file, max_samples=550)
    if ede_data:
        print(f"\n📊 EDE Chain (tier5_ede_shoes_predesi):")
        print(f"   Samples: {ede_data['n']}")
        print(f"   H0: {ede_data['H0']:.2f} ± {ede_data['H0_std']:.2f} (best: {ede_data['H0_best']:.2f})")
        print(f"   S8: {ede_data['S8']:.4f} ± {ede_data['S8_std']:.4f} (best: {ede_data['S8_best']:.4f})")
        print(f"   sigma8: {ede_data['sigma8']:.4f}, Omega_m: {ede_data['Omega_m']:.4f}")
        print(f"   Best -log(post): {ede_data['minuslogpost_best']:.2f}")
    else:
        print("❌ Failed to load EDE chain")
        sys.exit(1)
    
    # Load LCDM chain (first 550 samples)
    lcdm_data = load_chain(lcdm_file, max_samples=550)
    if lcdm_data:
        print(f"\n📊 LCDM Chain (tier5_lcdm_shoes_predesi):")
        print(f"   Samples: {lcdm_data['n']}")
        print(f"   H0: {lcdm_data['H0']:.2f} ± {lcdm_data['H0_std']:.2f} (best: {lcdm_data['H0_best']:.2f})")
        print(f"   S8: {lcdm_data['S8']:.4f} ± {lcdm_data['S8_std']:.4f} (best: {lcdm_data['S8_best']:.4f})")
        print(f"   sigma8: {lcdm_data['sigma8']:.4f}, Omega_m: {lcdm_data['Omega_m']:.4f}")
        print(f"   Best -log(post): {lcdm_data['minuslogpost_best']:.2f}")
    else:
        print("❌ Failed to load LCDM chain")
        sys.exit(1)
    
    # Comparison
    print(f"\n{'='*80}")
    print("COMPARISON:")
    print(f"{'='*80}")
    delta_H0 = ede_data['H0'] - lcdm_data['H0']
    delta_S8 = ede_data['S8'] - lcdm_data['S8']
    delta_chi2 = 2 * (ede_data['minuslogpost_best'] - lcdm_data['minuslogpost_best'])
    
    print(f"ΔH0 = {delta_H0:+.2f} km/s/Mpc (EDE - LCDM)")
    print(f"ΔS8 = {delta_S8:+.4f} (EDE - LCDM)")
    print(f"Δχ² = {delta_chi2:+.2f} (EDE - LCDM)")
    
    print(f"\n{'='*80}")
    if delta_S8 < 0:
        print("✅ EDE has LOWER S8 than LCDM (helps resolve S8 tension)")
    else:
        print("⚠️  EDE has HIGHER S8 than LCDM")
    print(f"{'='*80}")
