#!/bin/bash
# Validate that field at extremum (theta=pi) is stable across damping values

set -e

# Read calibrated Lambda
if [ ! -f lambda_extremum.txt ]; then
    echo "ERROR: lambda_extremum.txt not found!"
    echo "Run calibrate_lambda_at_extremum.sh first"
    exit 1
fi

LAMBDA=$(cat lambda_extremum.txt)

echo "========================================================================"
echo "Step 2: Validate Extremum Stability"
echo "========================================================================"
echo ""
echo "Configuration:"
echo "  theta_i = π (3.14159 rad)"
echo "  Lambda = $LAMBDA eV"
echo ""
echo "Testing damping values: 0.0, 1e-3, 1e-2, 0.1, 1.0"
echo "Expected: rho_ridder should remain constant (dV/dphi = 0 at extremum)"
echo ""

# Create test ini files
for damp in 0.0 0.001 0.01 0.1 1.0; do
    cat > test_extremum_damp_${damp}.ini <<EOF
# Extremum Stability Test
# theta_i = pi (potential extremum), damping = ${damp}

H0 = 67.36
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544
YHe = 0.2454
gauge = newtonian

# Ridder at extremum
Lambda_EDE_ridder = ${LAMBDA}
f_axion_ridder = 2.435e27
theta_i_ridder = 3.14159265359
beta_ridder = 0.0
n_ridder = 3
ridder_c_slow = 0.0

ridder_freeze_phi = no
ridder_force_damping = ${damp}
use_ridder_shooting = 0

output = 
write background = no
EOF
done

# Run tests
echo "Running tests..."
echo "damp     rho_early         rho_late          ratio         status"
echo "--------------------------------------------------------------------"

for damp in 0.0 0.001 0.01 0.1 1.0; do
    result=$(timeout 30 ./phase2/class/class test_extremum_damp_${damp}.ini 2>&1 || echo "FAILED")
    
    if echo "$result" | grep -q "BG_INIT: background_solve OK"; then
        # Extract rho values
        rho_early=$(echo "$result" | grep "RIDDER DEBUG.*a=1.0.*e-03" | head -1 | grep -oP 'rho_ridder=\K[\d.e+-]+' || echo "N/A")
        rho_late=$(echo "$result" | grep "RIDDER DEBUG" | tail -1 | grep -oP 'rho_ridder=\K[\d.e+-]+' || echo "N/A")
        
        if [ "$rho_early" != "N/A" ] && [ "$rho_late" != "N/A" ]; then
            ratio=$(echo "scale=6; $rho_late / $rho_early" | bc)
            
            # Check if ratio is close to 1.0 (stable field)
            if (( $(echo "$ratio > 0.99" | bc -l) )) && (( $(echo "$ratio < 1.01" | bc -l) )); then
                status="✓ STABLE"
            else
                status="✗ ROLLING"
            fi
        else
            ratio="N/A"
            status="✗ NO DATA"
        fi
        
        printf "%-8s %-17s %-17s %-13s %s\n" "$damp" "$rho_early" "$rho_late" "$ratio" "$status"
    else
        printf "%-8s %-17s %-17s %-13s %s\n" "$damp" "N/A" "N/A" "N/A" "✗ FAILED"
    fi
done

echo ""
echo "========================================================================"
echo "Extremum Validation Complete!"
echo ""
echo "Expected: All ratios should be ~1.0 (field stable at extremum)"
echo "If any show rolling, potential may have additional structure"
echo "========================================================================"

