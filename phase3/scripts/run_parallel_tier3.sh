#!/usr/bin/env bash
set -euo pipefail

# Launch 4 parallel Tier 3 chains (Planck + BAO + SH0ES)
# Each chain runs in isolated working directory to avoid file locking

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="${ROOT_DIR}/configs/ridder_tier3_full.yaml"

echo "======================================================================"
echo "LAUNCHING TIER 3: PLANCK + BAO + SH0ES (4 parallel chains)"
echo "======================================================================"
echo ""
echo "This will test if SH0ES H0 tension pulls theta_i back up from 0.5"
echo ""

# Kill any existing Cobaya processes
pkill -f cobaya-run || true
sleep 2

# Clean up old chain directories
for i in {1..4}; do
    rm -rf "${ROOT_DIR}/tier3_chain${i}_work"
done

# Launch 4 independent chains
for i in {1..4}; do
    CHAIN_WORK_DIR="${ROOT_DIR}/tier3_chain${i}_work"
    mkdir -p "${CHAIN_WORK_DIR}/chains"
    
    # Copy config to isolated directory
    cp "${CONFIG_FILE}" "${CHAIN_WORK_DIR}/ridder_tier3_full.yaml"
    
    echo "Starting Chain ${i} in ${CHAIN_WORK_DIR}..."
    
    # Launch in background with nohup
    cd "${CHAIN_WORK_DIR}"
    nohup cobaya-run ridder_tier3_full.yaml --force > "tier3_chain${i}.log" 2>&1 &
    
    echo "  PID: $!"
    sleep 2
done

cd "${ROOT_DIR}"

echo ""
echo "======================================================================"
echo "All 4 Tier 3 chains launched!"
echo "Monitor with: bash scripts/tier3_status.sh"
echo "======================================================================"

