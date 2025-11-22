#!/bin/bash
# Azure Batch Setup Script for Ridder Field MCMC
# This creates a Batch account and pool for parallel MCMC execution

set -e

set -e

echo "============================================================"
echo "Azure Batch Setup for Ridder Field MCMC"
echo "============================================================"
echo ""

# Configuration
RESOURCE_GROUP="ridder-cosmology-rg"
BATCH_ACCOUNT_NAME="ridder-batch-$(date +%s | tail -c 6)"
STORAGE_ACCOUNT_NAME="ridderbatch$(date +%s | tail -c 6)"
LOCATION="westus2"
POOL_ID="ridder-pool"
VM_SIZE="Standard_D4s_v3"
VM_COUNT=8  # Start with 8 VMs (32 cores)

echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Batch Account: $BATCH_ACCOUNT_NAME"
echo "  Storage Account: $STORAGE_ACCOUNT_NAME"
echo "  Pool ID: $POOL_ID"
echo "  VM Size: $VM_SIZE"
echo "  VM Count: $VM_COUNT"
echo ""

# Check if logged in
if ! az account show &>/dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

echo "✓ Azure CLI authenticated"
echo ""

# Create storage account for Batch
echo "Creating storage account..."
az storage account create \
    --resource-group $RESOURCE_GROUP \
    --name $STORAGE_ACCOUNT_NAME \
    --location $LOCATION \
    --sku Standard_LRS \
    --output none

echo "✓ Storage account created: $STORAGE_ACCOUNT_NAME"
echo ""

# Create Batch account
echo "Creating Batch account..."
az batch account create \
    --resource-group $RESOURCE_GROUP \
    --name $BATCH_ACCOUNT_NAME \
    --location $LOCATION \
    --storage-account $STORAGE_ACCOUNT_NAME \
    --output none

echo "✓ Batch account created: $BATCH_ACCOUNT_NAME"
echo ""

# Login to Batch account
echo "Logging in to Batch account..."
az batch account login \
    --resource-group $RESOURCE_GROUP \
    --name $BATCH_ACCOUNT_NAME \
    --shared-key-auth

echo "✓ Logged in to Batch account"
echo ""

# Create Batch pool
echo "Creating Batch pool with $VM_COUNT VMs..."
az batch pool create \
    --id $POOL_ID \
    --vm-size $VM_SIZE \
    --target-dedicated-nodes $VM_COUNT \
    --target-low-priority-nodes 0 \
    --image canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2 \
    --node-agent-sku-id "batch.node.ubuntu 22.04" \
    --output none

echo "✓ Batch pool created: $POOL_ID"
echo ""

# Wait for pool to be ready
echo "Waiting for pool to be ready (this may take 5-10 minutes)..."
az batch pool show --pool-id $POOL_ID --query "allocationState" -o tsv
while [ "$(az batch pool show --pool-id $POOL_ID --query 'allocationState' -o tsv)" != "steady" ]; do
    echo "  Pool state: $(az batch pool show --pool-id $POOL_ID --query 'allocationState' -o tsv)"
    sleep 10
done

echo "✓ Pool is ready!"
echo ""

# Show pool status
echo "Pool Status:"
az batch pool show --pool-id $POOL_ID \
    --query "{State:allocationState, Nodes:currentDedicatedNodes, Cores:currentDedicatedNodes * 4}" \
    -o table

echo ""
echo "============================================================"
echo "✅ Azure Batch Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Prepare MCMC job files"
echo "  2. Submit job to Batch: az batch job create --job-id ridder-mcmc-001"
echo "  3. Add tasks to job"
echo "  4. Monitor execution"
echo ""
echo "Useful commands:"
echo "  # Check pool status:"
echo "  az batch pool show --pool-id $POOL_ID"
echo ""
echo "  # List jobs:"
echo "  az batch job list"
echo ""
echo "  # Monitor tasks:"
echo "  az batch task list --job-id <job-id>"
echo ""

