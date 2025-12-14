#!/bin/bash
# Script to fetch MCMC chains from Azure VM for Zenodo archive
# 
# Prerequisites:
#   - SSH access to the VM (172.174.34.125)
#   - The chains are at /home/azureuser/Ridder-Field/paper2_dr6/chains/

VM_HOST="ridderadmin@172.174.34.125"
REMOTE_DIR="/home/azureuser/Ridder-Field/paper2_dr6/chains"
LOCAL_DIR="$(dirname "$0")/chains"

echo "=== Fetching MCMC Chains from Azure VM ==="
echo "Remote: ${VM_HOST}:${REMOTE_DIR}"
echo "Local:  ${LOCAL_DIR}"
echo ""

# Create local directory if needed
mkdir -p "${LOCAL_DIR}"

# List of primary chains mentioned in the paper
CHAINS=(
    # Primary model chains
    "lscan_0_16.1.txt"                    # EDE at Λ=0.16, ACT+DESI
    "act_desi_lcdm_matched.1.txt"         # ΛCDM baseline, ACT+DESI
    "p3_template_dr6_v2.1.txt"            # Template fit (A_sh free)
    "p2_free_lambda_act.1.txt"            # Free-Λ ACT+DESI
    
    # Frequency split chains (if they exist)
    "freq_90ghz_ede.1.txt"
    "freq_150ghz_ede.1.txt"
    "freq_220ghz_ede.1.txt"
    
    # Planck comparison chain
    "planck_desi_ede.1.txt"
)

echo "Chains to fetch:"
for chain in "${CHAINS[@]}"; do
    echo "  - ${chain}"
done
echo ""

# Fetch each chain
for chain in "${CHAINS[@]}"; do
    echo "Fetching ${chain}..."
    
    # Use sudo on remote to access azureuser's files
    ssh "${VM_HOST}" "sudo cat ${REMOTE_DIR}/${chain}" > "${LOCAL_DIR}/${chain}" 2>/dev/null
    
    if [ -s "${LOCAL_DIR}/${chain}" ]; then
        lines=$(wc -l < "${LOCAL_DIR}/${chain}")
        echo "  ✓ Downloaded: ${lines} lines"
    else
        echo "  ✗ Not found or empty"
        rm -f "${LOCAL_DIR}/${chain}"
    fi
done

# Also check for config files
echo ""
echo "=== Checking for config files ==="
CONFIG_DIR="/home/azureuser/Ridder-Field/paper2_dr6/configs"
LOCAL_CONFIG="$(dirname "$0")/configs"

CONFIGS=(
    "lscan_0_16.yaml"
    "act_desi_lcdm_matched.yaml"
    "p3_template_dr6_v2.yaml"
    "p2_free_lambda_act.yaml"
)

for config in "${CONFIGS[@]}"; do
    echo "Fetching ${config}..."
    ssh "${VM_HOST}" "sudo cat ${CONFIG_DIR}/${config}" > "${LOCAL_CONFIG}/${config}" 2>/dev/null
    
    if [ -s "${LOCAL_CONFIG}/${config}" ]; then
        echo "  ✓ Downloaded"
    else
        # Try alternate location
        ssh "${VM_HOST}" "sudo cat ${REMOTE_DIR}/lambda_scan/${config}" > "${LOCAL_CONFIG}/${config}" 2>/dev/null
        if [ -s "${LOCAL_CONFIG}/${config}" ]; then
            echo "  ✓ Downloaded (from lambda_scan/)"
        else
            echo "  ✗ Not found"
            rm -f "${LOCAL_CONFIG}/${config}"
        fi
    fi
done

echo ""
echo "=== Summary ==="
echo "Chains downloaded:"
ls -la "${LOCAL_DIR}"/*.txt 2>/dev/null | wc -l | xargs echo "  Total chain files:"
echo ""
echo "Configs downloaded:"
ls -la "${LOCAL_CONFIG}"/*.yaml 2>/dev/null | wc -l | xargs echo "  Total config files:"

