#!/bin/bash
# Quick chain status check for Paper 2

echo ""
echo "=============================================="
echo "  PAPER 2 CHAIN STATUS - $(date)"
echo "=============================================="

cd ~/Ridder-Field/phase4

echo ""
echo "=== MEMORY ==="
free -h | grep -E "Mem:|total"

echo ""
echo "=== RUNNING PROCESSES ==="
pgrep -af cobaya || echo "No cobaya processes running"

echo ""
echo "=== CHAIN FILES ==="
for chain in run_control_planck_only run_a_ede_marginalized run_b_lcdm_template; do
    files=$(ls -la chains/${chain}*.txt 2>/dev/null | wc -l)
    if [ $files -gt 0 ]; then
        samples=$(wc -l chains/${chain}.1.txt 2>/dev/null | awk '{print $1}')
        size=$(du -sh chains/${chain}*.txt 2>/dev/null | tail -1 | awk '{print $1}')
        echo "  $chain: $samples samples, $size"
    else
        echo "  $chain: not started"
    fi
done

echo ""
echo "=== LATEST LOG ENTRIES ==="
for log in chains/*.log; do
    if [ -f "$log" ]; then
        echo ""
        echo "--- $(basename $log) ---"
        tail -5 "$log" 2>/dev/null | grep -v "RIDDER DEBUG"
    fi
done

echo ""
echo "=== R-1 CONVERGENCE ==="
grep -h "R-1\|Rminus1" chains/*.log 2>/dev/null | tail -3

echo ""

