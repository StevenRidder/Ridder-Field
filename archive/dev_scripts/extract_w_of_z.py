#!/usr/bin/env python3
"""
Extract w(z) from CLASS background files.

For ΛCDM: w = -1 (cosmological constant)
For unified: w_ridder = p_ridder / rho_ridder

Creates plot comparing w(z) evolution.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent
OUTPUT_DIR = REPO_ROOT / "phase2" / "class" / "output"

print(f"\n{'='*70}")
print("EXTRACTING w(z) FROM BACKGROUND FILES")
print(f"{'='*70}\n")

# --------------------------------------------------------------------------
# Load background and compute w(z)
# --------------------------------------------------------------------------

def load_lcdm_background(prefix):
    """
    Load ΛCDM background.
    
    Columns:
    1:z, 4:H, 12:rho_lambda
    
    For ΛCDM: w = -1 (constant)
    """
    bg_file = OUTPUT_DIR / f"{prefix}00_background.dat"
    if not bg_file.exists():
        print(f"  ⚠️  File not found: {bg_file}")
        return None
    
    data = np.loadtxt(bg_file)
    z = data[:, 0]           # Column 1: redshift
    H = data[:, 3]           # Column 4: H(z)
    rho_lambda = data[:, 11] # Column 12: rho_lambda (0-indexed: 11)
    
    # w = -1 for cosmological constant
    w = np.full_like(z, -1.0)
    
    return {
        'z': z,
        'H': H,
        'rho_lambda': rho_lambda,
        'w': w,
    }


def load_unified_background(prefix):
    """
    Load unified Ridder field background.
    
    Columns:
    1:z, 4:H, 15:rho_ridder, 16:p_ridder
    
    w_ridder = p_ridder / rho_ridder
    """
    bg_file = OUTPUT_DIR / f"{prefix}00_background.dat"
    if not bg_file.exists():
        print(f"  ⚠️  File not found: {bg_file}")
        return None
    
    data = np.loadtxt(bg_file)
    z = data[:, 0]            # Column 1: redshift
    H = data[:, 3]            # Column 4: H(z)
    rho_ridder = data[:, 14]  # Column 15: rho_ridder (0-indexed: 14)
    p_ridder = data[:, 15]    # Column 16: p_ridder (0-indexed: 15)
    phi_ridder = data[:, 16]  # Column 17: phi_ridder
    
    # w = p / rho
    # Avoid division by zero: set w = -1 where rho ~ 0
    w = np.full_like(z, -1.0)
    mask = np.abs(rho_ridder) > 1e-30
    w[mask] = p_ridder[mask] / rho_ridder[mask]
    
    # Clip to physical range for plotting
    w = np.clip(w, -2.0, 1.0)
    
    return {
        'z': z,
        'H': H,
        'rho_ridder': rho_ridder,
        'p_ridder': p_ridder,
        'phi_ridder': phi_ridder,
        'w': w,
    }


# --------------------------------------------------------------------------
# Load all models
# --------------------------------------------------------------------------

models = {
    'ΛCDM': ('lcdm_baseline_', load_lcdm_background),
    'Hero': ('unified_cdm_hero_bgonly_', load_unified_background),
    'Safe': ('unified_cdm_safe_bgonly_', load_unified_background),
}

results = {}
for name, (prefix, load_func) in models.items():
    print(f"Loading {name:15s} ... ", end="", flush=True)
    data = load_func(prefix)
    if data is not None:
        print(f"✓ {len(data['z'])} points, z ∈ [{data['z'][-1]:.2e}, {data['z'][0]:.2e}]")
        results[name] = data
    else:
        print("❌ FAILED")

if len(results) == 0:
    print("\n⚠️  No data loaded! Exiting.")
    exit(1)

print()

# --------------------------------------------------------------------------
# Sample w(z) at key redshifts
# --------------------------------------------------------------------------

print(f"{'='*70}")
print("w(z) AT KEY REDSHIFTS")
print(f"{'='*70}\n")

z_samples = [0, 0.5, 1.0, 2.0, 5.0, 10.0, 100.0, 1000.0, 3000.0]

print(f"{'z':>8s}", end="")
for name in ['ΛCDM', 'Hero', 'Safe']:
    if name in results:
        print(f"{name:>12s}", end="")
print()
print("-" * 60)

for z_sample in z_samples:
    print(f"{z_sample:8.1f}", end="")
    for name in ['ΛCDM', 'Hero', 'Safe']:
        if name in results:
            z_arr = results[name]['z']
            w_arr = results[name]['w']
            # CLASS outputs z in descending order typically
            w_val = np.interp(z_sample, z_arr[::-1], w_arr[::-1])
            print(f"{w_val:>12.4f}", end="")
    print()

print()

# --------------------------------------------------------------------------
# Create plots
# --------------------------------------------------------------------------

print(f"{'='*70}")
print("CREATING PLOTS")
print(f"{'='*70}\n")

# Plot 1: w(z) evolution
fig, ax = plt.subplots(figsize=(10, 6))

colors = {'ΛCDM': 'black', 'Hero': 'red', 'Safe': 'blue'}
styles = {'ΛCDM': '-', 'Hero': '--', 'Safe': ':'}

for name in ['ΛCDM', 'Hero', 'Safe']:
    if name in results:
        z = results[name]['z']
        w = results[name]['w']
        
        # Plot in 1+z for better visualization
        ax.plot(1+z, w, 
                color=colors[name], 
                linestyle=styles[name],
                linewidth=2.5 if name == 'ΛCDM' else 2,
                label=name,
                alpha=0.9)

ax.axhline(-1, color='gray', linestyle=':', alpha=0.5, label='w = -1')
ax.set_xlabel('1 + z', fontsize=14)
ax.set_ylabel('w(z)', fontsize=14)
ax.set_xscale('log')
ax.set_xlim(1, 10000)
ax.set_ylim(-1.2, 0.2)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=12, loc='best')
ax.set_title('Dark Energy Equation of State Evolution', fontsize=16)

plt.tight_layout()
output_file = REPO_ROOT / "w_of_z_comparison.png"
plt.savefig(output_file, dpi=150)
print(f"✓ Saved: {output_file}")

# Plot 2: Deviation from ΛCDM
if 'Hero' in results or 'Safe' in results:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for name in ['Hero', 'Safe']:
        if name in results:
            z = results[name]['z']
            w = results[name]['w']
            
            # Deviation: Δw = w - (-1)
            delta_w = w + 1.0
            
            ax.plot(1+z, delta_w,
                    color=colors[name],
                    linestyle=styles[name],
                    linewidth=2,
                    label=name,
                    alpha=0.9)
    
    ax.axhline(0, color='gray', linestyle=':', alpha=0.5)
    ax.set_xlabel('1 + z', fontsize=14)
    ax.set_ylabel('Δw(z) = w(z) - (-1)', fontsize=14)
    ax.set_xscale('log')
    ax.set_xlim(1, 10000)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=12, loc='best')
    ax.set_title('Deviation from ΛCDM (w = -1)', fontsize=16)
    
    plt.tight_layout()
    output_file = REPO_ROOT / "w_deviation_from_lcdm.png"
    plt.savefig(output_file, dpi=150)
    print(f"✓ Saved: {output_file}")

# Plot 3: rho_ridder(z) evolution for unified models
if 'Hero' in results or 'Safe' in results:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for name in ['Hero', 'Safe']:
        if name in results:
            z = results[name]['z']
            rho = results[name]['rho_ridder']
            
            # Only plot where rho > 0
            mask = rho > 1e-20
            
            ax.plot(1+z[mask], rho[mask],
                    color=colors[name],
                    linestyle=styles[name],
                    linewidth=2,
                    label=name,
                    alpha=0.9)
    
    ax.set_xlabel('1 + z', fontsize=14)
    ax.set_ylabel('ρ_Ridder [Mpc⁻²]', fontsize=14)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1, 10000)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=12, loc='best')
    ax.set_title('Ridder Field Energy Density Evolution', fontsize=16)
    
    plt.tight_layout()
    output_file = REPO_ROOT / "rho_ridder_evolution.png"
    plt.savefig(output_file, dpi=150)
    print(f"✓ Saved: {output_file}")

print()

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------

print(f"{'='*70}")
print("SUMMARY")
print(f"{'='*70}\n")

print("✓ Successfully extracted w(z) from background files!")
print()
print("Key findings:")
print()

for name in ['Hero', 'Safe']:
    if name in results:
        z = results[name]['z']
        w = results[name]['w']
        rho = results[name]['rho_ridder']
        
        # Find peak of rho_ridder
        idx_peak = np.argmax(rho)
        z_peak = z[idx_peak]
        w_peak = w[idx_peak]
        rho_peak = rho[idx_peak]
        
        # Sample at z=0
        w_today = np.interp(0, z[::-1], w[::-1])
        
        print(f"{name}:")
        print(f"  - Peak: z = {z_peak:.1f}, ρ_Ridder = {rho_peak:.2e} Mpc⁻², w = {w_peak:.4f}")
        print(f"  - Today: z = 0, w = {w_today:.4f}")
        print()

print("🎯 NEXT STEPS:")
print("  1. ✅ w(z) extracted - DONE!")
print("  2. Create 'baby unified' configs (weaker Lambda, smaller beta)")
print("  3. Get perturbations stable on baby config")
print("  4. Extract S8 and EE/TE shoulder")
print("  5. Walk parameters back to hero/safe")
print()

