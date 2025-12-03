#!/usr/bin/env python3
"""Analyze chi2 breakdown by dataset for fixed H0 chains."""
import numpy as np
import os
import sys

def load_chain_with_breakdown(fname):
    """Load chain and extract chi2 breakdown by dataset."""
    try:
        with open(fname, "r") as f:
            header = f.readline().strip()
        if header.startswith("#"):
            header = header[1:]
        cols = header.split()
        col_map = {c.strip(): i for i, c in enumerate(cols)}
        data = np.loadtxt(fname)
        if len(data.shape) == 1:
            data = data.reshape(1, -1)
        if len(data) == 0:
            return None
        
        best_idx = np.argmin(data[:, col_map["minuslogpost"]])
        
        # Extract chi2 components
        breakdown = {}
        
        # Planck components
        if "chi2__planck_2018_lowl.TT" in col_map:
            breakdown["Planck_lowell_TT"] = data[best_idx, col_map["chi2__planck_2018_lowl.TT"]]
        if "chi2__planck_2018_lowl.EE" in col_map:
            breakdown["Planck_lowell_EE"] = data[best_idx, col_map["chi2__planck_2018_lowl.EE"]]
        if "chi2__planck_2018_highl_plik.TTTEEE" in col_map:
            breakdown["Planck_highl"] = data[best_idx, col_map["chi2__planck_2018_highl_plik.TTTEEE"]]
        if "chi2__planck_2018_lensing.clik" in col_map:
            breakdown["Planck_lensing"] = data[best_idx, col_map["chi2__planck_2018_lensing.clik"]]
        
        # ACT (if present)
        if "chi2__act" in col_map:
            breakdown["ACT"] = data[best_idx, col_map["chi2__act"]]
        
        # BAO components
        bao_total = 0.0
        if "chi2__bao.sixdf_2011_bao" in col_map:
            bao_total += data[best_idx, col_map["chi2__bao.sixdf_2011_bao"]]
        if "chi2__bao.sdss_dr7_mgs" in col_map:
            bao_total += data[best_idx, col_map["chi2__bao.sdss_dr7_mgs"]]
        if "chi2__bao.sdss_dr12_consensus_bao" in col_map:
            bao_total += data[best_idx, col_map["chi2__bao.sdss_dr12_consensus_bao"]]
        if bao_total > 0:
            breakdown["BAO_preDESI"] = bao_total
        
        if "chi2__likelihoods.desi_y1_bao.DESI_Y1_BAO" in col_map:
            breakdown["BAO_DESI"] = data[best_idx, col_map["chi2__likelihoods.desi_y1_bao.DESI_Y1_BAO"]]
        
        # Pantheon+
        if "chi2__sn.pantheonplus" in col_map:
            breakdown["PantheonPlus"] = data[best_idx, col_map["chi2__sn.pantheonplus"]]
        
        # SH0ES
        if "chi2__shoes_h0" in col_map:
            breakdown["SH0ES"] = data[best_idx, col_map["chi2__shoes_h0"]]
        
        # Total chi2
        total_chi2 = 2 * data[best_idx, col_map["minuslogpost"]]
        
        return {
            "n": len(data),
            "total_chi2": total_chi2,
            "breakdown": breakdown,
        }
    except Exception as e:
        print(f"Error loading {fname}: {e}", file=sys.stderr)
        return None

# Load REF (LCDM baseline)
ref_file = "chains/tier5_lcdm_shoes_desi.1.txt"
ref_data = load_chain_with_breakdown(ref_file)
if not ref_data:
    print("ERROR: Could not load REF chain", file=sys.stderr)
    sys.exit(1)

ref_total = ref_data["total_chi2"]
ref_breakdown = ref_data["breakdown"]

print("="*80)
print("CHI2 BREAKDOWN BY DATASET (Fixed H0 Analysis)")
print("="*80)
print()
print(f"REF (LCDM): Total chi2 = {ref_total:.1f}")
print()
print("Dataset breakdown (REF):")
for key, val in sorted(ref_breakdown.items()):
    print(f"  {key:20s}: {val:8.2f}")
print()

# Analyze each H0 value
h0_values = [69, 70, 71, 72]
results = []

for h0 in h0_values:
    chain_file = f"chains/tier5_ede_shoes_desi_h0_fixed_{h0}.1.txt"
    if not os.path.exists(chain_file):
        print(f"H0={h0}: Chain file not found")
        continue
    
    data = load_chain_with_breakdown(chain_file)
    if not data:
        print(f"H0={h0}: Could not load data")
        continue
    
    delta_total = data["total_chi2"] - ref_total
    
    print(f"{'='*80}")
    print(f"H0 = {h0} km/s/Mpc")
    print(f"{'='*80}")
    print(f"Total chi2: {data['total_chi2']:.1f} (Delta: {delta_total:+.1f})")
    print()
    print("Dataset contributions (Delta vs REF):")
    
    deltas = {}
    for key in sorted(set(list(data["breakdown"].keys()) + list(ref_breakdown.keys()))):
        val = data["breakdown"].get(key, 0.0)
        ref_val = ref_breakdown.get(key, 0.0)
        delta = val - ref_val
        deltas[key] = delta
        print(f"  {key:20s}: {val:8.2f} (delta: {delta:+8.2f})")
    
    results.append({
        "H0": h0,
        "total_chi2": data["total_chi2"],
        "delta_total": delta_total,
        "breakdown": data["breakdown"],
        "deltas": deltas,
    })
    print()

# Summary table
print("="*80)
print("SUMMARY: Delta chi2 by dataset")
print("="*80)
print()
print(f"{'Dataset':<20s} {'H0=69':>10s} {'H0=70':>10s} {'H0=71':>10s} {'H0=72':>10s}")
print("-"*80)

# Get all dataset keys
all_keys = set()
for r in results:
    all_keys.update(r["deltas"].keys())

for key in sorted(all_keys):
    row = f"{key:<20s}"
    for h0 in [69, 70, 71, 72]:
        r = next((x for x in results if x["H0"] == h0), None)
        if r and key in r["deltas"]:
            row += f"{r['deltas'][key]:+10.2f}"
        else:
            row += f"{'---':>10s}"
    print(row)

print()
print(f"{'TOTAL':<20s}", end="")
for h0 in [69, 70, 71, 72]:
    r = next((x for x in results if x["H0"] == h0), None)
    if r:
        print(f"{r['delta_total']:+10.1f}", end="")
    else:
        print(f"{'---':>10s}", end="")
print()
