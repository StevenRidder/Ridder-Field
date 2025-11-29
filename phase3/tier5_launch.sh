#!/bin/bash
# Tier 5 Chain Launch Script
# Run from: ~/Ridder-Field/phase3/

set -e

echo "=============================================="
echo "TIER 5: Modern Dataset Validation"
echo "=============================================="

cd ~/Ridder-Field/phase3

# Phase 1a: DESI-only (no Pantheon+)
echo ""
echo "=== PHASE 1a: DESI Y1 BAO ==="
echo "Testing: Is ~1% r_s reduction consistent with DESI?"

echo "[1/3] ΛCDM + DESI..."
nohup cobaya-run configs/tier5_lcdm_desi.yaml --force > logs/tier5_lcdm_desi.log 2>&1 &
sleep 2

echo "[2/3] CPL + DESI..."
nohup cobaya-run configs/tier5_cpl_desi.yaml --force > logs/tier5_cpl_desi.log 2>&1 &
sleep 2

echo "[3/3] EDE + DESI..."
nohup cobaya-run configs/tier5_ede_desi.yaml --force > logs/tier5_ede_desi.log 2>&1 &
sleep 2

# Wait a bit before launching Phase 1b
sleep 5

# Phase 1b: DESI + Pantheon+
echo ""
echo "=== PHASE 1b: DESI Y1 + Pantheon+ ==="
echo "Testing: Full distance ladder consistency"

echo "[1/3] ΛCDM + DESI + Pantheon+..."
nohup cobaya-run configs/tier5_lcdm_desi_pantheon.yaml --force > logs/tier5_lcdm_desi_pantheon.log 2>&1 &
sleep 2

echo "[2/3] CPL + DESI + Pantheon+..."
nohup cobaya-run configs/tier5_cpl_desi_pantheon.yaml --force > logs/tier5_cpl_desi_pantheon.log 2>&1 &
sleep 2

echo "[3/3] EDE + DESI + Pantheon+..."
nohup cobaya-run configs/tier5_ede_desi_pantheon.yaml --force > logs/tier5_ede_desi_pantheon.log 2>&1 &
sleep 2

echo ""
echo "=============================================="
echo "Phase 1 chains launched (6 total)"
echo "Check status: ps aux | grep cobaya"
echo "Check logs: tail -f logs/tier5_*.log"
echo "=============================================="

