#!/usr/bin/env python3
import subprocess
import os
import sys
from pathlib import Path

phase2 = Path("/Users/steveridder/Git/Ridder Field/phase2")
os.chdir(phase2)

status_file = phase2 / "clone_status.txt"

with open(status_file, "w") as f:
    f.write("Starting CLASS clone...\n")
    f.flush()
    
    if (phase2 / "class").exists():
        f.write("CLASS already exists!\n")
        sys.exit(0)
    
    f.write("Running: git clone https://github.com/lesgourg/class_public.git class\n")
    f.flush()
    
    try:
        result = subprocess.run(
            ["git", "clone", "https://github.com/lesgourg/class_public.git", "class"],
            cwd=phase2,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        f.write(f"Exit code: {result.returncode}\n")
        if result.stdout:
            f.write(f"STDOUT:\n{result.stdout}\n")
        if result.stderr:
            f.write(f"STDERR:\n{result.stderr}\n")
        
        if (phase2 / "class").exists():
            f.write("SUCCESS: CLASS directory created\n")
            if (phase2 / "class" / "Makefile").exists():
                f.write("SUCCESS: Makefile found\n")
            else:
                f.write("WARNING: Makefile not found\n")
        else:
            f.write("ERROR: CLASS directory not created\n")
            
    except subprocess.TimeoutExpired:
        f.write("ERROR: Clone timed out after 120 seconds\n")
    except Exception as e:
        f.write(f"ERROR: {e}\n")

print("Status written to clone_status.txt")

