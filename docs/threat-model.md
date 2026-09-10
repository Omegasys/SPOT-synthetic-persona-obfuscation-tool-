# SPOT Threat Model

This document describes the main threats SPOT is designed to address and the threats that remain outside its control.

## Purpose

SPOT creates and manages synthetic personas.

The main security objective is to prevent information from crossing between:

* The real user
* Different synthetic personas
* Different network environments

## Assets

SPOT may contain:

* Persona profiles
* Synthetic interests
* Synthetic preferences
* Synthetic routines
* Synthetic memory
* Activity history
* Browser profiles
* Network configuration
* Audit logs
* Safety configuration

Real passwords, authentication tokens, private documents, and personal browser data should not normally be present in SPOT.

## Threats

### Cross-Persona Leakage

One persona could gain access to another persona's information.

Examples include:

* Reading another persona's cookies
* Reading another persona's browser history
* Accessing another persona's files
* Accessing another persona's synthetic memory

Mitigations include filesystem permissions, process isolation, separate browser profiles, containers, namespaces, and Qubes isolation.

### Real-Identity Leakage

Synthetic activity could accidentally contain information belonging to the real user.

Examples include:

* Reusing a personal browser profile
* Reusing personal cookies
* Logging into a personal account
* Uploading a personal file
* Using a real authentication token

SPOT should prevent these operations by default.

### Network Leakage

Activity could bypass the intended network path.

For example, traffic intended to use Tor could accidentally use a direct connection.

Mitigations include:

* Explicit routing
* Firewall rules
* Kill switches
* Network health checks
* Fail-closed configuration
* Whonix integration
* Qubes networking

### DNS Leakage

DNS requests could bypass the intended network path.

SPOT should use explicit DNS configuration and avoid unexpected fallback resolvers.

### Browser Leakage

Browser state could allow different personas or sessions to become linked.

Potential sources include:

* Cookies
* Local storage
* Cache
* History
* Extensions
* Persistent browser state
* Fingerprinting characteristics

SPOT should use separate browser profiles and isolated sessions where appropriate.

### Predictable Activity

If every persona behaves in exactly the same way, the activity may become easier to recognize or correlate.

SPOT can reduce this problem through:

* Persona-specific routines
* Randomized scheduling
* Variable activity timing
* Probability-based activity selection
* Activity limits

Randomization should remain controlled and should never override safety limits.

### Resource Exhaustion

SPOT could accidentally consume excessive:

* CPU
* Memory
* Disk space
* Bandwidth
* Network requests
* Browser processes

SPOT should use resource and activity limits to reduce this risk.

### Malicious Plugins

A plugin could attempt to access information beyond its intended purpose.

Mitigations include:

* Explicit permissions
* Capability restrictions
* Plugin review
* Sandboxing where practical
* No automatic credential access

### Compromised Dependencies

A third-party dependency could contain a vulnerability or malicious code.

Mitigations include:

* Dependency updates
* Security scanning
* Dependency review
* Minimal dependencies
* Signed releases where practical
* Reproducible builds where practical

### Local Data Exposure

An attacker with access to the computer could potentially access SPOT's stored data.

Mitigations include:

* Data minimization
* Encryption
* File permissions
* Qubes isolation
* Limited data retention

## Qubes Threats

Incorrect Qubes configuration can weaken isolation.

Important risks include:

* Overly permissive RPC policies
* Unnecessary inter-qube communication
* Excessive dom0 access
* Incorrect networking
* Shared storage between personas

SPOT should document the minimum permissions required for its Qubes integration.

## Threats Outside SPOT's Control

SPOT does not guarantee protection against:

* Global traffic analysis
* Compromised operating systems
* Hardware compromise
* Browser zero-days
* Advanced fingerprinting
* External data brokers
* Account-level correlation
* Third-party information
* User configuration mistakes

## Trust Boundaries

The main trust boundaries are:

**Real User → SPOT**

Real user information should not automatically cross into SPOT.

**Persona → Persona**

Personas should not automatically access one another.

**SPOT → Network**

SPOT should only use the network path configured by the user.

**Plugin → SPOT**

Plugins should only receive explicitly granted capabilities.

**SPOT → Qubes**

Qubes integration should use explicit policies and minimum required permissions.

## Security Priorities

The highest-priority threats are:

1. Real credentials entering SPOT.
2. Cross-persona credential leakage.
3. Unexpected direct network connections.
4. Unrestricted Qubes or dom0 access.
5. Cross-persona filesystem access.
6. Browser profile leakage.
7. DNS leakage.
8. Excessive plugin permissions.

## Security Assumptions

SPOT assumes that:

* The operating system is not already fully compromised.
* The user understands their network configuration.
* Qubes policies are correctly configured when Qubes is used.
* Browser software is reasonably current.
* Dependencies are reasonably trustworthy.
* The user does not intentionally place real credentials inside synthetic environments.

## Summary

SPOT's main security goal is separation.

The desired model is:

**Real identity → isolated SPOT environment → isolated synthetic personas → explicitly controlled network**

SPOT should make accidental crossover difficult and should make important security failures visible to the user.
