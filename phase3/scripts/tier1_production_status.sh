#!/bin/bash
# Monitor Tier 1 Production Run: 8 Ridder + 2 ΛCDM chains

CHAINS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../chains"

echo "=========================================="
echo "TIER 1 PRODUCTION STATUS"
echo "Target: 5000 samples per chain"
echo "Time: $(date)"
echo "=========================================="

# Function to parse chain file
parse_chain() {
    local chain_file=$1
    local chain_name=$2
    local is_lcdm=$3
    
    if [[ ! -f "$chain_file" ]]; then
        echo "  ${chain_name}: NOT STARTED"
        return
    fi
    
    # Count samples (skip header lines starting with #)
    local samples=$(grep -v '^#' "$chain_file" | wc -l | tr -d ' ')
    
    if [[ $samples -eq 0 ]]; then
        echo "  ${chain_name}: INITIALIZING (0 samples)"
        return
    fi
    
    # Get last line of data
    local last_line=$(grep -v '^#' "$chain_file" | tail -1)
    
    if [[ -z "$last_line" ]]; then
        echo "  ${chain_name}: INITIALIZING (0 samples)"
        return
    fi
    
    # Parse parameters based on chain type
    if [[ "$is_lcdm" == "true" ]]; then
        # ΛCDM: weight H0 omega_b omega_cdm n_s tau logA ... chi2
        local h0=$(echo $last_line | awk '{print $2}')
        local omega_cdm=$(echo $last_line | awk '{print $4}')
        local chi2=$(echo $last_line | awk '{print $31}')
    else
        # Ridder: weight H0 omega_b omega_cdm n_s tau logA theta_i beta ... chi2
        local h0=$(echo $last_line | awk '{print $2}')
        local theta_i=$(echo $last_line | awk '{print $9}')
        local beta=$(echo $last_line | awk '{print $10}')
        local chi2=$(echo $last_line | awk '{print $37}')
    fi
    
    # Calculate progress
    local progress=$((samples * 100 / 5000))
    
    # Format output
    if [[ "$is_lcdm" == "true" ]]; then
        printf "  %-20s: %4d/5000 (%3d%%) | H0=%6.2f | Ωc=%6.4f | χ²=%7.1f\n" \
            "$chain_name" $samples $progress $h0 $omega_cdm $chi2
    else
        printf "  %-20s: %4d/5000 (%3d%%) | H0=%6.2f | θ=%5.3f | β=%6.4f | χ²=%7.1f\n" \
            "$chain_name" $samples $progress $h0 $theta_i $beta $chi2
    fi
}

echo ""
echo "RIDDER FIELD CHAINS (8):"
echo "----------------------------------------"
for i in {1..8}; do
    WORK_DIR="$CHAINS_DIR/ridder_prod_chain${i}_work"
    CHAIN_FILE="$WORK_DIR/ridder_tier1_production_chain${i}.1.txt"
    parse_chain "$CHAIN_FILE" "Ridder Chain ${i}" "false"
done

echo ""
echo "ΛCDM BASELINE CHAINS (2):"
echo "----------------------------------------"
for i in {1..2}; do
    WORK_DIR="$CHAINS_DIR/lcdm_prod_chain${i}_work"
    CHAIN_FILE="$WORK_DIR/lcdm_production_chain${i}.1.txt"
    parse_chain "$CHAIN_FILE" "ΛCDM Chain ${i}" "true"
done

echo ""
echo "=========================================="

# Calculate statistics across Ridder chains
echo ""
echo "RIDDER CHAINS STATISTICS:"
echo "----------------------------------------"

# Collect all Ridder chain data
ridder_samples=0
ridder_h0_sum=0
ridder_theta_sum=0
ridder_beta_sum=0
ridder_chi2_sum=0
ridder_count=0

for i in {1..8}; do
    WORK_DIR="$CHAINS_DIR/ridder_prod_chain${i}_work"
    CHAIN_FILE="$WORK_DIR/ridder_tier1_production_chain${i}.1.txt"
    
    if [[ -f "$CHAIN_FILE" ]]; then
        local samples=$(grep -v '^#' "$CHAIN_FILE" | wc -l | tr -d ' ')
        if [[ $samples -gt 0 ]]; then
            ridder_samples=$((ridder_samples + samples))
            
            # Get last values
            local last_line=$(grep -v '^#' "$CHAIN_FILE" | tail -1)
            local h0=$(echo $last_line | awk '{print $2}')
            local theta_i=$(echo $last_line | awk '{print $9}')
            local beta=$(echo $last_line | awk '{print $10}')
            local chi2=$(echo $last_line | awk '{print $37}')
            
            ridder_h0_sum=$(echo "$ridder_h0_sum + $h0" | bc -l)
            ridder_theta_sum=$(echo "$ridder_theta_sum + $theta_i" | bc -l)
            ridder_beta_sum=$(echo "$ridder_beta_sum + $beta" | bc -l)
            ridder_chi2_sum=$(echo "$ridder_chi2_sum + $chi2" | bc -l)
            ridder_count=$((ridder_count + 1))
        fi
    fi
done

if [[ $ridder_count -gt 0 ]]; then
    ridder_h0_avg=$(echo "scale=2; $ridder_h0_sum / $ridder_count" | bc -l)
    ridder_theta_avg=$(echo "scale=3; $ridder_theta_sum / $ridder_count" | bc -l)
    ridder_beta_avg=$(echo "scale=4; $ridder_beta_sum / $ridder_count" | bc -l)
    ridder_chi2_avg=$(echo "scale=1; $ridder_chi2_sum / $ridder_count" | bc -l)
    
    echo "Total samples: $ridder_samples / 40000 ($(( ridder_samples * 100 / 40000 ))%)"
    echo "Average H0: $ridder_h0_avg km/s/Mpc"
    echo "Average θᵢ: $ridder_theta_avg"
    echo "Average β: $ridder_beta_avg"
    echo "Average χ²: $ridder_chi2_avg"
else
    echo "No Ridder chains started yet"
fi

# Calculate statistics across ΛCDM chains
echo ""
echo "ΛCDM BASELINE STATISTICS:"
echo "----------------------------------------"

lcdm_samples=0
lcdm_h0_sum=0
lcdm_chi2_sum=0
lcdm_count=0

for i in {1..2}; do
    WORK_DIR="$CHAINS_DIR/lcdm_prod_chain${i}_work"
    CHAIN_FILE="$WORK_DIR/lcdm_production_chain${i}.1.txt"
    
    if [[ -f "$CHAIN_FILE" ]]; then
        local samples=$(grep -v '^#' "$CHAIN_FILE" | wc -l | tr -d ' ')
        if [[ $samples -gt 0 ]]; then
            lcdm_samples=$((lcdm_samples + samples))
            
            # Get last values
            local last_line=$(grep -v '^#' "$CHAIN_FILE" | tail -1)
            local h0=$(echo $last_line | awk '{print $2}')
            local chi2=$(echo $last_line | awk '{print $31}')
            
            lcdm_h0_sum=$(echo "$lcdm_h0_sum + $h0" | bc -l)
            lcdm_chi2_sum=$(echo "$lcdm_chi2_sum + $chi2" | bc -l)
            lcdm_count=$((lcdm_count + 1))
        fi
    fi
done

if [[ $lcdm_count -gt 0 ]]; then
    lcdm_h0_avg=$(echo "scale=2; $lcdm_h0_sum / $lcdm_count" | bc -l)
    lcdm_chi2_avg=$(echo "scale=1; $lcdm_chi2_sum / $lcdm_count" | bc -l)
    
    echo "Total samples: $lcdm_samples / 10000 ($(( lcdm_samples * 100 / 10000 ))%)"
    echo "Average H0: $lcdm_h0_avg km/s/Mpc"
    echo "Average χ²: $lcdm_chi2_avg"
else
    echo "No ΛCDM chains started yet"
fi

# Comparison
if [[ $ridder_count -gt 0 ]] && [[ $lcdm_count -gt 0 ]]; then
    echo ""
    echo "COMPARISON:"
    echo "----------------------------------------"
    delta_h0=$(echo "scale=2; $ridder_h0_avg - $lcdm_h0_avg" | bc -l)
    delta_chi2=$(echo "scale=1; $ridder_chi2_avg - $lcdm_chi2_avg" | bc -l)
    
    echo "ΔH0 (Ridder - ΛCDM): $delta_h0 km/s/Mpc"
    echo "Δχ² (Ridder - ΛCDM): $delta_chi2"
    
    # Check if improvement
    if (( $(echo "$delta_chi2 < -2.0" | bc -l) )); then
        echo "Status: Ridder model IMPROVING fit (Δχ² < -2)"
    elif (( $(echo "$delta_chi2 > 2.0" | bc -l) )); then
        echo "Status: ΛCDM model preferred (Δχ² > +2)"
    else
        echo "Status: Models statistically equivalent"
    fi
fi

echo ""
echo "=========================================="
echo "Refresh: watch -n 60 ./tier1_production_status.sh"
echo "=========================================="

