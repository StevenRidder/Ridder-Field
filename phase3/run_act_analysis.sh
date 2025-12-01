#!/bin/bash
# Master script to run ACT analysis chains
# PRODUCTION CONFIG - Runs both ΛCDM and EDE with tight Lambda prior
#
# Usage: bash run_act_analysis.sh [--clean]
#   --clean: Remove old chains before starting (default: resume)

set -e

PHASE3_DIR=~/Ridder-Field/phase3
CONFIG_DIR=${PHASE3_DIR}/configs
CHAIN_DIR=${PHASE3_DIR}/chains
LOG_DIR=${PHASE3_DIR}/logs

echo "=========================================="
echo "ACT ANALYSIS: Production Chains"
echo "=========================================="
echo ""

# Parse arguments
CLEAN_START=false
for arg in "$@"; do
    case $arg in
        --clean)
            CLEAN_START=true
            shift
            ;;
    esac
done

# Check if configs exist
if [ ! -f "${CONFIG_DIR}/act_world_lcdm.yaml" ] || [ ! -f "${CONFIG_DIR}/act_world_ede.yaml" ]; then
    echo "ERROR: ACT world configs not found!"
    echo "  Need: act_world_lcdm.yaml and act_world_ede.yaml"
    exit 1
fi

# Kill any existing ACT chains
echo "Stopping any existing ACT chains..."
pkill -9 -f 'cobaya.*act_world' 2>/dev/null || true
sleep 2

# Clean old chains if requested
if [ "$CLEAN_START" = true ]; then
    echo "Cleaning old chain files..."
    rm -f ${CHAIN_DIR}/act_world_lcdm*.txt ${CHAIN_DIR}/act_world_lcdm*.progress 2>/dev/null || true
    rm -f ${CHAIN_DIR}/act_world_ede*.txt ${CHAIN_DIR}/act_world_ede*.progress 2>/dev/null || true
    rm -f ${CHAIN_DIR}/act_world_lcdm*.input.yaml ${CHAIN_DIR}/act_world_lcdm*.updated.yaml 2>/dev/null || true
    rm -f ${CHAIN_DIR}/act_world_ede*.input.yaml ${CHAIN_DIR}/act_world_ede*.updated.yaml 2>/dev/null || true
    echo "  ✓ Old chains removed"
fi

# Create log directory
mkdir -p ${LOG_DIR}

echo ""
echo "Starting MCMC chains..."
echo "  ΛCDM: Using CLASS with l_max=8500"
echo "  EDE:  Using CLASS with Lambda prior [0.8, 1.2]"
echo ""

# Start LCDM chains (4 chains)
echo "Starting ΛCDM chains..."
for c in 1 2 3 4; do
    nohup cobaya-run ${CONFIG_DIR}/act_world_lcdm.yaml \
        -o ${CHAIN_DIR}/act_world_lcdm_c${c} \
        > ${LOG_DIR}/act_world_lcdm_c${c}.log 2>&1 &
    echo "  Started LCDM chain ${c} (PID: $!)"
done

# Small delay to avoid filesystem contention
sleep 2

# Start EDE chains (4 chains)
echo "Starting EDE chains..."
for c in 1 2 3 4; do
    nohup cobaya-run ${CONFIG_DIR}/act_world_ede.yaml \
        -o ${CHAIN_DIR}/act_world_ede_c${c} \
        > ${LOG_DIR}/act_world_ede_c${c}.log 2>&1 &
    echo "  Started EDE chain ${c} (PID: $!)"
done

sleep 3

# Verify chains started
n_procs=$(ps aux | grep -c '[c]obaya.*act_world' || echo 0)
echo ""
echo "=========================================="
echo "Status: ${n_procs}/8 chains running"
echo "=========================================="
echo ""

if [ "$n_procs" -lt 8 ]; then
    echo "WARNING: Not all chains started. Check logs:"
    echo "  ls ${LOG_DIR}/act_world*.log"
    echo ""
fi

echo "Monitor with:"
echo "  bash ${PHASE3_DIR}/check_chains.sh"
echo ""
echo "Once converged (R-1 < 0.02), run template fit:"
echo "  python3 ${PHASE3_DIR}/act_template_fit.py"
echo ""
echo "Key points:"
echo "  - ΛCDM chains should converge in ~2-4 hours"
echo "  - EDE chains should converge in ~4-8 hours"
echo "  - EDE Lambda should stay in [0.8, 1.2] → z_osc ~ 4000-5000"
echo ""
