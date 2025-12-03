#!/bin/bash
# Test Lambda ladder to find stable perturbation point

cd ~/Ridder-Field/phase2/class

echo "======================================================================="
echo "LAMBDA LADDER TEST"
echo "Testing Lambda_EDE = 0.3, 0.5, 0.7, 1.0 eV"
echo "Goal: Find largest Lambda where perturbations complete"
echo "======================================================================="
echo

for ini in ../../unified_baby_lambda0p5.ini ../../unified_baby_lambda0p7.ini ../../unified_baby_lambda1p0.ini; do
    lam=$(basename $ini .ini | sed 's/unified_baby_lambda//' | sed 's/p/./g')
    echo "-----------------------------------------------------------------------"
    echo "Testing Lambda = $lam eV"
    echo "-----------------------------------------------------------------------"
    
    # Run CLASS and capture exit code
    timeout 300 ./class $ini > /tmp/class_lambda_${lam}.log 2>&1
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ SUCCESS! Lambda = $lam completed"
        echo "   Checking outputs..."
        
        # Check if background and cl files were created
        root=$(grep "^root = " $ini | awk '{print $3}')
        bg_file="${root}00_background.dat"
        cl_file="${root}00_cl_lensed.dat"
        
        if [ -f "$bg_file" ]; then
            bg_size=$(du -h "$bg_file" | cut -f1)
            echo "   ✓ Background: $bg_size"
        else
            echo "   ⚠️  Background missing"
        fi
        
        if [ -f "$cl_file" ]; then
            cl_size=$(du -h "$cl_file" | cut -f1)
            echo "   ✓ CMB spectra: $cl_size"
        else
            echo "   ⚠️  CMB spectra missing"
        fi
        
        echo
        echo "🎉 FOUND STABLE POINT: Lambda = $lam eV"
        echo
        
    elif [ $exit_code -eq 124 ]; then
        echo "⏱️  TIMEOUT (>5 min) - likely hung, not stable"
    else
        # Check error type
        if grep -q "Step size too small" /tmp/class_lambda_${lam}.log; then
            echo "❌ FAILED - Perturbation stiffness"
            grep "Step size too small" /tmp/class_lambda_${lam}.log | head -1
        elif grep -q "Error" /tmp/class_lambda_${lam}.log; then
            echo "❌ FAILED - Other error"
            grep "Error" /tmp/class_lambda_${lam}.log | head -3
        else
            echo "❌ FAILED - Unknown reason"
        fi
    fi
    
    echo
done

echo "======================================================================="
echo "LAMBDA LADDER COMPLETE"
echo "======================================================================="
echo
echo "Summary:"
echo "  Lambda = 0.3: Previously tested - failed late"
echo "  Lambda = 0.5: $([ -f output/unified_baby_lambda0p5_00_cl_lensed.dat ] && echo '✅ STABLE' || echo '❌ Failed')"
echo "  Lambda = 0.7: $([ -f output/unified_baby_lambda0p7_00_cl_lensed.dat ] && echo '✅ STABLE' || echo '❌ Failed')"
echo "  Lambda = 1.0: $([ -f output/unified_baby_lambda1p0_00_cl_lensed.dat ] && echo '✅ STABLE' || echo '❌ Failed')"
echo
echo "Next: If any succeeded, extract S8 and CMB residuals"
echo "      If all failed, try with looser tolerances or fluid mode"
echo

