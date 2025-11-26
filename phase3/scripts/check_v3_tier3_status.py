#!/usr/bin/env python3
"""
V3 Tier 3 Test Status Checker - 4 Chains
Matches Tier 3 format exactly
"""
import glob
import os
import numpy as np
import sys
import subprocess

VM_HOST = "ridderadmin@172.174.34.125"
VM_PATH = "/home/ridderadmin/Ridder-Field/phase3"

def run_remote(cmd):
    """Run command on remote VM"""
    full_cmd = f'ssh -o ConnectTimeout=10 {VM_HOST} "cd {VM_PATH} && {cmd}"'
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout
    except:
        return ""

print("=" * 70)
print("V3 TIER 3 TEST: PLANCK FULL + BAO + SH0ES STATUS")
print("=" * 70)
print()

# 1. Check Processes
proc = run_remote("ps aux | grep 'v3_tier3_test' | grep -v grep")
proc_ids = [p for p in proc.strip().split('\n') if p]
print(f"Processes running: {len(proc_ids)}/4")
if len(proc_ids) == 0:
    print("❌ CRITICAL: No chains are running!")
elif len(proc_ids) < 4:
    print(f"⚠️  WARNING: Only {len(proc_ids)} chains running")
else:
    print("✅ All 4 chains active")
print()

# 2. Check Chain Files
chain_files = []
for i in range(1, 5):
    chain_file = f"{VM_PATH}/chains/v3_tier3_test_chain{i}.1.txt"
    chain_data = run_remote(f"tail -5 {chain_file} 2>/dev/null")
    if chain_data.strip():
        chain_files.append((f"chain{i}", chain_file))

if not chain_files:
    print("⏳ No chain files yet - checking logs...")
    for i in range(1, 5):
        log = run_remote(f"tail -1 chains/v3_tier3_test_chain{i}_work/chain{i}.log 2>/dev/null")
        if log.strip():
            last = log.strip()
            if len(last) > 80: last = last[:80] + "..."
            print(f"  Chain {i}: {last}")
        else:
            print(f"  Chain {i}: No log yet")
    print("\nWait 5-10 mins for first samples.")
    sys.exit(0)

print(f"✅ Found {len(chain_files)} chain file(s)\n")

# 3. Analyze Data
total_samples = 0
all_lambda = []
all_ac = []
all_H0 = []
all_chi2 = []

print(f"{'Chain':<10} | {'Samples':<7} | {'Lambda':<8} | {'a_c':<8} | {'H0':<6} | {'Chi2':<8}")
print("-" * 65)

for name, cf in sorted(chain_files):
    try:
        # Get data from remote
        data_raw = run_remote(f"tail -50 {cf} 2>/dev/null")
        lines = [l.strip() for l in data_raw.strip().split('\n') if l.strip()]
        data_lines = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 10 and not line.startswith('#'):
                try:
                    data_lines.append([float(p) for p in parts[:15]])
                except:
                    continue
        
        if not data_lines:
            print(f"{name:<10} | Error: No data")
            continue
            
        data = np.array(data_lines)
        n = len(data)
        total_samples += n
        
        # Column mapping: 0:weight, 1:minuslogpost, 2:logA, 3:ns, 4:H0, 5:wb, 6:wcdm, 7:tau
        # 8:Lambda_EDE, 9:a_c, 10:sigma_lna
        COL_H0 = 4
        COL_LAMBDA = 8
        COL_AC = 9
        COL_CHI2 = 1
        
        lambda_val = data[-1, COL_LAMBDA]
        ac_val = data[-1, COL_AC]
        h0 = data[-1, COL_H0]
        chi2 = data[-1, COL_CHI2] * 2
        
        all_lambda.append(lambda_val)
        all_ac.append(ac_val)
        all_H0.append(h0)
        all_chi2.append(chi2)
        
        print(f"{name:<10} | {n:<7} | {lambda_val:<8.4f} | {ac_val:<8.5f} | {h0:<6.2f} | {chi2:<8.1f}")
        
    except Exception as e:
        print(f"{name:<10} | Error reading: {e}")

if total_samples > 0:
    print("-" * 65)
    print("SUMMARY")
    print(f"Total Samples: {total_samples}")
    print(f"Lambda_EDE: {np.mean(all_lambda):.4f} ± {np.std(all_lambda):.4f}")
    print(f"a_c:        {np.mean(all_ac):.5f} ± {np.std(all_ac):.5f}")
    print(f"H0:         {np.mean(all_H0):.2f} ± {np.std(all_H0):.2f}")
    
    # Diagnosis
    avg_h0 = np.mean(all_H0)
    if avg_h0 > 72.0:
        print("\n✅ RESULT: High H0 maintained! Ridder Field solves H0 tension.")
    elif avg_h0 < 68.0:
        print("\n❌ RESULT: H0 dropped. Planck pulls stronger than SH0ES.")
    else:
        print("\n⚠️ RESULT: Transition region. Competition between datasets.")

print("=" * 70)

