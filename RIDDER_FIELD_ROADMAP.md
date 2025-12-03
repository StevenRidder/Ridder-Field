# Ridder Field Physics Roadmap

**Status:** Numerical infrastructure validated ✅  
**Next:** Physics calibration and exploration  
**Date:** 2025-11-24

---

## Where We Are

### ✅ Completed (Infrastructure)

1. **Unit conversions corrected**
   - V, dV/dφ, d²V/dφ² all in consistent units
   - Energy density and pressure match CLASS conventions
   - Verified against Klein-Gordon equation numerics

2. **Freeze and damping modes working**
   - Freeze mode: field acts as cosmological constant
   - Full KG mode: complete dynamics with physical force
   - Soft damping: tunable force strength (1.0 → 1e-8 → 0.0)
   - All three modes stable and fast with realistic Lambda

3. **File structure cleaned**
   - All source in `source/` directory (not root)
   - Makefile correctly compiles from `source/`
   - No more confusion between stale copies

4. **Initial conditions implemented**
   - Slow-roll ICs: φ' ≈ -(a/2H) dV/dφ
   - Tunable via `ridder_c_slow` parameter
   - Consistent units with evolution equation

5. **Shooting mechanism skeleton exists**
   - Bisection on log₁₀(Λ) implemented
   - Measures f_EDE peak in specified z window
   - Not yet validated with realistic physics

---

## The Three-Phase Plan

### Phase 1: Sanity and Calibration (Current Priority)

**Goal:** Prove the Ridder sector is a safe, ΛCDM-compatible extension

#### 1.1 Recover ΛCDM ✓ Next

**Test A: Freeze mode as effective Λ**
```ini
ridder_freeze_phi = yes
ridder_force_damping = 0.0
Lambda_EDE_ridder = [tune to match Ω_Λ,0 ≈ 0.7]
theta_i_ridder = 1.5
```

**Observables to check:**
- H(a) matches ΛCDM to < 0.1%
- Age of universe matches
- Ω_m, Ω_r, Ω_Λ correct at z=0
- Background tables complete to z=0

**Test B: Full KG mode with vacuum field**
```ini
ridder_freeze_phi = no
ridder_force_damping = 1.0
theta_i_ridder = 0.0  # or π (vacuum)
Lambda_EDE_ridder = [same as Test A]
```

**Observables to check:**
- H(a) still matches ΛCDM
- φ and φ' stay near vacuum (minimal oscillations)
- w_ridder ≈ -1 throughout
- No numerical instabilities

**Success Criterion:** Both tests reproduce ΛCDM H(z) to sub-percent accuracy

---

#### 1.2 Damping Continuity Test

**Setup:** Fix all parameters, vary only `ridder_force_damping`

```
Test series:
  damp = 1.0    (full physical force)
  damp = 0.1    (10x weaker)
  damp = 0.01   (100x weaker)
  damp = 0.001  (1000x weaker)
  damp = 1e-6   (essentially frozen)
  damp = 0.0    (explicit freeze) or use ridder_freeze_phi=yes
```

**For each, measure:**
- H(z) profile
- w_ridder(z) effective equation of state
- f_ridder(z) = ρ_ridder/ρ_tot
- Time to integrate (should scale roughly with damp for stiff regime)

**Success Criterion:** Smooth, monotonic deformation from full physics to frozen

---

#### 1.3 Full Pipeline Verification

**Run to z=0 with:**
- Freeze mode
- Mild dynamics (small Lambda, damp=1.0, theta_i chosen to keep f_ridder < 0.01 always)

**Verify CLASS modules complete:**
- Background ✓
- Thermodynamics
- Perturbations
- Transfer functions
- Harmonic (Cℓ's)
- Output

**Success Criterion:** No crashes, no pathological values in any output

---

### Phase 2: Shooting and Parameter Mapping

#### 2.1 Gentle Shooting Validation

**Test with tiny, easy target:**
```ini
use_ridder_shooting = 1
ridder_fEDE_target = 0.001  # 0.1% today (very weak)
ridder_zc_min = 0.1
ridder_zc_max = 10.0
ridder_shoot_log10Lambda_min = -80
ridder_shoot_log10Lambda_max = -50
```

**Instrumentation to add:**
```c
printf("SHOOT iter=%d log10Λ=%.4f f_measured=%.6e target=%.6e z_peak=%.1f\n",
       iter, logMid, fMid, target, zMid);
```

**Success Criterion:** Converges in < 20 iterations, f_measured within tolerance

---

#### 2.2 Define Ridder EDE Observable

**Precise definition:**
```c
f_ridder(z) = ρ_ridder(z) / ρ_tot(z)
z_peak = argmax(f_ridder) over [z_min, z_max]
f_peak = f_ridder(z_peak)
```

**Target band for EDE:**
- f_peak ∈ [0.05, 0.15]  (5-15% of total energy)
- z_peak ∈ [2000, 5000]  (around matter-radiation equality)

---

#### 2.3 θ_i Parameter Scan (No Shooting)

**Fixed setup:**
```ini
use_ridder_shooting = 0
Lambda_EDE_ridder = [hand-picked reasonable value]
f_axion_ridder = 2.435e27  # M_Pl
beta_ridder = 0.0
n_ridder = 3
ridder_c_slow = 1.0
ridder_freeze_phi = no
ridder_force_damping = 1.0
```

**Scan:** θ_i ∈ [-π, +π] with 20-50 points

**For each θ_i, record:**
- f_peak (maximum Ridder fraction)
- z_peak (redshift of peak)
- f_ridder(z=0) (today's value)
- w_ridder(z=0) (late-time equation of state)
- H₀ (inferred from background)

**Output:** Map θ_i → (f_peak, z_peak, H₀)

**Deliverable:** Plot or table showing:
1. Which θ_i give viable EDE (f_peak ~ 0.1, z_peak ~ 3000)
2. How sensitive the peak location is to θ_i
3. Whether there's a "natural" region or extreme fine-tuning

---

#### 2.4 Lambda Scale Calibration

Once we see θ_i map, pick a "good" θ_i and scan Lambda:

**Scan:** log₁₀(Lambda) ∈ [-60, -30] with 15 points

**For each Λ, record:**
- Same observables as θ_i scan

**Deliverable:** Map Λ → (f_peak, z_peak)

**Goal:** Understand scaling - how does peak amplitude depend on potential height?

---

#### 2.5 Re-enable Shooting with Realistic Target

Once manual scans show viable region exists:

```ini
use_ridder_shooting = 1
ridder_fEDE_target = 0.10
ridder_zc_min = 500
ridder_zc_max = 10000
ridder_shoot_log10Lambda_min = [from manual scan]
ridder_shoot_log10Lambda_max = [from manual scan]
```

**For grid of θ_i:**
- Shooter finds Λ for each θ_i
- Record converged (Λ, f_peak, z_peak, H₀)

**Deliverable:** Final map of viable parameter space

---

### Phase 3: Observables and Tension Relief

#### 3.1 Select Representative Points

From Phase 2 map, pick:
- "Perfect" EDE: f_peak ≈ 0.10, z_peak ≈ 3000
- Early peak: z_peak ≈ 5000
- Late peak: z_peak ≈ 1500  
- Small bump: f_peak ≈ 0.05

#### 3.2 Full CLASS Pipeline for Each

**Run complete calculation:**
1. Background (already have)
2. Thermodynamics
3. Perturbations (scalar, tensor, vector)
4. Transfer functions
5. CMB Cℓ's (TT, TE, EE, BB)
6. Matter power spectrum
7. Lensing potential

**Observables:**
- H₀ (inferred)
- S₈ = σ₈(Ω_m/0.3)^0.5
- r_drag (sound horizon at drag epoch)
- D_A (angular diameter distance to last scattering)
- Age of universe
- Full Cℓ spectra

#### 3.3 Compare to Planck ΛCDM

**Questions:**
1. Can we raise H₀ by ~5 km/s/Mpc while keeping Cℓ's reasonable?
2. Does S₈ get better or worse?
3. Are there distinctive signatures (e.g., oscillations from staircase)?
4. Does the model prediction for r_drag change in helpful ways?

#### 3.4 Look for Unique Signatures

**Beyond parameter shifts:**
- Staircase structure → periodic features in w(z)?
- Monodromy flattening → distinctive shape of f_EDE(z)?
- Coupling to DM → correlated changes in structure formation?

**Decision point:** Is this "just another EDE" or "qualitatively different"?

---

## Next Immediate Actions

### Today (Post File-Structure Fix):

1. ✅ **Clean up duplicate files** - DONE
2. **Sync to remote server**
3. **Create ΛCDM recovery test ini**
4. **Run Test 1.1A: Freeze mode as Λ**
5. **Document baseline H(z) for comparison**

### This Week:

1. Complete Phase 1.1 (ΛCDM recovery both modes)
2. Run Phase 1.2 (damping continuity test)
3. Verify Phase 1.3 (full pipeline to z=0)
4. Set up automated θ_i scan infrastructure

### Next Week:

1. Manual θ_i scan (no shooting)
2. Analyze results, identify viable region
3. Set up shooting with realistic bracket
4. Generate parameter space map

---

## Key Parameters Reference

### Current Test Values (Infrastructure Validation)
```ini
Lambda_EDE_ridder = 1e-50    # Tiny (for stability tests)
f_axion_ridder = 2.435e27     # M_Pl scale
theta_i_ridder = 1.5          # Mid-slope
```

### Expected EDE-Scale Values
```ini
Lambda_EDE_ridder = ???       # To be determined from scans
                               # Likely range: 1e-60 to 1e-40
f_axion_ridder = 2.435e27     # Keep at M_Pl
theta_i_ridder = ???          # To be mapped
                               # Expect viable range ~ 1.0 to 2.5
```

### Derived Scales
```
m_eff = sqrt(d²V/dφ²) ≈ sqrt(Λ⁴/f²) * [geometric factor]
For EDE at z~3000: need m_eff ~ H(z~3000) ~ few × 10⁻²⁰ Mpc⁻¹
```

---

## Success Metrics

### Phase 1 Success:
- ✅ Reproduces ΛCDM to < 0.1% when configured as effective Λ
- ✅ Smooth behavior across damping range
- ✅ No crashes in full CLASS pipeline

### Phase 2 Success:
- ✅ Shooting converges reliably with realistic targets
- ✅ Viable EDE region exists (not fine-tuned knife-edge)
- ✅ Clear mapping from parameters to (f_peak, z_peak)

### Phase 3 Success:
- ✅ Can adjust H₀ by several km/s/Mpc
- ✅ Doesn't destroy other observables
- 🎯 **Bonus:** Distinctive signatures beyond standard EDE

---

## Open Questions for V3

*To be addressed only after Phase 2 shows promise:*

1. Does viable parameter space cluster around specific structural features?
2. Can we derive those features from UV modulus physics?
3. Is there a selection principle that picks out the working regime?
4. Do staircase/monodromy details matter, or just effective mass scale?

---

## File Organization

**Code:**
- `phase2/class/source/background.c` - Main implementation
- `phase2/class/include/background.h` - Struct and parameters
- `phase2/class/source/input.c` - Parameter reading

**Test configurations:**
- `test_freeze_on.ini` - Infrastructure validation
- `test_freeze_off.ini` - Infrastructure validation
- `test_soft_damping.ini` - Infrastructure validation
- `test_lcdm_recovery.ini` - Phase 1.1 [to create]
- `test_gentle_shooting.ini` - Phase 2.1 [to create]

**Documentation:**
- `FREEZE_AND_DAMPING_VALIDATED.md` - Infrastructure status
- `RIDDER_FIELD_ROADMAP.md` - This file (physics plan)
- `UNITS_FIXED_STIFFNESS_REMAINS.md` - Historical debugging

**Results:** (to be created)
- `results/phase1_lcdm_recovery/`
- `results/phase2_theta_scan/`
- `results/phase3_observables/`

---

## Notes on "Will This Change the World?"

**Realistic expectations:**
- Prior is against any new scalar field model being revolutionary
- Most likely outcome: "Another viable EDE variant"
- Still valuable: Explores specific theoretical corner (axion monodromy inspired)

**What would be exceptional:**
- Viable parameter space has natural clustering (not fine-tuned)
- Distinctive observational signatures beyond H₀ shift
- UV story (V3) predicts the clustering

**Publication strategy:**
- Even "ho hum" result is publishable if done rigorously
- Focus: "Does this specific theoretical structure work or not?"
- Honest assessment better than overselling

---

**Status:** Ready for Phase 1.1 - ΛCDM Recovery Tests

