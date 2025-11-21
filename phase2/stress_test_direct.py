#!/usr/bin/env python3
"""
Scientific Stress Test for Ridder Field Model (Direct CLASS Execution)
======================================================================

Tests fundamental observational pillars BEFORE launching MCMC:
1. BBN Consistency (Y_He)
2. Background Evolution (r_s, H_0)
3. CMB Damping Tail (high-ℓ)
4. β-Coupling Linearity (structure suppression)

This version runs CLASS directly via .ini files and parses output.
"""

import subprocess
import os
import re
import numpy as np

CLASS_PATH = "/Users/steveridder/Git/Ridder Field/phase2/class"
OUTPUT_DIR = os.path.join(CLASS_PATH, "output")

def run_class(ini_file):
    """Run CLASS with given ini file and return output."""
    result = subprocess.run(
        [os.path.join(CLASS_PATH, "class"), ini_file],
        cwd=CLASS_PATH,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"CLASS failed: {result.stderr}")
    return result.stdout

def parse_background_output(output):
    """Parse background quantities from CLASS output."""
    data = {}
    
    # Extract Y_He
    match = re.search(r'primordial helium mass fraction Y_He\s*=\s*([\d.]+)', output)
    if match:
        data['YHe'] = float(match.group(1))
    
    # Extract r_s (baryon drag)
    match = re.search(r'with comoving sound horizon rs\s*=\s*([\d.]+)\s*Mpc', output)
    if match:
        data['rs'] = float(match.group(1))
    
    return data

def create_ini(filename, params):
    """Create a CLASS .ini file with given parameters."""
    ini_path = os.path.join(CLASS_PATH, filename)
    with open(ini_path, 'w') as f:
        for key, value in params.items():
            f.write(f"{key} = {value}\n")
    return ini_path

def run_audit():
    """Execute all four stress tests."""
    print("=" * 70)
    print("SCIENTIFIC STRESS TEST - RIDDER FIELD MODEL (Direct Execution)")
    print("=" * 70)
    print()
    
    results = {
        'bbn': None,
        'background': None,
        'damping': None,
        'coupling': None
    }
    
    # Base parameters
    base_params = {
        'h': 0.6736,
        'omega_b': 0.02237,
        'omega_cdm': 0.1200,
        'A_s': 2.1e-9,
        'n_s': 0.9649,
        'tau_reio': 0.0544,
        'gauge': 'newtonian',
        'background_verbose': 1,
        'thermodynamics_verbose': 1
    }
    
    # -------------------------------------------------------------------------
    # TEST 1 & 2: BBN + BACKGROUND
    # -------------------------------------------------------------------------
    print("[TEST 1 & 2] BBN Consistency + Background Evolution")
    print("-" * 70)
    
    try:
        # Run ΛCDM
        print("  Computing ΛCDM baseline...")
        lcdm_params = base_params.copy()
        lcdm_params['output'] = 'tCl'
        lcdm_params['l_max_scalars'] = 3000
        create_ini('stress_lcdm.ini', lcdm_params)
        lcdm_output = run_class('stress_lcdm.ini')
        lcdm_data = parse_background_output(lcdm_output)
        
        # Run Ridder
        print("  Computing Ridder model...")
        ridder_params = base_params.copy()
        ridder_params.update({
            'has_ridder': 'yes',
            'Lambda_EDE_ridder': 1.0,
            'f_axion_ridder': 1.0e27,
            'theta_i_ridder': 2.5,
            'beta_ridder': 0.01,
            'n_ridder': 3,
            'output': 'tCl',
            'l_max_scalars': 3000
        })
        create_ini('stress_ridder.ini', ridder_params)
        ridder_output = run_class('stress_ridder.ini')
        ridder_data = parse_background_output(ridder_output)
        
        # TEST 1: BBN
        print()
        print("  [TEST 1] Big Bang Nucleosynthesis")
        yhe_lcdm = lcdm_data.get('YHe', 0)
        yhe_ridder = ridder_data.get('YHe', 0)
        if yhe_lcdm > 0 and yhe_ridder > 0:
            diff_yhe = abs(yhe_ridder - yhe_lcdm) / yhe_lcdm * 100
            print(f"    ΛCDM:   Y_He = {yhe_lcdm:.6f}")
            print(f"    Ridder: Y_He = {yhe_ridder:.6f}")
            print(f"    Deviation: {diff_yhe:.3f}%")
            
            if diff_yhe < 0.5:
                print("    ✅ STATUS: PASS")
                results['bbn'] = 'PASS'
            elif diff_yhe < 1.0:
                print("    ⚠️  STATUS: WARNING")
                results['bbn'] = 'WARNING'
            else:
                print("    ❌ STATUS: FAIL")
                results['bbn'] = 'FAIL'
        else:
            print("    ⚠️  Could not extract Y_He")
            results['bbn'] = 'UNKNOWN'
        
        # TEST 2: Background
        print()
        print("  [TEST 2] Expansion History")
        rs_lcdm = lcdm_data.get('rs', 0)
        rs_ridder = ridder_data.get('rs', 0)
        h0_lcdm = base_params['h'] * 100.0  # Use input value
        h0_ridder = base_params['h'] * 100.0  # Same input for both
        
        if rs_lcdm > 0 and rs_ridder > 0:
            rs_reduction = (1 - rs_ridder / rs_lcdm) * 100
            # H_0 scales inversely with r_s for fixed angular scale
            h0_ridder_inferred = h0_lcdm * (rs_lcdm / rs_ridder)
            
            print(f"    ΛCDM:   r_s = {rs_lcdm:.2f} Mpc")
            print(f"    Ridder: r_s = {rs_ridder:.2f} Mpc")
            print(f"    r_s reduction: {rs_reduction:.2f}%")
            print(f"    Inferred H_0 (if fixing θ_s): {h0_ridder_inferred:.2f} km/s/Mpc")
            print()
            
            if 136.0 < rs_ridder < 138.0:
                print(f"    ✅ STATUS: PASS (r_s in target range for H_0~73)")
                results['background'] = 'PASS'
            elif 134.0 < rs_ridder < 140.0:
                print(f"    ⚠️  STATUS: WARNING (r_s marginal)")
                results['background'] = 'WARNING'
            else:
                print(f"    ❌ STATUS: FAIL (r_s does not resolve tension)")
                results['background'] = 'FAIL'
        else:
            print("    ⚠️  Could not extract r_s")
            results['background'] = 'UNKNOWN'
        
        print()
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results['bbn'] = 'ERROR'
        results['background'] = 'ERROR'
    
    # -------------------------------------------------------------------------
    # TEST 3: CMB DAMPING TAIL
    # -------------------------------------------------------------------------
    print("[TEST 3] CMB Damping Tail")
    print("-" * 70)
    
    try:
        # Read CMB spectra from output files (find latest run)
        import glob
        lcdm_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "stress_lcdm*_cl.dat")))
        ridder_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "stress_ridder*_cl.dat")))
        
        lcdm_cl_file = lcdm_files[-1] if lcdm_files else None
        ridder_cl_file = ridder_files[-1] if ridder_files else None
        
        if lcdm_cl_file and ridder_cl_file and os.path.exists(lcdm_cl_file) and os.path.exists(ridder_cl_file):
            lcdm_cl = np.loadtxt(lcdm_cl_file)
            ridder_cl = np.loadtxt(ridder_cl_file)
            
            # Extract TT column (column 1)
            ell_lcdm = lcdm_cl[:, 0].astype(int)
            tt_lcdm = lcdm_cl[:, 1]
            ell_ridder = ridder_cl[:, 0].astype(int)
            tt_ridder = ridder_cl[:, 1]
            
            # Find ratios at key ℓ values
            def get_ratio(ell_target):
                idx_lcdm = np.where(ell_lcdm == ell_target)[0]
                idx_ridder = np.where(ell_ridder == ell_target)[0]
                if len(idx_lcdm) > 0 and len(idx_ridder) > 0:
                    return tt_ridder[idx_ridder[0]] / tt_lcdm[idx_lcdm[0]]
                return None
            
            ratio_1000 = get_ratio(1000)
            ratio_2000 = get_ratio(2000)
            ratio_3000 = get_ratio(3000)
            
            print(f"  Ratio @ ℓ=1000: {ratio_1000:.4f}" if ratio_1000 else "  ℓ=1000: N/A")
            print(f"  Ratio @ ℓ=2000: {ratio_2000:.4f}" if ratio_2000 else "  ℓ=2000: N/A")
            print(f"  Ratio @ ℓ=3000: {ratio_3000:.4f}" if ratio_3000 else "  ℓ=3000: N/A")
            print()
            
            if ratio_3000 and 0.90 < ratio_3000 < 1.10:
                print("  ✅ STATUS: PASS")
                results['damping'] = 'PASS'
            elif ratio_3000 and 0.80 < ratio_3000 < 1.20:
                print("  ⚠️  STATUS: WARNING")
                results['damping'] = 'WARNING'
            else:
                print("  ❌ STATUS: FAIL")
                results['damping'] = 'FAIL'
        else:
            print("  ⚠️  CMB output files not found")
            results['damping'] = 'UNKNOWN'
        
        print()
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results['damping'] = 'ERROR'
    
    # -------------------------------------------------------------------------
    # TEST 4: β-COUPLING LINEARITY
    # -------------------------------------------------------------------------
    print("[TEST 4] β-Coupling Linearity")
    print("-" * 70)
    
    try:
        betas = [0.0, 0.005, 0.01, 0.015, 0.02]
        pk_values = []
        
        print("  Running β sweep...")
        for beta in betas:
            sweep_params = base_params.copy()
            sweep_params.update({
                'has_ridder': 'yes',
                'Lambda_EDE_ridder': 1.0,
                'f_axion_ridder': 1.0e27,
                'theta_i_ridder': 2.5,
                'beta_ridder': beta,
                'n_ridder': 3,
                'output': 'mPk',
                'P_k_max_1/Mpc': 1.0,
                'z_pk': 0.0
            })
            ini_name = f'stress_beta_{beta:.3f}.ini'
            create_ini(ini_name, sweep_params)
            run_class(ini_name)
            
            # Read P(k) output (find latest run)
            import glob
            pk_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, f"stress_beta_{beta:.3f}*_pk.dat")))
            pk_file = pk_files[-1] if pk_files else None
            if pk_file and os.path.exists(pk_file):
                pk_data = np.loadtxt(pk_file)
                k = pk_data[:, 0]
                pk = pk_data[:, 1]
                
                # Find P(k) at k ~ 0.1 h/Mpc
                idx = np.argmin(np.abs(k - 0.1))
                pk_at_01 = pk[idx]
                pk_values.append(pk_at_01)
                print(f"    β = {beta:.3f}: P(k=0.1) = {pk_at_01:.3e}")
            else:
                print(f"    β = {beta:.3f}: Output file not found")
                pk_values.append(np.nan)
        
        print()
        
        # Check monotonicity
        pk_array = np.array(pk_values)
        valid = ~np.isnan(pk_array)
        if np.sum(valid) >= 2:
            diffs = np.diff(pk_array[valid])
            is_monotonic = np.all(diffs < 0)
            
            print(f"  Monotonic suppression: {is_monotonic}")
            
            if is_monotonic:
                print("  ✅ STATUS: PASS")
                results['coupling'] = 'PASS'
            else:
                print("  ❌ STATUS: FAIL")
                results['coupling'] = 'FAIL'
        else:
            print("  ⚠️  Insufficient data")
            results['coupling'] = 'UNKNOWN'
        
        print()
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results['coupling'] = 'ERROR'
    
    # -------------------------------------------------------------------------
    # FINAL VERDICT
    # -------------------------------------------------------------------------
    print("=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    print()
    
    all_pass = all(r == 'PASS' for r in results.values() if r is not None)
    any_fail = any(r == 'FAIL' or r == 'ERROR' for r in results.values())
    
    print("Test Results:")
    print(f"  [1] BBN Consistency:    {results['bbn']}")
    print(f"  [2] Background:         {results['background']}")
    print(f"  [3] Damping Tail:       {results['damping']}")
    print(f"  [4] Coupling Linearity: {results['coupling']}")
    print()
    
    if all_pass:
        print("✅ CLEARED FOR PHASE 3 MCMC")
        return 0
    elif any_fail:
        print("❌ NOT READY FOR PHASE 3")
        return 1
    else:
        print("⚠️  PROCEED WITH CAUTION")
        return 2

if __name__ == "__main__":
    import sys
    exit_code = run_audit()
    sys.exit(exit_code)

