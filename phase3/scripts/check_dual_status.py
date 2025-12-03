#!/usr/bin/env python3
"""
V3 Dual Prior Status Checker - SH0ES + TRGB Combined
"""
import subprocess
import re
import sys
from datetime import datetime

# Chain configurations
CHAINS = {
    "shoes": {
        "name": "SH0ES",
        "h0_prior": "73.04 ± 1.04",
        "path_prefix": "v3_tier3_test_chain",
        "count": 2
    },
    "trgb": {
        "name": "TRGB", 
        "h0_prior": "69.8 ± 1.7",
        "path_prefix": "v3_trgb_test_chain",
        "count": 2
    }
}

BASE_PATH = "/home/ridderadmin/Ridder-Field/phase3/chains"

def get_chain_status(path_prefix, chain_num):
    """Get status for a single chain"""
    log_path = f"{BASE_PATH}/{path_prefix}{chain_num}_work/chain{chain_num}.log"
    
    try:
        # Get last progress line
        result = subprocess.run(
            f"grep 'Progress @' {log_path} 2>/dev/null | tail -1",
            shell=True, capture_output=True, text=True, timeout=5
        )
        progress_line = result.stdout.strip()
        
        if not progress_line:
            return {"status": "initializing", "steps": 0, "phase": "init"}
        
        # Parse: [mcmc] Progress @ 2025-11-26 06:39:14 : 102 steps taken -- still burning in, 2 accepted steps left.
        # or: [mcmc] Progress @ 2025-11-26 06:39:14 : 150 steps taken, 50 accepted.
        
        steps_match = re.search(r'(\d+) steps taken', progress_line)
        steps = int(steps_match.group(1)) if steps_match else 0
        
        if "burning in" in progress_line:
            remaining_match = re.search(r'(\d+) accepted steps left', progress_line)
            remaining = int(remaining_match.group(1)) if remaining_match else 0
            return {"status": "burn-in", "steps": steps, "remaining": remaining, "phase": "burn-in"}
        elif "accepted" in progress_line:
            accepted_match = re.search(r'(\d+) accepted', progress_line)
            accepted = int(accepted_match.group(1)) if accepted_match else 0
            return {"status": "sampling", "steps": steps, "accepted": accepted, "phase": "sampling"}
        else:
            return {"status": "running", "steps": steps, "phase": "unknown"}
            
    except Exception as e:
        return {"status": "error", "steps": 0, "phase": "error", "error": str(e)}

def check_processes():
    """Count running cobaya processes"""
    result = subprocess.run(
        "ps aux | grep cobaya | grep -v grep | wc -l",
        shell=True, capture_output=True, text=True
    )
    return int(result.stdout.strip())

def main():
    print("=" * 70)
    print("V3 DUAL PRIOR TEST: SH0ES + TRGB STATUS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    total_steps = 0
    total_accepted = 0
    total_chains = 0
    chains_sampling = 0
    chains_burnin = 0
    
    for prior_key, prior_info in CHAINS.items():
        print(f"\n{'─' * 70}")
        print(f"  {prior_info['name']} (H₀ = {prior_info['h0_prior']} km/s/Mpc)")
        print(f"{'─' * 70}")
        
        for i in range(1, prior_info["count"] + 1):
            status = get_chain_status(prior_info["path_prefix"], i)
            total_chains += 1
            
            if status["phase"] == "init":
                print(f"  Chain {i}: ⏳ Initializing (loading Planck data...)")
            elif status["phase"] == "burn-in":
                chains_burnin += 1
                total_steps += status["steps"]
                print(f"  Chain {i}: 🔄 Burn-in: {status['steps']} steps, {status['remaining']} left")
            elif status["phase"] == "sampling":
                chains_sampling += 1
                total_steps += status["steps"]
                total_accepted += status.get("accepted", 0)
                print(f"  Chain {i}: ✅ Sampling: {status['steps']} steps, {status['accepted']} accepted")
            elif status["phase"] == "error":
                print(f"  Chain {i}: ❌ Error: {status.get('error', 'unknown')}")
            else:
                total_steps += status["steps"]
                print(f"  Chain {i}: ⚙️  Running: {status['steps']} steps")
    
    # Summary
    print(f"\n{'=' * 70}")
    print("COMBINED SUMMARY")
    print(f"{'=' * 70}")
    
    procs = check_processes()
    print(f"  Processes running:  {procs} / {total_chains} expected")
    print(f"  Chains in burn-in:  {chains_burnin}")
    print(f"  Chains sampling:    {chains_sampling}")
    print(f"  Total steps taken:  {total_steps}")
    if total_accepted > 0:
        print(f"  Total accepted:     {total_accepted}")
    
    # Status indicator
    print()
    if procs == 0:
        print("  ❌ STATUS: NO CHAINS RUNNING!")
    elif procs < total_chains:
        print(f"  ⚠️  STATUS: Only {procs}/{total_chains} chains running")
    elif chains_sampling == total_chains:
        print("  ✅ STATUS: All chains sampling!")
    elif chains_sampling > 0:
        print(f"  🔄 STATUS: {chains_sampling} chains sampling, {chains_burnin} in burn-in")
    else:
        print("  🔄 STATUS: All chains in burn-in phase")
    
    print(f"{'=' * 70}")

if __name__ == "__main__":
    main()

