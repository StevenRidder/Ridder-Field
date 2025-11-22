# Single F8s_v2 VM in Australia East for Ridder Field MCMC
# 8 vCPUs, 16 GB RAM, compute-optimized

resource "azurerm_resource_group" "ridder_australia_rg" {
  name     = "ridder-australia-rg"
  location = "Australia East"
}

resource "azurerm_virtual_network" "ridder_australia_vnet" {
  name                = "ridder-australia-vnet"
  address_space       = ["10.1.0.0/16"]
  location            = azurerm_resource_group.ridder_australia_rg.location
  resource_group_name = azurerm_resource_group.ridder_australia_rg.name
}

resource "azurerm_subnet" "ridder_australia_subnet" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.ridder_australia_rg.name
  virtual_network_name = azurerm_virtual_network.ridder_australia_vnet.name
  address_prefixes     = ["10.1.2.0/24"]
}

resource "azurerm_public_ip" "ridder_australia_ip" {
  name                = "ridder-australia-ip"
  resource_group_name = azurerm_resource_group.ridder_australia_rg.name
  location            = azurerm_resource_group.ridder_australia_rg.location
  allocation_method   = "Static"
}

resource "azurerm_network_security_group" "ridder_australia_nsg" {
  name                = "ridder-australia-nsg"
  location            = azurerm_resource_group.ridder_australia_rg.location
  resource_group_name = azurerm_resource_group.ridder_australia_rg.name

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

resource "azurerm_network_interface" "ridder_australia_nic" {
  name                = "ridder-australia-nic"
  location            = azurerm_resource_group.ridder_australia_rg.location
  resource_group_name = azurerm_resource_group.ridder_australia_rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.ridder_australia_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.ridder_australia_ip.id
  }
}

resource "azurerm_network_interface_security_group_association" "ridder_australia_assoc" {
  network_interface_id      = azurerm_network_interface.ridder_australia_nic.id
  network_security_group_id = azurerm_network_security_group.ridder_australia_nsg.id
}

resource "azurerm_linux_virtual_machine" "ridder_australia_vm" {
  name                = "ridder-australia-01"
  resource_group_name = azurerm_resource_group.ridder_australia_rg.name
  location            = azurerm_resource_group.ridder_australia_rg.location
  size                = "Standard_F8s_v2"  # 8 vCPUs, 16 GB RAM, compute-optimized
  admin_username      = "ridderadmin"
  network_interface_ids = [
    azurerm_network_interface.ridder_australia_nic.id
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

  custom_data = filebase64("${path.module}/provision_australia.sh")
}

output "australia_public_ip" {
  value       = azurerm_public_ip.ridder_australia_ip.ip_address
  description = "Public IP of Australia East VM"
}

output "australia_ssh_command" {
  value       = "ssh ridderadmin@${azurerm_public_ip.ridder_australia_ip.ip_address}"
  description = "SSH command for Australia East VM"
}

