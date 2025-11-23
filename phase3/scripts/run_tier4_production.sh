#!/bin/bash
# Tier 4 Production Run: 4 Ridder chains
# Planck FULL + BAO + SH0ES + SN, 5000 samples each
# Run on Australia VM (8 vCPU)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_DIR="$SCRIPT_DIR/../configs"
CHAINS_DIR="$SCRIPT_DIR/../chains"

echo "=========================================="
echo "TIER 4 PRODUCTION RUN - THE GRAND SLAM"
echo "=========================================="
echo "Data: Planck + BAO + SH0ES + SN"
echo "Target: 5000 samples per chain"
echo "Ridder chains: 4"
echo "Total chains: 4"
echo "Estimated runtime: 36-48 hours"
echo "=========================================="

# Clean previous production runs
echo "Cleaning previous Tier 4 chains..."
rm -rf $CHAINS_DIR/ridder_tier4_prod_chain*_work
rm -f $CHAINS_DIR/ridder_tier4_prod_chain*.txt
rm -f $CHAINS_DIR/ridder_tier4_prod_chain*.updated.yaml

# Disable file locking (we're using isolated directories)
export COBAYA_USE_FILE_LOCKING=False
# Set packages path so Cobaya can find clipy
export COBAYA_PACKAGES_PATH="/home/ridderadmin/.local/share/cobaya"

# Launch 4 Ridder chains (each in isolated directory)
echo ""
echo "Launching 4 Ridder field chains..."
for i in {1..4}; do
    WORK_DIR="$CHAINS_DIR/ridder_tier4_prod_chain${i}_work"
    mkdir -p $WORK_DIR
    cp $CONFIG_DIR/ridder_tier4_full.yaml $WORK_DIR/config.yaml
    
    # Modify output path to write directly to chains dir
    sed -i "s|output: chains/ridder_tier4_grand_slam|output: $CHAINS_DIR/ridder_tier4_prod_chain${i}|g" $WORK_DIR/config.yaml
    
    cd $WORK_DIR
    nohup cobaya-run config.yaml --force > ridder_chain${i}.log 2>&1 &
    PID=$!
    echo "  Chain ${i}: PID ${PID} in ${WORK_DIR}"
    cd - > /dev/null
done

echo ""
echo "=========================================="
echo "All 4 chains launched successfully!"
echo "=========================================="
echo ""
echo "Monitor progress with:"
echo "  ./tier4_status.sh"
echo ""
echo "Estimated completion: $(date -d '+48 hours' 2>/dev/null || date -v+48H)"
echo "=========================================="


