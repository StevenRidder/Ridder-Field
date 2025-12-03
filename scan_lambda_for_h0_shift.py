#!/usr/bin/env python3
"""
Lambda scan to find EDE configurations with meaningful H₀ shifts.

Target: Δr_s/r_s ~ -3 to -5%, giving ΔH₀^eff ~ 2-3.5 km/s/Mpc

Strategy:
- Fix theta_i = 0.75 (from Phase 2 optimal)
- Scan Lambda from current 0.50 eV up to ~5 eV
- For each Lambda, measure z_peak, f_peak, r_s, and H₀^eff
"""

import subprocess
import numpy as np
import os
import sys
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
    rs = data[:, 7]  # Column 7: comov.snd.hrz.
    
    # Extract at z ~ 1060
    idx_drag = np.argmin(np.abs(z - 1060.0))
    return rs[idx_drag]

def extract_ede_peak(bg_file, z_min=100, z_max=10000):
    """Extract z_peak and f_peak from background file."""
    if not os.path.exists(bg_file):
        return None, None
    
    data = np.loadtxt(bg_file)
    z = data[:, 0]
    rho_ridder = data[:, 14]  # Column 14: rho_ridder
    rho_tot = data[:, 19]     # Column 19: rho_tot
    
    # Mask to search window
    mask = (z >= z_min) & (z <= z_max)
    if not np.any(mask):
        return None, None
    
    z_search = z[mask]
    rho_ridder_search = rho_ridder[mask]
    rho_tot_search = rho_tot[mask]
    
    # Compute fractional contribution
    f_ridder = np.where(rho_tot_search > 0, rho_ridder_search / rho_tot_search, 0)
    
    # Find peak
    idx_peak = np.argmax(f_ridder)
    z_peak = z_search[idx_peak]
    f_peak = f_ridder[idx_peak]
    
    return z_peak, f_peak

def create_lambda_ini(lambda_val, theta_i, output_prefix):
    """Create ini file for given Lambda and theta_i."""
    ini_content = f"""# Lambda Scan: Lambda = {lambda_val:.4f} eV, theta_i = {theta_i:.2f}

# Standard cosmological parameters
H0 = 67.36
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544
YHe = 0.2454

# Ridder field with scanned Lambda
Lambda_EDE_ridder = {lambda_val:.10f}
f_axion_ridder = 2.435e27
theta_i_ridder = {theta_i:.10f}
beta_ridder = 0.0
n_ridder = 3
ridder_c_slow = 1.0

# Full dynamics
ridder_freeze_phi = no
ridder_force_damping = 1.0
use_ridder_shooting = 0

# Gauge
gauge = newtonian

# Output
output = tCl,pCl,lCl,mPk
lensing = yes
l_max_scalars = 2500
P_k_max_h/Mpc = 10.0

# Write files
write background = yes
write thermodynamics = no
write primordial = no

# Output directory
root = output/{output_prefix}_
"""
    
    ini_file = f"scan_lambda_{output_prefix}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini_content)
    
    return ini_file

def main():
    # Reference r_s from vanilla ΛCDM
    rs_lcdm = 147.079129  # From previous run
    h0_input = 67.36
    
    # Scan parameters
    theta_i = 0.75  # Fixed from Phase 2
    
    # Lambda values to scan
    # Current: 0.50 eV → z_peak ~ 691, ΔH₀ ~ +0.3 km/s/Mpc
    # Target: z_peak ~ 3000-5000, ΔH₀ ~ +2-5 km/s/Mpc
    # From Phase 2 empirics: z_peak ∝ Lambda (roughly)
    # So to get z_peak ~ 3000, need Lambda ~ 2-3 eV
    
    lambda_values = [
        0.5,    # Baseline (already run)
        1.0,    # 2× increase
        1.5,    # 3× increase
        2.0,    # 4× increase
        3.0,    # 6× increase
        4.0,    # 8× increase
    ]
    
    print("=" * 90)
    print("LAMBDA SCAN FOR H₀ SHIFTS")
    print("=" * 90)
    print(f"Reference: Vanilla ΛCDM with r_s = {rs_lcdm:.6f} Mpc, H₀ = {h0_input:.4f} km/s/Mpc")
    print(f"Fixed: theta_i = {theta_i:.2f}")
    print(f"Scanning Lambda: {lambda_values}")
    print("=" * 90)
    print()
    
    results = []
    
    for lam in lambda_values:
        print(f"▶ Lambda = {lam:.2f} eV")
        print("-" * 90)
        
        # Create output prefix
        output_prefix = f"lambda{lam:.2f}_theta{theta_i:.2f}".replace('.', 'p')
        
        # Check if already run (Lambda = 0.5 case)
        if lam == 0.5:
            bg_file = "output/benchmark_ede_theta075_00_background.dat"
            cl_file = "output/benchmark_ede_theta075_00_cl.dat"
            
            if os.path.exists(bg_file):
                print("  Using existing run (benchmark_ede_theta075)")
            else:
                print("  ERROR: Baseline run not found!")
                continue
        else:
            # Create ini file
            ini_file = create_lambda_ini(lam, theta_i, output_prefix)
            print(f"  Created: {ini_file}")
            
            # Run CLASS
            print(f"  Running CLASS...")
            success, stdout, stderr = run_class(ini_file, timeout=180)
            
            if not success:
                print(f"  ❌ FAILED: {stderr[:200]}")
                results.append({
                    'lambda': lam,
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
                    'lambda': lam,
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
                'lambda': lam,
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
            'lambda': lam,
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
    print(f"{'Lambda [eV]':<12} {'z_peak':<10} {'f_peak':<10} {'r_s [Mpc]':<12} "
          f"{'H₀^eff':<12} {'ΔH₀ [km/s/Mpc]':<18}")
    print("-" * 90)
    
    for res in results:
        if res['status'] == 'success':
            print(f"{res['lambda']:<12.2f} {res['z_peak']:<10.1f} {res['f_peak']:<10.4f} "
                  f"{res['rs']:<12.6f} {res['h0_eff']:<12.4f} "
                  f"{res['delta_h0']:>+7.4f} ({res['delta_h0']/h0_input*100:+.2f}%)")
        else:
            print(f"{res['lambda']:<12.2f} {'FAILED':<10} {res['status']}")
    
    print()
    print("=" * 90)
    
    # Find best candidate
    successful = [r for r in results if r['status'] == 'success' and r['delta_h0'] is not None]
    if successful:
        # Sort by |ΔH₀ - 3.0| to find closest to target ~3 km/s/Mpc
        target_delta_h0 = 3.0
        successful_sorted = sorted(successful, key=lambda r: abs(r['delta_h0'] - target_delta_h0))
        best = successful_sorted[0]
        
        print("RECOMMENDATION:")
        print("-" * 90)
        print(f"Best candidate: Lambda = {best['lambda']:.2f} eV")
        print(f"  z_peak = {best['z_peak']:.1f}  (target: ~3000-5000)")
        print(f"  f_peak = {best['f_peak']*100:.2f}%  (target: ~10%)")
        print(f"  ΔH₀^eff = {best['delta_h0']:+.4f} km/s/Mpc  (target: ~3-5 km/s/Mpc)")
        print()
        
        if best['z_peak'] < 2000:
            print("  ⚠️  z_peak still too late. Consider higher Lambda.")
        elif best['z_peak'] > 6000:
            print("  ⚠️  z_peak too early. Consider lower Lambda.")
        else:
            print("  ✅ z_peak in good range!")
        
        if best['f_peak'] < 0.08:
            print("  ⚠️  f_peak too small. Consider increasing theta_i.")
        elif best['f_peak'] > 0.15:
            print("  ⚠️  f_peak too large. Consider decreasing theta_i.")
        else:
            print("  ✅ f_peak in good range!")
        
        if abs(best['delta_h0']) < 2.0:
            print("  ⚠️  ΔH₀ too small. Need stronger EDE.")
        elif abs(best['delta_h0']) > 8.0:
            print("  ⚠️  ΔH₀ very large. Check CMB spectrum quality.")
        else:
            print("  ✅ ΔH₀ in tension-relevant range!")
        
        print()
        print("=" * 90)

if __name__ == "__main__":
    main()

