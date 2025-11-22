# Azure Batch Infrastructure for Ridder Field MCMC
# This creates a Batch account and pool for parallel MCMC execution

resource "azurerm_resource_group" "batch_rg" {
  name     = "ridder-batch-rg"
  location = "East US"
}

resource "azurerm_storage_account" "batch_sa" {
  name                     = "riddercosmo${substr(md5(azurerm_resource_group.batch_rg.id), 0, 8)}"
  resource_group_name      = azurerm_resource_group.batch_rg.name
  location                 = azurerm_resource_group.batch_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  # Ensure name is globally unique
  tags = {
    Environment = "Production"
    Project     = "Ridder-Cosmology"
  }
}

resource "azurerm_batch_account" "ridder_batch" {
  name                = "ridderbatch${substr(md5(azurerm_resource_group.batch_rg.id), 0, 8)}"
  resource_group_name = azurerm_resource_group.batch_rg.name
  location            = azurerm_resource_group.batch_rg.location
  pool_allocation_mode = "BatchService"
  storage_account_id  = azurerm_storage_account.batch_sa.id
  storage_account_authentication_mode = "StorageKeys"
  
  tags = {
    Environment = "Production"
    Project     = "Ridder-Cosmology"
  }
}

resource "azurerm_batch_pool" "ridder_pool" {
  name                = "ridder-pool-16core"
  resource_group_name = azurerm_resource_group.batch_rg.name
  account_name        = azurerm_batch_account.ridder_batch.name
  node_agent_sku_id   = "batch.node.ubuntu 22.04"
  vm_size             = "Standard_D16s_v3" # 16 vCPUs per node

  # Auto-Scale Formula: If tasks exist, spin up nodes. Max 10 nodes (160 cores).
  auto_scale {
    evaluation_interval = "PT5M"
    formula = <<EOF
      startingNumberOfVMs = 0;
      maxNumberofVMs = 10;
      pendingTaskSamplePercent = $PendingTasks.GetSamplePercent(180 * TimeInterval_Second);
      pendingTaskSamples = pendingTaskSamplePercent < 70 ? startingNumberOfVMs : avg($PendingTasks.GetSample(180 * TimeInterval_Second));
      $TargetDedicatedNodes=min(maxNumberofVMs, pendingTaskSamples);
    EOF
  }

  storage_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }
  
  # Install CLASS dependencies on boot
  # Note: This slows node startup but is fine for prototyping
  # Production: Use custom image with CLASS pre-compiled
  start_task {
    command_line = "/bin/bash -c 'apt-get update && apt-get install -y gcc make python3-pip gfortran libopenblas-dev && pip3 install cobaya numpy scipy getdist'"
    wait_for_success = true
    user_identity {
      auto_user {
        elevation_level = "Admin"
        scope           = "Pool"
      }
    }
  }
}

output "batch_account_name" {
  value       = azurerm_batch_account.ridder_batch.name
  description = "Azure Batch account name"
}

output "batch_pool_name" {
  value       = azurerm_batch_pool.ridder_pool.name
  description = "Azure Batch pool name"
}

output "storage_account_name" {
  value       = azurerm_storage_account.batch_sa.name
  description = "Storage account name for Batch"
}

