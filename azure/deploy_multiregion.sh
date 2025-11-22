#!/bin/bash
# Deploy Multi-Region Azure Batch (4 regions, 32 parallel chains)

set -euo pipefail

cd "$(dirname "$0")"

echo "======================================================================"
echo "MULTI-REGION BATCH DEPLOYMENT"
echo "======================================================================"
echo ""
echo "This will deploy:"
echo "  - 1 Batch Account (Australia East)"
echo "  - 4 Batch Pools across Asia-Pacific:"
echo "    • Australia East:  1x F8s_v2 (8 vCPUs)"
echo "    • Southeast Asia:  1x F8s_v2 (8 vCPUs)"
echo "    • East Asia:       1x F8s_v2 (8 vCPUs)"
echo "    • Japan East:      1x F8s_v2 (8 vCPUs)"
echo ""
echo "Total Capacity: 32 parallel MCMC chains"
echo "Estimated Cost: \$2.03/hour = \$48.72/day"
echo ""
echo "⚠️  WARNING: This will incur Azure charges!"
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
echo "Planning multi-region deployment..."
terraform plan -target=azurerm_resource_group.batch_multiregion_rg \
               -target=azurerm_storage_account.batch_multiregion_sa \
               -target=azurerm_batch_account.ridder_batch_multiregion \
               -target=azurerm_batch_pool.pool_australiaeast \
               -target=azurerm_batch_pool.pool_southeastasia \
               -target=azurerm_batch_pool.pool_eastasia \
               -target=azurerm_batch_pool.pool_japaneast \
               -out=multiregion.tfplan

echo ""
echo "Applying deployment..."
terraform apply multiregion.tfplan

echo ""
echo "======================================================================"
echo "MULTI-REGION DEPLOYMENT COMPLETE!"
echo "======================================================================"
echo ""
terraform output pool_summary

echo ""
echo "Verifying pool status..."
BATCH_ACCOUNT=$(terraform output -raw batch_account_name_multiregion)
echo ""
echo "Pool Status:"
az batch pool list --account-name "$BATCH_ACCOUNT" --query "[].{Name:id, State:allocationState, Nodes:currentDedicatedNodes}" -o table

echo ""
echo "======================================================================"
echo "NEXT STEPS"
echo "======================================================================"
echo "1. Test with 1-minute run:"
echo "   bash submit_multiregion_test.sh"
echo ""
echo "2. Run Tier 1 (Planck):"
echo "   bash submit_multiregion_tier1.sh"
echo ""
echo "3. Monitor progress:"
echo "   az batch job show --job-id ridder-mcmc-test --account-name $BATCH_ACCOUNT"
echo ""
echo "4. Download results:"
echo "   bash download_results.sh"
echo ""

