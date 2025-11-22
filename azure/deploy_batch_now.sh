#!/bin/bash
# Deploy Azure Batch with current quota (2x D4s_v3 nodes)
# This fits within your 10 vCPU DSv3 quota

set -euo pipefail

cd "$(dirname "$0")"

echo "======================================================================"
echo "DEPLOYING AZURE BATCH (QUOTA-FRIENDLY)"
echo "======================================================================"
echo ""
echo "Configuration:"
echo "  VM Size: Standard_D4s_v3 (4 vCPUs, 16 GB RAM)"
echo "  Max Nodes: 2"
echo "  Total vCPUs: 8 (fits your 10 vCPU quota)"
echo "  Region: East US"
echo ""
echo "This will create:"
echo "  - Azure Batch Account"
echo "  - Storage Account (for job data)"
echo "  - Batch Pool (auto-scales 0-2 nodes)"
echo ""
read -p "Deploy now? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Initializing Terraform..."
terraform init

echo ""
echo "Planning deployment..."
terraform plan -target=azurerm_resource_group.batch_rg \
               -target=azurerm_storage_account.batch_sa \
               -target=azurerm_batch_account.ridder_batch \
               -target=azurerm_batch_pool.ridder_pool \
               -out=batch.tfplan

echo ""
echo "Applying deployment..."
terraform apply batch.tfplan

echo ""
echo "======================================================================"
echo "BATCH DEPLOYMENT COMPLETE"
echo "======================================================================"
echo ""
terraform output -json | jq -r '
  "Batch Account: " + .batch_account_name.value,
  "Pool Name: " + .batch_pool_name.value,
  "Storage Account: " + .storage_account_name.value
'

echo ""
echo "Next steps:"
echo "  1. Submit a test job: bash submit_batch_job.sh"
echo "  2. Monitor pool: az batch pool show --pool-id ridder-pool-4core"
echo "  3. Request quota increase for larger runs (see request_quota_increase.sh)"
echo ""

