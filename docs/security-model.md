# SPOT Security Model

SPOT is designed around isolation, least privilege, data minimization, and explicit security boundaries.

The main security goal is to keep synthetic activity separate from the user's real identity and from other synthetic personas.

## Security Goals

SPOT aims to:

1. Isolate personas from one another.
2. Keep real user information out of synthetic environments.
3. Prevent unexpected network routing.
4. Prevent accidental credential exposure.
5. Minimize sensitive stored information.
6. Provide useful local auditing.
7. Provide an emergency shutdown mechanism.
8. Fail safely when possible.
9. Use secure defaults.
10. Give the user control over security-sensitive settings.

## Isolation by Default

Personas should be isolated unless communication is explicitly required.

Isolation should cover:

* Files
* Processes
* Browser profiles
* Cookies
* Local storage
* History
* Synthetic memory
* Activity state
* Network configuration

## Least Privilege

SPOT components should receive only the permissions they need.

For example, a browser component should only need access to its assigned browser profile, while a persona should not automatically have access to another persona's files.

## Real Credentials

SPOT should not require real credentials.

Real passwords, authentication tokens, private keys, banking information, and personal browser sessions should not be imported into synthetic personas.

## Network Security

The network path should always be explicitly configured.

SPOT may support direct connections, proxies, Tor, or Whonix depending on the installation.

A privacy-sensitive configuration should be able to fail closed.

For example, if Tor is required but unavailable, SPOT should stop the activity instead of automatically switching to a direct connection.

## DNS Security

DNS traffic should follow the configured network path.

SPOT should avoid unexpected DNS requests through an unrelated resolver.

## Browser Security

Each persona should have a separate browser profile.

Browser state such as cookies, history, cache, and local storage should remain isolated between personas.

SPOT should not automatically import the user's personal browser profile.

## Qubes Security

Qubes integration should use explicit RPC policies and minimal permissions.

SPOT should not require unrestricted access to dom0.

Where appropriate, separate qubes or disposable qubes can be used for additional isolation.

## Storage Security

SPOT should minimize the amount of sensitive information it stores.

Potentially sensitive information includes:

* Persona data
* Activity history
* Synthetic memory
* Browser state
* Network configuration
* Logs

Sensitive local data should be encrypted where appropriate.

## Logging

Logs should provide useful information without unnecessarily exposing sensitive data.

Sensitive values should be redacted.

Debug logging should be disabled by default.

## Plugins

Plugins should be treated as potentially untrusted software.

Plugins should have explicit permissions and should only receive the capabilities they need.

A plugin should not automatically receive unrestricted filesystem, network, persona, or Qubes access.

## Safety Limits

SPOT should provide limits for:

* Concurrent personas
* Browser sessions
* Requests
* Bandwidth
* Runtime
* DNS activity
* CPU usage
* Memory usage

These limits help prevent accidental excessive activity and resource exhaustion.

## Emergency Shutdown

SPOT should provide:

`spot emergency-stop`

The emergency stop should terminate SPOT-controlled activity and prevent automatic restarting until the user explicitly starts SPOT again.

## Secure Defaults

Recommended defaults include:

* Telemetry disabled
* Credential import disabled
* Real browser profile import disabled
* Cross-persona access denied
* Plugin permissions denied until granted
* Network fallback disabled
* Emergency stop enabled
* Activity limits enabled
* Sensitive state minimized
* Debug logging disabled

## Updates and Dependencies

SPOT depends on external software and libraries.

The project should use:

* Regular dependency updates
* Vulnerability scanning
* Minimal dependencies
* Dependency review
* Signed releases where practical
* Reproducible builds where practical
* SBOM generation where practical

## Security Limitations

SPOT cannot protect against every possible threat.

Security may still be affected by:

* A compromised operating system
* Vulnerable software
* Malicious browser extensions
* Malicious plugins
* Hardware compromise
* Incorrect Qubes configuration
* Incorrect network configuration
* User mistakes

SPOT should therefore be considered one layer of a larger security architecture.

## Security Principle

The central security principle of SPOT is:

**Synthetic activity should never require compromising the user's real identity.**
