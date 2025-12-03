#!/usr/bin/env python3
"""
CDM Coupling Optimization: Find the Sweet Spot

Goal: Map the (beta, sigma_z) efficiency frontier
Target: ΔH₀ ≥ +3.5 km/s/Mpc with Max CMB Δ ≤ 40%

Based on breakthrough results:
- β=0.2, sigma=0.3: ΔH₀=+2.89, CMB=34.7% ✓ CMB, but low ΔH₀
- β=0.2, sigma=1.0: ΔH₀=+4.29, CMB=55.9% ✓ ΔH₀, but poor CMB
- Sweet spot likely: β~0.15-0.25, sigma~0.5-0.8
"""

import subprocess
import numpy as np
import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run_class_config(beta, sigma_z, z_c=3000):
    """Run CLASS with specific CDM coupling configuration."""
    
    config_name = f"opt_beta{beta:.2f}_sig{sigma_z:.1f}".replace('.', 'p')
    
    ini_content = f"""# CDM coupling optimization
# beta = {beta}, sigma_z = {sigma_z}, z_c = {z_c}

H0 = 67.36
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544

# Optimal EDE configuration
Lambda_EDE_ridder = 1.5
f_axion_ridder = 2.435e27
theta_i_ridder = 1.0
n_ridder = 3
ridder_c_slow = 1.0
ridder_freeze_phi = no
ridder_force_damping = 1.0

# CDM coupling parameters (OPTIMIZATION)
beta_ridder = {beta}
beta_z_c = {z_c}
beta_sigma_z = {sigma_z}
ridder_perturbation_mode = 0

# Output
gauge = newtonian
output = tCl,pCl,lCl
lensing = yes
l_max_scalars = 2500

write background = yes
root = output/{config_name}_
"""
    
    ini_file = f"optimize_{config_name}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini_content)
    
    result = subprocess.run(
        ['./phase2/class/class', ini_file],
        capture_output=True,
        text=True,
        timeout=180
    )
    
    if result.returncode != 0:
        return None, None
    
    import glob
    bg_files = glob.glob(f"output/{config_name}_*_background.dat")
    cl_files = glob.glob(f"output/{config_name}_*_cl.dat")
    
    if not bg_files or not cl_files:
        return None, None
    
    return bg_files[0], cl_files[0]

def extract_metrics(bg_file, cl_file, lcdm_cl_file):
    """Extract H0 and CMB quality metrics."""
    # r_s and H0
    data = np.loadtxt(bg_file)
    z = data[:, 0]
    rs = data[:, 7]
    idx_drag = np.argmin(np.abs(z - 1060.0))
    rs_drag = rs[idx_drag]
    
    rs_lcdm = 147.079129
    h0_input = 67.36
    h0_eff = h0_input * (rs_lcdm / rs_drag)
    delta_h0 = h0_eff - h0_input
    
    # CMB quality
    lcdm = np.loadtxt(lcdm_cl_file)
    ede = np.loadtxt(cl_file)
    
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
    max_diff_pct = np.max(np.abs(delta_frac[mask_full])) * 100
    rms_diff_pct = np.sqrt(np.mean(delta_frac[mask_full]**2)) * 100
    
    return {
        'rs': rs_drag,
        'h0_eff': h0_eff,
        'delta_h0': delta_h0,
        'delta_ell': delta_ell,
        'max_cmb_diff': max_diff_pct,
        'rms_cmb_diff': rms_diff_pct
    }

def main():
    print("=" * 90)
    print("CDM COUPLING OPTIMIZATION: FINDING THE SWEET SPOT")
    print("=" * 90)
    print()
    print("OBJECTIVE: Map (β, σ_z) efficiency frontier")
    print("TARGET: ΔH₀ ≥ +3.5 km/s/Mpc with Max CMB Δ ≤ 40%")
    print()
    print("Based on breakthrough:")
    print("  β=0.2, σ=0.3: ΔH₀=+2.89, CMB=34.7% (acceptable CMB, low ΔH₀)")
    print("  β=0.2, σ=1.0: ΔH₀=+4.29, CMB=55.9% (great ΔH₀, poor CMB)")
    print()
    print("Search space:")
    print("  β ∈ [0.10, 0.15, 0.20, 0.25, 0.30]")
    print("  σ_z ∈ [0.3, 0.5, 0.7, 0.9, 1.0]")
    print("  z_c = 3000 (fixed at optimal)")
    print()
    print("=" * 90)
    print()
    
    lcdm_cl_file = 'output/benchmark_vanilla_lcdm_00_cl.dat'
    
    # Grid parameters
    beta_values = [0.10, 0.15, 0.20, 0.25, 0.30]
    sigma_z_values = [0.3, 0.5, 0.7, 0.9, 1.0]
    z_c = 3000
    
    results = []
    total_configs = len(beta_values) * len(sigma_z_values)
    config_num = 0
    
    for beta in beta_values:
        for sigma_z in sigma_z_values:
            config_num += 1
            
            print(f"[{config_num}/{total_configs}] β={beta:.2f}, σ_z={sigma_z:.1f}")
            print("-" * 90)
            
            bg_file, cl_file = run_class_config(beta, sigma_z, z_c)
            
            if bg_file is None:
                print("  ❌ FAILED")
                results.append({'beta': beta, 'sigma_z': sigma_z, 'status': 'failed'})
                print()
                continue
            
            metrics = extract_metrics(bg_file, cl_file, lcdm_cl_file)
            
            print(f"  ΔH₀         = {metrics['delta_h0']:+.4f} km/s/Mpc")
            print(f"  Max CMB Δ   = {metrics['max_cmb_diff']:.1f}%")
            print(f"  RMS CMB Δ   = {metrics['rms_cmb_diff']:.1f}%")
            
            # Assess vs criteria
            passes_h0 = metrics['delta_h0'] >= 3.5
            passes_cmb = metrics['max_cmb_diff'] <= 40.0
            
            if passes_h0 and passes_cmb:
                verdict = "🎯 SWEET SPOT!"
            elif passes_h0:
                verdict = "✓ Good ΔH₀, CMB high"
            elif passes_cmb:
                verdict = "✓ Good CMB, ΔH₀ low"
            else:
                verdict = "Explore"
            
            print(f"  → {verdict}")
            print()
            
            results.append({
                'beta': beta,
                'sigma_z': sigma_z,
                'status': 'success',
                **metrics
            })
    
    # Analysis
    print("=" * 90)
    print("OPTIMIZATION COMPLETE")
    print("=" * 90)
    print()
    
    successful = [r for r in results if r['status'] == 'success']
    
    if not successful:
        print("❌ All configurations failed")
        return
    
    # Summary table
    print("FULL RESULTS TABLE:")
    print()
    print(f"{'β':<8} {'σ_z':<8} {'ΔH₀':<12} {'Max CMB':<10} {'RMS CMB':<10} {'Status':<20}")
    print("-" * 90)
    
    for r in successful:
        passes_h0 = r['delta_h0'] >= 3.5
        passes_cmb = r['max_cmb_diff'] <= 40.0
        
        if passes_h0 and passes_cmb:
            status = "🎯 SWEET SPOT"
        elif passes_h0:
            status = "High ΔH₀"
        elif passes_cmb:
            status = "Low CMB"
        else:
            status = ""
        
        print(f"{r['beta']:<8.2f} {r['sigma_z']:<8.1f} {r['delta_h0']:>+11.4f} "
              f"{r['max_cmb_diff']:>9.1f}% {r['rms_cmb_diff']:>9.1f}% {status:<20}")
    
    print()
    print("=" * 90)
    print("EFFICIENCY FRONTIER ANALYSIS")
    print("=" * 90)
    print()
    
    # Find sweet spots
    sweet_spots = [r for r in successful if r['delta_h0'] >= 3.5 and r['max_cmb_diff'] <= 40.0]
    
    if sweet_spots:
        print(f"✅ FOUND {len(sweet_spots)} SWEET SPOT(S):")
        print()
        
        for r in sweet_spots:
            tension_reduction_pct = (r['delta_h0'] / (73.0 - 67.36)) * 100
            print(f"  β={r['beta']:.2f}, σ_z={r['sigma_z']:.1f}:")
            print(f"    ΔH₀ = {r['delta_h0']:+.4f} km/s/Mpc ({tension_reduction_pct:.0f}% tension reduction)")
            print(f"    H₀^eff = {r['h0_eff']:.2f} km/s/Mpc (target: ~73)")
            print(f"    Max CMB Δ = {r['max_cmb_diff']:.1f}% (threshold: 40%)")
            print(f"    RMS CMB Δ = {r['rms_cmb_diff']:.1f}%")
            print()
        
        # Best sweet spot
        best = max(sweet_spots, key=lambda r: r['delta_h0'])
        
        print("RECOMMENDED CONFIGURATION:")
        print(f"  β_ridder = {best['beta']:.2f}")
        print(f"  beta_z_c = {z_c}")
        print(f"  beta_sigma_z = {best['sigma_z']:.1f}")
        print()
        print(f"  → ΔH₀ = {best['delta_h0']:+.4f} km/s/Mpc")
        print(f"  → Max CMB Δ = {best['max_cmb_diff']:.1f}%")
        print()
        print("NEXT STEPS:")
        print("  1. Test this config with full observables (σ₈, S₈, etc.)")
        print("  2. Consider fluid mode to further improve CMB")
        print("  3. Proceed to MCMC Tier 3 with this as baseline")
        
    else:
        print("⚠️  NO PERFECT SWEET SPOTS FOUND")
        print()
        print("Trade-off analysis:")
        
        # Best H0 with acceptable CMB
        acceptable_cmb = [r for r in successful if r['max_cmb_diff'] <= 45.0]
        if acceptable_cmb:
            best_h0_acceptable = max(acceptable_cmb, key=lambda r: r['delta_h0'])
            print(f"\n  Best ΔH₀ with CMB ≤ 45%:")
            print(f"    β={best_h0_acceptable['beta']:.2f}, σ_z={best_h0_acceptable['sigma_z']:.1f}")
            print(f"    ΔH₀ = {best_h0_acceptable['delta_h0']:+.4f} km/s/Mpc")
            print(f"    Max CMB Δ = {best_h0_acceptable['max_cmb_diff']:.1f}%")
        
        # Best CMB with good H0
        good_h0 = [r for r in successful if r['delta_h0'] >= 3.0]
        if good_h0:
            best_cmb_good_h0 = min(good_h0, key=lambda r: r['max_cmb_diff'])
            print(f"\n  Best CMB with ΔH₀ ≥ +3.0:")
            print(f"    β={best_cmb_good_h0['beta']:.2f}, σ_z={best_cmb_good_h0['sigma_z']:.1f}")
            print(f"    ΔH₀ = {best_cmb_good_h0['delta_h0']:+.4f} km/s/Mpc")
            print(f"    Max CMB Δ = {best_cmb_good_h0['max_cmb_diff']:.1f}%")
    
    # Save results
    with open('cdm_coupling_optimization_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create efficiency frontier plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for r in successful:
        if r['delta_h0'] >= 3.5 and r['max_cmb_diff'] <= 40.0:
            color = 'green'
            marker = '*'
            size = 200
            label = 'Sweet Spot' if 'Sweet Spot' not in [l.get_label() for l in ax.get_children()] else ''
        elif r['delta_h0'] >= 3.5:
            color = 'orange'
            marker = 'o'
            size = 100
            label = 'High ΔH₀' if 'High ΔH₀' not in [l.get_label() for l in ax.get_children()] else ''
        elif r['max_cmb_diff'] <= 40.0:
            color = 'blue'
            marker = 's'
            size = 100
            label = 'Low CMB' if 'Low CMB' not in [l.get_label() for l in ax.get_children()] else ''
        else:
            color = 'gray'
            marker = 'x'
            size = 50
            label = ''
        
        ax.scatter(r['max_cmb_diff'], r['delta_h0'], c=color, marker=marker, s=size, 
                  alpha=0.7, edgecolors='black', label=label)
        ax.text(r['max_cmb_diff'] + 1, r['delta_h0'], 
               f"β={r['beta']:.2f}\nσ={r['sigma_z']:.1f}", 
               fontsize=8, alpha=0.7)
    
    # Target lines
    ax.axhline(y=3.5, color='red', linestyle='--', alpha=0.5, label='Target ΔH₀ = +3.5')
    ax.axvline(x=40.0, color='purple', linestyle='--', alpha=0.5, label='Target CMB = 40%')
    
    ax.set_xlabel('Max CMB Distortion (%)', fontsize=12)
    ax.set_ylabel('ΔH₀ (km/s/Mpc)', fontsize=12)
    ax.set_title('CDM Coupling Efficiency Frontier', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('cdm_coupling_efficiency_frontier.png', dpi=300)
    
    print()
    print("=" * 90)
    print()
    print("Results saved to:")
    print("  - cdm_coupling_optimization_results.json")
    print("  - cdm_coupling_efficiency_frontier.png")
    print()
    print("=" * 90)

if __name__ == "__main__":
    main()

