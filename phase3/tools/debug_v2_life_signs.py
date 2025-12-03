#!/usr/bin/env python3
"""
V2 Life Signs Check

Diagnosis: Check if the Ridder field has any energy density.
If rho_scf = 0, the field is dead (stuck at phi=0).
If rho_scf > 0, the field is alive but parameters may be wrong.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for SSH
import matplotlib.pyplot as plt
import numpy as np
from classy import Class

# Parameters
f = 0.4  # Planck masses (reduced)
theta = 2.0
phi_ini = f * theta  # <--- MANUALLY CALCULATING IT HERE

print("="*70)
print("🏥 V2 LIFE SIGNS CHECK")
print("="*70)
print(f"Forcing phi_ini = {phi_ini:.3f} (theta={theta}, f={f})")
print("")

params = {
    'output': 'tCl, mPk',
    'H0': 70.0,
    'omega_b': 0.0224,
    'omega_cdm': 0.120,
    'A_s': 2.1e-9,
    'n_s': 0.965,
    'tau_reio': 0.054,
    
    # V2 Setup - Try to force it on
    'Lambda_EDE_ridder': 2.0,  # Energy scale
    'theta_i_ridder': theta,
    'beta_ridder': 0.015,
    'f_axion_ridder': 1.0,  # eV
    'n_ridder': 3,
    'gauge': 'newtonian',
}

print("Parameters:")
for k, v in params.items():
    if 'ridder' in k.lower() or k in ['Lambda_EDE_ridder', 'theta_i_ridder', 'beta_ridder']:
        print(f"  {k}: {v}")
print("")

cosmo = Class()
cosmo.set(params)

try:
    print("Computing CLASS...")
    cosmo.compute()
    print("✓ CLASS computed successfully")
    print("")
    
    # Get Background
    bg = cosmo.get_background()
    z = bg['z']
    
    # Try to get Ridder field density
    # CLASS may store it as different names
    possible_names = [
        '(.)rho_scf',
        '(.)rho_ridder', 
        '(.)rho_fld',
        'rho_scf',
        'rho_ridder'
    ]
    
    rho_scf = None
    for name in possible_names:
        if name in bg:
            rho_scf = bg[name]
            print(f"✓ Found field density as '{name}'")
            break
    
    if rho_scf is None:
        print("❌ CRITICAL: Cannot find Ridder field density in background!")
        print("Available columns:")
        for key in sorted(bg.keys()):
            print(f"  - {key}")
        print("")
        print("This means the field is not being tracked at all.")
        cosmo.struct_cleanup()
        cosmo.empty()
        exit(1)
    
    rho_tot = bg['(.)rho_tot']
    rho_cdm = bg['(.)rho_cdm']
    rho_b = bg['(.)rho_b']
    
    # Check for Pulse
    peak_rho = np.max(rho_scf)
    peak_z = z[np.argmax(rho_scf)]
    
    # Compute f_EDE at peak
    rho_tot_at_peak = rho_tot[np.argmax(rho_scf)]
    f_EDE_peak = peak_rho / rho_tot_at_peak if rho_tot_at_peak > 0 else 0
    
    print("="*70)
    print("DIAGNOSIS")
    print("="*70)
    print(f"Peak rho_scf:     {peak_rho:.4e}")
    print(f"Peak at redshift: z = {peak_z:.1f}")
    print(f"f_EDE at peak:    {f_EDE_peak*100:.2f}%")
    print("")
    
    if peak_rho < 1e-30:
        print("❌ FLATLINE: The field has NO energy.")
        print("   Diagnosis: Field is stuck at phi=0")
        print("   Cause: Initial conditions not being set")
        status = "DEAD"
    elif f_EDE_peak < 0.01:
        print("⚠️  WEAK PULSE: The field exists but is too weak.")
        print(f"   f_EDE = {f_EDE_peak*100:.4f}% (need ~10%)")
        print("   Diagnosis: Lambda_EDE too small or field decays too fast")
        status = "WEAK"
    else:
        print("✅ PULSE DETECTED: The field is alive!")
        print(f"   f_EDE = {f_EDE_peak*100:.2f}%")
        status = "ALIVE"
    
    print("="*70)
    
    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Energy densities
    ax = axes[0]
    ax.loglog(z, rho_scf, 'r-', linewidth=2, label='Ridder V2 Density')
    ax.loglog(z, rho_tot, 'k--', linewidth=1, label='Total Density')
    ax.loglog(z, rho_cdm, 'b:', linewidth=1, label='CDM Density')
    ax.set_xlim(1e5, 0.1)
    ax.set_xlabel('Redshift z', fontsize=12)
    ax.set_ylabel('Energy Density', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_title(f'V2 Life Signs: {status} (Peak rho={peak_rho:.2e} at z={peak_z:.0f})', fontsize=14, fontweight='bold')
    
    # Plot 2: f_EDE evolution
    ax = axes[1]
    f_EDE = rho_scf / rho_tot
    ax.semilogx(z, f_EDE * 100, 'r-', linewidth=2)
    ax.axhline(10, color='g', linestyle='--', label='Target: 10%')
    ax.set_xlim(1e5, 0.1)
    ax.set_ylim(0, max(15, f_EDE_peak*100*1.2))
    ax.set_xlabel('Redshift z', fontsize=12)
    ax.set_ylabel('f_EDE (%)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_title(f'Early Dark Energy Fraction (Peak: {f_EDE_peak*100:.2f}% at z={peak_z:.0f})', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('v2_life_signs.png', dpi=150)
    print("")
    print("✓ Graph saved to v2_life_signs.png")
    
    # Save data
    np.savetxt('v2_life_signs_data.txt', 
               np.column_stack([z, rho_scf, rho_tot, f_EDE]),
               header='z rho_scf rho_tot f_EDE')
    print("✓ Data saved to v2_life_signs_data.txt")
    
except Exception as e:
    print("")
    print("="*70)
    print("❌ CRASH DURING COMPUTATION")
    print("="*70)
    print(f"Error: {e}")
    print("")
    print("This means CLASS failed to run with these parameters.")
    import traceback
    traceback.print_exc()

finally:
    try:
        cosmo.struct_cleanup()
        cosmo.empty()
    except:
        pass

print("")
print("="*70)
print("LIFE SIGNS CHECK COMPLETE")
print("="*70)

