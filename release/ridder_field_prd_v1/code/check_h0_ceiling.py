#!/usr/bin/env python3
"""Check status of H0 fixed chains to test geometric ceiling."""
import numpy as np
import os

def load_chain_simple(fname):
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
        # H0 might be fixed (not in chain), so try to get it or use the fixed value
        h0_val = data[best_idx, col_map.get("H0", -1)] if "H0" in col_map else None
        return {
            "n": len(data),
            "chi2": 2 * data[best_idx, col_map["minuslogpost"]],
            "H0": h0_val,
        }
    except:
        return None

# Load REF
ref = load_chain_simple("chains/tier5_lcdm_shoes_desi.1.txt")
ref_chi2 = ref["chi2"] if ref else None

print("="*80)
print("H0 FIXED CHAIN STATUS (Testing Geometric Ceiling)")
print("="*80)
print()
print("H0    Samples    Chi2        Delta vs REF    Status")
print("-"*80)

# Auto-detect all H0 fixed chains
import glob
chain_files = glob.glob("chains/tier5_ede_shoes_desi_h0_fixed_*.1.txt")
h0_values = []
for f in chain_files:
    # Extract H0 value from filename: tier5_ede_shoes_desi_h0_fixed_XX.1.txt
    try:
        # Handle both "h0_fixed_69.1.txt" and "h0_fixed_68.5.1.txt"
        basename = os.path.basename(f)
        h0_str = basename.split("h0_fixed_")[1].split(".1.txt")[0]
        h0_val = float(h0_str)
        h0_values.append(h0_val)
    except Exception as e:
        continue

# Sort H0 values
h0_values = sorted(h0_values)

# If no chains found, use default coarse grid
if not h0_values:
    h0_values = [69, 70, 71, 72]

results = []

# Helper to check if process is running
def is_chain_running(h0_val):
    import subprocess
    h0_str = f"{int(h0_val)}" if h0_val % 1 == 0 else f"{h0_val}"
    result = subprocess.run(["pgrep", "-f", f"h0_fixed_{h0_str}"], 
                           capture_output=True, text=True)
    return result.returncode == 0

for h0 in h0_values:
    # Format H0: use int if it's a whole number, otherwise use decimal
    h0_str = f"{int(h0)}" if h0 % 1 == 0 else f"{h0}"
    chain_file = f"chains/tier5_ede_shoes_desi_h0_fixed_{h0_str}.1.txt"
    
    running = is_chain_running(h0)
    
    if os.path.exists(chain_file):
        # Check if file is stale (not updated in last 10 minutes)
        import time
        file_mtime = os.path.getmtime(chain_file)
        age_minutes = (time.time() - file_mtime) / 60.0
        is_stale = age_minutes > 10
        
        data = load_chain_simple(chain_file)
        if data:
            delta = data["chi2"] - ref_chi2 if ref_chi2 else np.nan
            # Status: Check if actively updating or stale
            if is_stale and not running:
                status = "Stale"
            elif data["n"] < 500:
                status = "Running" if running else "Stopped"
            else:
                status = "Converging"
            n_val = data["n"]
            chi2_val = data["chi2"]
            # Format H0 (handle both int and float)
            h0_str = f"{int(h0)}" if h0 % 1 == 0 else f"{h0:.1f}"
            print(f"{h0_str:>5s}  {n_val:8d}  {chi2_val:10.1f}  {delta:+13.1f}  {status}")
            results.append({"H0": h0, "n": n_val, "chi2": chi2_val, "delta": delta})
        else:
            h0_str = f"{h0:.1f}" if h0 % 1 != 0 else f"{int(h0)}"
            status = "Running" if running else "Not started"
            print(f"{h0_str:>5s}  {'0':>8}  {'---':>10}  {'---':>13}  {status}")
    else:
        h0_str = f"{h0:.1f}" if h0 % 1 != 0 else f"{int(h0)}"
        status = "Running" if running else "Not started"
        print(f"{h0_str:>5s}  {'0':>8}  {'---':>10}  {'---':>13}  {status}")

if ref_chi2 and len(results) >= 2:
    print()
    print(f"REF (LCDM): Chi2 = {ref_chi2:.1f}")
    print()
    print("="*80)
    print("CEILING TEST:")
    print("="*80)
    results.sort(key=lambda x: x["H0"])
    print("H0 progression:")
    for i, r in enumerate(results):
        if i > 0:
            prev_delta = results[i-1]["delta"]
            jump = r["delta"] - prev_delta
            h0_val = r["H0"]
            delta_val = r["delta"]
            prev_h0 = results[i-1]["H0"]
            print(f"  H0={h0_val}: Delta={delta_val:+.1f} (jump: {jump:+.1f} from H0={prev_h0})")
        else:
            h0_val = r["H0"]
            delta_val = r["delta"]
            print(f"  H0={h0_val}: Delta={delta_val:+.1f}")
    print()
    # Check for sharp elbow
    if len(results) >= 3:
        h0_69 = next((r for r in results if r["H0"] == 69), None)
        h0_70 = next((r for r in results if r["H0"] == 70), None)
        h0_71 = next((r for r in results if r["H0"] == 71), None)
        if h0_69 and h0_70 and h0_71:
            jump_69_to_70 = h0_70["delta"] - h0_69["delta"]
            jump_70_to_71 = h0_71["delta"] - h0_70["delta"]
            print(f"Jump from H0=69 to 70: {jump_69_to_70:+.1f} chi2")
            print(f"Jump from H0=70 to 71: {jump_70_to_71:+.1f} chi2")
            if jump_70_to_71 > 2 * abs(jump_69_to_70):
                print("YES: SHARP ELBOW at H0=70 (hard ceiling detected!)")
            else:
                print("NO: Smooth curve (soft preference, not hard limit)")
