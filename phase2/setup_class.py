#!/usr/bin/env python3
"""
Setup script to clone and compile CLASS for Ridder Field modifications.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, cwd=None, check=True):
    """Run a shell command and print output."""
    print(f"\n>>> {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with return code {e.returncode}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        return False

def main():
    print("="*70)
    print("RIDDER FIELD - CLASS Setup")
    print("="*70)
    
    # Get phase2 directory
    phase2_dir = Path(__file__).parent.absolute()
    os.chdir(phase2_dir)
    print(f"\nWorking directory: {phase2_dir}")
    
    # Step 1: Clone CLASS
    class_dir = phase2_dir / "class"
    
    if class_dir.exists():
        print(f"\n✓ CLASS directory already exists at {class_dir}")
        print("  (Delete it if you want to re-clone)")
    else:
        print("\nStep 1: Cloning CLASS repository...")
        success = run_cmd(
            "git clone https://github.com/lesgourg/class_public.git class",
            cwd=phase2_dir
        )
        
        if not success:
            print("\n✗ Failed to clone CLASS")
            print("  Check your internet connection and try again")
            return 1
        
        if class_dir.exists():
            print(f"\n✓ CLASS cloned successfully to {class_dir}")
        else:
            print("\n✗ CLASS directory not found after clone")
            return 1
    
    # Step 2: Check CLASS structure
    print("\nStep 2: Checking CLASS structure...")
    makefile = class_dir / "Makefile"
    if makefile.exists():
        print("  ✓ Makefile found")
    else:
        print("  ✗ Makefile not found - clone may have failed")
        return 1
    
    # Step 3: Compile CLASS
    print("\nStep 3: Compiling CLASS...")
    print("  (This may take a few minutes)")
    
    # Clean first
    run_cmd("make clean", cwd=class_dir, check=False)
    
    # Compile
    success = run_cmd("make -j4", cwd=class_dir)
    
    if not success:
        print("\n✗ CLASS compilation failed")
        print("  Make sure you have gcc/clang installed:")
        print("    macOS: xcode-select --install")
        print("    Linux: sudo apt-get install build-essential")
        return 1
    
    # Check if executable was created
    class_exe = class_dir / "class"
    if class_exe.exists():
        print(f"\n✓ CLASS compiled successfully")
        print(f"  Executable: {class_exe}")
    else:
        print("\n✗ CLASS executable not found after compilation")
        return 1
    
    # Step 4: Test CLASS
    print("\nStep 4: Testing CLASS...")
    explanatory_ini = class_dir / "explanatory.ini"
    
    if explanatory_ini.exists():
        success = run_cmd(
            f"./class {explanatory_ini.name}",
            cwd=class_dir,
            check=False
        )
        if success:
            print("  ✓ CLASS runs successfully")
        else:
            print("  ⚠ CLASS test run had warnings (may be OK)")
    else:
        print("  ⚠ explanatory.ini not found, skipping test")
    
    # Step 5: Create backup
    print("\nStep 5: Creating backup...")
    backup_dir = phase2_dir / "class_original"
    
    if backup_dir.exists():
        print(f"  ⚠ Backup already exists at {backup_dir}")
    else:
        print(f"  Creating backup: {backup_dir}")
        try:
            import shutil
            shutil.copytree(class_dir, backup_dir)
            print("  ✓ Backup created")
        except Exception as e:
            print(f"  ⚠ Failed to create backup: {e}")
            print("  (You can create it manually later)")
    
    # Summary
    print("\n" + "="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Open class/include/background.h in your editor")
    print("  2. Add Ridder field structure members")
    print("  3. Open class/source/background.c")
    print("  4. Copy code from ridder_background_modifications.c")
    print("  5. Follow PHASE2_SETUP_GUIDE.md step-by-step")
    print("\nReference files:")
    print(f"  - {phase2_dir / 'ridder_background_modifications.c'}")
    print(f"  - {phase2_dir / 'PHASE2_SETUP_GUIDE.md'}")
    print("\n" + "="*70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

