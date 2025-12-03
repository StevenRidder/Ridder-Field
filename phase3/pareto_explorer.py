#!/usr/bin/env python3
"""
PARETO EXPLORER - Multi-dimensional Pareto frontier analysis
Find non-dominated points across ANY set of parameters

Usage:
    python pareto_explorer.py                    # Default: H0↑, S8↓, chi2↓
    python pareto_explorer.py --params H0 S8 rs  # Custom parameters
    python pareto_explorer.py --plot             # Generate visualization
"""

import numpy as np
import glob
import argparse
from collections import defaultdict

# ============================================================
# CONFIGURATION
# ============================================================

# Define optimization directions for common parameters
# +1 = maximize (higher is better)
# -1 = minimize (lower is better)
PARAM_DIRECTIONS = {
    "H0": +1,           # Want higher H0 (toward 73)
    "S8": -1,           # Want lower S8 (toward 0.76)
    "sigma8": -1,       # Want lower sigma8
    "chi2": -1,         # Want lower chi2
    "Omega_m": -1,      # Generally want lower
    "rs_drag": 0,       # Neutral - just track it
    "n_s": 0,           # Neutral
    "omega_cdm": -1,    # Lower helps S8
    "omega_b": 0,       # Neutral
    "tau_reio": 0,      # Neutral
    "ridder_Lambda_EDE_eV": 0,  # Track only
    "ridder_a_c": 0,    # Track only
    "ridder_sigma_lna": 0,      # Track only
}

# Default parameters for Pareto analysis
DEFAULT_PARAMS = ["H0", "S8", "chi2"]

# Chi2 budget for filtering
MAX_DCHI2 = 20.0


def parse_chain(filepath):
    """Parse a chain file and return all parameter values at best-fit point."""
    try:
        with open(filepath, "r") as f:
            header_line = f.readline().strip()
        if header_line.startswith("#"):
            header_line = header_line[1:]
        cols = header_line.split()
        col_map = {name: i for i, name in enumerate(cols)}
        
        data = np.loadtxt(filepath)
        if len(data.shape) < 2 or len(data) < 10:
            return None
        
        # Get best-fit point (minimum -logpost)
        best_idx = np.argmin(data[:, 1])
        
        # Extract all parameters
        result = {"N": len(data)}
        for name, idx in col_map.items():
            result[name] = data[best_idx, idx]
        
        # Compute S8 if not present
        if "S8" not in result and "sigma8" in result and "Omega_m" in result:
            result["S8"] = result["sigma8"] * (result["Omega_m"] / 0.3)**0.5
        
        return result
    except Exception as e:
        return None


def get_world(name):
    """Determine which likelihood world a chain belongs to."""
    name_lower = name.lower()
    if "shoes" in name_lower:
        return "SHOES"
    elif "trgb" in name_lower:
        return "TRGB"
    elif "h71" in name_lower:
        return "H71"
    else:
        return "BASE"


def is_dominated(point_a, point_b, params, directions):
    """
    Check if point_a is dominated by point_b.
    
    point_b dominates point_a if:
    - For all params, b is at least as good as a
    - For at least one param, b is strictly better
    
    Returns True if a is dominated by b.
    """
    dominated_count = 0
    strictly_better = False
    
    for p in params:
        dir = directions.get(p, 0)
        if dir == 0:
            continue  # Skip neutral parameters
        
        val_a = point_a.get(p, float('nan'))
        val_b = point_b.get(p, float('nan'))
        
        if np.isnan(val_a) or np.isnan(val_b):
            continue
        
        # dir = +1 means maximize (higher is better)
        # dir = -1 means minimize (lower is better)
        if dir > 0:
            if val_b >= val_a:
                dominated_count += 1
                if val_b > val_a:
                    strictly_better = True
            else:
                return False  # b is worse in this dimension
        else:
            if val_b <= val_a:
                dominated_count += 1
                if val_b < val_a:
                    strictly_better = True
            else:
                return False  # b is worse in this dimension
    
    return dominated_count > 0 and strictly_better


def find_pareto_front(chains, params, directions):
    """
    Find the Pareto front across the given parameters.
    
    Returns list of non-dominated chain names and their data.
    """
    names = list(chains.keys())
    front = []
    
    for name_a in names:
        point_a = chains[name_a]
        is_dom = False
        
        for name_b in names:
            if name_a == name_b:
                continue
            point_b = chains[name_b]
            
            if is_dominated(point_a, point_b, params, directions):
                is_dom = True
                break
        
        if not is_dom:
            front.append((name_a, point_a))
    
    return front


def compute_tension_score(chain, H0_target=71.0, S8_target=0.76, 
                          alpha=10.0, beta=20.0, ref_chi2=None):
    """Compute tension-aware composite score."""
    H0 = chain.get("H0", 67.5)
    S8 = chain.get("S8", 0.83)
    chi2 = chain.get("chi2", 2800)
    
    dchi2 = chi2 - ref_chi2 if ref_chi2 else 0
    h_term = alpha * (H0 - H0_target)**2
    s_term = beta * (S8 - S8_target)**2
    
    return dchi2 + h_term + s_term


def print_pareto_analysis(world_name, chains, params, directions, ref_chi2=None):
    """Print detailed Pareto analysis for a world."""
    
    # Filter by chi2 budget if reference provided
    if ref_chi2 is not None:
        filtered = {}
        for name, c in chains.items():
            dchi2 = c.get("chi2", 9999) - ref_chi2
            if dchi2 <= MAX_DCHI2:
                filtered[name] = c
        chains = filtered
    
    if not chains:
        print(f"  No chains within Δχ² budget")
        return
    
    # Find Pareto front
    front = find_pareto_front(chains, params, directions)
    
    # Sort by tension score
    if ref_chi2:
        front.sort(key=lambda x: compute_tension_score(x[1], ref_chi2=ref_chi2))
    else:
        front.sort(key=lambda x: x[1].get("chi2", 9999))
    
    # Print header
    print()
    print(f"{'='*90}")
    print(f"PARETO FRONT: {world_name}")
    print(f"Optimizing: {', '.join(p + ('↑' if directions.get(p,0)>0 else '↓' if directions.get(p,0)<0 else '') for p in params)}")
    print(f"{'='*90}")
    
    # Build dynamic header based on params
    header = "%-28s" % "Chain"
    for p in params:
        header += " %8s" % p[:8]
    if ref_chi2:
        header += " %8s %8s" % ("Δχ²", "Score")
    print(header)
    print("-"*90)
    
    # Print each point on the front
    for name, c in front:
        row = "%-28s" % name
        for p in params:
            val = c.get(p, float('nan'))
            if p == "chi2":
                row += " %8.1f" % val
            elif p in ["H0", "rs_drag"]:
                row += " %8.2f" % val
            else:
                row += " %8.4f" % val
        
        if ref_chi2:
            dchi2 = c.get("chi2", 9999) - ref_chi2
            score = compute_tension_score(c, ref_chi2=ref_chi2)
            row += " %+8.1f %8.1f" % (dchi2, score)
        
        print(row)
    
    print()
    print(f"Non-dominated points: {len(front)} / {len(chains)} total")
    
    # Print dominated chains
    dominated = [n for n in chains.keys() if n not in [f[0] for f in front]]
    if dominated and len(dominated) < 10:
        print(f"Dominated: {', '.join(dominated[:5])}" + 
              (f" +{len(dominated)-5} more" if len(dominated) > 5 else ""))


def main():
    parser = argparse.ArgumentParser(description="Multi-dimensional Pareto analysis")
    parser.add_argument("--params", nargs="+", default=DEFAULT_PARAMS,
                        help="Parameters to optimize (default: H0 S8 chi2)")
    parser.add_argument("--world", default=None,
                        help="Filter to specific world (SHOES, BASE, TRGB)")
    parser.add_argument("--budget", type=float, default=MAX_DCHI2,
                        help="Chi2 budget relative to LCDM reference")
    parser.add_argument("--all", action="store_true",
                        help="Show all parameters in output")
    parser.add_argument("--plot", action="store_true",
                        help="Generate 2D scatter plot")
    
    args = parser.parse_args()
    
    # Load all chains
    print("Loading chains...")
    all_chains = {}
    files = sorted(glob.glob("/home/<VM_USER>/Ridder-Field/phase3/chains/tier*.1.txt"))
    
    for f in files:
        name = f.split("/")[-1].replace(".1.txt", "")
        if any(skip in name for skip in ["clean", "opt1", "opt2", "opt3"]):
            continue
        result = parse_chain(f)
        if result:
            result["world"] = get_world(name)
            result["is_lcdm"] = "lcdm" in name.lower()
            all_chains[name] = result
    
    print(f"Loaded {len(all_chains)} chains")
    
    # Get directions for requested params
    directions = {p: PARAM_DIRECTIONS.get(p, 0) for p in args.params}
    
    # Group by world
    worlds = defaultdict(dict)
    for name, c in all_chains.items():
        worlds[c["world"]][name] = c
    
    # Find LCDM references
    lcdm_refs = {}
    for world, chains in worlds.items():
        lcdm_chains = [(n, c) for n, c in chains.items() if c["is_lcdm"] and c["N"] > 50]
        if lcdm_chains:
            best = min(lcdm_chains, key=lambda x: x[1].get("chi2", 9999))
            lcdm_refs[world] = best[1].get("chi2")
    
    # Analyze each world
    if args.world:
        target_worlds = [args.world.upper()]
    else:
        target_worlds = ["SHOES", "BASE", "TRGB", "H71"]
    
    for world in target_worlds:
        if world not in worlds:
            continue
        ref_chi2 = lcdm_refs.get(world)
        print_pareto_analysis(world, worlds[world], args.params, directions, ref_chi2)
    
    # Optional: Generate plot
    if args.plot and len(args.params) >= 2:
        try:
            import matplotlib.pyplot as plt
            
            p1, p2 = args.params[0], args.params[1]
            
            fig, axes = plt.subplots(1, len(target_worlds), figsize=(5*len(target_worlds), 5))
            if len(target_worlds) == 1:
                axes = [axes]
            
            for ax, world in zip(axes, target_worlds):
                if world not in worlds:
                    continue
                
                chains = worlds[world]
                ref_chi2 = lcdm_refs.get(world, 2800)
                
                # Get front
                front = find_pareto_front(chains, args.params, directions)
                front_names = set(f[0] for f in front)
                
                # Plot all points
                for name, c in chains.items():
                    x = c.get(p1, float('nan'))
                    y = c.get(p2, float('nan'))
                    dchi2 = c.get("chi2", 9999) - ref_chi2
                    
                    if np.isnan(x) or np.isnan(y):
                        continue
                    
                    if name in front_names:
                        ax.scatter(x, y, s=100, c='red', edgecolors='black', 
                                   zorder=10, label='Pareto' if name == list(front_names)[0] else '')
                        ax.annotate(name.replace('tier9_', ''), (x, y), 
                                    fontsize=7, rotation=15)
                    else:
                        color = 'gray' if dchi2 > MAX_DCHI2 else 'blue'
                        ax.scatter(x, y, s=30, c=color, alpha=0.5)
                
                ax.set_xlabel(p1)
                ax.set_ylabel(p2)
                ax.set_title(f"{world} World")
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig("pareto_front.png", dpi=150)
            print("\nPlot saved to pareto_front.png")
        except ImportError:
            print("matplotlib not available for plotting")


if __name__ == "__main__":
    main()

