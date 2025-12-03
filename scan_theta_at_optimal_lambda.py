#!/usr/bin/env python3
"""
Theta_i scan at optimal Lambda to boost f_peak and ΔH₀.

From Lambda scan: Lambda ~ 1.5 eV gives z_peak ~ 2523, but f_peak ~ 7.3% is too small.
Need to increase theta_i to reach f_peak ~ 10-12% and ΔH₀ ~ 3-5 km/s/Mpc.
"""

import subprocess
import numpy as np
import os
import glob

def run_class(ini_file, timeout=120):
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

def create_theta_ini(lambda_val, theta_i, output_prefix):
    """Create ini file for given Lambda and theta_i."""
    ini_content = f"""# Theta scan at optimal Lambda: Lambda = {lambda_val:.4f} eV, theta_i = {theta_i:.2f}

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
n_ridder = 3
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
    
    ini_file = f"scan_theta_{output_prefix}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini_content)
    
    return ini_file

def main():
    # Reference
    rs_lcdm = 147.079129
    h0_input = 67.36
    
    # Optimal Lambda from previous scan
    lambda_val = 1.5
    
    # Theta values to scan
    # From Phase 2: higher theta_i → higher f_peak
    # Current: theta_i = 0.75 → f_peak ~ 7.3%
    # Target: f_peak ~ 10-12%
    theta_values = [
        0.75,   # Baseline
        1.00,   # Higher amplitude
        1.25,   # Even higher
        1.50,   # From Phase 2, this was ~6% at Lambda×30
        1.75,
        2.00,
    ]
    
    print("=" * 90)
    print("THETA_I SCAN AT OPTIMAL LAMBDA")
    print("=" * 90)
    print(f"Reference: Vanilla ΛCDM with r_s = {rs_lcdm:.6f} Mpc, H₀ = {h0_input:.4f} km/s/Mpc")
    print(f"Fixed: Lambda = {lambda_val:.2f} eV (optimal from Lambda scan)")
    print(f"Scanning theta_i: {theta_values}")
    print(f"Goal: f_peak ~ 10-12%, ΔH₀ ~ 3-5 km/s/Mpc")
    print("=" * 90)
    print()
    
    results = []
    
    for theta in theta_values:
        print(f"▶ theta_i = {theta:.2f}")
        print("-" * 90)
        
        output_prefix = f"lambda{lambda_val:.2f}_theta{theta:.2f}".replace('.', 'p')
        
        # Check if already run (theta = 0.75 case from Lambda scan)
        if theta == 0.75:
            bg_files = glob.glob("output/lambda1p50_theta0p75_*_background.dat")
            
            if bg_files:
                bg_file = bg_files[0]
                print("  Using existing run from Lambda scan")
            else:
                print("  ERROR: Baseline run not found!")
                continue
        else:
            # Create ini file
            ini_file = create_theta_ini(lambda_val, theta, output_prefix)
            print(f"  Created: {ini_file}")
            
            # Run CLASS
            print(f"  Running CLASS...")
            success, stdout, stderr = run_class(ini_file, timeout=180)
            
            if not success:
                print(f"  ❌ FAILED: {stderr[:200]}")
                results.append({
                    'theta': theta,
                    'status': 'failed',
                    'z_peak': None,
                    'f_peak': None,
                    'rs': None,
                    'h0_eff': None,
                    'delta_h0': None
                })
                print()
                continue
            
            print(f"  ✅ Success")
            
            # Find output files
            bg_pattern = f"output/{output_prefix}_*_background.dat"
            bg_files = glob.glob(bg_pattern)
            
            if not bg_files:
                print(f"  ❌ No background file found: {bg_pattern}")
                results.append({
                    'theta': theta,
                    'status': 'no_output',
                    'z_peak': None,
                    'f_peak': None,
                    'rs': None,
                    'h0_eff': None,
                    'delta_h0': None
                })
                print()
                continue
            
            bg_file = bg_files[0]
        
        # Extract observables
        z_peak, f_peak = extract_ede_peak(bg_file, z_min=100, z_max=20000)
        rs_ede = extract_rs_from_background(bg_file)
        
        if rs_ede is None or z_peak is None:
            print(f"  ❌ Failed to extract observables")
            results.append({
                'theta': theta,
                'status': 'extraction_failed',
                'z_peak': z_peak,
                'f_peak': f_peak,
                'rs': rs_ede,
                'h0_eff': None,
                'delta_h0': None
            })
            print()
            continue
        
        # Compute effective H₀
        h0_eff = h0_input * (rs_lcdm / rs_ede)
        delta_h0 = h0_eff - h0_input
        delta_rs_pct = (rs_ede - rs_lcdm) / rs_lcdm * 100
        
        print(f"  z_peak = {z_peak:.1f}")
        print(f"  f_peak = {f_peak:.4f} ({f_peak*100:.2f}%)")
        print(f"  r_s = {rs_ede:.6f} Mpc  (Δr_s/r_s = {delta_rs_pct:+.3f}%)")
        print(f"  H₀^eff = {h0_eff:.4f} km/s/Mpc  (ΔH₀ = {delta_h0:+.4f} km/s/Mpc)")
        
        results.append({
            'theta': theta,
            'status': 'success',
            'z_peak': z_peak,
            'f_peak': f_peak,
            'rs': rs_ede,
            'h0_eff': h0_eff,
            'delta_h0': delta_h0,
            'delta_rs_pct': delta_rs_pct
        })
        print()
    
    # Print summary table
    print("=" * 90)
    print("SUMMARY TABLE")
    print("=" * 90)
    print()
    print(f"{'theta_i':<10} {'z_peak':<10} {'f_peak':<10} {'r_s [Mpc]':<12} "
          f"{'H₀^eff':<12} {'ΔH₀ [km/s/Mpc]':<18}")
    print("-" * 90)
    
    for res in results:
        if res['status'] == 'success':
            print(f"{res['theta']:<10.2f} {res['z_peak']:<10.1f} {res['f_peak']:<10.4f} "
                  f"{res['rs']:<12.6f} {res['h0_eff']:<12.4f} "
                  f"{res['delta_h0']:>+7.4f} ({res['delta_h0']/h0_input*100:+.2f}%)")
        else:
            print(f"{res['theta']:<10.2f} {'FAILED':<10} {res['status']}")
    
    print()
    print("=" * 90)
    
    # Find best candidate
    successful = [r for r in results if r['status'] == 'success' and r['delta_h0'] is not None]
    if successful:
        # Sort by |ΔH₀ - 3.5| to find closest to target ~3-4 km/s/Mpc
        target_delta_h0 = 3.5
        successful_sorted = sorted(successful, key=lambda r: abs(r['delta_h0'] - target_delta_h0))
        best = successful_sorted[0]
        
        print("RECOMMENDATION:")
        print("-" * 90)
        print(f"Best candidate: Lambda = {lambda_val:.2f} eV, theta_i = {best['theta']:.2f}")
        print(f"  z_peak = {best['z_peak']:.1f}")
        print(f"  f_peak = {best['f_peak']*100:.2f}%")
        print(f"  Δr_s/r_s = {best['delta_rs_pct']:+.3f}%")
        print(f"  ΔH₀^eff = {best['delta_h0']:+.4f} km/s/Mpc")
        print()
        
        if best['f_peak'] >= 0.08 and best['f_peak'] <= 0.15:
            print("  ✅ f_peak in good range!")
        else:
            print("  ⚠️  f_peak out of target range")
        
        if abs(best['delta_h0']) >= 2.0 and abs(best['delta_h0']) <= 6.0:
            print("  ✅ ΔH₀ in tension-relevant range!")
        else:
            print("  ⚠️  ΔH₀ out of target range")
        
        print()
        print("=" * 90)

if __name__ == "__main__":
    main()

