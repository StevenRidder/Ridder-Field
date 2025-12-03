#!/bin/bash
# Launch Tier 5 Phase 2: Unconstrained DESI World (No H₀ Prior)
# This is the real scientific question: Where does DESI naturally put H₀ and r_s?
#
# Usage: ssh ridderadmin@172.191.4.60 "cd ~/Ridder-Field/phase3 && bash launch_unconstrained_desi.sh"
#
# Updated: 2025-11-30

set -e

cd /home/ridderadmin/Ridder-Field/phase3

echo "======================================"
echo "TIER 5 PHASE 2: UNCONSTRAINED DESI WORLD"
echo "======================================"
echo "Scientific question: Where does DESI+Planck naturally land without H₀ prior?"
echo "Hypothesis: H₀ ~ 70-71, r_s ~ 145.5 Mpc (the convergence window)"
echo ""

# Kill any old SH0ES/TRGB+DESI chains (they're archived)
echo "🏁 Stopping any archived SH0ES/TRGB+DESI chains..."
pkill -f "tier5_.*shoes.*desi" 2>/dev/null || true
pkill -f "tier5_.*trgb.*desi" 2>/dev/null || true
sleep 2

# Activate conda environment
source /home/ridderadmin/miniconda3/etc/profile.d/conda.sh
conda activate cobaya

# Launch ΛCDM baseline (k=6)
echo ""
echo "🚀 Launching ΛCDM+DESI (no H₀ prior) — k=6 baseline..."
nohup cobaya-run configs/tier5_lcdm_desi.yaml -f > logs/tier5_lcdm_desi.log 2>&1 &
LCDM_PID=$!
echo "   PID: $LCDM_PID"
sleep 5

# Launch CPL (k=8)
echo ""
echo "🚀 Launching CPL+DESI (no H₀ prior) — k=8, tests DESI's w(z) preference..."
nohup cobaya-run configs/tier5_cpl_desi.yaml -f > logs/tier5_cpl_desi.log 2>&1 &
CPL_PID=$!
echo "   PID: $CPL_PID"
sleep 5

# Launch EDE (k=8) - will likely fail to initialize without tension
echo ""
echo "🚀 Launching EDE+DESI (no H₀ prior) — k=8, tests if EDE can exist without tension..."
echo "   NOTE: This may fail or collapse to ΛCDM if EDE requires tension to activate"
nohup cobaya-run configs/tier5_ede_desi.yaml -f > logs/tier5_ede_desi.log 2>&1 &
EDE_PID=$!
echo "   PID: $EDE_PID"

echo ""
echo "======================================"
echo "CHAINS LAUNCHED"
echo "======================================"
echo "ΛCDM+DESI:  PID=$LCDM_PID  →  chains/tier5_lcdm_desi.1.txt"
echo "CPL+DESI:   PID=$CPL_PID   →  chains/tier5_cpl_desi.1.txt"
echo "EDE+DESI:   PID=$EDE_PID   →  chains/tier5_ede_desi.1.txt"
echo ""
echo "Monitor progress:"
echo "  tail -f logs/tier5_*_desi.log"
echo ""
echo "Check status:"
echo "  python3 tier5_unconstrained_status.py  (create this script)"
echo "======================================"
