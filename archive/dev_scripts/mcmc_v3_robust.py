#!/usr/bin/env python3
"""
mcmc_v3_robust.py - Robust tier 4 smoke test with explicit residual curves

Fixes from previous version:
1. Explicit ΛCDM baseline run (not file guessing)
2. Full residual curves: TT(ℓ), D_V(z)/r_s(z_drag)
3. Visual inspection capability
4. Proper CMB multipole-by-multipole comparison
"""

import subprocess
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Paths
REPO_ROOT = Path(__file__).parent
BUTTON_SCRIPT = REPO_ROOT / "run_unified_model_v3.py"
CLASS_PATH = REPO_ROOT / "phase2/class"
OUTPUT_DIR = CLASS_PATH / "output"
FIG_DIR = REPO_ROOT / "figures" / "mcmc_residuals"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# STEP 1: RUN ΛCDM BASELINE
# =============================================================================

def run_lcdm_baseline():
    """Run ΛCDM baseline and save as reference"""
    print("=" * 80)
    print("STEP 1: Running ΛCDM Baseline")
    print("=" * 80)
    
    cmd = [
        sys.executable,
        str(BUTTON_SCRIPT),
        "--preset", "lcdm_baseline",
        "--mode", "full",
        "--output_json", str(REPO_ROOT / "lcdm_baseline_ref.json")
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    if result.returncode != 0:
        print(f"✗ ΛCDM baseline failed!")
        return None
    
    # Find latest CLASS output files
    bg_files = sorted(OUTPUT_DIR.glob("v3_run*_background.dat"), 
                     key=lambda p: p.stat().st_mtime)
    cl_files = sorted(OUTPUT_DIR.glob("v3_run*_cl.dat"), 
                     key=lambda p: p.stat().st_mtime)
    
    if not bg_files or not cl_files:
        print("✗ No output files found!")
        return None
    
    lcdm_data = {
        'bg_file': str(bg_files[-1]),
        'cl_file': str(cl_files[-1]),
        'bg': np.loadtxt(bg_files[-1]),
        'cl': np.loadtxt(cl_files[-1]),
    }
    
    print(f"✓ ΛCDM baseline complete")
    print(f"  Background: {lcdm_data['bg_file']}")
    print(f"  Cl: {lcdm_data['cl_file']}")
    
    return lcdm_data

# =============================================================================
# STEP 2: RUN BRANCHES
# =============================================================================

def run_branch(preset, lcdm_data):
    """Run a branch and compute residuals vs ΛCDM"""
    print()
    print("=" * 80)
    print(f"Running: {preset}")
    print("=" * 80)
    
    output_json = REPO_ROOT / f"{preset}_ref.json"
    
    cmd = [
        sys.executable,
        str(BUTTON_SCRIPT),
        "--preset", preset,
        "--mode", "full",
        "--output_json", str(output_json)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    if result.returncode != 0:
        print(f"✗ {preset} failed!")
        return None
    
    # Load CLASS output
    bg_files = sorted(OUTPUT_DIR.glob("v3_run*_background.dat"), 
                     key=lambda p: p.stat().st_mtime)
    cl_files = sorted(OUTPUT_DIR.glob("v3_run*_cl.dat"), 
                     key=lambda p: p.stat().st_mtime)
    
    branch_bg = np.loadtxt(bg_files[-1])
    branch_cl = np.loadtxt(cl_files[-1])
    
    # Load JSON for observables
    with open(output_json, 'r') as f:
        obs_data = json.load(f)
    
    # Compute residuals
    residuals = compute_residuals(branch_bg, branch_cl, lcdm_data)
    
    print(f"✓ {preset} complete")
    print(f"  H0 = {obs_data['observables']['H0_km_s_Mpc']:.2f} km/s/Mpc")
    print(f"  f_EDE = {obs_data['observables']['f_EDE_peak']:.3f}")
    print(f"  CMB RMS = {residuals['cmb_rms']*100:.2f}%")
    print(f"  BAO max = {residuals['bao_max']*100:.2f}%")
    
    return {
        'preset': preset,
        'bg': branch_bg,
        'cl': branch_cl,
        'obs': obs_data['observables'],
        'residuals': residuals,
    }

# =============================================================================
# STEP 3: COMPUTE RESIDUALS
# =============================================================================

def compute_residuals(branch_bg, branch_cl, lcdm_data):
    """Compute detailed residuals vs ΛCDM"""
    
    lcdm_bg = lcdm_data['bg']
    lcdm_cl = lcdm_data['cl']
    
    # CMB: TT residual at each ℓ
    ell = branch_cl[:, 0]
    TT_branch = branch_cl[:, 1]
    ell_lcdm = lcdm_cl[:, 0]
    TT_lcdm = lcdm_cl[:, 1]
    
    # Interpolate to common ℓ grid
    ell_common = ell[(ell >= 30) & (ell <= 2000)]
    TT_branch_interp = np.interp(ell_common, ell, TT_branch)
    TT_lcdm_interp = np.interp(ell_common, ell_lcdm, TT_lcdm)
    
    # Fractional residual
    TT_residual = (TT_branch_interp - TT_lcdm_interp) / TT_lcdm_interp
    cmb_rms = np.sqrt(np.mean(TT_residual**2))
    
    # BAO: D_V(z) / r_s(z_drag) at standard BAO redshifts
    z_bg = branch_bg[:, 0]
    D_A = branch_bg[:, 5]  # Angular diameter distance
    H = branch_bg[:, 3]    # Hubble parameter [Mpc^-1]
    
    z_lcdm = lcdm_bg[:, 0]
    D_A_lcdm = lcdm_bg[:, 5]
    H_lcdm = lcdm_bg[:, 3]
    
    # Compute D_V = [(1+z)^2 D_A^2 c/H]^(1/3) at BAO redshifts
    z_bao = np.array([0.15, 0.35, 0.57, 0.70])
    bao_residuals = []
    
    for z_val in z_bao:
        # Branch
        D_A_val = np.interp(z_val, z_bg[::-1], D_A[::-1])
        H_val = np.interp(z_val, z_bg[::-1], H[::-1])
        D_V_val = ((1+z_val)**2 * D_A_val**2 / H_val)**(1/3)
        
        # ΛCDM
        D_A_lcdm_val = np.interp(z_val, z_lcdm[::-1], D_A_lcdm[::-1])
        H_lcdm_val = np.interp(z_val, z_lcdm[::-1], H_lcdm[::-1])
        D_V_lcdm_val = ((1+z_val)**2 * D_A_lcdm_val**2 / H_lcdm_val)**(1/3)
        
        # Residual
        residual = abs(D_V_val - D_V_lcdm_val) / D_V_lcdm_val
        bao_residuals.append(residual)
    
    bao_max = max(bao_residuals)
    
    return {
        'ell': ell_common,
        'TT_residual': TT_residual,
        'cmb_rms': cmb_rms,
        'z_bao': z_bao,
        'bao_residuals': np.array(bao_residuals),
        'bao_max': bao_max,
    }

# =============================================================================
# STEP 4: PLOT RESIDUALS
# =============================================================================

def plot_residuals(branches):
    """Plot CMB and BAO residuals for all branches"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    colors = {'v3_trgb_branch': 'green', 'v3_shoes_branch': 'red'}
    labels = {'v3_trgb_branch': 'TRGB (H₀=69.23)', 'v3_shoes_branch': 'SH0ES (H₀=73.10)'}
    
    # Left panel: CMB TT residuals
    for branch in branches:
        preset = branch['preset']
        res = branch['residuals']
        
        ax1.plot(res['ell'], res['TT_residual']*100, 
                label=f"{labels[preset]} (RMS={res['cmb_rms']*100:.2f}%)",
                color=colors[preset], linewidth=2, alpha=0.8)
    
    ax1.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax1.axhspan(-15, 15, color='lightgreen', alpha=0.2, label='15% threshold')
    ax1.set_xlabel('Multipole ℓ', fontsize=12, fontweight='bold')
    ax1.set_ylabel('TT Residual vs ΛCDM [%]', fontsize=12, fontweight='bold')
    ax1.set_title('CMB TT Power Spectrum Residuals', fontsize=14, fontweight='bold')
    ax1.set_xlim(30, 2000)
    ax1.set_ylim(-25, 25)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=10)
    
    # Right panel: BAO residuals
    width = 0.15
    x = np.arange(len(branches[0]['residuals']['z_bao']))
    
    for i, branch in enumerate(branches):
        preset = branch['preset']
        res = branch['residuals']
        
        ax2.bar(x + i*width, res['bao_residuals']*100, width,
               label=f"{labels[preset]} (max={res['bao_max']*100:.2f}%)",
               color=colors[preset], alpha=0.8)
    
    ax2.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.axhline(3, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='3% threshold')
    ax2.set_xlabel('BAO Redshift', fontsize=12, fontweight='bold')
    ax2.set_ylabel('D_V Residual vs ΛCDM [%]', fontsize=12, fontweight='bold')
    ax2.set_title('BAO Distance Residuals', fontsize=14, fontweight='bold')
    ax2.set_xticks(x + width/2)
    ax2.set_xticklabels([f'z={z:.2f}' for z in branches[0]['residuals']['z_bao']])
    ax2.set_ylim(0, 15)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.legend(loc='upper left', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'v3_tier4_residuals.png', dpi=300, bbox_inches='tight')
    plt.savefig(FIG_DIR / 'v3_tier4_residuals.pdf', bbox_inches='tight')
    print(f"\n✓ Residual plots saved to {FIG_DIR}")
    
    plt.show()

# =============================================================================
# STEP 5: SUMMARY
# =============================================================================

def print_summary(branches):
    """Print final summary table"""
    
    print()
    print("=" * 80)
    print("TIER 4 SMOKE TEST SUMMARY")
    print("=" * 80)
    print()
    
    print(f"{'Branch':<20} {'H0':>8} {'f_EDE':>8} {'CMB RMS':>10} {'BAO max':>10} {'Status':>10}")
    print("-" * 80)
    
    print(f"{'ΛCDM (reference)':<20} {'67.36':>8} {'0.000':>8} {'0.00%':>10} {'0.00%':>10} {'REF':>10}")
    
    for branch in branches:
        preset = branch['preset']
        obs = branch['obs']
        res = branch['residuals']
        
        H0 = obs['H0_km_s_Mpc']
        f_EDE = obs['f_EDE_peak']
        cmb_rms = res['cmb_rms'] * 100
        bao_max = res['bao_max'] * 100
        
        # Status
        if cmb_rms < 15 and bao_max < 3:
            status = '✓ PASS'
        elif cmb_rms < 20 and bao_max < 5:
            status = '~ MARGINAL'
        else:
            status = '✗ FAIL'
        
        print(f"{preset:<20} {H0:>8.2f} {f_EDE:>8.3f} {cmb_rms:>9.2f}% {bao_max:>9.2f}% {status:>10}")
    
    print()
    print("Thresholds:")
    print("  CMB RMS < 15%: Acceptable")
    print("  BAO max < 3%: Acceptable")
    print()

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 80)
    print("ROBUST TIER 4 SMOKE TEST")
    print("=" * 80)
    print()
    print("Testing:")
    print("  1. ΛCDM baseline (reference)")
    print("  2. v3_trgb_branch (H0~70)")
    print("  3. v3_shoes_branch (H0~73)")
    print()
    
    # Step 1: Run ΛCDM baseline
    lcdm_data = run_lcdm_baseline()
    if lcdm_data is None:
        print("\n✗ ΛCDM baseline failed! Cannot proceed.")
        return
    
    # Step 2: Run branches
    branch_presets = ['v3_trgb_branch', 'v3_shoes_branch']
    branches = []
    
    for preset in branch_presets:
        branch_data = run_branch(preset, lcdm_data)
        if branch_data:
            branches.append(branch_data)
    
    if not branches:
        print("\n✗ No branches completed successfully!")
        return
    
    # Step 3: Plot residuals
    plot_residuals(branches)
    
    # Step 4: Summary
    print_summary(branches)
    
    # Step 5: Save results
    results = {
        'lcdm': {
            'bg_file': lcdm_data['bg_file'],
            'cl_file': lcdm_data['cl_file'],
        },
        'branches': [
            {
                'preset': b['preset'],
                'H0': float(b['obs']['H0_km_s_Mpc']),
                'f_EDE': float(b['obs']['f_EDE_peak']),
                'cmb_rms': float(b['residuals']['cmb_rms']),
                'bao_max': float(b['residuals']['bao_max']),
            }
            for b in branches
        ]
    }
    
    results_file = REPO_ROOT / 'mcmc_v3_robust_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {results_file}")
    print()
    print("=" * 80)
    print("SMOKE TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

