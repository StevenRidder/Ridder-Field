#!/bin/bash
# Setup script for Phase 3: MCMC Parameter Fitting

set -e

echo "=========================================="
echo "Phase 3: MCMC Setup for Ridder Field"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Install Cobaya
echo ""
echo "Installing Cobaya..."
pip3 install --user cobaya

# Check if CLASS Python interface is available
CLASS_DIR="/Users/steveridder/Git/Ridder Field/phase2/class"
if [ -d "$CLASS_DIR/python" ]; then
    echo "✓ CLASS Python interface found"
    cd "$CLASS_DIR/python"
    if [ ! -f "classy.so" ] && [ ! -f "classy.cpython*.so" ]; then
        echo "  Building CLASS Python interface..."
        python3 setup.py build_ext --inplace
    fi
    echo "✓ CLASS Python interface ready"
else
    echo "⚠ Warning: CLASS Python interface not found"
fi

# Create directories
cd "/Users/steveridder/Git/Ridder Field/phase3"
mkdir -p chains
mkdir -p data
mkdir -p plots

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Download Planck 2018 data (if needed)"
echo "  2. Create parameter file: ridder_field.yaml"
echo "  3. Run test chain: python3 run_mcmc.py"
echo ""

