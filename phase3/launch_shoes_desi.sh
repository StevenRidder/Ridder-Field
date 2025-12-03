#!/bin/bash
# Launch SH0ES + DESI world chains
# Tests whether EDE survives DESI BAO with H0 tension active

set -e

echo "=============================================="
echo "TIER 5: SH0ES + DESI WORLD"
echo "=============================================="
echo ""
echo "This tests the KEY question:"
echo "  Does EDE survive when confronted with DESI's BAO"
echo "  constraints while the H0 tension is active?"
echo ""

cd /Users/steveridder/Git/Ridder-Field/phase3

# Create chains directory if needed
mkdir -p chains

echo "Starting ΛCDM chain..."
echo "---------------------------------------------"
cobaya-run configs/tier5_lcdm_shoes_desi_local.yaml &
LCDM_PID=$!

echo "Starting CPL chain..."
echo "---------------------------------------------"
cobaya-run configs/tier5_cpl_shoes_desi_local.yaml &
CPL_PID=$!

# Wait a bit before starting EDE (heavier computation)
sleep 5

echo "Starting EDE chain..."
echo "---------------------------------------------"
cobaya-run configs/tier5_ede_shoes_desi_local.yaml &
EDE_PID=$!

echo ""
echo "=============================================="
echo "All chains started!"
echo "=============================================="
echo ""
echo "PIDs:"
echo "  ΛCDM: $LCDM_PID"
echo "  CPL:  $CPL_PID"
echo "  EDE:  $EDE_PID"
echo ""
echo "Monitor with:"
echo "  tail -f chains/tier5_lcdm_shoes_desi.*.txt"
echo "  tail -f chains/tier5_cpl_shoes_desi.*.txt"
echo "  tail -f chains/tier5_ede_shoes_desi.*.txt"
echo ""
echo "Or check status with:"
echo "  python3 tier5_status.py"
echo ""

# Wait for all to complete
wait $LCDM_PID $CPL_PID $EDE_PID

echo ""
echo "=============================================="
echo "All chains completed!"
echo "=============================================="

