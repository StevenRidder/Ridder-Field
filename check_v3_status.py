#!/usr/bin/env python3
"""
check_v3_status.py - Monitor V3 MCMC chains on Azure VM

Usage:
    python3 check_v3_status.py              # Check all 3 runs
    python3 check_v3_status.py baseline     # Check baseline only
    python3 check_v3_status.py trgb         # Check TRGB only
    python3 check_v3_status.py shoes        # Check SH0ES only
"""

import os
import sys
import subprocess
import numpy as np
from datetime import datetime
import re

# Remote VM settings
VM_HOST = "ridderadmin@172.174.34.125"
VM_PATH = "/home/ridderadmin/Ridder-Field/phase3"

# Chain configurations
CHAINS = {
    "baseline": {
        "name": "V3 Baseline (No H0 Prior)",
        "output": "chains/ridder_v3_baseline",
        "target_H0": (67.0, 70.0),  # Expect natural value
        "log": "logs/v3_baseline.log"
    },
    "trgb": {
        "name": "V3 TRGB Branch (H0 = 69.8 ± 1.7)",
        "output": "chains/ridder_v3_trgb",
        "target_H0": (68.1, 71.5),  # TRGB range
        "log": "logs/v3_trgb.log"
    },
    "shoes": {
        "name": "V3 SH0ES Branch (H0 = 73.0 ± 1.0)",
        "output": "chains/ridder_v3_shoes",
        "target_H0": (72.0, 74.0),  # SH0ES range
        "log": "logs/v3_shoes.log"
    }
}

def run_remote(cmd):
    """Run command on remote VM"""
    full_cmd = f'ssh {VM_HOST} "cd {VM_PATH} && {cmd}"'
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"

def check_process_running(chain_name):
    """Check if MCMC process is still running"""
    output = run_remote(f"ps aux | grep 'ridder_v3_{chain_name}.yaml' | grep -v grep")
    return bool(output.strip())

def get_log_tail(log_file, lines=20):
    """Get tail of log file"""
    output = run_remote(f"tail -{lines} {log_file} 2>/dev/null")
    return output if output and not output.startswith("ERROR") else None

def parse_chain_progress(chain_prefix):
    """Parse chain files to get progress statistics"""
    # Get all chain files for this run
    cmd = f"ls -1 {chain_prefix}.*.txt 2>/dev/null"
    output = run_remote(cmd)
    
    if not output or output.startswith("ERROR"):
        return None
    
    chain_files = output.strip().split('\n')
    if not chain_files or chain_files == ['']:
        return None
    
    stats = {
        "n_chains": len(chain_files),
        "samples_per_chain": [],
        "H0_mean": [],
        "Lambda_tail_mean": [],
        "f_EDE_mean": []
    }
    
    for chain_file in chain_files:
        # Get line count
        line_count = run_remote(f"wc -l {chain_file} 2>/dev/null | awk '{{print $1}}'")
        try:
            n_samples = int(line_count.strip()) - 1  # Subtract header
            stats["samples_per_chain"].append(n_samples)
        except:
            continue
        
        # Get parameter means from last 100 samples
        cmd = f"tail -100 {chain_file} 2>/dev/null | awk '{{h+=$5; lt+=$8; fede+=$9; n++}} END {{print h/n, lt/n, fede/n}}'"
        means = run_remote(cmd)
        try:
            h0, lt, fede = map(float, means.strip().split())
            stats["H0_mean"].append(h0)
            stats["Lambda_tail_mean"].append(lt)
            stats["f_EDE_mean"].append(fede)
        except:
            continue
    
    return stats if stats["samples_per_chain"] else None

def format_progress_bar(current, target, width=30):
    """Create ASCII progress bar"""
    frac = min(current / target, 1.0)
    filled = int(width * frac)
    bar = "█" * filled + "░" * (width - filled)
    pct = frac * 100
    return f"[{bar}] {pct:5.1f}%"

def print_header(title):
    print("\n" + "═" * 80)
    print(f"  {title}")
    print("═" * 80)

def check_chain(chain_key):
    """Check status of a single chain"""
    config = CHAINS[chain_key]
    
    print_header(config["name"])
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Check if running
    is_running = check_process_running(chain_key)
    status_icon = "🔄" if is_running else "✅"
    status_text = "RUNNING" if is_running else "COMPLETED"
    print(f"\nProcess: {status_icon} {status_text}")
    
    # 2. Parse chain progress
    stats = parse_chain_progress(config["output"])
    
    if stats:
        print(f"\nChains: {stats['n_chains']} active")
        
        # Progress for each chain
        for i, n_samples in enumerate(stats["samples_per_chain"], 1):
            progress = format_progress_bar(n_samples, 10000)
            print(f"  Chain {i}: {progress}  ({n_samples:5d}/10000 samples)")
        
        # Current parameter estimates (from last 100 samples)
        if stats["H0_mean"]:
            H0_mean = np.mean(stats["H0_mean"])
            H0_std = np.std(stats["H0_mean"])
            lt_mean = np.mean(stats["Lambda_tail_mean"])
            fede_mean = np.mean(stats["f_EDE_mean"])
            
            print("\n📊 Current Estimates (last 100 samples):")
            
            # H0 with target check
            target_lo, target_hi = config["target_H0"]
            h0_status = "✅" if target_lo <= H0_mean <= target_hi else "⚠️"
            print(f"  {h0_status} H₀ = {H0_mean:.2f} ± {H0_std:.2f} km/s/Mpc  (target: {target_lo:.1f}-{target_hi:.1f})")
            
            print(f"     Λ_tail = {lt_mean:.3f} meV")
            print(f"     f_EDE = {fede_mean:.3%}")
    else:
        print("\n⚠️  No chain files found yet")
        print("   (Chains may still be initializing)")
    
    # 3. Show recent log output
    log_tail = get_log_tail(config["log"], 15)
    if log_tail:
        print("\n📋 Recent Log:")
        print("─" * 80)
        for line in log_tail.strip().split('\n')[-10:]:
            print(f"  {line}")
        print("─" * 80)
    
    # 4. Check for errors
    error_check = run_remote(f"grep -i 'error\\|exception\\|failed' {config['log']} 2>/dev/null | tail -3")
    if error_check and error_check.strip() and not error_check.startswith("ERROR"):
        print("\n⚠️  ERRORS DETECTED:")
        print("─" * 80)
        for line in error_check.strip().split('\n'):
            print(f"  {line}")
        print("─" * 80)

def main():
    # Determine which chains to check
    if len(sys.argv) > 1:
        chain_key = sys.argv[1].lower()
        if chain_key not in CHAINS:
            print(f"Error: Unknown chain '{chain_key}'")
            print(f"Valid options: {', '.join(CHAINS.keys())}")
            sys.exit(1)
        chains_to_check = [chain_key]
    else:
        chains_to_check = list(CHAINS.keys())
    
    print("═" * 80)
    print("  V3 MCMC STATUS MONITOR")
    print("═" * 80)
    
    # Check each chain
    for chain_key in chains_to_check:
        check_chain(chain_key)
    
    # Overall summary
    print_header("SUMMARY")
    
    any_running = False
    for chain_key in chains_to_check:
        is_running = check_process_running(chain_key)
        any_running = any_running or is_running
        status = "🔄 Running" if is_running else "✅ Complete"
        print(f"  {CHAINS[chain_key]['name']:40s} {status}")
    
    print("\n" + "═" * 80)
    
    if any_running:
        print("\n💡 TIP: Run this script periodically to monitor progress")
        print("   Watch for H₀ convergence and chain mixing (Rminus1 → 0.01)")
    else:
        print("\n✅ All requested chains appear complete!")
        print("   Next: Analyze with getdist and create publication plots")
    
    print()

if __name__ == "__main__":
    main()

