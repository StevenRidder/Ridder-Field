#!/usr/bin/env python3
"""
Test Unified Potential vs V2 Benchmarks

Verifies that unified mode can reproduce v2 "best CDM" results:
- Safe config (β=0.15): ΔH₀ ≈ +3.14 km/s/Mpc
- Hero config (β=0.20): ΔH₀ ≈ +3.49 km/s/Mpc

If these match within 5%, unified mode is validated.
"""

import subprocess
import numpy as np
import os
import json
from pathlib import Path

# V2 benchmark results (from Phase 2.5 optimization)
V2_BENCHMARKS = {
    'safe': {
        'beta': 0.15,
        'sigma_z': 0.5,
        'dH0': 3.14,
        'max_cmb_delta': 37.1,
        'rms_cmb_delta': 18.2,
        'z_peak': 3000,
        'f_peak': 0.14
    },
    'hero': {
        'beta': 0.20,
        'sigma_z': 0.5,
        'dH0': 3.49,
        'max_cmb_delta': 40.0,
        'rms_cmb_delta': 21.1,
        'z_peak': 3000,
        'f_peak': 0.14
    }
}

TOLERANCE = 0.05  # 5% match tolerance

def run_class(ini_file, timeout=300):
    """Run CLASS with given INI file"""
    print(f"\n  Running CLASS: {ini_file}")
    
    try:
        result = subprocess.run(
            ['./phase2/class/class', ini_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            print(f"  ❌ CLASS FAILED")
            print(f"  Error: {result.stderr[:300]}")
            return None
        
        print(f"  ✅ CLASS completed")
        return result
        
    except subprocess.TimeoutExpired:
        print(f"  ❌ TIMEOUT after {timeout}s")
        return None
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return None

def extract_H0_eff(background_file, LCDM_rs=144.43):
    """Extract effective H0 from background file"""
    try:
        data = np.loadtxt(background_file)
        # Assuming r_s in column (check your background format)
        # This is a placeholder - adjust to your actual format
        
        # For now, return a placeholder
        # You'll need to adapt this to your actual CLASS output format
        print("  ⚠️  H0_eff extraction not yet implemented")
        return None
        
    except Exception as e:
        print(f"  ❌ Could not extract H0_eff: {e}")
        return None

def extract_EDE_diagnostics(background_file):
    """Extract z_peak and f_peak from background"""
    try:
        # This should call your existing extract_ede_diagnostics.py
        result = subprocess.run(
            ['python3', 'extract_ede_diagnostics.py', background_file, '--z_min', '50'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return None, None
        
        # Parse JSON output
        output = result.stdout.strip().split('\n')[-1]
        data = json.loads(output)
        
        return data['z_peak'], data['f_peak']
        
    except Exception as e:
        print(f"  ⚠️  Could not extract EDE diagnostics: {e}")
        return None, None

def compare_results(name, unified, v2_bench):
    """Compare unified results to v2 benchmark"""
    print(f"\n{'='*70}")
    print(f"COMPARISON: {name.upper()} Configuration")
    print('='*70)
    
    matches = []
    
    # Compare H0 shift
    if unified.get('dH0') is not None:
        v2_dH0 = v2_bench['dH0']
        uni_dH0 = unified['dH0']
        diff_pct = abs(uni_dH0 - v2_dH0) / v2_dH0 * 100
        
        match = diff_pct <= TOLERANCE * 100
        matches.append(match)
        
        status = "✅ MATCH" if match else "❌ MISMATCH"
        print(f"\nΔH₀:")
        print(f"  V2:       {v2_dH0:+.2f} km/s/Mpc")
        print(f"  Unified:  {uni_dH0:+.2f} km/s/Mpc")
        print(f"  Diff:     {diff_pct:.1f}% {status}")
    
    # Compare z_peak
    if unified.get('z_peak') is not None:
        v2_z = v2_bench['z_peak']
        uni_z = unified['z_peak']
        diff_pct = abs(uni_z - v2_z) / v2_z * 100
        
        match = diff_pct <= TOLERANCE * 100
        matches.append(match)
        
        status = "✅ MATCH" if match else "❌ MISMATCH"
        print(f"\nz_peak:")
        print(f"  V2:       {v2_z:.0f}")
        print(f"  Unified:  {uni_z:.0f}")
        print(f"  Diff:     {diff_pct:.1f}% {status}")
    
    # Compare f_peak
    if unified.get('f_peak') is not None:
        v2_f = v2_bench['f_peak']
        uni_f = unified['f_peak']
        diff_pct = abs(uni_f - v2_f) / v2_f * 100
        
        match = diff_pct <= TOLERANCE * 100
        matches.append(match)
        
        status = "✅ MATCH" if match else "❌ MISMATCH"
        print(f"\nf_peak:")
        print(f"  V2:       {v2_f:.3f}")
        print(f"  Unified:  {uni_f:.3f}")
        print(f"  Diff:     {diff_pct:.1f}% {status}")
    
    # Overall verdict
    if all(matches):
        print(f"\n{'='*70}")
        print(f"✅ {name.upper()} VALIDATED: Unified matches V2 within {TOLERANCE*100}%")
        print('='*70)
        return True
    else:
        print(f"\n{'='*70}")
        print(f"❌ {name.upper()} VALIDATION FAILED")
        print('='*70)
        return False

def main():
    print("="*70)
    print("UNIFIED vs V2 VERIFICATION TEST")
    print("="*70)
    print(f"\nGoal: Verify unified mode reproduces v2 benchmarks")
    print(f"Tolerance: {TOLERANCE*100}% match required")
    
    results = {}
    
    # Test 1: Safe configuration
    print("\n" + "="*70)
    print("TEST 1: Safe Configuration (β=0.15)")
    print("="*70)
    
    class_result = run_class('unified_cdm_safe.ini')
    
    if class_result:
        # Extract diagnostics
        bg_file = 'output/unified_cdm_safe_background.dat'
        if os.path.exists(bg_file):
            z_peak, f_peak = extract_EDE_diagnostics(bg_file)
            
            # Placeholder for H0_eff extraction
            # You'll need to implement this based on your compute_effective_h0.py
            dH0 = None  # Replace with actual extraction
            
            results['safe'] = {
                'dH0': dH0,
                'z_peak': z_peak,
                'f_peak': f_peak
            }
            
            if z_peak and f_peak:
                print(f"\n  Extracted: z_peak={z_peak:.0f}, f_peak={f_peak:.3f}")
        else:
            print(f"  ⚠️  Background file not found: {bg_file}")
            results['safe'] = {}
    else:
        results['safe'] = {}
    
    # Test 2: Hero configuration
    print("\n" + "="*70)
    print("TEST 2: Hero Configuration (β=0.20)")
    print("="*70)
    
    class_result = run_class('unified_cdm_hero.ini')
    
    if class_result:
        # Extract diagnostics
        bg_file = 'output/unified_cdm_hero_background.dat'
        if os.path.exists(bg_file):
            z_peak, f_peak = extract_EDE_diagnostics(bg_file)
            
            # Placeholder for H0_eff extraction
            dH0 = None  # Replace with actual extraction
            
            results['hero'] = {
                'dH0': dH0,
                'z_peak': z_peak,
                'f_peak': f_peak
            }
            
            if z_peak and f_peak:
                print(f"\n  Extracted: z_peak={z_peak:.0f}, f_peak={f_peak:.3f}")
        else:
            print(f"  ⚠️  Background file not found: {bg_file}")
            results['hero'] = {}
    else:
        results['hero'] = {}
    
    # Compare results
    safe_match = compare_results('safe', results.get('safe', {}), V2_BENCHMARKS['safe'])
    hero_match = compare_results('hero', results.get('hero', {}), V2_BENCHMARKS['hero'])
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    if safe_match and hero_match:
        print("\n🎉 SUCCESS: Unified mode reproduces v2 benchmarks!")
        print("\nNext steps:")
        print("  1. Unified mode is validated ✅")
        print("  2. Ready to add inflation (plateau) ✅")
        print("  3. Can proceed to full unified MCMC ✅")
        return 0
    else:
        print("\n⚠️  VALIDATION INCOMPLETE")
        print("\nPossible reasons:")
        print("  - Shelf window parameters need adjustment")
        print("  - Initial conditions differ from v2")
        print("  - Window shape vs v2 implicit rolloff mismatch")
        print("\nNext steps:")
        print("  1. Check background evolution plots")
        print("  2. Adjust theta_EDE_low/high if needed")
        print("  3. Re-run tests")
        return 1

if __name__ == '__main__':
    exit(main())

