#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../chains" && pwd)"
NUM_RIDDER_CHAINS=2
NUM_LCDM_CHAINS=1

echo "======================================================================"
echo "TIER 2 TEST: PROGRESS REPORT (Planck + BAO)"
echo "======================================================================"
echo ""

GLOBAL_BEST_CHI2=999999999
RIDDER_TOTAL_SAMPLES=0
LCDM_TOTAL_SAMPLES=0

declare -a RIDDER_H0_VALUES=()
declare -a RIDDER_THETA_VALUES=()
declare -a RIDDER_BETA_VALUES=()
declare -a RIDDER_CHI2_VALUES=()
declare -a LCDM_H0_VALUES=()
declare -a LCDM_CHI2_VALUES=()

echo "RIDDER FIELD CHAINS:"
echo "----------------------------------------------------------------------"
for i in $(seq 1 ${NUM_RIDDER_CHAINS}); do
    CHAIN_FILE="${ROOT_DIR}/ridder_tier2_test_chain${i}.1.txt"
    
    if [ -f "${CHAIN_FILE}" ]; then
        SAMPLE_COUNT=$(tail -n +2 "${CHAIN_FILE}" | grep -v '^$' | wc -l | tr -d ' ')
        RIDDER_TOTAL_SAMPLES=$((RIDDER_TOTAL_SAMPLES + SAMPLE_COUNT))
        
        LAST_LINE=$(tail -1 "${CHAIN_FILE}")
        LAST_H0=$(echo "${LAST_LINE}" | awk '{print $5}')
        LAST_THETA=$(echo "${LAST_LINE}" | awk '{print $9}')
        LAST_BETA=$(echo "${LAST_LINE}" | awk '{print $10}')
        LAST_CHI2=$(echo "${LAST_LINE}" | awk '{print $38}')
        
        BEST_CHI2=$(awk 'NR>1 && NF>0 {if ($38 < min_chi2 || NR==2) min_chi2=$38} END{printf "%.2f", min_chi2}' "${CHAIN_FILE}")
        
        HALF_SAMPLES=$((SAMPLE_COUNT / 2))
        if [ ${HALF_SAMPLES} -gt 0 ]; then
            AVG_H0=$(tail -n ${HALF_SAMPLES} "${CHAIN_FILE}" | awk '{sum+=$5; n++} END{if(n>0) printf "%.2f", sum/n; else print "N/A"}')
            AVG_THETA=$(tail -n ${HALF_SAMPLES} "${CHAIN_FILE}" | awk '{sum+=$9; n++} END{if(n>0) printf "%.4f", sum/n; else print "N/A"}')
            AVG_BETA=$(tail -n ${HALF_SAMPLES} "${CHAIN_FILE}" | awk '{sum+=$10; n++} END{if(n>0) printf "%.5f", sum/n; else print "N/A"}')
            AVG_CHI2=$(tail -n ${HALF_SAMPLES} "${CHAIN_FILE}" | awk '{sum+=$38; n++} END{if(n>0) printf "%.2f", sum/n; else print "N/A"}')
            
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
        
        IS_BETTER=$(awk -v best="${BEST_CHI2}" -v global="${GLOBAL_BEST_CHI2}" 'BEGIN {print (best < global ? 1 : 0)}')
        if [ "${IS_BETTER}" = "1" ]; then
            GLOBAL_BEST_CHI2="${BEST_CHI2}"
        fi
        
        echo "Chain ${i}: ${SAMPLE_COUNT}/200 samples"
        printf "  Current: H0=%.2f  theta_i=%.4f  beta=%.5f  chi2=%.2f\n" "${LAST_H0}" "${LAST_THETA}" "${LAST_BETA}" "${LAST_CHI2}"
        if [ "${AVG_H0}" != "N/A" ]; then
            printf "  Average: H0=%s  theta_i=%s  beta=%s  chi2=%s (Best: %.2f)\n" "${AVG_H0}" "${AVG_THETA}" "${AVG_BETA}" "${AVG_CHI2}" "${BEST_CHI2}"
        fi
        echo ""
    else
        echo "Chain ${i}: No samples yet"
        echo ""
    fi
done

echo "ΛCDM BASELINE CHAIN:"
echo "----------------------------------------------------------------------"
CHAIN_FILE="${ROOT_DIR}/lcdm_tier2_test_chain1.1.txt"

if [ -f "${CHAIN_FILE}" ]; then
    SAMPLE_COUNT=$(tail -n +2 "${CHAIN_FILE}" | grep -v '^$' | wc -l | tr -d ' ')
    LCDM_TOTAL_SAMPLES=${SAMPLE_COUNT}
    
    LAST_LINE=$(tail -1 "${CHAIN_FILE}")
    LAST_H0=$(echo "${LAST_LINE}" | awk '{print $5}')
    LAST_CHI2=$(echo "${LAST_LINE}" | awk '{print $36}')
    
    BEST_CHI2=$(awk 'NR>1 && NF>0 {if ($36 < min_chi2 || NR==2) min_chi2=$36} END{printf "%.2f", min_chi2}' "${CHAIN_FILE}")
    
    HALF_SAMPLES=$((SAMPLE_COUNT / 2))
    if [ ${HALF_SAMPLES} -gt 0 ]; then
        AVG_H0=$(tail -n ${HALF_SAMPLES} "${CHAIN_FILE}" | awk '{sum+=$5; n++} END{if(n>0) printf "%.2f", sum/n; else print "N/A"}')
        AVG_CHI2=$(tail -n ${HALF_SAMPLES} "${CHAIN_FILE}" | awk '{sum+=$36; n++} END{if(n>0) printf "%.2f", sum/n; else print "N/A"}')
        
        if [ "${AVG_H0}" != "N/A" ]; then
            LCDM_H0_VALUES+=("${AVG_H0}")
            LCDM_CHI2_VALUES+=("${AVG_CHI2}")
        fi
    else
        AVG_H0="N/A"
        AVG_CHI2="N/A"
    fi
    
    IS_BETTER=$(awk -v best="${BEST_CHI2}" -v global="${GLOBAL_BEST_CHI2}" 'BEGIN {print (best < global ? 1 : 0)}')
    if [ "${IS_BETTER}" = "1" ]; then
        GLOBAL_BEST_CHI2="${BEST_CHI2}"
    fi
    
    echo "ΛCDM Chain 1: ${SAMPLE_COUNT}/200 samples"
    printf "  Current: H0=%.2f  chi2=%.2f\n" "${LAST_H0}" "${LAST_CHI2}"
    if [ "${AVG_H0}" != "N/A" ]; then
        printf "  Average: H0=%s  chi2=%s (Best: %.2f)\n" "${AVG_H0}" "${AVG_CHI2}" "${BEST_CHI2}"
    fi
    echo ""
else
    echo "ΛCDM Chain 1: No samples yet"
    echo ""
fi

echo "======================================================================"
echo "GLOBAL STATISTICS"
echo "======================================================================"

if [ ${#RIDDER_H0_VALUES[@]} -gt 0 ]; then
    RIDDER_H0_MEAN=$(printf "%s\n" "${RIDDER_H0_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.2f", sum/n}')
    RIDDER_THETA_MEAN=$(printf "%s\n" "${RIDDER_THETA_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.4f", sum/n}')
    RIDDER_BETA_MEAN=$(printf "%s\n" "${RIDDER_BETA_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.5f", sum/n}')
    RIDDER_CHI2_MEAN=$(printf "%s\n" "${RIDDER_CHI2_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.2f", sum/n}')
    
    echo "RIDDER FIELD (${#RIDDER_H0_VALUES[@]} chains):"
    printf "  H₀ = %s km/s/Mpc,  θᵢ = %s,  β = %s,  χ² = %s\n" "${RIDDER_H0_MEAN}" "${RIDDER_THETA_MEAN}" "${RIDDER_BETA_MEAN}" "${RIDDER_CHI2_MEAN}"
    echo ""
fi

if [ ${#LCDM_H0_VALUES[@]} -gt 0 ]; then
    LCDM_H0_MEAN=$(printf "%s\n" "${LCDM_H0_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.2f", sum/n}')
    LCDM_CHI2_MEAN=$(printf "%s\n" "${LCDM_CHI2_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.2f", sum/n}')
    
    echo "ΛCDM BASELINE:"
    printf "  H₀ = %s km/s/Mpc,  χ² = %s\n" "${LCDM_H0_MEAN}" "${LCDM_CHI2_MEAN}"
    echo ""
fi

if [ ${#RIDDER_CHI2_VALUES[@]} -gt 0 ] && [ ${#LCDM_CHI2_VALUES[@]} -gt 0 ]; then
    DELTA_CHI2=$(awk -v r="${RIDDER_CHI2_MEAN}" -v l="${LCDM_CHI2_MEAN}" 'BEGIN{printf "%.2f", r - l}')
    echo "COMPARISON:"
    printf "  Δχ² (Ridder - ΛCDM) = %s\n" "${DELTA_CHI2}"
    echo ""
fi

echo "----------------------------------------------------------------------"
echo "SUMMARY"
echo "----------------------------------------------------------------------"
echo "Ridder Samples: ${RIDDER_TOTAL_SAMPLES}/400 (target)"
echo "ΛCDM Samples: ${LCDM_TOTAL_SAMPLES}/200 (target)"
printf "Global Best χ²: %.2f\n" "${GLOBAL_BEST_CHI2}"
echo "======================================================================"

