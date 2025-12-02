#!/usr/bin/env python3
"""Compare S8, H0, and chi2 across Tier5 chains at matching sample counts."""
import numpy as np
import sys
import os
import glob

def load_chain(chain_file, max_samples=None):
    """Load chain and extract S8 statistics."""
    if not os.path.exists(chain_file):
        return None
    
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
        
        # Limit samples if requested
        if max_samples and len(data) > max_samples:
            data = data[:max_samples]
        
        if len(data) < 5:
            return None
        
        n_samples = len(data)
        
        # H0
        H0 = np.mean(data[:, col_map["H0"]])
        H0_std = np.std(data[:, col_map["H0"]])
        
        # S8 - try direct column first, then compute from sigma8 and Omega_m
        if "S8" in col_map:
            S8_vals = data[:, col_map["S8"]]
            # Check if values are reasonable (0.5-1.0)
            if np.all((S8_vals > 0.5) & (S8_vals < 1.0)):
                S8 = np.mean(S8_vals)
                S8_std = np.std(S8_vals)
            else:
                # S8 column has wrong values, compute from sigma8/Omega_m
                if "sigma8" in col_map and "Omega_m" in col_map:
                    S8_vals = data[:, col_map["sigma8"]] * np.sqrt(data[:, col_map["Omega_m"]] / 0.3)
                    S8 = np.mean(S8_vals)
                    S8_std = np.std(S8_vals)
                else:
                    S8, S8_std = np.nan, np.nan
        elif "sigma8" in col_map and "Omega_m" in col_map:
            S8_vals = data[:, col_map["sigma8"]] * np.sqrt(data[:, col_map["Omega_m"]] / 0.3)
            S8 = np.mean(S8_vals)
            S8_std = np.std(S8_vals)
        else:
            S8, S8_std = np.nan, np.nan
        
        # Best-fit point
        best_idx = np.argmin(data[:, col_map["minuslogpost"]])
        H0_best = data[best_idx, col_map["H0"]]
        if "S8" in col_map and np.all((data[:, col_map["S8"]] > 0.5) & (data[:, col_map["S8"]] < 1.0)):
            S8_best = data[best_idx, col_map["S8"]]
        elif "sigma8" in col_map and "Omega_m" in col_map:
            sig8_best = data[best_idx, col_map["sigma8"]]
            om_best = data[best_idx, col_map["Omega_m"]]
            S8_best = sig8_best * np.sqrt(om_best / 0.3)
        else:
            S8_best = np.nan
        
        # Also get sigma8 and Omega_m for diagnostics
        sigma8 = np.mean(data[:, col_map["sigma8"]]) if "sigma8" in col_map else np.nan
        Omega_m = np.mean(data[:, col_map["Omega_m"]]) if "Omega_m" in col_map else np.nan
        
        return {
            "n": n_samples,
            "H0": H0,
            "H0_std": H0_std,
            "H0_best": H0_best,
            "S8": S8,
            "S8_std": S8_std,
            "S8_best": S8_best,
            "sigma8": sigma8,
            "Omega_m": Omega_m,
            "minuslogpost_best": data[best_idx, col_map["minuslogpost"]],
        }
    except Exception as e:
        print(f"Error loading {chain_file}: {e}", file=sys.stderr)
        return None

def detect_data_combo(chain_file):
    """Detect data combination from chain header."""
    try:
        with open(chain_file, "r") as f:
            header = f.readline().strip()
        if header.startswith("#"):
            header = header[1:]
        
        has_desi = ("chi2__desi" in header.lower() or 
                    "chi2__likelihoods.desi_y1_bao" in header or
                    "DESI_Y1_BAO" in header)
        has_shoes = "chi2__shoes" in header or "chi2__SH0ES" in header
        has_pantheon = "chi2__sn.pantheonplus" in header or "chi2__pantheon" in header
        has_act = "chi2__act" in header.lower()
        
        combo = []
        if has_desi:
            combo.append("DESI")
        if has_shoes:
            combo.append("SH0ES")
        if has_pantheon:
            combo.append("Pantheon+")
        if has_act:
            combo.append("ACT")
        if not combo:
            combo.append("CMB+BAO")
        
        return "+".join(combo) if combo else "unknown"
    except:
        return "unknown"

def find_legacy_chains(base_dir, target_combo, exclude_names):
    """Find legacy Tier5 chains with matching data combination, excluding current chains."""
    patterns = [
        "tier5_ede_shoes*.1.txt",
        "tier5_lcdm_shoes*.1.txt",
    ]
    chains = {}
    for pattern in patterns:
        files = glob.glob(os.path.join(base_dir, pattern))
        for f in files:
            name = os.path.basename(f).replace(".1.txt", "")
            # EXCLUDE current chains
            if name in exclude_names:
                continue
            combo = detect_data_combo(f)
            # Only include chains with matching data combo
            if combo == target_combo:
                chains[name] = {"path": f, "combo": combo}
    return chains

if __name__ == "__main__":
    base_dir = os.path.expanduser("~/Ridder-Field/phase3/chains")
    
    # Check if v2 chain exists and has data (new peek chain with tightened code)
    ede_v2 = os.path.join(base_dir, "tier5_ede_shoes_desi_v2.1.txt")
    ede_v2_test = load_chain(ede_v2) if os.path.exists(ede_v2) else None
    
    if ede_v2_test and ede_v2_test['n'] > 0:
        # Use v2 as current, compare to v1
        ede_current = ede_v2
        ede_v1 = os.path.join(base_dir, "tier5_ede_shoes_desi.1.txt")
        lcdm_current = os.path.join(base_dir, "tier5_lcdm_shoes_desi.1.txt")
        is_v2_comparison = True
    else:
        # Default: try predesi chains, fall back to desi if not available
        ede_predesi = os.path.join(base_dir, "tier5_ede_shoes_predesi.1.txt")
        if os.path.exists(ede_predesi) and load_chain(ede_predesi):
            ede_current = ede_predesi
            lcdm_current = os.path.join(base_dir, "tier5_lcdm_shoes_predesi.1.txt")
        else:
            # Fall back to desi chains
            ede_current = os.path.join(base_dir, "tier5_ede_shoes_desi.1.txt")
            lcdm_current = os.path.join(base_dir, "tier5_lcdm_shoes_desi.1.txt")
        ede_v1 = None
        is_v2_comparison = False
    
    # Get current sample count from running EDE chain
    ede_data_full = load_chain(ede_current)
    if not ede_data_full:
        if is_v2_comparison:
            print(f"⚠️  V2 chain exists but has no samples yet (still starting)")
            print(f"   Will compare once it has samples. Checking v1 chain...")
            if os.path.exists(ede_v1):
                v1_data = load_chain(ede_v1)
                if v1_data:
                    print(f"   V1 chain has {v1_data['n']} samples")
            sys.exit(0)  # Exit gracefully, not an error
        else:
            print(f"❌ Could not load current EDE chain: {ede_current}")
            print(f"   File exists: {os.path.exists(ede_current)}")
            sys.exit(1)
    
    current_samples = ede_data_full["n"]
    
    # Detect data combination for current chains
    ede_combo = detect_data_combo(ede_current)
    lcdm_combo = detect_data_combo(lcdm_current)
    
    if ede_combo != lcdm_combo:
        print(f"⚠️  WARNING: EDE and LCDM chains have different data combinations!")
        print(f"   EDE: {ede_combo}")
        print(f"   LCDM: {lcdm_combo}")
        print(f"   This comparison may not be valid!")
    
    print("=" * 90)
    print(f"TIER5 CHAIN COMPARISON (at {current_samples} samples)")
    print(f"Data combination: {ede_combo}")
    print("=" * 90)
    print(f"\n📊 Current running chain: {current_samples} samples")
    
    # Load current chains at matching sample count
    ede_data = load_chain(ede_current, max_samples=current_samples)
    lcdm_data = load_chain(lcdm_current, max_samples=current_samples)
    
    if not ede_data or not lcdm_data:
        print("❌ Failed to load current chains")
        sys.exit(1)
    
    chain_type = "tier5_*_shoes_desi_v2 (NEW)" if is_v2_comparison else "tier5_*_shoes_predesi"
    print(f"\n{'='*90}")
    print(f"CURRENT CHAINS ({chain_type}) - Data: {ede_combo}")
    if is_v2_comparison:
        print(f"⚠️  V2 COMPARISON: Comparing tightened code (v2) vs original (v1)")
    print(f"{'='*90}")
    print(f"{'Chain':<35} {'N':>6} {'H0':>7} {'±σ':>5} {'S8':>7} {'±σ':>6} {'χ²':>9} {'Δχ²':>8}")
    print("-" * 90)
    
    ede_chi2 = 2 * ede_data['minuslogpost_best']
    lcdm_chi2 = 2 * lcdm_data['minuslogpost_best']
    delta_chi2 = ede_chi2 - lcdm_chi2
    
    print(f"{'EDE (current)':<35} {ede_data['n']:>6} {ede_data['H0']:>7.2f} {ede_data['H0_std']:>5.2f} "
          f"{ede_data['S8']:>7.4f} {ede_data['S8_std']:>6.4f} {ede_chi2:>9.1f} {delta_chi2:>+8.1f}")
    print(f"{'LCDM (baseline)':<35} {lcdm_data['n']:>6} {lcdm_data['H0']:>7.2f} {lcdm_data['H0_std']:>5.2f} "
          f"{lcdm_data['S8']:>7.4f} {lcdm_data['S8_std']:>6.4f} {lcdm_chi2:>9.1f} {'(ref)':>8}")
    
    # Find and compare to legacy chains with SAME data combination (excluding current)
    current_chain_names = [
        os.path.basename(ede_current).replace(".1.txt", ""),
        os.path.basename(lcdm_current).replace(".1.txt", "")
    ]
    # If v2 comparison, also exclude v2 from legacy search
    if is_v2_comparison:
        current_chain_names.append("tier5_ede_shoes_desi_v2")
    
    legacy_chains = find_legacy_chains(base_dir, ede_combo, current_chain_names)
    
    # Special handling: if v2 exists, explicitly compare to v1
    if is_v2_comparison and os.path.exists(ede_v1):
        v1_data = load_chain(ede_v1, max_samples=current_samples)
        if v1_data and v1_data['n'] >= current_samples:
            # Add v1 to legacy comparisons for explicit comparison
            v1_chi2 = 2 * v1_data['minuslogpost_best']
            legacy_chains["tier5_ede_shoes_desi"] = {
                "path": ede_v1,
                "combo": ede_combo
            }
    
    if legacy_chains:
        print(f"\n{'='*90}")
        print(f"LEGACY CHAINS (previous Tier5 runs) - Data: {ede_combo}")
        print(f"{'='*90}")
        print(f"{'Chain':<35} {'N':>6} {'H0':>7} {'±σ':>5} {'S8':>7} {'±σ':>6} {'χ²':>9} {'Match':>8}")
        print("-" * 90)
        
        # Find legacy chains that have at least current_samples
        legacy_comparisons = []
        for name, info in legacy_chains.items():
            path = info["path"]
            legacy_data = load_chain(path, max_samples=current_samples)
            if legacy_data and legacy_data['n'] >= current_samples:
                legacy_chi2 = 2 * legacy_data['minuslogpost_best']
                match_str = f"{legacy_data['n']}/{current_samples}" if legacy_data['n'] > current_samples else "exact"
                legacy_comparisons.append({
                    'name': name,
                    'data': legacy_data,
                    'chi2': legacy_chi2,
                    'match': match_str
                })
        
        # Sort by name
        legacy_comparisons.sort(key=lambda x: x['name'])
        
        for comp in legacy_comparisons:
            d = comp['data']
            print(f"{comp['name']:<35} {d['n']:>6} {d['H0']:>7.2f} {d['H0_std']:>5.2f} "
                  f"{d['S8']:>7.4f} {d['S8_std']:>6.4f} {comp['chi2']:>9.1f} {comp['match']:>8}")
        
        if legacy_comparisons:
            # Special: If v2 comparison, prioritize v1 comparison
            if is_v2_comparison:
                v1_comp = [c for c in legacy_comparisons if c['name'] == 'tier5_ede_shoes_desi']
                if v1_comp:
                    v1_comp = v1_comp[0]
                    print(f"\n{'='*90}")
                    print("V2 vs V1 COMPARISON (Tightened Code vs Original):")
                    print(f"{'='*90}")
                    print(f"{'Metric':<20} {'V2 (New)':>12} {'V1 (Original)':>12} {'Δ (V2-V1)':>12}")
                    print("-" * 90)
                    print(f"{'H0':<20} {ede_data['H0']:>12.2f} {v1_comp['data']['H0']:>12.2f} "
                          f"{ede_data['H0'] - v1_comp['data']['H0']:>+12.2f}")
                    print(f"{'S8':<20} {ede_data['S8']:>12.4f} {v1_comp['data']['S8']:>12.4f} "
                          f"{ede_data['S8'] - v1_comp['data']['S8']:>+12.4f}")
                    print(f"{'χ²':<20} {ede_chi2:>12.1f} {v1_comp['chi2']:>12.1f} "
                          f"{ede_chi2 - v1_comp['chi2']:>+12.1f}")
                    if ede_chi2 < v1_comp['chi2']:
                        print(f"\n✅ V2 has BETTER χ² than V1 (tightened code improved fit)")
                    elif ede_chi2 > v1_comp['chi2']:
                        print(f"\n⚠️  V2 has WORSE χ² than V1")
                    else:
                        print(f"\n➡️  V2 has SAME χ² as V1")
            
            # Also show best legacy comparison
            legacy_ede = [c for c in legacy_comparisons if 'ede' in c['name'].lower()]
            if legacy_ede:
                best_legacy = min(legacy_ede, key=lambda x: x['chi2'])
                if not (is_v2_comparison and best_legacy['name'] == 'tier5_ede_shoes_desi'):
                    print(f"\n{'='*90}")
                    print("COMPARISON: Current EDE vs Best Legacy EDE:")
                    print(f"{'='*90}")
                    print(f"{'Metric':<20} {'Current':>12} {'Legacy':>12} {'Δ':>10}")
                    print("-" * 90)
                    print(f"{'H0':<20} {ede_data['H0']:>12.2f} {best_legacy['data']['H0']:>12.2f} "
                          f"{ede_data['H0'] - best_legacy['data']['H0']:>+10.2f}")
                    print(f"{'S8':<20} {ede_data['S8']:>12.4f} {best_legacy['data']['S8']:>12.4f} "
                          f"{ede_data['S8'] - best_legacy['data']['S8']:>+10.4f}")
                    print(f"{'χ²':<20} {ede_chi2:>12.1f} {best_legacy['chi2']:>12.1f} "
                          f"{ede_chi2 - best_legacy['chi2']:>+10.1f}")
    else:
        print(f"\n⚠️  No legacy chains found with matching data combination: {ede_combo}")
        print(f"   (This is expected if these are the first chains with this data combo)")
        print(f"\n   Available chains with different data:")
        all_chains = glob.glob(os.path.join(base_dir, "tier5_*_shoes*.1.txt"))
        other_combos = {}
        for chain_file in all_chains:
            name = os.path.basename(chain_file).replace(".1.txt", "")
            combo = detect_data_combo(chain_file)
            if combo != ede_combo:
                if combo not in other_combos:
                    other_combos[combo] = []
                other_combos[combo].append(name)
        for combo, names in sorted(other_combos.items()):
            print(f"     {combo}: {', '.join(names[:3])}{'...' if len(names) > 3 else ''}")
    
    # Summary
    print(f"\n{'='*90}")
    print("SUMMARY:")
    print(f"{'='*90}")
    delta_H0 = ede_data['H0'] - lcdm_data['H0']
    delta_S8 = ede_data['S8'] - lcdm_data['S8']
    
    print(f"Current EDE vs LCDM:")
    print(f"  ΔH0 = {delta_H0:+.2f} km/s/Mpc")
    print(f"  ΔS8 = {delta_S8:+.4f}")
    print(f"  Δχ² = {delta_chi2:+.2f}")
    
    if delta_S8 < 0:
        print(f"\n✅ EDE has LOWER S8 (helps resolve S8 tension)")
    else:
        print(f"\n⚠️  EDE has HIGHER S8")
    
    if delta_H0 > 0:
        print(f"✅ EDE has HIGHER H0 (helps resolve H0 tension)")
    else:
        print(f"⚠️  EDE has LOWER H0")
    
    if delta_chi2 < 0:
        print(f"✅ EDE has BETTER χ²")
    else:
        print(f"⚠️  EDE has WORSE χ²")
    
    print(f"{'='*90}")
