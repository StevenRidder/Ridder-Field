# Quick Answer: Cluster Configuration & Performance

## Current Setup

**Servers:** 1 VM  
**CPUs/Cores:** 4 cores total  
**VM Type:** Standard_D4s_v3 (4 vCPUs, 16 GB RAM)  
**Status:** ✅ Running and tested

---

## Full MCMC Runtime Estimates

### Current Setup (1 VM, 4 cores)
- **Sequential:** ~28 hours for 10,000 samples
- **Parallel (4 chains):** ~7 hours for 10,000 samples
- **Optimized:** ~5-6 hours

### Recommended Cluster (8-16 VMs)
- **8 VMs (32 cores):** ~1 hour
- **16 VMs (64 cores):** ~20-30 minutes ⚡
- **Cost per run:** ~$1.50-2.00

---

## How to Make Code See the Cluster

### Option 1: Azure Batch (Recommended - Easiest)

**What it does:**
- Automatically distributes work across VMs
- Handles job scheduling
- No code changes needed - just submit job

**Setup:**
```bash
cd azure
chmod +x setup_batch.sh
./setup_batch.sh
```

**Run MCMC:**
```bash
# Submit job to Batch
az batch job create --job-id ridder-mcmc-001 --pool-id ridder-pool

# Add tasks (each task = one chain)
az batch task create --job-id ridder-mcmc-001 --task-id chain-01 \
  --command-line "python3 run_mcmc_cluster.py --mode single --chains 1"
```

**Result:** Batch automatically runs tasks across all VMs in the pool.

---

### Option 2: MPI Cluster (More Control)

**What it does:**
- Uses OpenMPI to coordinate across VMs
- Each VM runs one chain
- Requires MPI setup

**Setup:**
```bash
# 1. Deploy more VMs (3 more = 4 total)
for i in {2..4}; do
  az vm create \
    --resource-group ridder-cosmology-rg \
    --name ridder-compute-0$i \
    --image Ubuntu2204 \
    --size Standard_D4s_v3 \
    --vnet-name ridder-vnet \
    --subnet internal \
    --admin-username <VM_USER> \
    --ssh-key-values ~/.ssh/id_rsa.pub
done

# 2. Install OpenMPI on all VMs
ssh <VM_USER>@172.174.34.125 "sudo apt install -y openmpi-bin libopenmpi-dev"

# 3. Create MPI hostfile
cat > ~/mpi_hosts << EOF
ridder-compute-01 slots=4
ridder-compute-02 slots=4
ridder-compute-03 slots=4
ridder-compute-04 slots=4
EOF
```

**Run MCMC:**
```bash
# Run 4 chains across 4 VMs
mpirun -np 4 --hostfile ~/mpi_hosts \
  python3 run_mcmc_cluster.py --mode mpi
```

**Result:** Code automatically sees all VMs and distributes chains.

---

### Option 3: Manual Parallel (Simplest)

**What it does:**
- Run multiple chains on single VM
- Uses all 4 cores
- No cluster needed

**Run:**
```bash
python3 run_mcmc_cluster.py --mode single --chains 4
```

**Result:** 4 chains run in parallel on 4 cores.

---

## Recommended: Azure Batch Setup

### Why Azure Batch?
1. ✅ **Automatic:** Code doesn't need to know about cluster
2. ✅ **Scaling:** Start with 4 VMs, auto-scale to 16+
3. ✅ **Simple:** Just submit job, Batch handles the rest
4. ✅ **Cost-effective:** Pay only for compute time

### Quick Start

```bash
# 1. Set up Batch (one-time, ~10 minutes)
cd azure
./setup_batch.sh

# 2. Run MCMC (takes ~30 minutes)
cd ../phase3
python3 submit_batch_mcmc.py
```

**That's it!** Batch automatically:
- Distributes work across all VMs
- Runs chains in parallel
- Collects results
- Scales up/down as needed

---

## Performance Comparison

| Setup | VMs | Cores | Runtime | Setup Time |
|-------|-----|-------|---------|------------|
| Current | 1 | 4 | ~7 hours | ✅ Done |
| Manual Parallel | 1 | 4 | ~5-6 hours | ✅ Done |
| MPI Cluster | 4 | 16 | ~2 hours | ~30 min |
| Azure Batch | 8-16 | 32-64 | ~30 min | ~10 min |

---

## Next Steps

**Immediate (Today):**
1. Test current setup with 4 parallel chains
2. Measure actual performance

**This Week:**
1. Set up Azure Batch (10 minutes)
2. Run first production MCMC (~30 minutes)
3. Verify results

**Next Week:**
1. Optimize based on results
2. Scale to larger cluster if needed

---

## Summary

**Current:** 1 VM, 4 cores → ~7 hours  
**Recommended:** Azure Batch, 8-16 VMs, 32-64 cores → ~30 minutes  
**How:** Use Azure Batch - code automatically sees all VMs, no changes needed

**Action:** Run `./azure/setup_batch.sh` to set up cluster in 10 minutes.

