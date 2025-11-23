#!/bin/bash
set -e

# Master deployment script for V2 production MCMC
# Deploys to both Australia and US East VMs in parallel

AUSTRALIA_VM="ridderadmin@172.174.34.125"
USEAST_VM="ridderadmin@172.191.4.60"

echo "======================================================================"
echo "V2 PRODUCTION DEPLOYMENT: DUAL VM SETUP"
echo "======================================================================"
echo ""
echo "Australia VM: Tier 3 (Planck + BAO + SH0ES)"
echo "US East VM:   Tier 4 (Planck + BAO + Pantheon SN)"
echo ""
echo "======================================================================"

# Function to deploy to a single VM
deploy_to_vm() {
    local VM_HOST=$1
    local VM_NAME=$2
    local CONFIG_FILE=$3
    
    echo ""
    echo "----------------------------------------------------------------------"
    echo "DEPLOYING TO: $VM_NAME ($VM_HOST)"
    echo "----------------------------------------------------------------------"
    
    # Step 1: Sync code
    echo "Step 1: Syncing V2 code..."
    rsync -avz --exclude='*.o' --exclude='*.a' --exclude='chains/' \
        phase2/class/ ${VM_HOST}:~/Ridder-Field/phase2/class/
    
    rsync -avz phase3/${CONFIG_FILE} \
        ${VM_HOST}:~/Ridder-Field/phase3/
    
    # Step 2: Check if classy is already installed
    echo "Step 2: Checking classy installation..."
    CLASSY_INSTALLED=$(ssh ${VM_HOST} "python3 -c 'import classy; print(\"yes\")' 2>/dev/null || echo 'no'")
    
    if [ "$CLASSY_INSTALLED" = "yes" ]; then
        echo "  ✓ classy already installed, skipping compilation"
    else
        echo "  ✗ classy not found, compiling..."
        
        # Patch classy.pyx
        echo "  - Patching classy.pyx..."
        ssh ${VM_HOST} "cd ~/Ridder-Field/phase2/class/python && \
            sed -i.bak 's/except ImportError:/except (ImportError, TypeError):/' classy.pyx && \
            sed -i.bak 's/classy_path = dirname(abspath(__file__))/classy_path = os.environ.get(\"CLASS_DATA_PATH\", dirname(abspath(__file__)))/' classy.pyx"
        
        # Compile CLASS
        echo "  - Compiling CLASS C library..."
        ssh ${VM_HOST} "cd ~/Ridder-Field/phase2/class && make clean && make -j8"
        
        # Compile Python wrapper
        echo "  - Compiling Python wrapper..."
        ssh ${VM_HOST} "cd ~/Ridder-Field/phase2/class/python && \
            python3 -m Cython.Build.Cythonize classy.pyx && \
            python3 setup.py install --user"
        
        # Create symlink
        echo "  - Creating /classy symlink..."
        ssh ${VM_HOST} "
            CLASSY_PATH=\$(python3 -c 'import classy; print(classy.__file__)' | xargs dirname)
            sudo rm -f /classy
            sudo ln -s \"\$CLASSY_PATH\" /classy
        "
        
        # Copy external data
        echo "  - Copying external data..."
        ssh ${VM_HOST} "
            sudo mkdir -p /classy/external /classy/bbn
            sudo cp -r ~/Ridder-Field/phase2/class/external/* /classy/external/
            sudo cp -r ~/Ridder-Field/phase2/class/bbn/* /classy/bbn/
        "
        
        # Set environment variable
        echo "  - Setting CLASS_DATA_PATH..."
        ssh ${VM_HOST} "
            grep -q 'CLASS_DATA_PATH' ~/.bashrc || echo 'export CLASS_DATA_PATH=/classy' >> ~/.bashrc
        "
    fi
    
    # Step 3: Test import
    echo "Step 3: Testing classy import..."
    ssh ${VM_HOST} "export CLASS_DATA_PATH=/classy && python3 -c 'from classy import Class; print(\"✓ classy loaded successfully\")'"
    
    # Step 4: Create chains directory
    echo "Step 4: Creating chains directory..."
    ssh ${VM_HOST} "mkdir -p ~/Ridder-Field/phase3/chains"
    
    echo "✓ Deployment to $VM_NAME complete!"
}

# Deploy to both VMs
echo ""
echo "======================================================================"
echo "PHASE 1: DEPLOYING TO AUSTRALIA VM"
echo "======================================================================"
deploy_to_vm "$AUSTRALIA_VM" "Australia" "ridder_v2_tier3_production.yaml"

echo ""
echo "======================================================================"
echo "PHASE 2: DEPLOYING TO US EAST VM"
echo "======================================================================"
deploy_to_vm "$USEAST_VM" "US East" "ridder_v2_tier4_production.yaml"

echo ""
echo "======================================================================"
echo "DEPLOYMENT COMPLETE!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Launch Australia VM (Tier 3: Planck + BAO + SH0ES):"
echo "   ssh $AUSTRALIA_VM"
echo "   cd ~/Ridder-Field/phase3"
echo "   export CLASS_DATA_PATH=/classy"
echo "   nohup python3 -m cobaya.run ridder_v2_tier3_production.yaml > tier3_prod.log 2>&1 &"
echo ""
echo "2. Launch US East VM (Tier 4: Planck + BAO + Pantheon):"
echo "   ssh $USEAST_VM"
echo "   cd ~/Ridder-Field/phase3"
echo "   export CLASS_DATA_PATH=/classy"
echo "   nohup python3 -m cobaya.run ridder_v2_tier4_production.yaml > tier4_prod.log 2>&1 &"
echo ""
echo "3. Monitor progress:"
echo "   ./v2status  # (for smoke test, adapt for production)"
echo ""
echo "Expected runtime: ~10 hours per VM"
echo "======================================================================"

