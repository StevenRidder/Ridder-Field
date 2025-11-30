#!/usr/bin/env python3
"""
Compare Planck penalty between:
1. Current Tier 5 geometry-only (no H0 prior)
2. Archived SH0ES world (with H0 prior)

Key question: Was Planck always at +80, or did the SH0ES prior
let EDE find a different compromise?
"""
import numpy as np
import os

def load_and_analyze(chain_file, label):
    """Load chain and extract key chi2 values at best-fit"""
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
        "label": label,
        "N": len(data),
        "H0": best[col_map["H0"]] if "H0" in col_map else np.nan,
        "rs_drag": best[col_map["rs_drag"]] if "rs_drag" in col_map else np.nan,
        "chi2_total": best[col_map["chi2"]] if "chi2" in col_map else np.nan,
        "chi2_planck_highl": best[col_map.get("chi2__planck_2018_highl_plik.TTTEEE", -1)] if "chi2__planck_2018_highl_plik.TTTEEE" in col_map else np.nan,
        "chi2_planck_lowl_TT": best[col_map.get("chi2__planck_2018_lowl.TT", -1)] if "chi2__planck_2018_lowl.TT" in col_map else np.nan,
        "chi2_planck_lowl_EE": best[col_map.get("chi2__planck_2018_lowl.EE", -1)] if "chi2__planck_2018_lowl.EE" in col_map else np.nan,
        "chi2_planck_lensing": best[col_map.get("chi2__planck_2018_lensing.clik", -1)] if "chi2__planck_2018_lensing.clik" in col_map else np.nan,
        "chi2_desi": best[col_map.get("chi2__likelihoods.desi_y1_bao.DESI_Y1_BAO", -1)] if "chi2__likelihoods.desi_y1_bao.DESI_Y1_BAO" in col_map else np.nan,
        "chi2_shoes": best[col_map.get("chi2__sh0es_h0", -1)] if "chi2__sh0es_h0" in col_map else 0,
    }
    
    # EDE parameters if present
    if "theta_i_ridder" in col_map:
        result["theta_i"] = best[col_map["theta_i_ridder"]]
    if "beta_ridder" in col_map:
        result["beta"] = best[col_map["beta_ridder"]]
    
    return result

CHAIN_DIR = os.path.expanduser("~/Ridder-Field/phase3/chains")
ARCHIVE_DIR = os.path.expanduser("~/Ridder-Field/phase3/archive/all_chains_backup_20241130")

chains = {
    # Current geometry-only (no H0 prior)
    "Current LCDM (no H0)": f"{CHAIN_DIR}/tier5_lcdm_desi_unconstrained.1.txt",
    "Current EDE (no H0)": f"{CHAIN_DIR}/tier5_ede_desi_convergence.1.txt",
    # Archived with SH0ES prior (old DESI likelihood, but Planck is same)
    "Archived LCDM (SH0ES)": f"{ARCHIVE_DIR}/tier5_lcdm_shoes_desi.1.txt",
    "Archived EDE (SH0ES)": f"{ARCHIVE_DIR}/tier5_ede_shoes_desi.1.txt",
}

print("="*100)
print("PLANCK PENALTY COMPARISON: Geometry-Only vs SH0ES World")
print("="*100)
print("\nKEY QUESTION: Was Planck high-l penalty always +80, or did SH0ES let EDE find a softer shelf?")
print()

results = {}
for label, path in chains.items():
    r = load_and_analyze(path, label)
    if r:
        results[label] = r

# Print comparison table
print(f"\n{'Chain':<25} {'N':>5} {'H0':>7} {'r_s':>7} {'Pl_hl':>8} {'Pl_low':>8} {'DESI':>8} {'SH0ES':>8} {'Total':>9}")
print("-"*100)

for label, r in results.items():
    pl_low = r['chi2_planck_lowl_TT'] + r['chi2_planck_lowl_EE'] if not np.isnan(r['chi2_planck_lowl_TT']) else np.nan
    print(f"{label:<25} {r['N']:>5} {r['H0']:>7.2f} {r['rs_drag']:>7.1f} {r['chi2_planck_highl']:>8.1f} {pl_low:>8.1f} {r['chi2_desi']:>8.1f} {r['chi2_shoes']:>8.1f} {r['chi2_total']:>9.1f}")

# Compute Planck deltas
print(f"\n{'='*100}")
print("Δχ² ANALYSIS: EDE - ΛCDM (per world)")
print("="*100)

for world_tag in ["(no H0)", "(SH0ES)"]:
    lcdm_key = [k for k in results if "LCDM" in k and world_tag in k]
    ede_key = [k for k in results if "EDE" in k and world_tag in k]
    
    if not lcdm_key or not ede_key:
        continue
    
    lcdm = results[lcdm_key[0]]
    ede = results[ede_key[0]]
    
    d_planck_hl = ede['chi2_planck_highl'] - lcdm['chi2_planck_highl']
    d_desi = ede['chi2_desi'] - lcdm['chi2_desi']
    d_shoes = ede['chi2_shoes'] - lcdm['chi2_shoes']
    d_total = ede['chi2_total'] - lcdm['chi2_total']
    
    print(f"\n{world_tag}:")
    print(f"  Δχ²_Planck_highl = {d_planck_hl:+.1f}")
    print(f"  Δχ²_DESI         = {d_desi:+.1f}")
    print(f"  Δχ²_SH0ES        = {d_shoes:+.1f}")
    print(f"  Δχ²_total        = {d_total:+.1f}")
    
    if d_shoes < -10:
        print(f"  → SH0ES saves {-d_shoes:.0f} points for EDE!")
    
    print(f"\n  EDE params: H0={ede['H0']:.2f}, r_s={ede['rs_drag']:.1f}")
    if 'theta_i' in ede:
        print(f"              theta_i={ede.get('theta_i', np.nan):.3f}, beta={ede.get('beta', np.nan):.4f}")

print(f"\n{'='*100}")
print("INTERPRETATION")
print("="*100)
print("""
If Planck high-l Δχ² is similar (~+80) in BOTH worlds:
  → Planck always penalizes EDE by this much
  → SH0ES just offsets it with a larger negative Δχ²_SH0ES
  → This is EXPECTED from the paper's χ²_post vs χ²_lik distinction

If Planck high-l Δχ² is SMALLER (~+20-30) in the SH0ES world:
  → SH0ES prior steers EDE to a softer shelf that Planck tolerates better
  → The geometry-only run is hitting a harsher corner
  → May need to tune EDE priors to find the Pareto-optimal region
""")
print("="*100)
