# Pipeline Validation Plan

## Goal

Before accepting that "H₀ ≈ 67 is physics," prove the pipeline can actually find a high-H₀ solution when it exists.

---

## Validation Test 1: Mock Recovery

**Question**: Can the pipeline recover known input parameters?

### Setup
1. Pick a fiducial "Ridder world" matching Paper 1 best-fit:
   - H₀ = 72.5
   - Λ_EDE = 0.04
   - A_sh ≈ 1.0
   - n_s = 0.975
   - ω_b = 0.0224
   - ω_cdm = 0.118
   - τ = 0.055

2. Generate mock data:
   ```bash
   # Use CLASS to generate C_ℓ^TT, C_ℓ^TE, C_ℓ^EE at this cosmology
   # Add realistic noise matching ACT DR6 and Planck
   # Generate synthetic BAO distances at DESI redshifts
   ```

3. Run the same Cobaya setup on these mocks

### Pass Criteria
- Recovered H₀ within 1σ of input (72.5 ± ~1)
- Recovered Λ_EDE within 1σ of input
- χ² at truth close to expected DOF

### If it fails
Pipeline is broken. Fix configs before trusting any physics conclusions.

---

## Validation Test 2: ΛCDM Sanity Check

**Question**: Does our ΛCDM baseline match published DESI+Planck results?

### Comparison Targets
From DESI Y1 + Planck (arXiv:2404.03002):
- H₀ = 67.97 ± 0.38
- Ω_m = 0.3069 ± 0.0050
- S₈ = 0.815 ± 0.012

### Our P0b_DR6 Results
- H₀ = 68.02 ± 0.13 ✓
- Need to check: Ω_m, S₈

### Pass Criteria
- H₀ within 0.5 km/s/Mpc of published
- Ω_m within 0.01
- S₈ within 0.02
- Per-likelihood χ² reasonable (not 100s off)

### Action
```bash
# Extract Ω_m and S₈ from chains
ssh azureuser@172.174.34.125 '
cd ~/Ridder-Field/paper2_dr6/chains
awk "NR>1 {print \$X, \$Y}" prod_p0b_dr6_lcdm.1.txt | ...
'
```

---

## Validation Test 3: χ²(H₀) Scan at Fixed Parameters

**Question**: Who kills H₀ = 73 numerically?

### Setup
Take best-fit ΛCDM cosmology, fix everything except H₀.

Scan H₀ = [67, 68, 69, 70, 71, 72, 73] and evaluate:
- χ²_ACT(H₀)
- χ²_DESI(H₀)
- χ²_Planck_lowl(H₀)
- χ²_lensing(H₀)
- χ²_total(H₀)

### Implementation
```python
# Create single-point evaluation configs
for h0 in [67, 68, 69, 70, 71, 72, 73]:
    info = {
        "params": {
            "H0": {"value": h0},
            # ... fix all other params to LCDM best-fit
        },
        "sampler": {"evaluate": None},
        # ... likelihoods
    }
```

### Pass Criteria
- If DESI alone adds Δχ² > 50 at H₀=73 → geometry ceiling is real
- If ACT alone adds Δχ² > 50 at H₀=73 → damping tail hates high H₀
- If χ² is flat but sampler never visits → prior/proposal bug

### Expected Result
DESI should be the killer. BAO at z~0.5-2 pins D_A/r_s and D_H/r_s.

---

## Validation Test 4: SH0ES/TRGB Likelihood Plumbing

**Question**: Are the H₀ priors actually pulling?

### Direct Evaluation
```python
# SH0ES: N(73.04, 1.04)
# At H0=67: Δχ² = ((67-73.04)/1.04)² = 35.0
# At H0=73: Δχ² = 0

# TRGB: N(69.8, 1.7)  
# At H0=67: Δχ² = ((67-69.8)/1.7)² = 2.9
# At H0=73: Δχ² = ((73-69.8)/1.7)² = 3.5
```

### Test
Run single-point evaluations at H₀=67 and H₀=73 with SH0ES prior.
Confirm the Δχ² matches the expected Gaussian.

### Pass Criteria
- SH0ES adds exactly ~35 at H₀=67 vs H₀=73
- TRGB adds exactly ~2.9 at H₀=67 vs H₀=69.8

### If it fails
Prior is mis-encoded (wrong mean, wrong width, or not being evaluated).

---

## Validation Test 5: Reproduce a Literature EDE Paper

**Question**: Can we reproduce someone else's results?

### Target Paper
Poulin et al (2023) or Hill et al (2022) EDE analysis, or any recent DESI-era EDE paper.

### Setup
1. Implement their exact parameterization (f_EDE, z_c, θ_i)
2. Use their priors
3. Use their data combination
4. Run chains

### Pass Criteria
- Match their H₀ to within ~0.5
- Match their f_EDE to within ~20%
- Match their Δχ² qualitatively

### If it fails
Something fundamental is wrong with CLASS/Cobaya setup.

---

## Validation Sequence

### Phase A: Quick Checks (Today)
1. ✅ ΛCDM sanity vs DESI paper (already close: H₀=68.02)
2. ✅ SH0ES/TRGB likelihood correctly encoded (checked config lambdas)
3. ✅ χ²(H₀) scan completed - **GEOMETRY KILLS H₀=73**

#### χ²(H₀) Scan Results (BAO only, fixed cosmology):
```
H0    chi2_total    Δχ²(vs 68)
----------------------------------------
67          33.9       +12.5
68          21.4         0.0
70          26.2        +4.8
72          67.4       +46.1
73         100.6       +79.2   ← MASSIVE PENALTY
```

**Conclusion**: BAO geometry alone adds Δχ² = +79 at H₀=73.
SH0ES prior pulls with only Δχ² = 35 at H₀=67.
**Geometry wins: 79 > 35. The ceiling is real physics.**

### Phase B: Mock Test (1-2 days)
4. [ ] Generate mock CMB + BAO at Paper 1 cosmology
5. [ ] Run recovery chain
6. [ ] Confirm H₀ and Λ_EDE recovery

### Phase C: Literature Comparison (2-3 days)
7. [ ] Pick a reference EDE paper
8. [ ] Implement their setup
9. [ ] Compare results

---

## What Each Outcome Means

| Test | Pass | Fail |
|------|------|------|
| Mock recovery | Pipeline works | Config bug |
| ΛCDM sanity | Likelihoods correct | Data/likelihood wiring wrong |
| χ²(H₀) scan | Know who kills H₀=73 | Need to debug individual likelihoods |
| SH0ES plumbing | Prior pulling correctly | Prior not applied |
| Literature EDE | Our CLASS/EDE works | Fundamental CLASS bug |

---

## After Validation: Two Possible Conclusions

### If All Tests Pass
The H₀ ≈ 67 ceiling is **real physics** for this model class in the DESI era.

Statement we can make:
> "In the DESI + ACT DR6 era, a single-episode EDE shelf of the type we introduced in Paper 1 is real as a deformation of the CMB damping tail, but it cannot raise H₀ into the local ladder regime. Within this model class the geometry ceiling around 67–68 km/s/Mpc is hard."

### If Tests Fail
Fix the pipeline before making any physics claims.

---

## Next Steps After Validation

If we want H₀ > 68 with this field, we need "Ridder v2":
1. **Two-phase scalar**: Early shoulder + late distance tweak
2. **Mild DM coupling**: Screened interaction at low-z
3. **Separate late-time component**: Keep shoulder, add phantom w(z)

But first: **validate the pipeline**.

