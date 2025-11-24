#!/usr/bin/env python3
"""Scan Lambda_tail to check robustness of Track 2 model."""
import numpy as np
import subprocess
import os

def run_and_measure(lambda_tail):
    # Create temp INI
    with open("temp_scan.ini", "w") as f:
        f.write(f"""# Temp scan
H0 = 67.36
omega_b = 0.02238280
omega_cdm = 0.1201075
A_s = 2.098900e-09
n_s = 0.965952
tau_reio = 0.05430842
gauge = newtonian

use_ridder = yes
ridder_model_type = unified
ridder_use_tail = yes
ridder_use_shelf = no
ridder_use_plateau = no
ridder_Lambda_tail_eV = {lambda_tail}
ridder_n_tail = 1.0
ridder_alpha_tail = 1.0
theta_i_ridder = 0.5
ridder_f = 1.0e26
beta_ridder = 0.0
ridder_c_slow = 1.0

output = mPk
write background = yes
root = output/scan_
tol_background_integration = 1e-5
""")
    
    # Clear old outputs
    import glob
    for f in glob.glob("output/scan_*"):
        os.remove(f)
    
    # Run CLASS
    result = subprocess.run(
        ["./phase2/class/class", "temp_scan.ini"],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        return None, None, None
    
    # Find output files (CLASS adds suffix)
    bg_files = glob.glob("output/scan_*background.dat")
    pk_files = glob.glob("output/scan_*pk.dat")
    if not bg_files or not pk_files:
        return None, None, None
    
    bg = np.loadtxt(bg_files[0])
    pk = np.loadtxt([f for f in pk_files if "_cb" not in f][0])
    
    k, Pk = pk[:, 0], pk[:, 1]
    R = 8.0; x = k * R
    W = 3.0 * (np.sin(x) - x * np.cos(x)) / x**3
    W[x < 0.01] = 1.0
    sigma8 = np.sqrt(np.trapz(Pk * W**2 * k**2, k) / (2 * np.pi**2))
    
    H0 = bg[-1, 3] * 299792.458
    rho_b, rho_cdm = bg[-1, 9], bg[-1, 10]
    rho_crit = bg[-1, 13]
    Omega_m = (rho_b + rho_cdm) / rho_crit
    S8 = sigma8 * np.sqrt(Omega_m / 0.3)
    
    return H0, S8, Omega_m

# Scan Lambda_tail
baseline = 1.6e-3
lambdas = [baseline * 0.8, baseline * 0.9, baseline, baseline * 1.1, baseline * 1.2]

print("=" * 70)
print("LAMBDA_TAIL SCAN - Robustness Check")
print("=" * 70)
print(f"{'Lambda_tail':<15} {'H0':>10} {'S8':>10} {'Omega_m':>10}")
print("-" * 70)

for lam in lambdas:
    H0, S8, Om = run_and_measure(lam)
    if H0:
        mark = " <-- baseline" if abs(lam - baseline) < 1e-6 else ""
        print(f"{lam:.2e}       {H0:8.2f}   {S8:8.4f}   {Om:8.4f}{mark}")
    else:
        print(f"{lam:.2e}       FAILED")

print("=" * 70)
print("\nConclusion: If S8 stays in 0.74-0.77 range across Lambda_tail,")
print("the model is not finely tuned.")

