#!/usr/bin/env python3
"""
Relaxed constraint scan for Ridder Unified Model.
Tests two scenarios:
1. Relaxed B: f_EDE up to 0.35
2. Relaxed B+D: f_EDE up to 0.35 AND relaxed w(z)
"""

import subprocess
import numpy as np
import os

# Paths
CLASS_DIR = "/home/ridderadmin/Ridder-Field/phase2/class"
OUTPUT_DIR = "/home/ridderadmin/Ridder-Field/phase2/class/output/solver"

# Fixed model
FIXED = {
    "n_tail": 1.0, "n_shelf": 3.0, "alpha_tail": 1.0, "theta_i": 2.5,
    "theta_EDE_low": 0.5, "theta_EDE_high": 3.5, "sigma_EDE": 0.5,
    "m_axion": 7e4, "ridder_f": 7.305e26, "ridder_c_slow": 0.0, "beta_ridder": 0.0,
}

# Grid
LAMBDA_VALUES = [18, 20, 22, 24, 26, 28, 30, 32]
F_VALUES = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45]


def create_ini(lt, fa, root):
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
"""


def run_class(ini_path):
    result = subprocess.run(["./class", ini_path], cwd=CLASS_DIR, 
                          capture_output=True, text=True, timeout=600)
    return result.returncode == 0


def extract(label):
    try:
        bg = np.loadtxt(f"{OUTPUT_DIR}/{label}00_background.dat")
        cl = np.loadtxt(f"{OUTPUT_DIR}/{label}00_cl.dat")
        pk = np.loadtxt(f"{OUTPUT_DIR}/{label}00_pk.dat")
        lcdm_bg = np.loadtxt(f"{OUTPUT_DIR}/lcdm00_background.dat")
        lcdm_cl = np.loadtxt(f"{OUTPUT_DIR}/lcdm00_cl.dat")
        
        z, H, rho_r, rho_tot, D, p_r = bg[:,0], bg[:,3], bg[:,14], bg[:,19], bg[:,4], bg[:,15]
        f_r = rho_r / rho_tot
        idx_max = np.argmax(f_r)
        f_EDE, z_peak = float(f_r[idx_max]), float(z[idx_max])
        
        idx_0 = np.argmin(np.abs(z))
        H0 = float(H[idx_0] * 299792.458)
        
        w = p_r / rho_r
        w_z0 = float(np.interp(0.0, z[::-1], w[::-1]))
        w_z2 = float(np.interp(2.0, z[::-1], w[::-1]))
        
        # S8
        k, Pk = pk[:,0], pk[:,1]
        R = 8.0
        x = k * R
        W = np.where(x > 0.01, 3*(np.sin(x) - x*np.cos(x))/x**3, 1.0)
        sigma8 = float(np.sqrt(np.trapz(k**2 * Pk * W**2, k) / (2*np.pi**2)))
        S8 = float(sigma8 * np.sqrt(0.315/0.3))
        
        # BAO
        z_lcdm, D_lcdm = lcdm_bg[:,0], lcdm_bg[:,4]
        bao_035 = abs(np.interp(0.35, z[::-1], D[::-1]) - np.interp(0.35, z_lcdm[::-1], D_lcdm[::-1])) / np.interp(0.35, z_lcdm[::-1], D_lcdm[::-1])
        bao_057 = abs(np.interp(0.57, z[::-1], D[::-1]) - np.interp(0.57, z_lcdm[::-1], D_lcdm[::-1])) / np.interp(0.57, z_lcdm[::-1], D_lcdm[::-1])
        
        # CMB RMS
        ell, TT = cl[:,0], cl[:,1]
        ell_l, TT_l = lcdm_cl[:,0], lcdm_cl[:,1]
        mask = (ell >= 30) & (ell <= 2000)
        TT_i = np.interp(ell[mask], ell, TT)
        TT_l_i = np.interp(ell[mask], ell_l, TT_l)
        cmb_rms = float(np.sqrt(np.mean(((TT_i - TT_l_i)/TT_l_i)**2)))
        
        return {
            "H0": H0, "S8": S8, "f_EDE": f_EDE, "z_peak": z_peak, 
            "w_z0": w_z0, "w_z2": w_z2, "cmb_rms": cmb_rms, 
            "bao_max": float(max(bao_035, bao_057))
        }
    except Exception as e:
        print(f"  Error: {e}")
        return None


def classify(m, c):
    A = c["H0_min"] <= m["H0"] <= c["H0_max"] and c["S8_min"] <= m["S8"] <= c["S8_max"]
    B = c["f_EDE_min"] <= m["f_EDE"] <= c["f_EDE_max"] and c["z_peak_min"] <= m["z_peak"] <= c["z_peak_max"]
    C = m["cmb_rms"] <= c["CMB_RMS_max"] and m["bao_max"] <= c["BAO_max"]
    D = abs(m["w_z0"] + 1) <= c["w_z0_dev_max"] and c["w_z2_min"] <= m["w_z2"] <= c["w_z2_max"]
    
    if A and B and C and D:
        return "VIABLE", A, B, C, D
    elif A:
        return "TENSION_ONLY", A, B, C, D
    else:
        return "RULED_OUT", A, B, C, D


# CONSTRAINT SETS
RELAXED_B = {
    "H0_min": 71.0, "H0_max": 74.0, "S8_min": 0.70, "S8_max": 0.78,
    "f_EDE_min": 0.05, "f_EDE_max": 0.35,  # RELAXED from 0.25
    "z_peak_min": 3000.0, "z_peak_max": 5000.0,
    "CMB_RMS_max": 0.20, "BAO_max": 0.03,
    "w_z0_dev_max": 0.01, "w_z2_min": -1.02, "w_z2_max": -0.95,
}

RELAXED_BD = {
    "H0_min": 71.0, "H0_max": 74.0, "S8_min": 0.70, "S8_max": 0.78,
    "f_EDE_min": 0.05, "f_EDE_max": 0.35,  # RELAXED
    "z_peak_min": 2000.0, "z_peak_max": 6000.0,  # RELAXED
    "CMB_RMS_max": 0.20, "BAO_max": 0.05,  # SLIGHTLY RELAXED
    "w_z0_dev_max": 0.10, "w_z2_min": -1.20, "w_z2_max": -0.70,  # RELAXED
}


def main():
    print("=" * 70)
    print("RELAXED CONSTRAINT SCAN")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Collect results
    all_results = []
    total = len(LAMBDA_VALUES) * len(F_VALUES)
    count = 0
    
    print(f"\nRunning {total} points...")
    for lt in LAMBDA_VALUES:
        for fa in F_VALUES:
            count += 1
            label = f"L{lt}_f{int(fa*100):02d}"
            root = f"{OUTPUT_DIR}/{label}"
            ini = f"{root}.ini"
            
            with open(ini, "w") as f:
                f.write(create_ini(lt, fa, root))
            
            if not run_class(ini):
                print(f"[{count}/{total}] L={lt} f={fa:.2f}: FAILED")
                continue
            
            m = extract(label)
            if m is None:
                continue
            
            m["Lambda"] = lt
            m["f_axion"] = fa
            all_results.append(m)
            
            print(f"[{count}/{total}] L={lt} f={fa:.2f}: H0={m['H0']:.1f} S8={m['S8']:.2f} "
                  f"f_EDE={m['f_EDE']:.2f} w0={m['w_z0']:.2f} w2={m['w_z2']:.2f}")
    
    # =========================================
    # SCENARIO 1: RELAXED B
    # =========================================
    print("\n" + "=" * 70)
    print("SCENARIO 1: RELAXED B (f_EDE up to 0.35)")
    print("=" * 70)
    print(f"Constraints: f_EDE <= 0.35, w(0) ~ -1 +/- 0.01, w(2) in [-1.02, -0.95]")
    
    viable_B = []
    tension_B = []
    
    for m in all_results:
        status, A, B, C, D = classify(m, RELAXED_B)
        if status == "VIABLE":
            viable_B.append(m)
        elif status == "TENSION_ONLY":
            tension_B.append((m, B, C, D))
    
    print(f"\nVIABLE: {len(viable_B)}")
    print(f"TENSION_ONLY: {len(tension_B)}")
    
    if viable_B:
        print("\n--- VIABLE POINTS ---")
        for v in sorted(viable_B, key=lambda x: x["H0"], reverse=True):
            print(f"  L={v['Lambda']:2} f={v['f_axion']:.2f}: H0={v['H0']:.1f} S8={v['S8']:.2f} "
                  f"f_EDE={v['f_EDE']:.2f} w0={v['w_z0']:.2f}")
    
    if tension_B and not viable_B:
        print("\n--- TENSION_ONLY (helps H0/S8 but fails elsewhere) ---")
        for t, B, C, D in sorted(tension_B, key=lambda x: x[0]["H0"], reverse=True)[:5]:
            fails = []
            if not B: fails.append(f"EDE(f={t['f_EDE']:.2f})")
            if not C: fails.append(f"CMB/BAO")
            if not D: fails.append(f"w(z)")
            print(f"  L={t['Lambda']:2} f={t['f_axion']:.2f}: H0={t['H0']:.1f} S8={t['S8']:.2f} - Fails: {', '.join(fails)}")
    
    # =========================================
    # SCENARIO 2: RELAXED B+D
    # =========================================
    print("\n" + "=" * 70)
    print("SCENARIO 2: RELAXED B+D (f_EDE up to 0.35, relaxed w(z))")
    print("=" * 70)
    print(f"Constraints: f_EDE <= 0.35, w(0) ~ -1 +/- 0.10, w(2) in [-1.20, -0.70]")
    print(f"             BAO <= 5%")
    
    viable_BD = []
    tension_BD = []
    
    for m in all_results:
        status, A, B, C, D = classify(m, RELAXED_BD)
        if status == "VIABLE":
            viable_BD.append(m)
        elif status == "TENSION_ONLY":
            tension_BD.append((m, B, C, D))
    
    print(f"\nVIABLE: {len(viable_BD)}")
    print(f"TENSION_ONLY: {len(tension_BD)}")
    
    if viable_BD:
        print("\n--- VIABLE POINTS ---")
        print(f"{'L':>3} {'f':>5} {'H0':>6} {'S8':>5} {'f_EDE':>6} {'w(0)':>6} {'w(2)':>6} {'CMB%':>5} {'BAO%':>5}")
        for v in sorted(viable_BD, key=lambda x: x["H0"], reverse=True):
            print(f"{v['Lambda']:>3} {v['f_axion']:>5.2f} {v['H0']:>6.1f} {v['S8']:>5.2f} "
                  f"{v['f_EDE']:>6.2f} {v['w_z0']:>6.2f} {v['w_z2']:>6.2f} "
                  f"{v['cmb_rms']*100:>5.1f} {v['bao_max']*100:>5.1f}")
        
        best = max(viable_BD, key=lambda x: x["H0"])
        print(f"\n*** BEST VIABLE ***")
        print(f"  Lambda_tail = {best['Lambda']} meV")
        print(f"  f_axion = {best['f_axion']:.2f}")
        print(f"  H0 = {best['H0']:.1f} km/s/Mpc")
        print(f"  S8 = {best['S8']:.2f}")
        print(f"  f_EDE = {best['f_EDE']:.2f}")
        print(f"  w(z=0) = {best['w_z0']:.3f}")
        print(f"  w(z=2) = {best['w_z2']:.3f}")
        print(f"  CMB_RMS = {best['cmb_rms']*100:.1f}%")
        print(f"  BAO = {best['bao_max']*100:.1f}%")
    
    if tension_BD and not viable_BD:
        print("\n--- TENSION_ONLY ---")
        for t, B, C, D in sorted(tension_BD, key=lambda x: x[0]["H0"], reverse=True)[:5]:
            fails = []
            if not B: fails.append(f"EDE")
            if not C: fails.append(f"CMB/BAO(cmb={t['cmb_rms']*100:.0f}%,bao={t['bao_max']*100:.0f}%)")
            if not D: fails.append(f"w(z)")
            print(f"  L={t['Lambda']:2} f={t['f_axion']:.2f}: H0={t['H0']:.1f} S8={t['S8']:.2f} - Fails: {', '.join(fails)}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"With strict constraints (f_EDE<=0.25, w~-1): 0 viable")
    print(f"With relaxed B (f_EDE<=0.35): {len(viable_B)} viable")
    print(f"With relaxed B+D (f_EDE<=0.35, relaxed w): {len(viable_BD)} viable")
    print("=" * 70)


if __name__ == "__main__":
    main()

