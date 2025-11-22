#!/usr/bin/env bash
set -euo pipefail

# Status checker for Tier 1 Planck MCMC run
# Usage: ./scripts/check_status.sh [config_name] [run_label]

CONFIG_NAME="${1:-ridder_tier1_planck}"
RUN_LABEL="${2:-tier1_planck}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHAIN_DIR="${ROOT_DIR}/chains"
OUTPUT_DIR="${ROOT_DIR}/output/${RUN_LABEL}"
LOG_FILE="${OUTPUT_DIR}/log.txt"
CHAIN_ROOT="${CHAIN_DIR}/${CONFIG_NAME}"

echo "=============================================================="
echo "MCMC STATUS CHECK: ${CONFIG_NAME}"
echo "=============================================================="
echo ""

# 1. Check if process is running
echo "--- PROCESS STATUS ---"
if pgrep -f "cobaya.*${CONFIG_NAME}" > /dev/null; then
    PID=$(pgrep -f "cobaya.*${CONFIG_NAME}" | head -1)
    echo "✓ MCMC process running (PID: ${PID})"
    ps -p ${PID} -o pid,etime,pcpu,pmem,cmd --no-headers | awk '{printf "  Runtime: %s | CPU: %s%% | Mem: %s%%\n", $2, $3, $4}'
else
    echo "✗ No MCMC process found"
fi
echo ""

# 2. Check chain files
echo "--- CHAIN PROGRESS ---"
if [ -f "${CHAIN_ROOT}.1.txt" ]; then
    # Count samples (skip header and empty lines)
    SAMPLE_COUNT=$(tail -n +2 "${CHAIN_ROOT}.1.txt" | grep -v '^$' | wc -l | tr -d ' ')
    FILE_SIZE=$(du -h "${CHAIN_ROOT}.1.txt" | cut -f1)
    LAST_MODIFIED=$(stat -c %y "${CHAIN_ROOT}.1.txt" 2>/dev/null || stat -f "%Sm" "${CHAIN_ROOT}.1.txt" 2>/dev/null || echo "unknown")
    
    echo "✓ Chain file found: ${CHAIN_ROOT}.1.txt"
    echo "  Samples: ${SAMPLE_COUNT}"
    echo "  Size: ${FILE_SIZE}"
    echo "  Last modified: ${LAST_MODIFIED}"
    
    # Get max_samples from config if possible
    if [ -f "${ROOT_DIR}/configs/${CONFIG_NAME}.yaml" ]; then
        MAX_SAMPLES=$(grep -E "max_samples:" "${ROOT_DIR}/configs/${CONFIG_NAME}.yaml" | head -1 | awk '{print $2}' | tr -d '[:space:]')
        if [ -n "${MAX_SAMPLES}" ] && [ "${MAX_SAMPLES}" != "null" ]; then
            PERCENT=$(awk "BEGIN {printf \"%.1f\", (${SAMPLE_COUNT}/${MAX_SAMPLES})*100}")
            echo "  Progress: ${SAMPLE_COUNT}/${MAX_SAMPLES} (${PERCENT}%)"
        fi
    fi
    
    # Show last few samples
    echo ""
    echo "  Last 3 samples (theta_i | beta | H0):"
    tail -n 3 "${CHAIN_ROOT}.1.txt" | awk '{printf "    Sample %d: %.4f | %.5f | %.2f\n", NR, $9, $10, $5}' 2>/dev/null || echo "    (Columns may vary, check file manually)"
else
    echo "⚠ Chain file not yet created: ${CHAIN_ROOT}.1.txt"
    echo "  (This is normal during initialization - Cobaya creates it after first accepted sample)"
    
    # Check for progress/checkpoint files
    if [ -f "${CHAIN_ROOT}.progress" ]; then
        echo "  ✓ Progress file found (initialization in progress)"
        PROGRESS=$(cat "${CHAIN_ROOT}.progress" 2>/dev/null | head -1 || echo "unknown")
        echo "    Status: ${PROGRESS}"
    fi
    if [ -f "${CHAIN_ROOT}.checkpoint" ]; then
        echo "  ✓ Checkpoint file found"
    fi
fi
echo ""

# 3. Check log file
echo "--- RECENT LOG OUTPUT ---"
if [ -f "${LOG_FILE}" ]; then
    LOG_SIZE=$(du -h "${LOG_FILE}" | cut -f1)
    echo "✓ Log file: ${LOG_FILE} (${LOG_SIZE})"
    echo ""
    echo "Last 20 lines:"
    echo "----------------------------------------"
    tail -n 20 "${LOG_FILE}" 2>/dev/null || echo "  (log file empty or unreadable)"
    echo "----------------------------------------"
else
    echo "✗ Log file not found: ${LOG_FILE}"
fi
echo ""

# 4. Extract key statistics from log
echo "--- KEY STATISTICS ---"
if [ -f "${LOG_FILE}" ]; then
    # Acceptance rate
    ACCEPT_RATE=$(grep -i "acceptance" "${LOG_FILE}" | tail -1 | grep -oE "[0-9]+\.[0-9]+" | head -1 || echo "N/A")
    if [ "${ACCEPT_RATE}" != "N/A" ]; then
        echo "  Acceptance rate: ${ACCEPT_RATE}"
    fi
    
    # R-1 (Gelman-Rubin)
    R_MINUS_1=$(grep -i "R-1\|Rminus1\|gelman" "${LOG_FILE}" | tail -1 | grep -oE "[0-9]+\.[0-9]+" | head -1 || echo "N/A")
    if [ "${R_MINUS_1}" != "N/A" ]; then
        echo "  R-1: ${R_MINUS_1}"
    fi
    
    # Errors
    ERROR_COUNT=$(grep -i "error\|exception\|failed" "${LOG_FILE}" | wc -l | tr -d ' ')
    if [ "${ERROR_COUNT}" -gt 0 ]; then
        echo "  ⚠ Errors found: ${ERROR_COUNT}"
        echo "    Recent errors:"
        grep -i "error\|exception\|failed" "${LOG_FILE}" | tail -3 | sed 's/^/      /'
    else
        echo "  ✓ No errors detected"
    fi
else
    echo "  (No log file to analyze)"
fi
echo ""

# 5. Check for updated config (learned proposal)
if [ -f "${CHAIN_ROOT}.updated.yaml" ]; then
    echo "--- LEARNED PROPOSAL ---"
    echo "✓ Proposal covariance learned and saved"
    echo "  File: ${CHAIN_ROOT}.updated.yaml"
    echo ""
fi

# 6. Check for 4-chain parallel run status
echo "--- 4-CHAIN PARALLEL STATUS ---"
if [ -d "${ROOT_DIR}/chain1_work" ]; then
    python3 << "PYEOF"
import glob
import os
import numpy as np

work_dirs = sorted(glob.glob("${ROOT_DIR}/chain*_work"))
all_chain_files = []
for wd in work_dirs:
    cf = glob.glob(f"{wd}/chains/ridder_tier1_planck*.txt")
    all_chain_files.extend(cf)

if all_chain_files:
    print(f"Found {len(all_chain_files)} active chains.")
    print("-" * 40)
    
    total_samples = 0
    all_theta = []
    all_beta = []
    all_H0 = []
    all_chi2 = []
    
    for cf in sorted(all_chain_files):
        try:
            data = np.loadtxt(cf, skiprows=1)
            if data.ndim == 1: data = data.reshape(1, -1)
            n_samples = len(data)
            total_samples += n_samples
            
            # Cols: 8=theta, 9=beta, 4=H0, -5=chi2
            all_theta.extend(data[:, 8].tolist())
            all_beta.extend(data[:, 9].tolist())
            all_H0.extend(data[:, 4].tolist())
            all_chi2.extend(data[:, -5].tolist())
            
            # Get chain ID
            chain_id = os.path.basename(os.path.dirname(os.path.dirname(cf))).replace("chain", "").replace("_work", "")
            print(f"Chain {chain_id}: {n_samples} samples | theta={data[-1, 8]:.4f} | beta={data[-1, 9]:.5f} | chi2={data[-1, -5]:.1f}")
        except:
            pass
    
    print("-" * 40)
    if all_theta:
        print(f"TOTAL SAMPLES: {total_samples}")
        print(f"THETA_I: {np.mean(all_theta):.4f} ± {np.std(all_theta):.4f}  (Range: {np.min(all_theta):.4f}-{np.max(all_theta):.4f})")
        
        # Interpretation of Theta
        mean_theta = np.mean(all_theta)
        if mean_theta > 1.8: print("  ✅ STATUS: In Ridder Valley")
        elif mean_theta < 1.0: print("  ⚠️  STATUS: Drifted to ΛCDM")
        else: print("  ⚠️  STATUS: Transition/Sweet Spot (1.0-1.8)")
            
        print(f"BETA:    {np.mean(all_beta):.5f} ± {np.std(all_beta):.5f}  (Range: {np.min(all_beta):.5f}-{np.max(all_beta):.5f})")
        
        # Interpretation of Beta
        mean_beta = np.mean(all_beta)
        if mean_beta > 0.005: print("  ✅ STATUS: Strong Coupling Detected (>0.005)")
        elif mean_beta > 0.001: print("  ⚠️  STATUS: Weak Coupling")
        else: print("  ❌ STATUS: No Coupling")
            
        print(f"H0:      {np.mean(all_H0):.2f} ± {np.std(all_H0):.2f}")
        print(f"BEST CHI2: {np.min(all_chi2):.2f}")
else:
    print("No parallel chain files found yet.")
PYEOF
else
    echo "No parallel work directories found."
fi
echo ""

# 7. Summary
echo "=============================================================="
echo "QUICK COMMANDS:"
echo "  Watch log:     tail -f ${LOG_FILE}"
echo "  Check chains:  ls -lh ${CHAIN_DIR}/${CONFIG_NAME}.*"
echo "  Kill process:  pkill -f 'cobaya.*${CONFIG_NAME}'"
echo "=============================================================="

