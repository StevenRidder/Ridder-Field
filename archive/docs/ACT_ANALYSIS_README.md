# ACT Analysis: Two-Track Approach

This implements the complete ACT soft shoulder analysis in two tracks:

## Track 1: ACT+Planck MCMC (Consistency Check)
**Goal**: Verify that ACT doesn't immediately kill the EDE solution.

**What it does**:
- Runs combined Planck+ACT+BAO+SH0ES chains for both ΛCDM and EDE
- Gets best-fit parameters and χ² breakdown
- Answers: "Is ACT consistent with the predicted shoulder?"

**Output**: Best-fit parameters and Δχ²(ACT) = χ²_ACT(EDE) - χ²_ACT(ΛCDM)

## Track 2: Template Amplitude Measurement (Detection)
**Goal**: Measure the amplitude of the specific shoulder pattern.

**What it does**:
- Defines shoulder template: ΔC_ℓ = C_ℓ(EDE) - C_ℓ(ΛCDM) at best-fit parameters
- Fits template amplitude A_sh to ACT data: r = A_sh × t + noise
- Reports: A_sh, σ(A_sh), and S/N

**Output**: 
- A_sh = 0 → pure ΛCDM
- A_sh = 1 → Ridder field prediction
- If A_sh ≈ 1 ± 0.5 → 2σ detection!

---

## Quick Start

### Run Both Tracks:

```bash
# Deploy scripts
scp /Users/steveridder/Git/Ridder-Field/phase3/*.py /Users/steveridder/Git/Ridder-Field/phase3/*.sh \
    <VM_USER>@<VM_IP>:~/Ridder-Field/phase3/

# Run Track 1 (MCMC chains)
ssh <VM_USER>@<VM_IP> "cd ~/Ridder-Field/phase3 && bash run_act_analysis.sh"

# Monitor chains
ssh <VM_USER>@<VM_IP> "cd ~/Ridder-Field/phase3 && python3 check_chains.sh"

# Once chains converge, run Track 2 (template fit)
ssh <VM_USER>@<VM_IP> "cd ~/Ridder-Field/phase3 && python3 act_template_fit.py"
```

---

## Track 1 Details

### Configs Required:
- `configs/act_world_lcdm.yaml` - ΛCDM with ACT+Planck+BAO+SH0ES
- `configs/act_world_ede.yaml` - EDE with ACT+Planck+BAO+SH0ES

### Production ACT world configs (2025-12-01)

To stop the churn, we fix **one canonical ACT world stack** for both ΛCDM and EDE:

- **Likelihoods (no lensing block):**
  - `planck_2018_lowl.TT`
  - `planck_2018_lowl.EE`
  - `planck_2018_highl_plik.TTTEEE`
  - `act_dr6_mflike.ACTDR6MFLike`
  - `bao.sixdf_2011_bao`, `bao.sdss_dr7_mgs`, `bao.sdss_dr12_consensus_bao`
  - `shoes_h0` (Gaussian 73.04 ± 1.04 km/s/Mpc)

- **CLASS theory settings (`theory.classy.extra_args`):**
  - `output: tCl pCl lCl`  (space‑separated, **no commas**)
  - `l_max_scalars: 7000`  (ACT damping tail; reduced from 8500 to save memory)
  - `lensing: yes`, `gauge: newtonian`, `N_ncdm: 0`, `non_linear: none`
  - Accuracy: `accurate_lensing: 1`, `l_logstep: 1.04`, `l_linstep: 30`,
    `k_max_tau0_over_l_max: 2.5`,
    `tol_background_integration: 1e-5`,
    `tol_thermo_integration: 1e-5`
  - **Memory constraint:** Each ACT world chain uses ~6-8GB RAM. With 15GB total,
    run **maximum 2 chains simultaneously** to avoid OOM kills.
  - **No CAMB‑only knobs** like `perturb_sampling_stepsize`,
    `tol_perturb_integration`, `tol_perturb_integration_ls`
  - Use `input_params` so CLASS only sees true cosmological parameters:
    - ΛCDM: `[A_s, n_s, H0, omega_b, omega_cdm, tau_reio]`
    - EDE: add `Lambda_EDE_ridder`

- **Parameters and priors:**
  - Base ΛCDM: `omega_b`, `omega_cdm`, `H0`, `tau_reio`, `n_s`, `logA`
    with the priors in the Tier 10 templates (see configs).
  - EDE: add **only** `Lambda_EDE_ridder` with a physics‑motivated prior.
    - Template / “wide” prior: `{min: 0.0, max: 2.5}` (for generic scans).
    - **ACT shoulder runs:** use tight prior `{min: 0.8, max: 1.2}` to keep
      \(z_{\rm osc} \sim 4000{-}5000\) and avoid the wrong early‑EDE regime.
  - ACT calibration params (`calG_all`, `cal_dr6_*`, `calE_dr6_*`) have
    tight normal priors around 1.0 with small proposal widths.

- **Sampler (`sampler.mcmc`):**
  - `Rminus1_stop: 0.02`, `Rminus1_cl_stop: 0.1`
  - `covmat: auto`, `burn_in: 0.4`, `max_tries: 10`
  - `drag: true`, `proposal_scale: 2.0`, `learn_proposal: true`
  - Manual `blocking` is **disabled** in ACT world configs because the
    current Cobaya version on the cluster rejects the old blocking syntax.

- **Launch scripts:**
  - `run_act_analysis.sh` – legacy ACT world launcher
  - `run_tier6_act.sh` – Tier‑6 “SH0ES World + ACT” launcher using
    `tier6_lcdm_shoes_act.yaml` and `tier6_ede_shoes_act.yaml`

### What to Check:
1. **Convergence**: R-1 < 0.01, effective sample size ≥ 2000
2. **Δχ²(ACT)**: Should be small (|Δχ²| < 5) if ACT is neutral
3. **Best-fit parameters**: H₀, r_s, Λ_EDE

### Expected Results:
- If Δχ²(ACT) ≈ 0: ACT is neutral (like DESI) ✅
- If Δχ²(ACT) < -3: ACT prefers EDE! 🚀
- If Δχ²(ACT) > +5: ACT disfavors EDE ❌

---

## Track 2 Details

### Prerequisites:
- Track 1 chains must be converged
- ACT likelihood must be installed (`act_dr6_mflike`)
- CLASS with Ridder field must be available

### What It Does:

1. **Loads best-fit parameters** from Track 1 chains
2. **Computes C_ℓ spectra** using CLASS:
   - C_ℓ(ΛCDM) at LCDM best-fit
   - C_ℓ(EDE) at EDE best-fit
3. **Defines template**: ΔC_ℓ = C_ℓ(EDE) - C_ℓ(ΛCDM)
4. **Applies ACT windows** to convert to bandpowers
5. **Fits amplitude** using optimal linear estimator:
   ```
   A_sh = (t^T C^{-1} r) / (t^T C^{-1} t)
   σ(A_sh) = 1 / sqrt(t^T C^{-1} t)
   S/N = A_sh / σ(A_sh)
   ```

### Interpretation:

| A_sh | σ(A_sh) | S/N | Meaning |
|------|---------|-----|---------|
| 1.0 | 0.3 | 3.3 | **Strong detection!** |
| 0.8 | 0.5 | 1.6 | Hint of shoulder |
| 0.2 | 0.8 | 0.25 | Consistent but not detected |
| 0.0 | 0.5 | 0.0 | Pure ΛCDM |
| -0.5 | 0.4 | -1.25 | ACT disfavors pattern |

---

## Files

- `run_act_analysis.sh` - Master script to start Track 1
- `act_template_fit.py` - Track 2: Template amplitude fit
- `check_chains.sh` - Monitor chain progress
- `configs/act_world_lcdm.yaml` - Track 1 LCDM config
- `configs/act_world_ede.yaml` - Track 1 EDE config

---

## Paper Integration

Once you have results:

### Track 1 Results:
> "We run combined Planck+ACT+BAO+SH0ES chains for both ΛCDM and EDE. 
> The ACT contribution to Δχ² is [value], indicating [interpretation]."

### Track 2 Results:
> "We define a shoulder template as the difference between EDE and ΛCDM 
> spectra at the Planck+BAO+SH0ES best fits. Fitting the template amplitude 
> to ACT DR6 data gives A_sh = [value] ± [error] (S/N = [value]). 
> This [detects/hints at/is consistent with] the predicted soft shoulder pattern."

---

## Troubleshooting

**Chains not starting?**
- Check configs exist: `ls configs/act_world*.yaml`
- Check ACT likelihood installed: `python3 -c "from act_dr6_mflike import ACTDR6MFLike"`

**Template fit fails?**
- Ensure Track 1 chains are converged
- Check ACT data extraction works
- Verify CLASS with Ridder field is available

**Need faster results?**
- Reduce `max_samples` in configs
- Relax `Rminus1_stop` to 0.05
- Use `burn_in: 50` and `learn_proposal: false`
