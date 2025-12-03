#!/bin/bash
# Launch ACT chains with proper error handling and no file locking conflicts
# Usage: ./launch_act_chains.sh [num_ede] [num_lcdm]

set -e

NUM_EDE=${1:-2}
NUM_LCDM=${2:-2}
BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$BASE_DIR"

# Clean up old lock files
echo "Cleaning old lock files..."
rm -f chains/*.lock* chains/*.locked 2>/dev/null || true

# Create logs directory
mkdir -p logs

# Disable file locking to prevent conflicts
export COBAYA_USE_FILE_LOCKING=False

# Launch EDE chains
echo "Launching $NUM_EDE EDE chains..."
for i in $(seq 1 $NUM_EDE); do
    echo "  Starting EDE chain $i..."
    nohup env COBAYA_USE_FILE_LOCKING=False cobaya-run configs/act_world_ede.yaml \
        -o chains/act_ede_prod_c$i \
        >> logs/act_ede_prod_c$i.log 2>&1 &
    sleep 15  # Stagger launches to avoid memory spikes
done

# Launch LCDM chains
echo "Launching $NUM_LCDM LCDM chains..."
for i in $(seq 1 $NUM_LCDM); do
    echo "  Starting LCDM chain $i..."
    nohup env COBAYA_USE_FILE_LOCKING=False cobaya-run configs/act_world_lcdm.yaml \
        -o chains/act_lcdm_prod_c$i \
        >> logs/act_lcdm_prod_c$i.log 2>&1 &
    sleep 15  # Stagger launches to avoid memory spikes
done

# Wait a bit then check status
sleep 10
echo ""
echo "=== STATUS ==="
RUNNING=$(ps aux | grep cobaya | grep -v grep | wc -l)
echo "Running chains: $RUNNING"
ps aux | grep cobaya | grep -v grep | awk '{print $NF}'
echo ""
free -h | grep Mem

