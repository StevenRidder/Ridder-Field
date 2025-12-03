#!/usr/bin/env python3
"""
MCMC Smoke Test for Ridder Unified Model

Quick test to see if there's any viable region in parameter space.
Uses simple Metropolis-Hastings with a χ² likelihood.
"""

import subprocess
import numpy as np
import os
import json
from datetime import datetime

# Paths
CLASS_DIR = "/home/ridderadmin/Ridder-Field/phase2/class"
OUTPUT_DIR = "/home/ridderadmin/Ridder-Field/phase2/class/output/mcmc"

# Fixed model parameters
FIXED = {
    "n_tail": 1.0, "n_shelf": 3.0, "alpha_tail": 1.0, "theta_i": 2.5,
    "theta_EDE_low": 0.5, "theta_EDE_high": 3.5, "sigma_EDE": 0.5,
    "m_axion": 7e4, "ridder_f": 7.305e26, "ridder_c_slow": 0.0, "beta_ridder": 0.0,
}

# Parameter bounds (Lambda_tail in meV, f_axion dimensionless)
BOUNDS = {
    "Lambda_tail": (15.0, 40.0),
    "f_axion": (0.15, 0.50),
}

# Data constraints (targets with errors)
DATA = {
    "H0": (73.04, 1.04),      # SH0ES
    "S8": (0.766, 0.020),     # KiDS-1000
    "CMB_RMS_max": 0.15,      # 15% target
    "BAO_max": 0.03,          # 3% target
}

# LCDM reference
LCDM = {"H0": 67.36, "S8": 0.834}


def create_ini(lt, fa, label):
    """Create CLASS INI file."""
    root = f"{OUTPUT_DIR}/{label}"
    return f"""H0 = 67.36
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842
use_ridder = yes
gauge = newtonian
ridder_model_type = unified
ridder_use_tail = yes
ridder_Lambda_tail_eV = {lt}e-3
ridder_alpha_tail = {FIXED["alpha_tail"]}
ridder_n_tail = {FIXED["n_tail"]}
ridder_use_shelf = yes
ridder_m_axion = {FIXED["m_axion"]}
ridder_f_axion = {fa}
ridder_n_EDE = {FIXED["n_shelf"]}
ridder_theta_EDE_low = {FIXED["theta_EDE_low"]}
ridder_theta_EDE_high = {FIXED["theta_EDE_high"]}
ridder_sigma_theta_EDE = {FIXED["sigma_EDE"]}
ridder_use_plateau = no
ridder_f = {FIXED["ridder_f"]}
theta_i_ridder = {FIXED["theta_i"]}
beta_ridder = {FIXED["beta_ridder"]}
ridder_c_slow = {FIXED["ridder_c_slow"]}
output = tCl,mPk
write background = yes
l_max_scalars = 2500
root = {root}
""", root


def run_class(ini_content, label):
    """Run CLASS and return success."""
    ini_path = f"{OUTPUT_DIR}/{label}.ini"
    with open(ini_path, "w") as f:
        f.write(ini_content)
    result = subprocess.run(
        ["./class", ini_path], cwd=CLASS_DIR,
        capture_output=True, text=True, timeout=300
    )
    return result.returncode == 0


def extract_observables(label):
    """Extract observables from CLASS output."""
    try:
        bg = np.loadtxt(f"{OUTPUT_DIR}/{label}00_background.dat")
        cl = np.loadtxt(f"{OUTPUT_DIR}/{label}00_cl.dat")
        pk = np.loadtxt(f"{OUTPUT_DIR}/{label}00_pk.dat")
        lcdm_bg = np.loadtxt(f"{OUTPUT_DIR}/lcdm00_background.dat")
        lcdm_cl = np.loadtxt(f"{OUTPUT_DIR}/lcdm00_cl.dat")
        
        z, H, D = bg[:, 0], bg[:, 3], bg[:, 4]
        
        # H0
        idx_0 = np.argmin(np.abs(z))
        H0 = H[idx_0] * 299792.458
        
        # S8
        k, Pk = pk[:, 0], pk[:, 1]
        R = 8.0
        x = k * R
        W = np.where(x > 0.01, 3*(np.sin(x) - x*np.cos(x))/x**3, 1.0)
        sigma8 = np.sqrt(np.trapz(k**2 * Pk * W**2, k) / (2*np.pi**2))
        S8 = sigma8 * np.sqrt(0.315/0.3)
        
        # BAO
        z_lcdm, D_lcdm = lcdm_bg[:, 0], lcdm_bg[:, 4]
        bao_035 = abs(np.interp(0.35, z[::-1], D[::-1]) - np.interp(0.35, z_lcdm[::-1], D_lcdm[::-1])) / np.interp(0.35, z_lcdm[::-1], D_lcdm[::-1])
        bao_057 = abs(np.interp(0.57, z[::-1], D[::-1]) - np.interp(0.57, z_lcdm[::-1], D_lcdm[::-1])) / np.interp(0.57, z_lcdm[::-1], D_lcdm[::-1])
        bao_max = max(bao_035, bao_057)
        
        # CMB RMS
        ell, TT = cl[:, 0], cl[:, 1]
        ell_l, TT_l = lcdm_cl[:, 0], lcdm_cl[:, 1]
        mask = (ell >= 30) & (ell <= 2000)
        TT_i = np.interp(ell[mask], ell, TT)
        TT_l_i = np.interp(ell[mask], ell_l, TT_l)
        cmb_rms = np.sqrt(np.mean(((TT_i - TT_l_i)/TT_l_i)**2))
        
        return {"H0": H0, "S8": S8, "CMB_RMS": cmb_rms, "BAO": bao_max}
    except:
        return None


def log_likelihood(obs):
    """Compute log-likelihood from observables."""
    if obs is None:
        return -1e10
    
    # χ² contributions
    chi2_H0 = ((obs["H0"] - DATA["H0"][0]) / DATA["H0"][1])**2
    chi2_S8 = ((obs["S8"] - DATA["S8"][0]) / DATA["S8"][1])**2
    
    # Soft penalties for CMB and BAO (exponential outside bounds)
    if obs["CMB_RMS"] > DATA["CMB_RMS_max"]:
        chi2_CMB = ((obs["CMB_RMS"] - DATA["CMB_RMS_max"]) / 0.05)**2
    else:
        chi2_CMB = 0.0
    
    if obs["BAO"] > DATA["BAO_max"]:
        chi2_BAO = ((obs["BAO"] - DATA["BAO_max"]) / 0.01)**2
    else:
        chi2_BAO = 0.0
    
    chi2_total = chi2_H0 + chi2_S8 + chi2_CMB + chi2_BAO
    return -0.5 * chi2_total


def metropolis_hastings(n_samples=200, n_burn=50):
    """Simple Metropolis-Hastings MCMC."""
    
    # Starting point (middle of parameter space)
    current_lt = 25.0
    current_fa = 0.30
    
    # Step sizes
    step_lt = 2.0
    step_fa = 0.03
    
    # Run initial point
    print("Running initial point...")
    ini, root = create_ini(current_lt, current_fa, "mcmc_init")
    if not run_class(ini, "mcmc_init"):
        print("Initial point failed!")
        return None
    
    current_obs = extract_observables("mcmc_init")
    if current_obs is None:
        print("Could not extract observables from initial point!")
        return None
    
    current_logL = log_likelihood(current_obs)
    print(f"Initial: Lt={current_lt:.1f}, fa={current_fa:.2f}, "
          f"H0={current_obs['H0']:.1f}, S8={current_obs['S8']:.2f}, logL={current_logL:.1f}")
    
    # Storage
    samples = []
    accepted = 0
    
    print(f"\nRunning {n_samples} MCMC samples...")
    
    for i in range(n_samples):
        # Propose new point
        prop_lt = current_lt + np.random.normal(0, step_lt)
        prop_fa = current_fa + np.random.normal(0, step_fa)
        
        # Bounds check
        if not (BOUNDS["Lambda_tail"][0] <= prop_lt <= BOUNDS["Lambda_tail"][1]):
            continue
        if not (BOUNDS["f_axion"][0] <= prop_fa <= BOUNDS["f_axion"][1]):
            continue
        
        # Run CLASS
        label = f"mcmc_{i:04d}"
        ini, root = create_ini(prop_lt, prop_fa, label)
        if not run_class(ini, label):
            continue
        
        prop_obs = extract_observables(label)
        if prop_obs is None:
            continue
        
        prop_logL = log_likelihood(prop_obs)
        
        # Accept/reject
        log_alpha = prop_logL - current_logL
        if np.log(np.random.random()) < log_alpha:
            current_lt = prop_lt
            current_fa = prop_fa
            current_obs = prop_obs
            current_logL = prop_logL
            accepted += 1
        
        # Store (after burn-in)
        if i >= n_burn:
            samples.append({
                "Lambda_tail": current_lt,
                "f_axion": current_fa,
                "H0": current_obs["H0"],
                "S8": current_obs["S8"],
                "CMB_RMS": current_obs["CMB_RMS"],
                "BAO": current_obs["BAO"],
                "logL": current_logL,
            })
        
        if (i+1) % 20 == 0:
            print(f"[{i+1}/{n_samples}] Lt={current_lt:.1f} fa={current_fa:.2f} "
                  f"H0={current_obs['H0']:.1f} S8={current_obs['S8']:.2f} "
                  f"CMB={current_obs['CMB_RMS']*100:.0f}% BAO={current_obs['BAO']*100:.1f}% "
                  f"logL={current_logL:.1f} acc={accepted/(i+1)*100:.0f}%")
    
    return samples


def main():
    print("=" * 70)
    print("MCMC SMOKE TEST: Ridder Unified Model")
    print("=" * 70)
    print(f"\nParameter bounds:")
    print(f"  Lambda_tail: {BOUNDS['Lambda_tail']}")
    print(f"  f_axion: {BOUNDS['f_axion']}")
    print(f"\nData constraints:")
    print(f"  H0 = {DATA['H0'][0]} +/- {DATA['H0'][1]} (SH0ES)")
    print(f"  S8 = {DATA['S8'][0]} +/- {DATA['S8'][1]} (KiDS)")
    print(f"  CMB_RMS < {DATA['CMB_RMS_max']*100:.0f}%")
    print(f"  BAO < {DATA['BAO_max']*100:.0f}%")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Ensure LCDM baseline exists
    print("\nChecking LCDM baseline...")
    lcdm_file = f"{OUTPUT_DIR}/lcdm00_background.dat"
    if not os.path.exists(lcdm_file):
        print("Running LCDM baseline...")
        lcdm_ini = f"""H0 = 67.36
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842
output = tCl,mPk
write background = yes
l_max_scalars = 2500
root = {OUTPUT_DIR}/lcdm
"""
        with open(f"{OUTPUT_DIR}/lcdm.ini", "w") as f:
            f.write(lcdm_ini)
        subprocess.run(["./class", f"{OUTPUT_DIR}/lcdm.ini"], cwd=CLASS_DIR, 
                      capture_output=True, timeout=300)
    
    # Run MCMC
    print("\n" + "=" * 70)
    samples = metropolis_hastings(n_samples=150, n_burn=30)
    
    if samples is None or len(samples) == 0:
        print("\nMCMC failed!")
        return
    
    # Analyze results
    print("\n" + "=" * 70)
    print("MCMC RESULTS")
    print("=" * 70)
    
    samples_arr = np.array([(s["Lambda_tail"], s["f_axion"], s["H0"], s["S8"], 
                            s["CMB_RMS"], s["BAO"], s["logL"]) for s in samples])
    
    print(f"\nSamples: {len(samples)}")
    print(f"\nParameter posteriors:")
    print(f"  Lambda_tail: {np.mean(samples_arr[:,0]):.1f} +/- {np.std(samples_arr[:,0]):.1f} meV")
    print(f"  f_axion: {np.mean(samples_arr[:,1]):.3f} +/- {np.std(samples_arr[:,1]):.3f}")
    
    print(f"\nObservable posteriors:")
    print(f"  H0: {np.mean(samples_arr[:,2]):.1f} +/- {np.std(samples_arr[:,2]):.1f} km/s/Mpc")
    print(f"  S8: {np.mean(samples_arr[:,3]):.3f} +/- {np.std(samples_arr[:,3]):.3f}")
    print(f"  CMB_RMS: {np.mean(samples_arr[:,4])*100:.1f}% +/- {np.std(samples_arr[:,4])*100:.1f}%")
    print(f"  BAO: {np.mean(samples_arr[:,5])*100:.1f}% +/- {np.std(samples_arr[:,5])*100:.1f}%")
    
    # Best point
    best_idx = np.argmax(samples_arr[:, 6])
    best = samples[best_idx]
    print(f"\nBest point (max logL = {best['logL']:.1f}):")
    print(f"  Lambda_tail = {best['Lambda_tail']:.1f} meV")
    print(f"  f_axion = {best['f_axion']:.3f}")
    print(f"  H0 = {best['H0']:.1f} km/s/Mpc")
    print(f"  S8 = {best['S8']:.3f}")
    print(f"  CMB_RMS = {best['CMB_RMS']*100:.1f}%")
    print(f"  BAO = {best['BAO']*100:.1f}%")
    
    # Check for viable points
    viable = [s for s in samples if s["H0"] >= 71 and s["S8"] <= 0.78 
              and s["CMB_RMS"] <= 0.20 and s["BAO"] <= 0.05]
    
    print(f"\n{'='*70}")
    if viable:
        print(f"VIABLE POINTS FOUND: {len(viable)}")
        for v in sorted(viable, key=lambda x: x["logL"], reverse=True)[:5]:
            print(f"  Lt={v['Lambda_tail']:.1f} fa={v['f_axion']:.2f} "
                  f"H0={v['H0']:.1f} S8={v['S8']:.2f}")
    else:
        print("NO VIABLE POINTS FOUND IN MCMC SAMPLES")
        # Show how close we got
        best_tension = [s for s in samples if s["H0"] >= 70 and s["S8"] <= 0.80]
        if best_tension:
            print(f"\nClosest to viable ({len(best_tension)} samples with H0>=70, S8<=0.80):")
            for b in sorted(best_tension, key=lambda x: x["CMB_RMS"])[:3]:
                print(f"  Lt={b['Lambda_tail']:.1f} fa={b['f_axion']:.2f} "
                      f"H0={b['H0']:.1f} S8={b['S8']:.2f} "
                      f"CMB={b['CMB_RMS']*100:.0f}% BAO={b['BAO']*100:.1f}%")
    print("=" * 70)
    
    # Save results
    with open(f"{OUTPUT_DIR}/mcmc_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "n_samples": len(samples),
            "bounds": BOUNDS,
            "data": DATA,
            "samples": samples,
            "best": best,
        }, f, indent=2)
    print(f"\nResults saved to {OUTPUT_DIR}/mcmc_results.json")


if __name__ == "__main__":
    main()

