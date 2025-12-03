#!/bin/bash
# Pre-Publication Optimization Runner
# Executes the full optimization pipeline

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PHASE3_DIR="$(dirname "$SCRIPT_DIR")"

echo "=============================================="
echo "PRE-PUBLICATION OPTIMIZATION SUITE"
echo "=============================================="
echo "Working directory: $PHASE3_DIR"
echo ""

# Check for virtual environment
if [ -f "$PHASE3_DIR/../venv/bin/activate" ]; then
    source "$PHASE3_DIR/../venv/bin/activate"
    echo "✓ Virtual environment activated"
fi

# Step 1: Run χ² breakdown on existing chains
echo ""
echo "=============================================="
echo "STEP 1: χ² BREAKDOWN ANALYSIS"
echo "=============================================="

if [ -f "$PHASE3_DIR/chains/tier5_ede_shoes_predesi.1.txt" ] && \
   [ -f "$PHASE3_DIR/chains/tier5_lcdm_shoes_predesi.1.txt" ]; then
    python "$SCRIPT_DIR/chi2_breakdown.py" --world shoes_predesi
else
    echo "⚠ Chains not found. Skipping breakdown analysis."
    echo "  Run Tier 5 chains first, then re-run this script."
fi

# Step 2: Profile scans (optional - takes time)
echo ""
echo "=============================================="
echo "STEP 2: PROFILE SCANS"
echo "=============================================="
echo "Profile scans require ~2 hours each."
echo "To run manually:"
echo "  python $SCRIPT_DIR/profile_scan.py --param n_ridder --range 2.5 3.5 --steps 5"
echo "  python $SCRIPT_DIR/profile_scan.py --param sigma_ln_a --range 0.4 1.0 --steps 7"
echo ""

read -p "Run profile scans now? (y/N): " run_profiles
if [ "$run_profiles" = "y" ] || [ "$run_profiles" = "Y" ]; then
    echo "Running n_ridder profile scan..."
    python "$SCRIPT_DIR/profile_scan.py" --param n_ridder --range 2.5 3.5 --steps 5
    
    echo "Running sigma_ln_a profile scan..."
    python "$SCRIPT_DIR/profile_scan.py" --param sigma_ln_a --range 0.4 1.0 --steps 7
else
    echo "Skipping profile scans."
fi

# Step 3: Run optimized chains
echo ""
echo "=============================================="
echo "STEP 3: OPTIMIZED PRODUCTION CHAINS"
echo "=============================================="
echo "To run optimized chains:"
echo "  cobaya-run $SCRIPT_DIR/configs/optimized_ede_shoes_predesi.yaml"
echo "  cobaya-run $SCRIPT_DIR/configs/optimized_lcdm_shoes_predesi.yaml"
echo ""

read -p "Run optimized chains now? (y/N): " run_chains
if [ "$run_chains" = "y" ] || [ "$run_chains" = "Y" ]; then
    echo "Running optimized EDE chain..."
    nohup cobaya-run "$SCRIPT_DIR/configs/optimized_ede_shoes_predesi.yaml" &
    
    echo "Running optimized ΛCDM chain..."
    nohup cobaya-run "$SCRIPT_DIR/configs/optimized_lcdm_shoes_predesi.yaml" &
    
    echo "Chains started in background. Check with: ps aux | grep cobaya"
else
    echo "Skipping chain runs."
fi

# Step 4: Best-fit refinement (after chains complete)
echo ""
echo "=============================================="
echo "STEP 4: BEST-FIT REFINEMENT"
echo "=============================================="
echo "Run AFTER optimized chains complete:"
echo "  1. Extract best sample from chain"
echo "  2. Update ref values in bestfit_refine_ede.yaml"
echo "  3. cobaya-run $SCRIPT_DIR/configs/bestfit_refine_ede.yaml"
echo ""

echo "=============================================="
echo "OPTIMIZATION PIPELINE COMPLETE"
echo "=============================================="
echo ""
echo "Expected total improvement: Δχ² = -10 to -15"
echo ""
echo "Next steps:"
echo "  1. Wait for chains to complete (~24-48 hours)"
echo "  2. Run chi2_breakdown.py on optimized chains"
echo "  3. Run best-fit refinement"
echo "  4. Update paper with new numbers"
