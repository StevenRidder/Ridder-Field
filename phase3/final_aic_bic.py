#!/usr/bin/env python3
"""
Final AIC/BIC Analysis for Paper
All chains standardized to N=1000
"""
import numpy as np

print("="*95)
print("FINAL AIC/BIC ANALYSIS - All Chains N=1000")
print("="*95)

n_data = 2600  # approximate Planck+BAO data points

def load_chain(name):
    fname = f"chains/{name}.1.txt"
    with open(fname, "r") as f:
        header = f.readline().strip()
    if header.startswith("#"):
        header = header[1:]
    cols = header.split()
    col_map = {c: i for i, c in enumerate(cols)}
    data = np.loadtxt(fname)
    
    H0 = np.mean(data[:, col_map["H0"]])
    if "S8" in col_map:
        S8 = np.mean(data[:, col_map["S8"]])
    else:
        S8 = np.mean(data[:, col_map["sigma8"]] * np.sqrt(data[:, col_map["Omega_m"]]/0.3))
    
    best_idx = np.argmin(data[:, 1])
    chi2_best = data[best_idx, 1] * 2
    
    return {"H0": H0, "S8": S8, "chi2": chi2_best, "n": len(data)}

def compute_aic_bic(chi2, k, n_data):
    aic = 2*k + chi2
    bic = k * np.log(n_data) + chi2
    return aic, bic

# Chains with parameter counts
chains = {
    "tier9_lcdm_shoes": ("LCDM", 6, "SHOES"),
    "tier9_phenom_shoes": ("CPL", 8, "SHOES"),
    "tier9_v3_shoes_fresh": ("EDE(k=9)", 9, "SHOES"),
    "tier9_v3_shoes_wide_ocdm": ("EDE(k=9)", 9, "SHOES"),
    "tier9_v3_shoes_minimal": ("EDE(k=8)", 8, "SHOES"),
    "tier9_v3_shoes_optimal": ("EDE(k=9)", 9, "SHOES"),
    "tier9_lcdm_baseline": ("LCDM", 6, "BASE"),
    "tier9_phenom_baseline": ("CPL", 8, "BASE"),
    "tier9_v3_baseline": ("EDE(k=9)", 9, "BASE"),
    "tier9_v3_baseline_minimal": ("EDE(k=8)", 8, "BASE"),
    "tier9_lcdm_trgb": ("LCDM", 6, "TRGB"),
    "tier9_v3_trgb": ("EDE(k=9)", 9, "TRGB"),
}

# Load all chains
results = {}
for name, (model, k, world) in chains.items():
    try:
        data = load_chain(name)
        data["model"] = model
        data["k"] = k
        data["world"] = world
        data["name"] = name
        results[name] = data
    except Exception as e:
        print(f"Error loading {name}: {e}")

# Print by world
for world in ["SHOES", "BASE", "TRGB"]:
    print()
    print("=" * 95)
    print(f"WORLD: {world}")
    print("=" * 95)
    
    world_chains = {k: v for k, v in results.items() if v["world"] == world}
    if not world_chains:
        continue
    
    ref_name = [k for k, v in world_chains.items() if v["model"] == "LCDM"]
    if not ref_name:
        continue
    ref = world_chains[ref_name[0]]
    ref_chi2 = ref["chi2"]
    ref_aic, ref_bic = compute_aic_bic(ref_chi2, ref["k"], n_data)
    
    print()
    print("%-12s %-28s %2s %8s %7s %6s %6s %7s %7s" % 
          ("Model", "Chain", "k", "chi2", "Dchi2", "H0", "S8", "DAIC", "DBIC"))
    print("-" * 95)
    
    for name, data in sorted(world_chains.items(), key=lambda x: x[1]["chi2"]):
        aic, bic = compute_aic_bic(data["chi2"], data["k"], n_data)
        dchi2 = data["chi2"] - ref_chi2
        daic = aic - ref_aic
        dbic = bic - ref_bic
        
        marker = ""
        if data["model"] == "LCDM":
            marker = " [REF]"
        elif data["model"] == "EDE(k=8)":
            marker = " ***"
        
        print("%-12s %-28s %2d %8.1f %+7.1f %6.2f %6.3f %+7.1f %+7.1f%s" % 
              (data["model"], name, data["k"], data["chi2"], dchi2, 
               data["H0"], data["S8"], daic, dbic, marker))

print()
print("=" * 95)
print("KEY COMPARISON: SHOES World - Same Parameter Count (k=8)")
print("=" * 95)

ref = results["tier9_lcdm_shoes"]
ref_aic, ref_bic = compute_aic_bic(ref["chi2"], 6, n_data)

print()
print("%-12s %7s %7s %8s %8s %8s %s" % ("Model", "H0", "S8", "Dchi2", "DAIC", "DBIC", "Verdict"))
print("-" * 75)

# CPL
cpl = results["tier9_phenom_shoes"]
aic, bic = compute_aic_bic(cpl["chi2"], cpl["k"], n_data)
print("%-12s %7.2f %7.3f %+8.1f %+8.1f %+8.1f %s" % 
      ("CPL(k=8)", cpl["H0"], cpl["S8"], cpl["chi2"]-ref["chi2"], 
       aic-ref_aic, bic-ref_bic, "chi2 win, NO tension fix"))

# EDE minimal
ede = results["tier9_v3_shoes_minimal"]
aic, bic = compute_aic_bic(ede["chi2"], ede["k"], n_data)
verdict = "TENSIONS RESOLVED" if ede["H0"] > 70 and ede["S8"] < 0.81 else "partial"
print("%-12s %7.2f %7.3f %+8.1f %+8.1f %+8.1f %s" % 
      ("EDE(k=8)", ede["H0"], ede["S8"], ede["chi2"]-ref["chi2"], 
       aic-ref_aic, bic-ref_bic, verdict))

# LCDM
print("%-12s %7.2f %7.3f %+8.1f %+8.1f %+8.1f %s" % 
      ("LCDM(k=6)", ref["H0"], ref["S8"], 0, 0, 0, "[REF]"))

print()
print("=" * 95)
print("PAPER SUMMARY")
print("=" * 95)
print("""
At equal parameter count (k=8):

  CPL:  Best chi2 (-9.7), but H0=69.3, S8=0.83 -> NO tension resolution
  EDE:  Modest chi2 penalty, but H0=70.8, S8=0.79 -> BOTH tensions addressed

  "Same degrees of freedom, opposite physics strategies, only one solves tensions."

DBIC Interpretation (Kass & Raftery):
  |DBIC| < 2:   Not worth mentioning
  |DBIC| 2-6:   Positive evidence
  |DBIC| 6-10:  Strong evidence
  |DBIC| > 10:  Very strong evidence
""")
print("=" * 95)

