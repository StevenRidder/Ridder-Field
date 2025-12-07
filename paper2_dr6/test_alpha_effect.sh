#!/bin/bash
# Compare r_s with and without α-branching at high Lambda

CLASS="/Users/steveridder/Git/Ridder-Field/phase2/class/class"
OUTPUT="/Users/steveridder/Git/Ridder-Field/phase2/class/output"

# Create configs
cat > /tmp/config_a0.ini << 'EOF'
root = output/test_a0
write background = yes
h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
tau_reio = 0.0544
Lambda_EDE_ridder = 0.5
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
output = 
background_verbose = 1
gauge = newtonian
EOF

cat > /tmp/config_a05.ini << 'EOF'
root = output/test_a05
write background = yes
h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
tau_reio = 0.0544
Lambda_EDE_ridder = 0.5
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
output = 
background_verbose = 1
gauge = newtonian
EOF

echo "============================================="
echo "ALPHA-BRANCHING EFFECT TEST (Lambda = 0.5 eV)"
echo "============================================="

cd /Users/steveridder/Git/Ridder-Field/phase2/class

echo ""
echo "Running α=0 (baseline)..."
./class /tmp/config_a0.ini 2>&1 | grep -v "^α-BRANCH" | tail -15

# Get r_s from file
RS_0=$(awk 'NR>2 {if ($1 > 1099 && $1 < 1101) {print $8; exit}}' output/test_a000_background.dat)
echo "  r_s(z=1100) = $RS_0 Mpc"

echo ""
echo "Running α=0.5..."
./class /tmp/config_a05.ini 2>&1 | grep -v "^α-BRANCH" | tail -15

RS_05=$(awk 'NR>2 {if ($1 > 1099 && $1 < 1101) {print $8; exit}}' output/test_a0500_background.dat)
echo "  r_s(z=1100) = $RS_05 Mpc"

echo ""
echo "============================================="
echo "Comparing DR at z=1100:"
echo "α=0:"
awk 'NR>2 {if ($1 > 1099 && $1 < 1101) {print "  rho_ridder="$15, "rho_DR="$21, "rho_tot="$23; exit}}' output/test_a000_background.dat
echo "α=0.5:"
awk 'NR>2 {if ($1 > 1099 && $1 < 1101) {print "  rho_ridder="$15, "rho_DR="$21, "rho_tot="$23; exit}}' output/test_a0500_background.dat

