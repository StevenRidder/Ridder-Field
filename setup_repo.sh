#!/bin/bash
# Setup script for Ridder Cosmology repository
# Organizes files from ActionEngine into proper structure

set -e  # Exit on error

REPO_DIR="/Users/steveridder/Git/Ridder Field"
SOURCE_DIR="/Users/steveridder/Git/ActionEngine"

echo "========================================="
echo "Ridder Cosmology Repository Setup"
echo "========================================="

# Create directory structure
echo ""
echo "Creating directory structure..."
cd "$REPO_DIR"
mkdir -p phase1 phase2 phase3 docs data plots

# Copy Phase 1 code
echo "Copying Phase 1 code..."
cp "$SOURCE_DIR/ridder_cosmology_phase1.py" phase1/

# Copy data files
echo "Copying data files..."
cp "$SOURCE_DIR/ridder_cosmology_phase1_data.npz" data/

# Copy plots
echo "Copying plots..."
cp "$SOURCE_DIR/ridder_cosmology_phase1_results.png" plots/
if [ -f "$SOURCE_DIR/PHASE1_HUBBLE_VALIDATION.png" ]; then
    cp "$SOURCE_DIR/PHASE1_HUBBLE_VALIDATION.png" plots/
fi

# Copy documentation
echo "Copying documentation..."
cp "$SOURCE_DIR/PHASE1_CANONICAL.md" docs/
cp "$SOURCE_DIR/PHASE1_HONEST_VALIDATION_v2.md" docs/
cp "$SOURCE_DIR/PHASE1_FINAL_PROOF.md" docs/
cp "$SOURCE_DIR/PHASE1_PROVEN.txt" docs/
cp "$SOURCE_DIR/RIDDER_COSMOLOGY_PHASE1_RESULTS.md" docs/

# Create .gitignore
echo ""
echo "Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# Data files (large)
*.npz
*.npy
*.fits
*.hdf5

# Plots (generated)
*.png
*.pdf
*.jpg

# Logs
*.log

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# CLASS build files (Phase 2)
class/
CLASS/
*.o
*.a

# MCMC chains (Phase 3)
chains/
*.chain
*.covmat

# Temporary files
tmp/
temp/
*.tmp
EOF

# Create Python requirements.txt
echo ""
echo "Creating requirements.txt..."
cat > requirements.txt << 'EOF'
# Phase 1: Background Evolution
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0

# Phase 2: CLASS (will add when ready)
# cython>=0.29.0

# Phase 3: MCMC (will add when ready)
# montepython (manual install)
# OR cobaya (pip install cobaya)
EOF

# Initialize git repository
echo ""
echo "Initializing git repository..."
if [ ! -d .git ]; then
    git init
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already exists"
fi

# Create initial commit structure
echo ""
echo "Repository structure:"
tree -L 2 -I '__pycache__|*.pyc' . || ls -R

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Review files: cd '$REPO_DIR' && ls -la"
echo "2. Run Phase 1: python3 phase1/ridder_cosmology_phase1.py"
echo "3. View plots: open plots/ridder_cosmology_phase1_results.png"
echo "4. Add to git: git add . && git commit -m 'Initial commit: Phase 1 complete'"
echo "5. Create GitHub repo and push"
echo ""
echo "For Phase 2, we'll download CLASS next."
echo ""

