#!/usr/bin/env bash
set -euo pipefail

# Quick Tier 1 Planck status check
# Shows samples, theta_i, beta, and chi2 for all 4 chains

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NUM_CHAINS=4

echo "======================================================================"
echo "TIER 1 PLANCK: PROGRESS REPORT"
echo "======================================================================"
echo ""

ALL_THETA=()
ALL_BETA=()
TOTAL_SAMPLES=0
GLOBAL_BEST_CHI2=1e30

for i in $(seq 1 ${NUM_CHAINS}); do
    CHAIN_FILE="${ROOT_DIR}/chain${i}_work/chains/ridder_tier1_planck.1.txt"
    
    if [ -f "${CHAIN_FILE}" ]; then
        # Count samples (skip header)
        SAMPLE_COUNT=$(tail -n +2 "${CHAIN_FILE}" | grep -v '^$' | wc -l | tr -d ' ')
        TOTAL_SAMPLES=$((TOTAL_SAMPLES + SAMPLE_COUNT))
        
        # Get last sample (theta_i is column 3, beta is column 4, chi2 is last column)
        LAST_LINE=$(tail -1 "${CHAIN_FILE}")
        LAST_THETA=$(echo "${LAST_LINE}" | awk '{print $3}')
        LAST_BETA=$(echo "${LAST_LINE}" | awk '{print $4}')
        LAST_CHI2=$(echo "${LAST_LINE}" | awk '{print $NF}')
        
        # Get best chi2 for this chain
        BEST_CHI2=$(awk 'NR>1 && NF>0 {if ($NF < min_chi2 || NR==2) min_chi2=$NF} END{print min_chi2}' "${CHAIN_FILE}")
        
        # Update global best
        if (( $(echo "${BEST_CHI2} < ${GLOBAL_BEST_CHI2}" | bc -l) )); then
            GLOBAL_BEST_CHI2="${BEST_CHI2}"
        fi
        
        echo "Chain ${i}: ${SAMPLE_COUNT} samples"
        printf "  theta_i: %.4f\n" "${LAST_THETA}"
        printf "  beta:    %.5f\n" "${LAST_BETA}"
        printf "  chi2:    %.2f (Best: %.2f)\n" "${LAST_CHI2}" "${BEST_CHI2}"
        echo ""
        
        # Collect all samples for summary stats
        ALL_THETA+=($(awk 'NR>1 && NF>0 {print $3}' "${CHAIN_FILE}"))
        ALL_BETA+=($(awk 'NR>1 && NF>0 {print $4}' "${CHAIN_FILE}"))
    else
        echo "Chain ${i}: No samples yet"
        echo ""
    fi
done

echo "----------------------------------------------------------------------"
echo "SUMMARY"
echo "----------------------------------------------------------------------"
echo "Total Samples: ${TOTAL_SAMPLES}"

if [ ${#ALL_THETA[@]} -gt 0 ]; then
    # Calculate mean and std for theta_i
    THETA_MEAN=$(printf '%s\n' "${ALL_THETA[@]}" | awk '{sum+=$1; count++} END {print sum/count}')
    THETA_STD=$(printf '%s\n' "${ALL_THETA[@]}" | awk '{sum+=$1; sumsq+=$1*$1; count++} END {print sqrt(sumsq/count - (sum/count)^2)}')
    THETA_MIN=$(printf '%s\n' "${ALL_THETA[@]}" | sort -n | head -1)
    THETA_MAX=$(printf '%s\n' "${ALL_THETA[@]}" | sort -nr | head -1)
    
    printf "theta_i_ridder: %.4f ± %.4f\n" "${THETA_MEAN}" "${THETA_STD}"
    printf "  Range: [%.4f, %.4f]\n" "${THETA_MIN}" "${THETA_MAX}"
    
    # Calculate mean and std for beta
    BETA_MEAN=$(printf '%s\n' "${ALL_BETA[@]}" | awk '{sum+=$1; count++} END {print sum/count}')
    BETA_STD=$(printf '%s\n' "${ALL_BETA[@]}" | awk '{sum+=$1; sumsq+=$1*$1; count++} END {print sqrt(sumsq/count - (sum/count)^2)}')
    
    printf "beta_ridder: %.5f ± %.5f\n" "${BETA_MEAN}" "${BETA_STD}"
    printf "Global Best chi2: %.2f\n" "${GLOBAL_BEST_CHI2}"
fi

echo "======================================================================"

