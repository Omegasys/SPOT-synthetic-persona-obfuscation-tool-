# SPOT Proxy Networking Plugin

The SPOT Proxy Networking Plugin provides controlled proxy configuration and validation for SPOT.

It supports common proxy protocols while keeping proxy use subject to SPOT's network, safety, isolation, and emergency-stop policies.

## Supported Proxy Types

* HTTP
* HTTPS
* SOCKS5
* SOCKS5H

SOCKS5H is useful when hostname resolution should occur through the proxy rather than through the local system.

## Purpose

The plugin provides:

* Proxy configuration validation
* Proxy URL generation
* Protocol validation
* Endpoint health checks
* Fail-closed behavior
* Direct-network fallback prevention
* Proxy authentication configuration without exposing credentials
* SPOT network-policy integration
* Emergency-stop handling
* Bounded connection timeouts

## Security Model

The plugin follows SPOT's security model:

* Fail closed by default
* Direct fallback disabled by default
* No unrestricted network access
* No credential access
* No personal-data access
* No arbitrary firewall modification
* No arbitrary routing-table modification
* No DNS-policy bypass
* No unrestricted proxy chaining
* No silent fallback to another network mode

## Credentials

Proxy credentials are intentionally not handled by the default configuration.

SPOT should not import:

* Browser passwords
* System passwords
* Personal authentication tokens
* Personal proxy credentials

If authenticated proxy support is eventually implemented, credentials should be supplied through a dedicated secret-management interface rather than stored in ordinary YAML configuration.

## What the Plugin Does

The plugin can:

* validate a proxy endpoint
* describe the selected proxy route
* generate a proxy URL
* check whether the proxy endpoint is reachable
* enforce the configured fail-closed policy
* report proxy health
* provide routing information to SPOT's network manager

## What the Plugin Does Not Do

The plugin does not:

* automatically change system-wide proxy settings
* modify firewall rules
* modify routing tables
* bypass SPOT DNS controls
* silently switch to direct networking
* access browser credentials
* access personal files
* create accounts
* authenticate to arbitrary services
* perform unrestricted network scanning

## Relationship to SPOT Networking

The plugin does not replace:

```
src/spot/network/
```

Instead, it provides a controlled proxy backend for the SPOT network manager.

The intended flow is:

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
Proxy Plugin
  |
  v
Configured Proxy
  |
  v
Destination
```

## Tor and Whonix

The proxy plugin can represent SOCKS5/SOCKS5H endpoints, including locally configured endpoints.

For Tor-specific routing, prefer the dedicated:

```
plugins/networking/tor/
```

For Whonix-specific routing, prefer:

```
plugins/networking/whonix/
```

This separation prevents the generic proxy plugin from making assumptions about Tor or Whonix.

## Fail-Closed Behavior

If the proxy is required and becomes unavailable:

```
Proxy unavailable
      |
      v
Activity denied
```

The plugin does not silently switch to:

```
Direct Internet
```

## Health Checks

The default health check only verifies whether the configured proxy endpoint accepts a TCP connection.

It does not:

* browse the Internet
* contact arbitrary websites
* transmit persona activity
* authenticate to the proxy
* perform unrestricted proxy testing

## Testing

The test suite is designed to run offline.

Tests use mocked sockets where a connection is required.

A real proxy server is not required.

## Status

This plugin is an integration foundation.

Actual network traffic should remain controlled by SPOT's network manager and platform-specific networking backends.
