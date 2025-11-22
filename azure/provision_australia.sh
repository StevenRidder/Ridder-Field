#!/bin/bash
# Provision script for Australia East VM
# Sets up CLASS, Python, and MCMC environment

set -euo pipefail

# Update system
apt-get update
apt-get upgrade -y

# Install build tools
apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    make \
    git \
    wget \
    curl \
    vim \
    htop

# Install Python and scientific libraries
apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libopenblas-dev \
    liblapack-dev

# Install Python packages
pip3 install --upgrade pip
pip3 install numpy scipy matplotlib pandas
pip3 install cobaya getdist

# Create working directory
mkdir -p /home/ridderadmin/Ridder-Field
chown -R ridderadmin:ridderadmin /home/ridderadmin/Ridder-Field

echo "Provisioning complete!" > /home/ridderadmin/provision_complete.txt

