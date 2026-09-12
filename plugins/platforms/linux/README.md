# SPOT Linux Platform Plugin

The Linux platform plugin provides Linux-native integration for SPOT.

It is intended for normal Linux installations where SPOT is running outside Qubes OS.

The plugin provides:

- Linux platform detection
- systemd integration
- service lifecycle information
- local process supervision information
- Linux filesystem path validation
- sandbox capability checks
- network-state checks
- resource-limit awareness
- emergency-stop state handling
- controlled integration with the SPOT core
- fail-closed behavior

The plugin does not replace SPOT's core isolation, network, safety, or browser systems.

## Security Model

The Linux plugin follows these principles:

- default deny
- least privilege
- fail closed
- no unrestricted root access
- no arbitrary shell execution
- no arbitrary command execution
- no unrestricted filesystem access
- no automatic firewall modification
- no automatic routing-table modification
- no credential access
- no personal browser-profile access
- no personal-data import
- no direct network fallback when disabled
- emergency stop blocks new activity

The plugin is an integration layer rather than a general-purpose Linux administration tool.

## systemd

The plugin includes example systemd units:

- `spot-plugin.service`
- `spot-plugin.timer`

The service should run under a dedicated unprivileged `spot` account.

The service does not need to run as root for normal SPOT operation.

Systemd hardening options are included where practical.

## Sandboxing

Linux sandboxing can be provided by several mechanisms depending on the host:

- systemd sandboxing
- Linux namespaces
- seccomp
- AppArmor
- SELinux
- bubblewrap
- containers

The plugin only reports or prepares the required policy.

Actual privileged sandbox construction belongs to the appropriate restricted backend.

## Networking

The Linux plugin does not silently change host networking.

Network routing remains controlled by the SPOT network subsystem.

Possible SPOT network modes include:

- disabled
- direct
- proxy
- Tor
- Whonix

For privacy-sensitive operation, Whonix or Tor should be explicitly configured.

If fail-closed mode is enabled, an unavailable required network backend prevents activity.

## Filesystem

The Linux plugin does not provide unrestricted access to the host filesystem.

SPOT should use dedicated directories for:

- configuration
- runtime state
- logs
- browser profiles
- persona data
- temporary files

Personal directories and credential stores should not be imported.

## Emergency Stop

When the emergency stop is active:

- new SPOT activity is blocked
- new sessions are blocked
- network activity requested through SPOT is blocked
- scheduled activity is blocked
- browser activity is blocked
- the plugin reports the blocked state

The plugin does not assume that it can safely terminate arbitrary host processes.

Privileged shutdown actions, if ever required, must be implemented by a separate narrowly scoped integration.

## Installation

The plugin is disabled by default.

Enable it only after reviewing:

- `config.example.yaml`
- systemd units
- filesystem permissions
- network configuration
- sandbox configuration

## Development

The Linux plugin should remain small.

Platform-specific behavior should not leak into the SPOT core unless a generic interface is required.

Changes should include unit tests.

Tests must not require root privileges or modify the host system.
