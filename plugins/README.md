# SPOT Plugins

This directory contains optional plugins for SPOT (Synthetic Persona Obfuscation Tool).

Plugins extend SPOT without becoming part of the trusted core.

## Plugin Categories

### Activities

Activity plugins provide optional implementations for synthetic activities.

- Search
- Browser
- News
- Media
- DNS

### Networking

Networking plugins provide network backends.

- Tor
- Whonix
- Proxy

### Platforms

Platform plugins provide operating-system or virtualization integration.

- Qubes
- Linux

## Security Model

Plugins are untrusted extensions by default.

A plugin:

- Must explicitly declare its capabilities.
- Must run with only the permissions it needs.
- Must not access credentials.
- Must not access personal data.
- Must not access unrestricted filesystem paths.
- Must not bypass SPOT safety controls.
- Must not disable the emergency stop.
- Must not bypass network policies.
- Must not perform unrestricted network activity.
- Must not perform privileged operations unless a narrowly scoped backend explicitly permits them.
- Must not access Qubes `dom0` without an explicitly defined and restricted integration.
- Must not import personal browser profiles or credentials.

Plugins should fail safely when a required capability is unavailable.

## Development

Plugins should use the SPOT plugin interface:

    src/spot/plugins/interface.py

A plugin normally contains:

- `plugin.py` — implementation.
- `manifest.yaml` — metadata and requested capabilities.
- `config.example.yaml` — example configuration.
- `README.md` — documentation.
- `tests/` — plugin tests.

Plugins should be deterministic and testable wherever possible.

## Installation

Plugins should not be automatically enabled merely because their files exist.

A plugin should be:

1. Installed.
2. Discovered by SPOT.
3. Validated.
4. Granted explicitly requested capabilities.
5. Enabled by the administrator.

Plugins should remain disabled by default.

## Synthetic Activity Requirement

Activity plugins are intended to support synthetic, controlled activity.

They must not be used for:

- Spam.
- Bulk messaging.
- Harassment.
- Fraud.
- Impersonation of real people.
- Credential theft.
- Authentication bypass.
- CAPTCHA bypass.
- Security-control bypass.
- Denial-of-service activity.
- Unrestricted automated scanning.

SPOT does not guarantee anonymity, unlinkability, or successful manipulation of external profiling systems.

## Plugin Safety

The plugin manager should reject plugins that request prohibited capabilities.

Plugins should also respect:

- Activity limits.
- Request limits.
- Bandwidth limits.
- Runtime limits.
- Domain allowlists.
- Domain blocklists.
- Network routing policies.
- Browser isolation.
- Persona isolation.
- Emergency-stop state.

The core remains authoritative over these controls.

## License

SPOT is licensed under the GNU General Public License version 3.
