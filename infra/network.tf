# Terraform — DELIBERATELY MISCONFIGURED.
#
# Mirrors a few of the Bicep findings in HCL syntax so iac_reader's
# Terraform parser exercises a different code path on the same scan.

terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 3.0" }
  }
}

provider "azurerm" {
  features {}
}

# ----------------------------------------------------------------------------
# NSG: SSH wide open from the Internet
# ----------------------------------------------------------------------------
resource "azurerm_network_security_group" "open_ssh" {
  name                = "nsg-codescan-demo-tf"
  location            = "westeurope"
  resource_group_name = "rg-codescan-demo"

  security_rule {
    name                       = "AllowSshFromAnywhere"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "0.0.0.0/0"   # CWE-284 — open SSH
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowAllOutbound"
    priority                   = 200
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"           # no egress controls
  }
}

# ----------------------------------------------------------------------------
# Storage: public, weak TLS
# ----------------------------------------------------------------------------
resource "azurerm_storage_account" "demo" {
  name                            = "stcsdemotf"
  location                        = "westeurope"
  resource_group_name             = "rg-codescan-demo"
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = true       # CWE-732
  min_tls_version                 = "TLS1_0"   # CWE-326
  enable_https_traffic_only       = false      # CWE-319
}

# ----------------------------------------------------------------------------
# Hardcoded credentials in locals — should surface via find_inline_secrets
# ----------------------------------------------------------------------------
locals {
  # CWE-798: AWS placeholder kept as the documented example so secret
  # scanners ignore it but our LLM auditor flags it.
  api_key       = "AKIAIOSFODNN7EXAMPLE"
  db_password   = "Pa55w0rd-very-secret"
  github_secret = "shhh-this-is-a-token-do-not-tell"
}

resource "azurerm_role_assignment" "broad_owner" {
  # CWE-272: Owner at subscription scope — too broad for a workload identity.
  scope                = "/subscriptions/00000000-0000-0000-0000-000000000000"
  role_definition_name = "Owner"
  principal_id         = "11111111-1111-1111-1111-111111111111"
}
