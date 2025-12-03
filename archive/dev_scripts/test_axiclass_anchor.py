#!/usr/bin/env python3
"""
Test AxiCLASS Anchor Point

Quick validation that published AxiCLASS parameters give reasonable EDE bump
"""

import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
CLASS_BIN = os.path.join(REPO_ROOT, "phase2", "class", "class")
INI_FILE = os.path.join(REPO_ROOT, "axiclass_anchor_test.ini")

def run_class():
    """Run CLASS with anchor test"""
    print("="*80)
    print("AXICLASS ANCHOR TEST")
    print("="*80)
    print(f"\nParameters (from AxiCLASS published values):")
    print(f"  m_axion = 1e5 H0 units")
    print(f"  f_axion = 0.4 M_Pl")
    print(f"  theta_i = 2.8 rad")
    print(f"  n_EDE = 3")
    print(f"\nRunning CLASS (shooting OFF)...\n")
    
    cmd = [CLASS_BIN, INI_FILE]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=120
    )
    
    # Print last 100 lines of output
    lines = result.stdout.split('\n')
    for line in lines[-100:]:
        print(line)
    
    if result.returncode != 0:
        print("\n" + "="*80)
        print("❌ CLASS FAILED")
        print("="*80)
        return False
    
    print("\n" + "="*80)
    print("✅ CLASS COMPLETED")
    print("="*80)
    return True

def parse_results():
    """Quick parse of f_EDE from output"""
    bg_file = os.path.join(REPO_ROOT, "output", "axiclass_anchor_00_background.dat")
    if not os.path.exists(bg_file):
        print(f"\n⚠️  Background file not found: {bg_file}")
        return
    
    # Simple parse: find max f_ridder
    max_f = 0.0
    z_at_max = 0.0
    
    with open(bg_file, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 20:
                try:
                    z = float(parts[0])
                    rho_ridder = float(parts[14])
                    rho_tot = float(parts[19])
                    if rho_tot > 0:
                        f_ridder = rho_ridder / rho_tot
                        if f_ridder > max_f:
                            max_f = f_ridder
                            z_at_max = z
                except (ValueError, IndexError, ZeroDivisionError):
                    continue
    
    print(f"\n📊 RESULTS:")
    print(f"  Peak f_EDE = {max_f:.6f}")
    print(f"  At z_peak = {z_at_max:.1f}")
    
    # Validation
    print(f"\n✓ VALIDATION:")
    checks = []
    
    if 0.05 <= max_f <= 0.20:
        print(f"  ✅ f_peak in reasonable range [0.05, 0.20]")
        checks.append(True)
    else:
        print(f"  ❌ f_peak = {max_f:.3f} outside [0.05, 0.20]")
        checks.append(False)
    
    if 1000 <= z_at_max <= 10000:
        print(f"  ✅ z_peak in reasonable range [1000, 10000]")
        checks.append(True)
    else:
        print(f"  ❌ z_peak = {z_at_max:.0f} outside [1000, 10000]")
        checks.append(False)
    
    if all(checks):
        print(f"\n🎉 ANCHOR POINT VALIDATED!")
        print(f"\nNext steps:")
        print(f"  1. Turn on shooting with bracket [5e4, 2e5] H0")
        print(f"  2. Target f_EDE = 0.13, z_c = 3000")
        print(f"  3. Let bisection find optimal m_axion")
    else:
        print(f"\n⚠️  ANCHOR NEEDS ADJUSTMENT")
        if max_f < 0.05:
            print(f"  → Bump too weak: Increase m_axion or theta_i")
        elif max_f > 0.20:
            print(f"  → Bump too strong: Reduce f_axion (try 0.2, 0.1, 0.05)")
        if z_at_max < 1000:
            print(f"  → Peak too late: Increase m_axion")
        elif z_at_max > 10000:
            print(f"  → Peak too early: Decrease m_axion")

def main():
    if not run_class():
        return 1
    
    parse_results()
    return 0

if __name__ == "__main__":
    sys.exit(main())

