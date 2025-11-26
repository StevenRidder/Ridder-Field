#!/bin/bash
# V3 Tier 3 Quick Test: 4 chains, 200 samples each
# Planck FULL + BAO + SH0ES

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PHASE3_DIR="$SCRIPT_DIR/.."
CHAINS_DIR="$PHASE3_DIR/chains"

echo "=========================================="
echo "V3 TIER 3 QUICK TEST - 4 CHAINS"
echo "=========================================="
echo "Data: Planck FULL + BAO + SH0ES"
echo "Target: 200 samples per chain"
echo "Total chains: 4"
echo "=========================================="

# Clean previous test runs
echo "Cleaning previous Tier 3 test chains..."
rm -rf $CHAINS_DIR/v3_tier3_test_chain*_work
rm -f $CHAINS_DIR/v3_tier3_test_chain*.txt
rm -f $CHAINS_DIR/v3_tier3_test_chain*.updated.yaml

# Launch 4 chains (each in isolated directory)
echo ""
echo "Launching 4 chains..."
for i in {1..4}; do
    WORK_DIR="$CHAINS_DIR/v3_tier3_test_chain${i}_work"
    mkdir -p $WORK_DIR
    cp $PHASE3_DIR/ridder_v3_tier3_test.yaml $WORK_DIR/config.yaml
    
    # Modify output path for each chain
    sed -i "s|output: chains/v3_tier3_test|output: $CHAINS_DIR/v3_tier3_test_chain${i}|g" $WORK_DIR/config.yaml
    
    cd $WORK_DIR
    nohup cobaya-run config.yaml --force > chain${i}.log 2>&1 &
    PID=$!
    echo "  Chain ${i}: PID ${PID} in ${WORK_DIR}"
    cd - > /dev/null
    sleep 2  # Stagger launches slightly
done

echo ""
echo "=========================================="
echo "All 4 chains launched!"
echo "=========================================="
echo ""
echo "Monitor progress with:"
echo "  python3 $SCRIPT_DIR/check_v3_tier3_status.py"
echo ""

