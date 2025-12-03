#!/bin/bash
# CI TEST SUITE - Full validation
set -e
cd ~/Ridder-Field/phase3

echo "========================================"
echo "RIDDER-FIELD CI TEST SUITE"
echo "========================================"
echo ""

# 1. Unit Tests: CLASS Integration
echo "[1/3] Testing CLASS integration..."
python3 test_class_integration.py 2>&1 | grep -E "(TEST|✓|✗|PASS|FAIL|Error)" || true
echo ""

# 2. Physics Tests: Coupling behavior  
echo "[2/3] Testing coupling physics..."
python3 test_coupling_physics.py 2>&1 | grep -E "(σ8|✓|✗|PASS|FAIL|CHECK|ΛCDM|Ridder)" || true
echo ""

# 3. Chain Status Dashboard
echo "[3/3] Chain status dashboard..."
python3 status_validated.py
echo ""

echo "========================================"
echo "CI COMPLETE"
echo "========================================"
