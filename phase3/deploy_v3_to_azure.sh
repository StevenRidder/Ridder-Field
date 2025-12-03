#!/bin/bash
# deploy_v3_to_azure.sh
# Deploy v3 model to Azure VM and run MCMC

set -e  # Exit on error

echo "========================================================================"
echo "V3 MODEL DEPLOYMENT TO AZURE VM"
echo "========================================================================"
echo ""

# Configuration
REPO_DIR="${HOME}/Ridder-Field"
CLASS_DIR="${REPO_DIR}/phase2/class"
PHASE3_DIR="${REPO_DIR}/phase3"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check we're on the right machine
echo -e "${YELLOW}Step 1: Environment Check${NC}"
echo "----------------------------------------"
if [ -d "$REPO_DIR" ]; then
    echo -e "${GREEN}✓${NC} Repository found: $REPO_DIR"
else
    echo -e "${RED}✗${NC} Repository not found at $REPO_DIR"
    echo "   Clone it with: git clone https://github.com/StevenRidder/Ridder-Field.git ~/Ridder-Field"
    exit 1
fi

cd "$REPO_DIR"

# Check git branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"
if [ "$CURRENT_BRANCH" != "v3-development" ]; then
    echo -e "${YELLOW}⚠${NC}  Not on v3-development branch. Switching..."
    git checkout v3-development
fi

# Step 2: Pull latest code
echo ""
echo -e "${YELLOW}Step 2: Pull Latest V3 Code${NC}"
echo "----------------------------------------"
git fetch origin
git pull origin v3-development
echo -e "${GREEN}✓${NC} Code updated"

# Step 3: Rebuild CLASS
echo ""
echo -e "${YELLOW}Step 3: Rebuild CLASS with V3 Code${NC}"
echo "----------------------------------------"
cd "$CLASS_DIR"

# Check for C++ compiler
if ! command -v g++ &> /dev/null; then
    echo -e "${RED}✗${NC} g++ not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y build-essential gfortran
fi

# Clean and rebuild
make clean
echo "Building CLASS (this takes ~2 minutes)..."
make -j$(nproc)

if [ -f "class" ]; then
    echo -e "${GREEN}✓${NC} CLASS binary built successfully"
    ./class --version || true
else
    echo -e "${RED}✗${NC} CLASS build failed"
    exit 1
fi

# Check if classy Python wrapper is available
echo ""
echo "Checking classy Python wrapper..."
cd python
python3 -c "import classy" 2>/dev/null && echo -e "${GREEN}✓${NC} classy Python wrapper found" || {
    echo -e "${YELLOW}⚠${NC}  classy not found, installing..."
    python3 setup.py install --user
}

# Step 4: Test V3 Button API
echo ""
echo -e "${YELLOW}Step 4: Test V3 Button API${NC}"
echo "----------------------------------------"
cd "$REPO_DIR"

echo "Testing v3_trgb_branch preset..."
timeout 120 python3 run_unified_model_v3.py --preset v3_trgb_branch --mode quick || {
    echo -e "${RED}✗${NC} V3 button API test failed"
    exit 1
}
echo -e "${GREEN}✓${NC} V3 button API works"

# Step 5: Run Robust Smoke Test
echo ""
echo -e "${YELLOW}Step 5: Robust Smoke Test${NC}"
echo "----------------------------------------"
echo "This will take ~5 minutes..."
python3 mcmc_v3_robust.py || {
    echo -e "${RED}✗${NC} Smoke test failed"
    echo "   Check figures/mcmc_residuals/v3_tier4_residuals.png for diagnostics"
    exit 1
}

# Check results
SMOKE_RESULT=$(python3 -c "
import json
with open('mcmc_v3_robust_results.json') as f:
    data = json.load(f)
for b in data['branches']:
    cmb = b['cmb_rms'] * 100
    bao = b['bao_max'] * 100
    if cmb > 15 or bao > 3:
        print('FAIL')
        exit(1)
print('PASS')
" 2>/dev/null || echo "UNKNOWN")

if [ "$SMOKE_RESULT" = "PASS" ]; then
    echo -e "${GREEN}✓${NC} Smoke test PASSED (CMB < 15%, BAO < 3%)"
elif [ "$SMOKE_RESULT" = "FAIL" ]; then
    echo -e "${RED}✗${NC} Smoke test FAILED (residuals too large)"
    echo "   Review mcmc_v3_robust_results.json and residual plots"
    exit 1
else
    echo -e "${YELLOW}⚠${NC}  Could not parse smoke test results"
fi

# Step 6: Check Cobaya Setup
echo ""
echo -e "${YELLOW}Step 6: Check Cobaya Setup${NC}"
echo "----------------------------------------"
cd "$PHASE3_DIR"

# Check if Cobaya is installed
python3 -c "import cobaya" 2>/dev/null && echo -e "${GREEN}✓${NC} Cobaya installed" || {
    echo -e "${YELLOW}⚠${NC}  Cobaya not found, installing..."
    pip3 install --user cobaya
}

# Check if Planck data exists
if [ -d "packages/data/planck_2018" ]; then
    echo -e "${GREEN}✓${NC} Planck 2018 data found"
else
    echo -e "${YELLOW}⚠${NC}  Planck data not found"
    echo ""
    echo "To download Planck data (~50 GB, takes 1-2 hours):"
    echo "  cd $PHASE3_DIR"
    echo "  cobaya-install planck_2018 -p packages/"
    echo ""
    read -p "Download Planck data now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p packages
        cobaya-install planck_2018 -p packages/
    else
        echo "Skipping Planck download. You can run it later."
    fi
fi

# Step 7: Ready to Run
echo ""
echo "========================================================================"
echo -e "${GREEN}✓ V3 DEPLOYMENT COMPLETE${NC}"
echo "========================================================================"
echo ""
echo "Available MCMC configurations:"
echo "  1. ridder_v3_quick_test.yaml   (Phase 2: 2-4 hours, 800 samples)"
echo "  2. ridder_v3_baseline.yaml     (Phase 3: 30-40 hours, no H0 prior)"
echo "  3. ridder_v3_trgb.yaml         (Phase 3: 30-40 hours, H0=69.8±1.7)"
echo "  4. ridder_v3_shoes.yaml        (Phase 3: 30-40 hours, H0=73.04±1.04)"
echo ""
echo "Next steps:"
echo ""
echo "  # Quick Test (Phase 2)"
echo "  cd $PHASE3_DIR"
echo "  cobaya-run ridder_v3_quick_test.yaml"
echo ""
echo "  # Production Runs (Phase 3)"
echo "  nohup cobaya-run ridder_v3_baseline.yaml > logs/v3_baseline.log 2>&1 &"
echo "  nohup cobaya-run ridder_v3_trgb.yaml > logs/v3_trgb.log 2>&1 &"
echo "  nohup cobaya-run ridder_v3_shoes.yaml > logs/v3_shoes.log 2>&1 &"
echo ""
echo "  # Monitor"
echo "  tail -f logs/v3_baseline.log"
echo "  getdist chains/v3_baseline -p H0"
echo ""
echo "See phase3/V3_MIGRATION_GUIDE.md for full documentation."
echo ""

