#!/usr/bin/env python3
"""
Per-likelihood chi2 breakdown for P0b vs P2
"""
import numpy as np

CHAIN_DIR = "/home/azureuser/Ridder-Field/phase4/chains"

def load_chain(prefix):
    """Load chain and return best-fit row."""
    fname = f"{CHAIN_DIR}/{prefix}.1.txt"
    data = np.loadtxt(fname)
    with open(fname) as f:
        cols = f.readline().strip()[1:].split()
    logpost_idx = cols.index("minuslogpost")
    best_idx = np.argmin(data[:, logpost_idx])
    return data[best_idx], cols

def main():
    # Load chains
    p0b_best, cols = load_chain("prod_p0b_lcdm_act")
    p2_best, _ = load_chain("prod_p2_ede_act")
    
    # Per-likelihood chi2 columns (skip aggregates)
    chi2_cols = [c for c in cols if c.startswith("chi2__") 
                 and "BAO" not in c and "CMB" not in c and "SN" not in c
                 and c != "chi2__prior"]
    
    print("=" * 95)
    print("PER-LIKELIHOOD CHI2 BREAKDOWN (Best-fit point)")
    print("=" * 95)
    print("{:<60} {:>12} {:>12} {:>10}".format("Likelihood", "P0b (LCDM)", "P2 (EDE)", "Delta"))
    print("-" * 95)
    
    total_p0b = 0
    total_p2 = 0
    
    for col in chi2_cols:
        idx = cols.index(col)
        name = col.replace("chi2__", "").replace("likelihoods.", "")
        chi2_p0b = p0b_best[idx]
        chi2_p2 = p2_best[idx]
        delta = chi2_p2 - chi2_p0b
        total_p0b += chi2_p0b
        total_p2 += chi2_p2
        sign = "+" if delta >= 0 else ""
        print("{:<60} {:>12.1f} {:>12.1f} {:>+10.1f}".format(name, chi2_p0b, chi2_p2, delta))
    
    print("-" * 95)
    print("{:<60} {:>12.1f} {:>12.1f} {:>+10.1f}".format("TOTAL", total_p0b, total_p2, total_p2 - total_p0b))
    print("=" * 95)
    
    # Context
    h0_idx = cols.index("H0")
    s8_idx = cols.index("S8")
    print("\nBest-fit H0:  P0b = {:.2f},  P2 = {:.2f}".format(p0b_best[h0_idx], p2_best[h0_idx]))
    print("Best-fit S8:  P0b = {:.3f},  P2 = {:.3f}".format(p0b_best[s8_idx], p2_best[s8_idx]))

if __name__ == "__main__":
    main()

