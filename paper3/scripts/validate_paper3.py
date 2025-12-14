from classy import Class
import numpy as np

print("="*70)
print("PAPER 3 VALIDATION BATTERY")
print("="*70)

# Base LCDM params
base = {
    "h": 0.6736,
    "omega_b": 0.02237,
    "omega_cdm": 0.1200,
    "tau_reio": 0.0544,
    "A_s": 2.1e-9,
    "n_s": 0.9649,
    "N_ur": 2.0328,
    "N_ncdm": 1,
    "m_ncdm": 0.06,
    "output": "mPk tCl",
    "P_k_max_h/Mpc": 1,
    "z_pk": 0,
    "l_max_scalars": 2600,
}

#=== TEST 1: LCDM Reproduction ===
print("\n### TEST 1: LCDM Reproduction ###")
cosmo = Class()
cosmo.set({**base, "xi_late": 0.0})
cosmo.compute()
H0 = cosmo.Hubble(0) * 299792.458
Om = cosmo.Omega_m()
sig8 = cosmo.sigma8()
age = cosmo.age()
rs = cosmo.rs_drag()
print(f"  H0 = {H0:.2f} km/s/Mpc (Planck: 67.36)")
print(f"  Omega_m = {Om:.4f} (Planck: 0.315)")
print(f"  sigma8 = {sig8:.4f} (Planck: 0.811)")
print(f"  Age = {age:.2f} Gyr (Planck: 13.79)")
print(f"  r_s = {rs:.2f} Mpc (Planck: 147.09)")
if abs(H0 - 67.36) > 0.5:
    print("  WARNING: H0 mismatch")
else:
    print("  PASS: H0 matches")
cosmo.struct_cleanup()
cosmo.empty()

#=== TEST 4: Sound Horizon Preservation ===
print("\n### TEST 4: Sound Horizon Preservation ###")
rs_vals = []
for xi in [0.0, 0.05, 0.10]:
    cosmo = Class()
    cosmo.set({**base, "xi_late": xi})
    cosmo.compute()
    rs = cosmo.rs_drag()
    rs_vals.append(rs)
    print(f"  xi_late={xi:.2f}: r_s = {rs:.4f} Mpc")
    cosmo.struct_cleanup()
    cosmo.empty()
if max(rs_vals) - min(rs_vals) < 0.01:
    print("  PASS: r_s unchanged")
else:
    print("  FAIL: r_s changed!")

#=== TEST 17: Coupling Sign Verification ===
print("\n### TEST 17: Coupling Sign Verification ###")
om_vals = {}
for xi in [-0.10, 0.0, 0.05, 0.10]:
    cosmo = Class()
    cosmo.set({**base, "xi_late": xi})
    cosmo.compute()
    Om = cosmo.Omega_m()
    om_vals[xi] = Om
    print(f"  xi_late={xi:+.2f}: Omega_m = {Om:.4f}")
    cosmo.struct_cleanup()
    cosmo.empty()
if om_vals[0.10] < om_vals[0.0] < om_vals[-0.10]:
    print("  PASS: Coupling sign correct (positive xi reduces Omega_m)")
else:
    print("  FAIL: Coupling sign wrong!")

#=== TEST: xi_late Background Effect ===
print("\n### TEST: xi_late Background + S8 Effect ###")
for xi in [0.0, 0.05, 0.10]:
    cosmo = Class()
    cosmo.set({**base, "xi_late": xi})
    cosmo.compute()
    H0 = cosmo.Hubble(0) * 299792.458
    H05 = cosmo.Hubble(0.5) * 299792.458
    Om = cosmo.Omega_m()
    sig8 = cosmo.sigma8()
    S8 = sig8 * (Om/0.3)**0.5
    print(f"  xi={xi:.2f}: H0={H0:.2f}, H(0.5)={H05:.2f}, Om={Om:.4f}, sig8={sig8:.4f}, S8={S8:.4f}")
    cosmo.struct_cleanup()
    cosmo.empty()

print("\n" + "="*70)
print("VALIDATION COMPLETE")
print("="*70)
