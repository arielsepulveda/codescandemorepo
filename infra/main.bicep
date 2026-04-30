// Azure infrastructure — DELIBERATELY MISCONFIGURED.
//
// Two textbook IaC findings every cloud-posture / IaC SAST tool detects:
//   - Storage account with public blob access enabled
//   - NSG inbound rule exposing SSH from the Internet
//
// These are the "of course you flag those" baseline. The real demo value
// is the joint reasoning: ``app/subtle/iac_link.py`` writes user data
// into the public storage account declared below — the *cross-domain*
// finding that no IaC SAST or code SAST alone produces.

param location string = resourceGroup().location

// CWE-732: storage account is world-readable.
resource sa 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stcodescandemo'
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

// CWE-284: NSG inbound rule lets the entire Internet hit SSH.
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
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          sourcePortRange: '*'
          destinationPortRange: '22'
        }
      }
    ]
  }
}
