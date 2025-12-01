#!/usr/bin/env python3
"""
Phase 2 ACT Status Dashboard
Monitors ACT DR6 chains (LCDM and EDE) for shoulder diagnostic
"""
import numpy as np
import glob
import os
import sys
import subprocess
from datetime import datetime

# Allow running on VM via SSH
CHAIN_DIR = os.path.expanduser("~/Ridder-Field/phase3/chains")
if not os.path.exists(CHAIN_DIR):
    CHAIN_DIR = "chains"

LOG_DIR = os.path.expanduser("~/Ridder-Field/phase3/logs")
if not os.path.exists(LOG_DIR):
    LOG_DIR = "logs"

print("="*110)
print("PHASE 2 ACT DR6: SHOULDER DIAGNOSTIC — LIVE STATUS")
print("="*110)
print(f"Monitoring ACT chains in: {CHAIN_DIR}")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*110)

def check_process_running(chain_name):
    """Check if cobaya process is running for this chain"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", f"cobaya.*{chain_name}"],
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except:
        return False

def get_process_info(chain_name):
    """Get process CPU/memory info"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=2
        )
        for line in result.stdout.split("\n"):
            if f"cobaya.*{chain_name}" in line or f"cobaya-run.*{chain_name}" in line:
                parts = line.split()
                if len(parts) >= 11:
                    return {
                        "pid": parts[1],
                        "cpu": parts[2],
                        "mem": parts[3],
                        "time": parts[9]
                    }
    except:
        pass
    return None

def load_chain(chain_file):
    """Load chain and extract key statistics"""
    try:
        with open(chain_file, "r") as f:
            header = f.readline().strip()
        if header.startswith("#"):
            header = header[1:]
        cols = header.split()
        col_map = {c.strip(): i for i, c in enumerate(cols)}

        data = np.loadtxt(chain_file)
        if len(data.shape) == 1:
            data = data.reshape(1, -1)
        if len(data) < 5:
            return None

        n_samples = len(data)

        # H0
        H0 = np.mean(data[:, col_map["H0"]])
        H0_std = np.std(data[:, col_map["H0"]])

        # S8
        if "S8" in col_map:
            S8 = np.mean(data[:, col_map["S8"]])
        elif "sigma8" in col_map and "Omega_m" in col_map:
            S8 = np.mean(
                data[:, col_map["sigma8"]] * np.sqrt(data[:, col_map["Omega_m"]] / 0.3)
            )
        else:
            S8 = np.nan

        # r_s (sound horizon) - in Mpc
        if "rs_drag" in col_map:
            rs = np.mean(data[:, col_map["rs_drag"]])
        elif "rdrag" in col_map:
            rs = np.mean(data[:, col_map["rdrag"]])
        else:
            rs = np.nan

        # Best-fit chi2
        if "chi2" in col_map:
            best_idx = np.argmin(data[:, col_map["chi2"]])
            chi2_best = data[best_idx, col_map["chi2"]]
        else:
            best_idx = np.argmin(data[:, col_map["minuslogpost"]])
            chi2_best = data[best_idx, col_map["minuslogpost"]] * 2

        # Lambda_EDE for EDE chains
        Lambda_EDE = None
        if "Lambda_EDE_ridder" in col_map:
            Lambda_EDE = np.mean(data[:, col_map["Lambda_EDE_ridder"]])

        return {
            "n": n_samples,
            "H0": H0,
            "H0_std": H0_std,
            "S8": S8,
            "rs": rs,
            "chi2": chi2_best,
            "Lambda_EDE": Lambda_EDE,
        }
    except Exception as e:
        return None

# Find ACT chains
chain_files = glob.glob(f"{CHAIN_DIR}/phase2_act_*.1.txt")
chain_files = sorted(chain_files)

print(f"\n📂 Found {len(chain_files)} chain files:")
for f in chain_files:
    print(f"   - {os.path.basename(f)}")

# Check for progress files (chains initializing)
progress_files = glob.glob(f"{CHAIN_DIR}/phase2_act_*.progress")
if progress_files and not chain_files:
    print(f"\n🔄 Chains initializing ({len(progress_files)} progress files found)")
    for pf in progress_files:
        name = os.path.basename(pf).replace(".progress", "")
        try:
            with open(pf, "r") as f:
                progress = f.read().strip()
            print(f"   {name}: {progress}")
        except:
            print(f"   {name}: initializing...")

if not chain_files and not progress_files:
    print("\n⚠️  No ACT chains found yet.")
    print(f"   Looking in: {CHAIN_DIR}")
    print("   Run: cobaya-run configs/phase2_act_lcdm.yaml -o chains/phase2_act_lcdm")
    sys.exit(0)

# Process each chain
chains = {}
for f in chain_files:
    name = os.path.basename(f).replace(".1.txt", "")
    data = load_chain(f)
    
    # Determine model type
    if "lcdm" in name.lower():
        model = "ΛCDM"
    elif "ede" in name.lower():
        model = "EDE"
    else:
        model = "Unknown"
    
    chains[name] = {
        "model": model,
        "file": f,
        "data": data
    }

# Display status
print(f"\n{'='*110}")
print("📊 ACT CHAIN STATUS")
print(f"{'='*110}")
print(f"{'Model':<8} {'Chain':<30} {'Status':<12} {'N':>6} {'H0':>7} {'±σ':>5} {'S8':>6} {'r_s':>7} {'χ²':>9} {'Λ_EDE':>8}")
print("-"*110)

for name, info in sorted(chains.items()):
    model = info["model"]
    data = info["data"]
    is_running = check_process_running(name)
    proc_info = get_process_info(name)
    
    if data is None:
        status = "🔄 Init"
        if is_running:
            status += " (running)"
        print(f"{model:<8} {name:<30} {status:<12} {'---':>6} {'---':>7} {'---':>5} {'---':>6} {'---':>7} {'---':>9} {'---':>8}")
        continue
    
    # Status based on samples
    if data["n"] >= 2000:
        status = "✅ Ready"
    elif data["n"] >= 1000:
        status = "✅ >1000"
    elif data["n"] >= 500:
        status = "🔄 >500"
    elif data["n"] >= 100:
        status = "🔄 Running"
    else:
        status = "🔄 Start"
    
    if is_running and proc_info:
        status += f" (PID:{proc_info['pid']}, CPU:{proc_info['cpu']}%)"
    
    rs_str = f"{data['rs']:.1f}" if not np.isnan(data["rs"]) else "---"
    S8_str = f"{data['S8']:.3f}" if not np.isnan(data["S8"]) else "---"
    lambda_str = f"{data['Lambda_EDE']:.2f}" if data['Lambda_EDE'] is not None else "---"
    
    print(f"{model:<8} {name:<30} {status:<12} {data['n']:>6} {data['H0']:>7.2f} {data['H0_std']:>5.2f} {S8_str:>6} {rs_str:>7} {data['chi2']:>9.1f} {lambda_str:>8}")

# Δχ² Analysis
print(f"\n{'='*110}")
print("📐 Δχ² ANALYSIS: EDE vs ΛCDM")
print(f"{'='*110}")

lcdm_data = None
ede_data = None

for name, info in chains.items():
    if info["model"] == "ΛCDM" and info["data"]:
        lcdm_data = info["data"]
    elif info["model"] == "EDE" and info["data"]:
        ede_data = info["data"]

if lcdm_data and ede_data:
    dchi2 = ede_data["chi2"] - lcdm_data["chi2"]
    dH0 = ede_data["H0"] - lcdm_data["H0"]
    drs = ede_data["rs"] - lcdm_data["rs"] if not np.isnan(ede_data["rs"]) and not np.isnan(lcdm_data["rs"]) else np.nan
    drs_pct = (drs / lcdm_data["rs"] * 100) if not np.isnan(drs) else np.nan
    
    print(f"ΛCDM:  H₀={lcdm_data['H0']:.2f}, r_s={lcdm_data['rs']:.1f} Mpc, χ²={lcdm_data['chi2']:.1f}")
    print(f"EDE:   H₀={ede_data['H0']:.2f}, r_s={ede_data['rs']:.1f} Mpc, χ²={ede_data['chi2']:.1f}, Λ_EDE={ede_data['Lambda_EDE']:.2f}")
    print(f"\nΔχ² = {dchi2:+.1f}  |  ΔH₀ = {dH0:+.2f}  |  Δr_s = {drs:+.2f} Mpc ({drs_pct:+.2f}%)")
    
    if dchi2 < -5:
        print("✅ EDE strongly preferred")
    elif dchi2 < 0:
        print("✅ EDE mildly preferred")
    elif dchi2 < 10:
        print("⚠️  EDE viable but penalized")
    else:
        print("❌ EDE significantly penalized")
else:
    print("⚠️  Need both ΛCDM and EDE chains for comparison")

# Check log files for errors
print(f"\n{'='*110}")
print("📋 RECENT LOG OUTPUT")
print(f"{'='*110}")

for name in sorted(chains.keys()):
    log_file = f"{LOG_DIR}/phase2_act_{name.replace('phase2_act_', '')}.log"
    if os.path.exists(log_file):
        try:
            result = subprocess.run(
                ["tail", "-5", log_file],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.stdout.strip():
                print(f"\n{name}:")
                print(result.stdout.strip())
        except:
            pass

# Summary
print(f"\n{'='*110}")
print("🎯 SUMMARY")
print(f"{'='*110}")

total_samples = sum(info["data"]["n"] for info in chains.values() if info["data"])
n_running = sum(1 for name in chains.keys() if check_process_running(name))

print(f"Total chains: {len(chains)}")
print(f"Total samples: {total_samples}")
print(f"Chains running: {n_running}")

if total_samples < 1000:
    print("\n💡 TIP: Chains need ~1000+ samples for stable estimates")
    print("   Target: 2000-5000 samples per chain for publication")
elif total_samples < 2000:
    print("\n💡 TIP: Chains approaching convergence")
    print("   Check Rminus1 < 0.01 for convergence")
else:
    print("\n✅ Chains have sufficient samples for analysis")
    print("   Next: Extract best-fit and generate ACT residual plot")

print(f"\n{'='*110}")
