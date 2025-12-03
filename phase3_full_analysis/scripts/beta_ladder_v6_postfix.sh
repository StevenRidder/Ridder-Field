#!/bin/bash
#
# Beta Ladder V6 - Post Bug Fix Edition
# 
# After fixing 5 critical bugs in unified potential activation,
# we're re-running the beta ladder with conservative parameters.
#
# Strategy:
# - Lambda_EDE = 1.0 eV (known stable from Hour 1)
# - theta_i = 2.0 (inside wide window)
# - Wide window: theta_EDE_low = 0.1, theta_EDE_high = 5.0
# - Beta scan: 0.05, 0.10, 0.15, 0.20
#
# This should give us:
# - Stable perturbations (Lambda=1.0 worked before)
# - Field stays in active window
# - Progression of S8 reduction vs CMB distortion
#

set -e

REPO_ROOT="$HOME/Ridder-Field"
CLASS_BIN="$REPO_ROOT/phase2/class/class"
CONFIG_DIR="$REPO_ROOT/phase3_full_analysis/configs"
OUTPUT_DIR="$REPO_ROOT/phase3_full_analysis/output"
LOG_FILE="$OUTPUT_DIR/beta_ladder_v6.log"

mkdir -p "$CONFIG_DIR"
mkdir -p "$OUTPUT_DIR"

echo "======================================================================" | tee "$LOG_FILE"
echo "PHASE 1A: BETA LADDER V6 (Post Bug Fix)" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "Start time: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Fixed parameters
LAMBDA_EDE="1.0"
THETA_I="2.0"  # Not used anymore - set directly in INI to 0.01
THETA_LOW="0.001"  # Match the validation working range
THETA_HIGH="0.1"

# Beta values to scan
BETAS=(0.05 0.10 0.15 0.20)

for BETA in "${BETAS[@]}"; do
    echo "--------------------------------------------------------------------" | tee -a "$LOG_FILE"
    echo "Running: Lambda_EDE=${LAMBDA_EDE} eV, theta_i=${THETA_I}, beta=${BETA}" | tee -a "$LOG_FILE"
    echo "--------------------------------------------------------------------" | tee -a "$LOG_FILE"
    
    # Create config
    TAG="beta${BETA}_lambda${LAMBDA_EDE}_v6"
    INI_FILE="$CONFIG_DIR/unified_${TAG}.ini"
    
    cat > "$INI_FILE" <<EOF
# Unified Beta Ladder V6 - beta=${BETA}
# Post bug fix validation run

# Standard cosmology
H0 = 67.36
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544
YHe = 0.2454

gauge = newtonian

# Unified Ridder field
use_ridder = yes
ridder_model_type = unified
ridder_f = 1.0e16  # Decay constant (phi/theta), NOT Planck mass!

# Tail (late-time DE)
ridder_use_tail = no  # Turn OFF for now - focus on shelf only
ridder_Lambda_tail_eV = 2.3e-3
ridder_n_tail = 3.0

# Shelf (EDE) - Conservative Lambda
ridder_use_shelf = yes
ridder_m_axion = 1e-3  # H0 units - much weaker for stability
ridder_f_axion = 1e-6  # M_Pl units - much smaller
ridder_Lambda_EDE_eV = ${LAMBDA_EDE}
ridder_n_EDE = 3.0
ridder_theta_EDE_low = ${THETA_LOW}
ridder_theta_EDE_high = ${THETA_HIGH}
ridder_sigma_theta_EDE = 0.2

# Plateau (inflation) - OFF for now
ridder_use_plateau = no

# Initial conditions - start near minimum to avoid early domination
theta_i_ridder = 0.01

# CDM coupling - THIS IS WHAT WE'RE SCANNING
beta_ridder = ${BETA}
ridder_beta_sigma_z = 0.5
ridder_beta_zc = 3300.0

# Evolution controls
ridder_c_slow = 1.0
ridder_force_damping = 1.0
ridder_freeze_phi = no

# Outputs
output = tCl,pCl,lCl,mPk
write background = yes
background_verbose = 2
P_k_max_h/Mpc = 10.0
z_pk = 0
write parameters = yes
root = ${OUTPUT_DIR}/unified_${TAG}_

# Precision (standard)
tol_background_integration = 1e-6
tol_perturb_integration = 1e-6
EOF

    echo "  Config: $INI_FILE" | tee -a "$LOG_FILE"
    echo "  Running CLASS..." | tee -a "$LOG_FILE"
    
    START_TIME=$(date +%s)
    
    if timeout 300 "$CLASS_BIN" "$INI_FILE" >> "$LOG_FILE" 2>&1; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        
        echo "  ✓ SUCCESS (${DURATION}s)" | tee -a "$LOG_FILE"
        
        # Check output files
        BG_FILE="$OUTPUT_DIR/unified_${TAG}_00_background.dat"
        if [ -f "$BG_FILE" ]; then
            # Extract final Ridder fraction
            LAST_LINE=$(grep -v "^#" "$BG_FILE" | tail -1)
            RHO_RIDDER=$(echo "$LAST_LINE" | awk '{print $15}')
            RHO_TOT=$(echo "$LAST_LINE" | awk '{print $20}')
            
            if command -v python3 &> /dev/null; then
                F_RIDDER=$(python3 -c "print(f'{${RHO_RIDDER}/${RHO_TOT}:.6e}')")
                echo "  f_ridder(a=1) = $F_RIDDER" | tee -a "$LOG_FILE"
            fi
        fi
        
        # Check for CMB output
        CL_FILE="$OUTPUT_DIR/unified_${TAG}_00_cl.dat"
        if [ -f "$CL_FILE" ]; then
            echo "  CMB spectra: ✓" | tee -a "$LOG_FILE"
        else
            echo "  CMB spectra: ✗ (perturbations may have failed)" | tee -a "$LOG_FILE"
        fi
        
    else
        echo "  ✗ FAILED or TIMEOUT" | tee -a "$LOG_FILE"
        echo "  Check $LOG_FILE for details" | tee -a "$LOG_FILE"
    fi
    
    echo "" | tee -a "$LOG_FILE"
done

echo "======================================================================" | tee -a "$LOG_FILE"
echo "BETA LADDER V6 COMPLETE" | tee -a "$LOG_FILE"
echo "End time: $(date)" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Next steps:" | tee -a "$LOG_FILE"
echo "  1. Run analyze_beta_results.py to extract H0, S8, CMB metrics" | tee -a "$LOG_FILE"
echo "  2. Identify best (Lambda, beta) point" | tee -a "$LOG_FILE"
echo "  3. Proceed to Phase 1B (Tail activation)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

