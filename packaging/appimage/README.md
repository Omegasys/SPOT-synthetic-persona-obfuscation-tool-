# SPOT AppImage

This directory contains the AppImage packaging files for SPOT.

The AppImage provides a portable Linux distribution format for SPOT
without requiring installation into the host filesystem.

## Files

- `AppRun` — application launcher.
- `spot.desktop` — desktop integration metadata.
- `spot.svg` — SPOT application icon.
- `build-appimage.sh` — AppImage build script.

## Requirements

The build environment requires:

- Python 3
- the SPOT build dependencies
- `appimagetool`

`appimagetool` should be installed separately from the official
AppImage ecosystem.

## Building

From the repository root:

    ./packaging/appimage/build-appimage.sh

The resulting AppImage is written to:

    dist/

The filename follows this general format:

    SPOT-<version>-<architecture>.AppImage

## Running

Make the AppImage executable:

    chmod +x SPOT-*.AppImage

Then launch it:

    ./SPOT-*.AppImage

## Security

The AppImage does not grant SPOT additional privileges.

It should not:

- require root;
- access credentials;
- import personal browser profiles;
- access arbitrary personal files;
- modify the host firewall;
- modify host routing;
- execute arbitrary host commands;
- bypass SPOT network policy.

AppImage itself is not a security sandbox.

For stronger isolation, use SPOT through:

- systemd sandboxing;
- bubblewrap;
- a dedicated Linux account;
- Qubes OS;
- Whonix;
- another appropriate operating-system isolation mechanism.

## Networking

The AppImage does not provide anonymity by itself.

Tor and Whonix remain separate SPOT networking integrations.

If fail-closed networking is configured, SPOT should not silently
fall back to direct networking.

## Updates

The AppImage should not automatically replace itself.

Updates should be obtained through the project's normal release
process and verified before installation.

## Development

The AppImage packaging should remain a thin distribution layer.

Application behavior belongs in the SPOT source tree.
