#!/usr/bin/env python3
"""
Tier 5 vs Baseline: Isolating the effect of adding DESI
Compares:
  1. Baseline: Planck + pre-DESI BAO (Paper's geometry-only world)
  2. Tier 5 World A: Planck + pre-DESI BAO + DESI Y1 BAO

Goal: Does adding DESI increase the Planck penalty for EDE?
"""
import numpy as np
import os
import sys

CHAIN_DIR = os.path.expanduser("~/Ridder-Field/phase3/chains")

def load_chain_stats(chain_file):
    try:
        if not os.path.exists(chain_file):
            return None
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
        
        # Best fit sample
        if "chi2" in col_map:
            best_idx = np.argmin(data[:, col_map["chi2"]])
            chi2_best = data[best_idx, col_map["chi2"]]
        else:
            best_idx = np.argmin(data[:, col_map["minuslogpost"]])
            chi2_best = data[best_idx, col_map["minuslogpost"]] * 2
            
        best = data[best_idx]
        
        # Planck high-l chi2
        pl_hl = best[col_map["chi2__planck_2018_highl_plik.TTTEEE"]] if "chi2__planck_2018_highl_plik.TTTEEE" in col_map else np.nan
        
        return {
            "n": len(data),
            "H0": best[col_map["H0"]],
            "rs": best[col_map["rs_drag"]],
            "chi2": chi2_best,
            "chi2_pl_hl": pl_hl
        }
    except Exception:
        return None

chains = {
    "Baseline": {
        "ΛCDM": f"{CHAIN_DIR}/baseline_lcdm_no_desi.1.txt",
        "EDE": f"{CHAIN_DIR}/baseline_ede_no_desi.1.txt"
    },
    "Tier 5 (with DESI)": {
        "ΛCDM": f"{CHAIN_DIR}/tier5_lcdm_desi_unconstrained.1.txt",
        "EDE": f"{CHAIN_DIR}/tier5_ede_desi_convergence.1.txt"
    }
}

print("="*100)
print("ISOLATING DESI'S EFFECT ON PLANCK TENSION")
print("="*100)
print(f"{'World':<20} {'Model':<6} {'N':>5} {'H0':>7} {'r_s':>7} {'χ²_tot':>9} {'Pl_high-l':>10}")
print("-"*100)

results = {}

for world, models in chains.items():
    world_res = {}
    for model, path in models.items():
        stats = load_chain_stats(path)
        if stats:
            print(f"{world:<20} {model:<6} {stats['n']:>5} {stats['H0']:>7.2f} {stats['rs']:>7.1f} {stats['chi2']:>9.1f} {stats['chi2_pl_hl']:>10.1f}")
            world_res[model] = stats
        else:
            print(f"{world:<20} {model:<6} {'---':>5} {'---':>7} {'---':>7} {'---':>9} {'---':>10} (initializing)")
    results[world] = world_res

print("\n" + "="*100)
print("Δχ² ANALYSIS (EDE - ΛCDM)")
print("="*100)

for world, res in results.items():
    if "ΛCDM" in res and "EDE" in res:
        lcdm = res["ΛCDM"]
        ede = res["EDE"]
        
        d_chi2 = ede["chi2"] - lcdm["chi2"]
        d_pl_hl = ede["chi2_pl_hl"] - lcdm["chi2_pl_hl"]
        
        print(f"\n{world}:")
        print(f"  Δχ²_total        = {d_chi2:+.1f}")
        print(f"  Δχ²_Planck_highl = {d_pl_hl:+.1f}")
        print(f"  EDE H0           = {ede['H0']:.2f}")
        
print("\n" + "="*100)
print("HYPOTHESIS TEST")
print("="*100)
print("""
If Δχ²_Planck_highl is significantly LARGER in Tier 5 than Baseline:
  → Adding DESI forces EDE into a corner that Planck hates more.
  
If Δχ²_Planck_highl is SIMILAR in both:
  → Planck hates this EDE geometry (~1.5% r_s shift) regardless of DESI.
  → The penalty is fundamental to the EDE model, not caused by DESI.
""")
print("="*100)
