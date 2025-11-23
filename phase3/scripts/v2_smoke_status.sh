#!/usr/bin/env bash
set -euo pipefail

# V2 Smoke Test Status Checker
# Monitors the Ridder V2 MCMC smoke test running on Australia VM

VM_HOST="ridderadmin@172.174.34.125"
REMOTE_ROOT="/home/ridderadmin/Ridder-Field/phase3"
CHAIN_FILE="${REMOTE_ROOT}/chains/ridder_v2_smoke.1.txt"
LOG_FILE="${REMOTE_ROOT}/mcmc_smoke.log"
CONFIG_FILE="${REMOTE_ROOT}/ridder_v2_mcmc_smoke.yaml"

echo "======================================================================"
echo "RIDDER V2 SMOKE TEST: PROGRESS REPORT"
echo "======================================================================"
echo ""

# 1. Check if process is running
echo "--- PROCESS STATUS ---"
PROCESS_CHECK=$(ssh ${VM_HOST} "ps aux | grep -E 'python3.*ridder_v2_mcmc_smoke' | grep -v grep" || echo "")
if [ -n "${PROCESS_CHECK}" ]; then
    PID=$(echo "${PROCESS_CHECK}" | awk '{print $2}')
    CPU=$(echo "${PROCESS_CHECK}" | awk '{print $3}')
    MEM=$(echo "${PROCESS_CHECK}" | awk '{print $4}')
    ELAPSED=$(echo "${PROCESS_CHECK}" | awk '{print $10}')
    echo "✓ MCMC process running (PID: ${PID})"
    printf "  Runtime: %s | CPU: %s%% | Mem: %s%%\n" "${ELAPSED}" "${CPU}" "${MEM}"
else
    echo "✗ No MCMC process found"
    echo "  (Process may have completed or crashed)"
fi
echo ""

# 2. Check chain file and progress
echo "--- CHAIN PROGRESS ---"
CHAIN_EXISTS=$(ssh ${VM_HOST} "[ -f ${CHAIN_FILE} ] && echo 'yes' || echo 'no'")
if [ "${CHAIN_EXISTS}" = "yes" ]; then
    # Get sample count (subtract 1 for header)
    SAMPLE_COUNT=$(ssh ${VM_HOST} "wc -l < ${CHAIN_FILE}")
    SAMPLE_COUNT=$((SAMPLE_COUNT - 1))
    
    # Get max_samples from config
    MAX_SAMPLES=$(ssh ${VM_HOST} "grep 'max_samples:' ${CONFIG_FILE} | awk '{print \$2}'")
    
    # Calculate progress
    PERCENT=$(awk "BEGIN {printf \"%.1f\", (${SAMPLE_COUNT}/${MAX_SAMPLES})*100}")
    
    # Estimate time remaining
    if [ ${SAMPLE_COUNT} -gt 0 ]; then
        # Get file age in seconds
        FILE_AGE=$(ssh ${VM_HOST} "stat -c %Y ${CHAIN_FILE}")
        CURRENT_TIME=$(ssh ${VM_HOST} "date +%s")
        ELAPSED_SEC=$((CURRENT_TIME - FILE_AGE))
        
        # Calculate rate and ETA
        RATE=$(awk "BEGIN {printf \"%.1f\", ${SAMPLE_COUNT}/${ELAPSED_SEC}}")
        REMAINING_SAMPLES=$((MAX_SAMPLES - SAMPLE_COUNT))
        ETA_SEC=$(awk "BEGIN {printf \"%.0f\", ${REMAINING_SAMPLES}/${RATE}}")
        ETA_MIN=$((ETA_SEC / 60))
        ETA_HOUR=$((ETA_MIN / 60))
        ETA_MIN_REMAIN=$((ETA_MIN % 60))
        
        echo "✓ Chain file: ridder_v2_smoke.1.txt"
        echo "  Samples: ${SAMPLE_COUNT}/${MAX_SAMPLES} (${PERCENT}%)"
        printf "  Rate: %.1f samples/sec (%.1f sec/sample)\n" "${RATE}" "$(awk "BEGIN {print 1/${RATE}}")"
        if [ ${ETA_HOUR} -gt 0 ]; then
            printf "  ETA: %dh %dm\n" "${ETA_HOUR}" "${ETA_MIN_REMAIN}"
        else
            printf "  ETA: %dm\n" "${ETA_MIN}"
        fi
    else
        echo "✓ Chain file exists but no samples yet"
    fi
else
    echo "⚠ Chain file not yet created"
    echo "  (Cobaya creates it after first accepted sample)"
fi
echo ""

# 3. Show latest samples with key parameters
if [ "${CHAIN_EXISTS}" = "yes" ] && [ ${SAMPLE_COUNT} -gt 0 ]; then
    echo "--- LATEST SAMPLES ---"
    echo "Columns: H0 | Lambda_EDE | theta_i | beta | chi2"
    echo ""
    
    ssh ${VM_HOST} "tail -10 ${CHAIN_FILE}" | awk 'NR>1 {
        printf "  Sample %2d: H0=%.2f  Lambda=%.3f  theta=%.3f  beta=%.4f  chi2=%.1f\n", 
        NR-1, $5, $9, $10, $11, $38
    }'
    echo ""
fi

# 4. Compute statistics (if enough samples)
if [ "${CHAIN_EXISTS}" = "yes" ] && [ ${SAMPLE_COUNT} -gt 10 ]; then
    echo "--- STATISTICS (Last 50% of samples) ---"
    
    # Use SSH to compute stats on remote machine
    ssh ${VM_HOST} "tail -n +2 ${CHAIN_FILE}" | awk -v n="${SAMPLE_COUNT}" '
    BEGIN {
        h0_sum=0; h0_sumsq=0;
        lambda_sum=0; lambda_sumsq=0;
        theta_sum=0; theta_sumsq=0;
        beta_sum=0; beta_sumsq=0;
        chi2_sum=0; chi2_min=999999;
        count=0;
        start_row = int(n/2);
    }
    NR > start_row {
        h0=$5; lambda=$9; theta=$10; beta=$11; chi2=$38;
        
        h0_sum+=h0; h0_sumsq+=h0*h0;
        lambda_sum+=lambda; lambda_sumsq+=lambda*lambda;
        theta_sum+=theta; theta_sumsq+=theta*theta;
        beta_sum+=beta; beta_sumsq+=beta*beta;
        chi2_sum+=chi2;
        if (chi2 < chi2_min) chi2_min=chi2;
        
        count++;
    }
    END {
        if (count > 0) {
            h0_mean = h0_sum/count;
            h0_std = sqrt(h0_sumsq/count - h0_mean*h0_mean);
            
            lambda_mean = lambda_sum/count;
            lambda_std = sqrt(lambda_sumsq/count - lambda_mean*lambda_mean);
            
            theta_mean = theta_sum/count;
            theta_std = sqrt(theta_sumsq/count - theta_mean*theta_mean);
            
            beta_mean = beta_sum/count;
            beta_std = sqrt(beta_sumsq/count - beta_mean*beta_mean);
            
            chi2_mean = chi2_sum/count;
            
            printf "  H₀           = %.2f ± %.2f km/s/Mpc\n", h0_mean, h0_std;
            printf "  Lambda_EDE   = %.3f ± %.3f\n", lambda_mean, lambda_std;
            printf "  theta_i      = %.3f ± %.3f\n", theta_mean, theta_std;
            printf "  beta         = %.4f ± %.4f\n", beta_mean, beta_std;
            printf "  χ² (mean)    = %.1f\n", chi2_mean;
            printf "  χ² (best)    = %.1f\n", chi2_min;
            
            # Interpretation
            print "";
            print "INTERPRETATION:";
            if (h0_mean > 68.5) print "  ✅ H₀ elevated above Planck baseline (~67.4)";
            else if (h0_mean > 67.5) print "  ⚠️  H₀ slightly elevated";
            else print "  ❌ H₀ at ΛCDM level";
            
            if (lambda_mean > 0.8) print "  ⚠️  Strong EDE (Lambda > 0.8)";
            else if (lambda_mean > 0.3) print "  ✅ Moderate EDE (0.3 < Lambda < 0.8)";
            else print "  ⚠️  Weak EDE (Lambda < 0.3)";
            
            if (theta_mean > 2.0) print "  ✅ Field in Ridder Valley (theta > 2.0)";
            else if (theta_mean > 1.0) print "  ⚠️  Field in transition region";
            else print "  ❌ Field near ΛCDM (theta < 1.0)";
            
            if (beta_mean > 0.02) print "  ✅ Strong DM coupling (beta > 0.02)";
            else if (beta_mean > 0.01) print "  ⚠️  Moderate DM coupling";
            else print "  ❌ Weak/no DM coupling";
            
            if (chi2_min < 2780) print "  ✅ Excellent fit (chi2 < 2780)";
            else if (chi2_min < 2800) print "  ✅ Good fit (chi2 < 2800)";
            else print "  ⚠️  Fit needs improvement";
        }
    }'
    echo ""
fi

# 5. Check for errors in log
echo "--- ERROR CHECK ---"
LOG_EXISTS=$(ssh ${VM_HOST} "[ -f ${LOG_FILE} ] && echo 'yes' || echo 'no'")
if [ "${LOG_EXISTS}" = "yes" ]; then
    ERROR_COUNT=$(ssh ${VM_HOST} "grep -i 'error\|exception\|failed\|traceback' ${LOG_FILE} | wc -l")
    if [ ${ERROR_COUNT} -gt 0 ]; then
        echo "⚠ Errors found: ${ERROR_COUNT}"
        echo ""
        echo "Recent errors:"
        echo "----------------------------------------"
        ssh ${VM_HOST} "grep -i 'error\|exception\|failed' ${LOG_FILE} | tail -5"
        echo "----------------------------------------"
    else
        echo "✓ No errors detected"
    fi
else
    echo "⚠ Log file not found"
fi
echo ""

# 6. Show recent log output
echo "--- RECENT LOG OUTPUT ---"
if [ "${LOG_EXISTS}" = "yes" ]; then
    echo "Last 15 lines:"
    echo "----------------------------------------"
    ssh ${VM_HOST} "tail -15 ${LOG_FILE}"
    echo "----------------------------------------"
else
    echo "⚠ Log file not available"
fi
echo ""

# 7. Quick commands
echo "======================================================================"
echo "QUICK COMMANDS:"
echo "  Live tail:     ssh ${VM_HOST} 'tail -f ${CHAIN_FILE}'"
echo "  Watch log:     ssh ${VM_HOST} 'tail -f ${LOG_FILE}'"
echo "  Kill process:  ssh ${VM_HOST} 'pkill -f ridder_v2_mcmc_smoke'"
echo "  Re-run:        ssh ${VM_HOST} 'cd ${REMOTE_ROOT} && python3 -m cobaya.run ridder_v2_mcmc_smoke.yaml --force'"
echo "======================================================================"

