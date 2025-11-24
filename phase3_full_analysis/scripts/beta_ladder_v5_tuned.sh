#!/bin/bash
# Phase 1A V5: Beta Ladder with TUNED LAMBDA
#
# SOLUTION: Wide window [0.1, 5.0] + theta_i = 2.0 + Lambda = 0.7 eV
# Expected: f_peak ~ 12-15%, perturbations stable

cd ~/Ridder-Field/phase2/class

echo "======================================================================="
echo "PHASE 1A V5: BETA LADDER (TUNED LAMBDA)"
echo "Testing beta = 0.05, 0.10, 0.15"
echo "Lambda = 0.7 eV (tuned for f_peak ~ 12-15%)"
echo "Window = [0.1, 5.0], theta_i = 2.0"
echo "FINAL FIX: Window + theta_i + Lambda all optimized"
echo "======================================================================="
echo

results_file="../../phase3_full_analysis/results/beta_ladder_v5_results.txt"
echo "# Beta Ladder V5 Results - $(date)" > $results_file
echo "# Lambda=0.7 eV (tuned), wide window, varying beta" >> $results_file
echo "# beta | Status | Runtime | f_peak | z_peak" >> $results_file

# Create configs with TUNED parameters
for beta in 0.05 0.10 0.15; do
    ini="../../phase3_full_analysis/configs/unified_tuned_beta${beta/./p}.ini"
    
    # Start from baby config and modify ALL key parameters
    sed -e "s/ridder_Lambda_EDE_eV = 1.0/ridder_Lambda_EDE_eV = 0.7/g" \
        -e "s/theta_i_ridder = 1.0/theta_i_ridder = 2.0/g" \
        -e "s/ridder_theta_EDE_low = 0.5/ridder_theta_EDE_low = 0.1/g" \
        -e "s/ridder_theta_EDE_high = 2.0/ridder_theta_EDE_high = 5.0/g" \
        -e "s/ridder_sigma_theta_EDE = 0.2/ridder_sigma_theta_EDE = 0.4/g" \
        -e "s/beta_ridder = 0.05/beta_ridder = $beta/g" \
        -e "s/baby_lambda1p0/tuned_beta${beta/./p}/g" \
        ../../unified_baby_lambda1p0.ini > $ini
    
    echo "Created: $ini (Lambda=0.7, window=[0.1,5.0], theta_i=2.0, beta=$beta)"
done

echo
echo "-----------------------------------------------------------------------"
echo "Running CLASS with TUNED parameters..."
echo "-----------------------------------------------------------------------"
echo

for beta in 0.05 0.10 0.15; do
    ini="../../phase3_full_analysis/configs/unified_tuned_beta${beta/./p}.ini"
    
    echo "Testing Lambda=0.7, window=[0.1,5.0], theta_i=2.0, beta=$beta"
    
    start_time=$(date +%s)
    
    # Run CLASS with 10 min timeout
    timeout 600 ./class $ini > /tmp/class_tuned_beta_${beta}.log 2>&1
    exit_code=$?
    
    end_time=$(date +%s)
    runtime=$((end_time - start_time))
    
    if [ $exit_code -eq 0 ]; then
        echo "  ✅ SUCCESS! Completed in ${runtime}s"
        
        # Extract EDE diagnostics from background file
        root="output/unified_tuned_beta${beta/./p}_"
        
        if [ -f "${root}00_background.dat" ]; then
            # Use Python to extract f_peak and z_peak
            diagnostics=$(python3 << EOF
import numpy as np
try:
    data = np.loadtxt("${root}00_background.dat")
    z = data[:, 0]
    rho_r = data[:, 15]
    rho_t = data[:, 19]
    f = rho_r / rho_t
    mask = z > 50
    idx = np.argmax(f[mask])
    print(f"{f[mask][idx]:.4f},{z[mask][idx]:.1f}")
except:
    print("ERROR,ERROR")
EOF
)
            f_peak=$(echo $diagnostics | cut -d',' -f1)
            z_peak=$(echo $diagnostics | cut -d',' -f2)
            
            echo "  📊 f_peak = $f_peak ($(($(echo "$f_peak * 100" | bc -l | cut -d'.' -f1)))%)"
            echo "  📊 z_peak = $z_peak"
            
            if (( $(echo "$f_peak > 0.08" | bc -l) )) && (( $(echo "$f_peak < 0.20" | bc -l) )); then
                echo "  🎯 f_peak in target range (8-20%)!"
            fi
            
            echo "$beta | SUCCESS | ${runtime}s | $f_peak | $z_peak" >> $results_file
        else
            echo "  ⚠️  Background file missing"
            echo "$beta | PARTIAL | ${runtime}s | - | -" >> $results_file
        fi
        
    elif [ $exit_code -eq 124 ]; then
        echo "  ⏱️  TIMEOUT (>10 min)"
        echo "$beta | TIMEOUT | >600s | - | -" >> $results_file
    else
        echo "  ❌ FAILED"
        
        if grep -q "Step size too small" /tmp/class_tuned_beta_${beta}.log; then
            echo "     Reason: Perturbation stiffness"
            echo "$beta | STIFFNESS | ${runtime}s | - | -" >> $results_file
        else
            echo "     Reason: Unknown"
            tail -20 /tmp/class_tuned_beta_${beta}.log
            echo "$beta | ERROR | ${runtime}s | - | -" >> $results_file
        fi
    fi
    
    echo
done

echo "======================================================================="
echo "BETA LADDER V5 COMPLETE"
echo "======================================================================="
echo
echo "Summary:"
cat $results_file
echo
echo "If successful: Proceed to analyze_beta_results.py"
echo "If still stiff: Try Lambda = 0.5 eV (V6)"
echo

