#!/bin/bash
# =============================================================================
# TIER 5 PHASE 1: DESI Y1 BAO + Pantheon+ (Essential Distance Tests)
# =============================================================================
# Question: Is the ~1% r_s reduction allowed by the best current distance data?
#
# Chains: 3 per model, 1500-2500 samples each
# Target: R-1 < 0.01 for cosmology, ESS ≥ 1500 for H0/S8
#
# Usage: ssh <VM_USER>@<VM_IP> "cd ~/Ridder-Field/phase3 && bash launch_tier5_phase1.sh"
# =============================================================================

set -e
cd /home/<VM_USER>/Ridder-Field/phase3

echo "======================================================================"
echo "TIER 5 PHASE 1: DESI Y1 BAO + PANTHEON+ — DISTANCE LADDER TEST"
echo "======================================================================"
echo ""
echo "Scientific Questions:"
echo "  1. Does r_s sit ~1% below ΛCDM with DESI?"
echo "  2. Do DESI BAO points align with EDE geometry?"
echo "  3. Does Pantheon+ validate the late-time tail?"
echo ""
echo "Chain Standard: 3 chains × 1500-2500 samples, R-1 < 0.01"
echo "======================================================================"

# Activate conda
source /home/<VM_USER>/miniconda3/etc/profile.d/conda.sh
conda activate cobaya

# Create logs directory if needed
mkdir -p logs

# =============================================================================
# WORLD A: DESI Y1 ONLY (no H0 prior, no Pantheon+)
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "WORLD A: Planck + preDESI BAO + DESI Y1 (no H₀ prior)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ΛCDM baseline (k=6)
echo "🚀 [A1] Launching ΛCDM+DESI (k=6 baseline)..."
nohup cobaya-run configs/tier5_lcdm_desi.yaml -f > logs/tier5_lcdm_desi.log 2>&1 &
echo "   PID: $!"
sleep 3

# CPL (k=8) — equal parameter count comparison
echo "🚀 [A2] Launching CPL+DESI (k=8 late-time flexibility)..."
nohup cobaya-run configs/tier5_cpl_desi.yaml -f > logs/tier5_cpl_desi.log 2>&1 &
echo "   PID: $!"
sleep 3

# Geometric EDE (k=8) — main result
echo "🚀 [A3] Launching EDE+DESI (k=8 geometric shelf)..."
nohup cobaya-run configs/tier5_ede_desi.yaml -f > logs/tier5_ede_desi.log 2>&1 &
echo "   PID: $!"
sleep 3

# =============================================================================
# WORLD B: DESI Y1 + PANTHEON+ (full distance ladder)
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "WORLD B: Planck + preDESI BAO + DESI Y1 + Pantheon+"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ΛCDM baseline (k=6)
echo "🚀 [B1] Launching ΛCDM+DESI+Pantheon (k=6 baseline)..."
nohup cobaya-run configs/tier5_lcdm_desi_pantheon.yaml -f > logs/tier5_lcdm_desi_pantheon.log 2>&1 &
echo "   PID: $!"
sleep 3

# CPL (k=8)
echo "🚀 [B2] Launching CPL+DESI+Pantheon (k=8 late-time)..."
nohup cobaya-run configs/tier5_cpl_desi_pantheon.yaml -f > logs/tier5_cpl_desi_pantheon.log 2>&1 &
echo "   PID: $!"
sleep 3

# Geometric EDE (k=8) — main result
echo "🚀 [B3] Launching EDE+DESI+Pantheon (k=8 geometric)..."
nohup cobaya-run configs/tier5_ede_desi_pantheon.yaml -f > logs/tier5_ede_desi_pantheon.log 2>&1 &
echo "   PID: $!"

echo ""
echo "======================================================================"
echo "PHASE 1 CHAINS LAUNCHED — 6 TOTAL"
echo "======================================================================"
echo ""
echo "World A (DESI only):"
echo "  • tier5_lcdm_desi           → chains/tier5_lcdm_desi.1.txt"
echo "  • tier5_cpl_desi            → chains/tier5_cpl_desi.1.txt"
echo "  • tier5_ede_desi            → chains/tier5_ede_desi.1.txt"
echo ""
echo "World B (DESI + Pantheon+):"
echo "  • tier5_lcdm_desi_pantheon  → chains/tier5_lcdm_desi_pantheon.1.txt"
echo "  • tier5_cpl_desi_pantheon   → chains/tier5_cpl_desi_pantheon.1.txt"
echo "  • tier5_ede_desi_pantheon   → chains/tier5_ede_desi_pantheon.1.txt"
echo ""
echo "Monitor progress:"
echo "  python3 tier5_phase1_status.py"
echo "  tail -f logs/tier5_*.log"
echo ""
echo "Convergence targets:"
echo "  • R̂-1 < 0.01 for H0, S8, Ω_m, r_s"
echo "  • ESS ≥ 1500 for H0, S8"
echo "  • ESS ≥ 1000 for EDE parameters"
echo "======================================================================"
