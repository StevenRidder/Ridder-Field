#!/usr/bin/env python3
"""
CMB Spectrum Quality Assessment for EDE Configurations.

Pass/Maybe/Fail criteria:
- Peak location shift: Pass if |Δℓ₁| ≤ 3, Maybe if ≤ 5, Fail if > 5
- Max fractional diff: Pass if ≤ 20%, Maybe if ≤ 30%, Fail if > 30%
- RMS fractional diff: Pass if ≤ 10%, Maybe if ≤ 15%, Fail if > 15%
- High-ℓ behavior: Pass if smooth and ≤ 20% change
"""

import numpy as np
import matplotlib.pyplot as plt
import glob
import os

def load_cl_file(cl_file):
    """Load CLASS C_ℓ file and return ℓ, D_ℓ^TT."""
    data = np.loadtxt(cl_file)
    ell = data[:, 0]
    Cl_TT = data[:, 1]  # Already in ℓ(ℓ+1)C_ℓ/(2π) units
    return ell, Cl_TT

def find_first_peak(ell, D_ell, ell_min=50, ell_max=400):
    """Find first acoustic peak location."""
    mask = (ell >= ell_min) & (ell <= ell_max)
    idx_peak = np.argmax(D_ell[mask])
    ell_peak = ell[mask][idx_peak]
    D_peak = D_ell[mask][idx_peak]
    return ell_peak, D_peak

def compute_fractional_diff(ell, D_ede, D_lcdm):
    """Compute fractional difference: (EDE - ΛCDM) / ΛCDM."""
    # Interpolate EDE onto ΛCDM grid
    D_ede_interp = np.interp(ell, ell, D_ede)
    delta_frac = (D_ede_interp - D_lcdm) / D_lcdm
    return delta_frac

def assess_quality(model_name, ell_lcdm, D_lcdm, ell_ede, D_ede):
    """Assess CMB quality with pass/maybe/fail criteria."""
    
    # 1. Peak location
    ell_peak_lcdm, D_peak_lcdm = find_first_peak(ell_lcdm, D_lcdm)
    ell_peak_ede, D_peak_ede = find_first_peak(ell_ede, D_ede)
    delta_ell = ell_peak_ede - ell_peak_lcdm
    
    if abs(delta_ell) <= 3:
        peak_status = "PASS"
    elif abs(delta_ell) <= 5:
        peak_status = "MAYBE"
    else:
        peak_status = "FAIL"
    
    # 2. Fractional differences
    delta_frac = compute_fractional_diff(ell_lcdm, D_ede, D_lcdm)
    
    # Compute statistics over different ranges
    mask_full = (ell_lcdm >= 30) & (ell_lcdm <= 2000)
    mask_low = (ell_lcdm >= 30) & (ell_lcdm <= 800)
    mask_high = (ell_lcdm >= 1000) & (ell_lcdm <= 2000)
    
    max_abs_diff = np.max(np.abs(delta_frac[mask_full])) * 100
    rms_diff = np.sqrt(np.mean(delta_frac[mask_full]**2)) * 100
    mean_high_ell = np.mean(np.abs(delta_frac[mask_high])) * 100
    
    if max_abs_diff <= 20:
        max_status = "PASS"
    elif max_abs_diff <= 30:
        max_status = "MAYBE"
    else:
        max_status = "FAIL"
    
    if rms_diff <= 10:
        rms_status = "PASS"
    elif rms_diff <= 15:
        rms_status = "MAYBE"
    else:
        rms_status = "FAIL"
    
    if mean_high_ell <= 20:
        high_ell_status = "PASS"
    else:
        high_ell_status = "MAYBE"
    
    # Overall assessment
    statuses = [peak_status, max_status, rms_status, high_ell_status]
    if all(s == "PASS" for s in statuses):
        overall = "✅ PASS"
    elif any(s == "FAIL" for s in statuses):
        overall = "❌ FAIL"
    else:
        overall = "⚠️  MAYBE"
    
    results = {
        'model': model_name,
        'ell_peak_lcdm': ell_peak_lcdm,
        'ell_peak_ede': ell_peak_ede,
        'delta_ell': delta_ell,
        'peak_status': peak_status,
        'max_abs_diff': max_abs_diff,
        'max_status': max_status,
        'rms_diff': rms_diff,
        'rms_status': rms_status,
        'mean_high_ell': mean_high_ell,
        'high_ell_status': high_ell_status,
        'overall': overall,
        'delta_frac': delta_frac
    }
    
    return results

def plot_comparison(ell_lcdm, D_lcdm, models, results_list, output_file):
    """Create TT comparison plots."""
    fig = plt.figure(figsize=(14, 10))
    
    # Top panel: TT spectra overlay
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(ell_lcdm, D_lcdm * 1e10, 'k-', linewidth=2.5, label='Vanilla ΛCDM', zorder=10)
    
    colors = ['#1f77b4', '#ff7f0e', '#d62728']  # Blue, orange, red
    for i, (model, res) in enumerate(zip(models, results_list)):
        ell_ede, D_ede = model['ell'], model['D_ell']
        label = f"{model['label']} (ΔH₀={model['delta_h0']:.1f})"
        ax1.plot(ell_ede, D_ede * 1e10, color=colors[i], linewidth=2, 
                label=label, alpha=0.8)
    
    ax1.set_ylabel('$\\ell(\\ell+1)C_\\ell^{TT}/(2\\pi)$ [×10⁻¹⁰]', fontsize=12)
    ax1.set_xlim(2, 2500)
    ax1.legend(fontsize=10, loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_title('CMB Temperature Power Spectrum: EDE vs. ΛCDM', 
                 fontsize=14, fontweight='bold')
    
    # Bottom panel: Fractional differences
    ax2 = plt.subplot(2, 1, 2)
    
    for i, res in enumerate(results_list):
        ell = ell_lcdm
        delta = res['delta_frac'] * 100
        label = f"{res['model']} ({res['overall']})"
        ax2.plot(ell, delta, color=colors[i], linewidth=2, label=label, alpha=0.8)
    
    ax2.axhline(0, color='k', linestyle='--', alpha=0.5, linewidth=1)
    ax2.axhline(20, color='gray', linestyle=':', alpha=0.5, label='±20% threshold')
    ax2.axhline(-20, color='gray', linestyle=':', alpha=0.5)
    
    ax2.set_xlabel('Multipole $\\ell$', fontsize=12)
    ax2.set_ylabel('$\\Delta C_\\ell / C_\\ell$ [%]', fontsize=12)
    ax2.set_xlim(30, 2500)
    ax2.set_ylim(-40, 40)
    ax2.legend(fontsize=10, loc='best')
    ax2.grid(True, alpha=0.3)
    
    # Mark key regions
    ax2.axvspan(50, 400, alpha=0.05, color='blue', label='First peak region')
    ax2.axvspan(1000, 2500, alpha=0.05, color='red', label='Damping tail')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def main():
    print("=" * 90)
    print("CMB SPECTRUM QUALITY ASSESSMENT")
    print("=" * 90)
    print()
    
    # Reference ΛCDM
    lcdm_cl_file = 'output/benchmark_vanilla_lcdm_00_cl.dat'
    
    if not os.path.exists(lcdm_cl_file):
        print(f"ERROR: ΛCDM reference file not found: {lcdm_cl_file}")
        return
    
    ell_lcdm, D_lcdm = load_cl_file(lcdm_cl_file)
    print(f"Loaded ΛCDM reference: {len(ell_lcdm)} multipoles")
    print()
    
    # EDE configurations to test
    configs = [
        {
            'label': 'Option A: θ=1.0',
            'pattern': 'output/lambda1p50_theta1p00_*_cl.dat',
            'delta_h0': 2.06,
            'f_peak': 13.7,
            'z_peak': 3276
        },
        {
            'label': 'Option B: θ=1.25',
            'pattern': 'output/lambda1p50_theta1p25_*_cl.dat',
            'delta_h0': 3.28,
            'f_peak': 22.4,
            'z_peak': 3871
        },
        {
            'label': 'Option C: θ=1.5',
            'pattern': 'output/lambda1p50_theta1p50_*_cl.dat',
            'delta_h0': 5.08,
            'f_peak': 33.4,
            'z_peak': 4275
        }
    ]
    
    models = []
    results_list = []
    
    for config in configs:
        cl_files = glob.glob(config['pattern'])
        
        if not cl_files:
            print(f"⚠️  {config['label']}: No output found")
            continue
        
        cl_file = cl_files[0]
        ell_ede, D_ede = load_cl_file(cl_file)
        
        print(f"{'='*90}")
        print(f"{config['label']}")
        print(f"{'='*90}")
        print(f"File: {os.path.basename(cl_file)}")
        print(f"z_peak = {config['z_peak']:.0f}, f_peak = {config['f_peak']:.1f}%, "
              f"ΔH₀ = {config['delta_h0']:+.2f} km/s/Mpc")
        print()
        
        # Assess quality
        results = assess_quality(config['label'], ell_lcdm, D_lcdm, ell_ede, D_ede)
        
        print(f"Peak Location:")
        print(f"  ΛCDM: ℓ = {results['ell_peak_lcdm']:.0f}")
        print(f"  EDE:  ℓ = {results['ell_peak_ede']:.0f}")
        print(f"  Δℓ = {results['delta_ell']:+.1f}  [{results['peak_status']}]")
        print()
        
        print(f"Fractional Differences (30 ≤ ℓ ≤ 2000):")
        print(f"  Max |ΔC_ℓ/C_ℓ|: {results['max_abs_diff']:.2f}%  [{results['max_status']}]")
        print(f"  RMS ΔC_ℓ/C_ℓ:   {results['rms_diff']:.2f}%  [{results['rms_status']}]")
        print()
        
        print(f"High-ℓ Behavior (1000 ≤ ℓ ≤ 2000):")
        print(f"  Mean |ΔC_ℓ/C_ℓ|: {results['mean_high_ell']:.2f}%  [{results['high_ell_status']}]")
        print()
        
        print(f"Overall Assessment: {results['overall']}")
        print()
        
        models.append({
            'label': config['label'],
            'ell': ell_ede,
            'D_ell': D_ede,
            'delta_h0': config['delta_h0']
        })
        results_list.append(results)
    
    # Create plots
    os.makedirs('plots', exist_ok=True)
    plot_comparison(ell_lcdm, D_lcdm, models, results_list, 
                   'plots/cmb_quality_assessment.png')
    
    # Summary table
    print("=" * 90)
    print("SUMMARY TABLE")
    print("=" * 90)
    print()
    print(f"{'Config':<15} {'ΔH₀':<10} {'Δℓ₁':<8} {'Max Δ%':<10} {'RMS Δ%':<10} {'Status':<15}")
    print("-" * 90)
    
    for res in results_list:
        print(f"{res['model']:<15} "
              f"{'+' if res['model'].split()[-1] == 'θ=1.0' else ''}"
              f"{configs[[c['label'] for c in configs].index(res['model'])]['delta_h0']:<9.2f} "
              f"{res['delta_ell']:>+7.1f} "
              f"{res['max_abs_diff']:<10.2f} "
              f"{res['rms_diff']:<10.2f} "
              f"{res['overall']:<15}")
    
    print()
    print("=" * 90)
    
    # Recommendations
    print("RECOMMENDATIONS:")
    print("-" * 90)
    print()
    
    pass_count = sum(1 for r in results_list if "PASS" in r['overall'])
    maybe_count = sum(1 for r in results_list if "MAYBE" in r['overall'])
    fail_count = sum(1 for r in results_list if "FAIL" in r['overall'])
    
    if pass_count > 0:
        pass_configs = [r for r in results_list if "PASS" in r['overall']]
        best = max(pass_configs, key=lambda r: configs[[c['label'] for c in configs].index(r['model'])]['delta_h0'])
        print(f"✅ {pass_count} configuration(s) passed all criteria!")
        print(f"   Best: {best['model']} with ΔH₀ = "
              f"{configs[[c['label'] for c in configs].index(best['model'])]['delta_h0']:+.2f} km/s/Mpc")
        print()
    
    if maybe_count > 0:
        print(f"⚠️  {maybe_count} configuration(s) in 'maybe' category - worth deeper investigation")
        print()
    
    if fail_count > 0:
        fail_configs = [r for r in results_list if "FAIL" in r['overall']]
        print(f"❌ {fail_count} configuration(s) failed quality criteria:")
        for r in fail_configs:
            reasons = []
            if r['peak_status'] == "FAIL":
                reasons.append(f"peak shift Δℓ={r['delta_ell']:+.1f}")
            if r['max_status'] == "FAIL":
                reasons.append(f"max diff {r['max_abs_diff']:.1f}%")
            if r['rms_status'] == "FAIL":
                reasons.append(f"RMS diff {r['rms_diff']:.1f}%")
            print(f"   {r['model']}: {', '.join(reasons)}")
        print()
    
    print("Next steps:")
    print("  1. Examine plots/cmb_quality_assessment.png for visual inspection")
    print("  2. For PASS configs: proceed with full observable extraction (σ₈, θ_s, etc.)")
    print("  3. For MAYBE configs: check TE/EE spectra and consider data fits")
    print("  4. For FAIL configs: consider intermediate theta_i values or different Lambda")
    print()
    print("=" * 90)

if __name__ == "__main__":
    main()

