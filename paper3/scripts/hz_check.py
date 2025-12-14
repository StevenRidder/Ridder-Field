from classy import Class

lcdm_params = {
    "h": 0.6777,
    "omega_b": 0.02237,
    "omega_cdm": 0.1200,
    "tau_reio": 0.0544,
    "A_s": 2.1e-9,
    "n_s": 0.9649,
    "N_ur": 2.0328,
    "N_ncdm": 1,
    "m_ncdm": 0.06,
    "xi_late": 0.0,
    "output": "mPk",
    "P_k_max_h/Mpc": 1,
}

xi_params = lcdm_params.copy()
xi_params["xi_late"] = 0.05

cosmo_lcdm = Class()
cosmo_lcdm.set(lcdm_params)
cosmo_lcdm.compute()

cosmo_xi = Class()
cosmo_xi.set(xi_params)
cosmo_xi.compute()

print("H(z) COMPARISON")
print("z       H_LCDM      H_xi        dH/H(%)")
for z in [0.0, 0.2, 0.5, 1.0, 2.0, 10.0]:
    H_lcdm = cosmo_lcdm.Hubble(z) * 299792.458
    H_xi = cosmo_xi.Hubble(z) * 299792.458
    dH = (H_xi - H_lcdm) / H_lcdm * 100
    print(f"{z:<8.1f}{H_lcdm:<12.4f}{H_xi:<12.4f}{dH:<12.4f}")

print("")
print("Omega_m: LCDM={:.5f} xi={:.5f}".format(cosmo_lcdm.Omega_m(), cosmo_xi.Omega_m()))
print("sigma8:  LCDM={:.5f} xi={:.5f}".format(cosmo_lcdm.sigma8(), cosmo_xi.sigma8()))
print("r_s:     LCDM={:.5f} xi={:.5f}".format(cosmo_lcdm.rs_drag(), cosmo_xi.rs_drag()))
