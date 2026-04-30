// Azure infrastructure — DELIBERATELY MISCONFIGURED.
//
// This template intentionally violates several Azure security baselines so
// CodeScan's iac_auditor + azure_aware_auditor have things to find.

@description('Database administrator password.')
@secure()
param adminPassword string = 'P@ssw0rd-DEMO-DO-NOT-USE'   // CWE-798: hardcoded default

param location string = resourceGroup().location

// ---------------------------------------------------------------------------
// Storage account — public, weak TLS, no firewall, no encryption-with-CMK
// ---------------------------------------------------------------------------
resource sa 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stcodescandemo'
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: true                          // CWE-732
    minimumTlsVersion: 'TLS1_0'                          // CWE-326
    supportsHttpsTrafficOnly: false                      // CWE-319
    publicNetworkAccess: 'Enabled'
    networkAcls: { defaultAction: 'Allow' }              // wide open
  }
}

// ---------------------------------------------------------------------------
// Key Vault — legacy access policies, public, no purge protection
// ---------------------------------------------------------------------------
resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-codescan-demo'
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: false                       // CWE-732 (legacy ACLs)
    enableSoftDelete: false                              // recoverability gap
    enablePurgeProtection: false
    publicNetworkAccess: 'Enabled'
    networkAcls: { bypass: 'AzureServices', defaultAction: 'Allow' }
  }
}

// ---------------------------------------------------------------------------
// SQL Server — public, hardcoded admin, firewall 0.0.0.0/0
// ---------------------------------------------------------------------------
resource sql 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: 'sql-codescan-demo'
  location: location
  properties: {
    administratorLogin: 'sqladmin'
    administratorLoginPassword: adminPassword            // CWE-798 (default literal)
    publicNetworkAccess: 'Enabled'                       // CWE-1021
    minimalTlsVersion: '1.0'
  }
}

resource sqlOpenFw 'Microsoft.Sql/servers/firewallRules@2023-08-01-preview' = {
  parent: sql
  name: 'AllowAllInternet'
  properties: {
    startIpAddress: '0.0.0.0'                            // CWE-284 — entire IPv4 space
    endIpAddress: '255.255.255.255'
  }
}

// ---------------------------------------------------------------------------
// Network — NSG that allows SSH from anywhere
// ---------------------------------------------------------------------------
resource nsg 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: 'nsg-codescan-demo'
  location: location
  properties: {
    securityRules: [
      {
        name: 'AllowSshFromInternet'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '*'                       // CWE-284
          destinationAddressPrefix: '*'
          sourcePortRange: '*'
          destinationPortRange: '22'
        }
      }
      {
        name: 'AllowRdpFromInternet'
        properties: {
          priority: 110
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
          sourcePortRange: '*'
          destinationPortRange: '3389'
        }
      }
    ]
  }
}

// ---------------------------------------------------------------------------
// VM with admin password baked in
// ---------------------------------------------------------------------------
resource vm 'Microsoft.Compute/virtualMachines@2023-09-01' = {
  name: 'vm-codescan-demo'
  location: location
  properties: {
    hardwareProfile: { vmSize: 'Standard_B1s' }
    osProfile: {
      computerName: 'vmdemo'
      adminUsername: 'azureuser'
      adminPassword: 'Hardcoded-VM-Password!2026'        // CWE-798
      windowsConfiguration: {
        provisionVMAgent: true
        enableAutomaticUpdates: false                    // CWE-1104
      }
    }
    storageProfile: {
      imageReference: {
        publisher: 'MicrosoftWindowsServer'
        offer: 'WindowsServer'
        sku: '2022-datacenter'
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
        encryptionSettings: { enabled: false }           // CWE-311
      }
    }
    networkProfile: {
      networkInterfaces: []
    }
  }
}

// ---------------------------------------------------------------------------
// Role assignment at subscription scope — Owner, broadly scoped principal
// ---------------------------------------------------------------------------
resource raSubOwner 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: subscription()
  name: guid('codescan-demo-owner')
  properties: {
    principalId: '00000000-0000-0000-0000-000000000000'
    // Owner role — CWE-272 (excessive privilege)
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '8e3af657-a8ff-443c-a75c-2fe8c4bcb635'
    )
  }
}
