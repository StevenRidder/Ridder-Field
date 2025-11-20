# Quick Start - CLASS Setup

**The terminal tool isn't showing output, but here's exactly what to run:**

## Option 1: Automated Python Script (Recommended)

Open your terminal in Cursor and run:

```bash
cd "/Users/steveridder/Git/Ridder Field/phase2"
python3 setup_class.py
```

This will:
- Clone CLASS repository
- Compile it
- Test it
- Create a backup

## Option 2: Manual Setup

```bash
# Navigate to phase2
cd "/Users/steveridder/Git/Ridder Field/phase2"

# Clone CLASS
git clone https://github.com/lesgourg/class_public.git class

# Enter CLASS directory
cd class

# Compile
make clean
make -j4

# Test
./class explanatory.ini

# If successful, create backup
cd ..
cp -r class class_original
```

## Option 3: Use the Shell Script

```bash
cd "/Users/steveridder/Git/Ridder Field/phase2"
chmod +x clone_and_setup_class.sh
./clone_and_setup_class.sh
```

---

## After CLASS is Set Up

Once CLASS compiles successfully, you're ready to start modifications:

1. **Open in editor:**
   ```bash
   code class/include/background.h
   code class/source/background.c
   ```

2. **Follow the guide:**
   - Read `PHASE2_SETUP_GUIDE.md` step-by-step
   - Copy code from `ridder_background_modifications.c`
   - Start with `background.h` (add structure fields)
   - Then modify `background.c` (add evolution equations)

3. **Test after each change:**
   ```bash
   cd class
   make
   ./class explanatory.ini
   ```

---

## Verification

CLASS is ready when:
- ✅ `class/class` executable exists
- ✅ `make` completes without errors
- ✅ `./class explanatory.ini` runs successfully

Then you can start modifying the source code!

