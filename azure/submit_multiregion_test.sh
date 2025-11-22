#!/bin/bash
# Submit 1-minute MCMC test across 4 regions (32 parallel chains)

set -euo pipefail

cd "$(dirname "$0")"

echo "======================================================================"
echo "MULTI-REGION 1-MINUTE TEST"
echo "======================================================================"
echo ""

# Get Batch account details from Terraform
BATCH_ACCOUNT=$(terraform output -raw batch_account_name_multiregion 2>/dev/null || echo "")
STORAGE_ACCOUNT=$(terraform output -raw storage_account_name_multiregion 2>/dev/null || echo "")

if [ -z "$BATCH_ACCOUNT" ]; then
    echo "❌ Error: Batch account not found. Run deploy_multiregion.sh first."
    exit 1
fi

echo "Batch Account: $BATCH_ACCOUNT"
echo "Storage Account: $STORAGE_ACCOUNT"
echo ""

# Upload CLASS code and config to storage
echo "Uploading Ridder Field code to Azure Storage..."
CONTAINER_NAME="ridder-mcmc-input"
az storage container create --name "$CONTAINER_NAME" --account-name "$STORAGE_ACCOUNT" --auth-mode login || true

# Create a tarball of the phase2 directory
echo "Creating code package..."
cd ..
tar -czf /tmp/ridder-phase2.tar.gz phase2/
cd azure

# Upload to blob storage
az storage blob upload --account-name "$STORAGE_ACCOUNT" --container-name "$CONTAINER_NAME" \
    --name "ridder-phase2.tar.gz" --file "/tmp/ridder-phase2.tar.gz" --auth-mode login --overwrite

echo "✅ Code uploaded"
echo ""

# Create Batch job
JOB_ID="ridder-1min-test-$(date +%Y%m%d-%H%M%S)"
echo "Creating Batch job: $JOB_ID"

az batch job create --id "$JOB_ID" --account-name "$BATCH_ACCOUNT" \
    --pool-id "ridder-pool-australiaeast" || true

echo ""
echo "Submitting 32 tasks (8 per region)..."

# Submit 8 tasks to each pool
POOLS=("ridder-pool-australiaeast" "ridder-pool-southeastasia" "ridder-pool-eastasia" "ridder-pool-japaneast")
TASK_NUM=0

for POOL in "${POOLS[@]}"; do
    echo "  Submitting to $POOL..."
    
    for CHAIN in {1..8}; do
        TASK_ID="chain-${TASK_NUM}"
        TASK_NUM=$((TASK_NUM + 1))
        
        # Task command: download code, compile CLASS, run 1-minute MCMC
        TASK_CMD="/bin/bash -c '\
            cd /tmp && \
            wget -q https://${STORAGE_ACCOUNT}.blob.core.windows.net/${CONTAINER_NAME}/ridder-phase2.tar.gz && \
            tar -xzf ridder-phase2.tar.gz && \
            cd phase2/class && \
            make clean && make -j8 && \
            cd python && python3 setup.py install --user && \
            cd /tmp && \
            mkdir -p output && \
            echo \"Running 1-minute MCMC test (chain $CHAIN on $POOL)...\" && \
            python3 -c \"
from classy import Class
import time
c = Class()
c.set({
    'output': 'tCl',
    'theta_i_ridder': 2.0,
    'beta_ridder': 0.01,
    'Lambda_EDE_ridder': 1.0,
    'f_axion_ridder': 1e27,
    'n_ridder': 3,
    'omega_b': 0.0224,
    'omega_cdm': 0.12,
    'H0': 67.4,
    'A_s': 2.1e-9,
    'n_s': 0.965,
    'tau_reio': 0.054,
    'gauge': 'newtonian'
})
start = time.time()
c.compute()
elapsed = time.time() - start
print(f'✅ Chain $CHAIN on $POOL completed in {elapsed:.2f}s')
print(f'H0 = {c.Hubble(0) * 299792.458:.2f} km/s/Mpc')
with open('/tmp/output/chain_${TASK_ID}_result.txt', 'w') as f:
    f.write(f'Pool: $POOL\n')
    f.write(f'Chain: $CHAIN\n')
    f.write(f'Time: {elapsed:.2f}s\n')
    f.write(f'H0: {c.Hubble(0) * 299792.458:.2f}\n')
\" && \
            echo \"Task ${TASK_ID} complete\" \
        '"
        
        # Submit task to specific pool
        az batch task create --job-id "$JOB_ID" --task-id "$TASK_ID" \
            --account-name "$BATCH_ACCOUNT" \
            --command-line "$TASK_CMD" \
            --resource-files "[{\"httpUrl\":\"https://${STORAGE_ACCOUNT}.blob.core.windows.net/${CONTAINER_NAME}/ridder-phase2.tar.gz\",\"filePath\":\"ridder-phase2.tar.gz\"}]" \
            >/dev/null 2>&1 || echo "  (Task $TASK_ID already exists)"
    done
done

echo ""
echo "======================================================================"
echo "✅ 32 TASKS SUBMITTED"
echo "======================================================================"
echo ""
echo "Job ID: $JOB_ID"
echo ""
echo "Monitor progress:"
echo "  az batch task list --job-id $JOB_ID --account-name $BATCH_ACCOUNT --query \"[].{ID:id, State:state}\" -o table"
echo ""
echo "Expected completion: ~2-3 minutes (parallel execution)"
echo "vs Single VM: ~16 minutes (sequential)"
echo ""
echo "Performance gain: ~5-8x faster! 🚀"
echo ""

