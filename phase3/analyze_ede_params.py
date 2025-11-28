#!/usr/bin/env python3
"""
Analyze EDE parameters to identify garbage (unconstrained) vs useful parameters.
This helps reduce BIC penalty by fixing parameters that don't contribute.
"""
import numpy as np
import sys

def analyze_chain(chain_file):
    # Load chain
    with open(chain_file, "r") as f:
        header = f.readline().strip()
    if header.startswith("#"):
        header = header[1:]
    cols = header.split()
    col_map = {name: i for i, name in enumerate(cols)}
    
    data = np.loadtxt(chain_file)
    print("="*90)
    print(f"PARAMETER DIAGNOSTIC: {chain_file}")
    print("="*90)
    print(f"Samples: {len(data)}")
    
    # EDE parameters
    ede_params = ["ridder_Lambda_EDE_eV", "ridder_a_c", "ridder_sigma_lna"]
    
    print("\n" + "="*90)
    print("EDE PARAMETER POSTERIORS")
    print("="*90)
    
    for param in ede_params:
        if param in col_map:
            vals = data[:, col_map[param]]
            mean = np.mean(vals)
            std = np.std(vals)
            pmin, pmax = np.min(vals), np.max(vals)
            p16, p50, p84 = np.percentile(vals, [16, 50, 84])
            
            range_frac = std / (pmax - pmin) if pmax > pmin else 0
            if range_frac < 0.25:
                constrained = "YES - well constrained"
            elif range_frac < 0.4:
                constrained = "MAYBE - somewhat constrained"
            else:
                constrained = "NO - prior-dominated (garbage?)"
            
            print(f"\n{param}:")
            print(f"  Mean ± σ: {mean:.6f} ± {std:.6f}")
            print(f"  Range: [{pmin:.6f}, {pmax:.6f}]")
            print(f"  68% CI: {p16:.6f} - {p84:.6f}")
            print(f"  σ/range: {range_frac:.2f}")
            print(f"  Constrained: {constrained}")
    
    print("\n" + "="*90)
    print("CORRELATIONS WITH OBSERVABLES")
    print("="*90)
    
    H0 = data[:, col_map["H0"]]
    if "S8" in col_map:
        S8 = data[:, col_map["S8"]]
    else:
        S8 = data[:, col_map["sigma8"]] * np.sqrt(data[:, col_map["Omega_m"]]/0.3)
    
    # chi2 is usually minuslogpost * 2 or in a chi2 column
    chi2 = data[:, 1] * 2  # -logpost
    
    print(f"\n{'Parameter':<25} {'corr(H0)':>10} {'corr(S8)':>10} {'Verdict':<25}")
    print("-"*75)
    
    recommendations = {}
    for param in ede_params:
        if param in col_map:
            vals = data[:, col_map[param]]
            corr_H0 = np.corrcoef(vals, H0)[0,1]
            corr_S8 = np.corrcoef(vals, S8)[0,1]
            
            if abs(corr_H0) > 0.3 or abs(corr_S8) > 0.3:
                verdict = "KEEP - drives tension"
                recommendations[param] = "sample"
            else:
                verdict = "FIX - no impact on tension"
                recommendations[param] = "fix"
            
            print(f"{param:<25} {corr_H0:>+10.3f} {corr_S8:>+10.3f} {verdict:<25}")
    
    print("\n" + "="*90)
    print("BEST-FIT VALUES (use for fixing)")
    print("="*90)
    
    best_idx = np.argmin(data[:, 1])
    print("\nAt best-fit point:")
    for param in ede_params + ["H0", "omega_cdm", "S8"]:
        if param in col_map:
            val = data[best_idx, col_map[param]]
            action = recommendations.get(param, "")
            if action == "fix":
                print(f"  {param}: {val:.6f}  <-- FIX TO THIS VALUE")
            else:
                print(f"  {param}: {val:.6f}")
    
    print("\n" + "="*90)
    print("RECOMMENDATION")
    print("="*90)
    
    n_keep = sum(1 for v in recommendations.values() if v == "sample")
    n_fix = sum(1 for v in recommendations.values() if v == "fix")
    
    print(f"\nKeep sampling: {n_keep} parameters")
    print(f"Fix (garbage): {n_fix} parameters")
    print(f"\nWith minimal model: k = 6 (LCDM) + {n_keep} (EDE) = {6 + n_keep}")
    print("="*90)

if __name__ == "__main__":
    chain_file = sys.argv[1] if len(sys.argv) > 1 else "chains/tier9_v3_shoes_wide_ocdm.1.txt"
    analyze_chain(chain_file)

