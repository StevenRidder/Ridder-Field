#!/bin/bash
# Clone and setup CLASS for Ridder Field modifications
# Run this script from the phase2 directory

echo "=========================================="
echo "RIDDER FIELD - CLASS Setup Script"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [[ ! -f "PHASE2_SETUP_GUIDE.md" ]]; then
    echo "ERROR: Please run this script from the phase2 directory"
    exit 1
fi

echo "Step 1: Cloning CLASS repository..."
if [ -d "class" ]; then
    echo "  CLASS directory already exists. Skipping clone."
    echo "  (Delete 'class' folder if you want to re-clone)"
else
    git clone https://github.com/lesgourg/class_public.git class
    if [ $? -eq 0 ]; then
        echo "  ✓ CLASS cloned successfully"
    else
        echo "  ✗ Failed to clone CLASS"
        exit 1
    fi
fi

echo ""
echo "Step 2: Checking CLASS structure..."
cd class
if [ -f "Makefile" ]; then
    echo "  ✓ CLASS Makefile found"
else
    echo "  ✗ CLASS Makefile not found - clone may have failed"
    exit 1
fi

echo ""
echo "Step 3: Compiling CLASS (baseline)..."
make clean > /dev/null 2>&1
make -j4
if [ $? -eq 0 ]; then
    echo "  ✓ CLASS compiled successfully"
else
    echo "  ✗ CLASS compilation failed"
    echo "  Check that you have gcc/clang installed"
    exit 1
fi

echo ""
echo "Step 4: Testing CLASS..."
./class explanatory.ini > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ CLASS runs successfully"
else
    echo "  ✗ CLASS test run failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "SUCCESS! CLASS is ready for modification"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Create a backup: cp -r class class_original"
echo "  2. Open source/background.c in your editor"
echo "  3. Follow PHASE2_SETUP_GUIDE.md to add Ridder field"
echo ""
echo "Key files to modify:"
echo "  - include/background.h (add structure fields)"
echo "  - source/input.c (read parameters)"
echo "  - source/background.c (evolution equations)"
echo ""
echo "Reference:"
echo "  - ../ridder_background_modifications.c (C code templates)"
echo "  - ../PHASE2_SETUP_GUIDE.md (step-by-step guide)"
echo ""

