#!/usr/bin/env python3
"""
Setup script for Ridder Cosmology repository
Organizes files from ActionEngine into proper structure
"""

import os
import shutil
from pathlib import Path

# Paths
REPO_DIR = Path("/Users/steveridder/Git/Ridder Field")
SOURCE_DIR = Path("/Users/steveridder/Git/ActionEngine")

print("=" * 60)
print("Ridder Cosmology Repository Setup")
print("=" * 60)

# Create directory structure
print("\n📁 Creating directory structure...")
(REPO_DIR / "phase1").mkdir(exist_ok=True)
(REPO_DIR / "phase2").mkdir(exist_ok=True)
(REPO_DIR / "phase3").mkdir(exist_ok=True)
(REPO_DIR / "docs").mkdir(exist_ok=True)
(REPO_DIR / "data").mkdir(exist_ok=True)
(REPO_DIR / "plots").mkdir(exist_ok=True)
print("   ✓ Directories created")

# Files to copy
files_to_copy = {
    "phase1": [
        "ridder_cosmology_phase1.py",
    ],
    "data": [
        "ridder_cosmology_phase1_data.npz",
    ],
    "plots": [
        "ridder_cosmology_phase1_results.png",
        "PHASE1_HUBBLE_VALIDATION.png",  # optional
    ],
    "docs": [
        "PHASE1_CANONICAL.md",
        "PHASE1_HONEST_VALIDATION_v2.md",
        "PHASE1_FINAL_PROOF.md",
        "PHASE1_PROVEN.txt",
        "RIDDER_COSMOLOGY_PHASE1_RESULTS.md",
    ],
}

# Copy files
print("\n📄 Copying files...")
total_copied = 0
for dest_dir, files in files_to_copy.items():
    for filename in files:
        src = SOURCE_DIR / filename
        dst = REPO_DIR / dest_dir / filename
        if src.exists():
            shutil.copy2(src, dst)
            print(f"   ✓ {filename} → {dest_dir}/")
            total_copied += 1
        else:
            print(f"   ⚠ {filename} not found (skipping)")

print(f"\n   Total files copied: {total_copied}")

# Create .gitignore
print("\n📝 Creating .gitignore...")
gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# Data files (large - keep out of git by default)
# Uncomment if you want to track them:
# *.npz
# *.npy
*.fits
*.hdf5

# Plots (generated - can regenerate)
# Uncomment if you want to track them:
# *.png
# *.pdf

# Logs
*.log

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# CLASS build files (Phase 2)
class/
CLASS/
*.o
*.a

# MCMC chains (Phase 3)
chains/
*.chain
*.covmat

# Temporary
tmp/
temp/
*.tmp
"""
(REPO_DIR / ".gitignore").write_text(gitignore_content)
print("   ✓ .gitignore created")

# Create requirements.txt
print("\n📦 Creating requirements.txt...")
requirements = """# Phase 1: Background Evolution
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0

# Phase 2: CLASS (add when ready)
# cython>=0.29.0

# Phase 3: MCMC (add when ready)
# Will use MontePython or Cobaya
"""
(REPO_DIR / "requirements.txt").write_text(requirements)
print("   ✓ requirements.txt created")

# Initialize git if not already done
print("\n🔧 Git initialization...")
if not (REPO_DIR / ".git").exists():
    os.chdir(REPO_DIR)
    os.system("git init")
    print("   ✓ Git repository initialized")
else:
    print("   ✓ Git repository already exists")

# Show structure
print("\n📂 Repository structure:")
os.chdir(REPO_DIR)
os.system("find . -not -path './.git/*' -type f | sort")

print("\n" + "=" * 60)
print("Setup Complete! ✅")
print("=" * 60)
print("\nNext steps:")
print("1. cd '/Users/steveridder/Git/Ridder Field'")
print("2. python3 phase1/ridder_cosmology_phase1.py")
print("3. git add . && git commit -m 'Initial commit: Phase 1 complete'")
print("4. Create GitHub repo and push")
print("\nFor Phase 2: We'll download CLASS next 🚀")
print()

