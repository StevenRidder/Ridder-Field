#!/usr/bin/env python3
"""
UNIFIED HERO VALIDATION SUITE
=============================
Complete validation of the unified hero configuration.
Outputs: text summary + diagnostic plots.

This is the "show me everything about this model" button.
"""

import subprocess
import numpy as np
import os
from pathlib import Path
from datetime import datetime

CLASS_BIN = "phase2/class/class"
OUTPUT_DIR = Path("output")
PLOT_DIR = Path("validation_plots")

# Reference values
R_S_LCDM = 147.04  # Mpc
H0_LCDM = 67.36
H0_SHOES = 73.0
S8_PLANCK = 0.834
S8_KIDS = 0.759

# BAO redshifts
BAO_Z = [0.35, 0.57, 0.61]

def run_class(ini_file, timeout=180):
    """Run CLASS."""
    result = subprocess.run(
        [CLASS_BIN, ini_file],
        capture_output=True, text=True, timeout=timeout
    )
    return result.returncode == 0

def load_background(bg_file, has_ridder=True):
    """Load and parse background file."""
    bg = np.loadtxt(bg_file)
    ncols = bg.shape[1]
    
    # LCDM: 19 cols, rho_tot at col 14
    # Ridder: 24 cols, rho_ridder at col 14, rho_tot at col 19
    if has_ridder and ncols >= 20:
        return {
            'z': bg[:, 0],
            'H': bg[:, 3] * 299792.458,
            'r_s': bg[:, 7],
            'rho_ridder': bg[:, 14],
            'p_ridder': bg[:, 15],
            'rho_tot': bg[:, 19],
            'rho_b': bg[:, 9],
            'rho_cdm': bg[:, 10],
            'rho_crit': bg[:, 13],
        }
    else:
        return {
            'z': bg[:, 0],
            'H': bg[:, 3] * 299792.458,
            'r_s': bg[:, 7],
            'rho_ridder': np.zeros_like(bg[:, 0]),
            'p_ridder': np.zeros_like(bg[:, 0]),
            'rho_tot': bg[:, 14],
            'rho_b': bg[:, 9],
            'rho_cdm': bg[:, 10],
            'rho_crit': bg[:, 13],
        }

def compute_distances(bg):
    """Compute distance measures at various redshifts."""
    z = bg['z']
    H = bg['H']
    
    # D_A and D_V at BAO redshifts
    distances = {}
    
    for z_bao in BAO_Z:
        idx = np.argmin(np.abs(z - z_bao))
        H_z = H[idx]
        
        # D_H = c/H(z)
        D_H = 299792.458 / H_z  # Mpc
        
        # Approximate D_A from comoving distance
        # This is simplified - full calculation would integrate
        distances[f'H_{z_bao:.2f}'] = H_z
        distances[f'D_H_{z_bao:.2f}'] = D_H
    
    # r_s at drag (z ~ 1060)
    idx_drag = np.argmin(np.abs(z - 1060))
    distances['r_s_drag'] = bg['r_s'][idx_drag]
    
    return distances

def compute_ede_metrics(bg):
    """Compute EDE-specific metrics."""
    z = bg['z']
    rho_ridder = bg['rho_ridder']
    rho_tot = bg['rho_tot']
    
    valid = (rho_tot > 0) & (rho_ridder > 0)
    f_ridder = np.zeros_like(z)
    f_ridder[valid] = rho_ridder[valid] / rho_tot[valid]
    
    # EDE peak (z ~ 1000-20000)
    mask = (z > 1000) & (z < 20000)
    if mask.any():
        f_ede = f_ridder[mask]
        z_ede = z[mask]
        peak_idx = np.argmax(f_ede)
        f_peak = f_ede[peak_idx]
        z_peak = z_ede[peak_idx]
    else:
        f_peak, z_peak = 0, 0
    
    # Late-time
    f_late = f_ridder[-1]
    
    # w(z=0)
    w_late = 0
    if rho_ridder[-1] > 1e-50:
        w_late = bg['p_ridder'][-1] / rho_ridder[-1]
    
    return {
        'f_EDE': f_peak,
        'z_peak': z_peak,
        'f_late': f_late,
        'w_late': w_late,
        'f_ridder': f_ridder,
    }

def compute_structure(bg, pk_file):
    """Compute structure growth metrics."""
    if not pk_file.exists():
        return {}
    
    pk = np.loadtxt(pk_file)
    k, Pk = pk[:, 0], pk[:, 1]
    
    # sigma8
    R = 8.0
    x = k * R
    W = np.where(x > 0.01, 3.0 * (np.sin(x) - x * np.cos(x)) / x**3, 1.0)
    sigma8 = np.sqrt(np.trapz(Pk * W**2 * k**2, k) / (2 * np.pi**2))
    
    # Omega_m
    Omega_m = (bg['rho_b'][-1] + bg['rho_cdm'][-1]) / bg['rho_crit'][-1]
    
    # S8
    S8 = sigma8 * np.sqrt(Omega_m / 0.3)
    
    return {
        'sigma8': sigma8,
        'Omega_m': Omega_m,
        'S8': S8,
        'k': k,
        'Pk': Pk,
    }

def compute_cmb_diagnostics(cl_file, cl_lcdm_file=None):
    """Compute CMB spectrum diagnostics."""
    if not cl_file.exists():
        return {}
    
    cl = np.loadtxt(cl_file)
    ell = cl[:, 0]
    TT = cl[:, 1]
    
    diagnostics = {
        'ell': ell,
        'TT': TT,
        'TT_peak_ell': ell[np.argmax(TT)],
        'TT_peak_val': np.max(TT),
    }
    
    # If we have LCDM reference, compute residuals
    if cl_lcdm_file and cl_lcdm_file.exists():
        cl_lcdm = np.loadtxt(cl_lcdm_file)
        TT_lcdm = cl_lcdm[:, 1]
        
        # Fractional residuals
        residual = (TT - TT_lcdm) / TT_lcdm
        diagnostics['TT_residual'] = residual
        diagnostics['TT_residual_max'] = np.max(np.abs(residual))
        diagnostics['TT_residual_rms'] = np.sqrt(np.mean(residual**2))
    
    return diagnostics

def print_validation_report(hero, lcdm):
    """Print the validation report."""
    print("=" * 70)
    print("UNIFIED HERO VALIDATION REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # === 1. EDE Episode ===
    print("### 1. EDE EPISODE (Shelf)")
    print("-" * 50)
    print(f"  f_EDE (peak):    {hero['ede']['f_EDE']:.4f}")
    print(f"  z_peak:          {hero['ede']['z_peak']:.0f}")
    print(f"  Target range:    f_EDE ∈ [0.05, 0.20], z ∈ [2000, 5000]")
    f_ok = 0.05 < hero['ede']['f_EDE'] < 0.20
    z_ok = 2000 < hero['ede']['z_peak'] < 5000
    print(f"  Status:          {'✓ IN RANGE' if (f_ok and z_ok) else '⚠ OUT OF RANGE'}")
    print()
    
    # === 2. Late-Time Dark Energy (Tail) ===
    print("### 2. LATE-TIME DARK ENERGY (Tail)")
    print("-" * 50)
    print(f"  f_ridder(z=0):   {hero['ede']['f_late']:.4f}")
    print(f"  w(z=0):          {hero['ede']['w_late']:.3f}")
    print()
    
    # === 3. Sound Horizon & H0 ===
    print("### 3. SOUND HORIZON & H0")
    print("-" * 50)
    r_s_hero = hero['dist']['r_s_drag']
    r_s_lcdm = lcdm['dist']['r_s_drag']
    delta_rs = (r_s_hero - r_s_lcdm) / r_s_lcdm * 100
    H0_eff = H0_LCDM * (r_s_lcdm / r_s_hero)
    delta_H0 = H0_eff - H0_LCDM
    
    print(f"  r_s (ΛCDM):      {r_s_lcdm:.2f} Mpc")
    print(f"  r_s (Hero):      {r_s_hero:.2f} Mpc")
    print(f"  Δr_s/r_s:        {delta_rs:+.2f}%")
    print()
    print(f"  H0 (Planck):     {H0_LCDM:.2f} km/s/Mpc")
    print(f"  H0 (SH0ES):      {H0_SHOES:.1f} km/s/Mpc")
    print(f"  H0 (Hero):       {H0_eff:.2f} km/s/Mpc")
    print(f"  ΔH0:             {delta_H0:+.2f} km/s/Mpc")
    print()
    
    # === 4. Structure Growth ===
    print("### 4. STRUCTURE GROWTH")
    print("-" * 50)
    if 'S8' in hero['struct']:
        print(f"  σ8 (ΛCDM):       {lcdm['struct']['sigma8']:.4f}")
        print(f"  σ8 (Hero):       {hero['struct']['sigma8']:.4f}")
        print()
        print(f"  S8 (Planck):     {S8_PLANCK:.3f}")
        print(f"  S8 (KiDS):       {S8_KIDS:.3f}")
        print(f"  S8 (Hero):       {hero['struct']['S8']:.4f}")
        delta_S8 = hero['struct']['S8'] - lcdm['struct']['S8']
        print(f"  ΔS8:             {delta_S8:+.4f}")
        print()
        print(f"  Ω_m (Hero):      {hero['struct']['Omega_m']:.4f}")
    print()
    
    # === 5. BAO Distance Measures ===
    print("### 5. BAO DISTANCE MEASURES")
    print("-" * 50)
    print(f"  {'z':>6} {'H(z) ΛCDM':>12} {'H(z) Hero':>12} {'Δ%':>8}")
    print("  " + "-" * 42)
    for z_bao in BAO_Z:
        key = f'H_{z_bao:.2f}'
        H_lcdm = lcdm['dist'].get(key, 0)
        H_hero = hero['dist'].get(key, 0)
        if H_lcdm > 0:
            delta = (H_hero - H_lcdm) / H_lcdm * 100
            print(f"  {z_bao:>6.2f} {H_lcdm:>12.2f} {H_hero:>12.2f} {delta:>+8.2f}%")
    print()
    
    # === 6. CMB Diagnostics ===
    print("### 6. CMB DIAGNOSTICS")
    print("-" * 50)
    if 'TT_residual_max' in hero['cmb']:
        print(f"  Max |ΔC_ℓ/C_ℓ| (TT): {hero['cmb']['TT_residual_max']*100:.1f}%")
        print(f"  RMS residual (TT):   {hero['cmb']['TT_residual_rms']*100:.1f}%")
    print(f"  TT peak at ℓ =       {hero['cmb'].get('TT_peak_ell', 'N/A')}")
    print()
    
    # === 7. OVERALL ASSESSMENT ===
    print("=" * 70)
    print("OVERALL ASSESSMENT")
    print("=" * 70)
    
    h0_target = H0_eff > 71
    s8_target = hero['struct'].get('S8', 1) < 0.78
    
    print(f"  H0 > 71 km/s/Mpc:  {'✓ PASS' if h0_target else '✗ FAIL'} ({H0_eff:.2f})")
    print(f"  S8 < 0.78:         {'✓ PASS' if s8_target else '✗ FAIL'} ({hero['struct'].get('S8', 'N/A'):.4f})")
    
    if h0_target and s8_target:
        print()
        print("  ★ UNIFIED MODEL PASSES ALL PRIMARY TARGETS ★")
    
    print()

def main():
    PLOT_DIR.mkdir(exist_ok=True)
    
    print("Running validation suite...")
    print()
    
    # === Run LCDM baseline ===
    print("[1/2] Running ΛCDM baseline...")
    if not run_class("lcdm_baseline.ini"):
        print("ERROR: LCDM baseline failed")
        return 1
    
    # === Run unified hero ===
    print("[2/2] Running unified hero...")
    if not run_class("unified_hero.ini"):
        print("ERROR: Unified hero failed")
        return 1
    
    print()
    
    # === Load and analyze ===
    lcdm_bg = load_background(OUTPUT_DIR / "lcdm_baseline00_background.dat", has_ridder=False)
    hero_bg = load_background(OUTPUT_DIR / "unified_hero00_background.dat", has_ridder=True)
    
    lcdm = {
        'dist': compute_distances(lcdm_bg),
        'ede': compute_ede_metrics(lcdm_bg),
        'struct': compute_structure(lcdm_bg, OUTPUT_DIR / "lcdm_baseline00_pk.dat"),
        'cmb': compute_cmb_diagnostics(OUTPUT_DIR / "lcdm_baseline00_cl.dat"),
    }
    
    hero = {
        'dist': compute_distances(hero_bg),
        'ede': compute_ede_metrics(hero_bg),
        'struct': compute_structure(hero_bg, OUTPUT_DIR / "unified_hero00_pk.dat"),
        'cmb': compute_cmb_diagnostics(
            OUTPUT_DIR / "unified_hero00_cl.dat",
            OUTPUT_DIR / "lcdm_baseline00_cl.dat"
        ),
    }
    
    # === Print report ===
    print_validation_report(hero, lcdm)
    
    # === Generate plots ===
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        # Plot 1: f_ridder(z)
        fig, ax = plt.subplots(figsize=(10, 6))
        z = hero_bg['z']
        f_ridder = hero['ede']['f_ridder']
        mask = z > 1
        ax.loglog(z[mask], f_ridder[mask], 'b-', lw=2, label='Ridder field')
        ax.axvline(hero['ede']['z_peak'], color='r', ls='--', label=f'z_peak = {hero["ede"]["z_peak"]:.0f}')
        ax.axhline(hero['ede']['f_EDE'], color='g', ls=':', label=f'f_EDE = {hero["ede"]["f_EDE"]:.3f}')
        ax.set_xlabel('Redshift z')
        ax.set_ylabel('f_ridder = ρ_ridder / ρ_tot')
        ax.set_title('Ridder Field Energy Fraction')
        ax.legend()
        ax.set_xlim(1, 1e5)
        ax.grid(True, alpha=0.3)
        plt.savefig(PLOT_DIR / 'f_ridder_evolution.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        # Plot 2: P(k) comparison
        if 'Pk' in hero['struct'] and 'Pk' in lcdm['struct']:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [2, 1]})
            
            ax1.loglog(lcdm['struct']['k'], lcdm['struct']['Pk'], 'k-', lw=2, label='ΛCDM')
            ax1.loglog(hero['struct']['k'], hero['struct']['Pk'], 'b-', lw=2, label='Unified Hero')
            ax1.set_ylabel('P(k) [Mpc³/h³]')
            ax1.legend()
            ax1.set_title('Matter Power Spectrum')
            ax1.grid(True, alpha=0.3)
            
            # Interpolate to common k grid
            k_common = hero['struct']['k']
            Pk_lcdm_interp = np.interp(k_common, lcdm['struct']['k'], lcdm['struct']['Pk'])
            ratio = hero['struct']['Pk'] / Pk_lcdm_interp
            ax2.semilogx(k_common, ratio, 'b-', lw=2)
            ax2.axhline(1, color='k', ls='--')
            ax2.set_xlabel('k [h/Mpc]')
            ax2.set_ylabel('P(k)_hero / P(k)_ΛCDM')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(PLOT_DIR / 'pk_comparison.png', dpi=150, bbox_inches='tight')
            plt.close()
        
        # Plot 3: CMB TT spectrum
        if 'TT' in hero['cmb']:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [2, 1]})
            
            ax1.plot(lcdm['cmb']['ell'], lcdm['cmb']['TT'], 'k-', lw=1.5, label='ΛCDM')
            ax1.plot(hero['cmb']['ell'], hero['cmb']['TT'], 'b-', lw=1.5, label='Unified Hero')
            ax1.set_ylabel('ℓ(ℓ+1)C_ℓ/2π [μK²]')
            ax1.legend()
            ax1.set_title('CMB TT Spectrum')
            ax1.set_xlim(2, 2500)
            ax1.grid(True, alpha=0.3)
            
            if 'TT_residual' in hero['cmb']:
                ax2.plot(hero['cmb']['ell'], hero['cmb']['TT_residual'] * 100, 'b-', lw=1)
                ax2.axhline(0, color='k', ls='--')
                ax2.set_xlabel('Multipole ℓ')
                ax2.set_ylabel('ΔC_ℓ/C_ℓ [%]')
                ax2.set_xlim(2, 2500)
                ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(PLOT_DIR / 'cmb_tt_comparison.png', dpi=150, bbox_inches='tight')
            plt.close()
        
        print(f"Plots saved to: {PLOT_DIR}/")
        
    except ImportError:
        print("matplotlib not available, skipping plots")
    
    return 0

if __name__ == "__main__":
    exit(main())

