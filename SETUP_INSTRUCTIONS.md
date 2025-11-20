# Manual Setup Instructions for Ridder Cosmology Repository

Since the automated scripts aren't producing visible output, here are the **manual steps** to organize your repository:

##

 Step 1: Create Directory Structure

```bash
cd "/Users/steveridder/Git/Ridder Field"

# Create subdirectories
mkdir -p phase1 phase2 phase3 docs data plots
```

## Step 2: Copy Files from ActionEngine

```bash
# Copy Phase 1 Python code
cp /Users/steveridder/Git/ActionEngine/ridder_cosmology_phase1.py phase1/

# Copy data files
cp /Users/steveridder/Git/ActionEngine/ridder_cosmology_phase1_data.npz data/

# Copy plots
cp /Users/steveridder/Git/ActionEngine/ridder_cosmology_phase1_results.png plots/

# Copy documentation
cp /Users/steveridder/Git/ActionEngine/PHASE1_CANONICAL.md docs/
cp /Users/steveridder/Git/ActionEngine/PHASE1_HONEST_VALIDATION_v2.md docs/
cp /Users/steveridder/Git/ActionEngine/PHASE1_FINAL_PROOF.md docs/
cp /Users/steveridder/Git/ActionEngine/PHASE1_PROVEN.txt docs/
cp /Users/steveridder/Git/ActionEngine/RIDDER_COSMOLOGY_PHASE1_RESULTS.md docs/
```

## Step 3: Verify Structure

```bash
cd "/Users/steveridder/Git/Ridder Field"
find . -type f | grep -v ".git" | sort
```

You should see:
```
./README.md
./phase1/ridder_cosmology_phase1.py
./data/ridder_cosmology_phase1_data.npz
./plots/ridder_cosmology_phase1_results.png
./docs/PHASE1_CANONICAL.md
./docs/PHASE1_HONEST_VALIDATION_v2.md
./docs/PHASE1_FINAL_PROOF.md
./docs/PHASE1_PROVEN.txt
./docs/RIDDER_COSMOLOGY_PHASE1_RESULTS.md
```

## Step 4: Test Phase 1 Code

```bash
cd "/Users/steveridder/Git/Ridder Field"
python3 phase1/ridder_cosmology_phase1.py
```

Should output:
```
EDE Parameters:
  Lambda_EDE = 0.0 eV
  [Phase 1: EDE disabled for ΛCDM baseline validation]

Inflationary Predictions:
  n_s = 0.96498  (Planck: 0.9649 ± 0.0042)  ✓
  ...
```

## Step 5: Initialize Git Repository

```bash
cd "/Users/steveridder/Git/Ridder Field"

# Initialize git
git init

# Create .gitignore (copy from README or use setup.py)
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.DS_Store
*.log
.vscode/
.idea/
EOF

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Phase 1 complete

- Inflationary predictions: n_s=0.965, r=0.0035 ✓
- Background evolution validated
- Framework reduces to ΛCDM when EDE disabled
- Ready for Phase 2: CLASS implementation"
```

## Step 6: Create GitHub Repository

### Option A: Via GitHub Website
1. Go to https://github.com/new
2. Repository name: `ridder-cosmology` (or `ridder-field`)
3. Description: "Unified scalar field cosmology for hard sci-fi"
4. Keep it Public (or Private if preferred)
5. **Don't** initialize with README (we already have one)
6. Click "Create repository"

### Option B: Via GitHub CLI
```bash
# Install GitHub CLI if needed: brew install gh
gh repo create ridder-cosmology --public --source=. --remote=origin
```

## Step 7: Push to GitHub

```bash
cd "/Users/steveridder/Git/Ridder Field"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ridder-cosmology.git

# Push
git branch -M main
git push -u origin main
```

## Step 8: Verify on GitHub

Visit your repository at:
```
https://github.com/YOUR_USERNAME/ridder-cosmology
```

You should see:
- README.md displaying with all the info
- phase1/ folder with Python code
- docs/ folder with validation documents
- data/ and plots/ folders (if you want to track large files)

---

## Quick Commands (All-in-One)

If you want to run everything at once:

```bash
cd "/Users/steveridder/Git/Ridder Field"

# Create structure
mkdir -p phase1 phase2 phase3 docs data plots

# Copy files
cp /Users/steveridder/Git/ActionEngine/ridder_cosmology_phase1.py phase1/
cp /Users/steveridder/Git/ActionEngine/ridder_cosmology_phase1_data.npz data/
cp /Users/steveridder/Git/ActionEngine/ridder_cosmology_phase1_results.png plots/
cp /Users/steveridder/Git/ActionEngine/PHASE1_CANONICAL.md docs/
cp /Users/steveridder/Git/ActionEngine/PHASE1_HONEST_VALIDATION_v2.md docs/
cp /Users/steveridder/Git/ActionEngine/PHASE1_FINAL_PROOF.md docs/
cp /Users/steveridder/Git/ActionEngine/PHASE1_PROVEN.txt docs/
cp /Users/steveridder/Git/ActionEngine/RIDDER_COSMOLOGY_PHASE1_RESULTS.md docs/

# Initialize git
git init
git add .
git commit -m "Initial commit: Phase 1 complete"

# Add remote and push (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ridder-cosmology.git
git branch -M main
git push -u origin main
```

---

## What to Track in Git

### ✅ Always Track:
- Python code (`.py` files)
- Documentation (`.md`, `.txt` files)
- Configuration files (`requirements.txt`, etc.)
- README.md

### ❓ Maybe Track (your choice):
- Small data files (<10 MB): `ridder_cosmology_phase1_data.npz`
- Plots/figures: useful for showing results

### ❌ Don't Track:
- Large data files (>100 MB)
- Build artifacts (`__pycache__`, `.o`, `.so`)
- IDE files (`.vscode`, `.idea`)
- Logs

---

## Troubleshooting

### "Permission denied" errors
```bash
chmod +x setup.py setup_repo.sh
```

### Files not copying
Check if files exist in ActionEngine:
```bash
ls -la /Users/steveridder/Git/ActionEngine/ridder*
ls -la /Users/steveridder/Git/ActionEngine/PHASE1*
```

### Git push fails
Make sure you've created the remote repository on GitHub first!

---

Once setup is complete, you're ready for **Phase 2: CLASS Implementation**! 🚀

