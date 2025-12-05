#!/bin/bash
# Paper 2 Chain Status - Shows ACTUAL stats

echo ""
echo "=============================================="
echo "  PAPER 2 CHAIN STATUS"
echo "  $(date)"
echo "=============================================="

cd ~/Ridder-Field/phase4
source ~/cosmo_env/bin/activate 2>/dev/null

echo ""
echo "=== SYSTEM ==="
echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2 " used"}')"

# Show running processes with runtime
echo ""
echo "=== RUNNING CHAINS ==="
ps -o pid,etime,pcpu,pmem,cmd --no-headers -C python3 2>/dev/null | grep cobaya | while read line; do
    pid=$(echo $line | awk '{print $1}')
    time=$(echo $line | awk '{print $2}')
    cpu=$(echo $line | awk '{print $3}')
    mem=$(echo $line | awk '{print $4}')
    config=$(echo $line | grep -o 'run_[a-z_]*' | head -1)
    echo "  $config: running $time, CPU $cpu%, MEM $mem%"
done
[ $(pgrep -c -f cobaya 2>/dev/null || echo 0) -eq 0 ] && echo "  None running"

for chain in run_control_planck_only run_a_ede_marginalized run_b_lcdm_template; do
    echo ""
    echo "=============================================="
    echo "  $chain"
    echo "=============================================="
    
    # Check if running
    if pgrep -f "$chain" > /dev/null 2>&1; then
        echo "Status: 🟢 RUNNING"
        runtime=$(ps -o etime= -p $(pgrep -f "$chain" | head -1) 2>/dev/null | xargs)
        echo "Runtime: $runtime"
    else
        echo "Status: ⏹️  STOPPED"
    fi
    
    # Check log for stage - try multiple naming patterns
    log=""
    # Extract short name (e.g., "control" from "run_control_planck_only")
    short_name=$(echo "$chain" | sed 's/run_//' | cut -d'_' -f1)
    for pattern in "chains/${chain}.log" "chains/run_${short_name}.log" "chains/${short_name}.log"; do
        if [ -f "$pattern" ]; then
            log="$pattern"
            break
        fi
    done
    
    if [ -f "$log" ]; then
        # Get stage from log - check in order of progress
        if grep -q "Accepted" "$log" 2>/dev/null; then
            echo "Stage:  SAMPLING"
            acc_line=$(grep "Accepted" "$log" 2>/dev/null | tail -1)
            echo "        $acc_line"
        elif grep -q "burn-in\|Burn-in" "$log" 2>/dev/null; then
            echo "Stage:  BURN-IN"
        elif grep -q "Getting initial point" "$log" 2>/dev/null; then
            echo "Stage:  ⏳ COMPUTING FIRST POINT (takes 15-20 min for EDE)"
        elif grep -q "covmat\|proposal" "$log" 2>/dev/null; then
            echo "Stage:  LEARNING PROPOSAL"
        else
            echo "Stage:  INITIALIZING"
        fi
        
        # Get R-1 convergence
        r1_line=$(grep -E "R-1|Rminus1" "$log" 2>/dev/null | tail -1)
        if [ -n "$r1_line" ]; then
            echo "R-1:    $r1_line"
        fi
        
        # Get log file size as progress indicator
        log_size=$(du -h "$log" 2>/dev/null | awk '{print $1}')
        echo "Log:    $log_size"
    else
        echo "Stage:  NOT STARTED (no log file)"
    fi
    
    # Check chain file for samples
    chain_file="chains/${chain}.1.txt"
    if [ -f "$chain_file" ]; then
        samples=$(wc -l < "$chain_file")
        echo "Samples: $samples"
        
        # Parse actual parameter values from chain file
        # GetDist format: weight, -loglike, params...
        # Need to know column order from .paramnames file
        
        paramnames="chains/${chain}.paramnames"
        if [ -f "$paramnames" ]; then
            # Get column indices for key params
            h0_col=$(grep -n "^H0" "$paramnames" | cut -d: -f1)
            s8_col=$(grep -n "^S8\|^sigma8" "$paramnames" | cut -d: -f1)
            
            if [ -n "$h0_col" ]; then
                # Column in chain file = paramnames line + 2 (weight, loglike)
                h0_idx=$((h0_col + 2))
                
                # Get last 100 samples and compute mean
                h0_val=$(tail -100 "$chain_file" | awk -v col=$h0_idx '{sum+=$col; n++} END {if(n>0) printf "%.2f", sum/n}')
                h0_std=$(tail -100 "$chain_file" | awk -v col=$h0_idx -v mean=$h0_val '{sum+=($col-mean)^2; n++} END {if(n>1) printf "%.2f", sqrt(sum/(n-1))}')
                [ -n "$h0_val" ] && echo "H₀:     $h0_val ± $h0_std"
            fi
        fi
        
        # Best chi2 from chain (column 2 is -loglike, chi2 = 2*loglike)
        best_chi2=$(awk 'NR>1 {if(NR==2 || $2<min) min=$2} END {printf "%.1f", 2*min}' "$chain_file" 2>/dev/null)
        [ -n "$best_chi2" ] && [ "$best_chi2" != "0.0" ] && echo "Best χ²: $best_chi2"
        
    else
        echo "Samples: 0 (not started)"
    fi
done

echo ""
echo "=============================================="
echo "  LATEST LOG (last 5 non-debug lines)"
echo "=============================================="
for log in chains/*.log; do
    if [ -f "$log" ]; then
        echo "--- $(basename $log) ---"
        grep -v "RIDDER DEBUG\|V_RIDDER\|DDV_CHECK\|rho_ridder" "$log" 2>/dev/null | tail -5
        echo ""
    fi
done
