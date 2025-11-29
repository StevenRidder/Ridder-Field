#!/bin/bash
# Tier 5 Phase 2: ACT DR4
# Run after Phase 1 completes

set -e

echo "=============================================="
echo "TIER 5 PHASE 2: ACT DR4 (High-ℓ CMB)"
echo "=============================================="

cd ~/Ridder-Field/phase3

echo "Testing: Is EDE shelf consistent with damping tail?"

echo "[1/2] ΛCDM + ACT..."
nohup cobaya-run configs/tier5_lcdm_act.yaml --force > logs/tier5_lcdm_act.log 2>&1 &
sleep 2

echo "[2/2] EDE + ACT..."
nohup cobaya-run configs/tier5_ede_act.yaml --force > logs/tier5_ede_act.log 2>&1 &
sleep 2

echo ""
echo "Phase 2 chains launched (2 total)"

