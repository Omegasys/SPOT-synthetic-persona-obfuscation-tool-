# SPOT Snap

This directory contains the Snap packaging for SPOT.

## Purpose

The Snap provides a convenient, confined way to install and run SPOT
on Linux systems supporting Snap.

SPOT's security model remains active inside the Snap.

The Snap is not intended to replace:

- Qubes OS isolation
- Whonix
- Tor
- host firewalls
- AppArmor
- SELinux
- systemd sandboxing
- dedicated network namespaces

Instead, the Snap adds another application-level isolation boundary.

## Confinement

SPOT uses strict Snap confinement.

The initial package should use the smallest possible set of
interfaces.

Network access is explicitly declared rather than granting broad
system access.

SPOT must not require unrestricted access to:

- `/root`
- `/etc`
- `/proc`
- `/sys`
- `/var/lib`
- SSH credentials
- browser credentials
- password stores
- arbitrary host processes
- firewall configuration
- routing configuration
- Qubes dom0

## Network Architecture

The Snap's network interface provides ordinary application network
connectivity.

It does not itself guarantee Tor or Whonix routing.

For Tor or Whonix operation, SPOT should use its network abstraction
layer and require the appropriate external service.

If a configured privacy network is unavailable and fail-closed mode is
enabled, SPOT should stop network-dependent activity rather than
silently falling back to a direct connection.

## Qubes OS

The Snap is not the preferred mechanism for privileged Qubes
integration.

On Qubes OS, the native Qubes integration should be used for:

- qube creation
- disposable qubes
- RPC policies
- network qubes
- Whonix integration
- persona-to-qube assignment

The Snap should never require unrestricted dom0 access.

## Data

Runtime data should be stored in the user's Snap data directory.

SPOT should continue to apply its own:

- encryption
- retention limits
- log redaction
- persona isolation
- credential restrictions
- emergency-stop behavior

## Building

Install Snapcraft and build from the repository root:

    snapcraft pack

The resulting `.snap` package can be tested locally before publication.

## Installing a local build

A locally built Snap can be installed with:

    sudo snap install ./spot-privacy_0.1.0_amd64.snap --dangerous

The `--dangerous` option is required for a locally built package that
has not been signed and published through the Snap Store.

## Testing

Before publication, test:

- installation
- removal
- refresh
- confinement
- network failure
- Tor failure
- Whonix failure
- emergency stop
- persona isolation
- configuration permissions
- log permissions
- plugin loading
- application startup
- clean shutdown

## Security Principle

The Snap is an additional containment layer, not a replacement for
SPOT's security model.

SPOT should fail closed when its configured security boundary cannot
be established.
