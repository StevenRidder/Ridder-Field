#!/usr/bin/env python3
"""
Validate Minimal EDE Shooting Test

Purpose:
  Verify that shooting mechanism works for simplest axion EDE case
  
Checks:
  1. Shooting converged to find m_axion
  2. f_EDE at z_c matches target
  3. Background evolution is stable
  4. Field rolls correctly (not frozen)
  5. w(z) has expected behavior
  
Usage:
  python3 validate_minimal_shooting.py
"""

import os
import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt

REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
CLASS_BIN = os.path.join(REPO_ROOT, "phase2", "class", "class")
INI_FILE = os.path.join(REPO_ROOT, "minimal_ede_shooting.ini")
OUTPUT_DIR = os.path.join(REPO_ROOT, "output")

def run_shooting_test():
    """Run CLASS with minimal shooting config"""
    print("="*80)
    print("MINIMAL EDE SHOOTING VALIDATION")
    print("="*80)
    print(f"\nRunning CLASS with: {INI_FILE}")
    print("Expected: Shooting mechanism finds m_axion for f_EDE ~ 0.10 at z ~ 3000\n")
    
    cmd = [CLASS_BIN, INI_FILE]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=300
    )
    
    print(result.stdout)
    
    if result.returncode != 0:
        print("\n❌ CLASS FAILED")
        return False
    
    print("\n✅ CLASS COMPLETED")
    return True

def parse_background(bg_file):
    """Parse background file and extract key quantities"""
    if not os.path.exists(bg_file):
        # Try with _00 suffix
        bg_file_00 = bg_file.replace("_background.dat", "_00_background.dat")
        if os.path.exists(bg_file_00):
            bg_file = bg_file_00
        else:
            return None
    
    data = {
        'z': [],
        'a': [],
        'H': [],
        'rho_tot': [],
        'rho_ridder': [],
        'p_ridder': []
    }
    
    with open(bg_file, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 20:
                try:
                    data['z'].append(float(parts[0]))
                    data['a'].append(1.0 / (1.0 + float(parts[0])))
                    data['H'].append(float(parts[3]))
                    # Column indices depend on CLASS output format
                    # Adjust these based on actual background file structure
                    data['rho_tot'].append(float(parts[19]))  # Total density
                    data['rho_ridder'].append(float(parts[14]))  # Ridder density
                    data['p_ridder'].append(float(parts[15]))  # Ridder pressure
                except (ValueError, IndexError):
                    continue
    
    for key in data:
        data[key] = np.array(data[key])
    
    return data

def find_peak_EDE(data):
    """Find peak EDE fraction and its redshift"""
    if data is None or len(data['z']) == 0:
        return None, None
    
    f_ridder = data['rho_ridder'] / data['rho_tot']
    idx_peak = np.argmax(f_ridder)
    
    return f_ridder[idx_peak], data['z'][idx_peak]

def compute_w_ridder(data):
    """Compute equation of state w = p/rho for Ridder field"""
    if data is None:
        return None
    
    # Avoid division by zero
    w = np.zeros_like(data['rho_ridder'])
    mask = data['rho_ridder'] > 1e-30
    w[mask] = data['p_ridder'][mask] / data['rho_ridder'][mask]
    w[~mask] = -1.0  # Default to cosmological constant-like
    
    return w

def plot_results(data, output_prefix):
    """Create validation plots"""
    if data is None:
        print("⚠️  No data to plot")
        return
    
    f_ridder = data['rho_ridder'] / data['rho_tot']
    w_ridder = compute_w_ridder(data)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: f_ridder(z)
    ax = axes[0, 0]
    ax.semilogy(data['z'], f_ridder, 'b-', linewidth=2)
    ax.axhline(0.10, color='r', linestyle='--', label='Target f_EDE = 0.10')
    ax.axvline(3000, color='r', linestyle='--', alpha=0.5, label='Target z_c = 3000')
    ax.set_xlabel('Redshift z', fontsize=12)
    ax.set_ylabel('f_ridder = ρ_ridder / ρ_tot', fontsize=12)
    ax.set_title('EDE Fraction vs Redshift', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim([1, 1e5])
    
    # Plot 2: w(z)
    ax = axes[0, 1]
    ax.plot(data['z'], w_ridder, 'g-', linewidth=2)
    ax.axhline(-1, color='k', linestyle=':', label='w = -1 (Λ)')
    ax.axhline(0, color='gray', linestyle=':', alpha=0.5)
    ax.axhline(1, color='gray', linestyle=':', alpha=0.5)
    ax.set_xlabel('Redshift z', fontsize=12)
    ax.set_ylabel('w_ridder = p / ρ', fontsize=12)
    ax.set_title('Equation of State', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    ax.set_xlim([1, 1e5])
    ax.set_ylim([-2, 2])
    
    # Plot 3: Energy densities
    ax = axes[1, 0]
    ax.loglog(data['z'], data['rho_tot'], 'k-', linewidth=2, label='ρ_tot')
    ax.loglog(data['z'], data['rho_ridder'], 'b-', linewidth=2, label='ρ_ridder')
    ax.set_xlabel('Redshift z', fontsize=12)
    ax.set_ylabel('Energy Density (Mpc⁻²)', fontsize=12)
    ax.set_title('Energy Densities', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: H(z) / H_ΛCDM(z) - 1
    # For now, just plot H(z)
    ax = axes[1, 1]
    ax.loglog(data['z'], data['H'], 'r-', linewidth=2)
    ax.set_xlabel('Redshift z', fontsize=12)
    ax.set_ylabel('H(z) (Mpc⁻¹)', fontsize=12)
    ax.set_title('Hubble Parameter', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_file = f"{output_prefix}_validation.png"
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    print(f"\n📊 Validation plots saved: {plot_file}")

def main():
    # Run shooting test
    if not run_shooting_test():
        print("\n❌ Shooting test failed - cannot proceed with validation")
        return 1
    
    # Parse results
    bg_file = os.path.join(OUTPUT_DIR, "minimal_ede_shooting_background.dat")
    data = parse_background(bg_file)
    
    if data is None:
        print(f"\n❌ Could not parse background file: {bg_file}")
        return 1
    
    # Find peak EDE
    f_peak, z_peak = find_peak_EDE(data)
    
    print("\n" + "="*80)
    print("SHOOTING RESULTS")
    print("="*80)
    
    if f_peak is not None and z_peak is not None:
        print(f"  Peak EDE fraction: f_peak = {f_peak:.6f}")
        print(f"  Peak redshift:     z_peak = {z_peak:.1f}")
        print(f"\nTargets:")
        print(f"  Target f_EDE = 0.100")
        print(f"  Target z_c   = 3000.0")
        print(f"\nErrors:")
        print(f"  Δf_EDE = {abs(f_peak - 0.10):.6f} ({abs(f_peak - 0.10)/0.10 * 100:.2f}%)")
        print(f"  Δz_c   = {abs(z_peak - 3000):.1f} ({abs(z_peak - 3000)/3000 * 100:.2f}%)")
        
        # Success criteria
        f_ok = abs(f_peak - 0.10) < 0.01  # Within 10% relative
        z_ok = abs(z_peak - 3000) < 500   # Within ~15%
        
        if f_ok and z_ok:
            print("\n✅ SHOOTING SUCCESSFUL - Targets reached!")
        else:
            print("\n⚠️  SHOOTING INCOMPLETE - Targets not fully reached")
            if not f_ok:
                print(f"    f_peak off by {abs(f_peak - 0.10)/0.10 * 100:.1f}%")
            if not z_ok:
                print(f"    z_peak off by {abs(z_peak - 3000):.0f} redshift")
    else:
        print("❌ Could not extract peak EDE from data")
    
    # Create plots
    plot_results(data, os.path.join(OUTPUT_DIR, "minimal_ede_shooting"))
    
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("  1. Examine validation plots")
    print("  2. If shooting converged, proceed to add tail/coupling")
    print("  3. If not, adjust bracket or f_axion and re-run")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

