#!/usr/bin/env python3
"""
Phase 4, Week 1: n_ridder Parameter Scan

Goal: Test if potential shape (n) improves efficiency
Baseline: Lambda=1.5 eV, theta=1.0 (Phase 3 optimal)
Scan: n = [2, 3, 4, 5]

Success: Find n where ΔH₀ > +2.5 km/s/Mpc with similar CMB quality
"""

import subprocess
import numpy as np
import os
import glob

def run_class(ini_file, timeout=180):
    """Run CLASS with given ini file."""
    try:
        result = subprocess.run(
            ['./phase2/class/class', ini_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"

def extract_rs_from_background(bg_file):
    """Extract r_s at drag from background file."""
    if not os.path.exists(bg_file):
        return None
    
    data = np.loadtxt(bg_file)
    z = data[:, 0]
    rs = data[:, 7]
    
    idx_drag = np.argmin(np.abs(z - 1060.0))
    return rs[idx_drag]

def extract_ede_peak(bg_file, z_min=100, z_max=20000):
    """Extract z_peak and f_peak from background file."""
    if not os.path.exists(bg_file):
        return None, None
    
    data = np.loadtxt(bg_file)
    z = data[:, 0]
    rho_ridder = data[:, 14]
    rho_tot = data[:, 19]
    
    mask = (z >= z_min) & (z <= z_max)
    if not np.any(mask):
        return None, None
    
    z_search = z[mask]
    rho_ridder_search = rho_ridder[mask]
    rho_tot_search = rho_tot[mask]
    
    f_ridder = np.where(rho_tot_search > 0, rho_ridder_search / rho_tot_search, 0)
    
    idx_peak = np.argmax(f_ridder)
    z_peak = z_search[idx_peak]
    f_peak = f_ridder[idx_peak]
    
    return z_peak, f_peak

def assess_cmb_quality_simple(lcdm_cl_file, ede_cl_file):
    """Quick CMB quality check."""
    if not os.path.exists(lcdm_cl_file) or not os.path.exists(ede_cl_file):
        return None
    
    lcdm = np.loadtxt(lcdm_cl_file)
    ede = np.loadtxt(ede_cl_file)
    
    ell_lcdm = lcdm[:, 0]
    D_lcdm = lcdm[:, 1]
    ell_ede = ede[:, 0]
    D_ede = ede[:, 1]
    
    # Peak shift
    mask_peak = (ell_lcdm > 50) & (ell_lcdm < 400)
    ell_peak_lcdm = ell_lcdm[mask_peak][np.argmax(D_lcdm[mask_peak])]
    ell_peak_ede = ell_ede[mask_peak][np.argmax(D_ede[mask_peak])]
    delta_ell = ell_peak_ede - ell_peak_lcdm
    
    # Fractional differences
    D_ede_interp = np.interp(ell_lcdm, ell_ede, D_ede)
    delta_frac = (D_ede_interp - D_lcdm) / D_lcdm
    
    mask_full = (ell_lcdm >= 30) & (ell_lcdm <= 2000)
    max_abs_diff = np.max(np.abs(delta_frac[mask_full])) * 100
    rms_diff = np.sqrt(np.mean(delta_frac[mask_full]**2)) * 100
    
    return {
        'delta_ell': delta_ell,
        'max_diff_pct': max_abs_diff,
        'rms_diff_pct': rms_diff
    }

def create_n_scan_ini(lambda_val, theta_i, n_val, output_prefix):
    """Create ini file for n-scan."""
    ini_content = f"""# Phase 4, Week 1: n-scan
# Lambda = {lambda_val:.4f} eV, theta_i = {theta_i:.2f}, n = {n_val}

H0 = 67.36
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544
YHe = 0.2454

Lambda_EDE_ridder = {lambda_val:.10f}
f_axion_ridder = 2.435e27
theta_i_ridder = {theta_i:.10f}
beta_ridder = 0.0
n_ridder = {n_val}
ridder_c_slow = 1.0

ridder_freeze_phi = no
ridder_force_damping = 1.0
use_ridder_shooting = 0

gauge = newtonian

output = tCl,pCl,lCl,mPk
lensing = yes
l_max_scalars = 2500
P_k_max_h/Mpc = 10.0

write background = yes
write thermodynamics = no
write primordial = no

root = output/{output_prefix}_
"""
    
    ini_file = f"week1_n_scan_{output_prefix}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini_content)
    
    return ini_file

def main():
    # Reference
    rs_lcdm = 147.079129
    h0_input = 67.36
    lcdm_cl_file = 'output/benchmark_vanilla_lcdm_00_cl.dat'
    
    # Fixed parameters (Phase 3 optimal)
    lambda_val = 1.5
    theta_i = 1.0
    
    # n values to scan
    n_values = [2, 3, 4, 5]
    
    print("=" * 90)
    print("PHASE 4, WEEK 1: n_ridder SCAN")
    print("=" * 90)
    print(f"Goal: Find potential shape (n) that boosts efficiency")
    print(f"Baseline: Lambda = {lambda_val:.2f} eV, theta_i = {theta_i:.2f}")
    print(f"Phase 3 result: n=3 gave ΔH₀ = +2.06 km/s/Mpc")
    print(f"Target: ΔH₀ > +2.5 km/s/Mpc")
    print("=" * 90)
    print()
    
    results = []
    
    for n in n_values:
        print(f"▶ n_ridder = {n}")
        print("-" * 90)
        
        output_prefix = f"n{n}_lambda{lambda_val:.2f}_theta{theta_i:.2f}".replace('.', 'p')
        
        # Check if this is n=3 from Phase 3 (can reuse)
        if n == 3:
            # Look for existing theta=1.0 run from Phase 3
            bg_files = glob.glob("output/lambda1p50_theta1p00_*_background.dat")
            cl_files = glob.glob("output/lambda1p50_theta1p00_*_cl.dat")
            
            if bg_files and cl_files:
                print("  Using existing n=3 run from Phase 3")
                bg_file = bg_files[0]
                cl_file = cl_files[0]
            else:
                print("  Phase 3 run not found, running new...")
                # Create and run
                ini_file = create_n_scan_ini(lambda_val, theta_i, n, output_prefix)
                success, stdout, stderr = run_class(ini_file, timeout=180)
                
                if not success:
                    print(f"  ❌ FAILED")
                    results.append({'n': n, 'status': 'failed'})
                    print()
                    continue
                
                bg_files = glob.glob(f"output/{output_prefix}_*_background.dat")
                cl_files = glob.glob(f"output/{output_prefix}_*_cl.dat")
                bg_file = bg_files[0] if bg_files else None
                cl_file = cl_files[0] if cl_files else None
        else:
            # Create ini file
            ini_file = create_n_scan_ini(lambda_val, theta_i, n, output_prefix)
            print(f"  Created: {ini_file}")
            
            # Run CLASS
            print(f"  Running CLASS...")
            success, stdout, stderr = run_class(ini_file, timeout=180)
            
            if not success:
                print(f"  ❌ FAILED: {stderr[:200]}")
                results.append({'n': n, 'status': 'failed'})
                print()
                continue
            
            print(f"  ✅ Success")
            
            # Find output files
            bg_files = glob.glob(f"output/{output_prefix}_*_background.dat")
            cl_files = glob.glob(f"output/{output_prefix}_*_cl.dat")
            
            if not bg_files or not cl_files:
                print(f"  ❌ No output files found")
                results.append({'n': n, 'status': 'no_output'})
                print()
                continue
            
            bg_file = bg_files[0]
            cl_file = cl_files[0]
        
        # Extract observables
        z_peak, f_peak = extract_ede_peak(bg_file, z_min=100, z_max=20000)
        rs_ede = extract_rs_from_background(bg_file)
        cmb_quality = assess_cmb_quality_simple(lcdm_cl_file, cl_file)
        
        if rs_ede is None or z_peak is None or cmb_quality is None:
            print(f"  ❌ Failed to extract observables")
            results.append({'n': n, 'status': 'extraction_failed'})
            print()
            continue
        
        # Compute effective H₀
        h0_eff = h0_input * (rs_lcdm / rs_ede)
        delta_h0 = h0_eff - h0_input
        delta_rs_pct = (rs_ede - rs_lcdm) / rs_lcdm * 100
        
        # Compute efficiency
        efficiency = delta_h0 / f_peak if f_peak > 0 else 0  # km/s/Mpc per unit f_peak
        
        print(f"  z_peak = {z_peak:.1f}")
        print(f"  f_peak = {f_peak:.4f} ({f_peak*100:.2f}%)")
        print(f"  r_s = {rs_ede:.6f} Mpc  (Δr_s/r_s = {delta_rs_pct:+.3f}%)")
        print(f"  H₀^eff = {h0_eff:.4f} km/s/Mpc  (ΔH₀ = {delta_h0:+.4f} km/s/Mpc)")
        print(f"  Efficiency = {efficiency:.3f} km/s/Mpc per % f_peak")
        print(f"  CMB: Δℓ={cmb_quality['delta_ell']:+.1f}, max Δ={cmb_quality['max_diff_pct']:.1f}%, "
              f"RMS={cmb_quality['rms_diff_pct']:.1f}%")
        
        results.append({
            'n': n,
            'status': 'success',
            'z_peak': z_peak,
            'f_peak': f_peak,
            'rs': rs_ede,
            'h0_eff': h0_eff,
            'delta_h0': delta_h0,
            'delta_rs_pct': delta_rs_pct,
            'efficiency': efficiency,
            'delta_ell': cmb_quality['delta_ell'],
            'max_diff_pct': cmb_quality['max_diff_pct'],
            'rms_diff_pct': cmb_quality['rms_diff_pct']
        })
        print()
    
    # Summary table
    print("=" * 90)
    print("SUMMARY TABLE")
    print("=" * 90)
    print()
    print(f"{'n':<5} {'z_peak':<10} {'f_peak':<10} {'ΔH₀':<12} {'Efficiency':<12} "
          f"{'Δℓ':<8} {'Max Δ%':<10} {'Status':<15}")
    print("-" * 90)
    
    for res in results:
        if res['status'] == 'success':
            status = ""
            if res['delta_h0'] >= 2.5:
                status = "✅ TARGET MET"
            elif res['delta_h0'] >= 2.2:
                status = "⚠️  IMPROVED"
            else:
                status = "BASELINE"
            
            print(f"{res['n']:<5} {res['z_peak']:<10.1f} {res['f_peak']:<10.4f} "
                  f"{res['delta_h0']:>+11.4f} {res['efficiency']:>11.3f} "
                  f"{res['delta_ell']:>+7.1f} {res['max_diff_pct']:>9.1f} {status:<15}")
        else:
            print(f"{res['n']:<5} {'FAILED':<10} {res['status']}")
    
    print()
    print("=" * 90)
    
    # Analysis
    successful = [r for r in results if r['status'] == 'success']
    
    if len(successful) >= 2:
        print("ANALYSIS:")
        print("-" * 90)
        
        # Find best by efficiency
        best_eff = max(successful, key=lambda r: r['efficiency'])
        best_h0 = max(successful, key=lambda r: r['delta_h0'])
        baseline = [r for r in successful if r['n'] == 3][0] if any(r['n'] == 3 for r in successful) else successful[0]
        
        print(f"Baseline (n=3): ΔH₀ = {baseline['delta_h0']:+.4f} km/s/Mpc, "
              f"Efficiency = {baseline['efficiency']:.3f}")
        print()
        print(f"Best efficiency: n={best_eff['n']}")
        print(f"  ΔH₀ = {best_eff['delta_h0']:+.4f} km/s/Mpc ({(best_eff['delta_h0']/baseline['delta_h0']-1)*100:+.1f}%)")
        print(f"  Efficiency = {best_eff['efficiency']:.3f} ({(best_eff['efficiency']/baseline['efficiency']-1)*100:+.1f}%)")
        print(f"  CMB max Δ = {best_eff['max_diff_pct']:.1f}%")
        print()
        
        if best_h0['n'] != best_eff['n']:
            print(f"Best ΔH₀: n={best_h0['n']}")
            print(f"  ΔH₀ = {best_h0['delta_h0']:+.4f} km/s/Mpc")
            print(f"  f_peak = {best_h0['f_peak']*100:.2f}%")
            print()
        
        # Recommendation
        print("RECOMMENDATION:")
        print("-" * 90)
        
        if best_eff['delta_h0'] >= 2.5:
            print(f"✅ SUCCESS: n={best_eff['n']} achieves ΔH₀ > +2.5 km/s/Mpc target!")
            print(f"   Proceed to Week 2 with n={best_eff['n']}")
        elif best_eff['delta_h0'] >= 2.2:
            print(f"⚠️  PARTIAL: n={best_eff['n']} shows improvement but below target")
            print(f"   Improvement: {(best_eff['delta_h0']/baseline['delta_h0']-1)*100:.1f}%")
            print(f"   Recommend: Proceed to Week 2 with n={best_eff['n']}, combine with beta")
        else:
            print(f"❌ LIMITED: n-variation doesn't significantly improve efficiency")
            print(f"   Max improvement: {(best_eff['delta_h0']/baseline['delta_h0']-1)*100:.1f}%")
            print(f"   Recommend: Focus on Week 2 (beta coupling) and Week 3 (perturbations)")
        
        print()
        print("=" * 90)

if __name__ == "__main__":
    main()

