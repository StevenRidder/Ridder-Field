#!/usr/bin/env bash
set -euo pipefail

# Launch 4 parallel chains for Tier 3 (Planck + BAO + SH0ES)
# Each chain runs as a separate process in its own directory

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${ROOT_DIR}/configs/ridder_tier3_full.yaml"
NUM_CHAINS=4

echo "=============================================================="
echo "TIER 3: PLANCK + BAO + SH0ES"
echo "  Config: ${CONFIG}"
echo "  Chains: ${NUM_CHAINS}"
echo "  Start: theta_i=2.0, beta=0.01, H0=70"
echo "=============================================================="

cd "${ROOT_DIR}"

# Function to run a single chain
run_chain() {
    local CHAIN_ID=$1
    local CHAIN_WORK_DIR="${ROOT_DIR}/chain${CHAIN_ID}_tier3"
    local CHAIN_OUTPUT="${CHAIN_WORK_DIR}/chains/ridder_tier3"
    local LOG_FILE="${CHAIN_WORK_DIR}/chain${CHAIN_ID}.log"
    
    # Clean and create isolated directory
    rm -rf "${CHAIN_WORK_DIR}"
    mkdir -p "${CHAIN_WORK_DIR}/chains"
    mkdir -p "${CHAIN_WORK_DIR}/output"
    
    # Copy config
    cp "${CONFIG}" "${CHAIN_WORK_DIR}/config.yaml"
    
    echo "[$(date +%H:%M:%S)] Launching chain ${CHAIN_ID}..."
    
    (
        cd "${CHAIN_WORK_DIR}"
        export OMP_NUM_THREADS=1
        export MKL_NUM_THREADS=1
        export OPENBLAS_NUM_THREADS=1
        export COBAYA_USE_FILE_LOCKING=False
        
        nohup python3 -m cobaya.run config.yaml \
            --output "${CHAIN_OUTPUT}" \
            --force \
            > "${LOG_FILE}" 2>&1
    ) &
}

# Launch chains
echo ""
for i in $(seq 1 ${NUM_CHAINS}); do
    run_chain $i
    sleep 2
done

echo ""
echo "=============================================================="
echo "Chains launched. Monitor with:"
echo "  tail -f chain*_tier3/chain*.log"
echo "=============================================================="

