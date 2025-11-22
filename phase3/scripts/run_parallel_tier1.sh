#!/usr/bin/env bash
set -euo pipefail

# Run 4 parallel Tier 1 Planck chains on single VM
# Each chain uses 1 CPU core, so 4 chains = 4 cores

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${ROOT_DIR}/configs/ridder_tier1_planck.yaml"
NUM_CHAINS=4

echo "=============================================================="
echo "TIER 1 PLANCK: PARALLEL CHAINS"
echo "  Config: ${CONFIG}"
echo "  Chains: ${NUM_CHAINS}"
echo "  Max samples: 10000 per chain"
echo "=============================================================="

cd "${ROOT_DIR}"

# Create output directories
mkdir -p chains output

# Function to run a single chain
# COMPLETE ISOLATION: Each chain gets its own working directory
run_chain() {
    local CHAIN_ID=$1
    local CHAIN_WORK_DIR="${ROOT_DIR}/chain${CHAIN_ID}_work"
    local CHAIN_OUTPUT="${CHAIN_WORK_DIR}/chains/ridder_tier1_planck"
    local LOG_FILE="${CHAIN_WORK_DIR}/chain${CHAIN_ID}.log"
    
    # Create completely isolated working directory
    mkdir -p "${CHAIN_WORK_DIR}/chains"
    mkdir -p "${CHAIN_WORK_DIR}/output"
    
    # Copy config to chain's work directory (avoids any shared file issues)
    cp "${CONFIG}" "${CHAIN_WORK_DIR}/config.yaml"
    
    echo "[$(date +%H:%M:%S)] Starting chain ${CHAIN_ID} in isolated directory..."
    
    # Create PID directory
    mkdir -p "${ROOT_DIR}/output/tier1_planck_chain${CHAIN_ID}"
    
    # Run in the isolated directory with all environment set - use nohup for proper detachment
    (
        cd "${CHAIN_WORK_DIR}"
        export OMP_NUM_THREADS=1
        export MKL_NUM_THREADS=1
        export OPENBLAS_NUM_THREADS=1
        export COBAYA_USE_FILE_LOCKING=False
        
        # Run Cobaya in the isolated directory with nohup
        nohup python3 -m cobaya.run config.yaml \
            --output "${CHAIN_OUTPUT}" \
            --force \
            > "${LOG_FILE}" 2>&1
    ) &
    
    local PID=$!
    echo ${PID} > "${ROOT_DIR}/output/tier1_planck_chain${CHAIN_ID}/pid.txt"
    echo "[$(date +%H:%M:%S)] Chain ${CHAIN_ID} started (PID: ${PID}) in ${CHAIN_WORK_DIR}"
}

# Launch all chains
echo ""
echo "Launching ${NUM_CHAINS} chains in parallel..."
for i in $(seq 1 ${NUM_CHAINS}); do
    run_chain $i
    sleep 1  # Small stagger to avoid race conditions
done

# Wait a moment for all processes to start
sleep 3

echo ""
echo "=============================================================="
echo "All ${NUM_CHAINS} chains launched in isolated directories!"
echo ""
echo "Chain directories:"
for i in $(seq 1 ${NUM_CHAINS}); do
    echo "  Chain $i: chain${i}_work/"
done
echo ""
echo "Monitor chains:"
echo "  tail -f chain1_work/chain1.log"
echo "  tail -f chain2_work/chain2.log"
echo "  etc."
echo ""
echo "Check processes:"
echo "  ps aux | grep cobaya"
echo ""
echo "Chain files will be in:"
echo "  chain1_work/chains/ridder_tier1_planck.1.txt"
echo "  chain2_work/chains/ridder_tier1_planck.1.txt"
echo "  etc."
echo ""
echo "Stop all chains:"
echo "  pkill -f 'cobaya.*ridder_tier1'"
echo "=============================================================="

