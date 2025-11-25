#!/usr/bin/env python3
"""
EDE PARAMETER SCAN - Track 1
============================
Scan (m_axion, Lambda_EDE) to find configurations that hit:
- f_EDE ~ 0.1
- z_peak ~ 3000

This is a coarse grid search to identify working parameter regions.
"""

import subprocess
import numpy as np
from pathlib import Path
import os

CLASS_BIN = "phase2/class/class"
OUTPUT_DIR = Path("output")
BASE_INI = "pure_ede_benchmark.ini"

def read_base_ini():
    """Read base INI file."""
    with open(BASE_INI) as f:
        return f.read()

def write_temp_ini(base_content, m_axion, Lambda_EDE, root_tag):
    """Create temporary INI with modified parameters."""
    content = base_content
    
    # Replace parameters
    lines = []
    for line in content.split('\n'):
        if line.startswith('ridder_m_axion'):
            lines.append(f'ridder_m_axion = {m_axion:.6e}')
        elif line.startswith('ridder_Lambda_EDE_eV'):
            lines.append(f'ridder_Lambda_EDE_eV = {Lambda_EDE:.6e}')
        elif line.startswith('root ='):
            lines.append(f'root = output/{root_tag}')
        else:
            lines.append(line)
    
    # Write to temp file
    temp_path = f"temp_{root_tag}.ini"
    with open(temp_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return temp_path

def run_class(ini_file, timeout=60):
    """Run CLASS, return success. Short timeout to avoid hangs."""
    try:
        result = subprocess.run(
            [CLASS_BIN, ini_file],
            capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False

def extract_f_ede(bg_file):
    """Extract f_EDE peak and z_peak."""
    try:
        bg = np.loadtxt(bg_file)
    except:
        return None, None
    
    z = bg[:, 0]
    ncols = bg.shape[1]
    
    if ncols >= 20:
        rho_ridder = bg[:, 14]
        rho_tot = bg[:, 19] if ncols < 24 else bg[:, 21]
    else:
        return None, None
    
    valid = (rho_tot > 0) & (rho_ridder >= 0)
    f_ede = np.zeros_like(z)
    f_ede[valid] = rho_ridder[valid] / rho_tot[valid]
    
    # Peak in z > 100
    mask = z > 100
    if not np.any(mask):
        return None, None
    
    f_masked = f_ede[mask]
    z_masked = z[mask]
    
    peak_idx = np.argmax(f_masked)
    return f_masked[peak_idx], z_masked[peak_idx]

def main():
    print("=" * 70)
    print("EDE PARAMETER SCAN - Track 1")
    print("=" * 70)
    print("Target: f_EDE ~ 0.1 at z_peak ~ 3000")
    print()
    
    base_content = read_base_ini()
    
    # Parameter grid
    # m_axion controls z_peak: larger m -> earlier peak (higher z)
    # Lambda_EDE controls f_EDE: larger Lambda -> larger f_EDE
    
    m_values = [1e3, 1e4, 3e4, 1e5, 3e5, 1e6]
    Lambda_values = [0.5, 1.0, 2.0, 3.0, 5.0]
    
    results = []
    
    print(f"{'m_axion':<12} {'Λ_EDE':<10} {'f_EDE':>10} {'z_peak':>12} {'Status':<10}")
    print("-" * 70)
    
    for m in m_values:
        for Lambda in Lambda_values:
            tag = f"scan_m{m:.0e}_L{Lambda}"
            tag = tag.replace('+', '').replace('.', '_')
            
            ini_file = write_temp_ini(base_content, m, Lambda, tag)
            
            try:
                success = run_class(ini_file)
                
                if success:
                    bg_file = OUTPUT_DIR / f"{tag}00_background.dat"
                    f_peak, z_peak = extract_f_ede(bg_file)
                    
                    if f_peak is not None:
                        # Check if in target range
                        f_ok = 0.05 < f_peak < 0.20
                        z_ok = 1000 < z_peak < 10000
                        
                        if f_ok and z_ok:
                            status = "✓ TARGET"
                        elif f_ok or z_ok:
                            status = "~ partial"
                        else:
                            status = "✗"
                        
                        results.append({
                            'm': m, 'Lambda': Lambda,
                            'f_EDE': f_peak, 'z_peak': z_peak,
                            'target': f_ok and z_ok
                        })
                        
                        print(f"{m:<12.1e} {Lambda:<10.1f} {f_peak:>10.4f} {z_peak:>12.0f} {status:<10}")
                    else:
                        print(f"{m:<12.1e} {Lambda:<10.1f} {'N/A':>10} {'N/A':>12} {'no peak':<10}")
                else:
                    print(f"{m:<12.1e} {Lambda:<10.1f} {'---':>10} {'---':>12} {'FAILED':<10}")
            
            except subprocess.TimeoutExpired:
                print(f"{m:<12.1e} {Lambda:<10.1f} {'---':>10} {'---':>12} {'TIMEOUT':<10}")
            
            finally:
                # Cleanup temp file
                if os.path.exists(ini_file):
                    os.remove(ini_file)
    
    print("=" * 70)
    
    # Summary
    targets = [r for r in results if r['target']]
    if targets:
        print(f"\n✅ Found {len(targets)} configuration(s) hitting target:")
        for r in targets:
            print(f"   m = {r['m']:.1e}, Λ = {r['Lambda']:.1f} eV "
                  f"-> f_EDE = {r['f_EDE']:.3f}, z_peak = {r['z_peak']:.0f}")
    else:
        print("\n⚠️ No configuration hit the target yet.")
        print("   Try expanding the parameter grid or adjusting theta_i_ridder")
    
    return 0

if __name__ == "__main__":
    exit(main())
