#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "FINAL VERIFICATION - RIDDER FIELD RESTORATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Test 1: Compilation
echo "TEST 1: Compilation Check"
echo "────────────────────────────────────────────────────────────────"
cd phase2/class
make clean > /dev/null 2>&1
if make -j4 class > /dev/null 2>&1; then
    echo "✅ PASS: CLASS compiles without errors"
else
    echo "❌ FAIL: Compilation errors"
    exit 1
fi
echo ""

# Test 2: Quick Run
echo "TEST 2: Quick Run (30 seconds)"
echo "────────────────────────────────────────────────────────────────"
if timeout 60 ./class ../../phase3/ridder_smoketest_spec.ini > /dev/null 2>&1; then
    echo "✅ PASS: CLASS completes successfully"
else
    echo "❌ FAIL: CLASS did not complete"
    exit 1
fi
echo ""

# Test 3: Results Analysis
echo "TEST 3: Results Verification"
echo "────────────────────────────────────────────────────────────────"
python3 << 'PY'
import glob
files = sorted(glob.glob('output/ridder_smoketest_*_background.dat'))
fname = files[-1]

rs_rec = None
max_fede = -1.0
z_peak = None

with open(fname) as f:
    for line in f:
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        parts = line.split()
        if len(parts) < 21:
            continue
        z = float(parts[0])
        rs = float(parts[7])
        rho_ridder = float(parts[14])
        rho_tot = float(parts[19])
        fede = rho_ridder / rho_tot if rho_tot != 0 else 0.0
        if fede > max_fede:
            max_fede = fede
            z_peak = z
        if 1090 <= z <= 1110 and rs_rec is None:
            rs_rec = rs

# Check results
rs_ok = abs(rs_rec - 139.06) < 1.0
fede_ok = abs(max_fede - 0.1546) < 0.001
z_ok = abs(z_peak - 6697) < 50

print(f"r_s(rec)   = {rs_rec:.2f} Mpc (target: 139.06) → {'✅ PASS' if rs_ok else '❌ FAIL'}")
print(f"f_EDE_peak = {max_fede:.6f} (target: 0.1546) → {'✅ PASS' if fede_ok else '❌ FAIL'}")
print(f"z_peak     = {z_peak:.1f} (target: 6697) → {'✅ PASS' if z_ok else '❌ FAIL'}")

if not (rs_ok and fede_ok and z_ok):
    exit(1)
PY

if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "🎉 ALL TESTS PASSED - RIDDER FIELD FULLY OPERATIONAL 🎉"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "Summary:"
    echo "  ✅ Code compiles cleanly"
    echo "  ✅ Runs complete successfully"
    echo "  ✅ Physics results match targets"
    echo "  ✅ Ready for Phase 3 MCMC"
    echo ""
    echo "Next steps:"
    echo "  1. Deploy to Azure for full MCMC"
    echo "  2. Run precision tests (ℓ_max = 3000)"
    echo "  3. Compare to Planck data"
    echo ""
else
    echo "❌ SOME TESTS FAILED"
    exit 1
fi
