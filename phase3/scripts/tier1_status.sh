#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NUM_CHAINS=4

echo "======================================================================"
echo "TIER 1 PLANCK: PROGRESS REPORT"
echo "======================================================================"
echo ""

ALL_THETA=()
ALL_BETA=()
TOTAL_SAMPLES=0
GLOBAL_BEST_CHI2=999999999

for i in $(seq 1 ${NUM_CHAINS}); do
    CHAIN_FILE="${ROOT_DIR}/chain${i}_work/chains/ridder_tier1_planck.1.txt"
    
    if [ -f "${CHAIN_FILE}" ]; then
        SAMPLE_COUNT=$(tail -n +2 "${CHAIN_FILE}" | grep -v '^$' | wc -l | tr -d ' ')
        TOTAL_SAMPLES=$((TOTAL_SAMPLES + SAMPLE_COUNT))
        
        # Column 9 = theta_i_ridder, Column 10 = beta_ridder, Column 37 = total chi2
        LAST_LINE=$(tail -1 "${CHAIN_FILE}")
        LAST_THETA=$(echo "${LAST_LINE}" | awk '{print $9}')
        LAST_BETA=$(echo "${LAST_LINE}" | awk '{print $10}')
        LAST_CHI2=$(echo "${LAST_LINE}" | awk '{print $37}')
        
        BEST_CHI2=$(awk 'NR>1 && NF>0 {if ($37 < min_chi2 || NR==2) min_chi2=$37} END{printf "%.2f", min_chi2}' "${CHAIN_FILE}")
        
        IS_BETTER=$(awk -v best="${BEST_CHI2}" -v global="${GLOBAL_BEST_CHI2}" 'BEGIN {print (best < global ? 1 : 0)}')
        if [ "${IS_BETTER}" = "1" ]; then
            GLOBAL_BEST_CHI2="${BEST_CHI2}"
        fi
        
        echo "Chain ${i}: ${SAMPLE_COUNT} samples"
        printf "  theta_i: %.4f\n" "${LAST_THETA}"
        printf "  beta:    %.5f\n" "${LAST_BETA}"
        printf "  chi2:    %.2f (Best: %.2f)\n" "${LAST_CHI2}" "${BEST_CHI2}"
        echo ""
        
        ALL_THETA+=($(awk 'NR>1 && NF>0 {print $9}' "${CHAIN_FILE}"))
        ALL_BETA+=($(awk 'NR>1 && NF>0 {print $10}' "${CHAIN_FILE}"))
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
    THETA_MEAN=$(printf '%s\n' "${ALL_THETA[@]}" | awk '{sum+=$1; count++} END {printf "%.4f", sum/count}')
    THETA_STD=$(printf '%s\n' "${ALL_THETA[@]}" | awk '{sum+=$1; sumsq+=$1*$1; count++} END {printf "%.4f", sqrt(sumsq/count - (sum/count)^2)}')
    THETA_MIN=$(printf '%s\n' "${ALL_THETA[@]}" | sort -n | head -1)
    THETA_MAX=$(printf '%s\n' "${ALL_THETA[@]}" | sort -nr | head -1)
    
    echo "theta_i_ridder: ${THETA_MEAN} ± ${THETA_STD}"
    printf "  Range: [%.4f, %.4f]\n" "${THETA_MIN}" "${THETA_MAX}"
    
    BETA_MEAN=$(printf '%s\n' "${ALL_BETA[@]}" | awk '{sum+=$1; count++} END {printf "%.5f", sum/count}')
    BETA_STD=$(printf '%s\n' "${ALL_BETA[@]}" | awk '{sum+=$1; sumsq+=$1*$1; count++} END {printf "%.5f", sqrt(sumsq/count - (sum/count)^2)}')
    
    echo "beta_ridder: ${BETA_MEAN} ± ${BETA_STD}"
    printf "Global Best chi2: %.2f\n" "${GLOBAL_BEST_CHI2}"
fi

echo "======================================================================"
