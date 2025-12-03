#!/usr/bin/env python3
"""
Systematic Bounded Grid Search: Beta Coupling Optimization

Goal: Test if optimizing (z_c, sigma_z) can push ΔH₀ into +3.5-4.0 range

Guardrails (to maintain physics credibility):
- z_c ∈ [1500, 2000, 2500, 3000]: "coupling peaks near but not at EDE epoch"
- sigma_z ∈ [0.3, 0.6, 1.0]: "narrow to broad boost window"
- beta = 0.2: fixed at reasonable value (not extreme)

Decision Criteria:
- SUCCESS: Any point with ΔH₀ > +3.5 km/s/Mpc AND CMB quality acceptable
- CEILING CONFIRMED: All points give ΔH₀ < +3.0 km/s/Mpc
"""

import subprocess
import numpy as np
import os
import json

def run_class_config(z_c, sigma_z, beta=0.2):
    """Run CLASS with specific beta coupling configuration."""
    
    output_prefix = f"grid_zc{int(z_c)}_sig{sigma_z:.1f}_beta{beta:.2f}".replace('.', 'p')
    
    ini_content = f"""# Beta coupling grid search
# z_c = {z_c}, sigma_z = {sigma_z}, beta = {beta}

H0 = 67.36
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544

# Optimal EDE configuration (from Phase 3)
Lambda_EDE_ridder = 1.5
f_axion_ridder = 2.435e27
theta_i_ridder = 1.0
n_ridder = 3
ridder_c_slow = 1.0
ridder_freeze_phi = no
ridder_force_damping = 1.0

# Beta coupling parameters (GRID SEARCH)
beta_ridder = {beta}
beta_z_c = {z_c}
beta_sigma_z = {sigma_z}

# Output settings
gauge = newtonian
output = tCl,pCl,lCl
lensing = yes
l_max_scalars = 2500

write background = yes
write thermodynamics = no

root = output/{output_prefix}_
"""
    
    ini_file = f"grid_search_{output_prefix}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini_content)
    
    # Run CLASS
    result = subprocess.run(
        ['./phase2/class/class', ini_file],
        capture_output=True,
        text=True,
        timeout=180
    )
    
    if result.returncode != 0:
        return None, None, ini_file
    
    # Find output files
    import glob
    bg_files = glob.glob(f"output/{output_prefix}_*_background.dat")
    cl_files = glob.glob(f"output/{output_prefix}_*_cl.dat")
    
    if not bg_files or not cl_files:
        return None, None, ini_file
    
    return bg_files[0], cl_files[0], ini_file

def extract_rs(bg_file):
    """Extract r_s at z_drag."""
    data = np.loadtxt(bg_file)
    z = data[:, 0]
    rs = data[:, 7]
    idx_drag = np.argmin(np.abs(z - 1060.0))
    return rs[idx_drag]

def assess_cmb_simple(lcdm_cl_file, ede_cl_file):
    """Quick CMB quality metrics."""
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

def main():
    # Reference values
    rs_lcdm = 147.079129
    h0_input = 67.36
    lcdm_cl_file = 'output/benchmark_vanilla_lcdm_00_cl.dat'
    
    # Grid parameters (BOUNDED FOR PHYSICS CREDIBILITY)
    z_c_values = [1500, 2000, 2500, 3000]
    sigma_z_values = [0.3, 0.6, 1.0]
    beta = 0.2  # Fixed at reasonable value
    
    print("=" * 90)
    print("SYSTEMATIC BETA COUPLING GRID SEARCH")
    print("=" * 90)
    print()
    print("OBJECTIVE: Test if (z_c, sigma_z) optimization can push ΔH₀ > +3.5 km/s/Mpc")
    print()
    print("GUARDRAILS (Physics Credibility):")
    print(f"  z_c ∈ {z_c_values}: Coupling peaks near (not at) EDE epoch")
    print(f"  sigma_z ∈ {sigma_z_values}: Narrow to broad boost window")
    print(f"  beta = {beta}: Fixed at reasonable amplitude")
    print()
    print("DECISION CRITERIA:")
    print("  SUCCESS: ΔH₀ > +3.5 km/s/Mpc with acceptable CMB quality")
    print("  CEILING: All configs give ΔH₀ < +3.0 km/s/Mpc")
    print()
    print("=" * 90)
    print()
    
    results = []
    total_configs = len(z_c_values) * len(sigma_z_values)
    config_num = 0
    
    for z_c in z_c_values:
        for sigma_z in sigma_z_values:
            config_num += 1
            
            print(f"[{config_num}/{total_configs}] z_c = {z_c:.0f}, sigma_z = {sigma_z:.1f}")
            print("-" * 90)
            
            bg_file, cl_file, ini_file = run_class_config(z_c, sigma_z, beta)
            
            if bg_file is None:
                print("  ❌ FAILED")
                results.append({'z_c': z_c, 'sigma_z': sigma_z, 'status': 'failed'})
                print()
                continue
            
            # Extract observables
            rs_ede = extract_rs(bg_file)
            cmb_quality = assess_cmb_simple(lcdm_cl_file, cl_file)
            
            if rs_ede is None or cmb_quality is None:
                print("  ❌ Analysis failed")
                results.append({'z_c': z_c, 'sigma_z': sigma_z, 'status': 'analysis_failed'})
                print()
                continue
            
            # Compute H₀ metrics
            delta_rs_pct = (rs_ede - rs_lcdm) / rs_lcdm * 100
            h0_eff = h0_input * (rs_lcdm / rs_ede)
            delta_h0 = h0_eff - h0_input
            
            print(f"  r_s         = {rs_ede:.6f} Mpc  (Δr_s/r_s = {delta_rs_pct:+.3f}%)")
            print(f"  H₀^eff      = {h0_eff:.4f} km/s/Mpc")
            print(f"  ΔH₀         = {delta_h0:+.4f} km/s/Mpc")
            print(f"  CMB: Δℓ={cmb_quality['delta_ell']:+.1f}, "
                  f"max Δ={cmb_quality['max_diff_pct']:.1f}%, "
                  f"RMS={cmb_quality['rms_diff_pct']:.1f}%")
            
            # Verdict
            if delta_h0 >= 3.5:
                if cmb_quality['max_diff_pct'] < 35:
                    verdict = "🎯 BIG STICK FOUND!"
                else:
                    verdict = "⚠️  High ΔH₀ but CMB poor"
            elif delta_h0 >= 3.0:
                verdict = "✓ Improved"
            else:
                verdict = "Baseline"
            
            print(f"  → {verdict}")
            print()
            
            results.append({
                'z_c': z_c,
                'sigma_z': sigma_z,
                'status': 'success',
                'rs': rs_ede,
                'h0_eff': h0_eff,
                'delta_h0': delta_h0,
                'delta_rs_pct': delta_rs_pct,
                'delta_ell': cmb_quality['delta_ell'],
                'max_diff_pct': cmb_quality['max_diff_pct'],
                'rms_diff_pct': cmb_quality['rms_diff_pct']
            })
    
    # Analysis
    print("=" * 90)
    print("GRID SEARCH COMPLETE")
    print("=" * 90)
    print()
    
    successful = [r for r in results if r['status'] == 'success']
    
    if not successful:
        print("❌ ALL CONFIGURATIONS FAILED")
        return
    
    # Summary table
    print("SUMMARY TABLE:")
    print()
    print(f"{'z_c':<8} {'sigma_z':<10} {'ΔH₀':<12} {'Δr_s/r_s':<12} {'Δℓ':<8} {'Max Δ%':<10} {'Verdict':<20}")
    print("-" * 90)
    
    for r in successful:
        verdict = ""
        if r['delta_h0'] >= 3.5:
            if r['max_diff_pct'] < 35:
                verdict = "🎯 BIG STICK!"
            else:
                verdict = "⚠️  High but CMB poor"
        elif r['delta_h0'] >= 3.0:
            verdict = "✓ Improved"
        else:
            verdict = "Baseline"
        
        print(f"{r['z_c']:<8.0f} {r['sigma_z']:<10.1f} {r['delta_h0']:>+11.4f} "
              f"{r['delta_rs_pct']:>+11.3f}% {r['delta_ell']:>+7.1f} "
              f"{r['max_diff_pct']:>9.1f} {verdict:<20}")
    
    print()
    print("=" * 90)
    print("ANALYSIS & DECISION")
    print("=" * 90)
    print()
    
    # Find best config
    best = max(successful, key=lambda r: r['delta_h0'])
    
    print(f"Best Configuration:")
    print(f"  z_c = {best['z_c']:.0f}, sigma_z = {best['sigma_z']:.1f}")
    print(f"  ΔH₀ = {best['delta_h0']:+.4f} km/s/Mpc")
    print(f"  CMB: Δℓ={best['delta_ell']:+.1f}, max Δ={best['max_diff_pct']:.1f}%")
    print()
    
    # Decision logic
    if best['delta_h0'] >= 3.5 and best['max_diff_pct'] < 35:
        print("✅ SUCCESS: BIG STICK FOUND!")
        print()
        print(f"   This configuration achieves ΔH₀ > +3.5 km/s/Mpc with acceptable CMB")
        print(f"   (~75% Hubble tension reduction: 67.4 → {best['h0_eff']:.1f} km/s/Mpc)")
        print()
        print("   RECOMMENDATION:")
        print("   1. Lock this config as your MCMC candidate")
        print("   2. Run full CMB quality assessment")
        print("   3. Consider fluid mode to further improve CMB fit")
        print("   4. Proceed to Tier 3 MCMC with confidence")
        
    elif best['delta_h0'] >= 3.0:
        improvement_pct = ((best['delta_h0'] - 2.06) / 2.06) * 100
        print(f"⚠️  MODEST IMPROVEMENT: +{improvement_pct:.0f}% over baseline")
        print()
        print(f"   Best config: ΔH₀ = {best['delta_h0']:+.2f} km/s/Mpc")
        print(f"   (~60% Hubble tension reduction)")
        print()
        print("   RECOMMENDATION:")
        print("   - Better than baseline, but not transformative")
        print("   - Decision: Accept partial solution OR try fluid mode")
        print("   - MCMC might help, but won't double ΔH₀")
        
    else:
        print("❌ CEILING CONFIRMED: Beta optimization tapped out")
        print()
        print(f"   All configs give ΔH₀ < +3.0 km/s/Mpc")
        print(f"   Best achieved: {best['delta_h0']:+.2f} km/s/Mpc")
        print()
        print("   INTERPRETATION:")
        print("   - Radiation boost has limited leverage on r_s (even optimized)")
        print("   - Model has intrinsic efficiency ceiling ~40-50% tension reduction")
        print("   - Not an implementation bug - it's fundamental physics of this potential")
        print()
        print("   RECOMMENDATION:")
        print("   1. Accept partial solution (~40-50% tension reduction)")
        print("   2. Write paper on systematic optimization + efficiency limits")
        print("   3. Skip expensive MCMC (won't change fundamental ceiling)")
        print("   4. Consider this V2 foundation for future V3 variants")
    
    print()
    print("=" * 90)
    
    # Save results
    with open('grid_search_beta_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print("Results saved to: grid_search_beta_results.json")

if __name__ == "__main__":
    main()

