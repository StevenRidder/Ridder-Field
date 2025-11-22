# Tier 1 Planck MCMC: Current Status

**Last Check:** $(date)

## Summary

**Status:** ⚠️ **Only 1 of 4 chains running**

### The Problem

- **Chain 1:** ✅ Running successfully (computing likelihoods)
- **Chains 2, 3, 4:** ❌ Failed due to file locking errors

The file locking issue persists despite setting `COBAYA_USE_FILE_LOCKING=False`. This is because:
1. Each chain is trying to write to the same checkpoint/progress files
2. Even with unique output paths, Cobaya creates shared metadata files
3. The environment variable may not be propagating correctly to all subprocesses

## What Chain 1 is Doing

Chain 1 is actively:
- Computing CLASS Boltzmann solutions for each parameter proposal
- Evaluating Planck 2018 likelihoods (TT, EE, TTTEEE, lensing)
- Starting at `theta_i_ridder = 2.1` (Ridder valley) as configured
- Building the chain file (will appear as `chains/ridder_tier1_planck_chain1.txt`)

**Expected:** First sample typically takes 5-10 minutes due to:
- High `l_max_scalars = 2508` (Planck requires high resolution)
- Multiple likelihood evaluations
- CLASS computation for each parameter set

## What Needs to Happen

To get all 4 chains running:

1. **Option A:** Run chains sequentially (one at a time) - slower but guaranteed to work
2. **Option B:** Fix file locking by ensuring environment variable propagates correctly
3. **Option C:** Use Cobaya's built-in MPI support (if available)
4. **Option D:** Run chains on separate VMs (not possible with current quota)

## Current Recommendation

**Let Chain 1 run to completion** - it will still provide useful results, just without R-1 convergence diagnostics. Then we can:
- Analyze the single chain results
- Determine if theta_i stays near 2.1 (Ridder valley) or drifts
- Decide if we need to fix the parallel execution or proceed with sequential chains

## Next Steps

1. Wait for Chain 1 to produce first samples (~5-10 more minutes)
2. Check if `theta_i_ridder` values are near 2.1 (Ridder physics) or have drifted to ~0.5 (ΛCDM)
3. If Chain 1 works well, we can run 3 more chains sequentially after it completes

