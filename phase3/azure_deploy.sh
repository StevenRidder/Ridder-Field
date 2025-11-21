#!/bin/bash
# ============================================================
# AZURE MCMC DEPLOYMENT SCRIPT
# Single VM deployment (simplest option)
# ============================================================

set -e

echo "========================================================================"
echo "RIDDER FIELD MCMC - AZURE DEPLOYMENT"
echo "========================================================================"
echo ""

# Configuration
RESOURCE_GROUP="ridder-mcmc-rg"
LOCATION="westus2"
VM_NAME="ridder-mcmc-vm"
VM_SIZE="Standard_D16s_v3"  # 16 vCPUs, 64 GB RAM
IMAGE="Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest"

# ============================================================
# STEP 1: Create Resource Group
# ============================================================

echo "[1/6] Creating resource group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# ============================================================
# STEP 2: Create VM
# ============================================================

echo "[2/6] Creating VM..."
az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --image $IMAGE \
  --size $VM_SIZE \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard \
  --priority Spot \
  --max-price -1 \
  --eviction-policy Deallocate

# Get VM IP
VM_IP=$(az vm show -d \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --query publicIps -o tsv)

echo "VM created at: $VM_IP"

# ============================================================
# STEP 3: Install Dependencies
# ============================================================

echo "[3/6] Installing dependencies..."

ssh azureuser@$VM_IP << 'ENDSSH'
set -e

# Update system
sudo apt-get update
sudo apt-get install -y \
  build-essential \
  gfortran \
  libopenmpi-dev \
  openmpi-bin \
  python3-pip \
  python3-dev \
  git \
  wget

# Install Python packages
pip3 install --user \
  numpy \
  scipy \
  matplotlib \
  cython \
  cobaya \
  mpi4py

# Add to PATH
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

echo "Dependencies installed."
ENDSSH

# ============================================================
# STEP 4: Transfer CLASS Code
# ============================================================

echo "[4/6] Transferring CLASS code..."

# Create tarball of CLASS
cd "/Users/steveridder/Git/Ridder Field/phase2/class"
tar -czf /tmp/class_ridder.tar.gz \
  --exclude='output/*' \
  --exclude='*.o' \
  --exclude='*.pyc' \
  .

# Transfer to VM
scp /tmp/class_ridder.tar.gz azureuser@$VM_IP:~/

# Extract and compile
ssh azureuser@$VM_IP << 'ENDSSH'
set -e

mkdir -p ~/class
cd ~/class
tar -xzf ../class_ridder.tar.gz

# Compile CLASS
make clean
make -j16

# Test
./class --version

echo "CLASS compiled successfully."
ENDSSH

# ============================================================
# STEP 5: Transfer MCMC Configuration
# ============================================================

echo "[5/6] Transferring MCMC configuration..."

# Update paths in YAML
sed "s|/path/to/class|/home/azureuser/class|g" \
  "/Users/steveridder/Git/Ridder Field/phase3/ridder_mcmc.yaml" | \
sed "s|/path/to/output|/home/azureuser/output|g" \
  > /tmp/ridder_mcmc_azure.yaml

# Transfer
scp /tmp/ridder_mcmc_azure.yaml azureuser@$VM_IP:~/ridder_mcmc.yaml

# Create output directory
ssh azureuser@$VM_IP "mkdir -p ~/output"

# ============================================================
# STEP 6: Launch MCMC
# ============================================================

echo "[6/6] Launching MCMC..."

ssh azureuser@$VM_IP << 'ENDSSH'
set -e

cd ~

# Launch 4 chains in parallel using MPI
nohup mpirun -np 4 \
  cobaya-run ridder_mcmc.yaml \
  > mcmc.log 2>&1 &

echo "MCMC launched. PID: $!"
echo "Monitor with: tail -f ~/mcmc.log"
ENDSSH

# ============================================================
# DONE
# ============================================================

echo ""
echo "========================================================================"
echo "DEPLOYMENT COMPLETE"
echo "========================================================================"
echo ""
echo "VM IP: $VM_IP"
echo "SSH: ssh azureuser@$VM_IP"
echo "Monitor: ssh azureuser@$VM_IP 'tail -f ~/mcmc.log'"
echo ""
echo "To retrieve results:"
echo "  scp -r azureuser@$VM_IP:~/output ./azure_output"
echo ""
echo "To delete resources when done:"
echo "  az group delete --name $RESOURCE_GROUP --yes --no-wait"
echo ""
echo "Estimated runtime: 8-12 hours"
echo "Estimated cost: ~$8-12"
echo ""

