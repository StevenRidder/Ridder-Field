#!/usr/bin/env python3
"""
Compare EDE versions: current vs archived TRGB
"""
import numpy as np
import os

def analyze_chain(chain_file, label):
    """Extract chi2 breakdown from chain"""
    if not os.path.exists(chain_file):
        print(f"  {label}: FILE NOT FOUND")
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
    
    # Find best-fit
    if "chi2" in col_map:
        best_idx = np.argmin(data[:, col_map["chi2"]])
    else:
        best_idx = np.argmin(data[:, col_map["minuslogpost"]])
    
    best = data[best_idx]
    
    result = {
        "N": len(data),
        "H0": best[col_map["H0"]] if "H0" in col_map else np.nan,
        "rs_drag": best[col_map["rs_drag"]] if "rs_drag" in col_map else np.nan,
        "S8": best[col_map["S8"]] if "S8" in col_map else np.nan,
    }
    
    # Chi2 components
    for c in cols:
        if c.startswith("chi2"):
            result[c] = best[col_map[c]]
    
    return result

CHAIN_DIR = os.path.expanduser("~/Ridder-Field/phase3/chains")
ARCHIVE_DIR = os.path.expanduser("~/Ridder-Field/phase3/archive")

chains = {
    "Current EDE (DESI only)": f"{CHAIN_DIR}/tier5_ede_desi_convergence.1.txt",
    "Current EDE (DESI+Panth)": f"{CHAIN_DIR}/tier5_ede_desi_pantheon_convergence.1.txt",
    "Current LCDM (DESI only)": f"{CHAIN_DIR}/tier5_lcdm_desi_unconstrained.1.txt",
    "Archived TRGB EDE": f"{ARCHIVE_DIR}/all_chains_backup_20241130/tier5_ede_trgb_desi.1.txt",
    "Archived SH0ES EDE": f"{ARCHIVE_DIR}/all_chains_backup_20241130/tier5_ede_shoes_desi.1.txt",
}

print("="*100)
print("EDE VERSION COMPARISON")
print("="*100)

results = {}
for label, path in chains.items():
    r = analyze_chain(path, label)
    if r:
        results[label] = r

# Summary table
print(f"\n{'Chain':<30} {'N':>5} {'H0':>7} {'r_s':>7} {'S8':>6} {'χ²_total':>10} {'χ²_Planck_hl':>12}")
print("-"*100)

for label, r in results.items():
    planck_hl = r.get("chi2__planck_2018_highl_plik.TTTEEE", np.nan)
    chi2_total = r.get("chi2", np.nan)
    print(f"{label:<30} {r['N']:>5} {r['H0']:>7.2f} {r['rs_drag']:>7.1f} {r['S8']:>6.3f} {chi2_total:>10.1f} {planck_hl:>12.1f}")

# Detailed comparison
print(f"\n{'='*100}")
print("DETAILED χ² BREAKDOWN")
print("="*100)

chi2_keys = [
    "chi2__planck_2018_highl_plik.TTTEEE",
    "chi2__planck_2018_lowl.TT",
    "chi2__planck_2018_lowl.EE", 
    "chi2__planck_2018_lensing.clik",
    "chi2__likelihoods.desi_y1_bao.DESI_Y1_BAO",
    "chi2__bao.sdss_dr12_consensus_bao",
    "chi2__trgb_h0",
    "chi2",
]

print(f"\n{'Component':<45}", end="")
for label in results:
    short = label.split()[0] + " " + label.split()[-1]
    print(f"{short:>15}", end="")
print()
print("-"*100)

for key in chi2_keys:
    name = key.replace("chi2__", "").replace("_", " ")[:40]
    print(f"{name:<45}", end="")
    for label in results:
        val = results[label].get(key, np.nan)
        if np.isnan(val):
            print(f"{'---':>15}", end="")
        else:
            print(f"{val:>15.1f}", end="")
    print()

# Delta vs LCDM
if "Current LCDM (DESI only)" in results:
    ref = results["Current LCDM (DESI only)"]
    print(f"\n{'='*100}")
    print("Δχ² vs Current ΛCDM (DESI only)")
    print("="*100)
    
    print(f"\n{'Component':<45}", end="")
    for label in results:
        if "LCDM" in label:
            continue
        short = label.split()[-1]
        print(f"{short:>15}", end="")
    print()
    print("-"*80)
    
    for key in chi2_keys:
        name = key.replace("chi2__", "").replace("_", " ")[:40]
        ref_val = ref.get(key, np.nan)
        print(f"{name:<45}", end="")
        for label in results:
            if "LCDM" in label:
                continue
            val = results[label].get(key, np.nan)
            if np.isnan(val) or np.isnan(ref_val):
                print(f"{'---':>15}", end="")
            else:
                delta = val - ref_val
                print(f"{delta:>+15.1f}", end="")
        print()
