# ACT DR6 Analysis Playbook

**Last Updated**: 2025-12-02  
**Status**: Production-ready configuration and constraints

This document provides the **canonical, non-negotiable rules** for ACT+Planck+EDE analysis configs. All lessons learned from debugging (Issues 1-7) are incorporated here.

---

## Hard Constraints: "Do Not Touch" Contract

### 1. CLASS Binary

- **Always use** the custom Ridder CLASS shared object that is already copied into `~/.local/lib/python3.10/site-packages/`.
- **Never reinstall** `classy` from pip or change the CLASS path.
- If you touch the Python environment, you **must preserve** this shared object.

### 2. Output String

- In every config, `theory.classy.extra_args.output` must be **exactly**:
  ```yaml
  output: tCl pCl lCl
  ```
- Use **spaces, not commas**. Do not add or remove entries.
- **Rationale**: Cobaya's classy wrapper mangles comma-separated strings (Issue #1).

### 3. Legal CLASS Accuracy Knobs

**Allowed** in `extra_args`:
- `output, l_max_scalars, lensing, gauge, N_ncdm, non_linear`
- `accurate_lensing, l_logstep, l_linstep, k_max_tau0_over_l_max`
- `tol_background_integration, tol_thermo_integration`
- Ridder field shape parameters: `f_axion_ridder, theta_i_ridder, beta_ridder, n_ridder`

**Disallowed**: CAMB-style parameters such as:
- `perturb_sampling_stepsize`
- `tol_perturb_integration`
- `tol_perturb_integration_ls`
- Or anything similar

**Rationale**: CLASS doesn't recognize CAMB parameter names (Issue #6).

### 4. Parameters Routed into CLASS

- **For ΛCDM**, `theory.classy.input_params` must be:
  ```yaml
  input_params: [A_s, n_s, H0, omega_b, omega_cdm, tau_reio]
  ```

- **For EDE**, it must be:
  ```yaml
  input_params: [A_s, n_s, H0, omega_b, omega_cdm, tau_reio, Lambda_EDE_ridder]
  ```

- **Do not add** foreground or calibration parameters to `input_params`. They belong only in `params`, not in the CLASS call.

**Rationale**: Foreground parameters cause CLASS errors (Issue #2).

### 5. Ridder EDE Knobs

- The **only EDE parameter** that floats in ACT runs is `Lambda_EDE_ridder`.
- The shape parameters are **fixed** in `extra_args` and must stay fixed:
  ```yaml
  f_axion_ridder: 1.0e27
  theta_i_ridder: 1.0
  beta_ridder: 0.0
  n_ridder: 3
  ```
- **Do not promote** these to free parameters in ACT configs.
- **Do not delete** them.

### 6. Λ Prior Regime

- For ACT runs, use the **tight prior**:
  ```yaml
  Lambda_EDE_ridder:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.1}
    proposal: 0.05
  ```
- **Do not widen** this prior and **do not shift** it away from 1.0.
- Wider priors land in the wrong z-osc regime and destroy the shoulder (Issue #5).

### 7. Likelihood Stack

- For ACT+Planck analysis, always include:
  - `planck_2018_lowl.TT`
  - `planck_2018_lowl.EE`
  - `planck_2018_highl_plik.TTTEEE`
  - `planck_2018_lensing.clik`
  - `act_dr6_mflike.ACTDR6MFLike`
- BAO and SH0ES may be present or absent, but **do not "fix" issues** by silently stripping Planck or ACT.

### 8. ACT Calibration and Foreground Parameters

- Calibration and E-calibration parameters (`cal*`, `calE*`) live only in `params` with tight Gaussian priors centered at 1.0.
- Foreground parameters like `a_cibc, a_dust_tt, a_dust_ee, a_radio` should **not be defined at all** in ACT configs. Planck can use its own defaults.

### 9. Template Fit Units

- In any code that converts CLASS `C_ell` into the ACT bandpower space, you **must convert** to `D_ell` in μK² using:
  ```python
  T_CMB = 2.7255e6  # μK
  D_ell = ell*(ell+1)/(2*π) * C_ell * T_CMB**2
  ```
- **Do not fit templates** using raw dimensionless `C_ell`.

**Rationale**: Missing T_CMB² conversion produces garbage results (Issue #4).

### 10. High-ℓ Ridder Numerical Behaviour

- **Do not "fix"** silent hangs by changing `gauge`, deleting EDE parameters, or adding random accuracy knobs.
- Hangs at high `l_max_scalars` reflect a **numerical issue in the Ridder field implementation**, not a YAML configuration problem (Issue #7).
- If you must adjust `l_max_scalars` in a config, respect the production choice (`≈ 8500`) and propose changes only in a separate, clearly marked test config, not in the production files.

---

## Production Config Skeleton

### Theory Block (Shared)

```yaml
theory:
  classy:
    extra_args:
      # Output - NO COMMAS (space-separated only)
      output: tCl pCl lCl
      
      # ACT requires high ℓ_max for damping tail
      l_max_scalars: 8500
      
      # Standard CLASS settings
      lensing: yes
      gauge: newtonian
      N_ncdm: 0
      non_linear: none
      
      # Accuracy settings (CLASS-safe only)
      accurate_lensing: 1
      l_logstep: 1.035
      l_linstep: 25
      k_max_tau0_over_l_max: 2.5
      tol_background_integration: 1e-6
      tol_thermo_integration: 1e-6
      
      # Ridder field shape (needed for EDE; harmless at Lambda=0)
      f_axion_ridder: 1.0e27
      theta_i_ridder: 1.0
      beta_ridder: 0.0
      n_ridder: 3
    
    # For ΛCDM config:
    input_params: [A_s, n_s, H0, omega_b, omega_cdm, tau_reio]
    
    # For EDE config, add Lambda_EDE_ridder:
    # input_params: [A_s, n_s, H0, omega_b, omega_cdm, tau_reio, Lambda_EDE_ridder]
  
  # ACT foreground theory
  mflike.BandpowerForeground:
    experiments:
      - dr6_pa4_f220
      - dr6_pa5_f090
      - dr6_pa5_f150
      - dr6_pa6_f090
      - dr6_pa6_f150
    bandint_freqs: [220, 90, 150, 90, 150]
    beam_profile:
      beam_from_file: null
```

### Likelihood Block

```yaml
likelihood:
  # CMB - Planck 2018
  planck_2018_lowl.TT: null
  planck_2018_lowl.EE: null
  planck_2018_highl_plik.TTTEEE: null
  planck_2018_lensing.clik: null
  
  # ACT DR6 high-ℓ TT/TE/EE (damping tail)
  act_dr6_mflike.ACTDR6MFLike:
    stop_at_error: false
  
  # Optional distance ladder or BAO:
  # shoes_h0:
  #   external: "lambda H0: -0.5*((H0 - 73.04)/1.04)**2"
  #   output_params: [chi2__shoes_h0]
  # bao.sixdf_2011_bao: null
  # bao.sdss_dr7_mgs: null
  # bao.sdss_dr12_consensus_bao: null
```

### Parameters Block

#### Base ΛCDM Parameters

```yaml
params:
  # Base ΛCDM (k=6) - CLASS parameterization
  logA:
    prior: {min: 2.5, max: 3.7}
    ref: {dist: norm, loc: 3.05, scale: 0.02}
    proposal: 0.01
    drop: true
  A_s:
    value: "lambda logA: 1e-10*np.exp(logA)"
    latex: A_s
  n_s:
    prior: {min: 0.92, max: 1.02}
    ref: {dist: norm, loc: 0.97, scale: 0.01}
    proposal: 0.002
    latex: n_s
  H0:
    prior: {min: 60.0, max: 80.0}
    ref: {dist: norm, loc: 69.0, scale: 2.0}
    proposal: 0.2
    latex: H_0
  omega_b:
    prior: {min: 0.020, max: 0.025}
    ref: {dist: norm, loc: 0.0224, scale: 0.0005}
    proposal: 5e-5
    latex: \Omega_b h^2
  omega_cdm:
    prior: {min: 0.10, max: 0.14}
    ref: {dist: norm, loc: 0.120, scale: 0.005}
    proposal: 5e-4
    latex: \Omega_c h^2
  tau_reio:
    prior: {min: 0.03, max: 0.10}
    ref: {dist: norm, loc: 0.055, scale: 0.01}
    proposal: 0.005
    latex: \tau_{reio}
```

#### EDE Parameter (EDE configs only)

```yaml
  # EDE amplitude - tight prior for correct z_osc regime
  Lambda_EDE_ridder:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.1}
    proposal: 0.05
    latex: \Lambda_{EDE}
```

#### Planck Nuisance Parameters

```yaml
  # Planck nuisance parameters
  A_planck:
    prior: {dist: norm, loc: 1.0, scale: 0.0025}
    ref: 1.0
    proposal: 0.001
    latex: A_\mathrm{planck}
  calib_100T:
    prior: {dist: norm, loc: 1.0002, scale: 0.0007}
    ref: 1.0002
    proposal: 0.0003
  calib_217T:
    prior: {dist: norm, loc: 0.99805, scale: 0.00065}
    ref: 0.99805
    proposal: 0.0003

  # Planck foreground (plik defaults)
  A_cib_217:
    prior: {min: 0, max: 200}
    ref: 47
    proposal: 5
  xi_sz_cib:
    prior: {min: 0, max: 1}
    ref: 0.5
    proposal: 0.1
  A_sz:
    prior: {min: 0, max: 10}
    ref: 5
    proposal: 1
  ksz_norm:
    prior: {min: 0, max: 10}
    ref: 3
    proposal: 1
  gal545_A_100:
    prior: {min: 0, max: 50}
    ref: 8
    proposal: 2
  gal545_A_143:
    prior: {min: 0, max: 50}
    ref: 10
    proposal: 2
  gal545_A_143_217:
    prior: {min: 0, max: 100}
    ref: 20
    proposal: 4
  gal545_A_217:
    prior: {min: 0, max: 400}
    ref: 100
    proposal: 10
  ps_A_100_100:
    prior: {min: 0, max: 400}
    ref: 250
    proposal: 20
  ps_A_143_143:
    prior: {min: 0, max: 400}
    ref: 50
    proposal: 10
  ps_A_143_217:
    prior: {min: 0, max: 400}
    ref: 50
    proposal: 10
  ps_A_217_217:
    prior: {min: 0, max: 400}
    ref: 120
    proposal: 10
  galf_TE_A_100:
    prior: {min: 0, max: 1}
    ref: 0.1
    proposal: 0.05
  galf_TE_A_100_143:
    prior: {min: 0, max: 1}
    ref: 0.1
    proposal: 0.05
  galf_TE_A_100_217:
    prior: {min: 0, max: 1}
    ref: 0.4
    proposal: 0.1
  galf_TE_A_143:
    prior: {min: 0, max: 1}
    ref: 0.2
    proposal: 0.05
  galf_TE_A_143_217:
    prior: {min: 0, max: 1}
    ref: 0.6
    proposal: 0.1
  galf_TE_A_217:
    prior: {min: 0, max: 10}
    ref: 2
    proposal: 0.5
```

#### ACT Calibration Parameters

```yaml
  # ACT calibration - tight priors around 1
  calG_all:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.01}
    proposal: 0.005
  cal_dr6_pa4_f220:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.02}
    proposal: 0.01
  cal_dr6_pa5_f090:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.02}
    proposal: 0.01
  cal_dr6_pa5_f150:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.02}
    proposal: 0.01
  cal_dr6_pa6_f090:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.02}
    proposal: 0.01
  cal_dr6_pa6_f150:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.02}
    proposal: 0.01
  calE_dr6_pa4_f220:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.02}
    proposal: 0.01
  calE_dr6_pa5_f090:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.02}
    proposal: 0.01
  calE_dr6_pa5_f150:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.02}
    proposal: 0.01
  calE_dr6_pa6_f090:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.02}
    proposal: 0.01
  calE_dr6_pa6_f150:
    prior: {min: 0.8, max: 1.2}
    ref: {dist: norm, loc: 1.0, scale: 0.02}
    proposal: 0.01

  # ACT foreground parameters
  bandint_shift_dr6_pa4_f220:
    prior: {dist: norm, loc: 0.0, scale: 3.6}
    ref: 0.0
    proposal: 1.8
  bandint_shift_dr6_pa5_f090:
    prior: {dist: norm, loc: 0.0, scale: 1.0}
    ref: 0.0
    proposal: 0.5
  bandint_shift_dr6_pa5_f150:
    prior: {dist: norm, loc: 0.0, scale: 1.3}
    ref: 0.0
    proposal: 0.65
  bandint_shift_dr6_pa6_f090:
    prior: {dist: norm, loc: 0.0, scale: 1.2}
    ref: 0.0
    proposal: 0.6
  bandint_shift_dr6_pa6_f150:
    prior: {dist: norm, loc: 0.0, scale: 1.1}
    ref: 0.0
    proposal: 0.55
```

#### Derived Parameters

```yaml
  # Derived
  Omega_m:
    latex: \Omega_m
  sigma8:
    latex: \sigma_8
  S8:
    derived: "lambda sigma8, Omega_m: sigma8*np.sqrt(Omega_m/0.3)"
    latex: S_8
  rs_drag:
    derived: true
    latex: r_s
```

### Sampler Block

```yaml
sampler:
  mcmc:
    Rminus1_stop: 0.02
    Rminus1_cl_stop: 0.1
    # NOTE: covmat: null if xi_sz_cib (Planck) and xi (ACT) conflict
    # Otherwise use: covmat: auto
    covmat: null  # or auto if no parameter name conflicts
    burn_in: 0.4
    max_tries: 5000  # Increased for EDE (CLASS hangs on some param combos)
    drag: true
    proposal_scale: 2.0
    learn_proposal: true

output: chains/act_world_lcdm  # or chains/act_world_ede
resume: true
```

---

## Known Issues and Workarounds

### Issue #7: CLASS Ridder Field Hangs at High l_max

**Symptom**: EDE chains hang during "Getting initial point" phase.

**Root Cause**: CLASS Ridder field implementation has a numerical stability bug when computing high-l spectra (l_max >= 1000) with EDE enabled.

**Workaround**: 
1. Provide a good starting point (e.g., LCDM best-fit + Lambda_EDE_ridder=1.0)
2. Or reduce `l_max_scalars` temporarily for initial point search, then increase once chain starts

**Do NOT**: Try to "fix" this by changing `gauge`, deleting EDE parameters, or adding random accuracy knobs. This is a C code bug, not a YAML problem.

### Parameter Name Conflicts

**Issue**: `xi_sz_cib` (Planck) and `xi` (ACT) have duplicate aliases, causing `covmat: auto` to fail.

**Fix**: Use `covmat: null` in sampler settings.

---

## Memory Constraints

- Each ACT world chain uses **~6-8GB RAM**.
- With 15GB total system RAM, run **maximum 2 chains simultaneously** to avoid OOM kills.
- Current production configs use `l_max_scalars: 8500` (reduced from 9000 to save memory).

---

## Quick Reference: What NOT to Do

1. ❌ Use commas in `output: tCl, pCl, lCl` → Use spaces
2. ❌ Add CAMB-style accuracy parameters → Only use CLASS knobs
3. ❌ Route foreground params to CLASS → Use `input_params` explicitly
4. ❌ Widen Lambda prior beyond `[0.8, 1.2]` → Keeps correct z_osc regime
5. ❌ Remove `planck_2018_lensing.clik` → Include it in likelihood stack
6. ❌ Fit templates with raw `C_ell` → Convert to `D_ell` with T_CMB²
7. ❌ Try to "fix" CLASS hangs by changing config → It's a C code bug
8. ❌ Reinstall `classy` from pip → Preserve custom Ridder CLASS

---

## Related Documents

- `ACT_ANALYSIS_README.md` - Overview of two-track analysis approach
- `ACT_LIKELIHOOD_DEBUG.md` - Detailed debugging log (Issues 1-7)
- `configs/act_world_lcdm.yaml` - Production ΛCDM config
- `configs/act_world_ede.yaml` - Production EDE config

---

**Last Updated**: 2025-12-02  
**Maintainer**: See git history for changes
