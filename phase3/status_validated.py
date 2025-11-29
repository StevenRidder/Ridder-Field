#!/usr/bin/env python3
"""
TENSION DASHBOARD - H0 + S8 + chi2 all in one view
Compares each model to LCDM in same world
Now with PARETO FRONTIER analysis for tension resolution!
"""
import numpy as np
import glob
import subprocess

# ============================================================
# PARETO FRONTIER CONFIGURATION
# ============================================================
H0_TARGET = 71.0    # What we want H0 to be (TRGB/DESI concordance)
S8_TARGET = 0.76    # What we want S8 to be (weak lensing)
ALPHA = 10.0        # Penalty weight for H0 deviation
BETA = 20.0         # Penalty weight for S8 deviation
MAX_DCHI2 = 15.0    # Chi2 budget for Pareto analysis

def tension_score(H0, S8, dchi2):
    """
    Composite tension-aware score.
    LOWER is BETTER (like chi2).
    Score = Δχ² + α(H0-71)² + β(S8-0.76)²
    """
    if np.isnan(S8):
        S8 = 0.83  # assume LCDM-like if missing
    h_term = ALPHA * (H0 - H0_TARGET)**2
    s_term = BETA * (S8 - S8_TARGET)**2
    return dchi2 + h_term + s_term

def pareto_frontier_H0_S8(chains_list, ref_chi2, max_dchi2):
    """
    Find the Pareto front in (H0↑, S8↓) space under a χ² budget.
    
    A chain is NON-DOMINATED if no other chain within budget has:
    - H0 >= this H0
    - S8 <= this S8  
    - dchi2 <= this dchi2
    with at least one strict inequality.
    
    Returns list of non-dominated chains.
    """
    # Filter by chi2 budget
    candidates = []
    for name, c in chains_list:
        dchi2 = c["chi2"] - ref_chi2
        if dchi2 <= max_dchi2:
            cand = {
                "name": name,
                "H0": c["H0"],
                "S8": c["S8"] if not np.isnan(c["S8"]) else 0.83,
                "chi2": c["chi2"],
                "dchi2": dchi2,
                "running": c.get("running", False),
                "N": c.get("N", 0),
            }
            cand["score"] = tension_score(cand["H0"], cand["S8"], dchi2)
            candidates.append(cand)
    
    if not candidates:
        return []
    
    # Find non-dominated points
    front = []
    for a in candidates:
        dominated = False
        for b in candidates:
            if b["name"] == a["name"]:
                continue
            # b dominates a if b is >= in H0, <= in S8, <= in dchi2, with at least one strict
            if (b["H0"] >= a["H0"] and 
                b["S8"] <= a["S8"] and 
                b["dchi2"] <= a["dchi2"] and
                (b["H0"] > a["H0"] or b["S8"] < a["S8"] or b["dchi2"] < a["dchi2"])):
                dominated = True
                break
        if not dominated:
            front.append(a)
    
    # Sort by tension score (best first)
    front.sort(key=lambda c: c["score"])
    return front

def print_pareto_section(world, chains_list, ref_chi2):
    """Print Pareto front analysis for a world."""
    front = pareto_frontier_H0_S8(chains_list, ref_chi2, MAX_DCHI2)
    
    if not front:
        print(f"  (No chains within Δχ² ≤ {MAX_DCHI2} budget)")
        return
    
    print()
    print(f"  PARETO FRONT (Δχ² ≤ {MAX_DCHI2}) - Cannot improve H0/S8 without worse χ²:")
    print("  " + "-"*75)
    print("  %-26s %5s %6s %6s %7s %8s" % ("Chain", "H0", "S8", "Δχ²", "Score", "Verdict"))
    print("  " + "-"*75)
    
    for i, c in enumerate(front):
        marker = "→" if c["running"] else " "
        
        # Verdict based on position
        if i == 0:
            verdict = "★ BEST OVERALL"
        elif c["H0"] >= 70.5 and c["S8"] <= 0.80:
            verdict = "✓ TENSION SOLVER"
        elif c["dchi2"] < 0:
            verdict = "χ² WINNER"
        else:
            verdict = "FRONTIER"
        
        print("  %s%-25s %5.1f %6.3f %+6.1f %8.1f  %s" % (
            marker, c["name"], c["H0"], c["S8"], c["dchi2"], c["score"], verdict))

def get_running_chains():
    try:
        out = subprocess.check_output("ps aux | grep cobaya | grep -v grep", shell=True).decode()
        running = set()
        for line in out.strip().split("\n"):
            if "tier" in line:
                parts = line.split()
                for p in parts:
                    if "tier" in p and ".yaml" in p:
                        name = p.replace(".yaml", "").split("/")[-1]
                        running.add(name)
        return running
    except:
        return set()

def parse_chain(filepath):
    with open(filepath, "r") as f:
        header_line = f.readline().strip()
    if header_line.startswith("#"):
        header_line = header_line[1:]
    cols = header_line.split()
    col_map = {name: i for i, name in enumerate(cols)}
    
    try:
        data = np.loadtxt(filepath)
        if len(data.shape) < 2 or len(data) == 0:
            return None
    except:
        return None
    
    best_idx = np.argmin(data[:, 1])
    
    s8 = float("nan")
    if "S8" in col_map:
        s8 = data[best_idx, col_map["S8"]]
    elif "sigma8" in col_map and "Omega_m" in col_map:
        sig8 = data[best_idx, col_map["sigma8"]]
        om = data[best_idx, col_map["Omega_m"]]
        s8 = sig8 * (om / 0.3)**0.5
    
    return {
        "N": len(data),
        "H0": data[best_idx, col_map.get("H0", 4)],
        "rs": data[best_idx, col_map.get("rs_drag", 30)],
        "S8": s8,
        "chi2": data[best_idx, col_map.get("chi2", 36)],
    }

def get_world(name):
    if "shoes" in name.lower():
        return "SHOES"
    elif "trgb" in name.lower():
        return "TRGB"
    else:
        return "BASE"

def grade(dchi2, dH0, dS8):
    score = 0
    label = []
    
    if dchi2 < -5:
        score += 2
        label.append("X2--")
    elif dchi2 < -1:
        score += 1
        label.append("X2-")
    elif dchi2 > 10:
        score -= 2
        label.append("X2++")
    elif dchi2 > 3:
        score -= 1
        label.append("X2+")
    
    if dH0 > 2:
        score += 1
        label.append("H0+")
    elif dH0 < -1:
        score -= 1
        label.append("H0-")
    
    if not np.isnan(dS8):
        if dS8 < -0.02:
            score += 1
            label.append("S8-")
        elif dS8 > 0.02:
            score -= 1
            label.append("S8+")
    
    if score >= 2:
        g = "**"
    elif score >= 1:
        g = "*"
    elif score <= -2:
        g = "XX"
    elif score <= -1:
        g = "X"
    else:
        g = "~"
    
    return g, " ".join(label) if label else "~"

skip = ["clean", "opt1", "opt2", "opt3"]
running = get_running_chains()

chains = {}
files = sorted(glob.glob("/home/ridderadmin/Ridder-Field/phase3/chains/tier*.1.txt"))
for f in files:
    name = f.split("/")[-1].replace(".1.txt", "")
    if any(s in name for s in skip):
        continue
    result = parse_chain(f)
    if result is None:
        continue
    result["running"] = name in running
    result["world"] = get_world(name)
    result["is_lcdm"] = "lcdm" in name.lower()
    chains[name] = result

lcdm_ref = {}
for world in ["BASE", "SHOES", "TRGB"]:
    lcdm_chains = [(n, c) for n, c in chains.items() 
                   if c["world"] == world and c["is_lcdm"] and c["N"] > 50]
    if lcdm_chains:
        best = min(lcdm_chains, key=lambda x: x[1]["chi2"])
        lcdm_ref[world] = best[1]

print("="*95)
print("TENSION DASHBOARD - Delta values vs LCDM in same world")
print("="*95)

for world in ["BASE", "SHOES", "TRGB"]:
    world_chains = [(n, c) for n, c in chains.items() if c["world"] == world]
    if not world_chains:
        continue
    
    world_chains.sort(key=lambda x: x[1]["chi2"])
    
    ref = lcdm_ref.get(world)
    if ref:
        ref_str = "(ref: X2=%.1f, H0=%.1f, S8=%.3f)" % (ref["chi2"], ref["H0"], ref["S8"]) if not np.isnan(ref["S8"]) else "(ref: X2=%.1f, H0=%.1f)" % (ref["chi2"], ref["H0"])
    else:
        ref_str = "(no LCDM ref yet)"
    
    print()
    print("-"*95)
    print("WORLD: %s %s" % (world, ref_str))
    print("-"*95)
    print("%-24s %s %5s %6s %6s %6s %8s | %6s %5s %6s | %s" % (
        "Chain", "*", "N", "H0", "rs", "S8", "chi2", "dX2", "dH0", "dS8", "Grade"))
    print("-"*95)
    
    for name, c in world_chains:
        marker = "*" if c["running"] else " "
        s8_str = "%6.3f" % c["S8"] if not np.isnan(c["S8"]) else "  n/a "
        
        if ref and not c["is_lcdm"]:
            dchi2 = c["chi2"] - ref["chi2"]
            dH0 = c["H0"] - ref["H0"]
            dS8 = c["S8"] - ref["S8"] if not np.isnan(c["S8"]) and not np.isnan(ref["S8"]) else float("nan")
            g, detail = grade(dchi2, dH0, dS8)
            dchi2_str = "%+6.1f" % dchi2
            dH0_str = "%+5.1f" % dH0
            dS8_str = "%+6.3f" % dS8 if not np.isnan(dS8) else "  n/a "
        else:
            dchi2_str = "  REF" if c["is_lcdm"] else "  n/a"
            dH0_str = " REF" if c["is_lcdm"] else " n/a"
            dS8_str = "  REF " if c["is_lcdm"] else "  n/a "
            g, detail = ("REF", "") if c["is_lcdm"] else ("?", "")
        
        print("%-24s %s %5d %6.1f %6.2f %s %8.1f | %6s %5s %6s | %-2s %s" % (
            name, marker, c["N"], c["H0"], c["rs"], s8_str, c["chi2"],
            dchi2_str, dH0_str, dS8_str, g, detail))

    # Print Pareto front for this world
    if ref:
        print_pareto_section(world, world_chains, ref["chi2"])

# ============================================================
# FINAL SUMMARY
# ============================================================
print()
print("="*95)
print("SUMMARY")
print("="*95)
print()
print("Running: %d chains" % len(running))
print()
print("Scoring: Score = Δχ² + %.0f*(H0-%.1f)² + %.0f*(S8-%.2f)²" % (ALPHA, H0_TARGET, BETA, S8_TARGET))
print("         Lower score = better tension resolution")
print()
print("Interpretation:")
print("  • Δχ² < 0:  Fits data BETTER than ΛCDM (rare, valuable)")
print("  • Δχ² 0-10: Acceptable trade-off for tension resolution")
print("  • Δχ² > 15: Too expensive, model disfavored")
print()
print("Targets: H0 → 71 (TRGB/DESI concordance), S8 → 0.76 (weak lensing)")
print("="*95)
