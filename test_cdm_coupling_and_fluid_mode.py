#!/usr/bin/env python3
"""
Engineering Checklist Continuation:
1. Test CDM coupling (proper physics for gravity/structure)
2. Implement & test fluid perturbation mode
3. Systematic comparison

Goal: Complete the checklist and find the optimal configuration
"""

import subprocess
import numpy as np
import os
import json

def run_class_test(config_name, params):
    """Run CLASS with specific configuration."""
    
    ini_content = f"""# {config_name}
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

# Configuration parameters
beta_ridder = {params['beta']}
beta_z_c = {params['z_c']}
beta_sigma_z = {params['sigma_z']}
ridder_perturbation_mode = {params.get('pert_mode', 0)}

# Output
gauge = newtonian
output = tCl,pCl,lCl
lensing = yes
l_max_scalars = 2500

write background = yes
root = output/{config_name}_
"""
    
    ini_file = f"{config_name}.ini"
    with open(ini_file, 'w') as f:
        f.write(ini_content)
    
    result = subprocess.run(
        ['./phase2/class/class', ini_file],
        capture_output=True,
        text=True,
        timeout=180
    )
    
    if result.returncode != 0:
        print(f"  ❌ Failed: {result.stderr[:150]}")
        return None
    
    import glob
    bg_files = glob.glob(f"output/{config_name}_*_background.dat")
    cl_files = glob.glob(f"output/{config_name}_*_cl.dat")
    
    if not bg_files or not cl_files:
        return None
    
    return {'bg': bg_files[0], 'cl': cl_files[0]}

def extract_observables(bg_file, cl_file, lcdm_cl_file):
    """Extract H0, CMB quality, etc."""
    # r_s
    data = np.loadtxt(bg_file)
    z = data[:, 0]
    rs = data[:, 7]
    idx_drag = np.argmin(np.abs(z - 1060.0))
    rs_drag = rs[idx_drag]
    
    # H0
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
    
    D_ede_interp = np.interp(ell_lcdm, ell_ede, D_ede)
    delta_frac = (D_ede_interp - D_lcdm) / D_lcdm
    
    mask = (ell_lcdm >= 30) & (ell_lcdm <= 2000)
    max_diff_pct = np.max(np.abs(delta_frac[mask])) * 100
    rms_diff_pct = np.sqrt(np.mean(delta_frac[mask]**2)) * 100
    
    return {
        'rs': rs_drag,
        'h0_eff': h0_eff,
        'delta_h0': delta_h0,
        'max_cmb_diff': max_diff_pct,
        'rms_cmb_diff': rms_diff_pct
    }

def main():
    print("=" * 90)
    print("ENGINEERING CHECKLIST: CDM COUPLING + FLUID MODE")
    print("=" * 90)
    print()
    print("Goal: Complete systematic optimization")
    print("Step 1: Test CDM coupling (affects gravity & structure)")
    print("Step 2: Compare scalar vs fluid perturbation modes")
    print("=" * 90)
    print()
    
    lcdm_cl_file = 'output/benchmark_vanilla_lcdm_00_cl.dat'
    
    # Test configurations
    configs = [
        {
            'name': 'baseline_no_beta',
            'desc': 'Baseline (no coupling)',
            'params': {'beta': 0.0, 'z_c': 3000, 'sigma_z': 0.3, 'pert_mode': 0}
        },
        {
            'name': 'cdm_coupling_beta02',
            'desc': 'CDM coupling β=0.2 (scalar)',
            'params': {'beta': 0.2, 'z_c': 3000, 'sigma_z': 0.3, 'pert_mode': 0}
        },
        {
            'name': 'cdm_coupling_beta05',
            'desc': 'CDM coupling β=0.5 (scalar)',
            'params': {'beta': 0.5, 'z_c': 3000, 'sigma_z': 0.3, 'pert_mode': 0}
        },
        {
            'name': 'cdm_coupling_wide',
            'desc': 'CDM coupling β=0.2, wide (scalar)',
            'params': {'beta': 0.2, 'z_c': 3000, 'sigma_z': 1.0, 'pert_mode': 0}
        },
        {
            'name': 'fluid_mode_baseline',
            'desc': 'Baseline (fluid mode)',
            'params': {'beta': 0.0, 'z_c': 3000, 'sigma_z': 0.3, 'pert_mode': 1}
        },
        {
            'name': 'fluid_mode_beta02',
            'desc': 'CDM coupling β=0.2 (fluid)',
            'params': {'beta': 0.2, 'z_c': 3000, 'sigma_z': 0.3, 'pert_mode': 1}
        },
    ]
    
    results = []
    
    for i, config in enumerate(configs, 1):
        print(f"[{i}/{len(configs)}] {config['desc']}")
        print("-" * 90)
        
        files = run_class_test(config['name'], config['params'])
        
        if files is None:
            results.append({'config': config['name'], 'status': 'failed'})
            print()
            continue
        
        obs = extract_observables(files['bg'], files['cl'], lcdm_cl_file)
        
        print(f"  ΔH₀         = {obs['delta_h0']:+.4f} km/s/Mpc")
        print(f"  Max CMB Δ   = {obs['max_cmb_diff']:.1f}%")
        print(f"  RMS CMB Δ   = {obs['rms_cmb_diff']:.1f}%")
        print()
        
        results.append({
            'config': config['name'],
            'desc': config['desc'],
            'params': config['params'],
            'status': 'success',
            **obs
        })
    
    # Analysis
    print("=" * 90)
    print("ANALYSIS")
    print("=" * 90)
    print()
    
    successful = [r for r in results if r['status'] == 'success']
    
    if not successful:
        print("❌ All tests failed")
        return
    
    # Summary table
    print("SUMMARY TABLE:")
    print()
    print(f"{'Config':<30} {'ΔH₀':<12} {'Max CMB Δ':<12} {'RMS CMB Δ':<12}")
    print("-" * 90)
    
    for r in successful:
        print(f"{r['desc']:<30} {r['delta_h0']:>+11.4f} {r['max_cmb_diff']:>11.1f}% {r['rms_cmb_diff']:>11.1f}%")
    
    print()
    print("=" * 90)
    print("KEY FINDINGS:")
    print("=" * 90)
    print()
    
    # Compare CDM coupling effect
    baseline = next((r for r in successful if 'baseline_no_beta' in r['config']), None)
    if baseline:
        print("1. CDM Coupling Effect (Scalar Mode):")
        print()
        
        for r in successful:
            if 'cdm_coupling' in r['config'] and r['params']['pert_mode'] == 0:
                delta = r['delta_h0'] - baseline['delta_h0']
                print(f"   {r['desc']}:")
                print(f"     ΔH₀ boost: {delta:+.4f} km/s/Mpc")
                print(f"     CMB impact: {r['max_cmb_diff']:.1f}% (baseline: {baseline['max_cmb_diff']:.1f}%)")
                print()
    
    # Compare fluid vs scalar
    print("2. Fluid vs Scalar Perturbation Mode:")
    print()
    
    scalar_baseline = next((r for r in successful if 'baseline_no_beta' in r['config']), None)
    fluid_baseline = next((r for r in successful if 'fluid_mode_baseline' in r['config']), None)
    
    if scalar_baseline and fluid_baseline:
        print(f"   Baseline (scalar): ΔH₀={scalar_baseline['delta_h0']:+.4f}, CMB={scalar_baseline['max_cmb_diff']:.1f}%")
        print(f"   Baseline (fluid):  ΔH₀={fluid_baseline['delta_h0']:+.4f}, CMB={fluid_baseline['max_cmb_diff']:.1f}%")
        
        h0_change = fluid_baseline['delta_h0'] - scalar_baseline['delta_h0']
        cmb_change = fluid_baseline['max_cmb_diff'] - scalar_baseline['max_cmb_diff']
        
        print()
        print(f"   Fluid mode effect: ΔH₀ {h0_change:+.4f}, CMB {cmb_change:+.1f}%")
        
        if abs(h0_change) < 0.1 and cmb_change < -5:
            print("   ✅ Fluid mode: Same H₀, cleaner CMB!")
        elif abs(h0_change) < 0.1:
            print("   ⚠️  Fluid mode: No significant change")
        else:
            print(f"   ⚠️  Fluid mode changes H₀ (unexpected)")
    
    print()
    print("=" * 90)
    print("RECOMMENDATION:")
    print("=" * 90)
    print()
    
    best = max(successful, key=lambda r: r['delta_h0'])
    
    print(f"Best configuration: {best['desc']}")
    print(f"  ΔH₀ = {best['delta_h0']:+.4f} km/s/Mpc")
    print(f"  CMB quality: {best['max_cmb_diff']:.1f}% max, {best['rms_cmb_diff']:.1f}% RMS")
    print()
    
    if best['delta_h0'] >= 3.0:
        print("✅ BREAKTHROUGH: ΔH₀ > +3.0 km/s/Mpc achieved!")
        print("   This is competitive with our target. Proceed to full MCMC.")
    elif best['delta_h0'] >= 2.5:
        print("✓ PROGRESS: ΔH₀ ~ +2.5-3.0 km/s/Mpc")
        print("  Meaningful improvement. Consider MCMC or accept partial solution.")
    else:
        print("⚠️  LIMITED: ΔH₀ < +2.5 km/s/Mpc")
        print("   Model approaching efficiency ceiling with current potential.")
    
    # Save results
    with open('cdm_coupling_fluid_mode_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print("Results saved to: cdm_coupling_fluid_mode_results.json")
    print("=" * 90)

if __name__ == "__main__":
    main()

