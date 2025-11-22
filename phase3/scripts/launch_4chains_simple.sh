#!/usr/bin/env bash
set -euo pipefail

# Launch 4 parallel MCMC chains (simple approach, no MPI)
# Each chain runs as a separate process

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${ROOT_DIR}/configs/ridder_tier1_planck.yaml"

cd "${ROOT_DIR}"

echo "=============================================================="
echo "TIER 1 PLANCK: 4 PARALLEL CHAINS"
echo "  Config: ${CONFIG}"
echo "  Starting point: theta_i_ridder = 2.1 (Ridder valley)"
echo "  Max samples: 10000 per chain"
echo "=============================================================="

mkdir -p chains output

# Set thread count (1 thread per chain)
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

# Launch 4 chains - Cobaya will automatically number them .1, .2, .3, .4
echo ""
echo "Launching 4 chains..."
echo "This will create:"
echo "  chains/ridder_tier1_planck.1.txt"
echo "  chains/ridder_tier1_planck.2.txt"
echo "  chains/ridder_tier1_planck.3.txt"
echo "  chains/ridder_tier1_planck.4.txt"
echo ""

# Use Cobaya's built-in parallel chain support
nohup python3 -m cobaya.run "${CONFIG}" \
    --force \
    > output/4chains.log 2>&1 &

CHAIN_PID=$!
echo ${CHAIN_PID} > output/4chains.pid

echo "=============================================================="
echo "Chains launched (PID: ${CHAIN_PID})"
echo ""
echo "Monitor with:"
echo "  tail -f output/4chains.log"
echo "  ls -lh chains/ridder_tier1_planck.*"
echo ""
echo "Check processes:"
echo "  ps aux | grep cobaya"
echo ""
echo "Stop all chains:"
echo "  pkill -f 'cobaya.*ridder_tier1'"
echo "=============================================================="

