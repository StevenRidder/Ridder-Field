#!/usr/bin/env python3
"""
Tier 3 Status Checker
Verifies progress of Planck + BAO + SH0ES chains
"""
import glob
import os
import numpy as np
import sys

print("=" * 70)
print("TIER 3: PLANCK + BAO + SH0ES STATUS")
print("=" * 70)
print()

# 1. Check Processes
import subprocess
proc_result = subprocess.run(["pgrep", "-f", "cobaya.*ridder_tier3"], capture_output=True, text=True)
proc_ids = [p for p in proc_result.stdout.strip().split("\n") if p]
print(f"Processes running: {len(proc_ids)}/4")
if len(proc_ids) == 0:
    print("❌ CRITICAL: No chains are running!")
elif len(proc_ids) < 4:
    print(f"⚠️  WARNING: Only {len(proc_ids)} chains running")
else:
    print("✅ All 4 chains active")
print()

# 2. Check Chain Files
work_dirs = sorted(glob.glob("chain*_tier3"))
all_chains = []
for wd in work_dirs:
    cf = glob.glob(f"{wd}/chains/ridder_tier3*.txt")
    if cf:
        all_chains.append((os.path.basename(wd), cf[0]))

if not all_chains:
    print("⏳ No chain files yet - checking logs...")
    for i in range(1, 5):
        log = f"chain{i}_tier3/chain{i}.log"
        if os.path.exists(log):
            try:
                with open(log) as f:
                    lines = f.readlines()
                    last = lines[-1].strip() if lines else "Empty log"
                    # Truncate long lines
                    if len(last) > 80: last = last[:80] + "..."
                    print(f"  Chain {i}: {last}")
            except:
                print(f"  Chain {i}: Cannot read log")
    print("\nWait 5-10 mins for first samples.")
    sys.exit(0)

print(f"✅ Found {len(all_chains)} chain file(s)\n")

# 3. Analyze Data
total_samples = 0
all_theta = []
all_beta = []
all_H0 = []
all_chi2 = []

print(f"{'Chain':<10} | {'Samples':<7} | {'Theta_i':<8} | {'Beta':<8} | {'H0':<6} | {'Chi2':<8}")
print("-" * 65)

for name, cf in sorted(all_chains):
    try:
        data = np.loadtxt(cf, skiprows=1)
        if data.ndim == 1: data = data.reshape(1, -1)
        n = len(data)
        total_samples += n
        
        # Get last values
        # theta_i is usually col 8, beta col 9 (check yaml order)
        # In tier 3 yaml:
        # 0:weight, 1:minuslogpost, 2:logA, 3:ns, 4:H0, 5:wb, 6:wcdm, 7:tau, 8:theta, 9:beta
        
        theta = data[-1, 8]
        beta = data[-1, 9]
        h0 = data[-1, 4]
        chi2 = data[-1, -5] # Approximate location of chi2
        
        all_theta.append(theta)
        all_beta.append(beta)
        all_H0.append(h0)
        all_chi2.append(chi2)
        
        print(f"{name:<10} | {n:<7} | {theta:<8.4f} | {beta:<8.4f} | {h0:<6.2f} | {chi2:<8.1f}")
        
    except Exception as e:
        print(f"{name:<10} | Error reading: {e}")

if total_samples > 0:
    print("-" * 65)
    print("SUMMARY")
    print(f"Total Samples: {total_samples}")
    print(f"Theta_i: {np.mean(all_theta):.4f} ± {np.std(all_theta):.4f}")
    print(f"Beta:    {np.mean(all_beta):.4f} ± {np.std(all_beta):.4f}")
    print(f"H0:      {np.mean(all_H0):.2f} ± {np.std(all_H0):.2f}")
    
    # Diagnosis
    avg_theta = np.mean(all_theta)
    if avg_theta > 1.8:
        print("\n✅ RESULT: High Theta maintained! Ridder Field solves H0 tension.")
    elif avg_theta < 1.0:
        print("\n❌ RESULT: Theta dropped. Planck pulls stronger than SH0ES.")
    else:
        print("\n⚠️ RESULT: Transition region. Competition between datasets.")

print("=" * 70)

