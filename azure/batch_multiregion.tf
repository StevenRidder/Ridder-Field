# Multi-Region Azure Batch for Ridder Field MCMC
# Deploys 4 pools across Asia-Pacific regions (32 parallel chains)
# Each region has 10 vCPU quota, we use 8 vCPUs (1x F8s_v2) per region

# Primary Batch Account (Australia East - closest to Polynesia)
resource "azurerm_resource_group" "batch_multiregion_rg" {
  name     = "ridder-batch-multiregion-rg"
  location = "Australia East"
}

resource "azurerm_storage_account" "batch_multiregion_sa" {
  name                     = "ridderbatch${substr(md5(azurerm_resource_group.batch_multiregion_rg.id), 0, 8)}"
  resource_group_name      = azurerm_resource_group.batch_multiregion_rg.name
  location                 = azurerm_resource_group.batch_multiregion_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  tags = {
    Environment = "Production"
    Project     = "Ridder-Cosmology-MultiRegion"
  }
}

resource "azurerm_batch_account" "ridder_batch_multiregion" {
  name                = "riddermulti${substr(md5(azurerm_resource_group.batch_multiregion_rg.id), 0, 8)}"
  resource_group_name = azurerm_resource_group.batch_multiregion_rg.name
  location            = azurerm_resource_group.batch_multiregion_rg.location
  pool_allocation_mode = "BatchService"
  storage_account_id  = azurerm_storage_account.batch_multiregion_sa.id
  storage_account_authentication_mode = "StorageKeys"
  
  tags = {
    Environment = "Production"
    Project     = "Ridder-Cosmology-MultiRegion"
  }
}

# Pool 1: Australia East (8 vCPUs)
resource "azurerm_batch_pool" "pool_australiaeast" {
  name                = "ridder-pool-australiaeast"
  resource_group_name = azurerm_resource_group.batch_multiregion_rg.name
  account_name        = azurerm_batch_account.ridder_batch_multiregion.name
  node_agent_sku_id   = "batch.node.ubuntu 22.04"
  vm_size             = "Standard_F8s_v2" # 8 vCPUs, 16 GB RAM

  fixed_scale {
    target_dedicated_nodes = 1
    target_low_priority_nodes = 0
  }

  storage_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }
  
  start_task {
    command_line = "/bin/bash -c 'apt-get update && apt-get install -y gcc g++ make python3-pip gfortran libopenblas-dev git && pip3 install numpy scipy matplotlib cobaya getdist'"
    wait_for_success = true
    user_identity {
      auto_user {
        elevation_level = "Admin"
        scope           = "Pool"
      }
    }
  }
}

# Pool 2: Southeast Asia (Singapore) (8 vCPUs)
resource "azurerm_batch_pool" "pool_southeastasia" {
  name                = "ridder-pool-southeastasia"
  resource_group_name = azurerm_resource_group.batch_multiregion_rg.name
  account_name        = azurerm_batch_account.ridder_batch_multiregion.name
  node_agent_sku_id   = "batch.node.ubuntu 22.04"
  vm_size             = "Standard_F8s_v2"

  fixed_scale {
    target_dedicated_nodes = 1
    target_low_priority_nodes = 0
  }

  storage_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }
  
  start_task {
    command_line = "/bin/bash -c 'apt-get update && apt-get install -y gcc g++ make python3-pip gfortran libopenblas-dev git && pip3 install numpy scipy matplotlib cobaya getdist'"
    wait_for_success = true
    user_identity {
      auto_user {
        elevation_level = "Admin"
        scope           = "Pool"
      }
    }
  }
}

# Pool 3: East Asia (Hong Kong) (8 vCPUs)
resource "azurerm_batch_pool" "pool_eastasia" {
  name                = "ridder-pool-eastasia"
  resource_group_name = azurerm_resource_group.batch_multiregion_rg.name
  account_name        = azurerm_batch_account.ridder_batch_multiregion.name
  node_agent_sku_id   = "batch.node.ubuntu 22.04"
  vm_size             = "Standard_F8s_v2"

  fixed_scale {
    target_dedicated_nodes = 1
    target_low_priority_nodes = 0
  }

  storage_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }
  
  start_task {
    command_line = "/bin/bash -c 'apt-get update && apt-get install -y gcc g++ make python3-pip gfortran libopenblas-dev git && pip3 install numpy scipy matplotlib cobaya getdist'"
    wait_for_success = true
    user_identity {
      auto_user {
        elevation_level = "Admin"
        scope           = "Pool"
      }
    }
  }
}

# Pool 4: Japan East (8 vCPUs)
resource "azurerm_batch_pool" "pool_japaneast" {
  name                = "ridder-pool-japaneast"
  resource_group_name = azurerm_resource_group.batch_multiregion_rg.name
  account_name        = azurerm_batch_account.ridder_batch_multiregion.name
  node_agent_sku_id   = "batch.node.ubuntu 22.04"
  vm_size             = "Standard_F8s_v2"

  fixed_scale {
    target_dedicated_nodes = 1
    target_low_priority_nodes = 0
  }

  storage_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }
  
  start_task {
    command_line = "/bin/bash -c 'apt-get update && apt-get install -y gcc g++ make python3-pip gfortran libopenblas-dev git && pip3 install numpy scipy matplotlib cobaya getdist'"
    wait_for_success = true
    user_identity {
      auto_user {
        elevation_level = "Admin"
        scope           = "Pool"
      }
    }
  }
}

# Outputs
output "batch_account_name_multiregion" {
  value       = azurerm_batch_account.ridder_batch_multiregion.name
  description = "Multi-region Batch account name"
}

output "batch_account_endpoint" {
  value       = azurerm_batch_account.ridder_batch_multiregion.account_endpoint
  description = "Batch account endpoint for job submission"
}

output "storage_account_name_multiregion" {
  value       = azurerm_storage_account.batch_multiregion_sa.name
  description = "Storage account for multi-region batch"
}

output "pool_summary" {
  value = <<-EOT
  
  MULTI-REGION BATCH DEPLOYMENT
  ==============================
  Total Capacity: 32 vCPUs (4 regions × 8 vCPUs)
  
  Pools:
  - Australia East:   1x F8s_v2 (8 vCPUs)
  - Southeast Asia:   1x F8s_v2 (8 vCPUs)
  - East Asia:        1x F8s_v2 (8 vCPUs)
  - Japan East:       1x F8s_v2 (8 vCPUs)
  
  Estimated Cost: $2.03/hour = $48.72/day
  
  Next Steps:
  1. Submit test job: bash submit_multiregion_job.sh
  2. Monitor pools: az batch pool list --account-name ${azurerm_batch_account.ridder_batch_multiregion.name}
  EOT
}

