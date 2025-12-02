#!/bin/bash
# Launch Tier 6 ACT chains (SH0ES World + ACT)
# PRODUCTION SCRIPT - DO NOT MODIFY

set -e

PHASE3_DIR=~/Ridder-Field/phase3
CONFIG_DIR=${PHASE3_DIR}/configs
CHAIN_DIR=${PHASE3_DIR}/chains
LOG_DIR=${PHASE3_DIR}/logs

echo "=========================================="
echo "TIER 6 ACT ANALYSIS: SH0ES World + ACT"
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
if [ ! -f "${CONFIG_DIR}/tier6_lcdm_shoes_act.yaml" ] || [ ! -f "${CONFIG_DIR}/tier6_ede_shoes_act.yaml" ]; then
    echo "ERROR: Tier 6 configs not found!"
    echo "  Need: tier6_lcdm_shoes_act.yaml and tier6_ede_shoes_act.yaml"
    exit 1
fi

# Kill any existing Tier 6 chains
echo "Stopping any existing Tier 6 chains..."
pkill -9 -f 'cobaya.*tier6.*act' 2>/dev/null || true
sleep 2

# Clean old chains if requested
if [ "$CLEAN_START" = true ]; then
    echo "Cleaning old chain files..."
    rm -f ${CHAIN_DIR}/tier6_lcdm_shoes_act*.txt ${CHAIN_DIR}/tier6_lcdm_shoes_act*.progress 2>/dev/null || true
    rm -f ${CHAIN_DIR}/tier6_ede_shoes_act*.txt ${CHAIN_DIR}/tier6_ede_shoes_act*.progress 2>/dev/null || true
    rm -f ${CHAIN_DIR}/tier6_lcdm_shoes_act*.input.yaml ${CHAIN_DIR}/tier6_lcdm_shoes_act*.updated.yaml 2>/dev/null || true
    rm -f ${CHAIN_DIR}/tier6_ede_shoes_act*.input.yaml ${CHAIN_DIR}/tier6_ede_shoes_act*.updated.yaml 2>/dev/null || true
    echo "  ✓ Old chains removed"
fi

# Create log directory
mkdir -p ${LOG_DIR}

echo ""
echo "Starting MCMC chains..."
echo "  ΛCDM: SH0ES World + ACT"
echo "  EDE:  SH0ES World + ACT (Lambda prior [0.8, 1.2])"
echo ""

# Start LCDM chains (4 chains)
echo "Starting ΛCDM chains..."
for c in 1 2 3 4; do
    nohup cobaya-run ${CONFIG_DIR}/tier6_lcdm_shoes_act.yaml \
        -o ${CHAIN_DIR}/tier6_lcdm_shoes_act_c${c} \
        > ${LOG_DIR}/tier6_lcdm_shoes_act_c${c}.log 2>&1 &
    echo "  Started LCDM chain ${c} (PID: $!)"
done

# Small delay to avoid filesystem contention
sleep 2

# Start EDE chains (4 chains)
echo "Starting EDE chains..."
for c in 1 2 3 4; do
    nohup cobaya-run ${CONFIG_DIR}/tier6_ede_shoes_act.yaml \
        -o ${CHAIN_DIR}/tier6_ede_shoes_act_c${c} \
        > ${LOG_DIR}/tier6_ede_shoes_act_c${c}.log 2>&1 &
    echo "  Started EDE chain ${c} (PID: $!)"
done

sleep 3

# Verify chains started
n_procs=$(ps aux | grep -c '[c]obaya.*tier6.*act' || echo 0)
echo ""
echo "=========================================="
echo "Status: ${n_procs}/8 chains running"
echo "=========================================="
echo ""

if [ "$n_procs" -lt 8 ]; then
    echo "WARNING: Not all chains started. Check logs:"
    echo "  ls ${LOG_DIR}/tier6_*_shoes_act*.log"
    echo ""
fi

echo "Monitor with:"
echo "  bash ${PHASE3_DIR}/check_chains.sh"
echo ""
echo "Once converged (R-1 < 0.05), run template fit:"
echo "  python3 ${PHASE3_DIR}/act_template_fit.py"
echo ""
echo "Key points:"
echo "  - ΛCDM chains should converge in ~2-4 hours"
echo "  - EDE chains should converge in ~4-8 hours"
echo "  - EDE Lambda should stay in [0.8, 1.2] → z_osc ~ 4000-5000"
echo ""
