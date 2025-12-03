#!/bin/bash
#
# MATH VALIDATION: Verify CDM-Ridder coupling physics
#
# HARD ASSERTIONS:
# 1. ΛCDM must give σ8 in range [0.75, 0.90]
# 2. β=0 must be close to ΛCDM
# 3. β>0 MUST give LOWER σ8 than β=0 (core thesis!)
# 4. β<0 MUST give HIGHER σ8 than β=0
# 5. Effect must scale monotonically with |β|
# 6. Effect must not be catastrophic (<30% change)

set -e
cd "$(dirname "$0")/../phase2/class"

echo "========================================================================"
echo "COUPLING MATH VALIDATION"
echo "========================================================================"

# Create test configs
create_config() {
    local beta=$1
    local name=$2
    cat > /tmp/test_${name}.ini << EOF
h = 0.6732
omega_b = 0.02238
omega_cdm = 0.1201
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544
output = mPk
P_k_max_h/Mpc = 5.0
modes = s
ic = ad
gauge = newtonian
recombination = HyRec
root = output/test_${name}_

use_ridder = yes
ridder_model_type = v3_canon
ridder_use_shelf = yes
ridder_use_tail = no
ridder_f_eV = 2.0e26
theta_i_ridder = 2.8
ridder_Lambda_EDE_eV = 0.5
ridder_a_c = 0.0003
ridder_sigma_lna = 0.6
ridder_c_slow = 0.0
ridder_sigma_E = 0.4
beta_z_c = 3000.0
beta_sigma_z = 0.5
beta_ridder = ${beta}

input_verbose = 1
background_verbose = 1
thermodynamics_verbose = 1
perturbations_verbose = 1
fourier_verbose = 1
EOF
}

# Run and extract sigma8
run_and_get_sigma8() {
    local config=$1
    timeout 180 ./class "$config" 2>&1 | grep "sigma8=" | sed 's/.*sigma8=\([0-9.]*\).*/\1/'
}

# Create LCDM config (no Ridder)
cat > /tmp/test_lcdm.ini << EOF
h = 0.6732
omega_b = 0.02238
omega_cdm = 0.1201
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544
output = mPk
P_k_max_h/Mpc = 5.0
modes = s
ic = ad
recombination = HyRec
root = output/test_lcdm_
input_verbose = 1
fourier_verbose = 1
EOF

echo ""
echo "[1/6] Testing ΛCDM baseline..."
S8_LCDM=$(run_and_get_sigma8 /tmp/test_lcdm.ini)
echo "  σ8(ΛCDM) = $S8_LCDM"

echo ""
echo "[2/6] Testing β=0 (Ridder field, no coupling)..."
create_config 0.0 beta0
S8_BETA0=$(run_and_get_sigma8 /tmp/test_beta0.ini)
echo "  σ8(β=0) = $S8_BETA0"

echo ""
echo "[3/6] Testing β=+0.05 (positive coupling)..."
create_config 0.05 beta_pos
S8_BETA_POS=$(run_and_get_sigma8 /tmp/test_beta_pos.ini)
echo "  σ8(β=+0.05) = $S8_BETA_POS"

echo ""
echo "[4/6] Testing β=-0.05 (negative coupling)..."
create_config -0.05 beta_neg
S8_BETA_NEG=$(run_and_get_sigma8 /tmp/test_beta_neg.ini)
echo "  σ8(β=-0.05) = $S8_BETA_NEG"

echo ""
echo "[5/6] Testing β=+0.10 (stronger coupling)..."
create_config 0.10 beta_strong
S8_BETA_STRONG=$(run_and_get_sigma8 /tmp/test_beta_strong.ini)
echo "  σ8(β=+0.10) = $S8_BETA_STRONG"

echo ""
echo "========================================================================"
echo "RESULTS ANALYSIS"
echo "========================================================================"

# Calculate deltas
DELTA_POS=$(echo "$S8_BETA_POS - $S8_BETA0" | bc -l)
DELTA_NEG=$(echo "$S8_BETA_NEG - $S8_BETA0" | bc -l)
DELTA_STRONG=$(echo "$S8_BETA_STRONG - $S8_BETA0" | bc -l)

echo ""
printf "%-20s %10s %10s\n" "Model" "σ8" "Δσ8"
printf "%-20s %10s %10s\n" "--------------------" "----------" "----------"
printf "%-20s %10.4f %10s\n" "ΛCDM" "$S8_LCDM" "-"
printf "%-20s %10.4f %10s\n" "Ridder β=0" "$S8_BETA0" "baseline"
printf "%-20s %10.4f %+10.4f\n" "Ridder β=+0.05" "$S8_BETA_POS" "$DELTA_POS"
printf "%-20s %10.4f %+10.4f\n" "Ridder β=-0.05" "$S8_BETA_NEG" "$DELTA_NEG"
printf "%-20s %10.4f %+10.4f\n" "Ridder β=+0.10" "$S8_BETA_STRONG" "$DELTA_STRONG"

echo ""
echo "========================================================================"
echo "MATH ASSERTIONS"
echo "========================================================================"

PASS=0
FAIL=0

# Assert 1: ΛCDM in valid range
if (( $(echo "$S8_LCDM > 0.75 && $S8_LCDM < 0.90" | bc -l) )); then
    echo "✓ ASSERT 1: ΛCDM σ8 in valid range [0.75, 0.90]"
    ((PASS++))
else
    echo "✗ ASSERT 1 FAILED: ΛCDM σ8=$S8_LCDM outside [0.75, 0.90]"
    ((FAIL++))
fi

# Assert 2: β=0 close to ΛCDM (within 15%)
DIFF_LCDM=$(echo "($S8_BETA0 - $S8_LCDM) / $S8_LCDM * 100" | bc -l)
if (( $(echo "${DIFF_LCDM#-} < 15" | bc -l) )); then
    echo "✓ ASSERT 2: β=0 within 15% of ΛCDM (diff=${DIFF_LCDM}%)"
    ((PASS++))
else
    echo "✗ ASSERT 2 FAILED: β=0 differs from ΛCDM by ${DIFF_LCDM}%"
    ((FAIL++))
fi

# Assert 3: CORE THESIS - β>0 must DECREASE σ8
if (( $(echo "$DELTA_POS < 0" | bc -l) )); then
    echo "✓ ASSERT 3: β>0 DECREASES σ8 (Δ=$DELTA_POS) - CORE THESIS VERIFIED!"
    ((PASS++))
else
    echo "✗ ASSERT 3 FAILED: β>0 should decrease σ8 but Δ=$DELTA_POS (PHYSICS BUG!)"
    ((FAIL++))
fi

# Assert 4: β<0 must INCREASE σ8
if (( $(echo "$DELTA_NEG > 0" | bc -l) )); then
    echo "✓ ASSERT 4: β<0 INCREASES σ8 (Δ=$DELTA_NEG) - opposite direction verified"
    ((PASS++))
else
    echo "✗ ASSERT 4 FAILED: β<0 should increase σ8 but Δ=$DELTA_NEG"
    ((FAIL++))
fi

# Assert 5: Effect must scale (|Δ(β=0.10)| > |Δ(β=0.05)|)
ABS_DELTA_POS=$(echo "${DELTA_POS#-}" | bc -l)
ABS_DELTA_STRONG=$(echo "${DELTA_STRONG#-}" | bc -l)
if (( $(echo "$ABS_DELTA_STRONG > $ABS_DELTA_POS" | bc -l) )); then
    echo "✓ ASSERT 5: Coupling scales with |β| (|Δ(0.10)|=$ABS_DELTA_STRONG > |Δ(0.05)|=$ABS_DELTA_POS)"
    ((PASS++))
else
    echo "✗ ASSERT 5 FAILED: Coupling doesn't scale properly with β"
    ((FAIL++))
fi

# Assert 6: Effect not catastrophic (<30% change)
PERCENT_CHANGE=$(echo "$ABS_DELTA_STRONG / $S8_BETA0 * 100" | bc -l)
if (( $(echo "$PERCENT_CHANGE < 30" | bc -l) )); then
    echo "✓ ASSERT 6: Effect is bounded (${PERCENT_CHANGE}% < 30%)"
    ((PASS++))
else
    echo "✗ ASSERT 6 FAILED: Effect too large (${PERCENT_CHANGE}% > 30%)"
    ((FAIL++))
fi

echo ""
echo "========================================================================"
if [ $FAIL -eq 0 ]; then
    echo "✅ ALL $PASS ASSERTIONS PASSED - Coupling math is correct!"
    echo "========================================================================"
    exit 0
else
    echo "❌ $FAIL ASSERTIONS FAILED - Math bugs detected!"
    echo "========================================================================"
    exit 1
fi

