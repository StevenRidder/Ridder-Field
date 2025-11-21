#!/usr/bin/env python3
"""
Stress test the Ridder Field implementation
Try to break it with extreme parameters
"""

import subprocess
import os
import sys

def create_test_ini(name, params, description):
    """Create a test .ini file with given parameters"""
    content = f"""# STRESS TEST: {description}
root = output/stress_{name}_
output = tCl,pCl,lCl,mPk
lensing = yes
modes = s
gauge = newtonian
l_max_scalars = 2500
P_k_max_h/Mpc = 1.0
z_pk = 0

# Standard cosmology
h = 0.6736
T_cmb = 2.7255
omega_b = 0.02237
omega_cdm = 0.1200
Omega_fld = 0.0

# Ridder Field - TEST PARAMETERS
Lambda_EDE_ridder = {params.get('Lambda', 1.0)}
f_axion_ridder = {params.get('f', 1e27)}
theta_i_ridder = {params.get('theta', 2.8)}
beta_ridder = {params.get('beta', 0.01)}
n_ridder = {params.get('n', 3)}

# Primordial
A_s = 2.1e-9
n_s = 0.9665
tau_reio = 0.0561

# Precision
background_verbose = 1
thermodynamics_verbose = 1
"""
    
    filename = f"stress_tests/{name}.ini"
    os.makedirs("stress_tests", exist_ok=True)
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def run_test(name, params, description):
    """Run a single stress test"""
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"DESC: {description}")
    print(f"PARAMS: {params}")
    print('='*70)
    
    ini_file = create_test_ini(name, params, description)
    
    try:
        result = subprocess.run(
            ["../phase2/class/class", ini_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print("✅ PASS: Completed successfully")
            # Extract r_s if available
            for line in result.stdout.split('\n'):
                if 'sound horizon rs' in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print(f"❌ FAIL: Exit code {result.returncode}")
            # Print last 10 lines of error
            error_lines = result.stderr.split('\n')[-10:]
            for line in error_lines:
                if line.strip():
                    print(f"   {line}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️  TIMEOUT: Took > 60 seconds (likely hung)")
        return False
    except Exception as e:
        print(f"💥 CRASH: {str(e)}")
        return False

# Define stress tests
tests = [
    # Boundary conditions
    ("lambda_zero", {"Lambda": 0.0}, "No EDE (should reduce to ΛCDM)"),
    ("lambda_tiny", {"Lambda": 1e-10}, "Tiny EDE (near-ΛCDM)"),
    ("lambda_huge", {"Lambda": 100.0}, "Huge EDE (should fail or be unphysical)"),
    
    # f_axion extremes
    ("f_tiny", {"f": 1e10}, "Narrow well (high frequency oscillations)"),
    ("f_huge", {"f": 1e35}, "Wide well (slow roll)"),
    
    # theta_i extremes
    ("theta_zero", {"theta": 0.0}, "No displacement (no EDE)"),
    ("theta_pi", {"theta": 3.14159}, "Maximum displacement"),
    ("theta_negative", {"theta": -2.8}, "Negative displacement"),
    
    # beta extremes
    ("beta_zero", {"beta": 0.0}, "No DM coupling"),
    ("beta_tiny", {"beta": 1e-10}, "Tiny DM coupling"),
    ("beta_huge", {"beta": 10.0}, "Strong DM coupling (likely unphysical)"),
    
    # Combined extremes
    ("all_max", {"Lambda": 10.0, "f": 1e30, "theta": 3.0, "beta": 1.0}, "Everything cranked up"),
    ("all_min", {"Lambda": 0.01, "f": 1e20, "theta": 0.1, "beta": 0.0}, "Everything minimal"),
    
    # Edge cases
    ("w_eff_test", {"n": 1}, "n=1 gives w=-1 (cosmological constant)"),
    ("w_eff_test2", {"n": 5}, "n=5 gives w=0.67 (stiff)"),
]

# Run all tests
print("\n" + "="*70)
print("RIDDER FIELD STRESS TEST SUITE")
print("="*70)

results = {}
for name, params, desc in tests:
    success = run_test(name, params, desc)
    results[name] = success

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

passed = sum(results.values())
total = len(results)

print(f"\nPassed: {passed}/{total}")
print(f"Failed: {total-passed}/{total}")

print("\nDetailed Results:")
for name, success in results.items():
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"  {status}: {name}")

if passed < total:
    print("\n⚠️  HOLES FOUND! See failures above.")
    sys.exit(1)
else:
    print("\n✅ All tests passed! (But this doesn't mean there are no holes...)")
    sys.exit(0)

