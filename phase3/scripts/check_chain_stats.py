#!/usr/bin/env python3
"""
V3 Chain Statistics Viewer - FIXED column indexing per user analysis
Key insight: Header has '#' as field 1, but data rows don't, so indices differ by 1
"""
import numpy as np
import os
import glob
from datetime import datetime

BASE_PATH = "/home/<VM_USER>/Ridder-Field/phase3/chains"

CHAINS = {
    "ΛCDM Baseline": "baseline_lcdm",
    "SH0ES Chain 1": "v3_shoes_theta_chain1",
    "SH0ES Chain 2": "v3_shoes_theta_chain2", 
    "TRGB Chain 1": "v3_trgb_theta_chain1",
    "TRGB Chain 2": "v3_trgb_theta_chain2",
}

# Key parameters to display
KEY_PARAMS = ['theta_s_1e2', 'H0', 'omega_b', 'omega_cdm', 'n_s', 'tau_reio',
              'ridder_Lambda_EDE_eV', 'ridder_a_c', 'ridder_sigma_lna',
              'chi2', 'chi2__CMB', 'chi2__BAO']

def load_chain(prefix):
    """Load chain data from txt file with proper column mapping"""
    pattern = f"{BASE_PATH}/{prefix}*.txt"
    files = glob.glob(pattern)
    
    # Get the main chain file (not .progress, .updated, etc)
    chain_files = [f for f in files if f.endswith('.txt') and 
                   not any(x in f for x in ['progress', 'updated', 'input', 'info', 'covmat'])]
    if not chain_files:
        return None, None, None
    
    try:
        with open(chain_files[0], 'r') as f:
            header_line = f.readline().strip()
        
        # Parse header - split by whitespace, remove '#' prefix
        # Header: "# weight minuslogpost logA n_s H0 omega_b ..."
        # After split: ['#', 'weight', 'minuslogpost', 'logA', 'n_s', 'H0', ...]
        raw_header = header_line.split()
        
        # Remove '#' from start if present
        if raw_header[0] == '#':
            header = raw_header[1:]  # ['weight', 'minuslogpost', 'logA', 'n_s', 'H0', ...]
        else:
            header = raw_header
        
        # Load data - numpy skips header row
        data = np.loadtxt(chain_files[0], skiprows=1)
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        return header, data, chain_files[0]
    except Exception as e:
        print(f"  Error loading: {e}")
        return None, None, None

def print_column_map(header):
    """Print column mapping for debugging"""
    print(f"\n  Column Map (first 12):")
    for i, h in enumerate(header[:12]):
        print(f"    {i}: {h}")

def print_chain_stats(name, header, data, show_column_map=False):
    """Print statistics for a chain"""
    if header is None or data is None or len(data) == 0:
        print(f"  No data yet (still in burn-in)")
        return None
    
    n_samples = len(data)
    print(f"  Samples: {n_samples}")
    
    if show_column_map:
        print_column_map(header)
    
    # Create column lookup: header index = data column index
    col_map = {h: i for i, h in enumerate(header)}
    
    # Get weight column for weighted stats
    weight_idx = col_map.get('weight', 0)
    weights = data[:, weight_idx] if weight_idx < data.shape[1] else np.ones(n_samples)
    
    stats = {}
    
    print(f"\n  {'Parameter':<25} {'Last':<12} {'Mean±Std':<20} {'Unique':<8}")
    print(f"  {'-'*65}")
    
    for param in KEY_PARAMS:
        if param not in col_map:
            continue
            
        col_idx = col_map[param]
        if col_idx >= data.shape[1]:
            continue
            
        values = data[:, col_idx]
        
        # Count unique values (important for detecting frozen params)
        n_unique = len(np.unique(np.round(values, 6)))
        
        # Weighted mean and std
        mean = np.average(values, weights=weights)
        var = np.average((values - mean)**2, weights=weights)
        std = np.sqrt(var) if var > 0 else 0
        last = values[-1]
        
        stats[param] = {'mean': mean, 'std': std, 'last': last, 'n_unique': n_unique}
        
        # Format output based on parameter type
        if 'chi2' in param.lower():
            mean_std = f"{mean:.1f} ± {std:.1f}"
            print(f"  {param:<25} {last:<12.1f} {mean_std:<20} {n_unique}")
        elif param == 'theta_s_1e2':
            mean_std = f"{mean:.5f} ± {std:.5f}"
            frozen = " ⚠️FROZEN!" if n_unique <= 2 else ""
            print(f"  {param:<25} {last:<12.5f} {mean_std:<20} {n_unique}{frozen}")
        elif param == 'H0':
            mean_std = f"{mean:.2f} ± {std:.2f}"
            # Only flag frozen if we have enough samples AND low unique count
            if n_samples >= 10 and n_unique <= 3:
                frozen = " ⚠️FROZEN!"
            elif n_samples < 10:
                frozen = " (need more samples)"
            else:
                frozen = " ✅"
            print(f"  {param:<25} {last:<12.2f} {mean_std:<20} {n_unique}{frozen}")
        elif 'omega' in param:
            mean_std = f"{mean:.5f} ± {std:.5f}"
            print(f"  {param:<25} {last:<12.5f} {mean_std:<20} {n_unique}")
        elif 'ridder_a_c' in param:
            mean_std = f"{mean:.2e} ± {std:.1e}"
            print(f"  {param:<25} {last:<12.2e} {mean_std:<20} {n_unique}")
        else:
            mean_std = f"{mean:.4f} ± {std:.4f}"
            print(f"  {param:<25} {last:<12.4f} {mean_std:<20} {n_unique}")
    
    return stats

def verify_h0_chi2(header, data, prior_mean, prior_sigma, chi2_col_name):
    """Verify that chi2 from H0 prior matches expected formula"""
    col_map = {h: i for i, h in enumerate(header)}
    
    if 'H0' not in col_map or chi2_col_name not in col_map:
        return
    
    h0_idx = col_map['H0']
    chi2_idx = col_map[chi2_col_name]
    
    # Check last row
    h0_val = data[-1, h0_idx]
    chi2_val = data[-1, chi2_idx]
    expected = ((h0_val - prior_mean) / prior_sigma) ** 2
    
    match = abs(chi2_val - expected) < 0.1
    print(f"\n  H0 Prior Check: H0={h0_val:.2f}, chi2={chi2_val:.4f}, expected={expected:.4f}, match={match}")

def main():
    print("=" * 75)
    print("V3 CHAIN PARAMETER STATISTICS (FIXED COLUMN INDEXING)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 75)
    
    all_stats = {}
    
    # Show column map for first chain only
    first_chain = True
    
    for name, prefix in CHAINS.items():
        print(f"\n{'─' * 75}")
        chain_type = "SH0ES (H0=73.04±1.04)" if "SH0ES" in name else "TRGB (H0=69.8±1.7)"
        print(f"  {name} [{chain_type}]")
        print(f"{'─' * 75}")
        
        header, data, filepath = load_chain(prefix)
        
        if filepath:
            print(f"  File: {os.path.basename(filepath)}")
        
        stats = print_chain_stats(name, header, data, show_column_map=first_chain)
        first_chain = False
        
        if stats:
            all_stats[name] = stats
            
            # Verify H0 chi2 formula
            if "SH0ES" in name:
                verify_h0_chi2(header, data, 73.04, 1.04, 'chi2__sh0es_h0')
            else:
                verify_h0_chi2(header, data, 69.8, 1.7, 'chi2__trgb_h0')
    
    # Summary by prior type
    shoes_stats = {k: v for k, v in all_stats.items() if 'SH0ES' in k}
    trgb_stats = {k: v for k, v in all_stats.items() if 'TRGB' in k}
    
    print(f"\n{'=' * 75}")
    print("SUMMARY BY PRIOR TYPE")
    print(f"{'=' * 75}")
    
    for group_name, group_stats, prior_desc in [
        ("SH0ES COMBINED", shoes_stats, "H₀ = 73.04 ± 1.04"),
        ("TRGB COMBINED", trgb_stats, "H₀ = 69.8 ± 1.7")
    ]:
        print(f"\n  {group_name} ({prior_desc})")
        print(f"  {'-'*65}")
        
        if not group_stats:
            print(f"  ⏳ No samples yet")
            continue
        
        # Combine stats
        total_samples = sum(s.get('H0', {}).get('n_unique', 0) for s in group_stats.values())
        
        for param in ['H0', 'omega_cdm', 'ridder_Lambda_EDE_eV', 'chi2']:
            means = [s[param]['mean'] for s in group_stats.values() if param in s]
            if means:
                avg = np.mean(means)
                spread = np.std(means) if len(means) > 1 else 0
                n_unique = sum(s[param]['n_unique'] for s in group_stats.values() if param in s)
                
                if param == 'H0':
                    # Need at least 10 samples to judge if frozen
                    if n_unique <= 3 and n_unique < len(group_stats) * 5:
                        frozen = " ⚠️ H0 FROZEN!" 
                    else:
                        frozen = " ✅"
                    print(f"  {param:<20} mean={avg:.2f} spread=±{spread:.2f} unique={n_unique}{frozen}")
                elif 'chi2' in param:
                    print(f"  {param:<20} mean={avg:.1f} spread=±{spread:.1f}")
                else:
                    print(f"  {param:<20} mean={avg:.4f} spread=±{spread:.4f}")
    
    # Diagnostic summary
    print(f"\n{'=' * 75}")
    print("DIAGNOSTIC NOTES")
    print(f"{'=' * 75}")
    print("  • If H0 shows 'FROZEN' (unique ≤ 2), the sampler is not exploring H0")
    print("  • Check that chi2 from H0 prior matches expected formula")
    print("  • For production runs, increase max_samples to 10000+")
    print(f"{'=' * 75}")

if __name__ == "__main__":
    main()
