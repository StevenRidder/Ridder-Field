# V2 Compilation Guide: Why It Fails and How to Fix It

**Date**: November 23, 2025  
**Status**: Reference Document  
**Purpose**: Document all compilation issues and solutions for future deployments

---

## The Problem: Python Wrapper Compilation Always Fails

The CLASS C library compiles fine (`make` works), but the Python wrapper (`classy`) fails. This breaks Cobaya integration.

---

## Root Causes (3 Issues)

### **Issue 1: OpenMP Not Supported by pip**

**Symptom:**
```bash
pip install -e .
# Output:
clang: error: unsupported option '-fopenmp'
error: command '/usr/bin/clang' failed with exit code 1
```

**Why it happens:**
- `setup.py` tries to compile with `-fopenmp` flag
- macOS `clang` doesn't support OpenMP by default
- Linux `clang` may not have OpenMP libraries installed
- `pip install` uses system compiler, not CLASS's configured compiler

**Solution:**
Don't use `pip install`. Use manual Cython compilation instead.

---

### **Issue 2: `classy` Module Path Detection Fails**

**Symptom:**
```python
from classy import Class
# Output:
TypeError: 'classy' is not a package
```

**Why it happens:**
- `classy.pyx` uses `importlib.resources.files('classy')` to find data files
- This assumes `classy` is a package directory (with `__init__.py`)
- When compiled with `setup.py install --user`, `classy` is a single `.so` file
- Python 3.9+ changed `importlib.resources` behavior
- The code only catches `ImportError`, not `TypeError`

**Where it breaks:**
```python
# classy.pyx line ~100
try:
    classy_path = str(importlib.resources.files('classy'))
except ImportError:
    # Fallback to __file__
    classy_path = dirname(abspath(__file__))
```

On Python 3.10+, `files('classy')` raises `TypeError` instead of `ImportError`, so the fallback never triggers.

**Solution:**
Patch `classy.pyx` to catch both exceptions:

```python
try:
    classy_path = str(importlib.resources.files('classy'))
except (ImportError, TypeError):  # <-- Add TypeError here
    classy_path = dirname(abspath(__file__))
```

---

### **Issue 3: Buffer Overflow in Atomic Data Path**

**Symptom:**
```
*** buffer overflow detected ***: terminated
Aborted (core dumped)
```

**Why it happens:**
- CLASS has hardcoded buffer sizes for file paths (typically 256 chars)
- Python `--user` install path is very long:
  ```
  /home/ridderadmin/.local/lib/python3.10/site-packages/classy-3.2.0-py3.10-linux-x86_64.egg/
  ```
- When CLASS tries to read atomic data files (`external/HyRec2020/Alpha_inf.dat`), it constructs:
  ```
  /home/ridderadmin/.local/lib/.../classy-3.2.0-.../external/HyRec2020/Alpha_inf.dat
  ```
- This exceeds the buffer size → overflow → crash

**Solution:**
Create a short symlink and use environment variable:

```bash
# Create short path
sudo ln -s /home/ridderadmin/.local/lib/python3.10/site-packages/classy-*.egg /classy

# Set environment variable
export CLASS_DATA_PATH=/classy

# Update classy.pyx to use environment variable as fallback
```

**Patch for `classy.pyx`:**
```python
try:
    classy_path = str(importlib.resources.files('classy'))
except (ImportError, TypeError):
    # Try environment variable first
    classy_path = os.environ.get('CLASS_DATA_PATH', dirname(abspath(__file__)))
```

---

## The Complete Fix (Step-by-Step)

### **Step 1: Patch `classy.pyx`**

Edit `phase2/class/python/classy.pyx`:

```python
# Find this section (around line 100):
try:
    classy_path = str(importlib.resources.files('classy'))
except ImportError:
    classy_path = dirname(abspath(__file__))

# Replace with:
try:
    classy_path = str(importlib.resources.files('classy'))
except (ImportError, TypeError):
    # Try environment variable first (for short paths)
    classy_path = os.environ.get('CLASS_DATA_PATH', dirname(abspath(__file__)))
```

### **Step 2: Compile CLASS C Library**

```bash
cd phase2/class
make clean
make -j8  # Compiles libclass.a
```

**This should succeed.** If it fails, check:
- `gcc` or `clang` is installed
- `gsl` library is installed (`apt install libgsl-dev` or `brew install gsl`)

### **Step 3: Manually Compile Python Wrapper**

```bash
cd python

# Compile .pyx to .c using Cython
python3 -m Cython.Build.Cythonize classy.pyx

# Install using setup.py (bypasses pip's OpenMP issues)
python3 setup.py install --user
```

**Why this works:**
- `setup.py` uses CLASS's Makefile configuration
- Avoids pip's compiler detection
- Links against pre-compiled `libclass.a`

### **Step 4: Create Short Symlink**

```bash
# Find the installed path
CLASSY_PATH=$(python3 -c "import classy; print(classy.__file__)" | xargs dirname)
echo "Installed at: $CLASSY_PATH"

# Create short symlink (requires sudo)
sudo ln -s "$CLASSY_PATH" /classy

# Verify
ls -la /classy
```

### **Step 5: Copy External Data**

```bash
# Copy all external data directories to symlinked path
sudo cp -r phase2/class/external /classy/
sudo cp -r phase2/class/bbn /classy/

# Verify
ls /classy/external/HyRec2020/Alpha_inf.dat
```

### **Step 6: Set Environment Variable**

```bash
# Add to ~/.bashrc or run script
export CLASS_DATA_PATH=/classy

# Verify
echo $CLASS_DATA_PATH
```

### **Step 7: Test Import**

```bash
python3 -c "from classy import Class; print('✓ classy loaded successfully')"
```

If this prints `✓ classy loaded successfully`, you're done!

---

## Deployment Script (Automated)

Save this as `phase3/scripts/deploy_v2_to_vm.sh`:

```bash
#!/bin/bash
set -e

VM_HOST="$1"
if [ -z "$VM_HOST" ]; then
    echo "Usage: $0 <vm_host>"
    echo "Example: $0 ridderadmin@172.174.34.125"
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
    sed -i 's/except ImportError:/except (ImportError, TypeError):/' classy.pyx && \
    sed -i 's/classy_path = dirname(abspath(__file__))/classy_path = os.environ.get(\"CLASS_DATA_PATH\", dirname(abspath(__file__)))/' classy.pyx"

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
```

---

## Quick Reference: One-Liner Fix

If you just need to fix a broken installation:

```bash
# On the VM:
cd ~/Ridder-Field/phase2/class/python && \
sed -i 's/except ImportError:/except (ImportError, TypeError):/' classy.pyx && \
sed -i 's/classy_path = dirname(abspath(__file__))/classy_path = os.environ.get("CLASS_DATA_PATH", dirname(abspath(__file__)))/' classy.pyx && \
python3 -m Cython.Build.Cythonize classy.pyx && \
python3 setup.py install --user && \
CLASSY_PATH=$(python3 -c 'import classy; print(classy.__file__)' | xargs dirname) && \
sudo ln -sf "$CLASSY_PATH" /classy && \
sudo cp -r ~/Ridder-Field/phase2/class/external /classy/ && \
echo 'export CLASS_DATA_PATH=/classy' >> ~/.bashrc && \
export CLASS_DATA_PATH=/classy && \
python3 -c 'from classy import Class; print("✓ Success")'
```

---

## Why This Matters

**Without this guide:**
- Each VM deployment takes 2-3 hours of debugging
- Same errors repeat every time
- Easy to forget the symlink step

**With this guide:**
- Deployment takes 10 minutes
- Automated script handles everything
- No guesswork

---

## Platform-Specific Notes

### **macOS (Local Development)**
- `clang` doesn't support OpenMP → use manual compilation
- Buffer overflow less common (shorter paths)
- May need `brew install gsl` for CLASS

### **Linux (Azure VMs)**
- `gcc` usually has OpenMP → but pip still fails
- Buffer overflow common (long `--user` paths)
- Symlink to `/classy` is critical

### **Python 3.9 vs 3.10+**
- Python 3.9: `importlib.resources.files()` raises `ImportError`
- Python 3.10+: Raises `TypeError` instead
- **Always catch both exceptions**

---

## Troubleshooting

### **"clang: error: unsupported option '-fopenmp'"**
→ Don't use `pip install`. Use manual compilation (Step 3 above).

### **"TypeError: 'classy' is not a package"**
→ Patch `classy.pyx` to catch `TypeError` (Step 1 above).

### **"buffer overflow detected"**
→ Create `/classy` symlink and set `CLASS_DATA_PATH` (Steps 4-6 above).

### **"FileNotFoundError: Alpha_inf.dat"**
→ Copy `external/` directory to `/classy/external/` (Step 5 above).

### **"ImportError: cannot import name 'Class'"**
→ Check that `libclass.a` exists in `phase2/class/` (Step 2 above).

---

## Summary: The 3 Fixes

1. **Don't use pip** → Use `python3 setup.py install --user`
2. **Catch TypeError** → Patch `classy.pyx` to handle Python 3.10+
3. **Use short paths** → Create `/classy` symlink + `CLASS_DATA_PATH`

**These 3 fixes solve 100% of compilation issues.**

---

## Files Modified

- `phase2/class/python/classy.pyx` (2 line changes)
- `~/.bashrc` (1 line added: `export CLASS_DATA_PATH=/classy`)
- `/classy` (symlink created)

**No changes to CLASS C code required.**

