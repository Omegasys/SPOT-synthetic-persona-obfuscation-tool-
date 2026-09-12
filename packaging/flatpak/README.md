# SPOT Flatpak

This directory contains Flatpak packaging files for SPOT.

Flatpak provides stronger application sandboxing than a portable
AppImage because the application is launched inside a sandbox with
explicit permissions.

## Files

- `com.spot.SPOT.yml` — Flatpak build manifest.
- `com.spot.SPOT.desktop` — desktop integration metadata.
- `com.spot.SPOT.svg` — application icon.

## Requirements

Install Flatpak and Flatpak Builder.

On Fedora:

    sudo dnf install flatpak flatpak-builder

On Debian-family systems:

    sudo apt install flatpak flatpak-builder

## Runtime

The SPOT Flatpak uses a standard Freedesktop runtime.

The runtime version should be updated deliberately rather than
automatically changing between releases.

## Building

From the repository root:

    flatpak-builder \
        --user \
        --install \
        --force-clean \
        build/flatpak \
        packaging/flatpak/com.spot.SPOT.yml

## Running

Launch SPOT with:

    flatpak run com.spot.SPOT

## Sandbox

The Flatpak intentionally does not request unrestricted filesystem
access.

In particular, it does not request:

- `home` access;
- arbitrary host filesystem access;
- SSH access;
- credential-store access;
- host device access;
- host system administration;
- host firewall administration.

Network access is available to SPOT because some of its controlled
activity and networking integrations require network communication.

SPOT's own network policy remains responsible for deciding whether
network activity is permitted.

## Limitations

Flatpak cannot provide all of the functionality available to a native
Linux installation.

For example, host-level integrations involving:

- systemd administration;
- privileged namespaces;
- host firewall configuration;
- Qubes OS;
- host network routing;

should remain outside the Flatpak sandbox.

Use the native Linux package or Qubes integration when those
capabilities are required.

## Security

Flatpak is an additional isolation boundary, not a replacement for
SPOT's security model.

SPOT should continue enforcing:

- persona isolation;
- synthetic-only data;
- credential denial;
- browser-profile isolation;
- activity limits;
- network policies;
- emergency stop;
- fail-closed behavior.

## Development

Changes to application behavior belong in the main SPOT source tree.

This directory should contain only Flatpak-specific packaging
configuration.
