# Quick Start: Next Steps

## ✅ What's Done

1. **1-minute smoke test** - CLASS works, r_s = 139.026 Mpc ✅
2. **Infrastructure** - Azure VM running, 4 cores available ✅
3. **Roadmap** - Complete testing ladder defined ✅

## ⏳ Next: 10-Minute Metropolis Test

**Purpose:** Verify sampler actually moves through parameter space

**Run on Azure VM:**
```bash
ssh ridderadmin@172.174.34.125
cd ~/Ridder-Field/phase3
python3 run_10min_metropolis_test.py
```

**What to check:**
- Acceptance rate should be 0.2 - 0.5
- Parameters should show movement (not stuck)
- Proposal scale should adapt
- No zero acceptance or crashes

**If it works:** Proceed to parallel chains test  
**If it fails:** Check likelihood function, proposal settings, prior ranges

---

## Files Created

### Test Scripts
- `phase3/ridder_10min_metropolis.yaml` - 10-minute test config
- `phase3/run_10min_metropolis_test.py` - Test runner
- `phase3/compare_lcdm_vs_ridder.py` - Comparison framework

### Configuration
- `phase3/data_ladder_profiles.yaml` - Data profiles (Planck, BAO, SH0ES, S₈)

### Documentation
- `MCMC_ROADMAP.md` - Complete roadmap with all phases
- `CLUSTER_ANALYSIS.md` - Cluster options and performance
- `CLUSTER_QUICK_ANSWER.md` - Quick cluster reference

---

## Testing Ladder

1. ✅ **Smoke test** (1 min) - CLASS works
2. ⏳ **Metropolis test** (10 min) - Sampler moves ← **YOU ARE HERE**
3. ⏸️ **Parallel chains** (30 min) - Chains converge
4. ⏸️ **Cluster test** (30 min) - Orchestration works
5. ⏸️ **Full MCMC** (hours) - Production runs

---

## Data Ladder

1. **Tier 1:** Planck-only → Baseline comparison
2. **Tier 2:** Planck + BAO → Standard baseline
3. **Tier 3:** Planck + BAO + SH0ES → H₀ tension test
4. **Tier 4:** Full core (+ S₈) → Complete analysis

---

## Quick Commands

```bash
# 10-minute Metropolis test
cd phase3
python3 run_10min_metropolis_test.py

# Compare ΛCDM vs Ridder (after running both)
python3 compare_lcdm_vs_ridder.py --profile planck_core --compare

# Run on cluster (after setup)
python3 run_mcmc_cluster.py --mode batch --batch-account ridder-batch
```

---

## Success Criteria

### Phase 2 (10-minute test)
- ✅ Acceptance rate: 0.2 - 0.5
- ✅ Parameters move
- ✅ No crashes

### Phase 3 (Parallel)
- ✅ R-1 < 0.1
- ✅ Chains converge
- ✅ No divergence

### Tier Comparisons
- ✅ Tier 1: Δχ² acceptable
- ✅ Tier 2: H₀ tension reduced
- ✅ Tier 3: H₀ compatible with SH0ES
- ✅ Tier 4: S₈ tension reduced

---

**Next Action:** Run the 10-minute Metropolis test on Azure VM

