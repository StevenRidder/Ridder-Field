# V3 Performance Optimization Plan

**Date:** November 26, 2025  
**Current Performance:** 17 sec/MCMC step (37,000 derivative calls)  
**Target Performance:** 3-5 sec/MCMC step (5,000-10,000 derivative calls)  
**Goal:** **5x speedup**

---

## 🔴 CRITICAL ISSUE

**Problem:** V3 CLASS integrator is making **37,000 derivative calls per MCMC step** vs expected 1,000-5,000.

**Root Cause:** The v3 unified potential creates stiff dynamics that force the ODE integrator to take many small timesteps.

**Impact:** V3 tier 3 MCMC would take ~30 hours per chain instead of ~5 hours.

---

## 🎯 Optimization Strategy (Ranked by Impact)

### Priority 1: Reduce Derivative Call Count (Expected: 5-7x speedup)

#### Option 1A: Relax Background Integrator Tolerance
**Impact:** ⭐⭐⭐⭐⭐ (Expected 2-3x speedup)  
**Difficulty:** ⚡ Easy (10 minutes)  
**Risk:** 🟢 Low

**Action:**
```bash
ssh ridderadmin@172.174.34.125
cd ~/Ridder-Field/phase2/class/source

# Find and edit background.c
grep -n "tol_background_integration\|background_pert_integration_stepsize" background.c
```

**Current (likely):**
```c
pba->tol_background_integration = 1.e-5;  // Very tight
```

**Change to:**
```c
pba->tol_background_integration = 1.e-4;  // 10x looser
```

**Validation:**
- Run test point before/after
- Compare H(z), Cl's, chi2
- If difference < 0.1%, tolerance is safe

---

#### Option 1B: Disable Tail Component for Testing
**Impact:** ⭐⭐⭐⭐ (Expected 1.5-2x speedup)  
**Difficulty:** ⚡ Trivial (1 minute)  
**Risk:** 🟢 None (just testing)

**Action:**
```yaml
# Edit: ridder_v3_tier3_test.yaml
ridder_use_tail: "no"  # Change from "yes"
```

**Rationale:** Tail component adds complexity but may not be critical for EDE testing.

---

#### Option 1C: Implement Adaptive Potential Evaluation
**Impact:** ⭐⭐⭐ (Expected 1.5x speedup)  
**Difficulty:** ⚡⚡ Medium (1 hour)  
**Risk:** 🟡 Medium

**Action:** Skip expensive tail calculation when negligible

```c
// In ridder_v3_potential.c
double V_tail_v3(double theta, double a, struct ridder_unified_params *rp) {
  if (!rp->use_tail) return 0.0;
  
  // NEW: Skip if we're in early universe where tail is irrelevant
  if (a < 0.01) return 0.0;  // Tail only matters at z < 100
  
  // Original calculation...
}
```

---

### Priority 2: Optimize Potential Function (Expected: 1.5-2x speedup)

#### Option 2A: Replace pow() with Direct Multiplication
**Impact:** ⭐⭐⭐ (Expected 1.3-1.5x speedup)  
**Difficulty:** ⚡ Easy (15 minutes)  
**Risk:** 🟢 None

**Current code has 6 pow() calls per derivative evaluation:**

```c
// BEFORE (slow):
double Lambda4_EDE = pow(rp->Lambda_EDE_eV, 4.0);   // ~50 cycles
double Lambda4_tail = pow(rp->Lambda_tail_eV, 4.0); // ~50 cycles
double Lambda4_floor = pow(rp->Lambda_floor_eV, 4.0); // ~50 cycles
double bump = pow(one_minus_cos, n_EDE);  // ~50 cycles if n=3

// AFTER (fast):
double L = rp->Lambda_EDE_eV;
double Lambda4_EDE = L*L*L*L;  // ~3 cycles

double L = rp->Lambda_tail_eV;
double Lambda4_tail = L*L*L*L;  // ~3 cycles

double L = rp->Lambda_floor_eV;
double Lambda4_floor = L*L*L*L;  // ~3 cycles

// For integer powers, unroll:
if (n_EDE == 3) {
  bump = one_minus_cos * one_minus_cos * one_minus_cos;
} else {
  bump = pow(one_minus_cos, n_EDE);
}
```

**Savings:** 6 pow() calls → 0-1 pow() calls = **~200 cycles per derivative call**

---

#### Option 2B: Precompute Lambda^4 Values
**Impact:** ⭐⭐ (Expected 1.1x speedup)  
**Difficulty:** ⚡⚡ Medium (30 minutes)  
**Risk:** 🟢 Low

**Action:** Compute Lambda^4 once in initialization, store in struct

```c
// In ridder_unified_params struct (background.h):
struct ridder_unified_params {
  double Lambda_EDE_eV;
  double Lambda_EDE_eV_4;  // NEW: precomputed Lambda^4
  double Lambda_tail_eV;
  double Lambda_tail_eV_4;  // NEW: precomputed Lambda^4
  // ...
};

// In input.c (after reading Lambda_EDE_eV):
double L = pba->ridder_unified.Lambda_EDE_eV;
pba->ridder_unified.Lambda_EDE_eV_4 = L*L*L*L;

// In ridder_v3_potential.c:
double V_EDE_v3(...) {
  double Lambda4 = rp->Lambda_EDE_eV_4;  // Just read, no computation!
  // ...
}
```

---

#### Option 2C: Optimize Trig Functions
**Impact:** ⭐ (Expected 1.05x speedup)  
**Difficulty:** ⚡ Easy (10 minutes)  
**Risk:** 🟢 Low

**Action:** Reuse cos/sin calculations

```c
// BEFORE: Computing cos twice
double one_minus_cos_EDE = 1.0 - cos(theta - theta_E);
// ... later in derivative ...
double sin_term = sin(theta - theta_E);  // Should have saved from earlier

// AFTER: Compute once, store
double delta_theta_EDE = theta - rp->theta_E_center;
double cos_EDE = cos(delta_theta_EDE);
double sin_EDE = sin(delta_theta_EDE);
double one_minus_cos_EDE = 1.0 - cos_EDE;

// Use stored values everywhere
```

---

### Priority 3: Integrator Configuration (Expected: 2x speedup)

#### Option 3A: Use Faster ODE Solver
**Impact:** ⭐⭐⭐⭐ (Expected 2x speedup)  
**Difficulty:** ⚡⚡⚡ Hard (2-3 hours)  
**Risk:** 🟡 Medium

**Current:** CLASS uses `ndf15` (implicit solver for stiff equations)

**Alternative:** Try `rkck` (Runge-Kutta Cash-Karp) for non-stiff regions

**Check in background.c:**
```c
// Search for evolver selection
pba->evolver = ndf15;  // or similar
```

**Test both:**
- ndf15: Stable for stiff equations, slow
- rkck: Fast for smooth equations, may fail on stiff regions

---

#### Option 3B: Implement Dual-Regime Integration
**Impact:** ⭐⭐⭐⭐⭐ (Expected 3-5x speedup)  
**Difficulty:** ⚡⚡⚡⚡ Very Hard (1 week)  
**Risk:** 🔴 High

**Concept:**
- Early universe (a < 1e-4): Field frozen, use simple approximation
- Matter era (1e-4 < a < 0.1): Field evolving, full ODE
- Late times (a > 0.5): Field oscillating, switch to fluid

**Implementation:**
```c
if (a < pba->a_freeze_start) {
  // Frozen regime: phi = phi_i, no evolution needed
  phi_ridder = pba->theta_i * pba->f_eV;
  phi_prime_ridder = 0.0;
  // Fast path: no ODE solving
} else if (a > pba->a_oscillation) {
  // Fluid regime: use w_eff = -1 + delta
  // Fast path: algebraic w(a)
} else {
  // Full ODE integration (current expensive path)
}
```

**This is how Rock 'n' Roll EDE works in public CLASS versions!**

---

## 📊 Expected Cumulative Speedup

| Optimization | Individual | Cumulative |
|--------------|-----------|-----------|
| Baseline | 1.0x | 1.0x |
| + Relax tolerance | 2.5x | **2.5x** |
| + Disable tail (test) | 1.5x | **3.8x** |
| + Fast math (pow→mult) | 1.4x | **5.3x** |
| + Precompute Lambda^4 | 1.1x | **5.8x** |

**Target achieved:** 17 sec → 2.9 sec per step ✅

---

## 🚀 Implementation Timeline

### Week 1 (This Week)
**Goal:** Get from 17 sec → 5 sec per step

1. **Day 1 (Today):**
   - ✅ Diagnose problem (DONE)
   - ⏳ Apply Option 1B (disable tail)
   - ⏳ Apply Option 2A (fast math)
   - ⏳ Test and measure speedup

2. **Day 2:**
   - Apply Option 1A (relax tolerance)
   - Apply Option 2B (precompute Lambda^4)
   - Run 100-step test to verify

3. **Day 3:**
   - Profile to confirm remaining bottlenecks
   - Apply Option 2C if needed
   - Full validation test

### Week 2
**Goal:** Production deployment

4. **Days 4-5:**
   - Full tier 3 test (200 samples × 4 chains)
   - Monitor performance
   - Adjust if needed

5. **Days 6-7:**
   - Deploy to production (10,000 samples)

---

## 🔬 Validation Tests

After each optimization, run this test:

```bash
# Single CLASS evaluation timing test
cd ~/Ridder-Field
time ./phase2/class/class test_v3_minimal.ini

# Expected times:
# Before: ~0.5 sec
# After Option 2A: ~0.35 sec (1.4x faster)
# After Option 1A: ~0.15 sec (3x faster)
```

**Full MCMC test:**
```bash
# Run 20 steps, measure avg time
cd ~/Ridder-Field/phase3
./scripts/run_v3_tier3_test.sh

# Wait 5 minutes, check progress
python3 scripts/check_v3_tier3_status.py

# Count derivative calls
grep "DERIVS_ENTRY" chains/v3_tier3_test_chain1_work/chain1.log | tail -1

# Target: < 10,000 calls after 20 steps
```

---

## 📝 Implementation Patches

### Patch 1: Fast Math Optimization

Create file: `v3_fast_math.patch`

```patch
--- a/phase2/class/source/ridder_v3_potential.c
+++ b/phase2/class/source/ridder_v3_potential.c
@@ -70,7 +70,9 @@ static double V_EDE_v3(double theta, double a, const struct ridder_unified_para
   double S = S_time_window(a, rp->a_c, rp->sigma_lna);
   if (S < 1e-50) return 0.0;
   
-  double Lambda4 = pow(rp->Lambda_EDE_eV, 4.0);
+  double L = rp->Lambda_EDE_eV;
+  double L2 = L * L;
+  double Lambda4 = L2 * L2;  // Lambda^4 via 2 multiplications
   double B = B_field_bump(theta, rp->theta_E_center, rp->n_EDE);
   
   double V = Lambda4 * S * B;
@@ -160,7 +162,9 @@ static double V_tail_v3(double theta, const struct ridder_unified_params *rp) {
   if (!rp->use_tail) return 0.0;
   if (rp->Lambda_tail_eV <= 0.0) return 0.0;
   
-  double Lambda4 = pow(rp->Lambda_tail_eV, 4.0);
+  double L = rp->Lambda_tail_eV;
+  double L2 = L * L;
+  double Lambda4 = L2 * L2;
   
   double delta_theta = theta - rp->theta_T_center;
   double one_minus_cos = 1.0 - cos(delta_theta);
@@ -225,7 +229,9 @@ static double V_floor_v3(const struct ridder_unified_params *rp) {
 static double V_floor_v3(const struct ridder_unified_params *rp) {
   if (!rp->use_floor) return 0.0;
-  return pow(rp->Lambda_floor_eV, 4.0);
+  double L = rp->Lambda_floor_eV;
+  double L2 = L * L;
+  return L2 * L2;
 }
```

Apply with:
```bash
cd ~/Ridder-Field
patch -p1 < v3_fast_math.patch
cd phase2/class
make clean && make -j4
```

---

### Patch 2: Disable Tail for Testing

Create file: `v3_notail_test.patch`

```patch
--- a/phase3/ridder_v3_tier3_test.yaml
+++ b/phase3/ridder_v3_tier3_test.yaml
@@ -23,7 +23,7 @@ theory:
       
       # Tail component (Use TRGB calibration as starting point)
-      ridder_use_tail: "yes"
+      ridder_use_tail: "no"  # DISABLED FOR TESTING
       ridder_Lambda_tail_eV: 0.0012
       ridder_alpha_tail: 1.0
       ridder_theta_T_center: 0.0
```

---

## 📈 Success Criteria

**Minimum Acceptable Performance:**
- ✅ < 5 seconds per MCMC step
- ✅ < 10,000 derivative calls per step
- ✅ Full tier 3 test completes in < 2 hours

**Ideal Performance:**
- ⭐ < 3 seconds per MCMC step
- ⭐ < 5,000 derivative calls per step
- ⭐ Comparable to LCDM + simple EDE

---

## 🎬 Next Actions (Right Now)

```bash
# On VM:
ssh ridderadmin@172.174.34.125

# 1. Kill slow test
pkill -f cobaya

# 2. Apply fast math patch
cd ~/Ridder-Field
# Create and apply v3_fast_math.patch (see above)

# 3. Rebuild CLASS
cd phase2/class
make clean && make -j4

# 4. Run optimized test
cd ~/Ridder-Field/phase3
./scripts/run_v3_tier3_test.sh

# 5. Monitor for 5 minutes
watch -n 30 'python3 scripts/check_v3_tier3_status.py'

# 6. Check derivative count
grep "DERIVS_ENTRY" chains/v3_tier3_test_chain1_work/chain1.log | tail -1
```

**Expected result:** 5-10 steps in 5 minutes → 30-60 sec/step (better than 17 sec!)

---

## 📚 References

- CLASS integrator: `background.c:background_solve()` (line ~500)
- V3 potential: `ridder_v3_potential.c` (full file)
- MCMC config: `phase3/ridder_v3_tier3_test.yaml`
- Performance comparison: `V1_VS_V3_MCMC_COMPARISON.md`

**Last updated:** Nov 26, 2025 05:55 UTC

