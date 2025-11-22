#!/bin/bash
# Tier 1 Production Run: 8 Ridder chains + 2 ΛCDM baseline chains
# 5000 samples each for V1 publication
# Run on Australia VM (F8s_v2, 8 vCPU)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_DIR="$SCRIPT_DIR/../configs"
CHAINS_DIR="$SCRIPT_DIR/../chains"

echo "=========================================="
echo "TIER 1 PRODUCTION RUN - V1 PUBLICATION"
echo "=========================================="
echo "Target: 5000 samples per chain"
echo "Ridder chains: 8"
echo "ΛCDM baseline: 2"
echo "Total chains: 10"
echo "Estimated runtime: 24-36 hours"
echo "=========================================="

# Clean previous production runs
echo "Cleaning previous production chains..."
rm -f $CHAINS_DIR/ridder_tier1_production*.txt
rm -f $CHAINS_DIR/ridder_tier1_production*.updated.yaml
rm -f $CHAINS_DIR/lcdm_production*.txt
rm -f $CHAINS_DIR/lcdm_production*.updated.yaml

# Disable file locking (we're using isolated directories)
export COBAYA_USE_FILE_LOCKING=False

# Launch 8 Ridder chains (each in isolated directory)
echo ""
echo "Launching 8 Ridder field chains..."
for i in {1..8}; do
    WORK_DIR="$CHAINS_DIR/ridder_prod_chain${i}_work"
    mkdir -p $WORK_DIR
    cp $CONFIG_DIR/ridder_tier1_planck.yaml $WORK_DIR/config.yaml
    
    # Modify output path to include chain number
    sed -i "s|output: chains/ridder_tier1_production|output: ridder_tier1_production_chain${i}|g" $WORK_DIR/config.yaml
    
    cd $WORK_DIR
    nohup cobaya-run config.yaml --force > ridder_chain${i}.log 2>&1 &
    PID=$!
    echo "  Chain ${i}: PID ${PID} in ${WORK_DIR}"
    cd - > /dev/null
done

# Launch 2 ΛCDM baseline chains
echo ""
echo "Launching 2 ΛCDM baseline chains..."
for i in {1..2}; do
    WORK_DIR="$CHAINS_DIR/lcdm_prod_chain${i}_work"
    mkdir -p $WORK_DIR
    cp $CONFIG_DIR/lcdm_baseline.yaml $WORK_DIR/config.yaml
    
    # Modify output path to include chain number
    sed -i "s|output: chains/lcdm_production|output: lcdm_production_chain${i}|g" $WORK_DIR/config.yaml
    
    cd $WORK_DIR
    nohup cobaya-run config.yaml --force > lcdm_chain${i}.log 2>&1 &
    PID=$!
    echo "  ΛCDM Chain ${i}: PID ${PID} in ${WORK_DIR}"
    cd - > /dev/null
done

echo ""
echo "=========================================="
echo "All 10 chains launched successfully!"
echo "=========================================="
echo ""
echo "Monitor progress with:"
echo "  ./tier1_production_status.sh"
echo ""
echo "Check individual logs:"
echo "  tail -f $CHAINS_DIR/ridder_prod_chain1_work/ridder_chain1.log"
echo "  tail -f $CHAINS_DIR/lcdm_prod_chain1_work/lcdm_chain1.log"
echo ""
echo "Estimated completion: $(date -d '+36 hours' 2>/dev/null || date -v+36H)"
echo "=========================================="

