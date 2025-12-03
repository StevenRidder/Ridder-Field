#!/usr/bin/env python3
"""
Parse existing theta scan logs to extract results
"""

import re
import glob
import os

OUTPUT_DIR = 'output/theta_scan'

print("="*70)
print("PARSING THETA SCAN RESULTS")
print("="*70)

results = []

log_files = sorted(glob.glob(f'{OUTPUT_DIR}/theta_*.log'))

for logfile in log_files:
    # Extract theta from filename
    match = re.search(r'theta_(\d+\.\d+)\.log', logfile)
    if not match:
        continue
    
    theta = float(match.group(1))
    
    # Parse log file
    with open(logfile) as f:
        content = f.read()
    
    # Find all RIDDER_SHOOT lines
    shoot_lines = [line for line in content.split('\n') if 'RIDDER_SHOOT iter=' in line]
    
    if shoot_lines:
        # Parse last iteration (closest to convergence)
        last_line = shoot_lines[-1]
        match = re.search(r'log10_Lambda=(\S+)\s+f_peak=(\S+)\s+z_peak=\s*(\S+)', last_line)
        
        if match:
            log10_Lambda = float(match.group(1))
            Lambda = 10**log10_Lambda
            f_peak = float(match.group(2))
            z_peak = float(match.group(3))
            
            # Check convergence
            converged = abs(f_peak - 0.10) < 0.002
            
            results.append({
                'theta': theta,
                'Lambda': Lambda,
                'log10_Lambda': log10_Lambda,
                'f_peak': f_peak,
                'z_peak': z_peak,
                'status': 'converged' if converged else 'partial',
                'n_iter': len(shoot_lines)
            })
            
            print(f"theta={theta:.1f}: Lambda={Lambda:.3e} eV, f_peak={f_peak:.5f}, z_peak={z_peak:.0f} ({len(shoot_lines)} iter)")
        else:
            print(f"theta={theta:.1f}: Could not parse")
            results.append({'theta': theta, 'status': 'failed'})
    else:
        print(f"theta={theta:.1f}: No RIDDER_SHOOT lines found")
        results.append({'theta': theta, 'status': 'failed'})

print("\n" + "="*70)
print("SUMMARY TABLE")
print("="*70)
print(f"{'theta_i':>8} | {'Lambda (eV)':>12} | {'log10(Λ)':>9} | {'f_peak':>7} | {'z_peak':>7} | {'Status':>10}")
print("-"*70)

for r in results:
    if r['status'] in ['converged', 'partial']:
        status_mark = '✓' if r['status'] == 'converged' else '~'
        print(f"{r['theta']:8.1f} | {r['Lambda']:12.3e} | {r['log10_Lambda']:9.3f} | {r['f_peak']:7.5f} | {r['z_peak']:7.0f} | {status_mark:>9}{r['status']}")
    else:
        print(f"{r['theta']:8.1f} | {'---':>12} | {'---':>9} | {'---':>7} | {'---':>7} | {r['status']:>10}")

print("-"*70)

# Save to CSV
csv_file = f'{OUTPUT_DIR}/theta_scan_results.csv'
with open(csv_file, 'w') as f:
    f.write("theta_i,Lambda_eV,log10_Lambda,f_peak,z_peak,status\n")
    for r in results:
        if r['status'] in ['converged', 'partial']:
            f.write(f"{r['theta']},{r['Lambda']:.6e},{r['log10_Lambda']:.3f},{r['f_peak']:.6f},{r['z_peak']:.1f},{r['status']}\n")
        else:
            f.write(f"{r['theta']},,,,,{r['status']}\n")

print(f"\nResults saved to: {csv_file}")

# Analysis
good_results = [r for r in results if r['status'] in ['converged', 'partial']]

if len(good_results) >= 2:
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    
    # Check monotonicity
    z_peaks = [r['z_peak'] for r in good_results]
    Lambdas = [r['Lambda'] for r in good_results]
    thetas = [r['theta'] for r in good_results]
    
    z_increasing = all(z_peaks[i] <= z_peaks[i+1] for i in range(len(z_peaks)-1))
    Lambda_decreasing = all(Lambdas[i] >= Lambdas[i+1] for i in range(len(Lambdas)-1))
    
    print(f"\nMonotonicity checks:")
    print(f"  z_peak increases with theta_i: {'✓ YES' if z_increasing else '✗ NO'}")
    print(f"  Lambda decreases with theta_i: {'✓ YES' if Lambda_decreasing else '✗ NO'}")
    
    # Z-peak range
    z_min_scan = min(z_peaks)
    z_max_scan = max(z_peaks)
    print(f"\nPeak redshift range:")
    print(f"  z_peak ∈ [{z_min_scan:.0f}, {z_max_scan:.0f}]")
    
    if z_max_scan < 1000:
        print(f"  ⚠ All peaks are < 1000 (too late for EDE!)")
        print(f"  → Recommendation: Increase theta_i to 2.5-3.0")
    elif z_min_scan > 8000:
        print(f"  ⚠ All peaks are > 8000 (too early!)")
        print(f"  → Recommendation: Decrease theta_i to 0.5-1.0")
    else:
        # Find closest to target
        target_z = 3000
        best = min(good_results, key=lambda r: abs(r['z_peak'] - target_z))
        print(f"\n  ✓ Good range! Closest to z ~ {target_z}:")
        print(f"    theta_i = {best['theta']:.1f}")
        print(f"    z_peak = {best['z_peak']:.0f}")
        print(f"    Lambda = {best['Lambda']:.3e} eV")
        print(f"    f_peak = {best['f_peak']:.5f}")

print("\n" + "="*70 + "\n")

