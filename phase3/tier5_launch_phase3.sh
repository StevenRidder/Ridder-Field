#!/bin/bash
# Tier 5 Phase 3: DES Y1
# Run after Phase 2 completes

set -e

echo "=============================================="
echo "TIER 5 PHASE 3: DES Y1 (Weak Lensing)"
echo "=============================================="

cd ~/Ridder-Field/phase3

echo "Testing: Does EDE S8 suppression match weak lensing?"

echo "[1/2] ΛCDM + DES..."
nohup cobaya-run configs/tier5_lcdm_des.yaml --force > logs/tier5_lcdm_des.log 2>&1 &
sleep 2

echo "[2/2] EDE + DES..."
nohup cobaya-run configs/tier5_ede_des.yaml --force > logs/tier5_ede_des.log 2>&1 &
sleep 2

echo ""
echo "Phase 3 chains launched (2 total)"

