#!/usr/bin/env bash
set -euo pipefail

# Status checker for Tier 3 parallel MCMC runs
# Usage: ./scripts/tier3_status.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "======================================================================"
echo "TIER 3: PLANCK + BAO + SH0ES STATUS"
echo "======================================================================"
echo ""

NUM_CHAINS=4
TOTAL_SAMPLES=0
GLOBAL_BEST_CHI2=1e30

ALL_THETA_SAMPLES=()
ALL_BETA_SAMPLES=()
ALL_H0_SAMPLES=()

for i in $(seq 1 ${NUM_CHAINS}); do
    CHAIN_WORK_DIR="${ROOT_DIR}/tier3_chain${i}_work"
    CHAIN_OUTPUT_PREFIX="${CHAIN_WORK_DIR}/chains/ridder_tier3_planck_bao_sh0es"
    CHAIN_FILE="${CHAIN_OUTPUT_PREFIX}.1.txt"

    echo "Chain ${i}:"

    if [ -f "${CHAIN_FILE}" ]; then
        SAMPLE_COUNT=$(tail -n +2 "${CHAIN_FILE}" | grep -v '^$' | wc -l | tr -d ' ')
        TOTAL_SAMPLES=$((TOTAL_SAMPLES + SAMPLE_COUNT))

        # Extract last sample's theta_i, beta, H0, and chi2
        LAST_SAMPLE=$(tail -n 1 "${CHAIN_FILE}")
        LAST_THETA=$(echo "${LAST_SAMPLE}" | awk '{print $9}')
        LAST_BETA=$(echo "${LAST_SAMPLE}" | awk '{print $10}')
        LAST_H0=$(echo "${LAST_SAMPLE}" | awk '{print $5}')
        CURRENT_CHI2=$(echo "${LAST_SAMPLE}" | awk '{print $NF}')

        # Get best chi2 for this chain
        BEST_CHI2_CHAIN=$(awk 'NR>1 && NF>0 {if ($NF < min_chi2 || NR==2) min_chi2=$NF} END{print min_chi2}' "${CHAIN_FILE}")
        
        if (( $(echo "${BEST_CHI2_CHAIN} < ${GLOBAL_BEST_CHI2}" | bc -l) )); then
            GLOBAL_BEST_CHI2="${BEST_CHI2_CHAIN}"
        fi

        echo "  Samples: ${SAMPLE_COUNT}"
        echo "  theta_i: ${LAST_THETA:0:6}"
        echo "  beta:    ${LAST_BETA:0:7}"
        echo "  H0:      ${LAST_H0:0:6}"
        echo "  chi2:    ${CURRENT_CHI2:0:7} (Best: ${BEST_CHI2_CHAIN:0:7})"

        # Collect samples for stats
        CHAIN_THETA_SAMPLES=$(awk 'NR>1 {print $9}' "${CHAIN_FILE}")
        CHAIN_BETA_SAMPLES=$(awk 'NR>1 {print $10}' "${CHAIN_FILE}")
        CHAIN_H0_SAMPLES=$(awk 'NR>1 {print $5}' "${CHAIN_FILE}")
        ALL_THETA_SAMPLES+=(${CHAIN_THETA_SAMPLES})
        ALL_BETA_SAMPLES+=(${CHAIN_BETA_SAMPLES})
        ALL_H0_SAMPLES+=(${CHAIN_H0_SAMPLES})
    else
        echo "  No chain file yet."
    fi
    echo ""
done

echo "----------------------------------------------------------------------"
echo "SUMMARY"
echo "----------------------------------------------------------------------"
echo "Total Samples: ${TOTAL_SAMPLES}"

if [ ${#ALL_THETA_SAMPLES[@]} -gt 0 ]; then
    THETA_MEAN=$(echo "${ALL_THETA_SAMPLES[@]}" | tr ' ' '\n' | awk '{sum+=$1; count++} END {print sum/count}')
    THETA_STD=$(echo "${ALL_THETA_SAMPLES[@]}" | tr ' ' '\n' | awk '{sum+=$1; sumsq+=$1*$1; count++} END {print sqrt(sumsq/count - (sum/count)^2)}')
    THETA_MIN=$(echo "${ALL_THETA_SAMPLES[@]}" | tr ' ' '\n' | sort -n | head -1)
    THETA_MAX=$(echo "${ALL_THETA_SAMPLES[@]}" | tr ' ' '\n' | sort -nr | head -1)
    echo "theta_i_ridder: ${THETA_MEAN:0:6} ± ${THETA_STD:0:6}"
    echo "  Range: [${THETA_MIN:0:6}, ${THETA_MAX:0:6}]"
fi

if [ ${#ALL_BETA_SAMPLES[@]} -gt 0 ]; then
    BETA_MEAN=$(echo "${ALL_BETA_SAMPLES[@]}" | tr ' ' '\n' | awk '{sum+=$1; count++} END {print sum/count}')
    BETA_STD=$(echo "${ALL_BETA_SAMPLES[@]}" | tr ' ' '\n' | awk '{sum+=$1; sumsq+=$1*$1; count++} END {print sqrt(sumsq/count - (sum/count)^2)}')
    echo "beta_ridder: ${BETA_MEAN:0:7} ± ${BETA_STD:0:7}"
fi

if [ ${#ALL_H0_SAMPLES[@]} -gt 0 ]; then
    H0_MEAN=$(echo "${ALL_H0_SAMPLES[@]}" | tr ' ' '\n' | awk '{sum+=$1; count++} END {print sum/count}')
    H0_STD=$(echo "${ALL_H0_SAMPLES[@]}" | tr ' ' '\n' | awk '{sum+=$1; sumsq+=$1*$1; count++} END {print sqrt(sumsq/count - (sum/count)^2)}')
    echo "H0: ${H0_MEAN:0:6} ± ${H0_STD:0:6}"
fi

echo ""
echo "Best chi2: ${GLOBAL_BEST_CHI2:0:7}"
echo ""
echo "PREDICTION: If SH0ES pulls theta_i > 1.5, the Ridder field is active!"
echo "======================================================================"

