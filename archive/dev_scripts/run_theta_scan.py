#!/usr/bin/env python3
"""
Execute theta scan: map theta_i → (Lambda, f_peak, z_peak) for f_EDE = 10%
"""

import subprocess
import re
import time
import os

# Scan parameters
THETA_VALUES = [1.0, 1.2, 1.5, 1.8, 2.0, 2.2, 2.5]
BASE_INI = 'theta_scan_base.ini'
OUTPUT_DIR = 'output/theta_scan'

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read base ini
with open(BASE_INI) as f:
    base_ini = f.read()

print("="*70)
print("THETA SCAN: Mapping theta_i → (Lambda, f_peak, z_peak)")
print("="*70)
print(f"\nTarget: f_EDE = 10%")
print(f"Scanning theta_i = {THETA_VALUES}")
print(f"Output directory: {OUTPUT_DIR}/")
print("\n" + "-"*70)

results = []

for i, theta in enumerate(THETA_VALUES, 1):
    print(f"\n[{i}/{len(THETA_VALUES)}] Running theta_i = {theta:.1f}...")
    
    # Create ini for this theta
    ini_content = base_ini + f"\ntheta_i_ridder = {theta}\n"
    
    # Write to VM and run CLASS
    cmd = f"""ssh <VM_USER>@172.174.34.125 'cat > /tmp/theta_scan_{theta}.ini << "EOFINI"
{ini_content}
EOFINI
cd ~/Ridder-Field/phase2/class && timeout 90 ./class /tmp/theta_scan_{theta}.ini 2>&1'"""
    
    start = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    elapsed = time.time() - start
    
    output = result.stdout + result.stderr
    
    # Parse shooting trace - get LAST iteration (closest to convergence)
    Lambda = None
    f_peak = None
    z_peak = None
    log10_Lambda = None
    converged = False
    
    shoot_lines = []
    for line in output.split('\n'):
        if 'RIDDER_SHOOT iter=' in line:
            shoot_lines.append(line)
    
    # If we have shooting iterations, parse the last one
    if shoot_lines:
        last_line = shoot_lines[-1]
        match = re.search(r'log10_Lambda=(\S+)\s+f_peak=(\S+)\s+z_peak=(\S+)', last_line)
        if match:
            log10_Lambda = float(match.group(1))
            Lambda = 10**log10_Lambda
            f_peak = float(match.group(2))
            z_peak = float(match.group(3))
            
            # Check if converged (within tolerance)
            if abs(f_peak - 0.10) < 0.002:  # 0.2% tolerance
                converged = True
    
    # Save full output log
    log_file = f'{OUTPUT_DIR}/theta_{theta:.1f}.log'
    with open(log_file, 'w') as f:
        f.write(output)
    
    if converged and Lambda is not None:
        results.append({
            'theta': theta,
            'Lambda': Lambda,
            'log10_Lambda': log10_Lambda,
            'f_peak': f_peak,
            'z_peak': z_peak,
            'elapsed': elapsed,
            'status': 'converged'
        })
        print(f"  ✓ Converged in {elapsed:.1f}s")
        print(f"    Lambda = {Lambda:.3e} eV")
        print(f"    f_peak = {f_peak:.5f}")
        print(f"    z_peak = {z_peak:.0f}")
    else:
        results.append({
            'theta': theta,
            'Lambda': None,
            'log10_Lambda': None,
            'f_peak': None,
            'z_peak': None,
            'elapsed': elapsed,
            'status': 'failed'
        })
        print(f"  ✗ Failed to converge")
        print(f"    Check {log_file} for details")

print("\n" + "="*70)
print("SCAN COMPLETE")
print("="*70)

# Print summary table
print("\nResults Summary:")
print("-"*70)
print(f"{'theta_i':>8} | {'Lambda (eV)':>12} | {'f_peak':>7} | {'z_peak':>7} | {'Status':>10}")
print("-"*70)

for r in results:
    if r['status'] == 'converged':
        print(f"{r['theta']:8.1f} | {r['Lambda']:12.3e} | {r['f_peak']:7.5f} | {r['z_peak']:7.0f} | {r['status']:>10}")
    else:
        print(f"{r['theta']:8.1f} | {'---':>12} | {'---':>7} | {'---':>7} | {r['status']:>10}")

print("-"*70)

# Save results to CSV
csv_file = f'{OUTPUT_DIR}/theta_scan_results.csv'
with open(csv_file, 'w') as f:
    f.write("theta_i,Lambda_eV,log10_Lambda,f_peak,z_peak,elapsed_s,status\n")
    for r in results:
        if r['status'] == 'converged':
            f.write(f"{r['theta']},{r['Lambda']:.6e},{r['log10_Lambda']:.3f},{r['f_peak']:.6f},{r['z_peak']:.1f},{r['elapsed']:.1f},{r['status']}\n")
        else:
            f.write(f"{r['theta']},,,,,{r['elapsed']:.1f},{r['status']}\n")

print(f"\nResults saved to: {csv_file}")

# Analysis
converged_results = [r for r in results if r['status'] == 'converged']

if len(converged_results) >= 2:
    print("\nQuick Analysis:")
    print("-"*70)
    
    # Check if z_peak increases with theta
    z_peaks = [r['z_peak'] for r in converged_results]
    if all(z_peaks[i] <= z_peaks[i+1] for i in range(len(z_peaks)-1)):
        print("✓ z_peak increases monotonically with theta_i (expected!)")
    else:
        print("⚠ z_peak does NOT increase monotonically (unexpected)")
    
    # Check if Lambda decreases with theta
    Lambdas = [r['Lambda'] for r in converged_results]
    if all(Lambdas[i] >= Lambdas[i+1] for i in range(len(Lambdas)-1)):
        print("✓ Lambda decreases with theta_i (expected!)")
    else:
        print("⚠ Lambda does NOT decrease with theta_i (check physics)")
    
    # Find theta closest to z_peak ~ 3000
    target_z = 3000
    best = min(converged_results, key=lambda r: abs(r['z_peak'] - target_z))
    print(f"\nClosest to z_peak ~ {target_z}:")
    print(f"  theta_i = {best['theta']:.1f}")
    print(f"  z_peak = {best['z_peak']:.0f}")
    print(f"  Lambda = {best['Lambda']:.3e} eV")
    
    if best['z_peak'] < 1000:
        print("\n⚠ All z_peak values are < 1000 (too late!)")
        print("  Recommendation: Scan higher theta_i values (2.5-3.0)")
        print("  Or: Adjust f_axion or c_slow to shift onset earlier")
    elif best['z_peak'] > 8000:
        print("\n⚠ All z_peak values are > 8000 (too early!)")
        print("  Recommendation: Scan lower theta_i values (0.5-1.0)")

print("\n" + "="*70)
print("Next: Run 'python3 plot_theta_scan.py' to visualize results")
print("="*70 + "\n")

