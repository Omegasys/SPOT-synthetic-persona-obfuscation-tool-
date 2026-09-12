# SPOT Whonix Networking Plugin

The SPOT Whonix Networking Plugin provides controlled integration with a Whonix-based network path.

It is designed for environments where SPOT activity should be routed through a Whonix Gateway and Tor rather than directly through the Internet.

## Purpose

The plugin provides:

* Whonix configuration validation
* Gateway and Workstation topology validation
* Fail-closed networking
* Direct-network fallback prevention
* Tor requirement enforcement
* Network health checks
* Whonix routing descriptions
* Integration with SPOT network policy
* Integration with Qubes-aware network assignments
* Emergency-stop awareness
* Bounded health-check operations

## Security Model

The plugin follows SPOT's security model:

* Fail closed by default
* Direct networking disabled by default
* No silent network fallback
* No unrestricted host networking
* No unrestricted firewall modification
* No unrestricted routing-table modification
* No credential access
* No personal-data access
* No arbitrary Qubes administration
* No unrestricted dom0 operations
* No DNS bypass
* No disabling of SPOT safety controls

The plugin is an integration layer. Actual privileged networking operations belong to restricted platform backends.

## Recommended Topology

For Qubes OS, the recommended topology is:

```
SPOT Persona Qube
        |
        v
Whonix Workstation
        |
        v
sys-whonix
        |
        v
       Tor
        |
        v
     Internet
```

SPOT should not bypass the Whonix Gateway.

## What the Plugin Does

The plugin can:

* describe the expected Whonix topology
* validate configuration
* check configured endpoint availability
* report whether the required Gateway is available
* report whether Tor is expected
* enforce fail-closed policy at the SPOT policy layer
* provide a routing configuration to the network manager

## What the Plugin Does Not Do

The plugin does not:

* create Qubes VMs
* destroy Qubes VMs
* modify dom0
* change Qubes firewall rules directly
* modify Linux routing tables directly
* launch arbitrary privileged processes
* disable Tor
* fall back to direct Internet access
* bypass SPOT DNS policy
* access user credentials
* access personal browser profiles
* impersonate a real person

Platform-specific operations should be implemented through restricted backends and explicit Qubes RPC policies.

## Configuration

Start with:

```
config.example.yaml
```

The default configuration is intentionally conservative.

The recommended security settings are:

* `enabled: false` until explicitly configured
* `fail_closed: true`
* `allow_direct_fallback: false`
* `require_gateway: true`
* `require_tor: true`
* `prevent_dns_bypass: true`

## Relationship to the SPOT Network Layer

This plugin does not replace:

```
src/spot/network/
```

Instead, it provides an integration backend for that layer.

The normal flow should be:

```
Persona
  |
  v
SPOT Network Manager
  |
  v
Network Policy
  |
  v
Whonix Plugin
  |
  v
Whonix Workstation
  |
  v
Whonix Gateway
  |
  v
Tor
```

## Qubes OS

When running under Qubes OS, SPOT should normally use a Whonix-based Qube assignment.

The plugin can describe and validate the expected Qubes topology, but Qubes operations must remain controlled by the Qubes integration layer.

Qubes policy should remain default-deny.

## Health Checks

Health checks are deliberately limited.

The plugin may verify that configured Whonix endpoints or integration points are reachable.

It does not perform arbitrary Internet requests merely to determine whether the Internet works.

## Fail-Closed Behavior

If the required Whonix path is unavailable:

```
Activity
   |
   v
Whonix unavailable
   |
   v
Activity denied
```

SPOT should never silently change from:

```
Whonix -> Tor
```

to:

```
Direct Internet
```

## Testing

The test suite is designed to run offline.

Tests should not require:

* an Internet connection
* a real Whonix installation
* Qubes dom0
* a running Tor daemon
* real user credentials

External networking should be mocked where necessary.

## Status

This plugin is an integration foundation.

Actual platform-specific Whonix/Qubes control should remain isolated from the policy and configuration code.
