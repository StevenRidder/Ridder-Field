#!/bin/bash
# Run V3 chains with theta_s sampling (FIX for frozen H0)
# This samples theta_s_1e2 instead of H0 directly

cd ~/Ridder-Field/phase3

# Thread control
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# Clean old chain files
rm -rf chains/v3_shoes_theta* chains/v3_trgb_theta* 2>/dev/null

# Start SH0ES chains (2 chains)
for i in 1 2; do
    WORK_DIR="chains/v3_shoes_theta_chain${i}_work"
    mkdir -p "$WORK_DIR"
    cp ridder_v3_shoes_theta.yaml "$WORK_DIR/config.yaml"
    sed -i "s|output: chains/v3_shoes_theta|output: chains/v3_shoes_theta_chain${i}|" "$WORK_DIR/config.yaml"
    
    nohup cobaya-run "$WORK_DIR/config.yaml" > "$WORK_DIR/chain${i}.log" 2>&1 &
    echo "Started SH0ES chain $i (PID: $!)"
done

# Start TRGB chains (2 chains)
for i in 1 2; do
    WORK_DIR="chains/v3_trgb_theta_chain${i}_work"
    mkdir -p "$WORK_DIR"
    cp ridder_v3_trgb_theta.yaml "$WORK_DIR/config.yaml"
    sed -i "s|output: chains/v3_trgb_theta|output: chains/v3_trgb_theta_chain${i}|" "$WORK_DIR/config.yaml"
    
    nohup cobaya-run "$WORK_DIR/config.yaml" > "$WORK_DIR/chain${i}.log" 2>&1 &
    echo "Started TRGB chain $i (PID: $!)"
done

echo ""
echo "All chains started. Monitor with:"
echo "  ps aux | grep cobaya"
echo "  python3 ~/Ridder-Field/phase3/scripts/check_chain_stats.py"

