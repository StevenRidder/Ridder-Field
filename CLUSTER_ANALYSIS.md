# Ridder Field MCMC: Cluster Analysis & Scaling Plan

**Date:** November 21, 2024  
**Current Status:** Single VM Test Environment  
**Target:** Production MCMC Cluster

---

## Current Infrastructure

### Deployed Resources
- **VMs:** 1 × Standard_D4s_v3
- **Total vCPUs:** 4 cores
- **Total RAM:** 16 GB
- **Storage:** Premium SSD
- **Location:** Azure (West US 2)
- **IP:** 172.174.34.125

### VM Specifications (Standard_D4s_v3)
- **vCPUs:** 4
- **RAM:** 16 GB
- **Max IOPS:** 6,400
- **Max Throughput:** 96 MB/s
- **Network:** Up to 2,000 Mbps
- **Cost:** ~$0.192/hour (~$140/month if running 24/7)

---

## MCMC Runtime Estimates

### Single CLASS Run Performance
Based on test results:
- **Single CLASS execution:** ~5-10 seconds per parameter combination
- **Output generation:** ~1-2 seconds
- **Total per sample:** ~6-12 seconds

### MCMC Chain Requirements
- **Target samples:** 5,000 - 10,000 (for convergence)
- **Burn-in:** ~1,000 samples (discarded)
- **Effective samples needed:** ~4,000 - 9,000

### Runtime Projections

#### Single VM (Current Setup)
- **4 cores, sequential:** 10,000 samples × 10 sec = **100,000 seconds = ~28 hours**
- **4 cores, parallel (4 chains):** 4 chains × 2,500 samples × 10 sec = **25,000 seconds = ~7 hours**
- **4 cores, parallel (4 chains, optimized):** ~**5-6 hours** (with overhead)

#### Cluster Options

**Option 1: 4 VMs (16 cores total)**
- **4 chains, 4 VMs:** ~**1.5-2 hours**
- **Cost:** ~$0.77/hour = ~$1.50-2.00 per full MCMC run

**Option 2: 8 VMs (32 cores total)**
- **8 chains, 8 VMs:** ~**45-60 minutes**
- **Cost:** ~$1.54/hour = ~$1.00-1.50 per full MCMC run

**Option 3: 16 VMs (64 cores total)**
- **16 chains, 16 VMs:** ~**20-30 minutes**
- **Cost:** ~$3.07/hour = ~$1.00-1.50 per full MCMC run

**Option 4: Azure Batch (Auto-scaling)**
- **Dynamic scaling:** Start with 4 VMs, scale to 16+ as needed
- **Cost:** Pay only for compute time used
- **Runtime:** ~**20-30 minutes** (with auto-scaling)

---

## Cluster Configuration Options

### Option A: Manual MPI Cluster (Recommended for Control)

**Architecture:**
- Multiple VMs in same VNet
- OpenMPI or MPICH for parallel execution
- Shared storage (Azure Files) for results
- Master node coordinates workers

**Setup Steps:**
1. Deploy N VMs (N = desired cores / 4)
2. Install OpenMPI on all nodes
3. Configure SSH keys for passwordless access
4. Set up shared storage (Azure Files)
5. Configure MPI hostfile
6. Run MCMC with MPI parallelization

**Pros:**
- Full control over execution
- Can use existing CLASS parallelization
- Easy to debug
- Cost-effective for long runs

**Cons:**
- Manual setup required
- Need to manage VM lifecycle
- No auto-scaling

### Option B: Azure Batch (Recommended for Production)

**Architecture:**
- Azure Batch pool with auto-scaling
- Job scheduling built-in
- Automatic VM management
- Pay-per-use pricing

**Setup Steps:**
1. Create Azure Batch account
2. Create pool with VM configuration
3. Define job with task parallelism
4. Submit MCMC job
5. Batch handles scaling and execution

**Pros:**
- Automatic scaling
- Built-in job scheduling
- Pay only for compute time
- Handles VM lifecycle automatically
- Best for production workloads

**Cons:**
- Requires Azure Batch setup
- Less control over individual VMs
- Learning curve for Batch API

### Option C: Kubernetes Cluster (Advanced)

**Architecture:**
- Azure Kubernetes Service (AKS)
- Containerized CLASS execution
- Horizontal pod autoscaling
- Job scheduling with Kubernetes

**Pros:**
- Modern containerized approach
- Excellent scaling
- Good for microservices architecture

**Cons:**
- Complex setup
- Overkill for this use case
- Higher overhead

---

## Recommended Approach: Azure Batch

### Why Azure Batch?
1. **Auto-scaling:** Start small, scale up automatically
2. **Cost-effective:** Pay only for compute time
3. **Built-in job management:** No need to manage VMs manually
4. **Production-ready:** Designed for HPC workloads

### Implementation Plan

#### Phase 1: Setup Azure Batch (30 minutes)
```bash
# Create Batch account
az batch account create \
  --resource-group ridder-cosmology-rg \
  --name ridder-batch \
  --location westus2 \
  --storage-account ridderbatchstorage

# Create pool with 4-16 VMs
az batch pool create \
  --pool-id ridder-pool \
  --vm-size Standard_D4s_v3 \
  --target-dedicated-nodes 4 \
  --target-low-priority-nodes 0 \
  --image canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2
```

#### Phase 2: Prepare MCMC Job (1 hour)
- Package CLASS binary and configs
- Create job definition
- Define task parallelism
- Set up result storage

#### Phase 3: Run MCMC (20-30 minutes)
- Submit job to Batch
- Monitor progress
- Collect results

### Cost Estimate
- **Setup time:** ~1.5 hours (one-time)
- **Per MCMC run:** ~$1.00-2.00 (20-30 minutes of compute)
- **Monthly (10 runs):** ~$10-20

---

## Alternative: Manual MPI Cluster Setup

If you prefer manual control, here's the setup:

### Step 1: Deploy Additional VMs
```bash
# Deploy 3 more VMs (total 4 VMs = 16 cores)
for i in {2..4}; do
  az vm create \
    --resource-group ridder-cosmology-rg \
    --name ridder-compute-0$i \
    --image Ubuntu2204 \
    --size Standard_D4s_v3 \
    --admin-username ridderadmin \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --vnet-name ridder-vnet \
    --subnet internal
done
```

### Step 2: Install OpenMPI on All Nodes
```bash
# On each VM
sudo apt update
sudo apt install -y openmpi-bin libopenmpi-dev
```

### Step 3: Configure SSH Keys
```bash
# On master node (ridder-compute-01)
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
# Copy to all worker nodes
for i in {2..4}; do
  ssh-copy-id ridderadmin@ridder-compute-0$i
done
```

### Step 4: Create MPI Hostfile
```bash
# ~/mpi_hosts
ridder-compute-01 slots=4
ridder-compute-02 slots=4
ridder-compute-03 slots=4
ridder-compute-04 slots=4
```

### Step 5: Run Parallel MCMC
```bash
# Run 4 parallel chains
mpirun -np 4 --hostfile ~/mpi_hosts \
  python3 run_mcmc_parallel.py
```

---

## Performance Optimization

### 1. CLASS Compilation Flags
- Already using `-O3` optimization
- Consider `-march=native` for CPU-specific optimizations
- OpenMP parallelization (if CLASS supports it)

### 2. MCMC Parallelization Strategies

**Strategy A: Multiple Chains (Recommended)**
- Run 4-8 independent chains in parallel
- Each chain samples different regions
- Faster convergence, better diagnostics

**Strategy B: Parallel Likelihood Evaluation**
- Evaluate multiple parameter sets simultaneously
- Requires custom MCMC implementation
- More complex but potentially faster

**Strategy C: Hybrid Approach**
- Multiple chains + parallel likelihood evaluation
- Best performance but most complex

### 3. Storage Optimization
- Use Azure Premium SSD for I/O
- Consider Azure Files for shared storage
- Cache frequently used data

---

## Recommended Configuration

### For Initial Testing (Now)
- **1 VM (4 cores):** Current setup
- **Runtime:** ~7 hours for 10,000 samples
- **Cost:** ~$1.50 per run

### For Production MCMC (Recommended)
- **Azure Batch Pool:** 8-16 VMs (32-64 cores)
- **Runtime:** ~20-30 minutes for 10,000 samples
- **Cost:** ~$1.00-2.00 per run
- **Auto-scaling:** Start with 4, scale to 16 as needed

### For Large-Scale Analysis
- **Azure Batch Pool:** 32+ VMs (128+ cores)
- **Runtime:** ~5-10 minutes for 10,000 samples
- **Cost:** ~$2.00-4.00 per run
- **Use case:** Multiple parameter spaces, sensitivity analysis

---

## Next Steps

1. **Immediate (Today):**
   - Fix Python wrapper for Cobaya integration
   - Test single VM with 4 parallel chains
   - Measure actual performance

2. **Short-term (This Week):**
   - Set up Azure Batch account
   - Create pool with 4-8 VMs
   - Run first production MCMC

3. **Medium-term (Next Week):**
   - Optimize CLASS compilation
   - Implement result aggregation
   - Set up monitoring and alerts

4. **Long-term (Ongoing):**
   - Auto-scale based on queue depth
   - Implement result caching
   - Set up automated analysis pipeline

---

## Cost Summary

| Configuration | VMs | Cores | Runtime | Cost/Run | Monthly (10 runs) |
|--------------|-----|-------|---------|----------|-------------------|
| Current (1 VM) | 1 | 4 | ~7 hours | ~$1.50 | ~$15 |
| Small Cluster | 4 | 16 | ~2 hours | ~$1.50 | ~$15 |
| Medium Cluster | 8 | 32 | ~1 hour | ~$1.50 | ~$15 |
| Large Cluster | 16 | 64 | ~30 min | ~$2.00 | ~$20 |
| Azure Batch | 8-16 | 32-64 | ~30 min | ~$1.50 | ~$15 |

**Note:** Azure Batch costs are similar but include automatic scaling and management overhead.

---

## Conclusion

**Current Setup:**
- 1 VM, 4 cores
- Sufficient for testing
- ~7 hours for full MCMC

**Recommended Production Setup:**
- Azure Batch with 8-16 VMs (32-64 cores)
- ~20-30 minutes for full MCMC
- Auto-scaling and cost-effective

**Next Action:**
Set up Azure Batch for production MCMC runs.

---

*Generated: November 21, 2024*

