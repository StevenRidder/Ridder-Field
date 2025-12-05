#!/usr/bin/env python3
"""Show key statistics from running/completed chains."""

import sys
import numpy as np
from getdist import loadMCSamples

def show_stats(chain_root):
    """Display key cosmological parameters from chain."""
    try:
        samples = loadMCSamples(chain_root)
    except Exception as e:
        print(f"❌ Cannot load chain: {e}")
        print("   (Chain may still be burning in - no samples saved yet)")
        return

    # Key parameters to show
    params = ['H0', 'omega_b', 'omega_cdm', 'n_s', 'tau_reio', 'sigma8', 'S8', 'Omega_m']
    
    print(f"\n{'='*60}")
    print(f"Chain: {chain_root}")
    print(f"Samples: {samples.numrows}")
    print(f"{'='*60}")
    
    print(f"\n{'Parameter':<15} {'Mean':>12} {'Std':>12} {'68% CI':>20}")
    print("-" * 60)
    
    for p in params:
        try:
            mean = samples.mean(p)
            std = samples.std(p)
            lower, upper = samples.confidence(p, limfrac=0.68)
            print(f"{p:<15} {mean:>12.4f} {std:>12.4f} [{lower:.4f}, {upper:.4f}]")
        except:
            pass  # Parameter not in chain
    
    # Show chi2 if available
    try:
        chi2 = samples.mean('chi2')
        print(f"\nχ² = {chi2:.1f}")
    except:
        pass
    
    # Show convergence
    try:
        from getdist.mcsamples import MCSamplesFromCobaya
        # R-1 from cobaya output would be in progress file
        pass
    except:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default chain
        chain_root = "chains/run_control_planck_only"
    else:
        chain_root = sys.argv[1]
    
    show_stats(chain_root)

