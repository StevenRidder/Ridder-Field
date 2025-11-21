#!/bin/bash
#
# Ridder Field Azure VM Provisioning Script
# Automatically sets up the compute environment for MCMC
#

set -e

echo "============================================================"
echo "RIDDER FIELD: Azure VM Provisioning"
echo "============================================================"

# Update system
echo "[1/8] Updating system packages..."
apt-get update
apt-get upgrade -y

# Install build essentials
echo "[2/8] Installing build tools..."
apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    make \
    cmake \
    git \
    wget \
    curl \
    vim \
    htop

# Install Python and scientific libraries
echo "[3/8] Installing Python and dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    cython3

# Install MPI for parallel computing
echo "[4/8] Installing OpenMPI..."
apt-get install -y \
    libopenmpi-dev \
    openmpi-bin \
    openmpi-common

# Install FFTW (used by CLASS)
echo "[5/8] Installing FFTW..."
apt-get install -y libfftw3-dev

# Install Python packages for MCMC
echo "[6/8] Installing Python packages (Cobaya, GetDist, etc.)..."
pip3 install --upgrade pip
pip3 install \
    cobaya \
    getdist \
    matplotlib \
    numpy \
    scipy \
    cython \
    mpi4py

# Create working directory
echo "[7/8] Setting up working directory..."
mkdir -p /home/ridderadmin/ridder-field
chown -R ridderadmin:ridderadmin /home/ridderadmin/ridder-field

# Clone repository (will be done by user after SSH)
echo "[8/8] Setup complete!"

# Write helpful message
cat > /home/ridderadmin/WELCOME.txt << 'EOF'
============================================================
RIDDER FIELD COMPUTE NODE
============================================================

This VM is ready for Ridder Field MCMC analysis.

NEXT STEPS:
-----------

1. Clone the repository:
   git clone https://github.com/StevenRidder/Ridder-Field.git
   cd Ridder-Field

2. Compile CLASS:
   cd phase2/class
   make clean && make -j16
   cd ../..

3. Test CLASS:
   cd phase3
   ../phase2/class/class ridder_smoketest_spec.ini

4. Run MCMC test:
   python3 run_local_mcmc_test.py

SYSTEM INFO:
------------
CPUs: 16 cores
RAM: 64 GB
Disk: 200 GB SSD
OS: Ubuntu 22.04 LTS

INSTALLED SOFTWARE:
-------------------
✓ GCC, G++, Gfortran
✓ OpenMPI (for parallel computing)
✓ Python 3 + NumPy, SciPy, Matplotlib
✓ Cobaya (MCMC sampler)
✓ GetDist (analysis tools)
✓ FFTW (for CLASS)

USEFUL COMMANDS:
----------------
htop              - Monitor CPU/RAM usage
nvidia-smi        - Check GPU (if applicable)
df -h             - Check disk space
free -h           - Check memory usage

DOCUMENTATION:
--------------
See ~/Ridder-Field/MCMC_ROADMAP.md for full instructions

============================================================
EOF

chown ridderadmin:ridderadmin /home/ridderadmin/WELCOME.txt

echo "============================================================"
echo "Provisioning complete! VM is ready for use."
echo "============================================================"

