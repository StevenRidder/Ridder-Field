#!/bin/bash
# Monitor Tier 1 Production Run: 8 Ridder + 2 ΛCDM chains
# Shows progress, parameter values, and chi2 for all chains

CHAINS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../chains"

echo "============================================================"
echo "TIER 1 PRODUCTION STATUS - V1 PUBLICATION"
echo "Target: 5000 samples per chain | 8 Ridder + 2 ΛCDM"
echo "============================================================"
echo ""

# Function to parse chain file
parse_chain() {
    local chain_file=$1
    local chain_name=$2
    local is_lcdm=$3
    
    if [ ! -f "$chain_file" ]; then
        echo "[$chain_name] NOT STARTED"
        return
    fi
    
    # Count samples (excluding header lines starting with #)
    local samples=$(grep -v '^#' "$chain_file" | wc -l | tr -d ' ')
    
    if [ "$samples" -eq 0 ]; then
        echo "[$chain_name] INITIALIZING (0 samples)"
        return
    fi
    
    # Get last 10 lines for statistics
    local last_lines=$(tail -n 10 "$chain_file" | grep -v '^#')
    
    if [ "$is_lcdm" = "true" ]; then
        # ΛCDM: columns are weight, -logpost, H0, omega_b, omega_cdm, n_s, tau_reio, A_s, chi2_*
        # H0 is column 3, chi2 total is last column before derived params
        local h0_vals=$(echo "$last_lines" | awk '{print $3}')
        local chi2_vals=$(echo "$last_lines" | awk '{print $13}')  # Adjust based on actual column
        
        local h0_mean=$(echo "$h0_vals" | awk '{sum+=$1; count++} END {if(count>0) printf "%.2f", sum/count; else print "N/A"}')
        local chi2_mean=$(echo "$chi2_vals" | awk '{sum+=$1; count++} END {if(count>0) printf "%.1f", sum/count; else print "N/A"}')
        local chi2_best=$(echo "$chi2_vals" | awk 'NR==1 || $1<min {min=$1} END {if(NR>0) printf "%.1f", min; else print "N/A"}')
        
        echo "[$chain_name] $samples/5000 samples | H0=$h0_mean | χ²=$chi2_mean (best: $chi2_best)"
    else
        # Ridder: columns include theta_i_ridder (col 9), beta_ridder (col 10), H0 (col 3)
        # chi2 total is column 37
        local theta_vals=$(echo "$last_lines" | awk '{print $9}')
        local beta_vals=$(echo "$last_lines" | awk '{print $10}')
        local h0_vals=$(echo "$last_lines" | awk '{print $3}')
        local chi2_vals=$(echo "$last_lines" | awk '{print $37}')
        
        local theta_mean=$(echo "$theta_vals" | awk '{sum+=$1; count++} END {if(count>0) printf "%.3f", sum/count; else print "N/A"}')
        local beta_mean=$(echo "$beta_vals" | awk '{sum+=$1; count++} END {if(count>0) printf "%.4f", sum/count; else print "N/A"}')
        local h0_mean=$(echo "$h0_vals" | awk '{sum+=$1; count++} END {if(count>0) printf "%.2f", sum/count; else print "N/A"}')
        local chi2_mean=$(echo "$chi2_vals" | awk '{sum+=$1; count++} END {if(count>0) printf "%.1f", sum/count; else print "N/A"}')
        local chi2_best=$(echo "$chi2_vals" | awk 'NR==1 || $1<min {min=$1} END {if(NR>0) printf "%.1f", min; else print "N/A"}')
        
        echo "[$chain_name] $samples/5000 | θᵢ=$theta_mean | β=$beta_mean | H0=$h0_mean | χ²=$chi2_mean (best: $chi2_best)"
    fi
}

# Monitor 8 Ridder chains
echo "RIDDER FIELD CHAINS:"
echo "------------------------------------------------------------"
for i in {1..8}; do
    chain_file="$CHAINS_DIR/ridder_tier1_production_chain${i}.1.txt"
    parse_chain "$chain_file" "Ridder-${i}" "false"
done

echo ""
echo "ΛCDM BASELINE CHAINS:"
echo "------------------------------------------------------------"
for i in {1..2}; do
    chain_file="$CHAINS_DIR/lcdm_production_chain${i}.1.txt"
    parse_chain "$chain_file" "ΛCDM-${i}" "true"
done

echo ""
echo "============================================================"

# Calculate total progress
total_samples=0
for i in {1..8}; do
    chain_file="$CHAINS_DIR/ridder_tier1_production_chain${i}.1.txt"
    if [ -f "$chain_file" ]; then
        samples=$(grep -v '^#' "$chain_file" | wc -l | tr -d ' ')
        total_samples=$((total_samples + samples))
    fi
done
for i in {1..2}; do
    chain_file="$CHAINS_DIR/lcdm_production_chain${i}.1.txt"
    if [ -f "$chain_file" ]; then
        samples=$(grep -v '^#' "$chain_file" | wc -l | tr -d ' ')
        total_samples=$((total_samples + samples))
    fi
done

target_samples=$((5000 * 10))
progress_pct=$(echo "scale=1; $total_samples * 100 / $target_samples" | bc -l)

echo "TOTAL PROGRESS: $total_samples / $target_samples samples ($progress_pct%)"
echo "============================================================"
echo ""
echo "Refresh: watch -n 60 ./tier1_production_status.sh"
echo ""
