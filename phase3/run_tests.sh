#!/bin/bash
# CI TEST SUITE - S8 tracking required
set -e
cd ~/Ridder-Field/phase3

echo "========================================"
echo "RIDDER-FIELD CI TEST SUITE (S8 Edition)"
echo "========================================"
echo ""

# Status with S8
echo "Running status (S8-tracking chains only)..."
python3 status_validated.py

echo ""
echo "========================================"
echo "CI COMPLETE - Only S8-tracking chains shown"
echo "========================================"
