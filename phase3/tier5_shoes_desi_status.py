#!/usr/bin/env python3
"""
Tier 5 Status Dashboard - Universal
Monitors ALL Tier 5 chains currently running.
"""
import numpy as np
import glob
import os
import sys

# Allow running on VM via SSH
CHAIN_DIR = os.path.expanduser("~/Ridder-Field/phase3/chains")
if not os.path.exists(CHAIN_DIR):
    CHAIN_DIR = "chains"

print("="*110)
print("TIER 5: DESI Y1 BAO — LIVE STATUS")
print("="*110)
print("Monitoring all Tier 5 chains in:", CHAIN_DIR)
print("="*110)

def load_chain(chain_file):
    """Load chain and extract key statistics"""
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
        if len(data) < 5:
            return None

        n_samples = len(data)

        # H0
        H0 = np.mean(data[:, col_map["H0"]])
        H0_std = np.std(data[:, col_map["H0"]])

        # S8 (may be derived or direct)
        if "S8" in col_map:
            S8 = np.mean(data[:, col_map["S8"]])
        elif "sigma8" in col_map and "Omega_m" in col_map:
            S8 = np.mean(
                data[:, col_map["sigma8"]] * np.sqrt(data[:, col_map["Omega_m"]] / 0.3)
            )
        else:
            S8 = np.nan

        # r_s (sound horizon) - in Mpc
        if "rs_drag" in col_map:
            rs = np.mean(data[:, col_map["rs_drag"]])
        elif "rdrag" in col_map:
            rs = np.mean(data[:, col_map["rdrag"]])
        else:
            rs = np.nan

        # Best-fit chi2
        if "chi2" in col_map:
            best_idx = np.argmin(data[:, col_map["chi2"]])
            chi2_best = data[best_idx, col_map["chi2"]]
        else:
            best_idx = np.argmin(data[:, col_map["minuslogpost"]])
            chi2_best = data[best_idx, col_map["minuslogpost"]] * 2

        return {
            "n": n_samples,
            "H0": H0,
            "H0_std": H0_std,
            "S8": S8,
            "rs": rs,
            "chi2": chi2_best,
        }
    except Exception as e:
        print(f"   ⚠️ Error loading {os.path.basename(chain_file)}: {e}")
        return None

# Find ALL tier5 chains
chain_files = glob.glob(f"{CHAIN_DIR}/tier5_*.1.txt")
chain_files = sorted(chain_files)

print(f"\n📂 Found {len(chain_files)} chain files:")
for f in chain_files:
    print(f"   - {os.path.basename(f)}")

if not chain_files:
    print("\n⚠️  No Tier 5 chains found yet.")
    print(f"   Looking in: {CHAIN_DIR}")
    sys.exit(0)

# Group chains by world (DESI-only vs DESI+Pantheon)
world_a = {}  # DESI only
world_b = {}  # DESI + Pantheon

for f in chain_files:
    name = os.path.basename(f).replace(".1.txt", "")
    data = load_chain(f)
    name_lower = name.lower()
    
    # Determine model type
    if "lcdm" in name_lower:
        model = "ΛCDM (k=6)"
    elif "cpl" in name_lower:
        model = "CPL (k=8)"
    elif "ede" in name_lower:
        model = "EDE (k=8)"
    else:
        model = name
    
    # Determine world
    if "pantheon" in name_lower:
        world_b[model] = {"name": name, "data": data}
    else:
        world_a[model] = {"name": name, "data": data}

def print_world(world_name, chains):
    if not chains:
        return {}
    
    print(f"\n{'='*110}")
    print(f"📊 {world_name}")
    print(f"{'='*110}")
    print(f"{'Model':<12} {'Chain':<40} {'N':>6} {'H0':>7} {'±σ':>5} {'S8':>6} {'r_s':>7} {'χ²':>9} {'Status':<10}")
    print("-"*110)
    
    results = {}
    for model, info in chains.items():
        name = info["name"]
        data = info["data"]
        
        if data is None:
            print(f"{model:<12} {name:<40} {'---':>6} {'---':>7} {'---':>5} {'---':>6} {'---':>7} {'---':>9} 🔄 Init")
            continue
        
        results[model] = data
        
        if data["n"] >= 2500:
            status = "✅ Ready"
        elif data["n"] >= 1500:
            status = "✅ >1500"
        elif data["n"] >= 500:
            status = "🔄 >500"
        elif data["n"] >= 100:
            status = "🔄 Running"
        else:
            status = "🔄 Start"
        
        rs_str = f"{data['rs']:.1f}" if not np.isnan(data["rs"]) else "---"
        S8_str = f"{data['S8']:.3f}" if not np.isnan(data["S8"]) else "---"
        
        print(f"{model:<12} {name:<40} {data['n']:>6} {data['H0']:>7.2f} {data['H0_std']:>5.2f} {S8_str:>6} {rs_str:>7} {data['chi2']:>9.1f} {status}")
    
    return results

results_a = print_world("World A: DESI Y1 Only (no Pantheon+)", world_a)
results_b = print_world("World B: DESI Y1 + Pantheon+", world_b)

# Summary
total_samples = sum(d["n"] for d in results_a.values()) + sum(d["n"] for d in results_b.values())
print(f"\n{'='*110}")
print(f"📈 SUMMARY: {len(chain_files)} chains, {total_samples} total samples")
print(f"{'='*110}")

# Δχ² Analysis per world
def analyze_world(world_name, results):
    if not results or "ΛCDM (k=6)" not in results:
        return
    
    ref = results["ΛCDM (k=6)"]
    print(f"\n📐 Δχ² ANALYSIS: {world_name} (ref: ΛCDM χ²={ref['chi2']:.1f})")
    print(f"{'Model':<15} {'Δχ²':>8} {'H0':>7} {'ΔH0':>6} {'r_s':>7} {'Δr_s':>6} {'Δr_s%':>7}")
    print("-"*60)
    
    for model, data in results.items():
        dchi2 = data["chi2"] - ref["chi2"]
        dH0 = data["H0"] - ref["H0"]
        drs = data["rs"] - ref["rs"] if not np.isnan(data["rs"]) and not np.isnan(ref["rs"]) else np.nan
        drs_pct = (drs / ref["rs"] * 100) if not np.isnan(drs) else np.nan
        
        drs_str = f"{drs:+.1f}" if not np.isnan(drs) else "---"
        drs_pct_str = f"{drs_pct:+.1f}%" if not np.isnan(drs_pct) else "---"
        
        print(f"{model:<15} {dchi2:>+8.1f} {data['H0']:>7.2f} {dH0:>+6.2f} {data['rs']:>7.1f} {drs_str:>6} {drs_pct_str:>7}")

analyze_world("World A: DESI Only", results_a)
analyze_world("World B: DESI+Pantheon", results_b)

# Quick verdict
print(f"\n{'='*110}")
print("🎯 QUICK VERDICT")
print("="*110)

for world_name, results in [("World A", results_a), ("World B", results_b)]:
    if "EDE (k=8)" in results and "ΛCDM (k=6)" in results:
        ede = results["EDE (k=8)"]
        lcdm = results["ΛCDM (k=6)"]
        dchi2 = ede["chi2"] - lcdm["chi2"]
        drs_pct = (ede["rs"] - lcdm["rs"]) / lcdm["rs"] * 100
        
        print(f"\n{world_name}:")
        print(f"   EDE: H₀={ede['H0']:.1f}, r_s={ede['rs']:.1f} Mpc ({drs_pct:+.1f}% vs ΛCDM)")
        print(f"   Δχ² = {dchi2:+.0f}")
        
        if dchi2 > 50:
            print(f"   💀 DESI crushes this EDE regime (Δχ² >> 10)")
        elif dchi2 > 10:
            print(f"   ⚠️ Significant χ² penalty")
        else:
            print(f"   ✅ Viable")

print(f"\n{'='*110}")
print("Target: 1500-2500 samples per chain for stable estimates")
print("="*110)
