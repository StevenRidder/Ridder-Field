#!/bin/bash
# Tier 4 Status Monitor
# Shows real-time MCMC progress for Australia East VM

echo "========================================================================"
echo "TIER 4 STATUS: Australia East VM (F8s_v2)"
echo "========================================================================"
echo ""

CHAIN_DIR="/home/ridderadmin/Ridder-Field/phase3/chains"
# Main Tier 4 chain (Grand Slam run)
CHAIN_FILE="$CHAIN_DIR/ridder_tier4_grand_slam.1.txt"

# Check if chain file exists
if [ ! -f "$CHAIN_FILE" ]; then
    echo "❌ Chain file not found. MCMC may not have started yet."
    echo ""
    echo "Checking process status..."
    ps aux | grep cobaya-run | grep -v grep || echo "No cobaya-run process found."
    exit 1
fi

# Get total samples
TOTAL_SAMPLES=$(wc -l < "$CHAIN_FILE")
TOTAL_SAMPLES=$((TOTAL_SAMPLES - 1))  # Subtract header line

echo "📊 Total Samples: $TOTAL_SAMPLES"
echo ""

# Get last 20 samples and analyze
echo "Recent Parameter Evolution (Last 20 samples):"
echo "------------------------------------------------------------------------"
tail -20 "$CHAIN_FILE" | awk 'NR>1 {
    printf "Sample %4d: theta_i=%5.3f  beta=%6.4f  H0=%5.2f  chi2=%7.1f\n",
           NR-1, $9, $10, $5, $17
}'

echo ""
echo "------------------------------------------------------------------------"

# Calculate statistics from last 50 samples
echo "Statistics (Last 50 samples):"
echo "------------------------------------------------------------------------"
tail -50 "$CHAIN_FILE" | awk '
BEGIN {
    min_theta = 999; max_theta = 0; sum_theta = 0;
    min_beta = 999; max_beta = 0; sum_beta = 0;
    min_H0 = 999; max_H0 = 0; sum_H0 = 0;
    min_chi2 = 999999; max_chi2 = 0; sum_chi2 = 0;
    count = 0;
}
{
    theta = \$9; beta = \$10; H0 = \$5; chi2 = \$17;
    
    if (theta < min_theta) min_theta = theta;
    if (theta > max_theta) max_theta = theta;
    sum_theta += theta;
    
    if (beta < min_beta) min_beta = beta;
    if (beta > max_beta) max_beta = beta;
    sum_beta += beta;
    
    if (H0 < min_H0) min_H0 = H0;
    if (H0 > max_H0) max_H0 = H0;
    sum_H0 += H0;
    
    if (chi2 < min_chi2) min_chi2 = chi2;
    if (chi2 > max_chi2) max_chi2 = chi2;
    sum_chi2 += chi2;
    
    count++;
}
END {
    printf \"theta_i: mean=%.3f  min=%.3f  max=%.3f  range=%.3f\\n\", 
           sum_theta/count, min_theta, max_theta, max_theta-min_theta;
    printf \"beta:    mean=%.4f  min=%.4f  max=%.4f  range=%.4f\\n\", 
           sum_beta/count, min_beta, max_beta, max_beta-min_beta;
    printf \"H0:      mean=%.2f  min=%.2f  max=%.2f  range=%.2f\\n\", 
           sum_H0/count, min_H0, max_H0, max_H0-min_H0;
    printf \"chi2:    mean=%.1f  min=%.1f  max=%.1f  range=%.1f\\n\", 
           sum_chi2/count, min_chi2, max_chi2, max_chi2-min_chi2;
}
'

echo "------------------------------------------------------------------------"
echo ""

# Check if still running
if ps aux | grep -q '[c]obaya-run'; then
    echo "✅ Status: RUNNING"
else
    echo "⚠️  Status: STOPPED"
    echo ""
    echo "Last 10 lines of log:"
    tail -10 /home/ridderadmin/Ridder-Field/phase3/tier4_full.log 2>/dev/null | grep -v '^DEBUG:' | grep -v '^BG_FUNC:' | grep -v '^RIDDER'
fi

echo ""
echo "========================================================================"

