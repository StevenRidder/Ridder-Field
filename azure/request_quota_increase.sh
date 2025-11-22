#!/bin/bash
# Request Azure quota increase for Batch workload
# This submits a support request to increase DSv3 vCPU quota

set -euo pipefail

SUBSCRIPTION_ID="7c45aa43-0e69-489b-b19b-79e79c8b30ac"
LOCATION="eastus"

echo "======================================================================"
echo "AZURE QUOTA INCREASE REQUEST"
echo "======================================================================"
echo ""
echo "Current Quota:"
echo "  DSv3 Family: 10 vCPUs"
echo "  Total Regional: 14 vCPUs"
echo ""
echo "Requested Quota:"
echo "  DSv3 Family: 200 vCPUs (for 10x D16s_v3 nodes + headnode)"
echo "  Total Regional: 200 vCPUs"
echo ""
echo "Justification: Running parallel MCMC cosmology simulations"
echo "======================================================================"
echo ""

# Option 1: Via Azure Portal (Manual)
echo "METHOD 1: Azure Portal (Fastest for Pay-As-You-Go)"
echo "-------------------------------------------------------------------"
echo "1. Go to: https://portal.azure.com/#view/Microsoft_Azure_Support/NewSupportRequestV3Blade"
echo "2. Issue type: Service and subscription limits (quotas)"
echo "3. Subscription: Pay-As-You-Go"
echo "4. Quota type: Compute-VM (cores-vCPUs) subscription limit increases"
echo "5. Location: East US"
echo "6. VM series: DSv3 Series"
echo "7. New vCPU limit: 200"
echo "8. Justification: Parallel MCMC cosmology simulations for research"
echo ""
echo "Typical approval time: 1-2 business days for Pay-As-You-Go"
echo ""

# Option 2: Try different region with higher default quota
echo "METHOD 2: Try Different Region (Immediate)"
echo "-------------------------------------------------------------------"
echo "Some regions have higher default quotas. Checking alternatives..."
echo ""

for region in "westus2" "westus3" "centralus" "southcentralus"; do
    echo "Checking $region..."
    DSV3_QUOTA=$(az vm list-usage --location "$region" --query "[?name.value=='standardDSv3Family'].limit" -o tsv 2>/dev/null || echo "0")
    TOTAL_QUOTA=$(az vm list-usage --location "$region" --query "[?name.value=='cores'].limit" -o tsv 2>/dev/null || echo "0")
    echo "  DSv3: $DSV3_QUOTA vCPUs, Total: $TOTAL_QUOTA vCPUs"
done

echo ""
echo "METHOD 3: Use Smaller VMs (Immediate)"
echo "-------------------------------------------------------------------"
echo "Modify batch.tf to use Standard_D4s_v3 (4 vCPUs) instead of D16s_v3"
echo "  - Current: 10x D16s_v3 = 160 vCPUs"
echo "  - Alternative: 2x D4s_v3 = 8 vCPUs (fits current quota)"
echo "  - You can run 2 parallel chains per VM = 4 total chains"
echo ""

echo "======================================================================"
echo "RECOMMENDATION: Use METHOD 3 (smaller VMs) while waiting for quota"
echo "======================================================================"

