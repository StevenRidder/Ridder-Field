#!/usr/bin/env python3
"""
Tier 5 SH0ES+DESI Live Status Dashboard
Shows sample counts, H0, S8, chi2, r_s for all running chains
Tests: Does EDE survive DESI BAO with H0 tension active?
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
print("TIER 5: SH0ES + DESI Y1 BAO — LIVE STATUS")
print("="*110)
print("KEY QUESTION: Does Geometric EDE survive DESI's BAO constraints while resolving the H₀ tension?")
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
        
        # Acceptance rate estimate from weights
        if "weight" in col_map:
            weights = data[:, col_map["weight"]]
            accept_rate = n_samples / np.sum(weights) if np.sum(weights) > 0 else 0
        else:
            accept_rate = np.nan
        
        return {
            "n": n_samples,
            "H0": H0,
            "H0_std": H0_std,
            "S8": S8,
            "rs": rs,
            "chi2": chi2_best,
            "accept": accept_rate
        }
    except Exception as e:
        print(f"   ⚠️ Error loading {os.path.basename(chain_file)}: {e}")
        return None

# Find ALL Tier 5 chains (SH0ES, TRGB, etc.)
chain_patterns = [
    f"{CHAIN_DIR}/tier5_*.1.txt",  # Match all tier5 chains
]

chain_files = []
for pattern in chain_patterns:
    chain_files.extend(glob.glob(pattern))
chain_files = sorted(set(chain_files))

# Debug: show what files we found
print(f"\n📂 Found {len(chain_files)} chain files:")
for f in chain_files:
    print(f"   - {os.path.basename(f)}")

if not chain_files:
    print("\n⚠️  No Tier 5 SH0ES+DESI chains found yet.")
    print("   Chains may still be initializing...")
    print(f"   Looking in: {CHAIN_DIR}")
    print("\nExpected chain files:")
    print("  - tier5_lcdm_shoes_desi.1.txt")
    print("  - tier5_cpl_shoes_desi.1.txt")
    print("  - tier5_ede_shoes_desi.1.txt")
    sys.exit(0)

# Group by model type and H0 prior
groups = {
    # SH0ES World
    "ΛCDM (k=6) — SH0ES World": [],
    "CPL w₀wₐCDM (k=8) — SH0ES World": [],
    "Geometric EDE (k=8) — SH0ES World": [],
    # TRGB World  
    "ΛCDM (k=6) — TRGB World": [],
    "Geometric EDE (k=8) — TRGB World": [],
}

for f in chain_files:
    name = os.path.basename(f).replace(".1.txt", "")
    data = load_chain(f)
    
    # Determine world (TRGB vs SH0ES)
    is_trgb = "trgb" in name.lower()
    
    if "lcdm" in name.lower():
        if is_trgb:
            groups["ΛCDM (k=6) — TRGB World"].append((name, data))
        else:
            groups["ΛCDM (k=6) — SH0ES World"].append((name, data))
    elif "cpl" in name.lower():
        groups["CPL w₀wₐCDM (k=8) — SH0ES World"].append((name, data))
    elif "ede" in name.lower():
        if is_trgb:
            groups["Geometric EDE (k=8) — TRGB World"].append((name, data))
        else:
            groups["Geometric EDE (k=8) — SH0ES World"].append((name, data))

# Print status
total_samples = 0
results = {}

for group_name, chains in groups.items():
    if not chains:
        continue
    
    print(f"\n{'='*110}")
    print(f"📊 {group_name}")
    print(f"{'='*110}")
    print(f"{'Chain':<35} {'N':>6} {'H0':>7} {'±σ':>5} {'S8':>6} {'r_s':>7} {'χ²':>9} {'Status':<12}")
    print("-"*110)
    
    for name, data in chains:
        if data is None:
            print(f"{name:<35} {'---':>6} {'---':>7} {'---':>5} {'---':>6} {'---':>7} {'---':>9} 🔄 Initializing")
        else:
            total_samples += data["n"]
            results[name] = data
            
            # Status based on sample count (target: 3000)
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
            
            print(f"{name:<35} {data['n']:>6} {data['H0']:>7.2f} {data['H0_std']:>5.2f} {S8_str:>6} {rs_str:>7} {data['chi2']:>9.1f} {status}")

# Summary
print(f"\n{'='*110}")
print(f"📈 SUMMARY")
print(f"{'='*110}")
print(f"Total chains found: {len(chain_files)}")
print(f"Total samples: {total_samples}")

# Delta chi2 analysis
lcdm_chains = [name for name in results if "lcdm" in name.lower()]
if lcdm_chains:
    ref_name = lcdm_chains[0]
    ref_chi2 = results[ref_name]["chi2"]
    ref_H0 = results[ref_name]["H0"]
    ref_S8 = results[ref_name]["S8"]
    
    print(f"\n{'='*110}")
    print(f"📐 Δχ² ANALYSIS (vs ΛCDM reference: χ²={ref_chi2:.1f})")
    print(f"{'='*110}")
    print(f"{'Model':<35} {'Δχ²':>8} {'H0':>8} {'ΔH0':>7} {'S8':>7} {'ΔS8':>8} {'Assessment':<20}")
    print("-"*110)
    
    for name, data in results.items():
        dchi2 = data["chi2"] - ref_chi2
        dH0 = data["H0"] - ref_H0
        dS8 = data["S8"] - ref_S8 if not np.isnan(data["S8"]) and not np.isnan(ref_S8) else np.nan
        
        # Assessment
        if "lcdm" in name.lower():
            assessment = "Reference"
        elif dchi2 < -5:
            if dH0 > 1:
                assessment = "✅ Better fit + higher H0"
            else:
                assessment = "Better fit"
        elif dchi2 < 0:
            assessment = "Marginal improvement"
        elif dchi2 < 5:
            assessment = "Similar fit"
        else:
            assessment = "⚠️ Worse fit"
        
        dS8_str = f"{dS8:+.3f}" if not np.isnan(dS8) else "---"
        print(f"{name:<35} {dchi2:>+8.1f} {data['H0']:>8.2f} {dH0:>+7.2f} {data['S8']:>7.3f} {dS8_str:>8} {assessment}")

# Key science questions
print(f"\n{'='*110}")
print(f"🔬 KEY SCIENCE QUESTIONS")
print(f"{'='*110}")

# Find chains by type
ede_shoes = [name for name in results if "ede" in name.lower() and "trgb" not in name.lower()]
ede_trgb = [name for name in results if "ede" in name.lower() and "trgb" in name.lower()]
lcdm_shoes = [name for name in results if "lcdm" in name.lower() and "trgb" not in name.lower()]
lcdm_trgb = [name for name in results if "lcdm" in name.lower() and "trgb" in name.lower()]
cpl_chains = [name for name in results if "cpl" in name.lower()]

# Q1: Does "chasing 73" work with DESI?
print(f"\n1. Is 'chasing H₀=73' viable with DESI?")
if ede_shoes and lcdm_shoes:
    ede_s = results[ede_shoes[0]]
    lcdm_s = results[lcdm_shoes[0]]
    if ede_s["n"] >= 50:
        dchi2 = ede_s["chi2"] - lcdm_s["chi2"]
        print(f"   SH0ES EDE: H₀={ede_s['H0']:.1f}, r_s={ede_s['rs']:.1f} Mpc, Δχ²={dchi2:+.0f}")
        if dchi2 > 50:
            print(f"   💀 NO - Δχ²={dchi2:+.0f} is catastrophic. The SH0ES branch is dead with DESI.")
        elif dchi2 > 10:
            print(f"   ⚠️ Marginal - significant χ² penalty")
        else:
            print(f"   ✅ Viable")
    else:
        print(f"   🔄 Still running ({ede_s['n']} samples)")

# Q2: Does the TRGB "convergence window" work?
print(f"\n2. Does the TRGB convergence window (H₀~70.5, r_s~145.5) work with DESI?")
if ede_trgb:
    ede_t = results[ede_trgb[0]]
    if ede_t["n"] >= 20:
        # Compare to SH0ES ΛCDM if no TRGB ΛCDM yet
        if lcdm_trgb:
            ref_t = results[lcdm_trgb[0]]
            dchi2_t = ede_t["chi2"] - ref_t["chi2"]
            print(f"   TRGB EDE: H₀={ede_t['H0']:.1f}, r_s={ede_t['rs']:.1f} Mpc, S₈={ede_t['S8']:.3f}")
            print(f"   TRGB ΛCDM: χ²={ref_t['chi2']:.1f}")
            print(f"   Δχ² (vs TRGB ΛCDM) = {dchi2_t:+.1f}")
        else:
            print(f"   TRGB EDE: H₀={ede_t['H0']:.1f}, r_s={ede_t['rs']:.1f} Mpc, S₈={ede_t['S8']:.3f}")
            print(f"   ⏳ Waiting for ΛCDM+TRGB baseline for proper comparison")
        
        # Compare to SH0ES EDE
        if ede_shoes:
            ede_s = results[ede_shoes[0]]
            rs_improvement = ede_t['rs'] - ede_s['rs']
            chi2_improvement = ede_s['chi2'] - ede_t['chi2']
            print(f"\n   📊 TRGB vs SH0ES EDE Comparison:")
            print(f"      r_s: {ede_t['rs']:.1f} vs {ede_s['rs']:.1f} Mpc (Δr_s = {rs_improvement:+.1f} Mpc)")
            print(f"      χ²: {ede_t['chi2']:.1f} vs {ede_s['chi2']:.1f} (saves {chi2_improvement:.0f} in χ²)")
            print(f"      S₈: {ede_t['S8']:.3f} vs {ede_s['S8']:.3f}")
            if chi2_improvement > 50 and rs_improvement > 2:
                print(f"   ✅ YES - TRGB branch is much better (saves Δχ²={chi2_improvement:.0f}, r_s closer to target)")
            elif chi2_improvement > 0:
                print(f"   🎯 Promising - TRGB branch improving")
    else:
        print(f"   🔄 Still running ({ede_t['n']} samples)")
else:
    print(f"   🔄 No TRGB EDE chain found")

# Q3: Does CPL help with DESI?
print(f"\n3. Does late-time w(z) flexibility (CPL) resolve tensions with DESI?")
if cpl_chains and lcdm_shoes:
    cpl = results[cpl_chains[0]]
    lcdm_s = results[lcdm_shoes[0]]
    if cpl["n"] >= 50:
        dchi2_cpl = cpl["chi2"] - lcdm_s["chi2"]
        dH0_cpl = cpl["H0"] - lcdm_s["H0"]
        print(f"   CPL: H₀={cpl['H0']:.2f}, S₈={cpl['S8']:.3f}, Δχ²={dchi2_cpl:+.1f}")
        print(f"   ΔH₀ vs ΛCDM: {dH0_cpl:+.2f} km/s/Mpc")
        if dchi2_cpl < -3 and dH0_cpl < 1:
            print(f"   📊 DESI likes late-time w(z) flexibility (Δχ²={dchi2_cpl:.1f})")
            print(f"   ⚠️ BUT it does NOT use it to raise H₀ toward SH0ES!")
        elif dH0_cpl > 2:
            print(f"   ✅ CPL raises H₀ significantly")
        else:
            print(f"   ~ CPL provides marginal improvement")

# Q4: Sound horizon comparison
print(f"\n4. Sound Horizon Comparison (r_s target: ~145.5 Mpc)")
print(f"   {'Model':<25} {'r_s [Mpc]':>12} {'vs Planck':>12}")
print(f"   {'-'*50}")
planck_rs = 147.3
if lcdm_shoes:
    lcdm_s = results[lcdm_shoes[0]]
    print(f"   {'ΛCDM (SH0ES)':<25} {lcdm_s['rs']:>12.1f} {'(reference)':>12}")
if ede_shoes:
    ede_s = results[ede_shoes[0]]
    pct_s = (ede_s['rs'] - planck_rs) / planck_rs * 100
    print(f"   {'EDE (SH0ES)':<25} {ede_s['rs']:>12.1f} {pct_s:>+11.1f}%")
if ede_trgb:
    ede_t = results[ede_trgb[0]]
    pct_t = (ede_t['rs'] - planck_rs) / planck_rs * 100
    print(f"   {'EDE (TRGB)':<25} {ede_t['rs']:>12.1f} {pct_t:>+11.1f}%")
print(f"   {'Paper target':<25} {'~145.5':>12} {'-1.2%':>12}")

# Q5: S8 comparison
print(f"\n5. Clustering Tension (S₈ target: ~0.776 DES Y3)")
print(f"   {'Model':<25} {'S₈':>8} {'vs DES':>10}")
print(f"   {'-'*45}")
des_s8 = 0.776
if lcdm_shoes:
    lcdm_s = results[lcdm_shoes[0]]
    diff_l = lcdm_s['S8'] - des_s8
    print(f"   {'ΛCDM':<25} {lcdm_s['S8']:>8.3f} {diff_l:>+9.3f}")
if ede_shoes:
    ede_s = results[ede_shoes[0]]
    diff_s = ede_s['S8'] - des_s8
    print(f"   {'EDE (SH0ES)':<25} {ede_s['S8']:>8.3f} {diff_s:>+9.3f}")
if ede_trgb:
    ede_t = results[ede_trgb[0]]
    diff_t = ede_t['S8'] - des_s8
    print(f"   {'EDE (TRGB)':<25} {ede_t['S8']:>8.3f} {diff_t:>+9.3f}")
print(f"   {'DES Y3':<25} {'0.776':>8} {'(target)':>10}")

print(f"\n{'='*110}")
print("🎯 THESIS: The 'convergence window' at H₀~70.5, r_s~145.5 survives DESI better than 'chasing 73'")
print("Target: R-1 < 0.03, ~3000 samples per chain")
print("="*110)

