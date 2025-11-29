#!/usr/bin/env python3
"""Tier 10 Publication Chains - Status Dashboard with Paper Naming"""

import os
import glob
import numpy as np

def get_world(chain_name):
    if "_shoes" in chain_name:
        return "shoes"
    elif "_trgb" in chain_name:
        return "trgb"
    elif "_base" in chain_name:
        return "base"
    return "unknown"

def load_chain(path):
    try:
        # Read header line to get column names
        with open(path) as f:
            header = f.readline().strip()
        
        # Parse column names (skip # if present)
        if header.startswith('#'):
            header = header[1:]
        cols = header.split()
        
        # Find H0 and S8 columns
        h0_col = None
        s8_col = None
        chi2_col = None
        
        for i, c in enumerate(cols):
            if c == "H0":
                h0_col = i
            elif c == "S8":
                s8_col = i
            elif c == "chi2":
                chi2_col = i
        
        if h0_col is None or s8_col is None:
            return None
        
        # Load data (skip header)
        data = np.loadtxt(path, skiprows=1)
        if len(data) < 50:
            return None
        
        weights = data[:, 0]
        h0 = data[:, h0_col]
        s8 = data[:, s8_col]
        
        # Get chi2 from column or compute from minuslogpost
        if chi2_col is not None:
            chi2 = data[:, chi2_col]
        else:
            chi2 = 2 * data[:, 1]  # minuslogpost column
        
        return {
            "n": len(data),
            "h0": np.average(h0, weights=weights),
            "h0_std": np.sqrt(np.average((h0 - np.average(h0, weights=weights))**2, weights=weights)),
            "s8": np.average(s8, weights=weights),
            "s8_std": np.sqrt(np.average((s8 - np.average(s8, weights=weights))**2, weights=weights)),
            "chi2": np.min(chi2),
        }
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def main():
    print("=" * 100)
    print("TIER 10 PUBLICATION CHAINS - FINAL STATUS")
    print("=" * 100)
    
    chain_files = sorted(glob.glob("chains/tier10_*.1.txt"))
    
    groups = {
        ("LCDM", "shoes"): [],
        ("CPL", "shoes"): [],
        ("EDE", "shoes"): [],
        ("EDE_stress", "shoes"): [],
        ("EDE", "base"): [],
        ("EDE", "trgb"): [],
    }
    
    all_data = {}
    
    for f in chain_files:
        name = os.path.basename(f).replace(".1.txt", "")
        data = load_chain(f)
        if data:
            all_data[name] = data
            world = get_world(name)
            
            if "lcdm_ref" in name:
                groups[("LCDM", "shoes")].append((name, data))
            elif "cpl_control" in name:
                groups[("CPL", "shoes")].append((name, data))
            elif "ede_highH0" in name:
                groups[("EDE_stress", "shoes")].append((name, data))
            elif "ede_minimal_gold" in name:
                groups[("EDE", "shoes")].append((name, data))
            elif "ede_minimal_base" in name:
                groups[("EDE", "base")].append((name, data))
            elif "ede_minimal_trgb" in name:
                groups[("EDE", "trgb")].append((name, data))
    
    # Find best LCDM chi2 as reference
    lcdm_chains = groups[("LCDM", "shoes")]
    if lcdm_chains:
        ref_chi2 = min(d["chi2"] for _, d in lcdm_chains)
        ref_name = [n for n, d in lcdm_chains if d["chi2"] == ref_chi2][0]
    else:
        ref_chi2 = None
        ref_name = None
    
    def print_group(title, world_desc, chains):
        print()
        print("=" * 100)
        print(f"{title} -- {world_desc}")
        print("=" * 100)
        print(f"{'Chain':<45} {'N':>6} {'H0':>8} {'+/-':>6} {'S8':>8} {'chi2':>10} {'dchi2':>8} {'Status'}")
        print("-" * 100)
        
        for name, d in sorted(chains, key=lambda x: x[1]["chi2"]):
            n = d["n"]
            status = "Ready" if n >= 3000 else (">66%" if n >= 2000 else (">33%" if n >= 1000 else "Running"))
            delta = f"{d['chi2'] - ref_chi2:+.1f}" if ref_chi2 else "---"
            print(f"{name:<45} {n:>6} {d['h0']:>8.2f} {d['h0_std']:>6.2f} {d['s8']:>8.3f} {d['chi2']:>10.1f} {delta:>8} {status}")
    
    print_group("Standard Model (LCDM)", "Planck + BAO + SH0ES", groups[("LCDM", "shoes")])
    print_group("Late-Time Dynamical (w0waCDM)", "Planck + BAO + SH0ES", groups[("CPL", "shoes")])
    print_group("Geometric EDE (phiCDM) -- MAIN RESULT", "Planck + BAO + SH0ES", groups[("EDE", "shoes")])
    print_group("Geometric EDE -- High H0 Stress Test", "Planck + BAO + SH0ES", groups[("EDE_stress", "shoes")])
    print_group("Geometric EDE (phiCDM) -- Control", "Planck + BAO only (no H0 prior)", groups[("EDE", "base")])
    print_group("Geometric EDE (phiCDM) -- Control", "Planck + BAO + TRGB", groups[("EDE", "trgb")])
    
    # Summary
    print()
    print("=" * 100)
    print("PUBLICATION SUMMARY")
    print("=" * 100)
    
    total_chains = sum(len(g) for g in groups.values())
    total_samples = sum(d["n"] for d in all_data.values())
    
    print(f"\nTotal chains: {total_chains}")
    print(f"Total samples: {total_samples:,}")
    
    if ref_chi2:
        print(f"\nReference chi2 (LCDM best): {ref_chi2:.1f} [{ref_name}]")
    
    # Key results table
    print()
    print("KEY RESULTS (SH0ES World):")
    print("-" * 80)
    print(f"{'Model':<35} {'k':<4} {'H0':<16} {'S8':<16} {'Best chi2':<12} {'dchi2'}")
    print("-" * 80)
    
    # LCDM pooled
    if lcdm_chains:
        all_h0 = [d["h0"] for _, d in lcdm_chains]
        all_s8 = [d["s8"] for _, d in lcdm_chains]
        best_chi2 = min(d["chi2"] for _, d in lcdm_chains)
        h0_str = f"{np.mean(all_h0):.2f} +/- {np.std(all_h0):.2f}"
        s8_str = f"{np.mean(all_s8):.3f} +/- {np.std(all_s8):.3f}"
        print(f"{'Standard Model (LCDM)':<35} {'6':<4} {h0_str:<16} {s8_str:<16} {best_chi2:<12.1f} {'REF'}")
    
    # CPL pooled
    cpl_chains = groups[("CPL", "shoes")]
    if cpl_chains:
        all_h0 = [d["h0"] for _, d in cpl_chains]
        all_s8 = [d["s8"] for _, d in cpl_chains]
        best_chi2 = min(d["chi2"] for _, d in cpl_chains)
        delta = best_chi2 - ref_chi2 if ref_chi2 else 0
        h0_str = f"{np.mean(all_h0):.2f} +/- {np.std(all_h0):.2f}"
        s8_str = f"{np.mean(all_s8):.3f} +/- {np.std(all_s8):.3f}"
        print(f"{'Late-Time Dynamical (w0waCDM)':<35} {'8':<4} {h0_str:<16} {s8_str:<16} {best_chi2:<12.1f} {delta:+.1f}")
    
    # EDE pooled
    ede_chains = groups[("EDE", "shoes")]
    if ede_chains:
        all_h0 = [d["h0"] for _, d in ede_chains]
        all_s8 = [d["s8"] for _, d in ede_chains]
        best_chi2 = min(d["chi2"] for _, d in ede_chains)
        delta = best_chi2 - ref_chi2 if ref_chi2 else 0
        h0_str = f"{np.mean(all_h0):.2f} +/- {np.std(all_h0):.2f}"
        s8_str = f"{np.mean(all_s8):.3f} +/- {np.std(all_s8):.3f}"
        print(f"{'Geometric EDE (phiCDM)':<35} {'8':<4} {h0_str:<16} {s8_str:<16} {best_chi2:<12.1f} {delta:+.1f}")
    
    print()
    print("=" * 100)

if __name__ == "__main__":
    main()

