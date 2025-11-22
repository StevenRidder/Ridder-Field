#!/bin/bash
# Check Azure VM quotas across all major regions
# Focus on regions near Polynesia (Asia-Pacific) and alternatives

set -euo pipefail

echo "======================================================================"
echo "GLOBAL AZURE QUOTA CHECK"
echo "======================================================================"
echo ""
echo "Checking DSv3 and Total vCPU quotas across regions..."
echo "Prioritizing Asia-Pacific regions (closer to Polynesia)"
echo ""

# Define regions to check (prioritize APAC)
APAC_REGIONS=(
    "australiaeast"
    "australiasoutheast"
    "southeastasia"
    "eastasia"
    "japaneast"
    "japanwest"
    "koreacentral"
    "centralindia"
    "southindia"
)

US_REGIONS=(
    "eastus"
    "eastus2"
    "westus"
    "westus2"
    "westus3"
    "centralus"
    "southcentralus"
    "northcentralus"
)

EUROPE_REGIONS=(
    "northeurope"
    "westeurope"
    "uksouth"
    "ukwest"
    "francecentral"
    "germanywestcentral"
)

check_region() {
    local region=$1
    local region_name=$2
    
    # Get DSv3 quota
    DSV3_CURRENT=$(az vm list-usage --location "$region" --query "[?name.value=='standardDSv3Family'].currentValue" -o tsv 2>/dev/null || echo "0")
    DSV3_LIMIT=$(az vm list-usage --location "$region" --query "[?name.value=='standardDSv3Family'].limit" -o tsv 2>/dev/null || echo "0")
    
    # Get total regional quota
    TOTAL_CURRENT=$(az vm list-usage --location "$region" --query "[?name.value=='cores'].currentValue" -o tsv 2>/dev/null || echo "0")
    TOTAL_LIMIT=$(az vm list-usage --location "$region" --query "[?name.value=='cores'].limit" -o tsv 2>/dev/null || echo "0")
    
    # Calculate available
    DSV3_AVAIL=$((DSV3_LIMIT - DSV3_CURRENT))
    TOTAL_AVAIL=$((TOTAL_LIMIT - TOTAL_CURRENT))
    
    printf "%-25s | DSv3: %3d/%3d (%3d avail) | Total: %3d/%3d (%3d avail)\n" \
        "$region_name" "$DSV3_CURRENT" "$DSV3_LIMIT" "$DSV3_AVAIL" \
        "$TOTAL_CURRENT" "$TOTAL_LIMIT" "$TOTAL_AVAIL"
    
    # Return the DSv3 available count for sorting
    echo "$DSV3_AVAIL|$TOTAL_AVAIL|$region|$region_name"
}

echo "======================================================================"
echo "ASIA-PACIFIC REGIONS (Closest to Polynesia)"
echo "======================================================================"
printf "%-25s | %-30s | %-30s\n" "Region" "DSv3 Family vCPUs" "Total Regional vCPUs"
echo "----------------------------------------------------------------------"

RESULTS=()

for region in "${APAC_REGIONS[@]}"; do
    result=$(check_region "$region" "$region")
    RESULTS+=("$result")
done

echo ""
echo "======================================================================"
echo "US REGIONS"
echo "======================================================================"
printf "%-25s | %-30s | %-30s\n" "Region" "DSv3 Family vCPUs" "Total Regional vCPUs"
echo "----------------------------------------------------------------------"

for region in "${US_REGIONS[@]}"; do
    result=$(check_region "$region" "$region")
    RESULTS+=("$result")
done

echo ""
echo "======================================================================"
echo "EUROPE REGIONS"
echo "======================================================================"
printf "%-25s | %-30s | %-30s\n" "Region" "DSv3 Family vCPUs" "Total Regional vCPUs"
echo "----------------------------------------------------------------------"

for region in "${EUROPE_REGIONS[@]}"; do
    result=$(check_region "$region" "$region")
    RESULTS+=("$result")
done

echo ""
echo "======================================================================"
echo "TOP 5 REGIONS BY AVAILABLE DSv3 QUOTA"
echo "======================================================================"

# Sort results by available DSv3 quota (descending)
IFS=$'\n' sorted=($(sort -t'|' -k1 -nr <<<"${RESULTS[*]}"))
unset IFS

count=0
for result in "${sorted[@]}"; do
    if [ $count -ge 5 ]; then break; fi
    
    DSV3_AVAIL=$(echo "$result" | cut -d'|' -f1)
    TOTAL_AVAIL=$(echo "$result" | cut -d'|' -f2)
    REGION=$(echo "$result" | cut -d'|' -f3)
    REGION_NAME=$(echo "$result" | cut -d'|' -f4)
    
    if [ "$DSV3_AVAIL" -gt 0 ]; then
        echo "$((count+1)). $REGION_NAME: $DSV3_AVAIL DSv3 vCPUs available (Total: $TOTAL_AVAIL)"
        count=$((count+1))
    fi
done

echo ""
echo "======================================================================"
echo "RECOMMENDATIONS"
echo "======================================================================"
echo ""

# Find best APAC region
best_apac=""
best_apac_quota=0
for result in "${RESULTS[@]}"; do
    DSV3_AVAIL=$(echo "$result" | cut -d'|' -f1)
    REGION=$(echo "$result" | cut -d'|' -f3)
    
    # Check if it's an APAC region
    for apac in "${APAC_REGIONS[@]}"; do
        if [ "$REGION" == "$apac" ] && [ "$DSV3_AVAIL" -gt "$best_apac_quota" ]; then
            best_apac="$REGION"
            best_apac_quota="$DSV3_AVAIL"
        fi
    done
done

if [ "$best_apac_quota" -gt 6 ]; then
    echo "✅ BEST OPTION: $best_apac ($best_apac_quota DSv3 vCPUs available)"
    echo "   This is in Asia-Pacific (closer to Polynesia) and has available quota."
    echo ""
    echo "   To deploy here, update batch.tf:"
    echo "   location = \"$best_apac\""
else
    echo "⚠️  All regions have similar low quotas (~10 vCPUs default)"
    echo ""
    echo "   RECOMMENDED STRATEGY:"
    echo "   1. Pick closest region: ${APAC_REGIONS[0]} (Australia East)"
    echo "   2. Request quota increase for that region (1-2 days)"
    echo "   3. Deploy small batch pool now (2x D4s_v3) for testing"
fi

echo ""
echo "======================================================================"
