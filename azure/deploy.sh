#!/bin/bash
#
# Quick deployment script for Ridder Field Azure VM
#

set -e

echo "============================================================"
echo "RIDDER FIELD: Azure Deployment Script"
echo "============================================================"
echo ""

# Check prerequisites
echo "[1/5] Checking prerequisites..."

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found"
    echo "   Install: brew install azure-cli"
    exit 1
fi
echo "✓ Azure CLI installed"

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found"
    echo "   Install: brew install terraform"
    exit 1
fi
echo "✓ Terraform installed"

# Check SSH key
if [ ! -f ~/.ssh/id_rsa.pub ]; then
    echo "❌ SSH key not found at ~/.ssh/id_rsa.pub"
    echo "   Generate: ssh-keygen -t rsa -b 4096"
    exit 1
fi
echo "✓ SSH key found"

# Check Azure login
echo ""
echo "[2/5] Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "⚠️  Not logged in to Azure"
    echo "   Running: az login"
    az login
fi

SUBSCRIPTION=$(az account show --query name -o tsv)
echo "✓ Logged in to Azure"
echo "  Subscription: $SUBSCRIPTION"

# Initialize Terraform
echo ""
echo "[3/5] Initializing Terraform..."
terraform init

# Show plan
echo ""
echo "[4/5] Reviewing deployment plan..."
terraform plan

# Confirm deployment
echo ""
echo "============================================================"
echo "DEPLOYMENT SUMMARY"
echo "============================================================"
echo ""
echo "VM Size:     Standard_D16s_v3 (16 vCPUs, 64 GB RAM)"
echo "Location:    East US"
echo "OS:          Ubuntu 22.04 LTS"
echo "Disk:        200 GB Premium SSD"
echo ""
echo "Estimated Cost:"
echo "  Hourly:    ~\$0.77/hour"
echo "  Daily:     ~\$18/day"
echo "  Test run:  ~\$0.80 (1 hour)"
echo ""
echo "============================================================"
echo ""

read -p "Deploy? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# Deploy
echo ""
echo "[5/5] Deploying..."
terraform apply -auto-approve

# Get outputs
echo ""
echo "============================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "============================================================"
echo ""

IP=$(terraform output -raw public_ip_address)
SSH_CMD=$(terraform output -raw ssh_command)

echo "Public IP:   $IP"
echo "SSH Command: $SSH_CMD"
echo ""
echo "NEXT STEPS:"
echo "============================================================"
echo ""
echo "1. Wait ~2 minutes for provisioning to complete"
echo ""
echo "2. Connect to VM:"
echo "   $SSH_CMD"
echo ""
echo "3. Clone repository:"
echo "   git clone https://github.com/StevenRidder/Ridder-Field.git"
echo "   cd Ridder-Field"
echo ""
echo "4. Compile CLASS:"
echo "   cd phase2/class"
echo "   make clean && make -j16"
echo "   cd ../.."
echo ""
echo "5. Run MCMC test:"
echo "   cd phase3"
echo "   python3 run_local_mcmc_test.py"
echo ""
echo "============================================================"
echo ""
echo "To destroy when done:"
echo "  terraform destroy"
echo ""
echo "To stop VM (keeps data, stops charges):"
echo "  az vm deallocate -g ridder-cosmology-rg -n ridder-compute-01"
echo ""
echo "============================================================"

