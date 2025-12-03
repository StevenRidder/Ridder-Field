#!/usr/bin/env python3
"""
check_mcmc_status.py - Comprehensive MCMC chain status checker

Usage:
    python3 check_mcmc_status.py              # Check latest run
    python3 check_mcmc_status.py --remote     # Check on VM via SSH
"""

import os
import sys
import json
import numpy as np
import subprocess
from datetime import datetime

# Remote VM settings
VM_HOST = "ridderadmin@172.174.34.125"
VM_PATH = "~/Ridder-Field"
VM_OUTPUT = "~/Ridder-Field/phase2/class/output/mcmc"

def run_remote(cmd):
    """Run command on remote VM"""
    full_cmd = f'ssh {VM_HOST} "{cmd}"'
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"

def check_process_running():
    """Check if MCMC is still running on VM"""
    output = run_remote("ps aux | grep 'mcmc_smoke\\|emcee' | grep -v grep")
    return bool(output.strip())

def get_log_tail(lines=50):
    """Get tail of MCMC log"""
    return run_remote(f"tail -{lines} {VM_PATH}/mcmc_output.log 2>/dev/null")

def get_results_json():
    """Get MCMC results JSON"""
    output = run_remote(f"cat {VM_OUTPUT}/mcmc_results.json 2>/dev/null")
    try:
        return json.loads(output)
    except:
        return None

def get_chain_file():
    """Get chain file info"""
    return run_remote(f"ls -la {VM_OUTPUT}/chain_*.npy 2>/dev/null | tail -5")

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def format_status(value, target_lo, target_hi, name):
    """Format status with color codes"""
    if target_lo <= value <= target_hi:
        return f"✅ {name}: {value:.3f} (target: {target_lo:.2f}-{target_hi:.2f})"
    else:
        diff = min(abs(value - target_lo), abs(value - target_hi))
        return f"❌ {name}: {value:.3f} (target: {target_lo:.2f}-{target_hi:.2f}, off by {diff:.3f})"

def main():
    print_header("MCMC STATUS CHECK")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Check if still running
    is_running = check_process_running()
    print(f"\nProcess status: {'🔄 RUNNING' if is_running else '✅ COMPLETED'}")
    
    # 2. Get log tail
    print_header("RECENT LOG OUTPUT")
    log_tail = get_log_tail(30)
    print(log_tail if log_tail else "No log file found")
    
    # 3. Parse results if available
    results = get_results_json()
    if results:
        print_header("MCMC RESULTS SUMMARY")
        
        # Parameter posteriors
        if "posteriors" in results:
            post = results["posteriors"]
            print("\n📈 Parameter Posteriors:")
            print(f"   Lambda_tail: {post.get('Lambda_tail_mean', 'N/A'):.1f} ± {post.get('Lambda_tail_std', 'N/A'):.1f} meV")
            print(f"   f_axion: {post.get('f_axion_mean', 'N/A'):.3f} ± {post.get('f_axion_std', 'N/A'):.3f}")
        
        # Observable posteriors
        if "observables" in results:
            obs = results["observables"]
            print("\n📊 Observable Posteriors:")
            print(f"   H0: {obs.get('H0_mean', 'N/A'):.2f} ± {obs.get('H0_std', 'N/A'):.2f} km/s/Mpc")
            print(f"   S8: {obs.get('S8_mean', 'N/A'):.3f} ± {obs.get('S8_std', 'N/A'):.3f}")
            print(f"   CMB_RMS: {obs.get('CMB_mean', 'N/A')*100:.1f}% ± {obs.get('CMB_std', 'N/A')*100:.1f}%")
            print(f"   BAO: {obs.get('BAO_mean', 'N/A')*100:.1f}% ± {obs.get('BAO_std', 'N/A')*100:.1f}%")
        
        # Best point
        if "best_point" in results:
            best = results["best_point"]
            print("\n🏆 Best Point (max logL):")
            print(f"   Lambda_tail = {best.get('Lambda_tail', 'N/A'):.1f} meV")
            print(f"   f_axion = {best.get('f_axion', 'N/A'):.3f}")
            print(f"   H0 = {best.get('H0', 'N/A'):.2f} km/s/Mpc")
            print(f"   S8 = {best.get('S8', 'N/A'):.3f}")
            print(f"   CMB_RMS = {best.get('CMB_RMS', 0)*100:.1f}%")
            print(f"   BAO = {best.get('BAO', 0)*100:.1f}%")
            print(f"   logL = {best.get('logL', 'N/A'):.2f}")
        
        # Viable points
        n_viable = results.get("n_viable", 0)
        n_total = results.get("n_samples", 0)
        print(f"\n📋 Viable Points: {n_viable}/{n_total}")
        
        if n_viable == 0:
            print("\n⚠️  NO VIABLE POINTS FOUND")
            print("   The model cannot simultaneously satisfy all constraints.")
    else:
        print("\nNo results JSON found yet.")
    
    # 4. Chain diagnostics
    print_header("CHAIN DIAGNOSTICS")
    chain_info = get_chain_file()
    if chain_info.strip():
        print(chain_info)
    else:
        print("No chain files found")
    
    # 5. Summary verdict
    print_header("VERDICT")
    if is_running:
        print("🔄 MCMC still running - check back later")
    elif results and results.get("n_viable", 0) > 0:
        print("✅ SUCCESS - Viable points found!")
    elif results:
        print("❌ NO-GO - Model 1.0 is excluded by current constraints")
        print("\nNext steps:")
        print("  1. Relax CMB/BAO constraints further")
        print("  2. Add more free parameters (n_tail, theta_i)")
        print("  3. Consider Model 2.0 with different potential shape")
    else:
        print("⚠️  UNKNOWN - No results available")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

