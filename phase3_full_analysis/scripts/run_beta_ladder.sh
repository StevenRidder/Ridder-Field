#!/bin/bash
# Phase 1A: Beta Ladder
# Test beta = 0.10, 0.15, 0.20 at Lambda=1.0 eV

cd ~/Ridder-Field/phase2/class

echo "======================================================================="
echo "PHASE 1A: BETA LADDER"
echo "Testing beta = 0.10, 0.15, 0.20 at Lambda = 1.0 eV"
echo "Goal: Find beta that balances S8 reduction with CMB fit"
echo "======================================================================="
echo

results_file="../../phase3_full_analysis/results/beta_ladder_results.txt"
echo "# Beta Ladder Results - $(date)" > $results_file
echo "# beta | Status | H0 | S8 | CMB_chi2 | Runtime" >> $results_file

for beta in 0.10 0.15 0.20; do
    ini="../../phase3_full_analysis/configs/unified_beta${beta/./p}.ini"
    
    echo "-----------------------------------------------------------------------"
    echo "Testing beta = $beta"
    echo "-----------------------------------------------------------------------"
    
    start_time=$(date +%s)
    
    # Run CLASS with 5 min timeout
    timeout 300 ./class $ini > /tmp/class_beta_${beta}.log 2>&1
    exit_code=$?
    
    end_time=$(date +%s)
    runtime=$((end_time - start_time))
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ SUCCESS! beta = $beta completed in ${runtime}s"
        
        # Check outputs
        root="output/unified_beta${beta/./p}_"
        
        if [ -f "${root}00_background.dat" ] && [ -f "${root}00_cl_lensed.dat" ] && [ -f "${root}00_pk.dat" ]; then
            echo "   ✓ All outputs generated"
            echo "$beta | SUCCESS | TBD | TBD | TBD | ${runtime}s" >> $results_file
        else
            echo "   ⚠️  Some outputs missing"
            echo "$beta | PARTIAL | - | - | - | ${runtime}s" >> $results_file
        fi
        
    elif [ $exit_code -eq 124 ]; then
        echo "⏱️  TIMEOUT (>5 min)"
        echo "$beta | TIMEOUT | - | - | - | >300s" >> $results_file
    else
        echo "❌ FAILED"
        if grep -q "Step size too small" /tmp/class_beta_${beta}.log; then
            echo "   Reason: Perturbation stiffness"
            echo "$beta | STIFFNESS | - | - | - | ${runtime}s" >> $results_file
        else
            echo "   Reason: Unknown"
            echo "$beta | ERROR | - | - | - | ${runtime}s" >> $results_file
        fi
    fi
    
    echo
done

echo "======================================================================="
echo "BETA LADDER COMPLETE"
echo "======================================================================="
echo
echo "Summary:"
cat $results_file
echo
echo "Next: Run analyze_beta_results.py to extract observables"
echo

