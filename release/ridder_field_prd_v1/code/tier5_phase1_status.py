#!/usr/bin/env python3
"""
Tier 5 Phase 1: DESI Y1 + Pantheon+ Status Dashboard
Tests: Does DESI kill the "full SH0ES" EDE regime? Does late-time CPL help?

Usage: ssh <VM_USER>@<VM_IP> "cd ~/Ridder-Field/phase3 && python3 tier5_phase1_status.py"
"""
import numpy as np
import os
import sys

CHAIN_DIR = os.path.expanduser("~/Ridder-Field/phase3/chains")
if not os.path.exists(CHAIN_DIR):
    CHAIN_DIR = "chains"

print("="*120)
print("TIER 5 PHASE 1: GEOMETRY-FIRST WORLDS (NO LOCAL H₀ PRIOR)")
print("="*120)
print("Science Questions:")
print("  1. Does DESI BAO crush the 'full SH0ES' r_s regime (~142 Mpc)?")
print("  2. Can late-time CPL w(z) flexibility raise H₀? (spoiler: NO once SN are in)")
print("  3. Where does geometry-only data put H₀? (expect: 68-69, not 73)")
print("Target: R̂-1 < 0.01, ESS ≥ 1500 for H₀/S₈, 1500-2500 samples per chain")
print("="*120)

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
        
        # S8
        if "S8" in col_map:
            S8 = np.mean(data[:, col_map["S8"]])
            S8_std = np.std(data[:, col_map["S8"]])
        elif "sigma8" in col_map and "Omega_m" in col_map:
            S8_arr = data[:, col_map["sigma8"]] * np.sqrt(data[:, col_map["Omega_m"]]/0.3)
            S8 = np.mean(S8_arr)
            S8_std = np.std(S8_arr)
        else:
            S8, S8_std = np.nan, np.nan
        
        # r_s (sound horizon)
        if "rs_drag" in col_map:
            rs = np.mean(data[:, col_map["rs_drag"]])
            rs_std = np.std(data[:, col_map["rs_drag"]])
        elif "rdrag" in col_map:
            rs = np.mean(data[:, col_map["rdrag"]])
            rs_std = np.std(data[:, col_map["rdrag"]])
        else:
            rs, rs_std = np.nan, np.nan
        
        # Omega_m
        if "Omega_m" in col_map:
            Om = np.mean(data[:, col_map["Omega_m"]])
        else:
            Om = np.nan
        
        # Best-fit chi2
        if "chi2" in col_map:
            best_idx = np.argmin(data[:, col_map["chi2"]])
            chi2_best = data[best_idx, col_map["chi2"]]
        else:
            best_idx = np.argmin(data[:, col_map["minuslogpost"]])
            chi2_best = data[best_idx, col_map["minuslogpost"]] * 2
        
        # CPL parameters
        w0 = np.mean(data[:, col_map.get("w0_fld", -1)]) if "w0_fld" in col_map else np.nan
        wa = np.mean(data[:, col_map.get("wa_fld", -1)]) if "wa_fld" in col_map else np.nan
        
        # EDE parameters
        if "ridder_Lambda_EDE_eV" in col_map:
            Lambda_EDE = np.mean(data[:, col_map["ridder_Lambda_EDE_eV"]])
        else:
            Lambda_EDE = np.nan
        
        return {
            "n": n_samples,
            "H0": H0, "H0_std": H0_std,
            "S8": S8, "S8_std": S8_std,
            "rs": rs, "rs_std": rs_std,
            "Om": Om,
            "chi2": chi2_best,
            "w0": w0, "wa": wa,
            "Lambda_EDE": Lambda_EDE
        }
    except Exception as e:
        return None

# Define chain files for Phase 1
# EDE uses "convergence window" config (r_s ~145 Mpc, not SH0ES-like 142 Mpc)
worlds = {
    "World A: DESI Y1 Only": {
        "ΛCDM (k=6)": f"{CHAIN_DIR}/tier5_lcdm_desi_unconstrained.1.txt",
        "CPL (k=8)": f"{CHAIN_DIR}/tier5_cpl_desi_unconstrained.1.txt",
        "EDE (k=8)": f"{CHAIN_DIR}/tier5_ede_desi_convergence.1.txt",
    },
    "World B: DESI Y1 + Pantheon+": {
        "ΛCDM (k=6)": f"{CHAIN_DIR}/tier5_lcdm_desi_pantheon_v2.1.txt",
        "CPL (k=8)": f"{CHAIN_DIR}/tier5_cpl_desi_pantheon_v2.1.txt",
        "EDE (k=8)": f"{CHAIN_DIR}/tier5_ede_desi_pantheon_convergence.1.txt",
    }
}

# Load all chains
all_results = {}
total_samples = 0
chains_found = 0

for world_name, chains in worlds.items():
    print(f"\n{'='*120}")
    print(f"📊 {world_name}")
    print(f"{'='*120}")
    print(f"{'Model':<15} {'N':>6} {'H0':>7} {'±':>5} {'S8':>6} {'±':>5} {'r_s':>6} {'±':>4} {'Ω_m':>6} {'χ²':>9} {'Status':<12}")
    print("-"*120)
    
    world_results = {}
    for model_name, chain_file in chains.items():
        if not os.path.exists(chain_file):
            print(f"{model_name:<15} {'—':>6} {'—':>7} {'—':>5} {'—':>6} {'—':>5} {'—':>6} {'—':>4} {'—':>6} {'—':>9} ⏳ Not started")
            continue
        
        data = load_chain(chain_file)
        if data is None:
            print(f"{model_name:<15} {'—':>6} {'—':>7} {'—':>5} {'—':>6} {'—':>5} {'—':>6} {'—':>4} {'—':>6} {'—':>9} 🔄 Initializing")
            continue
        
        chains_found += 1
        total_samples += data["n"]
        world_results[model_name] = data
        
        # Status based on sample count (target: 1500-2500)
        if data["n"] >= 2500:
            status = "✅ Ready"
        elif data["n"] >= 1500:
            status = "✅ >1500"
        elif data["n"] >= 1000:
            status = "🔄 >1000"
        elif data["n"] >= 500:
            status = "🔄 >500"
        else:
            status = "🔄 Running"
        
        rs_str = f"{data['rs']:.1f}" if not np.isnan(data['rs']) else "—"
        rs_std_str = f"{data['rs_std']:.1f}" if not np.isnan(data['rs_std']) else "—"
        Om_str = f"{data['Om']:.3f}" if not np.isnan(data['Om']) else "—"
        
        print(f"{model_name:<15} {data['n']:>6} {data['H0']:>7.2f} {data['H0_std']:>5.2f} "
              f"{data['S8']:>6.3f} {data['S8_std']:>5.3f} {rs_str:>6} {rs_std_str:>4} "
              f"{Om_str:>6} {data['chi2']:>9.1f} {status}")
    
    all_results[world_name] = world_results

# Summary
print(f"\n{'='*120}")
print(f"📈 SUMMARY")
print(f"{'='*120}")
print(f"Chains found: {chains_found}/6")
print(f"Total samples: {total_samples}")

# Δχ² Analysis for each world
for world_name, world_results in all_results.items():
    if not world_results:
        continue
    
    # Find ΛCDM reference
    # Prefer SH0ES LCDM if available, otherwise TRGB, otherwise any LCDM
    lcdm_shoes = [k for k in world_results if "ΛCDM" in k and "SH0ES" in k.upper()]
    lcdm_trgb = [k for k in world_results if "ΛCDM" in k and "TRGB" in k.upper()]
    lcdm_any = [k for k in world_results if "ΛCDM" in k]
    
    if lcdm_shoes:
        ref_key = lcdm_shoes[0]
        ref_label = "SH0ES ΛCDM"
    elif lcdm_trgb:
        ref_key = lcdm_trgb[0]
        ref_label = "TRGB ΛCDM"
    elif lcdm_any:
        ref_key = lcdm_any[0]
        ref_label = "ΛCDM"
    else:
        continue
    
    ref = world_results[ref_key]
    
    print(f"\n{'='*120}")
    print(f"📐 Δχ² ANALYSIS: {world_name} (ref: {ref_label} χ²={ref['chi2']:.1f})")
    print(f"{'='*120}")
    print(f"{'Model':<15} {'Δχ²':>8} {'H0':>7} {'ΔH0':>6} {'r_s':>7} {'Δr_s':>6} {'Δr_s%':>7} {'Assessment':<25}")
    print("-"*120)
    
    for model_name, data in world_results.items():
        dchi2 = data["chi2"] - ref["chi2"]
        dH0 = data["H0"] - ref["H0"]
        drs = data["rs"] - ref["rs"] if not np.isnan(data["rs"]) and not np.isnan(ref["rs"]) else np.nan
        drs_pct = (drs / ref["rs"] * 100) if not np.isnan(drs) else np.nan
        
        # Assessment
        if "ΛCDM" in model_name:
            assessment = "Reference"
        elif "EDE" in model_name:
            if drs_pct < 0 and abs(drs_pct) > 0.5:
                if dchi2 < 5:
                    assessment = "✅ r_s reduced, fit OK"
                else:
                    assessment = "⚠️ r_s reduced, χ² penalty"
            else:
                assessment = "⚠️ r_s not reduced"
        elif "CPL" in model_name:
            if dchi2 < -2:
                assessment = "✅ Better fit"
            else:
                assessment = "~ Similar fit"
        else:
            assessment = "—"
        
        drs_str = f"{drs:+.1f}" if not np.isnan(drs) else "—"
        drs_pct_str = f"{drs_pct:+.2f}%" if not np.isnan(drs_pct) else "—"
        
        print(f"{model_name:<15} {dchi2:>+8.1f} {data['H0']:>7.2f} {dH0:>+6.2f} {data['rs']:>7.1f} {drs_str:>6} {drs_pct_str:>7} {assessment}")

# Key science questions
print(f"\n{'='*120}")
print(f"🔬 KEY SCIENCE QUESTIONS")
print(f"{'='*120}")

# Q1: Does r_s sit ~1% below ΛCDM?
print(f"\n1. Does r_s sit ~1% below ΛCDM with DESI? (target: Δr_s ≈ -1.5 Mpc)")
for world_name, world_results in all_results.items():
    ede_key = [k for k in world_results if "EDE" in k]
    lcdm_key = [k for k in world_results if "ΛCDM" in k]
    if ede_key and lcdm_key:
        ede = world_results[ede_key[0]]
        lcdm = world_results[lcdm_key[0]]
        drs = ede["rs"] - lcdm["rs"]
        drs_pct = drs / lcdm["rs"] * 100
        print(f"   {world_name}:")
        print(f"      ΛCDM r_s = {lcdm['rs']:.1f} Mpc")
        print(f"      EDE  r_s = {ede['rs']:.1f} Mpc")
        print(f"      Δr_s = {drs:+.1f} Mpc ({drs_pct:+.2f}%)")
        if drs_pct < -0.5:
            print(f"      ✅ YES — geometric shift detected")
        else:
            print(f"      ⚠️ NO — r_s not significantly reduced")

# Q2: Does CPL raise H0?
print(f"\n2. Does CPL use late-time flexibility to raise H₀? (expect: NO)")
for world_name, world_results in all_results.items():
    cpl_key = [k for k in world_results if "CPL" in k]
    lcdm_key = [k for k in world_results if "ΛCDM" in k]
    if cpl_key and lcdm_key:
        cpl = world_results[cpl_key[0]]
        lcdm = world_results[lcdm_key[0]]
        dH0 = cpl["H0"] - lcdm["H0"]
        dchi2 = cpl["chi2"] - lcdm["chi2"]
        print(f"   {world_name}:")
        print(f"      CPL H₀ = {cpl['H0']:.2f}, w₀ = {cpl['w0']:.2f}, wₐ = {cpl['wa']:.2f}")
        print(f"      ΔH₀ = {dH0:+.2f}, Δχ² = {dchi2:+.1f}")
        if abs(dH0) < 0.5 and dchi2 < 0:
            print(f"      ✅ Confirmed: CPL improves fit but doesn't raise H₀")

# Q3: Where does unconstrained DESI put H0?
print(f"\n3. Where does unconstrained DESI+Planck put H₀?")
for world_name, world_results in all_results.items():
    lcdm_key = [k for k in world_results if "ΛCDM" in k]
    if lcdm_key:
        lcdm = world_results[lcdm_key[0]]
        print(f"   {world_name}:")
        print(f"      ΛCDM: H₀ = {lcdm['H0']:.2f} ± {lcdm['H0_std']:.2f}")
        print(f"      vs Planck (67.4): {lcdm['H0'] - 67.4:+.2f}")
        print(f"      vs TRGB (69.85):  {lcdm['H0'] - 69.85:+.2f}")
        print(f"      vs SH0ES (73.04): {lcdm['H0'] - 73.04:+.2f}")

# Sound horizon target check
print(f"\n4. Sound Horizon Check (Planck: 147.3 Mpc, target: ~145.5 Mpc)")
print(f"   {'World':<35} {'ΛCDM r_s':>10} {'EDE r_s':>10} {'Δ':>8}")
print(f"   {'-'*65}")
for world_name, world_results in all_results.items():
    ede_key = [k for k in world_results if "EDE" in k]
    lcdm_key = [k for k in world_results if "ΛCDM" in k]
    if ede_key and lcdm_key:
        ede = world_results[ede_key[0]]
        lcdm = world_results[lcdm_key[0]]
        drs = ede["rs"] - lcdm["rs"]
        print(f"   {world_name:<35} {lcdm['rs']:>10.1f} {ede['rs']:>10.1f} {drs:>+8.1f}")

# Regime diagnosis
print(f"\n{'='*120}")
print("🔬 REGIME DIAGNOSIS")
print("="*120)
for world_name, world_results in all_results.items():
    ede_key = [k for k in world_results if "EDE" in k]
    lcdm_key = [k for k in world_results if "ΛCDM" in k]
    if ede_key and lcdm_key:
        ede = world_results[ede_key[0]]
        lcdm = world_results[lcdm_key[0]]
        drs_pct = (ede["rs"] - lcdm["rs"]) / lcdm["rs"] * 100
        dchi2 = ede["chi2"] - lcdm["chi2"]
        
        if drs_pct > -1.0:
            regime = "⚠️ TOO MILD — EDE not engaging"
        elif drs_pct > -2.5:
            regime = "✅ CONVERGENCE WINDOW — r_s ~1-2% below ΛCDM"
        else:
            regime = "❌ TOO AGGRESSIVE — SH0ES-like regime, DESI will crush"
        
        print(f"   {world_name}:")
        print(f"      EDE r_s shift: {drs_pct:+.1f}%  |  Δχ²: {dchi2:+.0f}")
        print(f"      Regime: {regime}")

print(f"\n{'='*120}")
print("🎯 SCIENCE QUESTION: Compare 'convergence window' (H₀~70.5, r_s~145.5) against 'chasing 73' under DESI Y1 BAO")
print("Target: R̂-1 < 0.01, 1500-2500 samples/chain, ESS ≥ 1500 for H₀/S₈")
print("="*120)
