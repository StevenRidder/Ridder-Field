#!/usr/bin/env bash
set -euo pipefail

# Azure Batch Job Submission Script
# Assumes you have already logged in and selected subscription:
#   az login
#   az account set --subscription "YourSubscriptionId"

BATCH_RG="ridder-batch-rg"
BATCH_ACCOUNT="ridderbatch"  # Update with actual account name from terraform output
POOL_NAME="ridder-pool-16core"
JOB_ID="ridder_full_mcmc_$(date +%Y%m%d_%H%M%S)"
NUM_CHAINS="${1:-8}"  # Default 8 chains, can override: ./submit_batch_job.sh 16

echo "============================================================"
echo "Azure Batch MCMC Job Submission"
echo "============================================================"
echo "  Job ID: ${JOB_ID}"
echo "  Pool: ${POOL_NAME}"
echo "  Chains: ${NUM_CHAINS}"
echo "============================================================"
echo ""

# 1. Point az CLI at the Batch account
echo "[1/4] Logging in to Batch account..."
az batch account login \
  --name "${BATCH_ACCOUNT}" \
  --resource-group "${BATCH_RG}" \
  --shared-key-auth

echo "✓ Logged in"
echo ""

# 2. Create a job bound to the pool
echo "[2/4] Creating Batch job..."
az batch job create \
  --id "${JOB_ID}" \
  --pool-id "${POOL_NAME}"

echo "✓ Job created: ${JOB_ID}"
echo ""

# 3. Create tasks (one per chain)
echo "[3/4] Creating ${NUM_CHAINS} tasks..."
for i in $(seq 1 ${NUM_CHAINS}); do
  TASK_ID="chain${i}"
  echo "  Creating task ${TASK_ID}..."
  
  az batch task create \
    --job-id "${JOB_ID}" \
    --task-id "${TASK_ID}" \
    --command-line "/bin/bash -c 'cd /home/ridder/cosmology && ./scripts/run_mcmc.sh configs/ridder_full.yaml full_run_chain${i} 16'" \
    --output none
  
  echo "    ✓ Task ${TASK_ID} created"
done

echo ""
echo "[4/4] Job submission complete!"
echo ""
echo "============================================================"
echo "Monitoring Commands:"
echo "============================================================"
echo ""
echo "  # Check job status:"
echo "  az batch job show --job-id ${JOB_ID}"
echo ""
echo "  # List all tasks:"
echo "  az batch task list --job-id ${JOB_ID} --output table"
echo ""
echo "  # Check task status:"
echo "  az batch task show --job-id ${JOB_ID} --task-id chain1"
echo ""
echo "  # Stream task output:"
echo "  az batch task file download --job-id ${JOB_ID} --task-id chain1 --file-path stdout.txt --destination ./chain1_stdout.txt"
echo ""
echo "  # Delete job when done:"
echo "  az batch job delete --job-id ${JOB_ID} --yes"
echo ""
echo "============================================================"

