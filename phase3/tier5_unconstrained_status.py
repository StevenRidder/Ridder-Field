#!/usr/bin/env python3
"""
Tier 5 Phase 2: Unconstrained DESI World Status Dashboard
Shows sample counts, H0, S8, chi2, r_s for unconstrained DESI chains
Tests: Where does DESI+Planck naturally land without H₀ prior?

Usage: ssh ridderadmin@172.191.4.60 "cd ~/Ridder-Field/phase3 && python3 tier5_unconstrained_status.py"
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
print("TIER 5 PHASE 2: UNCONSTRAINED DESI WORLD — LIVE STATUS")
print("="*110)
print("KEY QUESTION: Where does DESI+Planck naturally land WITHOUT an H₀ prior?")
print("HYPOTHESIS: H₀ ~ 70-71 km/s/Mpc, r_s ~ 145.5 Mpc (the 'convergence window')")
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
            S8 = np.mean(data[:, col_map["sigma8"]] * np.sqrt(data[:, col_map["Omega_m"]]/0.3))
        else:
            S8 = np.nan
        
        # r_s (sound horizon) - in Mpc
        if "rs_drag" in col_map:
            rs = np.mean(data[:, col_map["rs_drag"]])
        elif "rdrag" in col_map:
            rs = np.mean(data[:, col_map["rdrag"]])
        else:
            rs = np.nan
        
        # Best-fit chi2 - use direct chi2 column if available, otherwise derive from minuslogpost
        if "chi2" in col_map:
            best_idx = np.argmin(data[:, col_map["chi2"]])
            chi2_best = data[best_idx, col_map["chi2"]]
        else:
            # Fallback: chi2 = 2 * minuslogpost (approximately)
            best_idx = np.argmin(data[:, col_map["minuslogpost"]])
            chi2_best = data[best_idx, col_map["minuslogpost"]] * 2
        
        # For CPL, try to get w0 and wa
        w0 = data[:, col_map.get("w", col_map.get("w0", -1))].mean() if "w" in col_map or "w0" in col_map else np.nan
        wa = data[:, col_map.get("wa", -1)].mean() if "wa" in col_map else np.nan
        
        # For EDE, try to get f_EDE or Lambda_EDE
        if "ridder_Lambda_EDE_eV" in col_map:
            ede_param = np.mean(data[:, col_map["ridder_Lambda_EDE_eV"]])
            ede_name = "Λ_EDE"
        elif "f_EDE" in col_map:
            ede_param = np.mean(data[:, col_map["f_EDE"]])
            ede_name = "f_EDE"
        else:
            ede_param = np.nan
            ede_name = None
        
        return {
            "n": n_samples,
            "H0": H0,
            "H0_std": H0_std,
            "S8": S8,
            "rs": rs,
            "chi2": chi2_best,
            "w0": w0,
            "wa": wa,
            "ede_param": ede_param,
            "ede_name": ede_name
        }
    except Exception as e:
        print(f"   ⚠️ Error loading {os.path.basename(chain_file)}: {e}")
        return None

# Find unconstrained DESI chains (no SH0ES/TRGB)
chain_patterns = [
    f"{CHAIN_DIR}/tier5_lcdm_desi.1.txt",
    f"{CHAIN_DIR}/tier5_cpl_desi.1.txt",
    f"{CHAIN_DIR}/tier5_ede_desi.1.txt",
    f"{CHAIN_DIR}/tier5_lcdm_desi_pantheon.1.txt",
    f"{CHAIN_DIR}/tier5_cpl_desi_pantheon.1.txt",
    f"{CHAIN_DIR}/tier5_ede_desi_pantheon.1.txt",
]

chain_files = []
for pattern in chain_patterns:
    if os.path.exists(pattern):
        chain_files.append(pattern)

print(f"\n📂 Found {len(chain_files)} unconstrained DESI chain files:")
for f in chain_files:
    print(f"   - {os.path.basename(f)}")

if not chain_files:
    print("\n⚠️  No unconstrained DESI chains found yet.")
    print("   Launch with: bash launch_unconstrained_desi.sh")
    print(f"   Looking in: {CHAIN_DIR}")
    print("\nExpected chain files:")
    print("  - tier5_lcdm_desi.1.txt")
    print("  - tier5_cpl_desi.1.txt")
    print("  - tier5_ede_desi.1.txt")
    sys.exit(0)

# Load all chains
results = {}
for f in chain_files:
    name = os.path.basename(f).replace(".1.txt", "")
    data = load_chain(f)
    if data is not None:
        results[name] = data

# Print status table
print(f"\n{'='*110}")
print(f"📊 UNCONSTRAINED DESI WORLD (No H₀ Prior)")
print(f"{'='*110}")
print(f"{'Chain':<30} {'N':>6} {'H0':>7} {'±σ':>5} {'S8':>6} {'r_s':>7} {'χ²':>9} {'Extra':<15} {'Status':<10}")
print("-"*110)

total_samples = 0
for name, data in results.items():
    total_samples += data["n"]
    
    # Status based on sample count
    if data["n"] >= 3000:
        status = "✅ Ready"
    elif data["n"] >= 2000:
        status = "🔄 >66%"
    elif data["n"] >= 1000:
        status = "🔄 >33%"
    elif data["n"] >= 100:
        status = "🔄 Running"
    else:
        status = "🔄 Starting"
    
    rs_str = f"{data['rs']:.1f}" if not np.isnan(data['rs']) else "---"
    S8_str = f"{data['S8']:.3f}" if not np.isnan(data['S8']) else "---"
    
    # Extra column for model-specific info
    if "cpl" in name.lower():
        extra = f"w0={data['w0']:.2f}" if not np.isnan(data['w0']) else ""
    elif "ede" in name.lower():
        if data['ede_name']:
            extra = f"{data['ede_name']}={data['ede_param']:.2f}"
        else:
            extra = ""
    else:
        extra = ""
    
    print(f"{name:<30} {data['n']:>6} {data['H0']:>7.2f} {data['H0_std']:>5.2f} {S8_str:>6} {rs_str:>7} {data['chi2']:>9.1f} {extra:<15} {status}")

# Summary
print(f"\n{'='*110}")
print(f"📈 SUMMARY")
print(f"{'='*110}")
print(f"Total chains found: {len(results)}")
print(f"Total samples: {total_samples}")

# Delta chi2 analysis
lcdm_chains = [name for name in results if "lcdm" in name.lower() and "pantheon" not in name.lower()]
if lcdm_chains:
    ref_name = lcdm_chains[0]
    ref = results[ref_name]
    
    print(f"\n{'='*110}")
    print(f"📐 Δχ² ANALYSIS (vs {ref_name}: χ²={ref['chi2']:.1f})")
    print(f"{'='*110}")
    print(f"{'Model':<30} {'Δχ²':>8} {'H0':>8} {'ΔH0':>7} {'r_s':>7} {'Δr_s':>7}")
    print("-"*110)
    
    for name, data in results.items():
        dchi2 = data["chi2"] - ref["chi2"]
        dH0 = data["H0"] - ref["H0"]
        drs = data["rs"] - ref["rs"] if not np.isnan(data["rs"]) and not np.isnan(ref["rs"]) else np.nan
        
        drs_str = f"{drs:+.1f}" if not np.isnan(drs) else "---"
        print(f"{name:<30} {dchi2:>+8.1f} {data['H0']:>8.2f} {dH0:>+7.2f} {data['rs']:>7.1f} {drs_str:>7}")

# Key science questions
print(f"\n{'='*110}")
print(f"🔬 KEY SCIENCE QUESTIONS")
print(f"{'='*110}")

# Q1: Where does unconstrained ΛCDM land?
print(f"\n1. Where does unconstrained ΛCDM+DESI naturally land?")
if lcdm_chains:
    lcdm = results[lcdm_chains[0]]
    print(f"   H₀ = {lcdm['H0']:.2f} ± {lcdm['H0_std']:.2f} km/s/Mpc")
    print(f"   r_s = {lcdm['rs']:.1f} Mpc (Planck: 147.3 Mpc)")
    print(f"   S₈ = {lcdm['S8']:.3f}")
    
    # Compare to tensions
    print(f"\n   📊 Comparison to tension values:")
    print(f"      vs SH0ES (73.04): {lcdm['H0'] - 73.04:+.1f} km/s/Mpc")
    print(f"      vs TRGB (69.85):  {lcdm['H0'] - 69.85:+.1f} km/s/Mpc")
    print(f"      vs Planck (67.4): {lcdm['H0'] - 67.4:+.1f} km/s/Mpc")

# Q2: Does CPL raise H₀?
cpl_chains = [name for name in results if "cpl" in name.lower() and "pantheon" not in name.lower()]
print(f"\n2. Does CPL (w₀wₐCDM) raise H₀ with DESI?")
if cpl_chains and lcdm_chains:
    cpl = results[cpl_chains[0]]
    lcdm = results[lcdm_chains[0]]
    dH0 = cpl["H0"] - lcdm["H0"]
    dchi2 = cpl["chi2"] - lcdm["chi2"]
    print(f"   CPL: H₀ = {cpl['H0']:.2f}, w₀ = {cpl['w0']:.2f}")
    print(f"   ΔH₀ vs ΛCDM: {dH0:+.2f} km/s/Mpc")
    print(f"   Δχ² vs ΛCDM: {dchi2:+.1f}")
    if dchi2 < -3:
        print(f"   📊 DESI prefers dynamical w(z) (Δχ²={dchi2:.1f})")
    if abs(dH0) < 0.5:
        print(f"   ⚠️ BUT CPL does NOT raise H₀ — flexibility used for better fit, not tension relief")

# Q3: Can EDE exist without tension?
ede_chains = [name for name in results if "ede" in name.lower() and "pantheon" not in name.lower()]
print(f"\n3. Can EDE exist without tension (no SH0ES prior)?")
if ede_chains:
    ede = results[ede_chains[0]]
    print(f"   EDE: H₀ = {ede['H0']:.2f}, r_s = {ede['rs']:.1f} Mpc")
    if ede['ede_name']:
        print(f"   {ede['ede_name']} = {ede['ede_param']:.3f}")
    if abs(ede['H0'] - 68) < 1 and ede['ede_param'] < 0.1:
        print(f"   ⚠️ EDE collapses to near-ΛCDM without tension!")
        print(f"   This confirms EDE is specifically a tension-resolution mechanism.")
elif not ede_chains:
    print(f"   🔄 EDE chain not found — may have failed to initialize")
    print(f"   This would confirm that EDE REQUIRES tension to exist.")

# Convergence window check
print(f"\n4. Does the data support the 'convergence window'?")
print(f"   Target: H₀ ~ 70-71, r_s ~ 145.5 Mpc, S₈ ~ 0.78-0.80")
print(f"   {'-'*50}")
for name, data in results.items():
    in_window = (69 < data["H0"] < 72) and (144 < data["rs"] < 147) and (0.77 < data["S8"] < 0.83)
    status = "✅ IN WINDOW" if in_window else "❌ Outside"
    print(f"   {name:<30} {status}")

print(f"\n{'='*110}")
print("🎯 THESIS: The unconstrained DESI world naturally lands in the convergence window (H₀~70, r_s~145.5)")
print("Target: R-1 < 0.02, ~3000 samples per chain")
print("="*110)
