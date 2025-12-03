#!/usr/bin/env python3
"""
test_v3_stack.py - Comprehensive V3 Stack Validation

Tests:
1. V3 potential functions are called (not v2)
2. Button API works with all modes
3. Shooting mechanism converges
4. JSON schema is valid
5. Observables are physically reasonable
"""

import os
import sys
import json
import subprocess
from pathlib import Path

VM_HOST = "<VM_USER>@172.174.34.125"
VM_RIDDER_PATH = "~/Ridder-Field"

def run_remote(cmd):
    """Run command on VM"""
    full_cmd = f'ssh {VM_HOST} "{cmd}"'
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=120)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -1, "", str(e)

def print_test(name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {name}")
    if details:
        print(f"       {details}")

def test_v3_potential_active():
    """Test 1: Verify v3 potential functions are being called"""
    print("\n" + "="*70)
    print("TEST 1: V3 Potential Active")
    print("="*70)
    
    # Create minimal v3 INI
    cmd = f"""cd {VM_RIDDER_PATH} && cat > test_v3_minimal.ini << 'EOF'
output = 
write background = yes
h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649

use_ridder = yes
ridder_model_type = v3_canon
ridder_f_eV = 1.0e26
ridder_use_EDE = yes
ridder_Lambda_EDE_eV = 1e-2
ridder_theta_E_center = 2.4
ridder_sigma_E = 0.4
ridder_n_EDE = 2.0
ridder_use_tail = yes
ridder_Lambda_tail_eV = 16e-3
ridder_alpha_tail = 1.0
ridder_theta_T_center = 0.0
ridder_n_tail = 1.0
ridder_use_floor = no
ridder_Lambda_floor_eV = 0.0
theta_i_ridder = 2.4
ridder_c_slow = 0.0

root = phase2/class/output/test_v3_minimal
EOF
phase2/class/class test_v3_minimal.ini 2>&1 | grep -E 'ridder_V_v3|V_EDE_v3|V_tail_v3|model_type.*v3'
"""
    
    rc, stdout, stderr = run_remote(cmd)
    
    # Check for v3 function calls
    has_v3_calls = "ridder_V_v3" in stdout or "V_EDE_v3" in stdout or "v3_canon" in stdout
    has_v2_calls = "V_shelf_theta" in stdout or "simple_ede" in stdout
    
    print_test("V3 functions called", has_v3_calls, stdout[:200] if has_v3_calls else "No v3 debug output")
    print_test("No v2 fallback", not has_v2_calls, "Clean v3 path")
    
    return has_v3_calls and not has_v2_calls

def test_button_lcdm_baseline():
    """Test 2: Button API - LCDM baseline"""
    print("\n" + "="*70)
    print("TEST 2: Button API - LCDM Baseline")
    print("="*70)
    
    cmd = f"""cd {VM_RIDDER_PATH} && python3 run_unified_model_v3.py --preset lcdm_baseline --mode quick --skip_shooting 2>&1"""
    
    rc, stdout, stderr = run_remote(cmd)
    
    # Check for success
    success = rc == 0 and "CLASS completed" in stdout
    
    # Try to parse JSON
    json_valid = False
    observables = {}
    try:
        # Extract JSON from output
        lines = stdout.split('\n')
        json_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start is not None:
            json_str = '\n'.join(lines[json_start:])
            result = json.loads(json_str)
            json_valid = True
            observables = result.get('observables', {})
    except:
        pass
    
    print_test("Button runs successfully", success)
    print_test("JSON output valid", json_valid)
    
    if observables:
        H0 = observables.get('H0_km_s_Mpc', 0)
        f_EDE = observables.get('f_EDE_peak', 0)
        print_test("H0 ~ 67 km/s/Mpc (LCDM)", 66 < H0 < 68, f"H0 = {H0:.2f}")
        print_test("f_EDE ~ 0 (no EDE)", f_EDE < 0.01, f"f_EDE = {f_EDE:.4f}")
    
    return success and json_valid

def test_button_unified_compromise():
    """Test 3: Button API - Unified compromise (with shooting)"""
    print("\n" + "="*70)
    print("TEST 3: Button API - Unified Compromise (with shooting)")
    print("="*70)
    
    cmd = f"""cd {VM_RIDDER_PATH} && timeout 180 python3 run_unified_model_v3.py --preset unified_compromise --mode quick 2>&1"""
    
    rc, stdout, stderr = run_remote(cmd)
    
    # Check for shooting output
    has_shooting = "Shooting for f_EDE" in stdout or "Converged" in stdout
    success = rc == 0 and "CLASS completed" in stdout
    
    # Parse JSON
    json_valid = False
    observables = {}
    v3_params = {}
    try:
        lines = stdout.split('\n')
        json_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start is not None:
            json_str = '\n'.join(lines[json_start:])
            result = json.loads(json_str)
            json_valid = True
            observables = result.get('observables', {})
            v3_params = result.get('v3_params', {})
    except:
        pass
    
    print_test("Button runs successfully", success)
    print_test("Shooting mechanism active", has_shooting, "Lambda_EDE calibrated")
    print_test("JSON output valid", json_valid)
    
    if observables:
        H0 = observables.get('H0_km_s_Mpc', 0)
        f_EDE = observables.get('f_EDE_peak', 0)
        z_peak = observables.get('z_peak', 0)
        
        print_test("H0 > LCDM", H0 > 67.5, f"H0 = {H0:.2f} km/s/Mpc")
        print_test("f_EDE in reasonable range", 0.05 < f_EDE < 0.25, f"f_EDE = {f_EDE:.3f}")
        print_test("z_peak ~ recombination", 1000 < z_peak < 10000, f"z_peak = {z_peak:.0f}")
    
    if v3_params:
        Lambda_EDE = v3_params.get('Lambda_EDE_eV', 0)
        Lambda_tail = v3_params.get('Lambda_tail_eV', 0)
        print_test("Lambda_EDE calibrated", Lambda_EDE > 0, f"Lambda_EDE = {Lambda_EDE:.3e} eV")
        print_test("Lambda_tail = 16 meV", abs(Lambda_tail - 0.016) < 0.001, f"Lambda_tail = {Lambda_tail:.3e} eV")
    
    return success and has_shooting and json_valid

def test_button_custom_params():
    """Test 4: Button API - Custom parameters"""
    print("\n" + "="*70)
    print("TEST 4: Button API - Custom Parameters")
    print("="*70)
    
    cmd = f"""cd {VM_RIDDER_PATH} && timeout 180 python3 run_unified_model_v3.py --Lambda_tail_meV 20.0 --f_axion 0.45 --mode quick 2>&1"""
    
    rc, stdout, stderr = run_remote(cmd)
    
    success = rc == 0 and "CLASS completed" in stdout
    
    # Parse JSON
    json_valid = False
    input_params = {}
    try:
        lines = stdout.split('\n')
        json_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start is not None:
            json_str = '\n'.join(lines[json_start:])
            result = json.loads(json_str)
            json_valid = True
            input_params = result.get('input', {})
    except:
        pass
    
    print_test("Custom params run", success)
    print_test("JSON output valid", json_valid)
    
    if input_params:
        Lambda_tail_input = input_params.get('Lambda_tail_meV', 0)
        f_axion_input = input_params.get('f_axion', 0)
        
        print_test("Lambda_tail matches input", Lambda_tail_input == 20.0, f"Input: {Lambda_tail_input} meV")
        print_test("f_axion matches input", f_axion_input == 0.45, f"Input: {f_axion_input}")
    
    return success and json_valid

def test_json_schema_compliance():
    """Test 5: JSON schema compliance"""
    print("\n" + "="*70)
    print("TEST 5: JSON Schema Compliance")
    print("="*70)
    
    cmd = f"""cd {VM_RIDDER_PATH} && python3 run_unified_model_v3.py --preset unified_compromise --mode quick --skip_shooting 2>&1"""
    
    rc, stdout, stderr = run_remote(cmd)
    
    # Parse JSON
    try:
        lines = stdout.split('\n')
        json_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start is None:
            print_test("JSON found in output", False, "No JSON in stdout")
            return False
        
        json_str = '\n'.join(lines[json_start:])
        result = json.loads(json_str)
        
        # Check required top-level keys
        has_input = 'input' in result
        has_v3_params = 'v3_params' in result
        has_observables = 'observables' in result
        
        print_test("Has 'input' section", has_input)
        print_test("Has 'v3_params' section", has_v3_params)
        print_test("Has 'observables' section", has_observables)
        
        # Check input section
        if has_input:
            input_sec = result['input']
            has_potential_version = 'potential_version' in input_sec
            is_v3 = input_sec.get('potential_version') == 'v3'
            
            print_test("Has potential_version field", has_potential_version)
            print_test("potential_version = 'v3'", is_v3, f"Version: {input_sec.get('potential_version')}")
        
        # Check v3_params section
        if has_v3_params:
            v3_sec = result['v3_params']
            required_v3_fields = ['f_eV', 'Lambda_EDE_eV', 'Lambda_tail_eV', 'theta_E_center', 'sigma_E', 'n_EDE']
            
            for field in required_v3_fields:
                has_field = field in v3_sec
                print_test(f"v3_params.{field} present", has_field, f"Value: {v3_sec.get(field)}" if has_field else "Missing")
        
        # Check observables section
        if has_observables:
            obs_sec = result['observables']
            required_obs_fields = ['H0_km_s_Mpc', 'f_EDE_peak', 'z_peak']
            
            for field in required_obs_fields:
                has_field = field in obs_sec
                print_test(f"observables.{field} present", has_field, f"Value: {obs_sec.get(field)}" if has_field else "Missing")
        
        return has_input and has_v3_params and has_observables
        
    except json.JSONDecodeError as e:
        print_test("JSON parses correctly", False, f"JSON error: {e}")
        return False
    except Exception as e:
        print_test("JSON extraction", False, f"Error: {e}")
        return False

def test_physics_sanity():
    """Test 6: Physics sanity checks"""
    print("\n" + "="*70)
    print("TEST 6: Physics Sanity Checks")
    print("="*70)
    
    cmd = f"""cd {VM_RIDDER_PATH} && python3 run_unified_model_v3.py --Lambda_tail_meV 16.0 --f_axion 0.40 --mode quick --skip_shooting 2>&1"""
    
    rc, stdout, stderr = run_remote(cmd)
    
    try:
        lines = stdout.split('\n')
        json_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        json_str = '\n'.join(lines[json_start:])
        result = json.loads(json_str)
        
        obs = result.get('observables', {})
        
        H0 = obs.get('H0_km_s_Mpc', 0)
        f_EDE = obs.get('f_EDE_peak', 0)
        z_peak = obs.get('z_peak', 0)
        
        # Sanity checks
        H0_reasonable = 60 < H0 < 80
        f_EDE_reasonable = 0 <= f_EDE < 1.0
        z_peak_reasonable = z_peak == 0 or (100 < z_peak < 1e6)
        
        print_test("H0 physically reasonable", H0_reasonable, f"H0 = {H0:.2f} km/s/Mpc (expect 60-80)")
        print_test("f_EDE physically reasonable", f_EDE_reasonable, f"f_EDE = {f_EDE:.4f} (expect 0-1)")
        print_test("z_peak physically reasonable", z_peak_reasonable, f"z_peak = {z_peak:.0f} (expect 100-1e6 or 0)")
        
        return H0_reasonable and f_EDE_reasonable and z_peak_reasonable
        
    except Exception as e:
        print_test("Physics extraction", False, f"Error: {e}")
        return False

def main():
    print("="*70)
    print("V3 STACK VALIDATION TEST SUITE")
    print("="*70)
    print(f"VM: {VM_HOST}")
    print(f"Path: {VM_RIDDER_PATH}")
    print()
    
    results = []
    
    # Run all tests
    results.append(("V3 Potential Active", test_v3_potential_active()))
    results.append(("LCDM Baseline", test_button_lcdm_baseline()))
    results.append(("Unified Compromise", test_button_unified_compromise()))
    results.append(("Custom Parameters", test_button_custom_params()))
    results.append(("JSON Schema", test_json_schema_compliance()))
    results.append(("Physics Sanity", test_physics_sanity()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {name}")
    
    print()
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - V3 STACK IS OPERATIONAL")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED - REVIEW NEEDED")
        return 1

if __name__ == "__main__":
    sys.exit(main())

