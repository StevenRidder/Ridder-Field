# NEXT STEPS: Ridder Field Implementation

**Date:** 2025-11-21  
**Current Status:** Fluid approximation exhausted, ready for proper scalar field implementation

---

## Decision Point

You have three viable paths. Choose one based on your priorities:

### **Option 1: Full Scalar Field (Recommended for Publication)**

**Goal:** Implement Ridder as a true scalar field in CLASS using `scf` machinery

**Timeline:** 2-3 days focused work

**Steps:**
1. Study CLASS scalar field implementation:
   - Read `background.c` lines ~3000-4000 (scalar field evolution)
   - Read `perturbations.c` lines ~5000-6000 (scalar field perturbations)
   - Understand how `scf` handles oscillating fields

2. Clone existing scalar field:
   - Start with simplest oscillating example (e.g., cosine potential)
   - Replace potential with Ridder form: `V(φ) = Λ⁴(1 - cos(φ/f))ⁿ`
   - Map parameters: `Λ_EDE → Λ`, `f_axion → f`, `theta_i → φ_i`

3. Implement β-coupling:
   - Add coupling term to CDM perturbation equation
   - Ensure energy-momentum conservation

4. Validate:
   - Background should match current fluid implementation
   - CMB should be smooth (no ℓ=2500 spike)
   - Run `audit_rigorous.py` to verify

5. MCMC:
   - Use existing `ridder_field.yaml` (minimal changes needed)
   - Launch production chains

**Pros:**
- Scientifically correct
- Planck-grade precision
- Publication-ready
- Removes all approximation artifacts

**Cons:**
- Requires learning CLASS scalar field machinery
- More computationally expensive (but manageable)

---

### **Option 2: Background-Only (Quick Phenomenology)**

**Goal:** Get preliminary constraints while building Option 1

**Timeline:** 1 hour setup, overnight MCMC

**Steps:**
1. Modify `ridder_field.yaml`:
   ```yaml
   # Disable Ridder perturbations
   has_ridder: no
   # Add custom H(z) modifier (if CLASS supports)
   # OR: Keep has_ridder: yes but set beta_ridder: 0 and ignore P(k)
   ```

2. Run MCMC:
   ```bash
   cobaya-run ridder_field_background_only.yaml
   ```

3. Analyze:
   - Does background effect alone move H₀?
   - What are constraints on Λ_EDE, θ_i?
   - Use as "proof of concept" for full model

4. Document:
   - Clearly label as "background-only, perturbations neglected"
   - Use for internal discussion, not publication

**Pros:**
- Immediate results
- Tests viability of background mechanism
- Generates plots for presentations

**Cons:**
- Not physically complete
- Cannot address S₈ tension
- Must be clearly labeled as preliminary

---

### **Option 3: Detune θ_i (Stopgap)**

**Goal:** Minimize spike while exploring parameter space

**Timeline:** 10 minutes

**Steps:**
1. Edit `audit_rigorous.py`:
   ```python
   'theta_i_ridder': 2.0,  # was 2.35
   ```

2. Run audit:
   ```bash
   python3 audit_rigorous.py
   ```

3. Check if spike drops below 10%

4. If acceptable, run short MCMC to explore

**Pros:**
- Quick test
- Reduces artifact magnitude

**Cons:**
- Does not eliminate spike
- Sacrifices Hubble tension resolution (H₀ → 70-71)
- Still not production-ready

---

## Recommended Sequence

### Phase 1: Immediate (Today)

1. **Choose your path** (discuss with collaborators if needed)
2. **Archive current work:**
   ```bash
   cd /Users/steveridder/Git/Ridder\ Field
   git add -A
   git commit -m "Phase 2 complete: Fluid approximation exhausted, WKB hijack proven"
   git tag ridder_fluid_hack_nogo
   ```

3. **Update status documents:**
   - [x] `FINAL_VERDICT.md` (created)
   - [ ] `PHASE3_STATUS.md` (update with new path)
   - [ ] `README.md` (add roadmap)

### Phase 2: Short-term (This Week)

**If Option 1 (Scalar Field):**
- [ ] Create new branch: `ridder_scalar_field`
- [ ] Study CLASS `scf` implementation
- [ ] Implement Ridder potential
- [ ] Test background convergence

**If Option 2 (Background-Only):**
- [ ] Create `ridder_field_background_only.yaml`
- [ ] Run short MCMC chain
- [ ] Generate preliminary plots
- [ ] Start Option 1 in parallel

**If Option 3 (Detune):**
- [ ] Test θ_i = 2.0, 1.8, 1.5
- [ ] Find minimum spike configuration
- [ ] Run exploratory MCMC
- [ ] Plan transition to Option 1

### Phase 3: Medium-term (Next Month)

- [ ] Complete scalar field implementation
- [ ] Validate against fluid version (background)
- [ ] Run full MCMC with proper perturbations
- [ ] Generate "money plots": H(z), P(k), CMB
- [ ] Draft paper

---

## Resources

### CLASS Documentation
- Official docs: https://github.com/lesgourg/class_public
- Scalar field examples: `explanatory.ini` (search for `scf`)
- Community forum: https://github.com/lesgourg/class_public/issues

### Relevant Papers
- Scalar field EDE: Poulin et al. (2018) arXiv:1811.04083
- WKB matching: Smith et al. (2020) arXiv:2009.10740
- CLASS perturbations: Lesgourgues (2011) arXiv:1104.2932

### Internal Files
- Current implementation: `phase2/class/source/perturbations.c` lines 4481-4556 (WKB matching)
- Audit script: `phase2/audit_rigorous.py`
- Stress test results: `phase2/STRESS_TEST_REPORT.md`
- Final diagnosis: `phase2/FINAL_VERDICT.md`

---

## Contact Points

If you need help:

1. **CLASS implementation questions:**
   - Post on CLASS GitHub issues
   - Reference: "Implementing oscillating scalar field with coupling"

2. **Cosmology questions:**
   - Check EDE literature (Poulin, Smith, Niedermann)
   - Compare to Rock 'n' Roll model (similar structure)

3. **Numerical questions:**
   - WKB approximation: standard QM textbooks
   - Stiff ODE solvers: CLASS uses `ndf15` (good for oscillatory systems)

---

## Success Criteria

You will know you've succeeded when:

### For Option 1 (Scalar Field):
- ✅ Background H(z) matches fluid version
- ✅ CMB damping tail excess < 5%
- ✅ P(k) shows expected β-coupling suppression
- ✅ MCMC runs without crashes
- ✅ Constraints on Λ_EDE, θ_i, β are physically reasonable

### For Option 2 (Background-Only):
- ✅ MCMC converges (Gelman-Rubin R < 1.1)
- ✅ H₀ posterior shows shift toward SH0ES
- ✅ Preliminary constraints inform full model development

### For Option 3 (Detune):
- ✅ Damping tail excess < 10%
- ✅ MCMC explores parameter space without crashes
- ✅ Provides data for planning full implementation

---

## Final Checklist Before MCMC (Any Path)

- [ ] No compilation warnings
- [ ] `audit_rigorous.py` passes all tests (or documents known limitations)
- [ ] Background evolution is smooth (no discontinuities in H(z))
- [ ] CMB spectrum is stable across parameter variations
- [ ] P(k) shows expected behavior (or is excluded from likelihood)
- [ ] Cobaya YAML is configured correctly
- [ ] Output directory has sufficient disk space (~10 GB for long chains)
- [ ] Likelihoods are correctly specified (Planck, BAO, SH0ES)
- [ ] Prior ranges are physically motivated
- [ ] Proposal matrix is tuned (or use Cobaya defaults)

---

**Ready to proceed. Choose your path and execute.**

---

**Last Updated:** 2025-11-21  
**Next Review:** After completing chosen path

