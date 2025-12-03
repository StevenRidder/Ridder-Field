# Ridder Field MCMC: Complete Roadmap

**Date:** November 21, 2024  
**Status:** Phase 1 Complete (1-minute smoke test)  
**Next:** Phase 2 (10-minute Metropolis test)

---

## Overview

This roadmap implements a staged testing approach that builds confidence incrementally before scaling to full production MCMC. Each phase validates a specific component before moving to the next.

---

## Testing Ladder

### Phase 1: Smoke Test ✅ COMPLETE
**Status:** ✅ Passed  
**Duration:** ~1 minute  
**Purpose:** Verify CLASS runs with Ridder field

**What it tests:**
- CLASS compilation and execution
- Ridder field parameters read correctly
- Basic output generation (r_s calculation)
- No crashes or numerical errors

**Results:**
- ✅ All 9 parameter combinations passed
- ✅ r_s = 139.026 Mpc (target: 139.06 Mpc)
- ✅ No crashes or NaN values

**Files:**
- `phase3/run_direct_class_test.sh`
- `MCMC_1MINUTE_TEST_RESULTS.md`

---

### Phase 2: 10-Minute Metropolis Sampler ⏳ NEXT
**Status:** ⏳ Ready to run  
**Duration:** ~10 minutes  
**Purpose:** Verify sampler moves through parameter space

**What it tests:**
- Proposal adaptation works
- Acceptance rate is reasonable (0.2-0.5)
- Parameters actually move (not stuck)
- Likelihood surface is accessible
- No zero acceptance or proposal collapse

**Success Criteria:**
- ✅ Acceptance rate: 0.2 - 0.5
- ✅ Parameters show movement in traces
- ✅ Proposal scale adapts
- ✅ No crashes or zero acceptance

**Files:**
- `phase3/ridder_10min_metropolis.yaml`
- `phase3/run_10min_metropolis_test.py`

**Run:**
```bash
cd phase3
python3 run_10min_metropolis_test.py
```

**If it fails:**
- Zero acceptance → Likelihood or proposal issue
- Parameters stuck → Check prior ranges
- Proposal collapse → Check proposal adaptation settings

---

### Phase 3: Parallel Chains Test
**Status:** ⏳ Pending Phase 2  
**Duration:** ~20-30 minutes  
**Purpose:** Verify multiple chains stay coherent

**What it tests:**
- 4-8 chains run in parallel
- Chains converge toward same region
- No wild divergence
- R-1 statistic works correctly

**Success Criteria:**
- ✅ All chains converge (R-1 < 0.1)
- ✅ Chains don't drift in opposite directions
- ✅ Posterior distributions overlap
- ✅ No chain-specific failures

**Implementation:**
- Use `run_mcmc_cluster.py --mode single --chains 4`
- Or MPI: `mpirun -np 4 python3 run_mcmc_cluster.py --mode mpi`

---

### Phase 4: Cluster Launcher Test
**Status:** ⏳ Pending Phase 3  
**Duration:** ~30 minutes  
**Purpose:** Verify cluster orchestration works

**What it tests:**
- Azure Batch (or MPI cluster) spins up workers
- Jobs distribute correctly
- Results collect properly
- Workers tear down cleanly

**Success Criteria:**
- ✅ Workers start successfully
- ✅ Jobs distribute across VMs
- ✅ Results aggregate correctly
- ✅ No orphaned processes

**Implementation:**
- Azure Batch: `./azure/setup_batch.sh` then submit test job
- MPI: Deploy 4 VMs, test MPI coordination

---

### Phase 5: Full MCMC Production
**Status:** ⏳ Pending Phase 4  
**Duration:** Hours to days  
**Purpose:** Production runs with real data

**What it runs:**
- Full data ladder (see below)
- Many chains (8-16)
- Full convergence (R-1 < 0.01)
- Production corner plots

---

## Data Ladder

### Tier 1: Planck-Only
**Purpose:** Baseline CMB-only comparison

**Likelihoods:**
- `planck_2018_lowl.TT`
- `planck_2018_lowl.EE`
- `planck_2018_highl_plik.TTTEEE`
- `planck_2018_lensing.clik`

**Comparison:**
- ΛCDM vs Ridder
- Best-fit χ²
- Δχ²
- Posteriors on θᵢ, Ω_scf, β
- Derived: H₀, r_s, S₈

**Profile:** `planck_core`

---

### Tier 2: Planck + BAO
**Purpose:** Standard baseline (most papers use this)

**Likelihoods:**
- All Planck (Tier 1)
- `bao_boss` (BOSS DR12)
- `bao_6df` (6dF)
- `bao_mgs` (MGS)

**Comparison:**
- ΛCDM: "Gold standard" fit
- Ridder: Slightly worse χ², but better H₀
- Goal: Relieve H₀ tension without destroying Planck + BAO

**Profile:** `planck_bao`

---

### Tier 3: Planck + BAO + SH0ES
**Purpose:** Test H₀ tension relief

**Likelihoods:**
- All Planck + BAO (Tier 2)
- `sh0es_h0` (H₀ = 73.0 ± 1.0 km/s/Mpc)

**Comparison:**
- Under ΛCDM: Adding SH0ES usually blows up χ²
- Under Ridder:
  - H₀ posterior shifts higher toward SH0ES
  - χ² penalty from SH0ES drops
  - Model compatible with both

**Key Plots:**
- H₀ posterior: ΛCDM vs Ridder, with SH0ES prior
- Δχ² vs ΛCDM as SH0ES is added

**Profile:** `planck_bao_sh0es`

---

### Tier 4: Full Core (Planck + BAO + SH0ES + S₈)
**Purpose:** Complete tension test

**Likelihoods:**
- All Planck + BAO + SH0ES (Tier 3)
- `s8_prior` (S₈ = 0.76 ± 0.02 from lensing)

**Comparison:**
- S₈ posterior: ΛCDM vs Ridder
- Does Ridder naturally reduce S₈ tension?
- Does it conflict with Planck?

**Success:** Ridder keeps Planck happy, raises H₀, lowers S₈

**Profile:** `full_core`

---

## Implementation Files

### Test Scripts
- `phase3/run_direct_class_test.sh` - 1-minute smoke test ✅
- `phase3/run_10min_metropolis_test.py` - 10-minute Metropolis test ⏳
- `phase3/run_mcmc_cluster.py` - Cluster-aware runner
- `phase3/compare_lcdm_vs_ridder.py` - Comparison framework

### Configuration Files
- `phase3/ridder_10min_metropolis.yaml` - 10-minute test config
- `phase3/data_ladder_profiles.yaml` - Data profile definitions
- `phase3/ridder_local_test.yaml` - Local test config

### Infrastructure
- `azure/setup_batch.sh` - Azure Batch setup
- `CLUSTER_ANALYSIS.md` - Cluster options and analysis
- `CLUSTER_QUICK_ANSWER.md` - Quick cluster reference

---

## Execution Plan

### Immediate (Today)
1. ✅ Complete 1-minute smoke test
2. ⏳ Run 10-minute Metropolis test
3. ⏳ Verify acceptance rate and parameter movement

### This Week
1. Run parallel chains test (4 chains)
2. Set up Azure Batch
3. Test cluster launcher
4. Run Tier 1 (Planck-only) comparison

### Next Week
1. Run Tier 2 (Planck + BAO) comparison
2. Analyze Δχ² and posteriors
3. Run Tier 3 (Planck + BAO + SH0ES)
4. Generate H₀ tension plots

### Following Weeks
1. Run Tier 4 (Full core)
2. Generate production plots
3. Write paper sections
4. Sensitivity analysis

---

## Success Metrics

### Phase 2 (10-Minute Test)
- Acceptance rate: 0.2 - 0.5 ✅
- Parameters move: Yes ✅
- No crashes: Yes ✅

### Phase 3 (Parallel Chains)
- R-1 < 0.1: Yes ✅
- Chains converge: Yes ✅
- No divergence: Yes ✅

### Phase 4 (Cluster)
- Workers start: Yes ✅
- Jobs distribute: Yes ✅
- Results collect: Yes ✅

### Tier Comparisons
- Tier 1: Δχ² acceptable
- Tier 2: H₀ tension reduced
- Tier 3: H₀ compatible with SH0ES
- Tier 4: S₈ tension reduced

---

## Diagnostic Tests (1-Minute Each)

Once each phase works, turn it into a permanent 1-minute diagnostic:

1. **Smoke test** → Checks CLASS ✅
2. **Metropolis test** → Checks sampler stability
3. **Parallel test** → Checks chain coherence
4. **Cluster test** → Checks scaling

Chain these together for fast system validation after code changes.

---

## Troubleshooting Guide

### Zero Acceptance Rate
- **Cause:** Likelihood or proposal issue
- **Fix:** Check likelihood function, verify CLASS outputs, adjust proposal scale

### Parameters Stuck
- **Cause:** Prior ranges too narrow, proposal too small
- **Fix:** Widen priors, increase proposal scale

### Proposal Collapse
- **Cause:** Adaptation algorithm issue
- **Fix:** Check `learn_proposal` settings, verify adaptation logic

### Chains Diverge
- **Cause:** Likelihood discontinuity, sampling temperature
- **Fix:** Check likelihood smoothness, verify temperature settings

### Cluster Issues
- **Cause:** Network, authentication, or job distribution
- **Fix:** Check SSH keys, verify network connectivity, test job submission

---

## Cost Estimates

| Phase | Duration | Cost | Purpose |
|-------|----------|------|---------|
| Smoke test | 1 min | $0.003 | Basic functionality |
| Metropolis test | 10 min | $0.03 | Sampler validation |
| Parallel test | 30 min | $0.10 | Chain coherence |
| Cluster test | 30 min | $0.10 | Orchestration |
| Tier 1 (Planck) | 2-4 hours | $0.40-0.80 | Baseline comparison |
| Tier 2 (Planck+BAO) | 4-8 hours | $0.80-1.60 | Standard baseline |
| Tier 3 (+SH0ES) | 6-12 hours | $1.20-2.40 | H₀ tension |
| Tier 4 (Full) | 12-24 hours | $2.40-4.80 | Complete analysis |

**Total estimated cost:** ~$10-15 for complete analysis

---

## Next Steps

1. **Run 10-minute Metropolis test** (Phase 2)
2. **Verify acceptance and movement**
3. **Proceed to parallel chains** (Phase 3)
4. **Set up cluster** (Phase 4)
5. **Run Tier 1 comparison** (Planck-only)

---

*Last Updated: November 21, 2024*
