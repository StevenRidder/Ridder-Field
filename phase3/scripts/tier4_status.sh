#!/usr/bin/env bash
set -euo pipefail

CHAIN_DIR="/home/ridderadmin/Ridder-Field/phase3/chains"

echo "======================================================================"
echo "TIER 4 PRODUCTION: PROGRESS REPORT"
echo "======================================================================"
echo ""

GLOBAL_BEST_CHI2=999999999
RIDDER_TOTAL_SAMPLES=0

# Arrays for computing "global" averages
declare -a RIDDER_H0_VALUES=()
declare -a RIDDER_THETA_VALUES=()
declare -a RIDDER_BETA_VALUES=()
declare -a RIDDER_CHI2_VALUES=()

echo "RIDDER FIELD CHAINS:"
echo "----------------------------------------------------------------------"

# Loop through 4 Ridder chains
for CHAIN_NUM in 1 2 3 4; do
    CHAIN_FILE="${CHAIN_DIR}/ridder_tier4_prod_chain${CHAIN_NUM}.1.txt"
    
    if [ ! -f "${CHAIN_FILE}" ]; then
        echo "Chain ${CHAIN_NUM}: NOT FOUND"
        continue
    fi
    
    SAMPLE_COUNT=$(tail -n +2 "${CHAIN_FILE}" | grep -v '^$' | wc -l | tr -d ' ')
    RIDDER_TOTAL_SAMPLES=$((RIDDER_TOTAL_SAMPLES + SAMPLE_COUNT))
    
    LAST_LINE=$(tail -1 "${CHAIN_FILE}")
    LAST_H0=$(echo "${LAST_LINE}"    | awk '{print $5}')
    LAST_THETA=$(echo "${LAST_LINE}" | awk '{print $9}')
    LAST_BETA=$(echo "${LAST_LINE}"  | awk '{print $10}')
    LAST_CHI2=$(echo "${LAST_LINE}"  | awk '{print $17}')
    
    BEST_CHI2=$(awk 'NR>1 && NF>0 {if ($17 < min_chi2 || NR==2) min_chi2=$17} END{printf "%.2f", min_chi2}' "${CHAIN_FILE}")
    
    # Use last 50% of samples
    HALF_SAMPLES=$((SAMPLE_COUNT / 2))
    if [ ${HALF_SAMPLES} -gt 0 ]; then
        AVG_H0=$(tail -n ${HALF_SAMPLES} "${CHAIN_FILE}"   | awk '{sum+=$5;  n++} END{if(n>0) printf "%.2f", sum/n; else print "N/A"}')
        AVG_THETA=$(tail -n ${HALF_SAMPLES} "${CHAIN_FILE}"| awk '{sum+=$9;  n++} END{if(n>0) printf "%.4f", sum/n; else print "N/A"}')
        AVG_BETA=$(tail -n ${HALF_SAMPLES} "${CHAIN_FILE}" | awk '{sum+=$10; n++} END{if(n>0) printf "%.5f", sum/n; else print "N/A"}')
        AVG_CHI2=$(tail -n ${HALF_SAMPLES} "${CHAIN_FILE}" | awk '{sum+=$17; n++} END{if(n>0) printf "%.2f", sum/n; else print "N/A"}')
        
        if [ "${AVG_H0}" != "N/A" ]; then
            RIDDER_H0_VALUES+=("${AVG_H0}")
            RIDDER_THETA_VALUES+=("${AVG_THETA}")
            RIDDER_BETA_VALUES+=("${AVG_BETA}")
            RIDDER_CHI2_VALUES+=("${AVG_CHI2}")
        fi
    else
        AVG_H0="N/A"
        AVG_THETA="N/A"
        AVG_BETA="N/A"
        AVG_CHI2="N/A"
    fi
    
    if (( $(echo "${BEST_CHI2} < ${GLOBAL_BEST_CHI2}" | bc -l) )); then
        GLOBAL_BEST_CHI2="${BEST_CHI2}"
    fi
    
    echo "Chain ${CHAIN_NUM}: ${SAMPLE_COUNT} samples"
    printf "  Current: H0=%.2f  theta_i=%.4f  beta=%.5f  chi2=%.2f\n" "${LAST_H0}" "${LAST_THETA}" "${LAST_BETA}" "${LAST_CHI2}"
    if [ "${AVG_H0}" != "N/A" ]; then
        printf "  Average: H0=%s  theta_i=%s  beta=%s  chi2=%s (Best: %.2f)\n" "${AVG_H0}" "${AVG_THETA}" "${AVG_BETA}" "${AVG_CHI2}" "${BEST_CHI2}"
    fi
    echo ""
done

echo "======================================================================"
echo "GLOBAL STATISTICS (averaged across chains)"
echo "======================================================================"

if [ ${#RIDDER_H0_VALUES[@]} -gt 0 ]; then
    RIDDER_H0_MEAN=$(printf "%s\n" "${RIDDER_H0_VALUES[@]}"     | awk '{sum+=$1; n++} END{printf "%.2f", sum/n}')
    RIDDER_H0_STD=$(printf "%s\n"  "${RIDDER_H0_VALUES[@]}"     | awk -v mean="${RIDDER_H0_MEAN}" '{sum+=($1-mean)*($1-mean); n++} END{if(n>1) printf "%.2f", sqrt(sum/(n-1)); else print "0.00"}')
    
    RIDDER_THETA_MEAN=$(printf "%s\n" "${RIDDER_THETA_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.4f", sum/n}')
    RIDDER_THETA_STD=$(printf "%s\n"  "${RIDDER_THETA_VALUES[@]}" | awk -v mean="${RIDDER_THETA_MEAN}" '{sum+=($1-mean)*($1-mean); n++} END{if(n>1) printf "%.4f", sqrt(sum/(n-1)); else print "0.0000"}')
    
    RIDDER_BETA_MEAN=$(printf "%s\n" "${RIDDER_BETA_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.5f", sum/n}')
    RIDDER_BETA_STD=$(printf "%s\n"  "${RIDDER_BETA_VALUES[@]}" | awk -v mean="${RIDDER_BETA_MEAN}" '{sum+=($1-mean)*($1-mean); n++} END{if(n>1) printf "%.5f", sqrt(sum/(n-1)); else print "0.00000"}')
    
    RIDDER_CHI2_MEAN=$(printf "%s\n" "${RIDDER_CHI2_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.2f", sum/n}')
    RIDDER_CHI2_STD=$(printf "%s\n"  "${RIDDER_CHI2_VALUES[@]}" | awk -v mean="${RIDDER_CHI2_MEAN}" '{sum+=($1-mean)*($1-mean); n++} END{if(n>1) printf "%.2f", sqrt(sum/(n-1)); else print "0.00"}')
    
    echo "RIDDER FIELD (${#RIDDER_H0_VALUES[@]} chains):"
    printf "  H₀       = %s ± %s km/s/Mpc\n" "${RIDDER_H0_MEAN}" "${RIDDER_H0_STD}"
    printf "  θᵢ       = %s ± %s\n" "${RIDDER_THETA_MEAN}" "${RIDDER_THETA_STD}"
    printf "  β        = %s ± %s\n" "${RIDDER_BETA_MEAN}" "${RIDDER_BETA_STD}"
    printf "  χ²       = %s ± %s\n" "${RIDDER_CHI2_MEAN}" "${RIDDER_CHI2_STD}"
    echo ""
fi

echo "----------------------------------------------------------------------"
echo "SUMMARY"
echo "----------------------------------------------------------------------"
echo "Ridder Samples: ${RIDDER_TOTAL_SAMPLES}"
printf "Global Best χ²: %.2f\n" "${GLOBAL_BEST_CHI2}"
echo "==================================================================="
