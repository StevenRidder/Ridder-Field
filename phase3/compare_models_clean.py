#!/usr/bin/env python3
"""
Clean Model Comparison Script
=============================
Separates likelihood χ² from priors and computes proper AIC/BIC.

This script reads chains directly via getdist and produces:
- Likelihood-only χ² (for AIC/BIC)
- Raw posterior χ² (what the sampler minimized)
- Δχ², ΔAIC, ΔBIC relative to ΛCDM
- Pareto front tagging in (H₀, S₈, χ²)

Usage:
    python3 compare_models_clean.py
"""

import numpy as np
from math import log
import glob
import os

try:
    from getdist import loadMCSamples
    HAS_GETDIST = True
except ImportError:
    HAS_GETDIST = False
    print("WARNING: getdist not available, using raw file parsing")

# Effective data count (dominated by Planck ~2500 + BAO ~10 + SH0ES ~1)
N_DATA = 2600
LOG_N_DATA = log(N_DATA)

# Chain definitions: (pattern, model_name, world, k)
CHAIN_CONFIGS = [
    # SHOES world
    ("tier10_lcdm_ref_shoes_*", "ΛCDM", "shoes", 6),
    ("tier10_cpl_control_shoes_*", "w₀wₐCDM", "shoes", 8),
    ("tier10_ede_minimal_gold_shoes_*", "ϕCDM", "shoes", 8),
    ("tier10_ede_highH0_shoes", "ϕCDM-H71", "shoes", 8),
    # BASE world
    ("tier10_ede_minimal_base", "ϕCDM", "base", 8),
    # TRGB world  
    ("tier10_ede_minimal_trgb", "ϕCDM", "trgb", 8),
]


def load_chain_getdist(chain_path):
    """Load chain using getdist and extract best-fit info."""
    try:
        # Remove trailing wildcards and .1.txt suffix for getdist
        base_path = chain_path.replace("_*", "_1").replace(".1.txt", "")
        if base_path.endswith("_"):
            base_path = base_path[:-1]
        
        samples = loadMCSamples(base_path, no_cache=True)
        p = samples.getParams()
        
        # Find best chi2_lik (likelihood only)
        best_lik_idx = np.argmin(p.chi2)
        
        # Compute raw posterior (chi2 + 2*prior)
        raw_posterior = p.chi2 + 2 * p.minuslogprior
        best_raw_idx = np.argmin(raw_posterior)
        
        return {
            "file": base_path,
            "n_samples": len(p.chi2),
            # At best likelihood point
            "chi2_lik": float(p.chi2[best_lik_idx]),
            "chi2_lik_CMB": float(p.chi2__CMB[best_lik_idx]) if hasattr(p, 'chi2__CMB') else 0,
            "chi2_lik_BAO": float(p.chi2__BAO[best_lik_idx]) if hasattr(p, 'chi2__BAO') else 0,
            "chi2_lik_SH0ES": float(p.chi2__sh0es_h0[best_lik_idx]) if hasattr(p, 'chi2__sh0es_h0') else 0,
            "prior_at_best_lik": float(p.minuslogprior[best_lik_idx]),
            "H0_at_best_lik": float(p.H0[best_lik_idx]),
            "S8_at_best_lik": float(p.S8[best_lik_idx]),
            # At best raw posterior point (what status script shows)
            "chi2_raw": float(raw_posterior[best_raw_idx]),
            "chi2_lik_at_raw": float(p.chi2[best_raw_idx]),
            "prior_at_raw": float(p.minuslogprior[best_raw_idx]),
            "H0_at_raw": float(p.H0[best_raw_idx]),
            "S8_at_raw": float(p.S8[best_raw_idx]),
            # Posterior means
            "H0_mean": float(np.mean(p.H0)),
            "S8_mean": float(np.mean(p.S8)),
        }
    except Exception as e:
        return None


def load_chain_raw(chain_file):
    """Fallback: load chain from raw .txt file."""
    try:
        data = np.loadtxt(chain_file)
        # Column 0: weight, Column 1: -logpost (= chi2/2 + prior)
        raw_col = data[:, 1] * 2
        best_idx = np.argmin(raw_col)
        
        return {
            "file": chain_file,
            "n_samples": len(data),
            "chi2_raw": float(raw_col[best_idx]),
            # Can't separate lik/prior without getdist
            "chi2_lik": float(raw_col[best_idx]),  # Approximation
        }
    except:
        return None


def load_all_chains(chains_dir="chains"):
    """Load all configured chains."""
    records = []
    
    for pattern, model, world, k in CHAIN_CONFIGS:
        # Find matching chain files
        full_pattern = os.path.join(chains_dir, pattern)
        
        if "*" in pattern:
            # Multiple chains (e.g., _1, _2, _3, _4)
            base = pattern.replace("_*", "")
            for i in range(1, 10):
                chain_path = os.path.join(chains_dir, f"{base}_{i}")
                if os.path.exists(f"{chain_path}.1.txt"):
                    if HAS_GETDIST:
                        result = load_chain_getdist(chain_path)
                    else:
                        result = load_chain_raw(f"{chain_path}.1.txt")
                    
                    if result:
                        result["model"] = model
                        result["world"] = world
                        result["k"] = k
                        result["chain_id"] = i
                        records.append(result)
        else:
            # Single chain
            chain_path = os.path.join(chains_dir, pattern)
            if os.path.exists(f"{chain_path}.1.txt"):
                if HAS_GETDIST:
                    result = load_chain_getdist(chain_path)
                else:
                    result = load_chain_raw(f"{chain_path}.1.txt")
                
                if result:
                    result["model"] = model
                    result["world"] = world
                    result["k"] = k
                    result["chain_id"] = 1
                    records.append(result)
    
    return records


def reduce_best_by_model(records):
    """For each (world, model, k), pick the sample with minimum chi2_lik."""
    best = {}
    for r in records:
        key = (r["world"], r["model"], r["k"])
        if key not in best or r["chi2_lik"] < best[key]["chi2_lik"]:
            best[key] = r
    return list(best.values())


def compute_model_comparison(best_records):
    """Compute Δχ², ΔAIC, ΔBIC relative to ΛCDM within each world."""
    by_world = {}
    for r in best_records:
        by_world.setdefault(r["world"], []).append(r)
    
    out = []
    for world, recs in by_world.items():
        # Find ΛCDM reference
        lcdm_recs = [r for r in recs if "ΛCDM" in r["model"] or "lcdm" in r["model"].lower()]
        if not lcdm_recs:
            # No LCDM in this world, use first record as reference
            lcdm_ref = min(recs, key=lambda r: r["chi2_lik"])
        else:
            lcdm_ref = min(lcdm_recs, key=lambda r: r["chi2_lik"])
        
        chi2_ref = lcdm_ref["chi2_lik"]
        k_ref = lcdm_ref["k"]
        
        for r in recs:
            dchi2 = r["chi2_lik"] - chi2_ref
            dk = r["k"] - k_ref
            dAIC = 2.0 * dk + dchi2
            dBIC = dk * LOG_N_DATA + dchi2
            
            rr = dict(r)
            rr["chi2_ref"] = chi2_ref
            rr["dchi2_lik"] = dchi2
            rr["dAIC"] = dAIC
            rr["dBIC"] = dBIC
            
            # Also compute raw deltas for comparison
            if "chi2_raw" in r and "chi2_raw" in lcdm_ref:
                rr["dchi2_raw"] = r["chi2_raw"] - lcdm_ref["chi2_raw"]
            
            out.append(rr)
    
    return out


def is_dominated(a, b):
    """
    Return True if model b dominates model a:
    H0(b) >= H0(a), S8(b) <= S8(a), chi2(b) <= chi2(a)
    with at least one strict.
    """
    h0_a = a.get("H0_at_best_lik", a.get("H0_mean", 0))
    h0_b = b.get("H0_at_best_lik", b.get("H0_mean", 0))
    s8_a = a.get("S8_at_best_lik", a.get("S8_mean", 0))
    s8_b = b.get("S8_at_best_lik", b.get("S8_mean", 0))
    
    cond1 = h0_b >= h0_a
    cond2 = s8_b <= s8_a
    cond3 = b["chi2_lik"] <= a["chi2_lik"]
    
    if not (cond1 and cond2 and cond3):
        return False
    
    strict = (h0_b > h0_a) or (s8_b < s8_a) or (b["chi2_lik"] < a["chi2_lik"])
    return strict


def tag_pareto_front(records, chi2_budget=10.0):
    """Tag each record with Pareto front status."""
    groups = {}
    for r in records:
        key = (r["world"], r["k"])
        groups.setdefault(key, []).append(r)
    
    for key, recs in groups.items():
        for r in recs:
            r["within_budget"] = (r["dchi2_lik"] <= chi2_budget)
        
        active = [r for r in recs if r["within_budget"]]
        
        for r in recs:
            r["pareto"] = False
        
        for i, a in enumerate(active):
            dominated = False
            for j, b in enumerate(active):
                if i == j:
                    continue
                if is_dominated(a, b):
                    dominated = True
                    break
            if not dominated:
                a["pareto"] = True
    
    return records


def print_world_table(records, world="shoes"):
    """Print formatted table for a world."""
    rows = [r for r in records if r["world"] == world]
    if not rows:
        print(f"\nWORLD: {world.upper()} - No chains found")
        return
    
    rows = sorted(rows, key=lambda r: (r["k"], r["model"]))
    
    print(f"\n{'='*100}")
    print(f"WORLD: {world.upper()}")
    print(f"{'='*100}")
    print(f"{'Model':<12} k  {'χ²_lik':>10} {'Δχ²_lik':>8} {'Δχ²_raw':>8} {'ΔAIC':>8} {'ΔBIC':>8} {'H0':>6} {'S8':>6} P  B")
    print("-" * 100)
    
    for r in rows:
        flag_p = "*" if r.get("pareto", False) else " "
        flag_b = "Y" if r.get("within_budget", False) else "N"
        
        h0 = r.get("H0_at_best_lik", r.get("H0_mean", 0))
        s8 = r.get("S8_at_best_lik", r.get("S8_mean", 0))
        dchi2_raw = r.get("dchi2_raw", 0)
        
        print(
            f"{r['model']:<12} {r['k']:>1d}  "
            f"{r['chi2_lik']:>10.1f} {r['dchi2_lik']:>+8.1f} {dchi2_raw:>+8.1f} "
            f"{r['dAIC']:>+8.1f} {r['dBIC']:>+8.1f} "
            f"{h0:>6.2f} {s8:>6.3f} {flag_p}  {flag_b}"
        )


def print_interpretation():
    """Print interpretation guide."""
    print("\n" + "=" * 100)
    print("INTERPRETATION GUIDE")
    print("=" * 100)
    print("""
Columns:
  χ²_lik    = Likelihood chi-squared (CMB + BAO + SH0ES) - USE THIS FOR AIC/BIC
  Δχ²_lik   = Difference from ΛCDM in likelihood chi-squared
  Δχ²_raw   = Difference from ΛCDM in raw posterior (what status script shows)
  ΔAIC      = Δχ²_lik + 2*Δk (lower is better)
  ΔBIC      = Δχ²_lik + Δk*ln(N) (lower is better)
  P         = On Pareto front (* = yes)
  B         = Within χ² budget (Y/N)

BIC Thresholds (Kass & Raftery):
  |ΔBIC| < 2:   Not worth mentioning
  2 ≤ |ΔBIC| < 6:   Positive evidence
  6 ≤ |ΔBIC| < 10:  Strong evidence
  |ΔBIC| ≥ 10:  Very strong evidence

Key insight:
  - Δχ²_lik is what matters for statistical model comparison
  - Δχ²_raw includes prior penalties which differ between models
  - If Δχ²_raw < Δχ²_lik, the model has lower prior penalty than ΛCDM
""")


def main():
    print("=" * 100)
    print("CLEAN MODEL COMPARISON - Likelihood vs Prior Separation")
    print("=" * 100)
    
    # Load all chains
    print("\nLoading chains...")
    records = load_all_chains()
    print(f"Loaded {len(records)} chain records")
    
    if not records:
        print("ERROR: No chains found!")
        return
    
    # Reduce to best per model
    best = reduce_best_by_model(records)
    print(f"Reduced to {len(best)} best-fit points (one per model/world)")
    
    # Compute deltas
    comp = compute_model_comparison(best)
    
    # Tag Pareto
    tagged = tag_pareto_front(comp, chi2_budget=15.0)
    
    # Print tables
    for world in ["shoes", "base", "trgb"]:
        print_world_table(tagged, world)
    
    # Print interpretation
    print_interpretation()
    
    # Summary
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    
    shoes_recs = [r for r in tagged if r["world"] == "shoes"]
    if shoes_recs:
        lcdm = next((r for r in shoes_recs if "ΛCDM" in r["model"]), None)
        ede = next((r for r in shoes_recs if "ϕCDM" in r["model"] and "H71" not in r["model"]), None)
        
        if lcdm and ede:
            print(f"\nSH0ES World Comparison:")
            print(f"  ΛCDM:  χ²_lik = {lcdm['chi2_lik']:.1f}, H0 = {lcdm.get('H0_at_best_lik', 0):.2f}")
            print(f"  ϕCDM:  χ²_lik = {ede['chi2_lik']:.1f}, H0 = {ede.get('H0_at_best_lik', 0):.2f}")
            print(f"  Δχ²_lik = {ede['dchi2_lik']:+.1f} (+ means ΛCDM wins)")
            print(f"  ΔAIC = {ede['dAIC']:+.1f}")
            print(f"  ΔBIC = {ede['dBIC']:+.1f}")


if __name__ == "__main__":
    main()

