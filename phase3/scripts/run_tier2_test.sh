#!/bin/bash
# Tier 2 Test Run: 2 Ridder chains + 1 ΛCDM baseline
# 200 samples each for quick validation
# Run on US East VM (4 vCPU)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_DIR="$SCRIPT_DIR/../configs"
CHAINS_DIR="$SCRIPT_DIR/../chains"

echo "=========================================="
echo "TIER 2 TEST RUN - PLANCK + BAO"
echo "=========================================="
echo "Target: 200 samples per chain (quick test)"
echo "Ridder chains: 2"
echo "ΛCDM baseline: 1"
echo "Total chains: 3"
echo "Estimated runtime: 2-3 hours"
echo "=========================================="

# Clean previous test runs
echo "Cleaning previous test chains..."
rm -rf $CHAINS_DIR/ridder_tier2_test_chain*_work
rm -rf $CHAINS_DIR/lcdm_tier2_test_chain*_work
rm -f $CHAINS_DIR/ridder_tier2_test*.txt
rm -f $CHAINS_DIR/ridder_tier2_test*.updated.yaml
rm -f $CHAINS_DIR/lcdm_tier2_test*.txt
rm -f $CHAINS_DIR/lcdm_tier2_test*.updated.yaml

# Disable file locking (we're using isolated directories)
export COBAYA_USE_FILE_LOCKING=False

# Launch 2 Ridder chains
echo ""
echo "Launching 2 Ridder field chains..."
for i in {1..2}; do
    WORK_DIR="$CHAINS_DIR/ridder_tier2_test_chain${i}_work"
    mkdir -p $WORK_DIR
    cp $CONFIG_DIR/ridder_tier2_planck_bao.yaml $WORK_DIR/config.yaml
    
    # Modify output path to include chain number
    sed -i "s|output: chains/ridder_tier2_test|output: ridder_tier2_test_chain${i}|g" $WORK_DIR/config.yaml
    
    cd $WORK_DIR
    nohup cobaya-run config.yaml --force > ridder_chain${i}.log 2>&1 &
    PID=$!
    echo "  Chain ${i}: PID ${PID} in ${WORK_DIR}"
    cd - > /dev/null
done

# Launch 1 ΛCDM baseline chain
echo ""
echo "Launching 1 ΛCDM baseline chain..."
WORK_DIR="$CHAINS_DIR/lcdm_tier2_test_chain1_work"
mkdir -p $WORK_DIR
cp $CONFIG_DIR/lcdm_tier2_planck_bao.yaml $WORK_DIR/config.yaml

sed -i "s|output: chains/lcdm_tier2_test|output: lcdm_tier2_test_chain1|g" $WORK_DIR/config.yaml

cd $WORK_DIR
nohup cobaya-run config.yaml --force > lcdm_chain1.log 2>&1 &
PID=$!
echo "  ΛCDM Chain 1: PID ${PID} in ${WORK_DIR}"
cd - > /dev/null

echo ""
echo "=========================================="
echo "All 3 chains launched successfully!"
echo "=========================================="
echo ""
echo "Monitor progress with:"
echo "  ./tier2_test_status.sh"
echo ""
echo "Check individual logs:"
echo "  tail -f $CHAINS_DIR/ridder_tier2_test_chain1_work/ridder_chain1.log"
echo "  tail -f $CHAINS_DIR/lcdm_tier2_test_chain1_work/lcdm_chain1.log"
echo ""
echo "Estimated completion: $(date -d '+3 hours' 2>/dev/null || date -v+3H 2>/dev/null || echo 'in ~3 hours')"
echo "=========================================="

