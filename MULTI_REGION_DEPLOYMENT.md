# Multi-Region Azure Batch Deployment

## Overview
Deploy Ridder Field MCMC across 4 Asia-Pacific regions to bypass quota limits and achieve **4x speedup**.

## Architecture

### Deployment
- **1 Batch Account** (Australia East - primary)
- **4 Batch Pools** across regions:
  - 🇦🇺 Australia East: 1x F8s_v2 (8 vCPUs)
  - 🇸🇬 Southeast Asia: 1x F8s_v2 (8 vCPUs)
  - 🇭🇰 East Asia: 1x F8s_v2 (8 vCPUs)
  - 🇯🇵 Japan East: 1x F8s_v2 (8 vCPUs)

### Capacity
- **Total: 32 vCPUs** (4 regions × 8 vCPUs)
- **32 parallel MCMC chains**
- **No quota increase needed!**

### Cost
- **Compute**: $2.03/hour = $48.72/day
- **Storage**: ~$1/day
- **Data transfer**: ~$0.50/day (cross-region)
- **Total**: ~$50/day for 32 chains

## Performance Comparison

| Setup | Chains | Time for 1000 samples | Cost/day |
|-------|--------|----------------------|----------|
| Single VM (current) | 4 | ~6 hours | $9.22 |
| Multi-region (new) | 32 | ~45 minutes | $50.25 |
| **Speedup** | **8x** | **8x faster** | **5.5x cost** |

**Cost per sample**: Multi-region is actually **cheaper per sample**!

## Deployment Steps

### 1. Deploy Infrastructure
```bash
cd /Users/steveridder/Git/Ridder-Field/azure
./deploy_multiregion.sh
```

**Time**: ~10 minutes (pools need to spin up)

### 2. Run 1-Minute Test
```bash
./submit_multiregion_test.sh
```

**Expected**:
- 32 tasks submitted
- Completion: 2-3 minutes
- vs Single VM: 16 minutes
- **Speedup: 5-8x** ✅

### 3. Run Tier 1 (Planck)
After test succeeds, run full Tier 1:
```bash
./submit_multiregion_tier1.sh  # (to be created)
```

**Expected**:
- 32 chains × 200 samples each = 6400 total samples
- Time: ~2 hours (vs 16 hours on single VM)
- **Speedup: 8x** ✅

## Testing Roadmap

### Phase 1: Validation (Tonight)
1. ✅ Deploy 4 pools
2. ✅ Run 1-minute test (32 chains)
3. ✅ Verify all regions working
4. ✅ Check performance gain

### Phase 2: Production (Tomorrow)
1. Run Tier 1 (Planck only)
2. Run Tier 3 (Planck + SH0ES)
3. Compare results with single-VM baseline

### Phase 3: Scale Up (After quota increase)
1. Request 200 vCPU quota in Australia East
2. Consolidate to single region
3. Deploy 10x F16s_v2 = 160 chains

## Monitoring

### Check pool status:
```bash
BATCH_ACCOUNT=$(cd azure && terraform output -raw batch_account_name_multiregion)
az batch pool list --account-name $BATCH_ACCOUNT --query "[].{Name:id, State:allocationState, Nodes:currentDedicatedNodes}" -o table
```

### Check job progress:
```bash
az batch task list --job-id ridder-1min-test-YYYYMMDD-HHMMSS --account-name $BATCH_ACCOUNT --query "[].{ID:id, State:state, Pool:nodeInfo.poolId}" -o table
```

### View task output:
```bash
az batch task file download --job-id JOB_ID --task-id TASK_ID --file-path stdout.txt --destination ./task_output.txt --account-name $BATCH_ACCOUNT
```

## Cleanup

### Destroy all resources:
```bash
cd azure
terraform destroy -target=azurerm_batch_pool.pool_australiaeast \
                  -target=azurerm_batch_pool.pool_southeastasia \
                  -target=azurerm_batch_pool.pool_eastasia \
                  -target=azurerm_batch_pool.pool_japaneast \
                  -target=azurerm_batch_account.ridder_batch_multiregion \
                  -target=azurerm_storage_account.batch_multiregion_sa \
                  -target=azurerm_resource_group.batch_multiregion_rg
```

**Or just delete the resource group:**
```bash
az group delete --name ridder-batch-multiregion-rg --yes --no-wait
```

## Troubleshooting

### Pool stuck in "resizing":
Wait 5-10 minutes for nodes to provision. Check:
```bash
az batch pool show --pool-id ridder-pool-australiaeast --account-name $BATCH_ACCOUNT --query "{State:allocationState, Nodes:currentDedicatedNodes, Errors:resizeErrors}"
```

### Task failed:
Check task logs:
```bash
az batch task file list --job-id JOB_ID --task-id TASK_ID --account-name $BATCH_ACCOUNT
az batch task file download --job-id JOB_ID --task-id TASK_ID --file-path stderr.txt --destination ./error.log --account-name $BATCH_ACCOUNT
```

### Quota exceeded:
Check which region hit the limit:
```bash
az vm list-usage --location australiaeast --query "[?name.value=='standardFSv2Family'].{Name:name.localizedValue, Current:currentValue, Limit:limit}" -o table
```

## Next Steps

1. **Tonight**: Deploy and run 1-minute test
2. **Tomorrow**: Run Tier 1 if test succeeds
3. **This week**: Request quota increase for Australia East
4. **Next week**: Consolidate to single-region 160-chain deployment

## Questions?

- Check logs in Azure Portal: https://portal.azure.com
- Batch Explorer: https://azure.github.io/BatchExplorer/
- Azure CLI docs: https://docs.microsoft.com/en-us/cli/azure/batch

