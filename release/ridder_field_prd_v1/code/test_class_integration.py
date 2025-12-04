#!/usr/bin/env python3
"""
Test CLASS integration with Cobaya for Ridder Field model

This script tests if:
1. CLASS Python interface works
2. Ridder field parameters are recognized
3. We can compute observables
"""

import sys
import os

# Detect environment and set CLASS path
home = os.path.expanduser("~")
if os.path.exists(os.path.join(home, "Ridder-Field")):
    # VM environment
    class_dir = os.path.join(home, "Ridder-Field/phase2/class")
else:
    # Mac environment  
    class_dir = "/Users/steveridder/Git/Ridder-Field/phase2/class"
sys.path.insert(0, os.path.join(class_dir, "python"))

def test_class_interface():
    """Test if CLASS Python interface works"""
    print("\n" + "="*70)
    print("TEST 1: CLASS Python Interface")
    print("="*70)
    
    try:
        import classy
        print("✓ classy module imported")
    except ImportError as e:
        print(f"✗ Error importing classy: {e}")
        print("  Try: cd phase2/class/python && python3 setup.py build_ext --inplace")
        return False
    
    # Test basic CLASS call
    try:
        cosmo = classy.Class()
        cosmo.set({
            'h': 0.6736,
            'omega_b': 0.02237,
            'omega_cdm': 0.1200,
            'Omega_Lambda': 0.6911,
            'A_s': 2.1e-9,
            'n_s': 0.9665,
            'tau_reio': 0.0561,
            'output': 'tCl',
            'l_max_scalars': 10,
        })
        cosmo.compute()
        
        H0 = cosmo.h() * 100.0
        print(f"✓ CLASS runs successfully")
        print(f"  H0 = {H0:.2f} km/s/Mpc")
        
        cosmo.struct_cleanup()
        cosmo.empty()
        return True
        
    except Exception as e:
        print(f"✗ Error running CLASS: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ridder_parameters():
    """Test if Ridder field parameters are recognized"""
    print("\n" + "="*70)
    print("TEST 2: Ridder Field Parameters")
    print("="*70)
    
    try:
        import classy
        cosmo = classy.Class()
        
        # Try to set Ridder field parameters (v3_canon mode)
        params = {
            'h': 0.6736,
            'omega_b': 0.02237,
            'omega_cdm': 0.1200,
            'A_s': 2.1e-9,
            'n_s': 0.9665,
            'tau_reio': 0.0561,
            'output': 'tCl',
            'l_max_scalars': 10,
            'gauge': 'newtonian',
            # Ridder v3 parameters
            'use_ridder': 'yes',
            'ridder_model_type': 'v3_canon',
            'ridder_use_shelf': 'yes',
            'ridder_use_tail': 'no',
            'ridder_f_eV': 2.0e26,
            'theta_i_ridder': 2.8,
            'ridder_Lambda_EDE_eV': 0.5,
            'ridder_a_c': 0.0003,
            'ridder_sigma_lna': 0.6,
            'ridder_c_slow': 0.0,
            'ridder_sigma_E': 0.4,
            'beta_ridder': 0.0,
            'beta_z_c': 3000.0,
            'beta_sigma_z': 0.5,
        }
        
        cosmo.set(params)
        print("✓ Ridder field parameters accepted")
        
        # Try to compute
        try:
            cosmo.compute()
            print("✓ CLASS computes with Ridder field")
            
            H0 = cosmo.h() * 100.0
            print(f"  H0 = {H0:.2f} km/s/Mpc")
            
            cosmo.struct_cleanup()
            cosmo.empty()
            return True
            
        except Exception as e:
            print(f"✗ Error computing with Ridder field: {e}")
            print("  This might indicate a problem with the implementation")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cobaya_integration():
    """Test if Cobaya can use CLASS with Ridder field"""
    print("\n" + "="*70)
    print("TEST 3: Cobaya + CLASS Integration")
    print("="*70)
    
    try:
        import cobaya
        print(f"✓ Cobaya version: {cobaya.__version__}")
    except ImportError:
        print("✗ Cobaya not installed")
        print("  Run: pip3 install --user cobaya")
        return False
    
    # Create minimal info dict with v3 Ridder parameters
    info = {
        'theory': {
            'classy': {
                'path': class_dir,
                'extra_args': {
                    'output': 'tCl',
                    'l_max_scalars': 10,
                    'gauge': 'newtonian',
                    'use_ridder': 'yes',
                    'ridder_model_type': 'v3_canon',
                    'ridder_use_shelf': 'yes',
                    'ridder_use_tail': 'no',
                    'ridder_f_eV': 2.0e26,
                    'theta_i_ridder': 2.8,
                    'ridder_c_slow': 0.0,
                    'ridder_sigma_E': 0.4,
                    'beta_ridder': 0.0,
                    'beta_z_c': 3000.0,
                    'beta_sigma_z': 0.5,
                }
            }
        },
        'params': {
            'H0': 67.36,
            'omega_b': 0.02237,
            'omega_cdm': 0.1200,
            'logA': 3.044,
            'n_s': 0.9665,
            'tau_reio': 0.0561,
            'ridder_Lambda_EDE_eV': 0.5,
            'ridder_a_c': 0.0003,
            'ridder_sigma_lna': 0.6,
        },
        'likelihood': {
            'one': None  # Dummy likelihood for testing
        },
        'sampler': {'evaluate': {}},
    }
    
    try:
        from cobaya.model import get_model
        model = get_model(info)
        print("✓ Cobaya model created")
        
        # Test evaluation
        loglikes, derived = model.loglikes({})
        print("✓ Model evaluation works")
        print(f"  Log-likelihood: {loglikes[0]:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*70)
    print("RIDDER FIELD: CLASS + COBAYA INTEGRATION TEST")
    print("="*70)
    
    results = []
    
    # Test 1: CLASS interface
    results.append(("CLASS Interface", test_class_interface()))
    
    # Test 2: Ridder parameters
    results.append(("Ridder Parameters", test_ridder_parameters()))
    
    # Test 3: Cobaya integration
    results.append(("Cobaya Integration", test_cobaya_integration()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nThe Ridder field implementation is ready for MCMC fitting.")
        print("Next: Download Planck data and run full chains.")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nFix the issues above before running MCMC.")
    
    print("="*70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())

