#!/bin/bash
# Start all 3 V3 production MCMC runs on Azure VM
# Each will run 4 chains with 10K samples per chain

set -e

VM_HOST="ridderadmin@172.174.34.125"
VM_PATH="/home/ridderadmin/Ridder-Field/phase3"

echo "════════════════════════════════════════════════════════════════════════════════"
echo "  STARTING V3 PRODUCTION MCMC RUNS"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Configuration:"
echo "  • 3 runs: Baseline, TRGB, SH0ES"
echo "  • 4 chains per run (Cobaya default)"
echo "  • 10,000 samples per chain"
echo "  • Expected runtime: 3-5 days per run"
echo ""
echo "───────────────────────────────────────────────────────────────────────────────"

# Start Baseline (no H0 prior)
echo ""
echo "🚀 Starting BASELINE run (no H0 prior)..."
ssh $VM_HOST "cd $VM_PATH && nohup cobaya-run ridder_v3_baseline.yaml > logs/v3_baseline.log 2>&1 &"
echo "   PID: $(ssh $VM_HOST 'pgrep -f ridder_v3_baseline.yaml' 2>/dev/null || echo 'starting...')"

# Start TRGB (H0 = 69.8 ± 1.7)
echo ""
echo "🚀 Starting TRGB run (H0 = 69.8 ± 1.7)..."
ssh $VM_HOST "cd $VM_PATH && nohup cobaya-run ridder_v3_trgb.yaml > logs/v3_trgb.log 2>&1 &"
echo "   PID: $(ssh $VM_HOST 'pgrep -f ridder_v3_trgb.yaml' 2>/dev/null || echo 'starting...')"

# Start SH0ES (H0 = 73.0 ± 1.0)
echo ""
echo "🚀 Starting SH0ES run (H0 = 73.0 ± 1.0)..."
ssh $VM_HOST "cd $VM_PATH && nohup cobaya-run ridder_v3_shoes.yaml > logs/v3_shoes.log 2>&1 &"
echo "   PID: $(ssh $VM_HOST 'pgrep -f ridder_v3_shoes.yaml' 2>/dev/null || echo 'starting...')"

echo ""
echo "───────────────────────────────────────────────────────────────────────────────"
echo "✅ All 3 runs started!"
echo ""
echo "Monitor progress:"
echo "  python3 check_v3_status.py              # Check all 3"
echo "  python3 check_v3_status.py baseline     # Check baseline only"
echo ""
echo "Direct VM access:"
echo "  ssh $VM_HOST"
echo "  cd $VM_PATH"
echo "  tail -f logs/v3_baseline.log"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"

