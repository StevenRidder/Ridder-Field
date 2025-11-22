#!/usr/bin/env bash
set -euo pipefail

# Launch 4 parallel MCMC chains using MPI
# This ensures 4 separate walkers for proper R-1 convergence

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${ROOT_DIR}/configs/ridder_tier1_planck.yaml"
NUM_CHAINS=4

cd "${ROOT_DIR}"

echo "=============================================================="
echo "TIER 1 PLANCK: 4 PARALLEL CHAINS (MPI)"
echo "  Config: ${CONFIG}"
echo "  Chains: ${NUM_CHAINS}"
echo "  Starting point: theta_i_ridder = 2.1 (Ridder valley)"
echo "  Max samples: 10000 per chain"
echo "=============================================================="

# Check if MPI is available
if ! command -v mpirun &> /dev/null; then
    echo "ERROR: mpirun not found. Installing openmpi..."
    sudo apt-get update && sudo apt-get install -y openmpi-bin libopenmpi-dev
fi

# Create output directory
mkdir -p chains output

# Set thread count (1 thread per chain to avoid oversubscription)
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

# Launch with MPI
echo ""
echo "Launching ${NUM_CHAINS} chains with MPI..."
echo "This will create:"
echo "  chains/ridder_tier1_planck.1.txt"
echo "  chains/ridder_tier1_planck.2.txt"
echo "  chains/ridder_tier1_planck.3.txt"
echo "  chains/ridder_tier1_planck.4.txt"
echo ""

nohup mpirun -np ${NUM_CHAINS} \
    python3 -m cobaya.run "${CONFIG}" \
    --force \
    > output/mpi_4chains.log 2>&1 &

MPI_PID=$!
echo ${MPI_PID} > output/mpi_4chains.pid

echo "=============================================================="
echo "MPI job launched (PID: ${MPI_PID})"
echo ""
echo "Monitor with:"
echo "  tail -f output/mpi_4chains.log"
echo "  ls -lh chains/ridder_tier1_planck.*"
echo ""
echo "Check processes:"
echo "  ps aux | grep cobaya"
echo ""
echo "Stop all chains:"
echo "  pkill -f 'cobaya.*ridder_tier1'"
echo "=============================================================="

