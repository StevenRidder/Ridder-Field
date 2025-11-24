#!/bin/bash
# Phase 1A Revised: Beta Ladder at Lower Lambda
# 
# Issue: Lambda=1.0 too stiff for beta > 0.05
# Fix: Test at Lambda=0.7 (known stable from earlier)
#
# Strategy: Find beta at Lambda=0.7, THEN optimize Lambda

cd ~/Ridder-Field/phase2/class

echo "======================================================================="
echo "PHASE 1A REVISED: BETA LADDER (Lambda = 0.7 eV)"
echo "Testing beta = 0.05, 0.10, 0.15 at Lambda = 0.7 eV"
echo "Goal: Find stable beta before optimizing Lambda"
echo "======================================================================="
echo

results_file="../../phase3_full_analysis/results/beta_ladder_v2_results.txt"
echo "# Beta Ladder V2 Results - $(date)" > $results_file
echo "# Lambda=0.7 eV, varying beta" >> $results_file
echo "# beta | Status | Runtime" >> $results_file

# Create configs for Lambda=0.7
for beta in 0.05 0.10 0.15; do
    ini="../../phase3_full_analysis/configs/unified_lambda0p7_beta${beta/./p}.ini"
    
    # Start from baby config and modify both Lambda and beta
    sed -e "s/ridder_Lambda_EDE_eV = 1.0/ridder_Lambda_EDE_eV = 0.7/g" \
        -e "s/beta_ridder = 0.05/beta_ridder = $beta/g" \
        -e "s/baby_lambda1p0/lambda0p7_beta${beta/./p}/g" \
        ../../unified_baby_lambda1p0.ini > $ini
    
    echo "Created: $ini"
done

echo
echo "-----------------------------------------------------------------------"
echo "Running CLASS for Lambda=0.7, beta sweep..."
echo "-----------------------------------------------------------------------"
echo

for beta in 0.05 0.10 0.15; do
    ini="../../phase3_full_analysis/configs/unified_lambda0p7_beta${beta/./p}.ini"
    
    echo "Testing Lambda=0.7, beta=$beta"
    
    start_time=$(date +%s)
    
    # Run CLASS with 10 min timeout
    timeout 600 ./class $ini > /tmp/class_lambda0p7_beta_${beta}.log 2>&1
    exit_code=$?
    
    end_time=$(date +%s)
    runtime=$((end_time - start_time))
    
    if [ $exit_code -eq 0 ]; then
        echo "  ✅ SUCCESS! Completed in ${runtime}s"
        echo "$beta | SUCCESS | ${runtime}s" >> $results_file
        
        # Check outputs
        root="output/unified_lambda0p7_beta${beta/./p}_"
        
        if [ -f "${root}00_background.dat" ] && [ -f "${root}00_cl_lensed.dat" ]; then
            echo "  ✓ All outputs generated"
        else
            echo "  ⚠️  Some outputs missing"
        fi
        
    elif [ $exit_code -eq 124 ]; then
        echo "  ⏱️  TIMEOUT (>10 min)"
        echo "$beta | TIMEOUT | >600s" >> $results_file
    else
        echo "  ❌ FAILED"
        if grep -q "Step size too small" /tmp/class_lambda0p7_beta_${beta}.log; then
            echo "     Reason: Perturbation stiffness"
            echo "$beta | STIFFNESS | ${runtime}s" >> $results_file
        else
            echo "     Reason: Unknown"
            tail -20 /tmp/class_lambda0p7_beta_${beta}.log
            echo "$beta | ERROR | ${runtime}s" >> $results_file
        fi
    fi
    
    echo
done

echo "======================================================================="
echo "BETA LADDER V2 COMPLETE"
echo "======================================================================="
echo
echo "Summary:"
cat $results_file
echo
echo "Next: Run analyze_beta_results.py with --version v2"
echo

