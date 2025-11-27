#!/usr/bin/env python3
"""Quick validation: Extract CPL params from tier6 chains and suggest V4 priors."""
import numpy as np
from pathlib import Path

def analyze_chain(chain_path):
    """Extract key parameters from chain."""
    with open(chain_path) as f:
        header = f.readline().strip().replace("#", "").split()
    col_map = {name: i for i, name in enumerate(header)}
    data = np.loadtxt(chain_path, comments="#")
    
    # Use last 50% of chain
    n_burn = len(data) // 2
    mean = {name: np.mean(data[n_burn:, i]) for name, i in col_map.items()}
    std = {name: np.std(data[n_burn:, i]) for name, i in col_map.items()}
    
    # Best fit
    if "minuslogpost" in col_map:
        best_idx = np.argmin(data[:, col_map["minuslogpost"]])
    else:
        best_idx = len(data) // 2
    bf = {name: data[best_idx, i] for name, i in col_map.items()}
    
    return {"bf": bf, "mean": mean, "std": std}

def main():
    base = Path("/Users/steveridder/Git/Ridder-Field/phase3/chains")
    
    chains = [
        "tier6_phenom_baseline",
        "tier6_phenom_shoes", 
        "tier6_phenom_shoes_Hprior",
    ]
    
    print("="*80)
    print("TIER6 PHENOMENOLOGICAL ANALYSIS - Learning from CPL")
    print("="*80)
    
    for name in chains:
        path = base / f"{name}.1.txt"
        if not path.exists():
            continue
            
        params = analyze_chain(path)
        m, s, bf = params["mean"], params["std"], params["bf"]
        
        print(f"\n{name}:")
        print(f"  H0     = {m.get('H0', 0):.2f} ± {s.get('H0', 0):.2f} km/s/Mpc")
        print(f"  sigma8 = {m.get('sigma8', 0):.4f} ± {s.get('sigma8', 0):.4f}")
        print(f"  S8     = {m.get('s8', m.get('S8', 0)):.4f}")
        print(f"  w0     = {m.get('w0_fld', -1):.3f} ± {s.get('w0_fld', 0):.3f}")
        print(f"  wa     = {m.get('wa_fld', 0):.3f} ± {s.get('wa_fld', 0):.3f}")
        
        # Calculate w(z=0) and w(z=1)
        w0 = m.get('w0_fld', -1)
        wa = m.get('wa_fld', 0)
        print(f"  w(z=0) = {w0:.3f}")
        print(f"  w(z=1) = {w0 + wa*0.5:.3f}") 
        print(f"  w(z→∞)= {w0 + wa:.3f}")
        
        # Chi2 info
        if "chi2" in m:
            print(f"  chi2   = {m['chi2']:.1f}")
        if "minuslogpost" in m:
            print(f"  -logP  = {m['minuslogpost']:.1f}")

if __name__ == "__main__":
    main()
