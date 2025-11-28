#!/usr/bin/env python3
"""
Tier 10 Live Status Dashboard
Shows sample counts, H0, S8, chi2 for all running chains
"""
import numpy as np
import glob
import os

print("="*100)
print("TIER 10 PUBLICATION CHAINS - LIVE STATUS")
print("="*100)

def load_chain(chain_file):
    """Load chain and extract key statistics"""
    try:
        with open(chain_file, "r") as f:
            header = f.readline().strip()
        if header.startswith("#"):
            header = header[1:]
        cols = header.split()
        col_map = {c: i for i, c in enumerate(cols)}
        
        data = np.loadtxt(chain_file)
        if len(data) < 10:
            return None
            
        n_samples = len(data)
        H0 = np.mean(data[:, col_map["H0"]])
        H0_std = np.std(data[:, col_map["H0"]])
        
        if "S8" in col_map:
            S8 = np.mean(data[:, col_map["S8"]])
        else:
            S8 = np.mean(data[:, col_map["sigma8"]] * np.sqrt(data[:, col_map["Omega_m"]]/0.3))
        
        # Best-fit chi2
        best_idx = np.argmin(data[:, 1])
        chi2_best = data[best_idx, 1] * 2
        
        return {
            "n": n_samples,
            "H0": H0,
            "H0_std": H0_std,
            "S8": S8,
            "chi2": chi2_best
        }
    except Exception as e:
        return None

# Find all tier10 chains
chain_files = sorted(glob.glob("chains/tier10_*.1.txt"))

if not chain_files:
    print("\nNo Tier 10 chains found yet. Chains may still be initializing...")
    print("Check again in a few minutes.")
    exit(0)

# Group by model type with paper-facing names
groups = {
    "Standard Model (ΛCDM) — Planck + BAO + SH0ES": [],
    "Late-Time Dynamical (w₀wₐCDM) — Planck + BAO + SH0ES": [],
    "Geometric EDE (ϕCDM) — Planck + BAO + SH0ES": [],
    "Geometric EDE High H₀ Stress Test": [],
    "Geometric EDE (ϕCDM) — Planck + BAO only": [],
    "Geometric EDE (ϕCDM) — Planck + BAO + TRGB": [],
}

for f in chain_files:
    name = os.path.basename(f).replace(".1.txt", "")
    data = load_chain(f)
    
    if "lcdm_ref" in name:
        groups["Standard Model (ΛCDM) — Planck + BAO + SH0ES"].append((name, data))
    elif "cpl_control" in name:
        groups["Late-Time Dynamical (w₀wₐCDM) — Planck + BAO + SH0ES"].append((name, data))
    elif "ede_minimal_gold" in name:
        groups["Geometric EDE (ϕCDM) — Planck + BAO + SH0ES"].append((name, data))
    elif "ede_highH0" in name:
        groups["Geometric EDE High H₀ Stress Test"].append((name, data))
    elif "ede_minimal_base" in name:
        groups["Geometric EDE (ϕCDM) — Planck + BAO only"].append((name, data))
    elif "ede_minimal_trgb" in name:
        groups["Geometric EDE (ϕCDM) — Planck + BAO + TRGB"].append((name, data))

# Print status
total_samples = 0
for group_name, chains in groups.items():
    if not chains:
        continue
    
    print(f"\n{'='*100}")
    print(f"{group_name}")
    print(f"{'='*100}")
    print(f"{'Chain':<40} {'N':>8} {'H0':>8} {'±σ':>6} {'S8':>8} {'χ²':>10} {'Status'}")
    print("-"*100)
    
    for name, data in chains:
        if data is None:
            print(f"{name:<40} {'---':>8} {'---':>8} {'---':>6} {'---':>8} {'---':>10} Initializing...")
        else:
            total_samples += data["n"]
            # Status based on sample count (target: 3000)
            if data["n"] >= 3000:
                status = "✅ Ready"
            elif data["n"] >= 2000:
                status = "🔄 >66%"
            elif data["n"] >= 1000:
                status = "🔄 >33%"
            elif data["n"] >= 100:
                status = "🔄 Running"
            else:
                status = "🔄 Starting"
            
            print(f"{name:<40} {data['n']:>8} {data['H0']:>8.2f} {data['H0_std']:>6.2f} {data['S8']:>8.3f} {data['chi2']:>10.1f} {status}")

print(f"\n{'='*100}")
print(f"SUMMARY")
print(f"{'='*100}")
print(f"Total chains found: {len(chain_files)}")
print(f"Total samples: {total_samples}")

# Check for reference chi2 to compute deltas
ref_chains = [c for c in chain_files if "lcdm_ref" in c]
if ref_chains:
    ref_data = load_chain(ref_chains[0])
    if ref_data and ref_data["n"] >= 100:
        ref_chi2 = ref_data["chi2"]
        print(f"\nReference χ² (LCDM): {ref_chi2:.1f}")
        print(f"\nΔχ² Summary:")
        
        for f in chain_files:
            name = os.path.basename(f).replace(".1.txt", "")
            data = load_chain(f)
            if data and data["n"] >= 100:
                dchi2 = data["chi2"] - ref_chi2
                print(f"  {name}: Δχ² = {dchi2:+.1f}, H0 = {data['H0']:.1f}, S8 = {data['S8']:.3f}")

print(f"\n{'='*100}")
print("Target: R-1 < 0.01 for multi-chain models, ESS > 2000 for single chains")
print("="*100)

