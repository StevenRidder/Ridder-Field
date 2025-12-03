#!/bin/bash
# ALWAYS use this script after modifying C code!
# Ensures complete fresh rebuild to avoid stale library issues

set -e

VM_HOST="ridderadmin@172.174.34.125"

echo "🔄 FORCING COMPLETE REBUILD ON VM..."
echo ""

# Sync code
echo "📤 Syncing background.c..."
rsync -avz phase2/class/source/background.c ${VM_HOST}:~/Ridder-Field/phase2/class/source/

# Force complete rebuild
echo ""
echo "🧹 Cleaning all build artifacts..."
ssh ${VM_HOST} "cd ~/Ridder-Field/phase2/class && rm -rf build libclass.a && make clean"

echo ""
echo "🔨 Rebuilding C library..."
ssh ${VM_HOST} "cd ~/Ridder-Field/phase2/class && make -j8 2>&1 | tail -3"

echo ""
echo "🐍 Rebuilding Python wrapper..."
ssh ${VM_HOST} "cd ~/Ridder-Field/phase2/class/python && rm -rf build classy.c *.so && python3 -m Cython.Build.Cythonize classy.pyx 2>&1 | tail -2"

echo ""
echo "📦 Installing Python wrapper..."
ssh ${VM_HOST} "cd ~/Ridder-Field/phase2/class/python && python3 setup.py install --user --force 2>&1 | tail -2"

echo ""
echo "✅ REBUILD COMPLETE!"
echo ""
echo "Running test..."
echo ""

# Run test
ssh ${VM_HOST} "cd ~/Ridder-Field && python3 -c \"
from classy import Class
cosmo = Class()
cosmo.set({
    'output': 'tCl',
    'H0': 70.0,
    'omega_b': 0.0224,
    'omega_cdm': 0.120,
    'A_s': 2.1e-9,
    'n_s': 0.965,
    'tau_reio': 0.054,
    'Lambda_EDE_ridder': 0.1,          # 0.1 eV (try lower scale)
    'theta_i_ridder': 0.5,             # SMALL angle (near minimum where V'' is large)
    'beta_ridder': 0.0,                # No coupling
    'f_axion_ridder': 2.435e27,        # f = M_Pl
    'n_ridder': 3,                     # Cosine cubed
    'gauge': 'newtonian',
})
cosmo.compute()
print('✓ Test complete')
\" 2>&1 | grep -E 'DERIVS:|PRE_IF|FIELD_MODE|✓' | head -20"

echo ""
echo "Done!"

