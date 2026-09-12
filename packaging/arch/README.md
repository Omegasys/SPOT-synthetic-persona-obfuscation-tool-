# SPOT Arch Linux Packaging

This directory contains the Arch Linux package definition for SPOT.

The package is built using the Arch Linux `makepkg` system.

## Package

The package name is:

    spot

## Requirements

Install the Arch packaging tools:

    sudo pacman -S --needed base-devel python python-setuptools

## Building

From this directory:

    makepkg -s

This downloads required sources, builds the package, and produces a
local package file.

For a clean rebuild:

    makepkg -Cfs

## Installing

Install the generated package with:

    sudo pacman -U ./spot-<version>-<release>-any.pkg.tar.zst

## Updating

When a new SPOT version is released, update the following in
`PKGBUILD`:

- `pkgver`
- `pkgrel`
- source information
- checksums

## Service

The package installs:

    spot.service

The service is not automatically enabled.

After reviewing the configuration:

    sudo systemctl enable spot.service

Start SPOT with:

    sudo systemctl start spot.service

Check the service:

    systemctl status spot.service

## Security

SPOT runs under a dedicated `spot` service account.

The package does not intentionally provide:

- unrestricted root access;
- arbitrary shell execution;
- arbitrary command execution;
- unrestricted filesystem access;
- credential access;
- personal browser-profile access;
- automatic firewall administration;
- automatic routing-table administration.

The systemd service provides additional sandboxing.

## Directories

SPOT uses:

    /etc/spot/
    /var/lib/spot/
    /run/spot/
    /var/log/spot/

## Privacy

Installing SPOT does not itself provide anonymity.

Tor and Whonix remain separate networking integrations.

If fail-closed network mode is configured, SPOT should not silently
fall back to direct networking.

## Development

Keep Arch-specific packaging changes inside this directory.

Do not weaken SPOT's security model to accommodate packaging
convenience.
