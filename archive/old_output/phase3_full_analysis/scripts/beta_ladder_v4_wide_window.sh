#!/bin/bash
# Phase 1A V4: Beta Ladder with WIDE WINDOW
#
# ROOT CAUSE: Window [0.5, 2.0] too narrow
# Field rolls from theta~2 to theta~5
# FIX: Widen window to [0.1, 5.0]

cd ~/Ridder-Field/phase2/class

echo "======================================================================="
echo "PHASE 1A V4: BETA LADDER (WIDE WINDOW)"
echo "Testing beta = 0.05, 0.10, 0.15 at Lambda = 1.0 eV"
echo "Window: [0.1, 5.0] (was [0.5, 2.0])"
echo "ROOT CAUSE FIX: Field rolls from theta=2 to theta=5"
echo "======================================================================="
echo

results_file="../../phase3_full_analysis/results/beta_ladder_v4_results.txt"
echo "# Beta Ladder V4 Results - $(date)" > $results_file
echo "# Lambda=1.0 eV, wide window [0.1, 5.0], varying beta" >> $results_file
echo "# beta | Status | Runtime | f_ridder" >> $results_file

# Create configs with WIDE window
for beta in 0.05 0.10 0.15; do
    ini="../../phase3_full_analysis/configs/unified_wide_beta${beta/./p}.ini"
    
    # Start from baby config and modify window AND theta_i AND beta
    sed -e "s/theta_i_ridder = 1.0/theta_i_ridder = 2.0/g" \
        -e "s/ridder_theta_EDE_low = 0.5/ridder_theta_EDE_low = 0.1/g" \
        -e "s/ridder_theta_EDE_high = 2.0/ridder_theta_EDE_high = 5.0/g" \
        -e "s/beta_ridder = 0.05/beta_ridder = $beta/g" \
        -e "s/baby_lambda1p0/wide_beta${beta/./p}/g" \
        ../../unified_baby_lambda1p0.ini > $ini
    
    echo "Created: $ini (window=[0.1,5.0], theta_i=2.0, beta=$beta)"
done

echo
echo "-----------------------------------------------------------------------"
echo "Running CLASS with WIDE window..."
echo "-----------------------------------------------------------------------"
echo

for beta in 0.05 0.10 0.15; do
    ini="../../phase3_full_analysis/configs/unified_wide_beta${beta/./p}.ini"
    
    echo "Testing window=[0.1,5.0], Lambda=1.0, beta=$beta"
    
    start_time=$(date +%s)
    
    # Run CLASS with 10 min timeout
    timeout 600 ./class $ini > /tmp/class_wide_beta_${beta}.log 2>&1
    exit_code=$?
    
    end_time=$(date +%s)
    runtime=$((end_time - start_time))
    
    if [ $exit_code -eq 0 ]; then
        echo "  ✅ SUCCESS! Completed in ${runtime}s"
        
        # Extract f_ridder from log
        f_ridder=$(grep "f_ridder" /tmp/class_wide_beta_${beta}.log | tail -1 | awk '{print $3}')
        echo "  f_ridder = $f_ridder"
        
        if (( $(echo "$f_ridder > 0.05" | bc -l) )); then
            echo "  🎯 f_ridder in expected range! Window fix SUCCESS!"
        elif (( $(echo "$f_ridder < 0.01" | bc -l) )); then
            echo "  ⚠️  f_ridder still too small"
        fi
        
        echo "$beta | SUCCESS | ${runtime}s | $f_ridder" >> $results_file
        
    elif [ $exit_code -eq 124 ]; then
        echo "  ⏱️  TIMEOUT (>10 min)"
        echo "$beta | TIMEOUT | >600s | -" >> $results_file
    else
        echo "  ❌ FAILED"
        
        # Check f_ridder even if failed
        f_ridder=$(grep "f_ridder" /tmp/class_wide_beta_${beta}.log | tail -1 | awk '{print $3}')
        if [ -n "$f_ridder" ]; then
            echo "  f_ridder = $f_ridder"
        fi
        
        if grep -q "Step size too small" /tmp/class_wide_beta_${beta}.log; then
            echo "     Reason: Perturbation stiffness"
            echo "$beta | STIFFNESS | ${runtime}s | $f_ridder" >> $results_file
        else
            echo "     Reason: Unknown"
            tail -20 /tmp/class_wide_beta_${beta}.log
            echo "$beta | ERROR | ${runtime}s | $f_ridder" >> $results_file
        fi
    fi
    
    echo
done

echo "======================================================================="
echo "BETA LADDER V4 COMPLETE"
echo "======================================================================="
echo
echo "Summary:"
cat $results_file
echo
echo "Expected: f_ridder ~ 0.10-0.15 for successful window match"
echo
echo "Next: If successful, run analyze_beta_results.py"
echo

