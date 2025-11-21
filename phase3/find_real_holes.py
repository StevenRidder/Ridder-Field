#!/usr/bin/env python3
"""Find REAL holes by running CLASS correctly"""
import subprocess
import os

CLASS_DIR = "../phase2/class"
CLASS_BIN = f"{CLASS_DIR}/class"

def run_class(ini_content, test_name):
    """Run CLASS with given ini content"""
    # Write ini file in CLASS directory
    ini_path = f"{CLASS_DIR}/test_{test_name}.ini"
    with open(ini_path, 'w') as f:
        f.write(ini_content)
    
    try:
        result = subprocess.run(
            [CLASS_BIN, f"test_{test_name}.ini"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=CLASS_DIR
        )
        
        # Clean up
        os.remove(ini_path)
        
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -2, "", str(e)

def test(name, params, description):
    """Run a test"""
    ini = f"""# {description}
root = output/hole_{name}_
output = tCl,pCl
gauge = newtonian
h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
Omega_fld = 0.0
Lambda_EDE_ridder = {params.get('Lambda', 1.0)}
f_axion_ridder = {params.get('f', 1e27)}
theta_i_ridder = {params.get('theta', 2.8)}
beta_ridder = {params.get('beta', 0.01)}
n_ridder = {params.get('n', 3)}
A_s = 2.1e-9
n_s = 0.9665
tau_reio = 0.0561
"""
    
    print(f"\n{'='*60}")
    print(f"TEST: {name} - {description}")
    print(f"PARAMS: {params}")
    
    code, stdout, stderr = run_class(ini, name)
    
    if code == 0:
        # Extract r_s
        for line in stdout.split('\n'):
            if 'sound horizon rs' in line:
                rs = float(line.split('=')[1].split('Mpc')[0].strip())
                print(f"✅ PASS: r_s = {rs:.2f} Mpc")
                return True, rs
    else:
        # Find error
        error_lines = [l for l in stderr.split('\n') if 'error' in l.lower() or 'Error' in l]
        if error_lines:
            print(f"❌ FAIL: {error_lines[0][:80]}")
        else:
            print(f"❌ FAIL: Exit code {code}")
    
    return False, None

# Run tests
print("="*60)
print("FINDING REAL HOLES IN RIDDER FIELD IMPLEMENTATION")
print("="*60)

results = {}

# Test 1: Lambda = 0 (should give ΛCDM)
success, rs = test("lambda_zero", {"Lambda": 0.0}, "No EDE")
results["Lambda=0"] = {"pass": success, "rs": rs, "expected": 147.11}

# Test 2: Huge Lambda
success, rs = test("lambda_huge", {"Lambda": 10.0}, "Huge EDE")
results["Lambda=10"] = {"pass": success, "rs": rs, "expected": "<120"}

# Test 3: theta = 0
success, rs = test("theta_zero", {"theta": 0.0}, "No displacement")
results["theta=0"] = {"pass": success, "rs": rs, "expected": 147.11}

# Test 4: theta = pi
success, rs = test("theta_pi", {"theta": 3.14159}, "Max displacement")
results["theta=pi"] = {"pass": success, "rs": rs, "expected": "<130"}

# Test 5: beta = 0
success, rs = test("beta_zero", {"beta": 0.0}, "No DM coupling")
results["beta=0"] = {"pass": success, "rs": rs, "expected": 126.37}

# Test 6: beta huge
success, rs = test("beta_huge", {"beta": 10.0}, "Strong DM coupling")
results["beta=10"] = {"pass": success, "rs": rs, "expected": "???"}

# Test 7: n=1 (w=-1)
success, rs = test("n_one", {"n": 1}, "n=1 (cosmological constant)")
results["n=1"] = {"pass": success, "rs": rs, "expected": "???"}

# Test 8: f tiny (high frequency)
success, rs = test("f_tiny", {"f": 1e15}, "Narrow well")
results["f=1e15"] = {"pass": success, "rs": rs, "expected": "???"}

# Test 9: f huge (slow roll)
success, rs = test("f_huge", {"f": 1e35}, "Wide well")
results["f=1e35"] = {"pass": success, "rs": rs, "expected": "???"}

# Summary
print("\n" + "="*60)
print("HOLES FOUND:")
print("="*60)

holes = []
for test_name, result in results.items():
    if not result["pass"]:
        holes.append(test_name)
        print(f"🔴 {test_name}: FAILED")
    elif result["rs"] is not None:
        print(f"✅ {test_name}: r_s = {result['rs']:.2f} Mpc (expected {result['expected']})")

if holes:
    print(f"\n⚠️  {len(holes)} HOLES FOUND!")
else:
    print("\n✅ No obvious holes in parameter space")

