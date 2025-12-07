#!/bin/bash
# Compare α=0 (no decay) vs α=0.5 (radiation branching)
# to see impact on sound horizon

cd /Users/steveridder/Git/Ridder-Field/phase2/class
mkdir -p output

echo "================================================"
echo "Testing α-branching effect on sound horizon"
echo "================================================"

# Test 1: No decay (baseline)
echo ""
echo "=== TEST 1: α = 0.0 (no decay) ==="
cat > /tmp/test_alpha0.ini << 'EOF'
root = output/test_alpha0
write background = yes
h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
tau_reio = 0.0544
Lambda_EDE_ridder = 0.3
f_axion_ridder = 1.0e+27
theta_i_ridder = 1.0
n_ridder = 3
beta_ridder = 0.0
alpha_ridder_to_dr = 0.0
z_ridder_decay = 3500
Gamma_decay_ridder = 0.0
ridder_force_damping = 1.0
ridder_freeze_phi = no
use_ridder_shooting = 0
output = mPk
modes = s
l_max_scalars = 100
gauge = newtonian
EOF

./class /tmp/test_alpha0.ini 2>&1 | grep -E "(r_s\(z_d|sound horizon|100\*theta)" | head -5

# Test 2: α = 0.5 (radiation branching)
echo ""
echo "=== TEST 2: α = 0.5 (50% → radiation) ==="
cat > /tmp/test_alpha05.ini << 'EOF'
root = output/test_alpha05
write background = yes
h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
tau_reio = 0.0544
Lambda_EDE_ridder = 0.3
f_axion_ridder = 1.0e+27
theta_i_ridder = 1.0
n_ridder = 3
beta_ridder = 0.0
alpha_ridder_to_dr = 0.5
z_ridder_decay = 3500
Gamma_decay_ridder = 0.0
ridder_force_damping = 1.0
ridder_freeze_phi = no
use_ridder_shooting = 0
output = mPk
modes = s
l_max_scalars = 100
gauge = newtonian
EOF

./class /tmp/test_alpha05.ini 2>&1 | grep -E "(r_s\(z_d|sound horizon|100\*theta)" | head -5

# Test 3: Γ = 2.0 (kinetic friction)
echo ""
echo "=== TEST 3: Γ = 2.0 (kinetic friction) ==="
cat > /tmp/test_gamma2.ini << 'EOF'
root = output/test_gamma2
write background = yes
h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
tau_reio = 0.0544
Lambda_EDE_ridder = 0.3
f_axion_ridder = 1.0e+27
theta_i_ridder = 1.0
n_ridder = 3
beta_ridder = 0.0
alpha_ridder_to_dr = 0.0
z_ridder_decay = 3500
Gamma_decay_ridder = 2.0
ridder_force_damping = 1.0
ridder_freeze_phi = no
use_ridder_shooting = 0
output = mPk
modes = s
l_max_scalars = 100
gauge = newtonian
EOF

./class /tmp/test_gamma2.ini 2>&1 | grep -E "(r_s\(z_d|sound horizon|100\*theta|Γ-DECAY)" | head -10

echo ""
echo "================================================"
echo "If α-branching works, r_s should DECREASE"
echo "(more radiation → faster expansion → smaller r_s)"
echo "================================================"

