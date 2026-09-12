# SPOT Debian Packaging

This directory contains Debian packaging files for SPOT.

The package is intended for Debian-family systems, including Debian and compatible distributions.

## Package

The resulting package is:

    spot

The package installs SPOT under standard Linux filesystem locations.

## Build Requirements

Install the Debian packaging tools:

    sudo apt install build-essential debhelper devscripts fakeroot python3-all python3-setuptools

Additional Python build dependencies may be required depending on the SPOT release.

## Building

From the repository root:

    dpkg-buildpackage -us -uc

This produces a Debian package in the parent directory.

For a local unsigned build:

    dpkg-buildpackage -us -uc -b

## Installing

Install the resulting package with:

    sudo apt install ../spot_<version>_<architecture>.deb

## Service

The package installs:

    spot.service

The service is not automatically enabled or started by the package.

Enable it manually after reviewing the configuration:

    sudo systemctl enable spot.service

Start it with:

    sudo systemctl start spot.service

Check its status with:

    systemctl status spot.service

## Security

SPOT is intended to run as the dedicated `spot` user.

The package should not:

- grant unrestricted root access
- install setuid executables
- enable arbitrary shell execution
- import personal browser profiles
- import credentials
- modify host firewall rules automatically
- modify host routing automatically
- bypass SPOT's network policy
- automatically enable direct networking when fail-closed mode is configured

The systemd service contains additional sandboxing.

## Configuration

System configuration is stored under:

    /etc/spot/

Persistent application data is stored under:

    /var/lib/spot/

Runtime state is stored under:

    /run/spot/

Logs are stored under:

    /var/log/spot/

## Uninstallation

Removing the package should not automatically destroy SPOT state.

This allows an administrator to inspect or back up configuration and data before removal.

## Development

Debian-specific changes should remain in this directory.

Do not modify the SPOT application solely to accommodate Debian packaging unless the behavior is genuinely platform-independent.
