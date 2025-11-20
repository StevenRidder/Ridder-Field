# Phase 2: CLASS Implementation

**Status:** Setup scripts ready. Run `python3 setup_class.py` to clone and compile CLASS.

## What's Here

- **`setup_class.py`** - Automated Python script to clone and compile CLASS
- **`clone_and_setup_class.sh`** - Shell script alternative
- **`PHASE2_SETUP_GUIDE.md`** - Complete step-by-step implementation guide
- **`ridder_background_modifications.c`** - C code templates ready to copy-paste
- **`QUICK_START.md`** - Quick reference for setup commands

## Quick Setup

```bash
cd "/Users/steveridder/Git/Ridder Field/phase2"
python3 setup_class.py
```

This will clone CLASS, compile it, test it, and create a backup.

## After Setup

Once CLASS is compiled, follow `PHASE2_SETUP_GUIDE.md` to:
1. Modify `class/include/background.h` - Add Ridder field structure
2. Modify `class/source/input.c` - Read parameters
3. Modify `class/source/background.c` - Evolution equations
4. Test: ΛCDM baseline must reproduce exactly

## Reference

All C code snippets are in `ridder_background_modifications.c` - just copy and paste into CLASS source files.

