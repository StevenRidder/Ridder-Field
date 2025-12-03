#!/usr/bin/env python3
"""
V3 Tier 3 Test Status Checker - 4 Chains
Monitors progress DURING burn-in AND after
"""
import os
import subprocess
import numpy as np
import sys
import re

# Run locally on VM
CHAINS_DIR = os.path.expanduser("~/Ridder-Field/phase3/chains")
CHAIN_PREFIX = "v3_tier3_test_chain"

print("=" * 70)
print("V3 TIER 3 TEST: PLANCK FULL + BAO + SH0ES STATUS")
print("=" * 70)
print()

# 1. Check Processes
proc_result = subprocess.run(
    "ps aux | grep 'cobaya-run' | grep -v grep | wc -l",
    shell=True, capture_output=True, text=True
)
n_procs = int(proc_result.stdout.strip() or 0)
print(f"Processes running: {n_procs}")
if n_procs == 0:
    print("❌ CRITICAL: No chains are running!")
else:
    print(f"✅ {n_procs} cobaya processes active")
print()

# 2. Check Progress for each chain
total_samples = 0
all_data = []
chain_status = []

for i in range(1, 5):
    work_dir = f"{CHAINS_DIR}/{CHAIN_PREFIX}{i}_work"
    chain_file = f"{CHAINS_DIR}/{CHAIN_PREFIX}{i}.1.txt"
    log_file = f"{work_dir}/chain{i}.log"
    
    print(f"Chain {i}:")
    
    # Check for chain data file first
    if os.path.exists(chain_file):
        try:
            data = np.loadtxt(chain_file, skiprows=1)
            if data.ndim == 1:
                data = data.reshape(1, -1)
            n_samples = len(data)
            total_samples += n_samples
            
            # Get stats: 0:weight, 1:minuslogpost, 2:logA, 3:ns, 4:H0, 5:wb, 6:wcdm, 7:tau
            # 8:Lambda_EDE, 9:a_c, 10:sigma_lna
            h0 = data[-1, 4]
            lam = data[-1, 8]
            ac = data[-1, 9]
            chi2 = data[-1, 1] * 2
            
            all_data.append(data)
            chain_status.append((n_samples, h0, lam, ac, chi2))
            print(f"  ✅ {n_samples} samples | H0={h0:.2f} | Λ_EDE={lam:.4f} | a_c={ac:.5f} | χ²={chi2:.1f}")
            continue
        except Exception as e:
            print(f"  ⚠️ Error reading chain: {e}")
    
    # No chain file yet - check log for burn-in progress
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                content = f.read()
            
            # Find all Progress lines
            progress_lines = re.findall(r'\[mcmc\] Progress.*', content)
            if progress_lines:
                last_progress = progress_lines[-1]
                # Extract steps and burn-in info
                match = re.search(r'(\d+) steps taken.*?(\d+) accepted steps left', last_progress)
                if match:
                    steps = int(match.group(1))
                    left = int(match.group(2))
                    print(f"  🔄 Burn-in: {steps} steps, {left} left until sampling")
                    chain_status.append(('burn-in', steps, left))
                    continue
                else:
                    print(f"  🔄 {last_progress[-60:]}")
                    continue
            
            # Check for errors
            if 'ERROR' in content:
                errors = re.findall(r'ERROR.*', content)
                if errors:
                    print(f"  ❌ ERROR: {errors[-1][:60]}...")
                    continue
            
            print(f"  ⏳ Initializing...")
        except Exception as e:
            print(f"  ⚠️ Cannot read log: {e}")
    else:
        print(f"  ⏳ No log file yet")

print()
print("-" * 70)

# Summary
if total_samples > 0:
    print("SUMMARY - Chain Data:")
    print(f"{'Chain':<8} | {'Samples':<8} | {'H0':<8} | {'Lambda':<8} | {'a_c':<10} | {'Chi2':<8}")
    print("-" * 65)
    
    for i, status in enumerate(chain_status, 1):
        if isinstance(status[0], int):  # Has samples
            n, h0, lam, ac, chi2 = status
            print(f"Chain {i:<2} | {n:<8} | {h0:<8.2f} | {lam:<8.4f} | {ac:<10.5f} | {chi2:<8.1f}")
    
    # Combined stats
    combined = np.vstack([d for d in all_data])
    print("-" * 65)
    print(f"TOTAL: {total_samples} samples across {len(all_data)} chain(s)")
    print()
    print(f"H0:         {np.mean(combined[:, 4]):.2f} ± {np.std(combined[:, 4]):.2f} km/s/Mpc")
    print(f"Lambda_EDE: {np.mean(combined[:, 8]):.4f} ± {np.std(combined[:, 8]):.4f} eV")
    print(f"a_c:        {np.mean(combined[:, 9]):.5f} ± {np.std(combined[:, 9]):.5f}")
    
    avg_h0 = np.mean(combined[:, 4])
    if avg_h0 > 72.0:
        print("\n✅ RESULT: High H0 maintained! Ridder Field solves H0 tension.")
    elif avg_h0 < 68.0:
        print("\n❌ RESULT: H0 dropped. Planck pulls stronger than SH0ES.")
    else:
        print("\n⚠️ RESULT: Transition region. Competition between datasets.")
else:
    print("STATUS: All chains still in burn-in phase")
    print()
    burn_progress = [(s[1], s[2]) for s in chain_status if s[0] == 'burn-in']
    if burn_progress:
        avg_steps = np.mean([p[0] for p in burn_progress])
        avg_left = np.mean([p[1] for p in burn_progress])
        print(f"Average burn-in progress: {avg_steps:.0f} steps, ~{avg_left:.0f} remaining")
        est_time = avg_left * 1.5  # ~1.5 min per step
        print(f"Estimated time to data: ~{est_time:.0f} minutes")

print("=" * 70)
