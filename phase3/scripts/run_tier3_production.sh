#!/bin/bash
# Tier 3 Production Run: 4 Ridder chains + 2 ΛCDM baseline chains
# Planck FULL + BAO + SH0ES, 5000 samples each
# Run on US East VM (4 vCPU)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_DIR="$SCRIPT_DIR/../configs"
CHAINS_DIR="$SCRIPT_DIR/../chains"

echo "=========================================="
echo "TIER 3 PRODUCTION RUN - PLANCK + BAO + SH0ES"
echo "=========================================="
echo "Target: 5000 samples per chain"
echo "Ridder chains: 4"
echo "ΛCDM baseline: 2"
echo "Total chains: 6"
echo "Estimated runtime: 24-36 hours"
echo "=========================================="

# Clean previous production runs
echo "Cleaning previous production chains..."
rm -rf $CHAINS_DIR/ridder_tier3_prod_chain*_work
rm -rf $CHAINS_DIR/lcdm_tier3_prod_chain*_work
rm -f $CHAINS_DIR/ridder_tier3_prod_chain*.txt
rm -f $CHAINS_DIR/ridder_tier3_prod_chain*.updated.yaml
rm -f $CHAINS_DIR/lcdm_tier3_prod_chain*.txt
rm -f $CHAINS_DIR/lcdm_tier3_prod_chain*.updated.yaml

# Disable file locking (we're using isolated directories)
export COBAYA_USE_FILE_LOCKING=False

# Launch 4 Ridder chains (each in isolated directory)
echo ""
echo "Launching 4 Ridder field chains..."
for i in {1..4}; do
    WORK_DIR="$CHAINS_DIR/ridder_tier3_prod_chain${i}_work"
    mkdir -p $WORK_DIR
    cp $CONFIG_DIR/ridder_tier3_production.yaml $WORK_DIR/config.yaml
    
    # Modify output path to write directly to chains dir
    sed -i "s|output: ridder_tier3_prod_chain|output: $CHAINS_DIR/ridder_tier3_prod_chain${i}|g" $WORK_DIR/config.yaml
    
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
    WORK_DIR="$CHAINS_DIR/lcdm_tier3_prod_chain${i}_work"
    mkdir -p $WORK_DIR
    cp $CONFIG_DIR/lcdm_tier3_production.yaml $WORK_DIR/config.yaml
    
    # Modify output path to write directly to chains dir
    sed -i "s|output: lcdm_tier3_prod_chain|output: $CHAINS_DIR/lcdm_tier3_prod_chain${i}|g" $WORK_DIR/config.yaml
    
    cd $WORK_DIR
    nohup cobaya-run config.yaml --force > lcdm_chain${i}.log 2>&1 &
    PID=$!
    echo "  ΛCDM Chain ${i}: PID ${PID} in ${WORK_DIR}"
    cd - > /dev/null
done

echo ""
echo "=========================================="
echo "All 6 chains launched successfully!"
echo "=========================================="
echo ""
echo "Monitor progress with:"
echo "  ./tier3_production_status.sh"
echo ""
echo "Estimated completion: $(date -d '+36 hours' 2>/dev/null || date -v+36H)"
echo "=========================================="


