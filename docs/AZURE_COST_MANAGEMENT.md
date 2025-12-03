# Azure Cost Management

**Last Updated**: December 2025

---

## ⚠️ PostgreSQL Auto-Restart Warning

Azure PostgreSQL Flexible Server **automatically restarts after 7 days** when stopped.

### Options to Keep It Down

#### Option 1: Delete It (Recommended if not needed)
```bash
az postgres flexible-server delete \
  --resource-group TX_Reporter \
  --name reporter \
  --yes
```

#### Option 2: Scheduled Stop Script
Run this every 6 days (set a calendar reminder):
```bash
az account set --subscription "Primary"
az postgres flexible-server stop --resource-group TX_Reporter --name reporter
```

#### Option 3: Azure Automation (Auto-stop)
Create an Azure Automation runbook to stop it every 6 days. More complex but fully automated.

#### Option 4: Delete the Entire Resource Group
If TX_Reporter is not needed at all:
```bash
az group delete --name TX_Reporter --yes --no-wait
```

---

## Current Monthly Costs (After Optimization)

### December 2025 Status

| Resource | Status | Monthly Cost |
|----------|--------|--------------|
| ridder-compute-01 | Deallocated | ~$5 (disk only) |
| ridder-australia-01 | Deallocated | ~$5 (disk only) |
| TX_Reporter PostgreSQL | Stopped* | $0 (while stopped) |
| TX_Reporter Container | Stopped | $0 |
| TX_Reporter App Service | Free (F1) | $0 |
| training VM | Deallocated | ~$5 (disk only) |
| Storage accounts | Active | ~$5-10 |

**Estimated Total: ~$20-25/month** (down from ~$450+/month)

*⚠️ PostgreSQL will auto-restart after 7 days

---

## Quick Commands

### Check What's Running
```bash
# VMs
az vm list --output table --show-details

# PostgreSQL servers
az postgres flexible-server list --output table

# All resources
az resource list --output table
```

### Stop Everything Quickly
```bash
# Deallocate all VMs in a resource group
az vm deallocate --ids $(az vm list -g ridder-cosmology-rg --query "[].id" -o tsv)

# Stop PostgreSQL
az postgres flexible-server stop -g TX_Reporter -n reporter
```

### Cost Analysis
```bash
# View consumption (requires billing permissions)
az consumption usage list --output table
```

---

## Reminders

- [ ] **Every 6 days**: Stop TX_Reporter PostgreSQL (or delete it)
- [ ] Before starting VMs: Check current Azure credit balance
- [ ] After work is done: Deallocate VMs immediately

---

## Resource Groups Summary

| Resource Group | Subscription | Contents | Action |
|----------------|--------------|----------|--------|
| ridder-cosmology-rg | Pay-As-You-Go | VM + network | Keep (deallocated) |
| ridder-australia-rg | Pay-As-You-Go | VM + network | Keep (deallocated) |
| MaxwellTraining | Pay-As-You-Go | ML workspace, GPU VM | Keep |
| TX_Reporter | Primary | PostgreSQL, containers | Consider deleting |
| maxwell | Primary | Container services | Check with team |
| Taikun | Sponsorship | VM | Keep (deallocated) |

