# SPOT Network Engine

The network engine controls how SPOT connects to external networks.

Its primary purpose is to provide an explicit and predictable network boundary for synthetic activity.

## Purpose

The network engine manages:

* Network modes
* Routing
* Proxies
* Tor
* Whonix
* DNS
* Firewall rules
* Kill switches
* Network health checks

## Network Modes

Depending on the installation, SPOT may support:

* Direct
* Proxy
* Tor
* Whonix

Only modes supported by the installed version should be enabled.

## Explicit Routing

SPOT should always know which network mode a persona is expected to use.

For example:

**Persona → Browser → Tor**

If a different route is detected, SPOT should be able to stop the activity.

## Direct Mode

Direct mode connects through the normal system network.

It can be useful for testing or for users who do not require an additional network layer.

Users should understand that direct mode does not provide the privacy properties of Tor or Whonix.

## Proxy Mode

Proxy mode routes SPOT activity through a configured proxy.

The proxy configuration should be explicit.

If the proxy becomes unavailable, SPOT should follow the configured failure policy rather than silently switching to another network path.

## Tor Mode

Tor mode routes supported SPOT activity through Tor.

SPOT should verify that the expected Tor connection is available before starting privacy-sensitive activity.

Tor should not be treated as a guarantee of complete anonymity.

## Whonix Mode

Whonix can provide a dedicated Tor-based network architecture.

When SPOT is used with Whonix, the network engine should respect the existing Whonix routing design rather than attempting to bypass it.

## DNS

DNS requests should follow the configured network path.

The network engine should detect unexpected DNS configuration where practical.

## Firewall

Firewall rules can help prevent unwanted network connections.

A firewall configuration may restrict traffic to the expected interfaces, proxies, or network paths.

Firewall rules should be applied carefully because incorrect rules can interrupt normal system networking.

## Kill Switch

A kill switch can stop network activity when the expected network path is unavailable.

For example:

**Expected network unavailable → SPOT activity stops**

This is particularly useful for privacy-sensitive configurations.

## Network Health

The network engine should monitor whether the configured network path is available.

Possible states include:

* Available
* Unavailable
* Connecting
* Failed
* Blocked

Activities should only run when their network requirements are satisfied.

## Persona Network Separation

Personas should not automatically share network configuration.

Where stronger isolation is required, personas can use separate network environments or Qubes networking.

## Qubes Integration

On Qubes OS, the network engine can work with Qubes networking and Whonix.

Qubes RPC policies should remain explicit and minimal.

SPOT should not require unrestricted dom0 access.

## Network Failure

If the expected network path fails, SPOT should follow the configured failure policy.

For a fail-closed configuration:

**Network failure → Stop activity**

SPOT should not silently switch to a less private network.

## Logging

The network engine should record useful events such as:

* Network mode changes
* Connection failures
* Health-check failures
* Kill-switch activation
* DNS problems
* Emergency shutdown

Sensitive network information should be minimized in logs.

## Safety

The network engine should enforce configured limits where applicable, including:

* Bandwidth
* Connections
* Runtime
* DNS requests

SPOT should not be designed to perform denial-of-service activity, scanning of systems without authorization, or other abusive network behavior.

## Emergency Stop

The network engine must respond to the emergency stop.

Active SPOT network activity should be stopped as quickly and safely as practical.

## Summary

The network engine answers the question:

**"Which network path should this SPOT activity use, and is that path safe to use right now?"**
