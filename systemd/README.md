# SPOT systemd Integration

This directory contains optional systemd units for running SPOT as a
managed Linux service.

The units are:

- `spot.service` — normal SPOT runtime.
- `spot.timer` — scheduled SPOT activation.
- `spot-emergency.service` — persistent application-level emergency stop.

## Security Model

The systemd integration follows SPOT's least-privilege model.

The normal service:

- Runs as the dedicated `spot` user.
- Does not run as root.
- Does not receive arbitrary capabilities.
- Does not use shell commands through systemd.
- Uses a private temporary directory.
- Protects the host filesystem.
- Protects `/home` and other user data.
- Cannot directly manipulate kernel modules.
- Cannot directly manipulate kernel tunables.
- Cannot directly access physical devices.
- Cannot create arbitrary Linux namespaces.
- Has access only to SPOT's designated state/log/runtime paths.

The service should not be granted unrestricted access to the host merely
because SPOT may integrate with Qubes OS, Whonix, Tor, containers, or
other isolation systems.

Privileged operations belong in narrowly scoped integration components
with their own explicit policies.

## Installation

Create the dedicated service account:

```bash
sudo useradd \
    --system \
    --home /var/lib/spot \
    --create-home \
    --shell /usr/sbin/nologin \
    spot
