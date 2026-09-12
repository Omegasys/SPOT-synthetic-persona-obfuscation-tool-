# SPOT Tor Networking Plugin

The Tor Networking Plugin provides optional Tor networking integration for SPOT.

It provides a controlled interface for configuring and checking a Tor SOCKS
connection while leaving SPOT's core network policy in control.

## Purpose

The plugin can:

- Configure a Tor SOCKS endpoint.
- Validate Tor configuration.
- Check basic Tor connectivity through an approved backend.
- Prepare proxy settings for SPOT.
- Enforce fail-closed behavior.
- Prevent direct-network fallback.
- Associate routing with a SPOT session or persona.

## Security Model

The Tor plugin is an extension, not the security authority.

SPOT's core network layer remains responsible for:

- Network mode.
- Fail-closed behavior.
- Destination restrictions.
- DNS policy.
- Rate limits.
- Bandwidth limits.
- Emergency-stop state.
- Persona isolation.

The plugin must not override those policies.

## Direct Connection Policy

Direct fallback is disabled by default.

If Tor is unavailable and fail-closed mode is enabled:

    SPOT Activity
        |
        v
    Tor Plugin
        |
        X
    Tor unavailable
        |
        v
    Activity blocked

The plugin must never silently change to:

    SPOT Activity
        |
        X Tor
        |
        v
    Direct Internet

## Tor Interface

The default interface is SOCKS5.

Example:

    127.0.0.1:9050

A SOCKS5 hostname-aware endpoint may also be used where supported.

## DNS

The Tor plugin does not provide an independent DNS bypass.

DNS handling remains under SPOT's DNS and network policies.

When remote DNS through a SOCKS-aware backend is required, that behavior must
be explicitly configured.

## Health Checks

Health checks should verify that the configured Tor endpoint is reachable.

A health check does not automatically modify the system's routing.

The plugin should report:

- Available.
- Unavailable.
- Misconfigured.
- Blocked by policy.

## Safety

The plugin must not:

- Disable SPOT's emergency stop.
- Enable direct fallback without explicit policy.
- Modify arbitrary host firewall rules.
- Modify arbitrary routing tables.
- Access credentials.
- Access personal data.
- Provide unrestricted raw network access.
- Bypass SPOT destination restrictions.
- Circumvent security controls.

## Configuration

See:

    config.example.yaml

## Testing

Run:

    pytest plugins/networking/tor/tests/

Tests must not require a running Tor daemon and must not make external
network connections.
