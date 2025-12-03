#!/bin/bash
# RUN_ON_VM.sh - Copy this to your Azure VM and run it

echo "=========================================="
echo "V3 Model Deployment Test on Azure VM"
echo "=========================================="
echo ""

# Pull latest code
cd ~/Ridder-Field
git pull origin v3-development

# Run deployment
bash phase3/deploy_v3_to_azure.sh

