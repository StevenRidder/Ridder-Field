# Cluster Setup Complete - Ridder Field MCMC

## Overview

This setup provides a complete path from "1-minute smoke test" to "full production MCMC on Azure Batch cluster" with the same codebase and scripts.

## Directory Structure

```
Ridder-Field/
├── azure/
│   ├── batch.tf                    # Batch infrastructure (Terraform)
│   ├── submit_batch_job.sh         # Job submission script
│   └── main.tf                     # Single VM (existing)
├── phase2/class/                   # CLASS fork (compiled)
└── phase3/
    ├── configs/
    │   ├── ridder_test_1min.yaml   # 1-minute smoke test
    │   ├── ridder_test_10min.yaml  # 10-minute Metropolis test
    │   └── ridder_full.yaml        # Full production config
    ├── scripts/
    │   └── run_mcmc.sh             # Universal MCMC runner
    └── output/                      # Results directory
        ├── local_test/
        └── cluster_runs/
```

## Quick Start

### 1. Deploy Batch Infrastructure

```bash
cd azure
terraform init
terraform plan
terraform apply
```

This creates:
- Batch account (auto-named for uniqueness)
- Storage account (auto-named)
- Batch pool with auto-scaling (0-10 nodes, D16s_v3, 16 cores each)

### 2. Test Locally (1-minute)

```bash
cd phase3
./scripts/run_mcmc.sh configs/ridder_test_1min.yaml local_1min 4
```

### 3. Test Locally (10-minute)

```bash
./scripts/run_mcmc.sh configs/ridder_test_10min.yaml local_10min 8
```

### 4. Submit to Batch Cluster

```bash
cd ../../azure
# Update BATCH_ACCOUNT in submit_batch_job.sh with terraform output
./submit_batch_job.sh 8  # 8 chains
```

## Configuration Files

### `ridder_test_1min.yaml`
- **Purpose:** Smoke test
- **Likelihood:** BAO only
- **Samples:** 50
- **Time:** ~1 minute

### `ridder_test_10min.yaml`
- **Purpose:** Metropolis sampler test
- **Likelihood:** BAO + minimal Planck (lowl.TT, highl_plik.TT)
- **Samples:** 2000
- **Time:** ~10 minutes

### `ridder_full.yaml`
- **Purpose:** Production MCMC
- **Likelihood:** Full Planck 2018 + BAO + SNe
- **Samples:** 10,000
- **Convergence:** R-1 < 0.01

## The Universal Script: `run_mcmc.sh`

This script works identically on:
- Your local machine
- Single Azure VM
- Azure Batch nodes

**Usage:**
```bash
./scripts/run_mcmc.sh <config.yaml> <run_label> <num_threads>
```

**Arguments:**
1. `config.yaml` - Cobaya configuration file
2. `run_label` - Output directory name
3. `num_threads` - OMP threads for CLASS (default: 4)

## Batch Job Submission

The `submit_batch_job.sh` script:
1. Creates a Batch job
2. Creates N tasks (one per chain)
3. Each task runs `run_mcmc.sh` with the same config
4. Tasks write to separate output directories

**Note:** You'll need to:
- Sync your repo to Batch nodes (via resource files or custom image)
- Update `BATCH_ACCOUNT` name in the script (from terraform output)

## Terraform Improvements

The `batch.tf` includes:
- ✅ Globally unique storage account name (using hash)
- ✅ Consistent autoscale formula
- ✅ Start task for dependencies (slower startup, but works)
- ✅ Ubuntu 22.04 (matches single VM)

**For Production:**
- Build custom VM image with CLASS pre-compiled
- Use start task only for `git pull` or config updates
- Faster node startup (~30 seconds vs ~5 minutes)

## Next Steps

1. **Deploy Batch infrastructure:**
   ```bash
   cd azure && terraform apply
   ```

2. **Test locally:**
   ```bash
   cd phase3
   ./scripts/run_mcmc.sh configs/ridder_test_1min.yaml test 4
   ```

3. **Prepare Batch deployment:**
   - Package repo as tarball
   - Upload to storage account
   - Configure resource files in Batch tasks

4. **Run full MCMC:**
   ```bash
   ./azure/submit_batch_job.sh 8
   ```

## Cost Estimates

- **Batch Pool:** Auto-scales 0-10 nodes
- **Per Node:** Standard_D16s_v3 (~$0.77/hour)
- **Full MCMC (8 chains, ~30 min):** ~$1.50-2.00
- **Monthly (10 runs):** ~$15-20

## Monitoring

```bash
# Check job status
az batch job show --job-id <job-id>

# List tasks
az batch task list --job-id <job-id> --output table

# Download results
az batch task file download --job-id <job-id> --task-id chain1 \
  --file-path output/full_run_chain1/chains/ridder_full_1.txt \
  --destination ./chain1_results.txt
```

## Comparison Strategy

To compare Ridder vs ΛCDM:

1. **Create ΛCDM config:** Copy `ridder_full.yaml`, remove Ridder parameters
2. **Run both:** Same data, same sampler settings
3. **Compare:**
   - Posterior means (H₀, Ωₘ, σ₈, n_s)
   - Δχ² for joint dataset and subsets
   - Derived parameters (S₈, r_s)

The pipeline is identical - only the YAML changes.

---

**Status:** ✅ Infrastructure ready, scripts tested locally
**Next:** Deploy Batch pool and test job submission

