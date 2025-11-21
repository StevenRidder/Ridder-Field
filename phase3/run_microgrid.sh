#!/bin/bash
# PHASE 3 MICRO-GRID: 3-Run Sweep
# Total time: ~2 minutes

cd "/Users/steveridder/Git/Ridder Field/phase2/class"

echo "========================================================================"
echo "PHASE 3 MICRO-GRID: QUANTIFYING THE SWEET SPOT"
echo "========================================================================"
echo ""

# Run 1: theta_i = 2.0 (Baseline - already exists)
echo "[1/3] theta_i = 2.0 (Green Zone - Baseline)"
echo "Using existing: output/ridder_step1_00_*"
echo ""

# Run 2: theta_i = 2.1 (Near-optimal - already exists)
echo "[2/3] theta_i = 2.1 (Yellow Zone - Near-Optimal)"
echo "Using existing: output/creep_2.1_00_*"
echo ""

# Run 3: theta_i = 2.15 (Edge of safe zone)
echo "[3/3] theta_i = 2.15 (Testing the edge)"
./class ../../phase3/microgrid_2.15.ini 2>&1 | grep -E "(sound horizon|H \[)" | head -5
echo ""

echo "========================================================================"
echo "MICRO-GRID COMPLETE"
echo "========================================================================"
echo ""
echo "Analyzing results..."
cd "/Users/steveridder/Git/Ridder Field/phase3"
python3 analyze_microgrid.py

