#!/usr/bin/env python3
"""
V3 Quick Test Status Checker - Full Detail
"""
import subprocess
import numpy as np
import sys
import os

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

print("=" * 80)
print("V3 QUICK TEST: DETAILED STATUS REPORT")
print("=" * 80)
print()

# 1. Check Processes
proc = run_remote("ps aux | grep 'v3_quick_test' | grep -v grep")
if proc.strip():
    print("✅ MCMC Process: RUNNING")
else:
    print("❌ MCMC Process: STOPPED or FINISHED")
print()

# 2. Check Chain Files
chain_file = f"{VM_PATH}/chains/v3_quick_test.1.txt"
# Get last 20 lines
chain_data_raw = run_remote(f"tail -20 {chain_file} 2>/dev/null")

if not chain_data_raw.strip():
    print("⏳ Chain file empty or not created yet (still in burn-in)")
    log = run_remote("grep 'Progress' v3_test.log | tail -1")
    if log.strip():
        print(f"   Log Status: {log.strip()}")
    print("\n   (Cobaya writes to chain file only after burn-in completes)")
    sys.exit(0)

# Parse chain data
lines = [l.strip() for l in chain_data_raw.strip().split('\n') if l.strip()]
data_lines = []
for line in lines:
    parts = line.split()
    if len(parts) >= 10 and not line.startswith('#'):
        try:
            # 0:weight, 1:minuslogpost, 2:logA, 3:ns, 4:H0, 5:omega_b, 6:omega_cdm, 7:tau
            # 8:Lambda_EDE, 9:a_c, 10:sigma_lna
            data_lines.append([float(p) for p in parts[:15]])
        except:
            continue

if not data_lines:
    print("❌ Error parsing chain data")
    sys.exit(1)

data = np.array(data_lines)
total_lines = run_remote(f"wc -l {chain_file}").split()[0]

print(f"📊 Total Samples: {total_lines}")
print()

# Column mapping
COL_H0 = 4
COL_LAMBDA = 8
COL_AC = 9
COL_SIGMA = 10
COL_CHI2 = 1

print("RECENT SAMPLES (Last 10):")
print("-" * 80)
print(f"{'Sample':<8} | {'H0':<8} | {'Λ_EDE':<8} | {'a_c':<10} | {'σ_ln(a)':<8} | {'Chi2':<8}")
print("-" * 80)

for i in range(max(0, len(data)-10), len(data)):
    h0 = data[i, COL_H0]
    lam = data[i, COL_LAMBDA]
    ac = data[i, COL_AC]
    sig = data[i, COL_SIGMA]
    chi2 = data[i, COL_CHI2] * 2
    print(f"{i:<8} | {h0:<8.2f} | {lam:<8.4f} | {ac:<10.5f} | {sig:<8.3f} | {chi2:<8.1f}")

print("-" * 80)
print()

print("STATISTICS (Last 20 samples):")
print("-" * 40)
print(f"H0:         {np.mean(data[:, COL_H0]):.2f} ± {np.std(data[:, COL_H0]):.2f} km/s/Mpc")
print(f"Lambda_EDE: {np.mean(data[:, COL_LAMBDA]):.4f} ± {np.std(data[:, COL_LAMBDA]):.4f} eV")
print(f"a_c:        {np.mean(data[:, COL_AC]):.5f} ± {np.std(data[:, COL_AC]):.5f}")
print("-" * 40)
print()

# Verdict
avg_h0 = np.mean(data[:, COL_H0])
if avg_h0 > 70.0:
    print("✅ VERDICT: High H0 (>70) achieved!")
elif avg_h0 < 68.0:
    print("❌ VERDICT: Low H0 (<68) - Planck pull dominates")
else:
    print("⚠️ VERDICT: Intermediate H0 (68-70)")

print("=" * 80)

