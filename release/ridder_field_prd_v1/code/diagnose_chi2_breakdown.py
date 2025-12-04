#!/usr/bin/env python3
"""
Diagnose χ² breakdown by likelihood block.
Reads chain files and shows which likelihoods are contributing to the penalty.
"""
import numpy as np
import os
import sys

CHAIN_DIR = os.path.expanduser("~/Ridder-Field/phase3/chains")
if not os.path.exists(CHAIN_DIR):
    CHAIN_DIR = "chains"

def load_chain_with_likelihoods(chain_file):
    """Load chain and extract all chi2 components"""
    with open(chain_file, "r") as f:
        header = f.readline().strip()
    if header.startswith("#"):
        header = header[1:]
    cols = header.split()
    col_map = {c.strip(): i for i, c in enumerate(cols)}
    
    data = np.loadtxt(chain_file)
    if len(data.shape) == 1:
        data = data.reshape(1, -1)
    
    return cols, col_map, data

def analyze_chain(chain_file, label):
    """Analyze a single chain's chi2 breakdown"""
    print(f"\n{'='*80}")
    print(f"📊 {label}")
    print(f"   File: {os.path.basename(chain_file)}")
    print(f"{'='*80}")
    
    if not os.path.exists(chain_file):
        print("   ⚠️ File not found")
        return None
    
    cols, col_map, data = load_chain_with_likelihoods(chain_file)
    
    # Find chi2 columns
    chi2_cols = [c for c in cols if c.startswith("chi2")]
    
    print(f"\n   Available χ² columns ({len(chi2_cols)}):")
    for c in chi2_cols:
        print(f"      - {c}")
    
    if len(data) < 5:
        print(f"   ⚠️ Only {len(data)} samples, too early")
        return None
    
    # Find best-fit sample (minimum total chi2)
    if "chi2" in col_map:
        best_idx = np.argmin(data[:, col_map["chi2"]])
    else:
        best_idx = np.argmin(data[:, col_map["minuslogpost"]])
    
    best_sample = data[best_idx]
    
    print(f"\n   Best-fit sample (index {best_idx} of {len(data)}):")
    
    # Key parameters
    params = ["H0", "S8", "sigma8", "Omega_m", "rs_drag", "rdrag"]
    for p in params:
        if p in col_map:
            print(f"      {p}: {best_sample[col_map[p]]:.4f}")
    
    # Chi2 breakdown
    print(f"\n   χ² Breakdown:")
    chi2_breakdown = {}
    total_chi2 = 0
    
    for c in sorted(chi2_cols):
        val = best_sample[col_map[c]]
        chi2_breakdown[c] = val
        if c == "chi2":
            continue  # Skip total, we'll compute it
        total_chi2 += val
        
        # Clean up names for display
        name = c.replace("chi2__", "").replace("_", " ")
        print(f"      {name:<45} {val:>10.2f}")
    
    if "chi2" in col_map:
        print(f"      {'TOTAL (from chain)':<45} {best_sample[col_map['chi2']]:>10.2f}")
    print(f"      {'TOTAL (sum of parts)':<45} {total_chi2:>10.2f}")
    
    return chi2_breakdown

# Analyze both LCDM and EDE in each world
print("="*80)
print("χ² BREAKDOWN DIAGNOSTIC")
print("="*80)
print("This shows which likelihoods are contributing to the Δχ² penalty")

chains_to_analyze = [
    (f"{CHAIN_DIR}/tier5_lcdm_desi_unconstrained.1.txt", "World A: ΛCDM (DESI only)"),
    (f"{CHAIN_DIR}/tier5_ede_desi_convergence.1.txt", "World A: EDE (DESI only)"),
    (f"{CHAIN_DIR}/tier5_lcdm_desi_pantheon_v2.1.txt", "World B: ΛCDM (DESI+Pantheon)"),
    (f"{CHAIN_DIR}/tier5_ede_desi_pantheon_convergence.1.txt", "World B: EDE (DESI+Pantheon)"),
]

results = {}
for chain_file, label in chains_to_analyze:
    breakdown = analyze_chain(chain_file, label)
    if breakdown:
        results[label] = breakdown

# Compare LCDM vs EDE
print(f"\n{'='*80}")
print("📐 Δχ² BY LIKELIHOOD BLOCK")
print("="*80)

for world in ["World A", "World B"]:
    lcdm_key = [k for k in results if world in k and "ΛCDM" in k]
    ede_key = [k for k in results if world in k and "EDE" in k]
    
    if not lcdm_key or not ede_key:
        continue
    
    lcdm = results[lcdm_key[0]]
    ede = results[ede_key[0]]
    
    print(f"\n{world}:")
    print(f"   {'Likelihood':<45} {'ΛCDM':>10} {'EDE':>10} {'Δχ²':>10}")
    print(f"   {'-'*75}")
    
    all_keys = set(lcdm.keys()) | set(ede.keys())
    total_delta = 0
    
    for key in sorted(all_keys):
        if key == "chi2":
            continue
        lcdm_val = lcdm.get(key, 0)
        ede_val = ede.get(key, 0)
        delta = ede_val - lcdm_val
        total_delta += delta
        
        name = key.replace("chi2__", "").replace("_", " ")
        
        # Highlight big contributors
        if abs(delta) > 10:
            marker = "⚠️"
        elif abs(delta) > 5:
            marker = "📌"
        else:
            marker = "  "
        
        print(f"   {marker} {name:<43} {lcdm_val:>10.1f} {ede_val:>10.1f} {delta:>+10.1f}")
    
    print(f"   {'-'*75}")
    print(f"   {'TOTAL Δχ²':<45} {'':>10} {'':>10} {total_delta:>+10.1f}")

print(f"\n{'='*80}")
print("🔍 INTERPRETATION GUIDE")
print("="*80)
print("""
If Δχ² is dominated by:
  - Planck (TT/TE/EE/lensing): EDE is fighting the CMB peaks
  - DESI BAO: The BAO likelihood is penalizing the r_s shift
  - Pre-DESI BAO (6dF/SDSS): Old BAO is fighting the shift
  - Pantheon+: Supernovae are penalizing the late expansion

A healthy EDE model might have:
  - Δχ²_Planck ~ +10-30 (some CMB tension expected)
  - Δχ²_BAO ~ +5-15 (some BAO penalty expected)
  - Δχ²_total ~ +20-50 (viable range)

If Δχ² > 100, either:
  1. The model is genuinely ruled out by the data
  2. There's still a config/likelihood bug
  3. The chains haven't converged yet (N < 500)
""")
print("="*80)
