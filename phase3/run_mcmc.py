#!/usr/bin/env python3
"""
Run MCMC chains for Ridder Field model using Cobaya

This script:
1. Loads the parameter file
2. Runs MCMC chains
3. Monitors convergence
4. Saves results
"""

import os
import sys
from cobaya import run
from cobaya.log import LoggedError

def main():
    print("\n" + "="*70)
    print("RIDDER FIELD: MCMC PARAMETER FITTING")
    print("="*70)
    
    # Check if Cobaya is installed
    try:
        import cobaya
        print(f"✓ Cobaya version: {cobaya.__version__}")
    except ImportError:
        print("✗ Error: Cobaya not installed")
        print("  Run: pip3 install --user cobaya")
        return 1
    
    # Check if CLASS is available
    class_dir = "/Users/steveridder/Git/Ridder Field/phase2/class"
    if not os.path.exists(class_dir):
        print(f"✗ Error: CLASS directory not found: {class_dir}")
        return 1
    
    # Check if parameter file exists
    param_file = "ridder_field.yaml"
    if not os.path.exists(param_file):
        print(f"✗ Error: Parameter file not found: {param_file}")
        return 1
    
    print(f"\n✓ Parameter file: {param_file}")
    print(f"✓ CLASS directory: {class_dir}")
    
    # Load parameter file
    print("\n" + "-"*70)
    print("Loading parameter file...")
    print("-"*70)
    
    try:
        from cobaya.yaml import yaml_load_file
        info = yaml_load_file(param_file)
        print("✓ Parameter file loaded")
    except Exception as e:
        print(f"✗ Error loading parameter file: {e}")
        return 1
    
    # Check if likelihoods are available
    print("\n" + "-"*70)
    print("Checking likelihoods...")
    print("-"*70)
    
    # For now, we'll run without likelihoods to test CLASS interface
    # In production, you'd download Planck data and configure properly
    print("⚠ Note: Running without likelihoods (test mode)")
    print("   To run with data, download Planck 2018 likelihoods first")
    
    # Run MCMC
    print("\n" + "-"*70)
    print("Starting MCMC chains...")
    print("-"*70)
    print("\nThis will run MCMC to explore parameter space.")
    print("Press Ctrl+C to stop early.\n")
    
    try:
        updated_info, sampler = run(info)
        print("\n✓ MCMC completed successfully!")
        
        # Print summary
        print("\n" + "="*70)
        print("RESULTS SUMMARY")
        print("="*70)
        print(f"\nChains saved to: {info.get('output', 'chains/ridder_field')}")
        print("\nTo analyze results, run:")
        print("  python3 analyze_results.py")
        
    except KeyboardInterrupt:
        print("\n\n⚠ MCMC interrupted by user")
        print("Partial results may be available in chains/ directory")
        return 0
    except LoggedError as e:
        print(f"\n✗ Error during MCMC: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

