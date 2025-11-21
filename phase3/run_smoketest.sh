#!/bin/bash
# =============================================================================
# PHASE 3 SMOKE TEST - Quick Validation Run
# =============================================================================
# This script runs the minimal CLASS test and analyzes results
# Expected runtime: < 1 minute on MacBook Air
# =============================================================================

set -e

echo "=============================================================================="
echo "PHASE 3 SMOKE TEST (ULTRA-LIGHT)"
echo "=============================================================================="
echo ""

# Check if CLASS is available
if [ ! -f "../phase2/class/class" ]; then
    echo "❌ CLASS executable not found."
    echo "   Expected: ../phase2/class/class"
    echo "   Please compile CLASS first."
    exit 1
fi

# Create output directory if needed
mkdir -p output

# Run CLASS
echo "Running CLASS with smoke test configuration..."
echo "  Config: ridder_smoketest.ini"
echo "  Expected time: < 1 minute"
echo ""

cd ../phase2/class
./class ../../phase3/ridder_smoketest.ini

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ CLASS run failed. Check error messages above."
    exit 1
fi

echo ""
echo "✅ CLASS run completed successfully!"
echo ""

echo "=============================================================================="
echo "Smoke test complete!"
echo "Check results in phase3/output/ridder_smoketest_background.dat"
echo "=============================================================================="
