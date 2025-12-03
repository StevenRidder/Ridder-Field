# Azure VM Guide for Scientific Computing

**Last Updated**: December 2025  
**Purpose**: Reference for MCMC chain runs and cosmology computations

---

## Quick Reference: What We Used

| VM | Size | vCPUs | RAM | Cost | Location |
|----|------|-------|-----|------|----------|
| ridder-compute-01 | D4s_v3 | 4 | 16 GB | $0.19/hr (~$140/mo) | eastus |
| ridder-australia-01 | F8s_v2 | 8 | 16 GB | $0.34/hr (~$245/mo) | australiaeast |

**Status**: Both deallocated (not running, not costing compute)

---

## VM Tiers for MCMC/Scientific Work

### 💚 Budget Tier (~$30-60/month)

| Size | vCPUs | RAM | $/hr | $/month | Best For |
|------|-------|-----|------|---------|----------|
| B2s | 2 | 4 GB | $0.04 | ~$30 | Light testing, dev |
| B2ms | 2 | 8 GB | $0.08 | ~$60 | Small chains, overnight runs |
| B4ms | 4 | 16 GB | $0.17 | ~$120 | Medium chains |

*B-series = "Burstable" — cheap baseline, can burst when needed*

### 💛 Mid Tier (~$70-150/month) ⭐ RECOMMENDED

| Size | vCPUs | RAM | $/hr | $/month | Best For |
|------|-------|-----|------|---------|----------|
| D2s_v5 | 2 | 8 GB | $0.10 | ~$70 | Single chain |
| **D4s_v5** | 4 | 16 GB | $0.19 | ~$140 | 2-4 parallel chains |
| D8s_v5 | 8 | 32 GB | $0.38 | ~$280 | Full Tier 5 production |
| **D4as_v5** ⭐ | 4 | 16 GB | $0.17 | ~$125 | Same as D4s, AMD (cheaper) |
| D8as_v5 | 8 | 32 GB | $0.34 | ~$250 | Same as D8s, AMD (cheaper) |

*D-series v5 = Latest gen, best price/performance*  
*"as" = AMD processors (10-20% cheaper than Intel "s" series)*

### 🔴 High Performance (~$200-500/month)

| Size | vCPUs | RAM | $/hr | $/month | Best For |
|------|-------|-----|------|---------|----------|
| D16s_v5 | 16 | 64 GB | $0.77 | ~$560 | Massive parallel runs |
| E4s_v5 | 4 | 32 GB | $0.25 | ~$185 | Memory-heavy workloads |
| E8s_v5 | 8 | 64 GB | $0.50 | ~$365 | Very memory-heavy |
| F8s_v2 | 8 | 16 GB | $0.34 | ~$245 | Raw CPU speed |
| F16s_v2 | 16 | 32 GB | $0.68 | ~$490 | Maximum CPU throughput |

*E-series = Memory-optimized*  
*F-series = CPU-optimized (highest clock speeds)*

---

## Recommendations by Task

### For Ridder Field MCMC Chains

| Task | Recommended VM | Cost | Est. Runtime |
|------|----------------|------|--------------|
| Quick smoke test | B2ms | $0.08/hr | 1-2 hrs |
| Single Tier 5 chain | D2s_v5 | $0.10/hr | 8-12 hrs |
| Production (4 chains) | **D4as_v5** ⭐ | $0.17/hr | 24 hrs |
| Rush job (8 chains) | D8as_v5 | $0.34/hr | 12 hrs |
| Full Tier 5 suite | D8s_v5 | $0.38/hr | 48 hrs |

### Cost Examples

| Scenario | VM | Hours | Total Cost |
|----------|-----|-------|------------|
| One overnight chain | D2s_v5 | 12 | **$1.20** |
| Full Tier 5 production | D4as_v5 | 48 | **$8.16** |
| Rush full analysis | D8as_v5 | 24 | **$8.16** |

---

## Commands

### Create a New VM

```bash
# Best value for MCMC work
az vm create \
  --resource-group ridder-cosmology-rg \
  --name ridder-mcmc \
  --image Ubuntu2204 \
  --size Standard_D4as_v5 \
  --admin-username ridderadmin \
  --generate-ssh-keys \
  --location eastus
```

### Start/Stop VMs

```bash
# Start
az vm start --resource-group ridder-cosmology-rg --name ridder-compute-01

# Stop (deallocate - stops charges)
az vm deallocate --resource-group ridder-cosmology-rg --name ridder-compute-01

# Check status
az vm list --output table --show-details
```

### Using Spot VMs (Up to 90% Cheaper)

```bash
az vm create \
  --resource-group ridder-cosmology-rg \
  --name ridder-spot \
  --image Ubuntu2204 \
  --size Standard_D4as_v5 \
  --priority Spot \
  --eviction-policy Deallocate \
  --max-price 0.05 \
  --admin-username ridderadmin \
  --generate-ssh-keys
```

⚠️ **Spot VMs can be evicted with 30s notice** — good for MCMC since you can checkpoint

---

## Money-Saving Tips

1. **Deallocate when done** — VMs cost $0 when deallocated (only disk storage ~$5/mo)

2. **Use AMD ("as" series)** — D4as_v5 is 10-20% cheaper than D4s_v5

3. **Spot VMs** — Up to 90% off, but can be evicted

4. **Cheapest regions**: East US, West US 2, North Central US

5. **Reserved Instances** — 40-60% off for 1-3 year commitments (if running 24/7)

6. **Right-size** — Don't use 8 cores if 4 will do

---

## Current Azure Resources

### Active Subscriptions

| Subscription | ID |
|--------------|-----|
| Pay-As-You-Go | 7c45aa43-0e69-489b-b19b-79e79c8b30ac |
| Primary | 07d86cc8-edc9-4278-8f89-2f0687b1317f |
| Microsoft Azure Sponsorship | c0ba54d9-a894-4cf4-b40a-45f5f2b8bb54 |

### Deallocated VMs (Ready to Restart)

| VM | Resource Group | Size | IP |
|----|----------------|------|-----|
| ridder-compute-01 | ridder-cosmology-rg | D4s_v3 | 172.191.4.60 |
| ridder-australia-01 | ridder-australia-rg | F8s_v2 | 20.58.129.33 |
| training | MaxwellTraining | NC4as_T4_v3 (GPU) | 52.186.169.9 |
| Taikun | Taikun (Sponsorship) | — | 20.168.12.116 |

### To Restart Cosmology VMs

```bash
# East US VM
az vm start --resource-group ridder-cosmology-rg --name ridder-compute-01
ssh ridderadmin@172.191.4.60

# Australia VM
az vm start --resource-group ridder-australia-rg --name ridder-australia-01
ssh ridderadmin@20.58.129.33
```

---

## Pricing Reference (December 2025)

All prices are East US, Pay-As-You-Go. Prices vary by region.

| Series | Use Case | Price Range |
|--------|----------|-------------|
| B-series | Burstable, dev/test | $0.04-0.17/hr |
| D-series v5 | General purpose | $0.10-0.77/hr |
| E-series v5 | Memory-optimized | $0.13-1.00/hr |
| F-series v2 | CPU-optimized | $0.08-0.68/hr |
| NC-series | GPU (ML/AI) | $0.50-3.00/hr |

For current pricing: https://azure.microsoft.com/pricing/details/virtual-machines/linux/

