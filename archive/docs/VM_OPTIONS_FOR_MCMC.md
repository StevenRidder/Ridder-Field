# Azure VM Options for MCMC Workloads

## Current Quota Status (Australia East - Closest to Polynesia)
**All VM families have 10 vCPU default quota for Pay-As-You-Go subscriptions**

## Best VM Families for MCMC (Compute-Intensive Workloads)

### **Tier 1: Compute-Optimized (Best for MCMC)**

#### **F-Series (Compute-Optimized)**
- **FSv2 Family**: 10 vCPU quota available
  - `Standard_F4s_v2`: 4 vCPUs, 8 GB RAM, ~$0.169/hr
  - `Standard_F8s_v2`: 8 vCPUs, 16 GB RAM, ~$0.338/hr
  - `Standard_F16s_v2`: 16 vCPUs, 32 GB RAM, ~$0.677/hr
  - **Best CPU/$ ratio**
  - High clock speed (3.4 GHz base)
  - **RECOMMENDED for MCMC**

- **FXmdsv2 Family**: 10 vCPU quota
  - Newer generation, similar pricing
  - Good alternative

### **Tier 2: General Purpose (Good Balance)**

#### **D-Series (Current Choice)**
- **DSv3 Family**: 10 vCPU quota (what you're using now)
  - `Standard_D4s_v3`: 4 vCPUs, 16 GB RAM, ~$0.192/hr
  - `Standard_D8s_v3`: 8 vCPUs, 32 GB RAM, ~$0.384/hr
  - `Standard_D16s_v3`: 16 vCPUs, 64 GB RAM, ~$0.768/hr
  - Good balance, but more expensive than F-series

- **Dv4/DSv4 Family**: 10 vCPU quota each
  - Newer generation than v3
  - Similar pricing

- **Dv6/DSv6 Family**: 10 vCPU quota each
  - Latest generation
  - Best performance/watt

#### **Dav6/DASv4 (AMD-based)**
- **Dav6 Family**: 10 vCPU quota
  - AMD EPYC processors
  - Often cheaper than Intel
  - Good for parallel workloads

### **Tier 3: Memory-Optimized (Overkill for MCMC)**

#### **E-Series**
- **ESv3/Ev3 Family**: 10 vCPU quota each
  - High RAM (8 GB per vCPU)
  - More expensive
  - **Not needed for MCMC** (CLASS uses <2 GB per chain)

### **Tier 4: High-Performance Compute**

#### **H-Series**
- **H Family**: 8 vCPU quota
  - InfiniBand networking
  - Expensive ($2-3/hr)
  - **Overkill for your workload**

## **RECOMMENDATIONS FOR YOUR MCMC WORKLOAD**

### **Option 1: Switch to F-Series (BEST)**
**Why:**
- ✅ **20-30% cheaper** than D-series
- ✅ **Higher clock speeds** (better for single-threaded CLASS)
- ✅ **Same 10 vCPU quota**
- ✅ Less RAM (but you don't need it)

**Batch Pool Config:**
```hcl
vm_size = "Standard_F8s_v2"  # 8 vCPUs, 16 GB RAM
maxNumberofVMs = 1            # Fits 10 vCPU quota
```
**Result:** 1 node with 8 cores = 8 parallel MCMC chains

OR

```hcl
vm_size = "Standard_F4s_v2"  # 4 vCPUs, 8 GB RAM
maxNumberofVMs = 2            # Fits 10 vCPU quota
```
**Result:** 2 nodes with 4 cores each = 8 parallel MCMC chains

### **Option 2: Stay with D-Series**
**Why:**
- ✅ You're already using it
- ✅ More RAM (useful if you add more likelihoods)
- ❌ More expensive

**Current Config:**
```hcl
vm_size = "Standard_D4s_v3"  # 4 vCPUs, 16 GB RAM
maxNumberofVMs = 2            # Fits 10 vCPU quota
```

### **Option 3: Try AMD (Dav6)**
**Why:**
- ✅ Often 10-15% cheaper
- ✅ Good multi-core performance
- ✅ Same 10 vCPU quota

```hcl
vm_size = "Standard_D4as_v6"  # 4 vCPUs, 16 GB RAM (AMD)
maxNumberofVMs = 2             # Fits 10 vCPU quota
```

## **COST COMPARISON (Australia East, per hour)**

| VM Type | vCPUs | RAM | Cost/hr | Cost per vCPU/hr | Best For |
|---------|-------|-----|---------|------------------|----------|
| F4s_v2 | 4 | 8 GB | $0.169 | $0.042 | **MCMC (Best $)** |
| F8s_v2 | 8 | 16 GB | $0.338 | $0.042 | **MCMC (Best $)** |
| D4s_v3 | 4 | 16 GB | $0.192 | $0.048 | General (Current) |
| D8s_v3 | 8 | 32 GB | $0.384 | $0.048 | General |
| D4as_v6 | 4 | 16 GB | $0.173 | $0.043 | AMD Alternative |
| E4s_v3 | 4 | 32 GB | $0.252 | $0.063 | Memory (Overkill) |

**For a 24-hour MCMC run with 8 vCPUs:**
- **F8s_v2**: $8.11 (CHEAPEST)
- **D8s_v3**: $9.22 (Current choice)
- **E8s_v3**: $12.10 (Overkill)

**Savings: ~$1.11/day or $33/month by switching to F-series**

## **FINAL RECOMMENDATION**

### **Immediate Action (Tonight):**
1. **Update `batch.tf` to use F-series**:
   ```hcl
   vm_size = "Standard_F8s_v2"
   maxNumberofVMs = 1
   ```
2. **Deploy in Australia East** (lower latency to Polynesia)
3. **Request quota increase** for F-series to 200 vCPUs

### **After Quota Increase:**
```hcl
vm_size = "Standard_F16s_v2"  # 16 vCPUs
maxNumberofVMs = 10            # 160 vCPUs total
```
**Result:** 10 nodes × 16 cores = 160 parallel MCMC chains

**Cost for full production (160 vCPUs, 24 hours):**
- F16s_v2: $162.48/day
- D16s_v3: $184.32/day
- **Savings: $21.84/day = $655/month**

## **Action Items**
1. ✅ Switch to F-series (cheaper, faster)
2. ✅ Deploy in Australia East (closer to you)
3. ✅ Request 200 vCPU quota for FSv2 family
4. ✅ Test with 1x F8s_v2 node (8 chains) tonight

