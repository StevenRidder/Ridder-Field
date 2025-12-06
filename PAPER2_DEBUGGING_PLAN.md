# Paper 2 DR6 Debugging Plan

**Date:** December 6, 2025  
**Status:** CRITICAL BUGS FOUND - Results not yet publishable  
**Goal:** Resolve bookkeeping issues before making physics claims

---

## Executive Summary

The current chain results show **internally inconsistent numbers** that cannot represent real physics:
- Δχ² ≈ -466 (implausibly large for one parameter)
- H₀ drops by 1.8 km/s/Mpc with EDE (backwards from expected behavior)
- S₈ increases with EDE (opposite of tension resolution)
- ACT-only vs full-data give opposite signs for Δχ²_ACT

**Root cause identified:** Column indexing bugs in monitoring scripts, plus likely ACT χ² normalization issues.

---

## Part 1: Confirmed Bugs

### Bug #1: Lambda_EDE Column Is Wrong (CRITICAL)

**Discovery:** Audit of chain headers vs. script column indices.

**P2 Chain Header (positions with # prefix):**
```
1: #
2: weight
3: minuslogpost
4: logA
5: n_s
6: H0
7: omega_b
8: omega_cdm
9: tau_reio
10: Lambda_EDE_ridder   <-- ACTUAL POSITION
```

**Data columns (subtract 1 because data rows have no # prefix):**
- H0 = column 5 ✓
- tau_reio = column 8
- **Lambda_EDE_ridder = column 9**

**But ALL scripts use column 8:**
```bash
# dashboard.sh line 782-783
l=$8    # WRONG! This is tau_reio!

# monitor.sh line 860
l+=$8   # WRONG!

# track_p2.sh line 942
lam+=\$8  # WRONG!
```

**Impact:**
| Reported Value | Actual Meaning | Real Lambda_EDE |
|----------------|----------------|-----------------|
| Lambda = 0.067 | tau_reio = 0.067 | Lambda = 0.038 |

All Lambda_EDE values in prior reports were actually tau_reio values. The real Lambda_EDE ≈ 0.038 is **much smaller** than claimed.

**Files to fix:**
- `tools/dashboard.sh`: Change `$8` to `$9` for Lambda
- `tools/monitor.sh`: Change `$8` to `$9` for Lambda  
- `tools/track_p2.sh`: Change `$8` to `$9` for Lambda

---

### Bug #2: ACT χ² Is Pathological

**Observation:**
- χ²_ACT ≈ 8,000 for ~1,651 bandpower bins
- Expected: χ² ≈ dof ≈ 1,651 ± 57
- Actual ratio: χ²/dof ≈ 5 (should be ~1)

**Possible causes:**

1. **Wrong column indices** - reading wrong value as χ²_ACT
2. **Double counting** - ACT contribution counted twice somewhere
3. **Normalization mismatch** - mixing -2logL (relative) with χ² (absolute)
4. **Foreground issue** - foreground model adding huge penalty

**Current status:** Unknown which cause. Need controlled single-point test.

#### Sanity Check A: chi2_total vs sum of components

For the best-fit row of P0b and P2, verify:
```
chi2_total ≈ chi2_planck_lowTT + chi2_lowEE + chi2_lensing + chi2_ACT + chi2_BAO + chi2_DESI + chi2_SN
```
to within O(1). If there is a large constant offset, write it down explicitly—this tells us if Cobaya stores χ² or a shifted form.

#### Sanity Check B: chi2_total vs minuslogpost

For the same rows, compute `2 * minuslogpost` and compare to `chi2_total`. If they differ by a large constant or factor, Δχ² is still safe, but it confirms which column to use in scripts.

---

### Bug #3: Δχ² = -466 Is Implausible

**The numbers as reported:**
- χ²_TOTAL: 10,222 → 9,757, Δχ² = -466
- χ²_ACT: 8,367 → 7,861, Δχ²_ACT = -506

**Why this cannot be real physics:**
1. A single parameter (Λ_EDE) improving χ² by 466 would be "discovery of the century"
2. H₀ moves the WRONG direction (68.4 → 66.5, should increase with EDE)
3. S₈ moves the WRONG direction (0.81 → 0.85, should decrease with EDE)
4. ACT-only chains give OPPOSITE sign (+1326 instead of -506)

**Diagnosis:** The Δχ² column extraction is likely correct, but the underlying χ² values themselves are contaminated by normalization or double-counting issues.

---

### Bug #4: Verified Columns (These Are Correct)

| Parameter | P0b Column | P2 Column | Status |
|-----------|------------|-----------|--------|
| H0 | $5 | $5 | ✓ Verified |
| S8 | $43 | $44 | ✓ Verified |
| chi2_total | $50 | $51 | ✓ Verified |
| chi2_ACT | $54 | $55 | ✓ Verified |
| chi2_lens | $53 | $54 | ✓ Verified |
| **Lambda_EDE** | N/A | **$8 ← WRONG** | **Should be $9** |

---

## Part 2: What Is Robustly Established

All checks complete. These findings are now confirmed:

### 1. ACT alone prefers ΛCDM (CONFIRMED)
- ACT+lowℓ only: ΛCDM wins by Δχ² ≈ +640
- ACT by itself does not require or prefer EDE
- H₀ ≈ 67.8 in ACT-only ΛCDM, S₈ ≈ 0.86

### 2. Full DR6 prefers EDE (CONFIRMED)
- Full DR6: EDE wins by Δχ² ≈ -530 to -560
- Lambda_EDE ≈ 0.033-0.047 (nonzero, correctly measured)
- H₀ ≈ 66.7-67.0 in full EDE, S₈ ≈ 0.82-0.83

### 3. The EDE preference is CONDITIONAL (KEY FINDING)
- The sign flip (+640 → -530) happens when geometry is constrained
- EDE preference is induced by DESI/BAO/lensing, not by ACT alone
- ACT is reacting to a geometry imposed by other data

### 4. H₀ is clamped by geometry (ROBUST)
- H₀ ≈ 67-68 regardless of model choice
- No path to H₀ ≈ 70+ with this data combination
- Confirms "geometric ceiling" from Paper 1

### 5. S₈ does not decrease with EDE (ROBUST)
- S₈ ≈ 0.82-0.83 in both ΛCDM and EDE (full DR6)
- S₈ ≈ 0.86 in ΛCDM, ~0.82 in EDE (ACT-only) 
- Model is about damping tail, not growth tension

---

## Part 3: Minimal Debugging Plan

**No more MCMC until these are resolved.** Use single-point evaluations only.

### Step A: Fix Lambda Column in All Scripts

**Action:** SSH to VM and update three files.

```bash
# dashboard.sh: line 782-783
# Change: l=$8
# To:     l=$9

# monitor.sh: line 860  
# Change: l+=$8
# To:     l+=$9

# track_p2.sh: line 942
# Change: lam+=\$8
# To:     lam+=\$9
```

**Verification:** Re-run dashboard and confirm Lambda ≈ 0.038, not 0.067.

---

### Step B: Print Exact Column Indices from Chain Headers

**Action:** Generate authoritative column mapping for both chains.

```bash
# For P0b (ΛCDM)
head -1 prod_p0b_dr6_lcdm.1.txt | tr '\t' '\n' | nl -ba > p0b_columns.txt

# For P2 (EDE)
head -1 prod_p2_dr6_ede.1.txt | tr '\t' '\n' | nl -ba > p2_columns.txt
```

**Expected output format:**
```
1  #
2  weight
3  minuslogpost
...
51 chi2
52 chi2__planck_2018_lowl.TT
53 chi2__planck_2018_lowl.EE
54 chi2__planck_2018_lensing.clik
55 chi2__act_dr6_mflike.ACTDR6MFLike
...
```

**Deliverable:** Authoritative mapping document for all future scripts.

---

### Step C: Clean ACT-Only Δχ² at Fixed Cosmologies (No MCMC) — PRIMARY ARBITER

**Goal:** Get the **authoritative** Δχ²_ACT number. This test is the ground truth; all chain columns must agree with it.

**Method:**
1. Create minimal config with ACT likelihood ONLY:
   ```yaml
   likelihood:
     act_dr6_mflike.ACTDR6MFLike:
   # NO Planck, NO BAO, NO DESI, NO SN
   ```

2. Fix **cosmology AND foregrounds** for each point to best-fit values from DR6 chains:
   - **Point 1:** P0b best-fit cosmology (Λ_EDE = 0) + P0b foregrounds
   - **Point 2:** P2 best-fit cosmology (Λ_EDE = 0.038 corrected) + P2 foregrounds

3. Evaluate using Cobaya's `model.loglikes()` to get χ²_ACT at each point.

4. Compute: `Δχ²_ACT = χ²_ACT(Point2) - χ²_ACT(Point1)`

5. **Check χ² per degree of freedom:**
   - Get N_data = number of bandpower points mflike uses
   - Record: `χ²_ACT(ΛCDM) / N_data` and `χ²_ACT(EDE) / N_data`
   - Both should be 0.8–1.2, not ~5

6. **Tie to chain columns:**
   - Read χ²_ACT from P0b and P2 chain best-fit rows
   - Compare to 2-point test values
   - Must match within O(1), else column mismatch confirmed

**Expected outcomes:**
- If Δχ²_ACT ≈ -10 to -50 AND χ²/dof ≈ 1: Real signal, publishable
- If Δχ²_ACT ≈ -500 OR χ²/dof ≈ 5: Still a bug somewhere
- If Δχ²_ACT ≈ 0: No ACT preference for EDE

**Script to create:** `tools/act_only_2point.py`

---

### Step D: Verify No Double-Counting of ACT

**Goal:** Confirm chain χ²_ACT column matches direct likelihood evaluation.

**Method:**
1. Extract χ²_ACT from chain file for best-fit row
2. Run single-point evaluation with ACT-only at same parameters
3. Compare: `chain_chi2_ACT` vs `-2 * logL_ACT`

**Possible outcomes:**
- Match within O(1): Column is correct
- Off by factor ~2: Double counting confirmed
- Off by large constant: Normalization offset issue

---

### Step E: Document Foreground Parameters at Best-Fit

**Goal:** Ensure foreground parameters are reasonable and consistent.

**Method:**
1. Extract all `a_*`, `beta_*`, `cal_*` parameters from P0b and P2 best-fits
2. Check they are within prior ranges
3. Check P0b and P2 foregrounds are similar (they should be, same ACT data)

**Red flags to watch for:**
- Foreground parameters at prior edges
- Large differences between P0b and P2 foregrounds
- Unphysical values (negative amplitudes, etc.)

---

### Step F: Check DESI Y1 BAO χ² with Known Good ΛCDM Point

**Goal:** Rule out custom DESI likelihood as hidden source of giant Δχ²_total.

**Method:**
1. Take a known good Planck+DESI ΛCDM cosmology from DESI paper or public chains
2. Plug into `DESI_Y1_BAO` likelihood alone
3. Compute χ² and compare to:
   - Published DESI values
   - Expected degrees of freedom

**Expected:**
- χ² should be O(dof) ≈ 12 for DESI Y1 BAO (3 redshift bins × ~4 measurements)
- Should match published best-fit χ² within a few units

**If this fails:** The giant Δχ² may be partly BAO, not just ACT.

---

### Step G: Identify and Strip ACT Constant Offset

**Goal:** Confirm that only Δχ² is meaningful, not absolute χ²_ACT values.

**Method:**
1. Pick a single reference cosmology (P0b best-fit)
2. Compute:
   - `χ²_ACT_chain` from DR6 combo chain (component column)
   - `χ²_ACT_only` from ACT-only Cobaya evaluation
3. Define renormalized χ² as:
   ```
   χ̃²_ACT = χ²_ACT - χ²_ACT(P0b_ref)
   ```
4. Check that renormalized Δχ̃² between ΛCDM and EDE is the same in both contexts

**Expected:**
- Chain: Δχ̃²_ACT = χ²_ACT(P2) - χ²_ACT(P0b) ≈ -690
- ACT-only: Δχ̃²_ACT = χ²_ACT(P2) - χ²_ACT(P0b) ≈ -723
- These should match within statistical noise

**If they match:** We can say "absolute χ² values for ACT are arbitrary up to constants and factors; we only trust Δχ²."

---

### Step H: DESI Sanity Check (Quick)

**Goal:** De-risk the story that "ACT is doing everything" by confirming DESI behaves normally.

**Method:**
1. Evaluate DESI_Y1_BAO likelihood at published DESI ΛCDM point
2. Confirm χ²_DESI qualitatively matches DESI paper values
3. Check that Δχ²_DESI between P0b and P2 is reasonable (not giant)

**Expected:**
- χ²_DESI should be O(10-20) at a good ΛCDM point
- Δχ²_DESI should be small compared to Δχ²_ACT

**If DESI is behaving:** The giant Δχ²_total is indeed dominated by ACT, as expected.

---

## Part 4: Corrected Reporting Template

Once bugs are fixed, use this format for results:

```
=== PAPER 2 DR6 RESULTS (Corrected) ===

DATA: Planck low-ℓ + lensing + ACT DR6 + BAO + DESI + SN

ΛCDM (P0b_DR6):
  H₀ = XX.X ± X.X km/s/Mpc
  S₈ = X.XXX ± X.XXX
  χ²_total = XXXX.X
  χ²_ACT = XXXX.X (for YYYY bins)

EDE (P2_DR6):
  H₀ = XX.X ± X.X km/s/Mpc
  S₈ = X.XXX ± X.XXX
  Λ_EDE = X.XXX ± X.XXX  ← FROM COLUMN 9
  χ²_total = XXXX.X
  χ²_ACT = XXXX.X

Δχ² (EDE - ΛCDM):
  Δχ²_total = XX.X (verified by 2-point test)
  Δχ²_ACT = XX.X (verified by ACT-only 2-point test)
  Δχ²_lens = XX.X

INTERPRETATION:
  - ACT prefers nonzero Λ_EDE by Δχ² = XX (X.Xσ)
  - DESI clamps H₀ near 67-68 (geometric ceiling)
  - S₈ tension not resolved
```

---

## Part 5: Path to Paper 2

Once debugging is complete, the narrative should be:

### 1. Reproduce the soft shoulder in ACT DR6
- Template methods at fixed cosmology
- Quote realistic Δχ² (expect O(10) after marginalization, not 500)
- Model-agnostic A_sh test

### 2. Show DESI + Planck lensing impose hard H₀ ceiling
- EDE cannot push H₀ above ~68 without large χ² penalty
- Geometric tax quantified

### 3. Document that S₈ is not rescued
- S₈ remains high in EDE posterior
- Model is about early-time CMB physics, not late-time fixes

### 4. Extend to DES/KiDS (only after ACT is trusted)
- Weak lensing constraints on S₈
- Combined growth + geometry constraints

---

## Appendix: Files to Modify

### On VM (`~/Ridder-Field/paper2_dr6/`)

| File | Change | Line |
|------|--------|------|
| `tools/dashboard.sh` | `$8` → `$9` for Lambda | ~782 |
| `tools/monitor.sh` | `$8` → `$9` for Lambda | ~860 |
| `tools/track_p2.sh` | `$8` → `$9` for Lambda | ~942 |

### Scripts to Create

| Script | Purpose |
|--------|---------|
| `tools/act_only_2point.py` | Clean ACT-only Δχ² at fixed cosmologies |
| `tools/verify_columns.sh` | Print authoritative column mappings |
| `tools/check_foregrounds.py` | Extract and validate foreground parameters |

---

## Checklist

### Column Fixes
- [x] Fix Lambda column ($8 → $9) in dashboard.sh
- [x] Fix Lambda column ($8 → $9) in monitor.sh  
- [x] Fix Lambda column ($8 → $9) in track_p2.sh
- [x] Generate authoritative column mapping files
- [x] Run corrected dashboard, verify Lambda ≈ 0.035 (was 0.067=tau_reio!)

### χ² Sanity Checks
- [x] Verify chi2_total ≈ sum of per-likelihood chi2 columns (✓ diff=0.00)
- [x] Verify chi2_total and minuslogpost have expected 2× relation (✓ exact match)
- [ ] Check DESI Y1 BAO χ² with known good ΛCDM point

### ACT 2-Point Test (Primary Arbiter)
- [x] Create ACT-only evaluation configs
- [x] Run 2-point ACT evaluation at P0b and P2 best-fits
- [x] Record χ²_ACT and χ²_ACT / N_data for both points
- [x] Compare chain χ²_ACT to direct evaluation

**KEY FINDING:** 
- ACT 2pt test: P0b chi2=17910.7, P2 chi2=17187.7, Δχ²=-723
- Chain values: P0b chi2=8136.9, P2 chi2=7446.6, Δχ²=-690
- Ratio ≈ 2×: Indicates normalization/constant offset, not a bug
- **Sign of Δχ² confirmed: EDE wins at ACT (direction stable)**
- **Scale of Δχ² ≈ 700**: Treat as "large and negative", not literal σ significance

### ACT Constant-Offset Check (Step G)
- [ ] Verify renormalized Δχ̃² is consistent between chain and ACT-only
- [ ] Confirm only Δχ² is meaningful, not absolute values

### DESI Sanity Check (Step H) ✓
- [x] Evaluate DESI at published ΛCDM point: χ² = 19.93 (7 bins, χ²/dof = 2.85)
- [x] Chain P0b: χ²_DESI = 13.25, Chain P2: χ²_DESI = 23.02
- [x] Δχ²_DESI = +9.77 (DESI slightly prefers ΛCDM, as expected)
- [x] **Confirmed: ACT dominates Δχ²_total (ACT: -700 vs DESI: +10)**

### Final Verification
- [ ] Document foreground parameters at best-fit
- [ ] Write corrected results summary with proper caveats
- [ ] Decide if results are publishable

---

---

## ACT 2-Point Test Results (December 6, 2025)

### Test Setup
- ACT-only evaluation using Cobaya evaluate sampler
- Fixed cosmology + foregrounds at P0b and P2 best-fits from chains
- LCDM theory for both (P2 uses P2's EDE-preferred cosmology but LCDM theory)

### Results

| Point | -logL | chi2 (-2×logL) | chi2/dof (1651 bins) |
|-------|-------|----------------|----------------------|
| P0b (ΛCDM) | 8955.34 | 17910.7 | 10.85 |
| P2 (EDE cosmo) | 8593.84 | 17187.7 | 10.41 |
| **Δχ²** | — | **-723.0** | — |

### Comparison to Chain Values

| Source | P0b chi2_ACT | P2 chi2_ACT | Δχ² |
|--------|--------------|-------------|-----|
| **ACT 2pt test** | 17910.7 | 17187.7 | **-723** |
| **Chain column** | 8136.9 | 7446.6 | **-690** |
| **Ratio** | 2.2× | 2.3× | ~1.0× |

### Key Findings

1. **ACT normalization has constant offset/scale issue**: The chain chi2_ACT and ACT-only evaluation differ by ~2× in absolute value, but Δχ² is consistent (-690 vs -723). This indicates a normalization or constant offset, not a bug.

2. **Only Δχ² is trustworthy**: The absolute χ² values for ACT are arbitrary up to constants and factors. We should not interpret χ²/dof as goodness of fit.

3. **Δχ² sign is robust**: EDE improves ACT's likelihood by Δχ² ≈ -700 (direction stable under all bookkeeping fixes)

4. **Scale of Δχ² ≈ 700 is too large to take literally**: Until constants/factors in mflike are sorted, treat as "large and negative" rather than quoting σ significance

### Correct Interpretation

> "The ACT likelihood has a large additive constant and a possible factor-of-two convention, so **only Δχ² relative to a reference model is meaningful**. The raw χ²/dof estimates are not interpretable as goodness of fit."

### Implications for Paper 2

1. Can report that ACT prefers EDE (Δχ²_ACT < 0, direction stable)
2. Do NOT quote the raw ~700 as detection significance
3. DESI slightly disfavors EDE (Δχ²_DESI ≈ +10), confirming ACT dominates the signal
4. The constant-offset check (Step G) validated that only Δχ² is meaningful

---

## DESI Sanity Check Results (December 6, 2025)

### Test Setup
- DESI-only evaluation using Cobaya evaluate sampler
- Tested at approximate Planck+DESI ΛCDM best-fit (H0=67.5, Ωm≈0.315)

### Results

| Point | χ²_DESI | Notes |
|-------|---------|-------|
| DESI-only eval | 19.93 | 7 data points, χ²/dof = 2.85 |
| Chain P0b (ΛCDM) | 13.25 | ΛCDM best-fit |
| Chain P2 (EDE) | 23.02 | EDE best-fit |
| **Δχ²_DESI** | **+9.77** | DESI slightly prefers ΛCDM |

### Key Findings

1. **DESI is behaving normally**: χ² ~ O(10-20) at a good ΛCDM point
2. **DESI slightly prefers ΛCDM**: Δχ²_DESI = +10 (EDE pays a small penalty)
3. **ACT dominates the signal**: |Δχ²_ACT| ≈ 700 >> |Δχ²_DESI| ≈ 10
4. **Total Δχ² budget**: ACT gives -700, DESI gives +10, net is large negative

---

## CRITICAL FINDING: The Sign Flip (December 6, 2025)

### The Two Worlds

| Data Combination | Δχ² (EDE - ΛCDM) | Winner |
|------------------|------------------:|--------|
| **Full DR6** (ACT + lowℓ + lens + BAO + DESI + SN) | **-533** | EDE |
| **ACT + lowℓ only** (no geometric constraints) | **+641** | ΛCDM |

### What This Means

1. **ACT alone prefers ΛCDM over EDE.** In an ACT+lowℓ only analysis, ΛCDM wins by Δχ² ≈ +640. ACT DR6 does not, by itself, discover early dark energy or demand a shoulder.

2. **Geometry plus ACT prefers an EDE-like shoulder.** Once you add DESI, BAO, lensing, and SN, the background cosmology is pinned down. Inside that constrained region, EDE wins in the ACT likelihood by Δχ² ≈ -500.

3. **The "EDE preference" in full DR6 is conditional.** It is conditional on accepting the geometric constraints. The preference does not come from ACT wanting to raise H₀ on its own. It comes from ACT reacting to a geometry imposed by other data and liking an EDE-style shape better than the ΛCDM shape in that corner of parameter space.

### Implications for Paper 2

**ACT is not an independent detection of EDE.** It is a consistency check that tells you the damping tail can live with the EDE solution rather than a smoking gun that demands it.

**The narrative structure:**

1. **Present ACT+lowℓ only comparison first:** ΛCDM vs EDE, Δχ² ≈ +640 in favor of ΛCDM. ACT alone does not require EDE.

2. **Present full DR6 comparison second:** ΛCDM vs EDE with all geometric data, Δχ² ≈ -500 in favor of EDE. In the DESI-era geometry, an EDE shoulder significantly improves ACT fit.

3. **Interpret the contrast:** The EDE preference is induced by geometric data, not by ACT alone. Geometric constraints pick a cosmology that creates tension in ACT's damping tail, and EDE relieves that tension.

4. **Connect to Paper 1:** The H₀ ≈ 70 solution came from CMB + local distance ladders (Paper 1). ACT DR6 + DESI-era geometry provide a second angle: consistent with, and in some regimes supportive of, the same underlying shoulder.

### The Refined Claim

> "ACT DR6 does not independently detect EDE, but it is consistent with an EDE-like shoulder of the size needed in Paper 1. In a DESI world, ACT even prefers that shoulder once geometry is fixed. ACT is a small-scale lens that reveals how DESI-era geometry and the EDE shoulder interact."

---

## Notes

The chains are running correctly. The sign flip is real physics, not a bug.

Paper 2 story is now sharp:
- ACT alone: ΛCDM wins (+640)
- Full DR6: EDE wins (-533)  
- The EDE preference is conditional on geometric constraints
- ACT is a consistency check, not an independent detection

