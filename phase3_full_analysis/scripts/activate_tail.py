#!/usr/bin/env python3
"""
Phase 1B: Tail Activation

Goal: Add late-time dark energy tail to unified potential and tune Lambda_tail
      to achieve w₀ ≈ -1 while maintaining dynamic w(z) at intermediate redshift.

This script:
1. Takes a working EDE+CDM configuration
2. Activates the tail component
3. Scans Lambda_tail to match observed Omega_Lambda
4. Verifies w(z) evolution
"""

import sys
from pathlib import Path
import subprocess
import json

# Configuration
REPO_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = REPO_ROOT / "phase3_full_analysis" / "configs"
RESULTS_DIR = REPO_ROOT / "phase3_full_analysis" / "results"
CLASS_BIN = REPO_ROOT / "phase2" / "class" / "class"

# Target: match ΛCDM's Omega_Lambda ~ 0.6889
OMEGA_LAMBDA_TARGET = 0.6889
TOLERANCE = 0.01  # 1% tolerance

# w₀ acceptable range (DESI/SNe constraints)
W0_MIN = -1.05
W0_MAX = -0.95

print(f"\n{'='*70}")
print("PHASE 1B: TAIL ACTIVATION")
print(f"{'='*70}\n")
print(f"Goal: Activate late-time tail, tune Lambda_tail for w₀ ≈ -1")
print(f"Target: Omega_Lambda ≈ {OMEGA_LAMBDA_TARGET:.4f}")
print(f"Constraint: {W0_MIN:.2f} < w₀ < {W0_MAX:.2f}")
print()

def create_tail_config(base_config, lambda_tail, n_tail, output_name):
    """
    Create config with tail activated.
    
    Modifies:
    - ridder_use_tail = yes
    - ridder_Lambda_tail_eV = lambda_tail
    - ridder_n_tail = n_tail
    - Forces background-only output (faster iteration)
    """
    base_path = CONFIG_DIR / base_config
    output_path = CONFIG_DIR / output_name
    
    if not base_path.exists():
        print(f"[ERROR] Base config not found: {base_path}")
        sys.exit(1)
    
    with open(base_path, "r") as f_in, open(output_path, "w") as f_out:
        for line in f_in:
            # Activate tail
            if "ridder_use_tail" in line:
                f_out.write("ridder_use_tail = yes\n")
            # Set Lambda_tail
            elif "ridder_Lambda_tail_eV" in line:
                f_out.write(f"ridder_Lambda_tail_eV = {lambda_tail:.6e}\n")
            # Set n_tail
            elif "ridder_n_tail" in line:
                f_out.write(f"ridder_n_tail = {n_tail:.1f}\n")
            # Force background only for speed
            elif line.strip().startswith("output"):
                f_out.write("output = \n")  # Empty = background only
            # Change root
            elif line.strip().startswith("root"):
                root_name = output_name.replace(".ini", "")
                f_out.write(f"root = output/{root_name}_\n")
            else:
                f_out.write(line)
    
    return output_path


def run_class_background(config_path):
    """Run CLASS for background only, return success/failure."""
    cmd = [str(CLASS_BIN), str(config_path)]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=60  # 1 min timeout for background-only
        )
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stdout
            
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"


def extract_omega_lambda(background_file):
    """Extract final Omega_Lambda from background output."""
    import numpy as np
    
    if not background_file.exists():
        return None
    
    try:
        data = np.loadtxt(background_file)
        # Column 6 (0-indexed: 5) is (Omega_Lambda)
        omega_lambda = data[-1, 5]
        return omega_lambda
    except Exception as e:
        print(f"[WARN] Could not extract Omega_Lambda: {e}")
        return None


def extract_w0(background_file):
    """Extract w(z=0) from background output."""
    import numpy as np
    
    if not background_file.exists():
        return None
    
    try:
        data = np.loadtxt(background_file)
        # w = p / rho
        # Column 21 (0-indexed: 20) is p_tot
        # Column 20 (0-indexed: 19) is rho_tot
        p_tot = data[-1, 20]
        rho_tot = data[-1, 19]
        
        if rho_tot > 0:
            w0 = p_tot / rho_tot
            return w0
        else:
            return None
            
    except Exception as e:
        print(f"[WARN] Could not extract w0: {e}")
        return None


def bisection_search(base_config, n_tail, lambda_min, lambda_max, max_iter=10):
    """
    Bisection search to find Lambda_tail that gives Omega_Lambda ≈ target.
    """
    print(f"Starting bisection search:")
    print(f"  Lambda range: [{lambda_min:.6e}, {lambda_max:.6e}] eV")
    print(f"  n_tail: {n_tail:.1f}")
    print(f"  Max iterations: {max_iter}")
    print()
    
    results = []
    
    for iteration in range(max_iter):
        lambda_mid = (lambda_min + lambda_max) / 2.0
        
        print(f"Iteration {iteration+1}/{max_iter}:")
        print(f"  Testing Lambda_tail = {lambda_mid:.6e} eV")
        
        # Create config
        config_name = f"tail_test_iter{iteration+1}.ini"
        config_path = create_tail_config(base_config, lambda_mid, n_tail, config_name)
        
        # Run CLASS
        success, output = run_class_background(config_path)
        
        if not success:
            print(f"  ❌ CLASS failed")
            # Try smaller Lambda
            lambda_max = lambda_mid
            continue
        
        # Extract observables
        root_name = config_name.replace(".ini", "")
        bg_file = REPO_ROOT / "phase2" / "class" / "output" / f"{root_name}_00_background.dat"
        
        omega_lambda = extract_omega_lambda(bg_file)
        w0 = extract_w0(bg_file)
        
        if omega_lambda is None:
            print(f"  ⚠️  Could not extract Omega_Lambda")
            lambda_max = lambda_mid
            continue
        
        error = omega_lambda - OMEGA_LAMBDA_TARGET
        print(f"  Omega_Lambda = {omega_lambda:.6f} (error: {error:+.6f})")
        
        if w0 is not None:
            print(f"  w₀ = {w0:.6f}")
        
        results.append({
            "iteration": iteration + 1,
            "lambda_tail": lambda_mid,
            "omega_lambda": omega_lambda,
            "w0": w0,
            "error": error,
        })
        
        # Check convergence
        if abs(error) < TOLERANCE:
            print(f"  ✅ CONVERGED!")
            return lambda_mid, omega_lambda, w0, results
        
        # Adjust search range
        if omega_lambda < OMEGA_LAMBDA_TARGET:
            # Need more dark energy → increase Lambda
            lambda_min = lambda_mid
            print(f"  → Increasing Lambda (new range: [{lambda_min:.6e}, {lambda_max:.6e}])")
        else:
            # Too much dark energy → decrease Lambda
            lambda_max = lambda_mid
            print(f"  → Decreasing Lambda (new range: [{lambda_min:.6e}, {lambda_max:.6e}])")
        
        print()
    
    # Max iterations reached
    print(f"⚠️  Max iterations reached without convergence")
    print(f"   Best result: Lambda = {lambda_mid:.6e}, Omega_Lambda = {omega_lambda:.6f}")
    
    return lambda_mid, omega_lambda, w0, results


def main():
    """Main execution."""
    
    # Use the working configuration from Hour 1
    # Lambda=1.0, beta=0.05 (we know this works for perturbations)
    base_config = "unified_baby_lambda1p0.ini"
    
    print(f"Base configuration: {base_config}")
    print(f"  (Lambda_EDE = 1.0 eV, beta = 0.05, tail currently OFF)")
    print()
    
    # Initial guess for Lambda_tail
    # From theory: Lambda_tail ~ 2.3e-3 eV for Omega_Lambda ~ 0.7
    # But we'll search a range to be safe
    lambda_min = 1.0e-3  # 1 meV
    lambda_max = 5.0e-3  # 5 meV
    n_tail = 3.0  # Standard power
    
    # Run bisection search
    lambda_optimal, omega_lambda, w0, history = bisection_search(
        base_config=base_config,
        n_tail=n_tail,
        lambda_min=lambda_min,
        lambda_max=lambda_max,
        max_iter=12
    )
    
    print(f"\n{'='*70}")
    print("TAIL ACTIVATION COMPLETE")
    print(f"{'='*70}\n")
    
    print(f"Optimal Lambda_tail: {lambda_optimal:.6e} eV")
    print(f"Omega_Lambda:        {omega_lambda:.6f} (target: {OMEGA_LAMBDA_TARGET:.6f})")
    
    if w0 is not None:
        print(f"w₀:                  {w0:.6f}")
        
        if W0_MIN <= w0 <= W0_MAX:
            print(f"  ✅ w₀ within acceptable range [{W0_MIN:.2f}, {W0_MAX:.2f}]")
        else:
            print(f"  ⚠️  w₀ outside acceptable range [{W0_MIN:.2f}, {W0_MAX:.2f}]")
    
    print()
    
    # Save results
    results_file = RESULTS_DIR / "tail_activation_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "optimal_lambda_tail": lambda_optimal,
            "omega_lambda": omega_lambda,
            "w0": w0,
            "n_tail": n_tail,
            "target_omega_lambda": OMEGA_LAMBDA_TARGET,
            "convergence_history": history,
        }, f, indent=2)
    
    print(f"✓ Results saved to {results_file}")
    print()
    
    # Create final config with tail activated
    final_config = "unified_with_tail.ini"
    final_path = create_tail_config(base_config, lambda_optimal, n_tail, final_config)
    
    # But re-enable perturbations for this final config
    with open(final_path, "r") as f:
        lines = f.readlines()
    
    with open(final_path, "w") as f:
        for line in lines:
            if line.strip().startswith("output"):
                f.write("output = tCl,pCl,lCl,mPk\n")
            else:
                f.write(line)
    
    print(f"✓ Final configuration saved: {final_config}")
    print(f"  Ready for full CLASS run with tail activated")
    print()
    
    print("Next steps:")
    print("  1. Run full CLASS on unified_with_tail.ini")
    print("  2. Extract full observables (H₀, S₈, CMB, w(z))")
    print("  3. Verify dynamic w(z) at intermediate redshift")
    print("  4. Proceed to Phase 1C: H₀ extraction")
    print()


if __name__ == "__main__":
    main()

