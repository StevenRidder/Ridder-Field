#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../chains" && pwd)"
NUM_RIDDER_CHAINS=8
NUM_LCDM_CHAINS=2

echo "======================================================================"
echo "TIER 1 PRODUCTION: PROGRESS REPORT"
echo "======================================================================"
echo ""

GLOBAL_BEST_CHI2=999999999
RIDDER_TOTAL_SAMPLES=0
LCDM_TOTAL_SAMPLES=0

# Arrays for computing averages
declare -a RIDDER_H0_VALUES=()
declare -a RIDDER_THETA_VALUES=()
declare -a RIDDER_BETA_VALUES=()
declare -a RIDDER_CHI2_VALUES=()
declare -a LCDM_H0_VALUES=()
declare -a LCDM_CHI2_VALUES=()

echo "RIDDER FIELD CHAINS:"
echo "----------------------------------------------------------------------"
for i in $(seq 1 ${NUM_RIDDER_CHAINS}); do
    CHAIN_FILE="${ROOT_DIR}/ridder_tier1_production_chain${i}.1.txt"
    
    if [ -f "${CHAIN_FILE}" ]; then
        SAMPLE_COUNT=$(tail -n +2 "${CHAIN_FILE}" | grep -v '^$' | wc -l | tr -d ' ')
        RIDDER_TOTAL_SAMPLES=$((RIDDER_TOTAL_SAMPLES + SAMPLE_COUNT))
        
        LAST_LINE=$(tail -1 "${CHAIN_FILE}")
        LAST_H0=$(echo "${LAST_LINE}" | awk '{print $5}')
        LAST_THETA=$(echo "${LAST_LINE}" | awk '{print $9}')
        LAST_BETA=$(echo "${LAST_LINE}" | awk '{print $10}')
        LAST_CHI2=$(echo "${LAST_LINE}" | awk '{print $38}')
        
        BEST_CHI2=$(awk 'NR>1 && NF>0 {if ($38 < min_chi2 || NR==2) min_chi2=$38} END{printf "%.2f", min_chi2}' "${CHAIN_FILE}")
        
        # Compute chain averages (last 50% of samples for burn-in)
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
        
        echo "Chain ${i}: ${SAMPLE_COUNT} samples"
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

echo "ΛCDM BASELINE CHAINS:"
echo "----------------------------------------------------------------------"
for i in $(seq 1 ${NUM_LCDM_CHAINS}); do
    CHAIN_FILE="${ROOT_DIR}/lcdm_production_chain${i}.1.txt"
    
    if [ -f "${CHAIN_FILE}" ]; then
        SAMPLE_COUNT=$(tail -n +2 "${CHAIN_FILE}" | grep -v '^$' | wc -l | tr -d ' ')
        LCDM_TOTAL_SAMPLES=$((LCDM_TOTAL_SAMPLES + SAMPLE_COUNT))
        
        LAST_LINE=$(tail -1 "${CHAIN_FILE}")
        LAST_H0=$(echo "${LAST_LINE}" | awk '{print $5}')
        LAST_CHI2=$(echo "${LAST_LINE}" | awk '{print $36}')
        
        BEST_CHI2=$(awk 'NR>1 && NF>0 {if ($36 < min_chi2 || NR==2) min_chi2=$36} END{printf "%.2f", min_chi2}' "${CHAIN_FILE}")
        
        # Compute chain averages
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
        
        echo "ΛCDM Chain ${i}: ${SAMPLE_COUNT} samples"
        printf "  Current: H0=%.2f  chi2=%.2f\n" "${LAST_H0}" "${LAST_CHI2}"
        if [ "${AVG_H0}" != "N/A" ]; then
            printf "  Average: H0=%s  chi2=%s (Best: %.2f)\n" "${AVG_H0}" "${AVG_CHI2}" "${BEST_CHI2}"
        fi
        echo ""
    else
        echo "ΛCDM Chain ${i}: No samples yet"
        echo ""
    fi
done

echo "======================================================================"
echo "GLOBAL STATISTICS (averaged across chains)"
echo "======================================================================"

# Compute global averages and standard deviations
if [ ${#RIDDER_H0_VALUES[@]} -gt 0 ]; then
    RIDDER_H0_MEAN=$(printf "%s\n" "${RIDDER_H0_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.2f", sum/n}')
    RIDDER_H0_STD=$(printf "%s\n" "${RIDDER_H0_VALUES[@]}" | awk -v mean="${RIDDER_H0_MEAN}" '{sum+=($1-mean)*($1-mean); n++} END{if(n>1) printf "%.2f", sqrt(sum/(n-1)); else print "0.00"}')
    
    RIDDER_THETA_MEAN=$(printf "%s\n" "${RIDDER_THETA_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.4f", sum/n}')
    RIDDER_THETA_STD=$(printf "%s\n" "${RIDDER_THETA_VALUES[@]}" | awk -v mean="${RIDDER_THETA_MEAN}" '{sum+=($1-mean)*($1-mean); n++} END{if(n>1) printf "%.4f", sqrt(sum/(n-1)); else print "0.0000"}')
    
    RIDDER_BETA_MEAN=$(printf "%s\n" "${RIDDER_BETA_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.5f", sum/n}')
    RIDDER_BETA_STD=$(printf "%s\n" "${RIDDER_BETA_VALUES[@]}" | awk -v mean="${RIDDER_BETA_MEAN}" '{sum+=($1-mean)*($1-mean); n++} END{if(n>1) printf "%.5f", sqrt(sum/(n-1)); else print "0.00000"}')
    
    RIDDER_CHI2_MEAN=$(printf "%s\n" "${RIDDER_CHI2_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.2f", sum/n}')
    RIDDER_CHI2_STD=$(printf "%s\n" "${RIDDER_CHI2_VALUES[@]}" | awk -v mean="${RIDDER_CHI2_MEAN}" '{sum+=($1-mean)*($1-mean); n++} END{if(n>1) printf "%.2f", sqrt(sum/(n-1)); else print "0.00"}')
    
    echo "RIDDER FIELD (${#RIDDER_H0_VALUES[@]} chains):"
    printf "  H₀       = %s ± %s km/s/Mpc\n" "${RIDDER_H0_MEAN}" "${RIDDER_H0_STD}"
    printf "  θᵢ       = %s ± %s\n" "${RIDDER_THETA_MEAN}" "${RIDDER_THETA_STD}"
    printf "  β        = %s ± %s\n" "${RIDDER_BETA_MEAN}" "${RIDDER_BETA_STD}"
    printf "  χ²       = %s ± %s\n" "${RIDDER_CHI2_MEAN}" "${RIDDER_CHI2_STD}"
    echo ""
fi

if [ ${#LCDM_H0_VALUES[@]} -gt 0 ]; then
    LCDM_H0_MEAN=$(printf "%s\n" "${LCDM_H0_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.2f", sum/n}')
    LCDM_H0_STD=$(printf "%s\n" "${LCDM_H0_VALUES[@]}" | awk -v mean="${LCDM_H0_MEAN}" '{sum+=($1-mean)*($1-mean); n++} END{if(n>1) printf "%.2f", sqrt(sum/(n-1)); else print "0.00"}')
    
    LCDM_CHI2_MEAN=$(printf "%s\n" "${LCDM_CHI2_VALUES[@]}" | awk '{sum+=$1; n++} END{printf "%.2f", sum/n}')
    LCDM_CHI2_STD=$(printf "%s\n" "${LCDM_CHI2_VALUES[@]}" | awk -v mean="${LCDM_CHI2_MEAN}" '{sum+=($1-mean)*($1-mean); n++} END{if(n>1) printf "%.2f", sqrt(sum/(n-1)); else print "0.00"}')
    
    echo "ΛCDM BASELINE (${#LCDM_H0_VALUES[@]} chains):"
    printf "  H₀       = %s ± %s km/s/Mpc\n" "${LCDM_H0_MEAN}" "${LCDM_H0_STD}"
    printf "  χ²       = %s ± %s\n" "${LCDM_CHI2_MEAN}" "${LCDM_CHI2_STD}"
    echo ""
fi

if [ ${#RIDDER_CHI2_VALUES[@]} -gt 0 ] && [ ${#LCDM_CHI2_VALUES[@]} -gt 0 ]; then
    DELTA_CHI2=$(awk -v r="${RIDDER_CHI2_MEAN}" -v l="${LCDM_CHI2_MEAN}" 'BEGIN{printf "%.2f", r - l}')
    echo "COMPARISON:"
    printf "  Δχ² (Ridder - ΛCDM) = %s\n" "${DELTA_CHI2}"
    
    # Use bc for comparison if available, otherwise awk
    if command -v bc >/dev/null 2>&1; then
        if [ $(echo "${DELTA_CHI2} < -2" | bc) -eq 1 ]; then
            echo "  → Ridder field is FAVORED (Δχ² < -2)"
        elif [ $(echo "${DELTA_CHI2} > 2" | bc) -eq 1 ]; then
            echo "  → ΛCDM is FAVORED (Δχ² > 2)"
        else
            echo "  → Models are EQUIVALENT (|Δχ²| < 2)"
        fi
    else
        echo "  → (Install bc for automatic interpretation)"
    fi
    echo ""
fi

echo "----------------------------------------------------------------------"
echo "SUMMARY"
echo "----------------------------------------------------------------------"
echo "Ridder Samples: ${RIDDER_TOTAL_SAMPLES}"
echo "ΛCDM Samples: ${LCDM_TOTAL_SAMPLES}"
printf "Global Best χ²: %.2f\n" "${GLOBAL_BEST_CHI2}"
echo "======================================================================"

