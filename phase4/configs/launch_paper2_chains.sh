#!/bin/bash
# Paper 2: Launch all MCMC chains for marginalized ACT analysis
# Run from: /home/azureuser/Ridder-Field/phase3

set -e

CONFIGS_DIR="configs/paper2"
CHAINS_DIR="chains/paper2"

# Create output directory
mkdir -p $CHAINS_DIR

echo "=========================================="
echo "Paper 2: Full Marginalized ACT Analysis"
echo "=========================================="
echo ""

# Check that configs exist
if [ ! -f "$CONFIGS_DIR/run_a_ede_marginalized.yaml" ]; then
    echo "ERROR: Config files not found in $CONFIGS_DIR"
    exit 1
fi

echo "Available runs:"
echo "  A: Geometric EDE with derived A_sh (full marginalization)"
echo "  B: ΛCDM + phenomenological A_sh template"
echo "  C: Control - Planck-only EDE (no ACT)"
echo ""

# Parse command line argument
RUN_TYPE=${1:-"all"}

case $RUN_TYPE in
    "a"|"A")
        echo "Starting Run A: Geometric EDE marginalized..."
        nohup cobaya-run $CONFIGS_DIR/run_a_ede_marginalized.yaml \
            -f run_a_ede_marginalized \
            > $CHAINS_DIR/run_a.log 2>&1 &
        echo "PID: $!"
        ;;
    "b"|"B")
        echo "Starting Run B: ΛCDM + template..."
        nohup cobaya-run $CONFIGS_DIR/run_b_lcdm_template.yaml \
            -f run_b_lcdm_template \
            > $CHAINS_DIR/run_b.log 2>&1 &
        echo "PID: $!"
        ;;
    "c"|"C"|"control")
        echo "Starting Control Run: Planck-only..."
        nohup cobaya-run $CONFIGS_DIR/run_control_planck_only.yaml \
            -f run_control_planck_only \
            > $CHAINS_DIR/run_control.log 2>&1 &
        echo "PID: $!"
        ;;
    "all")
        echo "Starting ALL runs in background..."
        echo ""
        
        # Run A
        echo "[1/3] Starting Run A: Geometric EDE marginalized..."
        nohup cobaya-run $CONFIGS_DIR/run_a_ede_marginalized.yaml \
            -f run_a_ede_marginalized \
            > $CHAINS_DIR/run_a.log 2>&1 &
        echo "  PID: $!"
        sleep 5
        
        # Run B
        echo "[2/3] Starting Run B: ΛCDM + template..."
        nohup cobaya-run $CONFIGS_DIR/run_b_lcdm_template.yaml \
            -f run_b_lcdm_template \
            > $CHAINS_DIR/run_b.log 2>&1 &
        echo "  PID: $!"
        sleep 5
        
        # Control
        echo "[3/3] Starting Control Run: Planck-only..."
        nohup cobaya-run $CONFIGS_DIR/run_control_planck_only.yaml \
            -f run_control_planck_only \
            > $CHAINS_DIR/run_control.log 2>&1 &
        echo "  PID: $!"
        ;;
    *)
        echo "Usage: $0 [a|b|c|control|all]"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Chains running in background"
echo "Monitor with: tail -f $CHAINS_DIR/run_*.log"
echo "Check status: python3 check_chains_status.py"
echo "=========================================="

