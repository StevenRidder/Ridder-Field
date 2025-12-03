#!/bin/bash
# Sync Environment from Australia -> US East
# Run this on AUSTRALIA VM after successful update/test
set -e

US_EAST_IP="<VM_IP>"
USER="<VM_USER>"

echo "========================================"
echo "SYNCING AUSTRALIA -> US EAST ($US_EAST_IP)"
echo "========================================"

# 1. Sync Python Environment (includes compiled classy)
echo "[1/2] Syncing ~/.local (Python packages)..."
rsync -avz \
  /home/$USER/.local/ \
  $USER@$US_EAST_IP:/home/$USER/.local/

# 2. Sync Data Packages (Planck/BAO data)
echo "[2/2] Syncing packages/data..."
rsync -avz \
  /home/$USER/Ridder-Field/phase3/packages/data/ \
  $USER@$US_EAST_IP:/home/$USER/Ridder-Field/phase3/packages/data/

echo "========================================"
echo "SYNC COMPLETE"
echo "US East is now ready to run MCMC."
echo "========================================"

