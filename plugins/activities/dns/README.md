# DNS Activity Plugin

The DNS Activity Plugin provides a controlled interface for synthetic DNS activity.

It is designed to work with SPOT's existing DNS policy and network layers.

The plugin does not implement an independent DNS resolver.

## Purpose

The plugin can:

- Prepare synthetic DNS queries.
- Validate domain names.
- Associate queries with a SPOT persona.
- Apply query limits.
- Apply domain allowlists and blocklists.
- Produce bounded DNS activity requests.
- Delegate actual DNS handling to SPOT's network layer.

## Important Design Rule

This plugin must not become a DNS-leak mechanism.

Actual DNS resolution should be performed by SPOT's configured network backend.

For example:

    SPOT
      |
      +-- DNS Activity Plugin
      |
      +-- SPOT DNS Policy
      |
      +-- SPOT Network Manager
      |
      +-- Whonix/Tor or approved network backend

The plugin must never silently fall back to the host's resolver.

## Supported Queries

The plugin is intended for normal DNS activity such as:

- A
- AAAA
- CNAME
- MX
- NS
- TXT

Additional record types should require explicit support.

## Safety

The plugin must:

- Respect emergency stop.
- Respect DNS limits.
- Respect rate limits.
- Respect domain blocklists.
- Respect domain allowlists.
- Reject loopback addresses.
- Reject private destinations where required by policy.
- Fail closed when the network backend is unavailable.

The plugin must not:

- Perform DNS scanning.
- Enumerate large address ranges.
- Perform DNS amplification.
- Generate bulk DNS traffic.
- Bypass network policy.
- Bypass Tor or Whonix routing.
- Use unrestricted host DNS.

## Privacy

DNS queries can be sensitive.

The plugin should minimize local logging and should not store complete DNS history unless explicitly enabled by a future privacy-preserving configuration.

## Configuration

See:

    config.example.yaml

## Testing

Run:

    pytest plugins/activities/dns/tests/

Tests must not perform real DNS queries.
