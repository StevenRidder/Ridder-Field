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
# Each chain needs a UNIQUE output path to avoid file locking conflicts
run_chain() {
    local CHAIN_ID=$1
    # Use unique output path - we'll rename later to .1, .2, .3, .4 format
    local CHAIN_OUTPUT="chains/ridder_tier1_planck_chain${CHAIN_ID}"
    local LOG_DIR="output/tier1_planck_chain${CHAIN_ID}"
    
    mkdir -p "${LOG_DIR}"
    
    echo "[$(date +%H:%M:%S)] Starting chain ${CHAIN_ID}..."
    
    # Set thread count to 1 per chain (CLASS will use 1 thread)
    export OMP_NUM_THREADS=1
    export MKL_NUM_THREADS=1
    export OPENBLAS_NUM_THREADS=1
    
    # Disable file locking to allow parallel chains
    export COBAYA_USE_FILE_LOCKING=False
    
    # Run Cobaya with unique output path
    nohup python3 -m cobaya.run "${CONFIG}" \
        --output "${CHAIN_OUTPUT}" \
        --force \
        > "${LOG_DIR}/log.txt" 2>&1 &
    
    local PID=$!
    echo ${PID} > "${LOG_DIR}/pid.txt"
    echo "[$(date +%H:%M:%S)] Chain ${CHAIN_ID} started (PID: ${PID})"
}

# Launch all chains
echo ""
echo "Launching ${NUM_CHAINS} chains in parallel..."
for i in $(seq 1 ${NUM_CHAINS}); do
    run_chain $i
    sleep 2  # Stagger starts slightly
done

echo ""
echo "=============================================================="
echo "All ${NUM_CHAINS} chains launched!"
echo ""
echo "Monitor with:"
echo "  ./scripts/check_status.sh ridder_tier1_planck tier1_planck_chain1"
echo ""
echo "Check all chains:"
echo "  ps aux | grep cobaya"
echo ""
echo "Stop all chains:"
echo "  pkill -f 'cobaya.*ridder_tier1_planck'"
echo "=============================================================="

