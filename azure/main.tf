provider "azurerm" {
  features {}
  # Using alternate subscription for larger VM/batch quotas
  subscription_id = "7c45aa43-0e69-489b-b19b-79e79c8b30ac"
}

resource "azurerm_resource_group" "ridder_rg" {
  name     = "ridder-cosmology-rg"
  location = "East US"
}

resource "azurerm_virtual_network" "ridder_vnet" {
  name                = "ridder-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.ridder_rg.location
  resource_group_name = azurerm_resource_group.ridder_rg.name
}

resource "azurerm_subnet" "ridder_subnet" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.ridder_rg.name
  virtual_network_name = azurerm_virtual_network.ridder_vnet.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_public_ip" "ridder_ip" {
  name                = "ridder-headnode-ip"
  resource_group_name = azurerm_resource_group.ridder_rg.name
  location            = azurerm_resource_group.ridder_rg.location
  allocation_method   = "Static"
}

resource "azurerm_network_security_group" "ridder_nsg" {
  name                = "ridder-nsg"
  location            = azurerm_resource_group.ridder_rg.location
  resource_group_name = azurerm_resource_group.ridder_rg.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
    source_port_range          = "*"
    destination_port_range     = "22"
  }
}

resource "azurerm_network_interface" "ridder_nic" {
  name                = "ridder-nic"
  location            = azurerm_resource_group.ridder_rg.location
  resource_group_name = azurerm_resource_group.ridder_rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.ridder_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.ridder_ip.id
  }
}

resource "azurerm_network_interface_security_group_association" "ridder_assoc" {
  network_interface_id      = azurerm_network_interface.ridder_nic.id
  network_security_group_id = azurerm_network_security_group.ridder_nsg.id
}

resource "azurerm_linux_virtual_machine" "ridder_vm" {
  name                = "ridder-compute-01"
  resource_group_name = azurerm_resource_group.ridder_rg.name
  location            = azurerm_resource_group.ridder_rg.location
  size                = "Standard_D4s_v3"  # 4 vCPUs, 16 GB RAM (fits quota)
  admin_username      = "ridderadmin"
  network_interface_ids = [
    azurerm_network_interface.ridder_nic.id
  ]

  admin_ssh_key {
    username   = "ridderadmin"
    public_key = file("${pathexpand("~")}/.ssh/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
    disk_size_gb         = 200
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  # Attach cloud-init script for automatic setup
  custom_data = filebase64("${path.module}/provision.sh")
}

output "public_ip_address" {
  value       = azurerm_public_ip.ridder_ip.ip_address
  description = "Public IP address of the Ridder compute node"
}

output "ssh_command" {
  value       = "ssh ridderadmin@${azurerm_public_ip.ridder_ip.ip_address}"
  description = "SSH command to connect to the VM"
}

