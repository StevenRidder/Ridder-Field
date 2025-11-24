#!/bin/bash
# Quick calibration at potential extremum (theta = pi)
# This gives us the clean ΛCDM control configuration

set -e

echo "========================================================================"
echo "Step 1: Calibrate Lambda at Potential Extremum (theta = π)"
echo "========================================================================"
echo ""
echo "Goal: Find Lambda such that frozen field at theta=pi gives f_ridder ~ 0.69"
echo "Expected: Field should be stable even with damp=1.0 (dV/dphi = 0 at extremum)"
echo ""

# Run calibration with theta = pi
python3 calibrate_lambda_lcdm.py \
  --target 0.69 \
  --tolerance 0.01 \
  --max-iter 20 \
  --class-exe ./phase2/class/class \
  2>&1 | tee lambda_extremum_calibration.log

# Extract the converged Lambda
LAMBDA_EXTREMUM=$(grep "Lambda = " lambda_extremum_calibration.log | grep "eV" | tail -1 | awk '{print $3}')

echo ""
echo "========================================================================"
echo "Calibration Complete!"
echo "Lambda_extremum = $LAMBDA_EXTREMUM eV"
echo "========================================================================"
echo ""

# Save for next step
echo "$LAMBDA_EXTREMUM" > lambda_extremum.txt

echo "Next: Run damping continuity test at this extremum..."
echo "  bash validate_extremum_stability.sh"

