#!/usr/bin/env python3
"""
Extract sound horizon at drag (r_s) and compute effective H₀.

The key formula:
  H₀^eff ≈ H₀^input × (r_s^ΛCDM / r_s^EDE)

If EDE shrinks r_s by 5%, then H₀^eff increases by ~5%.
"""

import numpy as np
import sys
import os

def extract_rs_from_thermodynamics(thermo_file):
    """
    Extract r_s at baryon drag from CLASS thermodynamics output.
    
    CLASS thermodynamics file contains columns including:
    - z (redshift)
    - tau (conformal time)
    - rs (comoving sound horizon)
    
    We need r_s(z_drag), where z_drag is the baryon drag epoch.
    CLASS typically computes this and we can find it in the thermo file.
    """
    if not os.path.exists(thermo_file):
        return None, None
    
    # Load thermodynamics data
    data = np.loadtxt(thermo_file)
    
    # Columns in CLASS thermodynamics output:
    # 0: z
    # 1: conf. time [Mpc]
    # 2: H [1/Mpc]
    # 3: comov.snd.hrz. [Mpc]  <- This is r_s(z)
    # ...
    
    z = data[:, 0]
    rs = data[:, 3]  # Comoving sound horizon in Mpc
    
    # Find baryon drag epoch
    # Typically z_drag ~ 1060 (slightly before recombination at z_* ~ 1090)
    # We'll use the value near z ~ 1060, or we can look for where
    # visibility peaks (but that requires more columns)
    
    # For simplicity, extract r_s at z ~ 1060 (typical drag epoch)
    # Better: CLASS actually computes z_drag precisely, but we approximate
    
    # Find closest point to z_drag ~ 1060
    z_drag_approx = 1060.0
    idx_drag = np.argmin(np.abs(z - z_drag_approx))
    rs_drag = rs[idx_drag]
    z_drag_actual = z[idx_drag]
    
    return rs_drag, z_drag_actual

def extract_rs_from_background(bg_file):
    """
    Alternative: extract r_s from background file.
    Background file has column 7: comov.snd.hrz. [Mpc]
    """
    if not os.path.exists(bg_file):
        return None, None
    
    data = np.loadtxt(bg_file)
    
    # Column 0: z
    # Column 7: comov.snd.hrz. [Mpc]
    
    z = data[:, 0]
    rs = data[:, 7]
    
    # Extract at z ~ 1060 (drag epoch)
    z_drag_approx = 1060.0
    idx_drag = np.argmin(np.abs(z - z_drag_approx))
    rs_drag = rs[idx_drag]
    z_drag_actual = z[idx_drag]
    
    return rs_drag, z_drag_actual

def compute_effective_h0(h0_input, rs_lcdm, rs_ede):
    """
    Compute effective H₀ that EDE would prefer if we fixed θ_s.
    
    Formula: H₀^eff ≈ H₀^input × (r_s^ΛCDM / r_s^EDE)
    
    If EDE shrinks r_s (r_s^EDE < r_s^ΛCDM), then H₀^eff > H₀^input.
    """
    if rs_ede == 0 or rs_lcdm == 0:
        return None
    
    ratio = rs_lcdm / rs_ede
    h0_eff = h0_input * ratio
    
    return h0_eff

def main():
    # Configuration
    models = [
        {
            'name': 'Vanilla ΛCDM',
            'bg_file': 'output/benchmark_vanilla_lcdm_00_background.dat',
            'thermo_file': 'output/benchmark_vanilla_lcdm_00_thermodynamics.dat',
            'h0_input': 67.36,
            'is_reference': True
        },
        {
            'name': 'EDE (θ=0.75, Λ=0.50eV)',
            'bg_file': 'output/benchmark_ede_theta075_00_background.dat',
            'thermo_file': 'output/benchmark_ede_theta075_00_thermodynamics.dat',
            'h0_input': 67.36,
            'is_reference': False
        }
    ]
    
    print("=" * 80)
    print("EFFECTIVE H₀ ANALYSIS")
    print("=" * 80)
    print()
    
    results = []
    rs_reference = None
    
    for model in models:
        print(f"Processing: {model['name']}")
        print("-" * 80)
        
        # Try background file first (more reliable for r_s)
        rs_drag, z_drag = extract_rs_from_background(model['bg_file'])
        
        if rs_drag is None:
            # Fallback to thermodynamics file
            rs_drag, z_drag = extract_rs_from_thermodynamics(model['thermo_file'])
        
        if rs_drag is None:
            print(f"  ERROR: Could not extract r_s from {model['name']}")
            print()
            continue
        
        print(f"  r_s(z_drag) = {rs_drag:.6f} Mpc")
        print(f"  z_drag ≈ {z_drag:.1f}")
        print(f"  H₀^input = {model['h0_input']:.4f} km/s/Mpc")
        
        if model['is_reference']:
            rs_reference = rs_drag
            h0_eff = model['h0_input']  # By definition for reference
            delta_h0 = 0.0
            delta_rs = 0.0
            print(f"  [Reference model]")
        else:
            if rs_reference is None:
                print(f"  ERROR: No reference r_s available")
                h0_eff = None
                delta_h0 = None
                delta_rs = None
            else:
                h0_eff = compute_effective_h0(model['h0_input'], rs_reference, rs_drag)
                delta_h0 = h0_eff - model['h0_input']
                delta_rs = (rs_drag - rs_reference) / rs_reference * 100
                
                print(f"  Δr_s/r_s = {delta_rs:+.3f}%")
                print(f"  H₀^eff = {h0_eff:.4f} km/s/Mpc")
                print(f"  ΔH₀^eff = {delta_h0:+.4f} km/s/Mpc  ({delta_h0/model['h0_input']*100:+.2f}%)")
        
        print()
        
        results.append({
            'name': model['name'],
            'rs_drag': rs_drag,
            'z_drag': z_drag,
            'h0_input': model['h0_input'],
            'h0_eff': h0_eff,
            'delta_h0': delta_h0,
            'delta_rs_percent': delta_rs if not model['is_reference'] else 0.0
        })
    
    # Print summary table
    print("=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print()
    print(f"{'Model':<30} {'r_s [Mpc]':<12} {'H₀^input':<12} {'H₀^eff':<12} {'ΔH₀^eff [km/s/Mpc]':<20}")
    print("-" * 80)
    
    for res in results:
        if res['h0_eff'] is not None:
            delta_str = f"{res['delta_h0']:+.4f} ({res['delta_h0']/res['h0_input']*100:+.2f}%)"
        else:
            delta_str = "N/A"
        
        print(f"{res['name']:<30} {res['rs_drag']:>11.6f} {res['h0_input']:>11.4f} "
              f"{res['h0_eff']:>11.4f} {delta_str:<20}")
    
    print()
    print("=" * 80)
    
    # Interpretation
    if len(results) >= 2 and results[1]['delta_h0'] is not None:
        delta_h0_abs = abs(results[1]['delta_h0'])
        delta_rs_pct = abs(results[1]['delta_rs_percent'])
        
        print("INTERPRETATION:")
        print("-" * 80)
        print()
        
        if delta_h0_abs < 0.5:
            print("⚠️  **Negligible H₀ effect** (ΔH₀^eff < 0.5 km/s/Mpc)")
            print("   The EDE bump is not significantly affecting the sound horizon.")
            print("   This is consistent with z_peak ~ 691 (too late) and f_peak ~ 6.3% (too weak).")
            print()
            print("   To get H₀ shifts relevant for the tension (~5 km/s/Mpc):")
            print("   - Need to push z_peak earlier (increase Lambda)")
            print("   - Need to increase f_peak (adjust theta_i)")
        elif delta_h0_abs < 2.0:
            print("📊 **Small H₀ effect** (0.5 < ΔH₀^eff < 2.0 km/s/Mpc)")
            print("   The EDE field is starting to affect the expansion history.")
            print("   To reach tension-resolving levels (~5 km/s/Mpc), consider:")
            print("   - Slightly earlier peak (increase Lambda)")
            print("   - Higher amplitude (increase theta_i)")
        elif delta_h0_abs < 7.0:
            print("✅ **Moderate H₀ effect** (2 < ΔH₀^eff < 7 km/s/Mpc)")
            print("   This is in the range where EDE can help with the Hubble tension!")
            print("   The field is affecting pre-recombination expansion at a relevant level.")
        else:
            print("⚠️  **Large H₀ effect** (ΔH₀^eff > 7 km/s/Mpc)")
            print("   This is a very strong effect. Check:")
            print("   - CMB spectrum quality (peaks, damping tail)")
            print("   - BAO consistency")
            print("   - Late-time field decay (should be f_ridder(z=0) ~ 0)")
        
        print()
        print(f"   Δr_s/r_s = {delta_rs_pct:+.3f}%")
        print(f"   Current z_peak ~ 691, f_peak ~ 0.063")
        print()
        print("=" * 80)

if __name__ == "__main__":
    main()

