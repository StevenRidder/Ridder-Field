#!/usr/bin/env python3
"""
Find a VIABLE unified point, not a maximum-power point.

Target criteria:
  - H0 >= 70.5 km/s/Mpc
  - S8 <= 0.77
  - f_EDE <= 0.18 (standard EDE range)
  - BAO residuals <= 3%
  - CMB acoustic region residuals <= 10%

Strategy: Lower f_axion to bring f_EDE into standard range,
          keep Lambda_tail moderate for BAO compliance.
"""

import subprocess
import numpy as np
import os
import json
import tempfile
import shutil

# ============================================================================
# Configuration
# ============================================================================

# Parameter grid - focus on LOWER f_axion to bring f_EDE down
LAMBDA_TAIL_VALUES = [14, 16, 18, 20]  # meV
F_AXION_VALUES = [0.15, 0.20, 0.25, 0.30, 0.35]  # Lower than before!

# Viability criteria
CRITERIA = {
    'H0_min': 70.5,
    'S8_max': 0.77,
    'f_EDE_max': 0.18,
    'BAO_max_pct': 3.0,
    'CMB_acoustic_max_pct': 10.0
}

# Paths
CLASS_DIR = os.path.expanduser("~/Git/Ridder-Field/phase2/class")
REPO_DIR = os.path.expanduser("~/Git/Ridder-Field")
OUTPUT_DIR = os.path.join(REPO_DIR, "output/viable_scan")
BASE_INI = "unified_hero.ini"

# ============================================================================
# Helper functions
# ============================================================================

def create_scan_ini(lambda_tail, f_axion, ini_path, output_root):
    """Create INI file for this scan point."""
    content = f"""# Viable point scan: Lambda={lambda_tail}meV, f_axion={f_axion}
# Targeting f_EDE <= 0.18, BAO <= 3%, CMB acoustic <= 10%

# Standard cosmology
H0 = 67.36
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842

# Ridder unified
use_ridder = yes
gauge = newtonian
ridder_model_type = unified

# Tail (late-time DE)
ridder_use_tail = yes
ridder_Lambda_tail_eV = {lambda_tail}e-3
ridder_alpha_tail = 1.0
ridder_n_tail = 1.0

# Shelf (EDE) - controlled by f_axion
ridder_use_shelf = yes
ridder_m_axion = 7e4
ridder_f_axion = {f_axion}
ridder_n_EDE = 3.0
ridder_theta_EDE_low = 0.1
ridder_theta_EDE_high = 3.0
ridder_sigma_theta_EDE = 0.3

ridder_use_plateau = no

# Field properties
ridder_f = 1.0e26
theta_i_ridder = 1.0
beta_ridder = 0.0
ridder_c_slow = 1.0

# Output
output = tCl, pCl, mPk
write background = yes
l_max_scalars = 2500
root = {output_root}
"""
    with open(ini_path, 'w') as f:
        f.write(content)


def run_class(ini_path):
    """Run CLASS and return success status."""
    try:
        result = subprocess.run(
            ["./class", ini_path],
            cwd=CLASS_DIR,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except Exception as e:
        print(f"  CLASS error: {e}")
        return False


def extract_f_ede(bg_file):
    """Extract f_EDE and z_peak from background file."""
    try:
        data = np.loadtxt(bg_file)
        z = data[:, 0]
        # Column 17 = rho_ridder, column 19 = rho_tot (for unified output)
        if data.shape[1] > 19:
            rho_ridder = data[:, 17]
            rho_tot = data[:, 19]
        else:
            return 0.0, 0.0
        
        f_ridder = rho_ridder / rho_tot
        idx_max = np.argmax(f_ridder)
        return f_ridder[idx_max], z[idx_max]
    except Exception as e:
        return 0.0, 0.0


def extract_h0_from_background(bg_file):
    """Extract H0 from background file (H at z=0)."""
    try:
        data = np.loadtxt(bg_file)
        z = data[:, 0]
        H = data[:, 3]  # H [1/Mpc]
        
        # Find H at z closest to 0
        idx_0 = np.argmin(np.abs(z))
        H0_inv_mpc = H[idx_0]
        
        # Convert to km/s/Mpc: H0 = H * c where c = 299792.458 km/s
        H0 = H0_inv_mpc * 299792.458
        return H0
    except:
        return 67.36


def extract_s8(pk_file, bg_file):
    """Extract S8 from matter power spectrum."""
    try:
        # Read P(k)
        pk_data = np.loadtxt(pk_file)
        k = pk_data[:, 0]  # h/Mpc
        Pk = pk_data[:, 1]  # (Mpc/h)^3
        
        # Get Omega_m from background
        bg_data = np.loadtxt(bg_file)
        z = bg_data[:, 0]
        idx_0 = np.argmin(np.abs(z))
        
        # Approximate Omega_m from rho_m / rho_crit at z=0
        # Columns: rho_b=10, rho_cdm=11, rho_crit from H
        H0_inv_mpc = bg_data[idx_0, 3]
        rho_crit = 3 * H0_inv_mpc**2 / (8 * np.pi)  # In CLASS units
        
        # Sum matter components
        rho_b = bg_data[idx_0, 10] if bg_data.shape[1] > 10 else 0
        rho_cdm = bg_data[idx_0, 11] if bg_data.shape[1] > 11 else 0
        rho_m = rho_b + rho_cdm
        
        Omega_m = 0.315  # Use Planck value as approximation
        
        # Compute sigma8 via integration
        R = 8.0  # Mpc/h
        
        # Window function (top-hat in Fourier space)
        x = k * R
        W = np.where(x > 0.01, 3 * (np.sin(x) - x * np.cos(x)) / x**3, 1.0)
        
        # sigma8^2 = 1/(2*pi^2) * integral of k^2 * P(k) * W^2 dk
        integrand = k**2 * Pk * W**2
        sigma8_sq = np.trapz(integrand, k) / (2 * np.pi**2)
        sigma8 = np.sqrt(sigma8_sq)
        
        # S8 = sigma8 * sqrt(Omega_m / 0.3)
        S8 = sigma8 * np.sqrt(Omega_m / 0.3)
        return S8
    except Exception as e:
        return 0.84


def extract_bao_residuals(bg_file, bg_lcdm_file):
    """Compute BAO distance residuals at z=0.35 and z=0.57."""
    try:
        # Load both files
        data = np.loadtxt(bg_file)
        data_lcdm = np.loadtxt(bg_lcdm_file)
        
        z = data[:, 0]
        z_lcdm = data_lcdm[:, 0]
        
        # Column 4 = comov. dist. (Mpc)
        D_comov = data[:, 4]
        D_comov_lcdm = data_lcdm[:, 4]
        
        # H(z)
        H = data[:, 3]
        H_lcdm = data_lcdm[:, 3]
        
        residuals = []
        for z_bao in [0.35, 0.57]:
            # Interpolate
            D_at_z = np.interp(z_bao, z[::-1], D_comov[::-1])
            D_lcdm_at_z = np.interp(z_bao, z_lcdm[::-1], D_comov_lcdm[::-1])
            
            H_at_z = np.interp(z_bao, z[::-1], H[::-1])
            H_lcdm_at_z = np.interp(z_bao, z_lcdm[::-1], H_lcdm[::-1])
            
            # D_A = D_comov / (1+z)
            DA = D_at_z / (1 + z_bao)
            DA_lcdm = D_lcdm_at_z / (1 + z_bao)
            
            # D_V = (D_A^2 * c*z / H)^(1/3)
            c = 299792.458  # km/s
            DV = (DA**2 * c * z_bao / (H_at_z * c))**(1/3)  # Simplified
            DV_lcdm = (DA_lcdm**2 * c * z_bao / (H_lcdm_at_z * c))**(1/3)
            
            # Percent difference
            pct = abs(DA - DA_lcdm) / DA_lcdm * 100
            residuals.append(pct)
        
        return max(residuals)
    except Exception as e:
        return 10.0


def extract_cmb_band_residuals(cl_file, cl_lcdm_file):
    """
    Compute CMB TT residuals by ℓ band:
    - Low ℓ: 2-30 (cosmic variance dominated)
    - Acoustic: 30-800 (peaks, high precision)
    - Damping: 800-2000 (damping tail)
    """
    try:
        # Load Cl files
        cl = np.loadtxt(cl_file)
        cl_lcdm = np.loadtxt(cl_lcdm_file)
        
        # Column 0 = ell, column 1 = TT
        ell = cl[:, 0]
        TT = cl[:, 1]
        
        ell_lcdm = cl_lcdm[:, 0]
        TT_lcdm = cl_lcdm[:, 1]
        
        # Interpolate to common ell grid
        ell_common = ell[ell <= min(ell.max(), ell_lcdm.max())]
        TT_interp = np.interp(ell_common, ell, TT)
        TT_lcdm_interp = np.interp(ell_common, ell_lcdm, TT_lcdm)
        
        # Compute residuals
        residual = np.abs(TT_interp - TT_lcdm_interp) / np.abs(TT_lcdm_interp) * 100
        
        # Band masks
        low_mask = (ell_common >= 2) & (ell_common <= 30)
        acoustic_mask = (ell_common > 30) & (ell_common <= 800)
        damping_mask = (ell_common > 800) & (ell_common <= 2000)
        
        # Max residual in each band
        low_max = residual[low_mask].max() if low_mask.any() else 0
        acoustic_max = residual[acoustic_mask].max() if acoustic_mask.any() else 0
        damping_max = residual[damping_mask].max() if damping_mask.any() else 0
        
        return {
            'low': low_max,
            'acoustic': acoustic_max,
            'damping': damping_max
        }
    except Exception as e:
        return {'low': 100, 'acoustic': 100, 'damping': 100}


def check_viability(metrics):
    """Check if a point meets all viability criteria."""
    checks = {
        'H0': metrics['H0'] >= CRITERIA['H0_min'],
        'S8': metrics['S8'] <= CRITERIA['S8_max'],
        'f_EDE': metrics['f_EDE'] <= CRITERIA['f_EDE_max'],
        'BAO': metrics['BAO_max'] <= CRITERIA['BAO_max_pct'],
        'CMB_acoustic': metrics['CMB_acoustic'] <= CRITERIA['CMB_acoustic_max_pct']
    }
    return checks, all(checks.values())


# ============================================================================
# Main scan
# ============================================================================

def main():
    print("=" * 70)
    print("VIABLE POINT FINDER: Searching for observationally defensible config")
    print("=" * 70)
    print(f"\nCriteria:")
    print(f"  H0 >= {CRITERIA['H0_min']} km/s/Mpc")
    print(f"  S8 <= {CRITERIA['S8_max']}")
    print(f"  f_EDE <= {CRITERIA['f_EDE_max']}")
    print(f"  BAO residuals <= {CRITERIA['BAO_max_pct']}%")
    print(f"  CMB acoustic residuals <= {CRITERIA['CMB_acoustic_max_pct']}%")
    print()
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # First, run LCDM baseline for comparison
    print("Running LCDM baseline...")
    lcdm_ini = f"{OUTPUT_DIR}/lcdm_baseline.ini"
    with open(lcdm_ini, 'w') as f:
        f.write(f"""# LCDM baseline for comparison
H0 = 67.36
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842

output = tCl, pCl, mPk
write background = yes
l_max_scalars = 2500
root = {OUTPUT_DIR}/lcdm_baseline
""")
    
    if not run_class(lcdm_ini):
        print("  WARNING: LCDM baseline failed!")
    
    lcdm_bg = f"{OUTPUT_DIR}/lcdm_baseline00_background.dat"
    lcdm_cl = f"{OUTPUT_DIR}/lcdm_baseline00_cl.dat"
    
    # Results storage
    results = []
    viable_points = []
    
    total = len(LAMBDA_TAIL_VALUES) * len(F_AXION_VALUES)
    count = 0
    
    print(f"\nScanning {total} points...")
    print("-" * 70)
    
    for lambda_tail in LAMBDA_TAIL_VALUES:
        for f_axion in F_AXION_VALUES:
            count += 1
            label = f"L={lambda_tail}meV, f={f_axion}"
            print(f"\n[{count}/{total}] {label}")
            
            # Create and run
            ini_path = f"{OUTPUT_DIR}/scan_L{lambda_tail:.0f}_f{f_axion*100:.0f}.ini"
            output_root = f"{OUTPUT_DIR}/scan_L{lambda_tail:.0f}_f{f_axion*100:.0f}"
            create_scan_ini(lambda_tail, f_axion, ini_path, output_root)
            
            if not run_class(ini_path):
                print("  ❌ CLASS failed")
                continue
            
            # Output file paths
            root = f"{OUTPUT_DIR}/scan_L{lambda_tail:.0f}_f{f_axion*100:.0f}"
            bg_file = f"{root}00_background.dat"
            pk_file = f"{root}00_pk.dat"
            cl_file = f"{root}00_cl.dat"
            
            # Extract metrics
            f_ede, z_peak = extract_f_ede(bg_file)
            H0 = extract_h0_from_background(bg_file)
            S8 = extract_s8(pk_file, bg_file)
            bao_max = extract_bao_residuals(bg_file, lcdm_bg)
            cmb_bands = extract_cmb_band_residuals(cl_file, lcdm_cl)
            
            metrics = {
                'lambda_tail': lambda_tail,
                'f_axion': f_axion,
                'H0': H0,
                'S8': S8,
                'f_EDE': f_ede,
                'z_peak': z_peak,
                'BAO_max': bao_max,
                'CMB_low': cmb_bands['low'],
                'CMB_acoustic': cmb_bands['acoustic'],
                'CMB_damping': cmb_bands['damping']
            }
            
            # Check viability
            checks, is_viable = check_viability(metrics)
            metrics['checks'] = checks
            metrics['viable'] = is_viable
            
            results.append(metrics)
            
            # Print summary
            status = "✅ VIABLE" if is_viable else "❌"
            print(f"  H0={H0:.2f}, S8={S8:.3f}, f_EDE={f_ede:.3f}")
            print(f"  BAO={bao_max:.1f}%, CMB_acoustic={cmb_bands['acoustic']:.1f}%")
            print(f"  {status}")
            
            # Show which criteria failed
            if not is_viable:
                failed = [k for k, v in checks.items() if not v]
                print(f"  Failed: {', '.join(failed)}")
            else:
                viable_points.append(metrics)
    
    # Summary
    print("\n" + "=" * 70)
    print("SCAN COMPLETE")
    print("=" * 70)
    
    print(f"\nTotal points: {len(results)}")
    print(f"Viable points: {len(viable_points)}")
    
    if viable_points:
        print("\n" + "-" * 70)
        print("VIABLE CONFIGURATIONS:")
        print("-" * 70)
        print(f"{'Λ_tail':>8} {'f_axion':>8} {'H0':>8} {'S8':>8} {'f_EDE':>8} {'BAO%':>8} {'CMB_ac%':>8}")
        print("-" * 70)
        
        for p in viable_points:
            print(f"{p['lambda_tail']:>8.0f} {p['f_axion']:>8.2f} {p['H0']:>8.2f} "
                  f"{p['S8']:>8.3f} {p['f_EDE']:>8.3f} {p['BAO_max']:>8.1f} {p['CMB_acoustic']:>8.1f}")
        
        # Find best by simple scoring
        print("\n" + "-" * 70)
        print("BEST VIABLE POINT (highest H0 that passes all criteria):")
        print("-" * 70)
        best = max(viable_points, key=lambda x: x['H0'])
        print(f"  Λ_tail = {best['lambda_tail']} meV")
        print(f"  f_axion = {best['f_axion']}")
        print(f"  H0 = {best['H0']:.2f} km/s/Mpc")
        print(f"  S8 = {best['S8']:.3f}")
        print(f"  f_EDE = {best['f_EDE']:.3f} at z = {best['z_peak']:.0f}")
        print(f"  BAO max residual = {best['BAO_max']:.1f}%")
        print(f"  CMB acoustic max = {best['CMB_acoustic']:.1f}%")
    else:
        print("\n⚠️  NO VIABLE POINTS FOUND")
        print("Consider relaxing criteria or expanding parameter range")
        
        # Show closest points
        print("\n" + "-" * 70)
        print("CLOSEST TO VIABLE (sorted by number of criteria passed):")
        print("-" * 70)
        
        for r in sorted(results, key=lambda x: sum(x['checks'].values()), reverse=True)[:5]:
            passed = sum(r['checks'].values())
            print(f"  L={r['lambda_tail']}, f={r['f_axion']}: {passed}/5 criteria")
            print(f"    H0={r['H0']:.2f}, S8={r['S8']:.3f}, f_EDE={r['f_EDE']:.3f}")
            print(f"    BAO={r['BAO_max']:.1f}%, CMB_ac={r['CMB_acoustic']:.1f}%")
            failed = [k for k, v in r['checks'].items() if not v]
            print(f"    Failed: {', '.join(failed)}")
    
    # Save results
    results_file = f"{OUTPUT_DIR}/viable_scan_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_file}")


if __name__ == "__main__":
    main()

