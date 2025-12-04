#!/usr/bin/env python3
"""Launch fine-grid H0 fixed chains (68.5, 69.5, 70.5, 71.5)."""
import subprocess
import os
import sys

h0_values = [68.5, 69.5, 70.5, 71.5]

print("="*80)
print("Launching Fine-Grid H0 Fixed Chains")
print("="*80)
print()

for h0 in h0_values:
    config_file = f"configs/tier5_ede_shoes_desi_h0_fixed_{h0}.yaml"
    log_file = f"logs/tier5_ede_h0_fixed_{h0}.log"
    
    if not os.path.exists(config_file):
        print(f"ERROR: Config file not found: {config_file}")
        continue
    
    # Check if already running
    result = subprocess.run(
        ["pgrep", "-f", f"h0_fixed_{h0}"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"H0={h0}: Already running (PID: {result.stdout.strip()})")
        continue
    
    # Launch chain
    cmd = [
        "nohup",
        "cobaya-run",
        config_file,
        ">",
        log_file,
        "2>&1",
        "&"
    ]
    
    print(f"Launching H0={h0}...")
    print(f"  Config: {config_file}")
    print(f"  Log: {log_file}")
    
    # Use shell=True for the redirect
    subprocess.Popen(
        f"nohup cobaya-run {config_file} > {log_file} 2>&1 &",
        shell=True
    )
    
    print(f"  ✓ Started")
    print()

print("="*80)
print("All chains launched. Check status with:")
print("  python3 check_h0_ceiling.py")
print("="*80)
