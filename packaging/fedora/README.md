# SPOT Fedora Packaging

This directory contains RPM packaging files for SPOT.

The package is intended for Fedora and compatible RPM-based Linux
distributions.

## Package

The resulting RPM package is:

    spot

## Build Requirements

Install the Fedora packaging tools:

    sudo dnf install rpm-build rpmdevtools python3-devel python3-setuptools

For a clean RPM build environment:

    rpmdev-setuptree

## Building

From the repository root, the SPEC file can be built with:

    rpmbuild -ba packaging/fedora/spot.spec

The resulting RPM files are placed under:

    ~/rpmbuild/RPMS/

Source RPM files are placed under:

    ~/rpmbuild/SRPMS/

## Installing

Install the resulting RPM with:

    sudo dnf install ~/rpmbuild/RPMS/noarch/spot-<version>-<release>.noarch.rpm

## Service

The package installs:

    spot.service

The service is not automatically enabled or started.

After reviewing the configuration, enable it with:

    sudo systemctl enable spot.service

Start it with:

    sudo systemctl start spot.service

Check it with:

    systemctl status spot.service

## Directories

SPOT uses:

    /etc/spot/
    /var/lib/spot/
    /run/spot/
    /var/log/spot/

## Security

SPOT should run as the dedicated `spot` user.

The package must not:

- grant unrestricted root access;
- install setuid executables;
- enable arbitrary shell execution;
- import personal browser profiles;
- import credentials;
- modify host firewall rules automatically;
- modify host routing automatically;
- bypass SPOT network policy;
- silently fall back to direct networking when fail-closed mode is enabled.

The systemd service provides additional sandboxing.

## SELinux

Fedora systems commonly use SELinux.

The SPOT package should not disable SELinux or attempt to replace the
system SELinux policy.

A future SPOT release may provide a dedicated SELinux policy package
if additional confinement is required.

## Uninstallation

Removing the RPM should not automatically delete SPOT configuration,
state, or logs.

Administrators should inspect or back up these directories before
removing them.

## Development

Fedora-specific packaging changes belong in this directory.

Security behavior should remain consistent with the main SPOT project.
