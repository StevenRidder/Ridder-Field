#!/bin/bash
set -e

VM_HOST="$1"
if [ -z "$VM_HOST" ]; then
    echo "Usage: $0 <vm_host>"
    echo "Example: $0 <VM_USER>@172.174.34.125"
    exit 1
fi

echo "======================================================================"
echo "DEPLOYING V2 TO: $VM_HOST"
echo "======================================================================"

# Step 1: Sync code
echo ""
echo "Step 1: Syncing V2 code..."
rsync -avz --exclude='*.o' --exclude='*.a' \
    phase2/class/ ${VM_HOST}:~/Ridder-Field/phase2/class/

rsync -avz phase3/ridder_v2_*.yaml \
    ${VM_HOST}:~/Ridder-Field/phase3/

# Step 2: Patch classy.pyx
echo ""
echo "Step 2: Patching classy.pyx..."
ssh ${VM_HOST} "cd ~/Ridder-Field/phase2/class/python && \
    sed -i.bak 's/except ImportError:/except (ImportError, TypeError):/' classy.pyx && \
    sed -i.bak 's/classy_path = dirname(abspath(__file__))/classy_path = os.environ.get(\"CLASS_DATA_PATH\", dirname(abspath(__file__)))/' classy.pyx"

# Step 3: Compile CLASS
echo ""
echo "Step 3: Compiling CLASS C library..."
ssh ${VM_HOST} "cd ~/Ridder-Field/phase2/class && \
    make clean && \
    make -j8"

# Step 4: Compile Python wrapper
echo ""
echo "Step 4: Compiling Python wrapper..."
ssh ${VM_HOST} "cd ~/Ridder-Field/phase2/class/python && \
    python3 -m Cython.Build.Cythonize classy.pyx && \
    python3 setup.py install --user"

# Step 5: Create symlink
echo ""
echo "Step 5: Creating short symlink..."
ssh ${VM_HOST} "
    CLASSY_PATH=\$(python3 -c 'import classy; print(classy.__file__)' | xargs dirname)
    echo \"Installed at: \$CLASSY_PATH\"
    sudo rm -f /classy
    sudo ln -s \"\$CLASSY_PATH\" /classy
"

# Step 6: Copy external data
echo ""
echo "Step 6: Copying external data..."
ssh ${VM_HOST} "
    sudo mkdir -p /classy/external /classy/bbn
    sudo cp -r ~/Ridder-Field/phase2/class/external/* /classy/external/
    sudo cp -r ~/Ridder-Field/phase2/class/bbn/* /classy/bbn/
"

# Step 7: Set environment variable
echo ""
echo "Step 7: Setting CLASS_DATA_PATH..."
ssh ${VM_HOST} "
    grep -q 'CLASS_DATA_PATH' ~/.bashrc || echo 'export CLASS_DATA_PATH=/classy' >> ~/.bashrc
    export CLASS_DATA_PATH=/classy
"

# Step 8: Test
echo ""
echo "Step 8: Testing import..."
ssh ${VM_HOST} "export CLASS_DATA_PATH=/classy && python3 -c 'from classy import Class; print(\"✓ classy loaded successfully\")'"

echo ""
echo "======================================================================"
echo "DEPLOYMENT COMPLETE!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. SSH to VM: ssh ${VM_HOST}"
echo "  2. Run production MCMC: cd ~/Ridder-Field/phase3 && nohup python3 -m cobaya.run ridder_v2_tier3_production.yaml &"
echo ""

