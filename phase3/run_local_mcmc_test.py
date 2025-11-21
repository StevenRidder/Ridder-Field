#!/usr/bin/env python3
"""
Local MCMC Test for Ridder Field
Minimal test without Planck data - just explores parameter space
"""

import os
import sys

def main():
    print("\n" + "="*70)
    print("RIDDER FIELD: LOCAL MCMC TEST")
    print("="*70)
    print("\nThis is a MINIMAL test to verify MCMC setup works.")
    print("It will:")
    print("  1. Run CLASS with varying theta_i and beta")
    print("  2. Compute r_s for each parameter combination")
    print("  3. Sample ~500 points (takes ~5-10 minutes)")
    print("  4. Check if MCMC converges")
    print("\nNO Planck data needed - this is just a technical test.")
    print("="*70 + "\n")
    
    # Check if Cobaya is installed
    try:
        import cobaya
        print(f"✓ Cobaya version: {cobaya.__version__}")
    except ImportError:
        print("✗ Error: Cobaya not installed")
        print("\nTo install:")
        print("  pip3 install cobaya")
        print("\nOr if that fails:")
        print("  python3 -m pip install --user cobaya")
        return 1
    
    # Check if CLASS is compiled
    class_dir = "/Users/steveridder/Git/Ridder-Field/phase2/class"
    class_exe = os.path.join(class_dir, "class")
    if not os.path.exists(class_exe):
        print(f"✗ Error: CLASS executable not found: {class_exe}")
        print("\nTo compile CLASS:")
        print(f"  cd {class_dir}")
        print("  make clean && make class")
        return 1
    
    print(f"✓ CLASS executable: {class_exe}")
    
    # Check if parameter file exists
    param_file = "ridder_local_test.yaml"
    if not os.path.exists(param_file):
        print(f"✗ Error: Parameter file not found: {param_file}")
        return 1
    
    print(f"✓ Parameter file: {param_file}")
    
    # Create chains directory
    os.makedirs("chains", exist_ok=True)
    print(f"✓ Output directory: chains/")
    
    # Run MCMC
    print("\n" + "-"*70)
    print("Starting MCMC test...")
    print("-"*70)
    print("\nThis will take ~5-10 minutes on a Mac.")
    print("You'll see CLASS running for each parameter combination.")
    print("Press Ctrl+C to stop early.\n")
    
    try:
        from cobaya import run
        from cobaya.yaml import yaml_load_file
        
        # Load parameter file
        info = yaml_load_file(param_file)
        
        # Run MCMC
        updated_info, sampler = run(info)
        
        print("\n" + "="*70)
        print("✅ MCMC TEST COMPLETED!")
        print("="*70)
        
        # Get results
        from getdist.mcsamples import loadMCSamples
        samples = loadMCSamples("chains/ridder_local_test")
        
        print(f"\nSamples collected: {samples.numrows}")
        print(f"Parameters: {samples.getParamNames().list()}")
        
        # Print mean values
        print("\nMean parameter values:")
        for param in ['theta_i_ridder', 'beta_ridder']:
            if param in samples.getParamNames().list():
                mean = samples.mean(param)
                std = samples.std(param)
                print(f"  {param}: {mean:.4f} ± {std:.4f}")
        
        # Check convergence
        print("\nConvergence check:")
        try:
            R = sampler.products()["sample"].R()
            print(f"  Gelman-Rubin R-1: {R:.4f}")
            if R < 0.1:
                print("  ✅ Converged (R-1 < 0.1)")
            else:
                print("  ⚠️  Not fully converged (need more samples)")
        except:
            print("  (R-1 not available for single chain)")
        
        print("\n" + "="*70)
        print("NEXT STEPS:")
        print("="*70)
        print("\n1. If this worked, you're ready for full MCMC!")
        print("2. To run with Planck data:")
        print("   - Download data: cobaya-install ridder_mcmc.yaml")
        print("   - Run: python3 run_mcmc.py")
        print("\n3. Or deploy to Azure for cluster run")
        print("   - See: AZURE_DEPLOYMENT_GUIDE.md")
        
    except KeyboardInterrupt:
        print("\n\n⚠ MCMC interrupted by user")
        print("Partial results may be in chains/ directory")
        return 0
    except Exception as e:
        print(f"\n✗ Error during MCMC: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*70)
        print("TROUBLESHOOTING:")
        print("="*70)
        print("\n1. Make sure Cobaya is installed:")
        print("   pip3 install cobaya")
        print("\n2. Make sure CLASS is compiled:")
        print("   cd phase2/class && make class")
        print("\n3. Check the error message above for details")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

