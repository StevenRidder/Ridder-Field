#!/bin/bash
# Phase 1A V3: Beta Ladder with FIXED theta_i
#
# ROOT CAUSE: theta too small (0.07) relative to window (0.5-2.0)
# FIX: Increase theta_i from 1.0 to 2.0 to land in window

cd ~/Ridder-Field/phase2/class

echo "======================================================================="
echo "PHASE 1A V3: BETA LADDER (FIXED theta_i)"
echo "Testing beta = 0.05, 0.10, 0.15 at Lambda = 1.0 eV, theta_i = 2.0"
echo "ROOT CAUSE FIX: theta was below window (0.07 < 0.5)"
echo "======================================================================="
echo

results_file="../../phase3_full_analysis/results/beta_ladder_v3_results.txt"
echo "# Beta Ladder V3 Results - $(date)" > $results_file
echo "# Lambda=1.0 eV, theta_i=2.0 (FIXED), varying beta" >> $results_file
echo "# beta | Status | Runtime" >> $results_file

# Create configs with FIXED theta_i
for beta in 0.05 0.10 0.15; do
    ini="../../phase3_full_analysis/configs/unified_fixed_beta${beta/./p}.ini"
    
    # Start from baby config and modify theta_i AND beta
    sed -e "s/theta_i_ridder = 1.0/theta_i_ridder = 2.0/g" \
        -e "s/beta_ridder = 0.05/beta_ridder = $beta/g" \
        -e "s/baby_lambda1p0/fixed_beta${beta/./p}/g" \
        ../../unified_baby_lambda1p0.ini > $ini
    
    echo "Created: $ini (theta_i=2.0, beta=$beta)"
done

echo
echo "-----------------------------------------------------------------------"
echo "Running CLASS with FIXED theta_i..."
echo "-----------------------------------------------------------------------"
echo

for beta in 0.05 0.10 0.15; do
    ini="../../phase3_full_analysis/configs/unified_fixed_beta${beta/./p}.ini"
    
    echo "Testing theta_i=2.0, Lambda=1.0, beta=$beta"
    
    start_time=$(date +%s)
    
    # Run CLASS with 10 min timeout
    timeout 600 ./class $ini > /tmp/class_fixed_beta_${beta}.log 2>&1
    exit_code=$?
    
    end_time=$(date +%s)
    runtime=$((end_time - start_time))
    
    if [ $exit_code -eq 0 ]; then
        echo "  ✅ SUCCESS! Completed in ${runtime}s"
        
        # Extract f_ridder from log
        f_ridder=$(grep "f_ridder" /tmp/class_fixed_beta_${beta}.log | tail -1 | awk '{print $3}')
        echo "  f_ridder = $f_ridder"
        
        echo "$beta | SUCCESS | ${runtime}s | f_ridder=$f_ridder" >> $results_file
        
    elif [ $exit_code -eq 124 ]; then
        echo "  ⏱️  TIMEOUT (>10 min)"
        echo "$beta | TIMEOUT | >600s" >> $results_file
    else
        echo "  ❌ FAILED"
        
        # Check f_ridder even if failed
        f_ridder=$(grep "f_ridder" /tmp/class_fixed_beta_${beta}.log | tail -1 | awk '{print $3}')
        if [ -n "$f_ridder" ]; then
            echo "  f_ridder = $f_ridder (too small?)"
        fi
        
        if grep -q "Step size too small" /tmp/class_fixed_beta_${beta}.log; then
            echo "     Reason: Perturbation stiffness"
            echo "$beta | STIFFNESS | ${runtime}s | f_ridder=$f_ridder" >> $results_file
        else
            echo "     Reason: Unknown"
            tail -20 /tmp/class_fixed_beta_${beta}.log
            echo "$beta | ERROR | ${runtime}s" >> $results_file
        fi
    fi
    
    echo
done

echo "======================================================================="
echo "BETA LADDER V3 COMPLETE"
echo "======================================================================="
echo
echo "Summary:"
cat $results_file
echo
echo "If f_ridder ~ 0.1-0.15: SUCCESS! Window fix worked."
echo "If f_ridder ~ 10^-7: Window still too narrow, need Option 2."
echo
echo "Next: Run analyze_beta_results.py with --version v3"
echo

