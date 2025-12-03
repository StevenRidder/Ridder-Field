#!/bin/bash
# Update Ridder V2 on Australia VM (Run this ON the Australia VM)
set -e

echo "========================================"
echo "UPDATING RIDDER V2 ON AUSTRALIA VM"
echo "========================================"

# 1. Update Code
echo "[1/4] Pulling latest code..."
cd ~/Ridder-Field
git pull

# 2. Rebuild CLASS
echo "[2/4] Rebuilding CLASS..."
cd phase2/class
make clean
make -j16

# 3. Update Python Wrapper
echo "[3/4] Installing classy python module..."
# Force re-install to update with V2 changes
pip3 install --user --upgrade --force-reinstall .

# 4. Run Smoke Test
echo "[4/4] Running V2 MCMC Smoke Test..."
cd ../../phase3
cobaya-run ridder_v2_mcmc_smoke.yaml --force

echo "========================================"
echo "SUCCESS! V2 is updated and verified."
echo "Now run 'bash phase3/scripts/sync_to_useast.sh' to push to US East."
echo "========================================"

