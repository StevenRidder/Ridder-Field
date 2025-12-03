# Azure Resource Audit

**Date**: November 22, 2025  
**Subscription**: Pay-As-You-Go (<SUBSCRIPTION_ID>)

## Current Running Resources

### Virtual Machines (2 total)

#### 1. **training** (Taikun Action Engine)
- **Resource Group**: MaxwellTraining
- **Location**: East US
- **Size**: Standard_NC4as_T4_v3 (4 vCPUs, 28 GB RAM, NVIDIA T4 GPU)
- **Status**: ⚪ **DEALLOCATED** (not incurring compute charges)
- **Private IP**: 10.0.0.4
- **Public IP**: <VM_IP>
- **Purpose**: Taikun Action Engine / ML Training
- **Cost**: $0/day (deallocated)

#### 2. **ridder-compute-01** (Ridder Field MCMC)
- **Resource Group**: ridder-cosmology-rg
- **Location**: East US
- **Size**: Standard_D4s_v3 (4 vCPUs, 16 GB RAM)
- **Status**: 🟢 **RUNNING** (actively incurring charges)
- **Private IP**: 10.0.2.4
- **Public IP**: <VM_IP>
- **Purpose**: Ridder Field MCMC computations
- **Cost**: ~$0.192/hour = **$4.61/day** = **$138/month**
- **Current Usage**: 4 vCPUs used out of 10 vCPU quota

### Resource Groups (5 total)

1. **MaxwellTraining** (East US)
   - Contains: training VM (deallocated)
   - Status: Inactive

2. **ridder-cosmology-rg** (East US)
   - Contains: ridder-compute-01 VM (running)
   - Status: Active

3. **ridder-batch-rg** (East US)
   - Contains: Storage account (riddercosmo1ab20339)
   - Status: Storage only, no compute
   - Cost: ~$0.10/day for storage

4. **NetworkWatcherRG** (East US)
   - Azure-managed network monitoring
   - Cost: Minimal

5. **DefaultResourceGroup-WUS** (West US)
   - Default resource group
   - Status: Empty

## Current Costs

### Daily Costs
- **ridder-compute-01**: $4.61/day (running)
- **Storage**: ~$0.10/day
- **Networking**: ~$0.05/day
- **Total**: ~**$4.76/day** = **$143/month**

### Quota Usage (East US)
- **Total Regional vCPUs**: 4/14 used (10 available)
- **DSv3 Family vCPUs**: 4/10 used (6 available)
- **NC4as_T4_v3**: 4/4 used (deallocated, but counts toward quota)

## Recommendations

### Immediate Actions

#### 1. **Keep Running**
- ✅ **ridder-compute-01**: Currently running Tier 3 MCMC (now stopped)
- **Action**: Keep for multi-region deployment testing

#### 2. **Already Deallocated**
- ✅ **training VM**: Already stopped (good!)
- **Action**: None needed

#### 3. **Clean Up Unused Resources**
- ⚠️ **ridder-batch-rg**: Has storage account but no Batch account deployed
- **Action**: Either deploy Batch or delete resource group
- **Savings**: $0.10/day (minimal)

### Multi-Region Deployment Plan

When you deploy the multi-region cluster:
- **New Resource Group**: ridder-batch-multiregion-rg
- **Location**: Australia East (primary)
- **Resources**: 
  - 1 Batch Account
  - 1 Storage Account
  - 4 Batch Pools (Australia East, Southeast Asia, East Asia, Japan East)
  - 4 VMs (1x F8s_v2 per region)
- **Additional Cost**: $48.72/day while running
- **Total Cost**: $4.76 + $48.72 = **$53.48/day** during MCMC runs

### Cost Optimization

#### Option 1: Keep Current Setup
- **Cost**: $4.76/day = $143/month
- **Capacity**: 4 parallel chains
- **Use Case**: Small tests, development

#### Option 2: Deploy Multi-Region for Production Runs
- **Cost**: $53.48/day when running
- **Capacity**: 32 parallel chains
- **Use Case**: Production MCMC (run for 1-2 days, then tear down)
- **Strategy**: Deploy → Run MCMC → Tear Down → Save results
- **Effective Cost**: ~$100-150 for a full production run

#### Option 3: Request Quota + Single Region (Future)
- **Cost**: $162/day when running (10x F16s_v2)
- **Capacity**: 160 parallel chains
- **Use Case**: Final publication-quality runs
- **Strategy**: Deploy for 1 day, get 10,000+ samples per chain

## Action Items

### Tonight
- [ ] Deploy multi-region Batch (4 regions, 32 chains)
- [ ] Run 1-minute test to verify setup
- [ ] Tear down if successful (or keep for Tier 1 run)

### This Week
- [ ] Request quota increase (200 vCPUs in Australia East)
- [ ] Run production Tier 1 and Tier 3 on multi-region
- [ ] Clean up ridder-batch-rg if not using

### Next Week
- [ ] Consolidate to single-region after quota approval
- [ ] Run final publication-quality MCMC (10,000 samples)

## Summary

**Current State**: Minimal resources running, low cost ($4.76/day)

**Ready to Deploy**: Multi-region cluster for 8x speedup

**Cost-Effective Strategy**: Deploy on-demand for production runs, tear down when done

**No Surprises**: All resources accounted for, no orphaned VMs

