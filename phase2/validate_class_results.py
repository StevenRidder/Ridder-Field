#!/usr/bin/env python3
"""
Validation script: Compare CLASS results with Phase 1 Python results

This script:
1. Runs CLASS with LambdaCDM baseline (Lambda_EDE = 0)
2. Runs CLASS with EDE mode (Lambda_EDE > 0)
3. Extracts key observables: H0, r_s, z_eq, Omega_*
4. Compares with Phase 1 Python results
5. Creates validation plots
"""

import subprocess
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add CLASS Python interface path
sys.path.insert(0, '/Users/steveridder/Git/Ridder Field/phase2/class/python')

try:
    import classy
except ImportError:
    print("Warning: classy not found. Will use CLASS binary directly.")
    classy = None

# Phase 1 reference values (from PHASE1_CANONICAL.md)
PHASE1_REF = {
    'H0': 67.36,  # km/s/Mpc
    'r_s': 147.0,  # Mpc (ΛCDM value)
    'z_eq': 3400,
    'Omega_b': 0.0486,
    'Omega_cdm': 0.258,
    'Omega_Lambda': 0.691,
    'n_s': 0.96498,
    'r': 0.00350,
}

def run_class_binary(ini_file):
    """Run CLASS binary and capture output"""
    class_dir = '/Users/steveridder/Git/Ridder Field/phase2/class'
    class_binary = os.path.join(class_dir, 'class')
    
    if not os.path.exists(class_binary):
        raise FileNotFoundError(f"CLASS binary not found at {class_binary}")
    
    ini_path = os.path.join(class_dir, ini_file)
    if not os.path.exists(ini_path):
        raise FileNotFoundError(f"INI file not found at {ini_path}")
    
    result = subprocess.run(
        [class_binary, ini_file],
        cwd=class_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"CLASS error output:\n{result.stderr}")
        raise RuntimeError(f"CLASS failed with return code {result.returncode}")
    
    return result.stdout, result.stderr

def extract_class_observables(ini_file):
    """Extract key observables from CLASS output"""
    stdout, stderr = run_class_binary(ini_file)
    
    # Parse output for key values
    observables = {}
    
    # Extract age
    for line in stdout.split('\n'):
        if 'age =' in line:
            try:
                age_str = line.split('age =')[1].split('Gyr')[0].strip()
                observables['age'] = float(age_str)
            except:
                pass
    
    # Extract equality redshift
    for line in stdout.split('\n'):
        if 'radiation/matter equality at z =' in line:
            try:
                z_eq_str = line.split('z =')[1].strip()
                observables['z_eq'] = float(z_eq_str)
            except:
                pass
    
    # Try to use classy if available for more detailed extraction
    if classy is not None:
        try:
            class_dir = '/Users/steveridder/Git/Ridder Field/phase2/class'
            ini_path = os.path.join(class_dir, ini_file)
            
            cosmo = classy.Class()
            cosmo.set(ini_path)
            cosmo.compute()
            
            # Extract key parameters
            observables['H0'] = cosmo.h() * 100.0  # Convert to km/s/Mpc
            observables['Omega_b'] = cosmo.Omega_b()
            observables['Omega_cdm'] = cosmo.Omega_cdm()
            observables['Omega_Lambda'] = cosmo.Omega_Lambda()
            observables['age'] = cosmo.age()
            
            # Sound horizon at drag epoch
            observables['r_s'] = cosmo.rs_drag()
            
            # Get background evolution
            z_array = np.logspace(-2, 3, 100)
            H_array = np.array([cosmo.H(z) for z in z_array])
            observables['z_array'] = z_array
            observables['H_array'] = H_array
            
            cosmo.struct_cleanup()
            cosmo.empty()
            
        except Exception as e:
            print(f"Warning: Could not use classy: {e}")
            print("Will parse binary output instead")
    
    return observables

def compare_results(lcdm_results, ede_results, phase1_ref):
    """Compare CLASS results with Phase 1 reference"""
    
    print("\n" + "="*70)
    print("VALIDATION: CLASS vs Phase 1 Python")
    print("="*70)
    
    print("\n--- LambdaCDM Baseline (Lambda_EDE = 0) ---")
    if 'H0' in lcdm_results:
        h0_diff = abs(lcdm_results['H0'] - phase1_ref['H0']) / phase1_ref['H0'] * 100
        print(f"  H0: {lcdm_results['H0']:.2f} km/s/Mpc (Phase 1: {phase1_ref['H0']:.2f})")
        print(f"      Difference: {h0_diff:.2f}%")
        if h0_diff < 5:
            print(f"      ✓ Within 5%")
    
    if 'r_s' in lcdm_results:
        rs_diff = abs(lcdm_results['r_s'] - phase1_ref['r_s']) / phase1_ref['r_s'] * 100
        print(f"  r_s: {lcdm_results['r_s']:.2f} Mpc (Phase 1: {phase1_ref['r_s']:.2f})")
        print(f"       Difference: {rs_diff:.2f}%")
        if rs_diff < 10:
            print(f"       ✓ Within 10%")
    
    if 'z_eq' in lcdm_results:
        zeq_diff = abs(lcdm_results['z_eq'] - phase1_ref['z_eq']) / phase1_ref['z_eq'] * 100
        print(f"  z_eq: {lcdm_results['z_eq']:.1f} (Phase 1: {phase1_ref['z_eq']:.0f})")
        print(f"        Difference: {zeq_diff:.2f}%")
        if zeq_diff < 5:
            print(f"        ✓ Within 5%")
    
    print("\n--- EDE Mode (Lambda_EDE > 0) ---")
    if 'H0' in ede_results and 'H0' in lcdm_results:
        h0_shift = (ede_results['H0'] - lcdm_results['H0']) / lcdm_results['H0'] * 100
        print(f"  H0 shift: {h0_shift:+.2f}%")
        if h0_shift > 0:
            print(f"            ✓ H0 increased (expected for EDE)")
    
    if 'r_s' in ede_results and 'r_s' in lcdm_results:
        rs_shift = (ede_results['r_s'] - lcdm_results['r_s']) / lcdm_results['r_s'] * 100
        print(f"  r_s shift: {rs_shift:+.2f}%")
        if rs_shift < 0:
            print(f"            ✓ r_s decreased (expected for EDE)")
    
    print("\n" + "="*70)
    print("KEY QUESTION: Have we proven anything?")
    print("="*70)
    
    # Check if we've proven anything
    proven = []
    
    if 'H0' in lcdm_results:
        if abs(lcdm_results['H0'] - phase1_ref['H0']) / phase1_ref['H0'] < 0.05:
            proven.append("✓ CLASS reproduces Phase 1 H0 (within 5%)")
    
    if 'r_s' in lcdm_results:
        if abs(lcdm_results['r_s'] - phase1_ref['r_s']) / phase1_ref['r_s'] < 0.10:
            proven.append("✓ CLASS reproduces Phase 1 r_s (within 10%)")
    
    if 'H0' in ede_results and 'H0' in lcdm_results:
        if ede_results['H0'] > lcdm_results['H0']:
            proven.append("✓ EDE increases H0 (as expected)")
    
    if 'r_s' in ede_results and 'r_s' in lcdm_results:
        if ede_results['r_s'] < lcdm_results['r_s']:
            proven.append("✓ EDE decreases r_s (as expected)")
    
    if proven:
        print("\n✅ PROVEN:")
        for item in proven:
            print(f"  {item}")
    else:
        print("\n⚠️  No clear validation yet - need to check results")
    
    return proven

def plot_comparison(lcdm_results, ede_results, phase1_ref):
    """Create comparison plots"""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('CLASS Validation: Ridder Field Implementation', fontsize=14, fontweight='bold')
    
    # Plot 1: H(z) evolution
    ax1 = axes[0, 0]
    if 'z_array' in lcdm_results and 'H_array' in lcdm_results:
        ax1.loglog(lcdm_results['z_array'], lcdm_results['H_array'], 
                  'b-', label='CLASS ΛCDM', linewidth=2)
    if 'z_array' in ede_results and 'H_array' in ede_results:
        ax1.loglog(ede_results['z_array'], ede_results['H_array'], 
                  'r--', label='CLASS EDE', linewidth=2)
    ax1.set_xlabel('Redshift z')
    ax1.set_ylabel('H(z) [km/s/Mpc]')
    ax1.set_title('Hubble Parameter Evolution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Key observables comparison
    ax2 = axes[0, 1]
    if 'H0' in lcdm_results and 'r_s' in lcdm_results:
        obs_names = ['H0', 'r_s']
        lcdm_vals = [lcdm_results.get('H0', 0), lcdm_results.get('r_s', 0)]
        ref_vals = [phase1_ref.get('H0', 0), phase1_ref.get('r_s', 0)]
        
        x = np.arange(len(obs_names))
        width = 0.35
        ax2.bar(x - width/2, [lcdm_vals[0]/ref_vals[0]*100 if ref_vals[0] > 0 else 0,
                               lcdm_vals[1]/ref_vals[1]*100 if ref_vals[1] > 0 else 0],
                width, label='CLASS/Phase1', alpha=0.7)
        ax2.axhline(100, color='k', linestyle='--', alpha=0.5, label='Perfect match')
        ax2.set_ylabel('Ratio (%)')
        ax2.set_title('Observables: CLASS / Phase 1')
        ax2.set_xticks(x)
        ax2.set_xticklabels(obs_names)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
    
    # Plot 3: EDE effect on r_s
    ax3 = axes[1, 0]
    if 'r_s' in lcdm_results and 'r_s' in ede_results:
        models = ['ΛCDM', 'EDE']
        rs_vals = [lcdm_results['r_s'], ede_results['r_s']]
        colors = ['blue', 'red']
        bars = ax3.bar(models, rs_vals, color=colors, alpha=0.7)
        ax3.axhline(phase1_ref['r_s'], color='k', linestyle='--', 
                   label=f"Phase 1 ref: {phase1_ref['r_s']:.1f} Mpc")
        ax3.set_ylabel('r_s [Mpc]')
        ax3.set_title('Sound Horizon: EDE Effect')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Add percentage change
        if len(rs_vals) == 2:
            change = (rs_vals[1] - rs_vals[0]) / rs_vals[0] * 100
            ax3.text(0.5, max(rs_vals) * 0.95, f'{change:+.1f}%', 
                    ha='center', fontweight='bold')
    
    # Plot 4: Summary
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    summary_text = "VALIDATION SUMMARY\n\n"
    summary_text += f"ΛCDM Baseline:\n"
    if 'H0' in lcdm_results:
        summary_text += f"  H0 = {lcdm_results['H0']:.2f} km/s/Mpc\n"
    if 'r_s' in lcdm_results:
        summary_text += f"  r_s = {lcdm_results['r_s']:.2f} Mpc\n"
    if 'z_eq' in lcdm_results:
        summary_text += f"  z_eq = {lcdm_results['z_eq']:.1f}\n"
    
    summary_text += f"\nEDE Mode:\n"
    if 'H0' in ede_results:
        summary_text += f"  H0 = {ede_results['H0']:.2f} km/s/Mpc\n"
    if 'r_s' in ede_results:
        summary_text += f"  r_s = {ede_results['r_s']:.2f} Mpc\n"
    
    summary_text += f"\nPhase 1 Reference:\n"
    summary_text += f"  H0 = {phase1_ref['H0']:.2f} km/s/Mpc\n"
    summary_text += f"  r_s = {phase1_ref['r_s']:.1f} Mpc\n"
    
    ax4.text(0.1, 0.5, summary_text, fontfamily='monospace', 
            verticalalignment='center', fontsize=10)
    
    plt.tight_layout()
    
    output_file = '/Users/steveridder/Git/Ridder Field/phase2/class_validation.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Plot saved to: {output_file}")
    
    return fig

def main():
    """Main validation routine"""
    
    print("\n" + "="*70)
    print("RIDDER FIELD: CLASS IMPLEMENTATION VALIDATION")
    print("="*70)
    print("\nThis script validates the CLASS implementation by:")
    print("  1. Running ΛCDM baseline (Lambda_EDE = 0)")
    print("  2. Running EDE mode (Lambda_EDE > 0)")
    print("  3. Comparing with Phase 1 Python results")
    print("  4. Checking if EDE effects are visible")
    
    # Run CLASS for both cases
    print("\n" + "-"*70)
    print("Step 1: Running CLASS - ΛCDM Baseline")
    print("-"*70)
    try:
        lcdm_results = extract_class_observables('test_ridder_lcdm.ini')
        print("✓ ΛCDM run completed")
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    print("\n" + "-"*70)
    print("Step 2: Running CLASS - EDE Mode")
    print("-"*70)
    try:
        ede_results = extract_class_observables('test_ridder_ede.ini')
        print("✓ EDE run completed")
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    # Compare results
    print("\n" + "-"*70)
    print("Step 3: Comparing Results")
    print("-"*70)
    proven = compare_results(lcdm_results, ede_results, PHASE1_REF)
    
    # Create plots
    print("\n" + "-"*70)
    print("Step 4: Creating Validation Plots")
    print("-"*70)
    try:
        plot_comparison(lcdm_results, ede_results, PHASE1_REF)
        print("✓ Plots created")
    except Exception as e:
        print(f"⚠ Warning: Could not create plots: {e}")
    
    print("\n" + "="*70)
    print("VALIDATION COMPLETE")
    print("="*70)
    
    if proven:
        print(f"\n✅ We've proven {len(proven)} things!")
        print("\nThe Ridder field implementation in CLASS:")
        for item in proven:
            print(f"  {item}")
    else:
        print("\n⚠️  Results need further investigation")
        print("Check the output files and plots for details")

if __name__ == '__main__':
    main()

