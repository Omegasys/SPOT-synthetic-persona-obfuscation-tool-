Security Policy

SPOT — Synthetic Persona Obfuscation Tool

SPOT is a Linux-native framework for creating, managing, and running isolated synthetic personas and their associated activity.

Security and isolation are core design requirements of SPOT. The project is designed so that synthetic personas can operate independently from the user’s real digital identity.

⸻

Supported Versions

Security fixes are primarily provided for the latest stable release.

Version	Supported
Latest stable	Yes
Previous stable	Best effort
Development/nightly	Best effort
End-of-life releases	No

Users should upgrade to the latest stable release whenever possible.

⸻

Security Philosophy

SPOT follows several fundamental security principles:

1. Isolation by default
2. Least privilege
3. No unnecessary collection of user data
4. No dependence on real credentials
5. Explicit network boundaries
6. Fail closed where practical
7. Local control
8. Auditable behavior
9. Minimal trust between components
10. Safe failure and emergency shutdown

SPOT is not intended to replace a properly configured operating-system security model, firewall, VPN, Tor, Whonix, Qubes OS, or other security technology.

Instead, SPOT is designed to operate alongside these technologies.

⸻

Threat Model

SPOT considers several classes of threats.

1. Cross-Persona Leakage

A synthetic persona must not unintentionally gain access to:

* Real user browser profiles
* Real cookies
* Real authentication tokens
* Passwords
* SSH keys
* Cryptocurrency wallets
* Personal documents
* Private photographs
* Personal email
* Real social-media accounts
* Other personas’ private state

Persona separation is therefore treated as a security boundary.

⸻

2. Network Leakage

SPOT may support multiple networking configurations.

Examples include:

* Direct networking
* VPN/proxy routing
* Tor
* Whonix
* Qubes networking

If a persona is configured to use a specific network path, SPOT should detect failures where practical rather than silently falling back to an unintended path.

For example:

Persona
   |
   v
Configured Network
   |
   +---- Available ----> Continue
   |
   +---- Unavailable ---> Stop / Fail Closed

The exact behavior should be configurable by the user.

⸻

3. Credential Leakage

SPOT should never require the user’s real credentials to generate synthetic activity.

The application must not automatically import:

* Browser passwords
* Password-manager databases
* SSH credentials
* API keys
* Authentication cookies
* Session tokens
* Private certificates

If an integration requires credentials, they must be explicitly configured and clearly separated from persona state.

⸻

Persona Isolation

Every persona should have an independent security context.

A typical persona should have its own:

Persona
├── Configuration
├── Browser profile
├── Cookies
├── Cache
├── Local storage
├── History
├── Behavioral memory
├── Activity history
└── Network configuration

A persona should not automatically have access to another persona’s directory.

Where supported, stronger isolation should be used.

Examples include:

* Linux namespaces
* Containers
* Sandboxing
* Separate system users
* Qubes qubes
* Disposable Qubes
* Whonix-based networking

⸻

Qubes OS

SPOT may support Qubes OS as an optional high-isolation deployment.

A recommended architecture is:

                    dom0
                      |
              SPOT Controller
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
   Persona 01     Persona 02    Persona 03
        |             |             |
    Network 01    Network 02    Network 03

The controller should not automatically have unrestricted access to persona contents.

Qubes RPC policies should be used to explicitly define permitted operations.

Users should review generated Qubes policies before deployment.

⸻

Browser Security

Each synthetic persona should preferably receive an independent browser profile.

SPOT should avoid sharing:

* Cookies
* Local storage
* Indexed databases
* Authentication sessions
* Browser history
* Cached credentials

Browser automation must also include safety controls to prevent accidental navigation to unintended destinations.

SPOT should not attempt to defeat website authentication, access controls, CAPTCHAs, paywalls, or other security mechanisms.

⸻

Network Security

SPOT’s networking subsystem should support explicit policies.

Example:

PERSONA: Example
Allowed:
    HTTP/HTTPS
    DNS
Routing:
    Whonix/Tor
Fallback:
    NONE
Kill Switch:
    ENABLED

If the configured routing path disappears, SPOT should stop activity when fail-closed mode is enabled.

SPOT should not silently switch from a privacy network to a direct connection.

⸻

DNS Security

SPOT may generate synthetic DNS activity as part of its activity engine.

DNS behavior should respect the persona’s configured network path.

For example:

Persona
   |
   v
SPOT DNS Engine
   |
   v
Configured Resolver
   |
   v
Network Isolation

DNS requests should not bypass the configured privacy/network boundary.

⸻

Data Storage

SPOT should minimize persistent data.

Where persistent state is required, it should be limited to information necessary for:

* Persona configuration
* Behavioral state
* Scheduling
* Local statistics
* Debugging
* Audit logs

Sensitive local state should support encryption.

The project should never transmit stored persona data to a central SPOT server by default.

⸻

Telemetry

SPOT should not require centralized telemetry.

The default configuration should provide:

Telemetry:
    Disabled

Local statistics may be enabled by the user.

If optional telemetry is ever introduced, it must be:

* Explicitly opt-in
* Documented
* Minimally scoped
* Configurable
* Disableable
* Free of unnecessary personal information

⸻

Logging

Logs should avoid storing sensitive information unnecessarily.

Logs should not contain:

* Passwords
* Authentication tokens
* Private keys
* Session cookies
* Full personal documents
* Unredacted private URLs when unnecessary

Sensitive values should be redacted.

Example:

API_TOKEN=********
SESSION_COOKIE=********

The audit system should distinguish between:

Operational logs
Security logs
Debug logs
Audit events

⸻

Emergency Stop

SPOT should provide an emergency-stop mechanism.

Example:

spot emergency-stop

An emergency stop should attempt to:

1. Stop active synthetic sessions.
2. Stop browser automation.
3. Stop scheduled tasks.
4. Stop network activity where possible.
5. Terminate temporary processes.
6. Remove temporary session state.
7. Record a local security event.

The emergency-stop mechanism should remain usable even if the normal scheduler or activity engine is malfunctioning.

⸻

Safety Limits

SPOT should provide configurable limits for automated activity.

Examples:

Maximum concurrent personas
Maximum concurrent sessions
Maximum requests per session
Maximum daily activity
Maximum bandwidth
Maximum runtime
Maximum browser instances
Maximum DNS requests
Maximum CPU usage
Maximum memory usage

These controls reduce the possibility of runaway automation.

⸻

Domain Controls

SPOT should support:

Allowlist
Blocklist
Category restrictions
Per-persona restrictions
Global restrictions

A global blocklist should take precedence over persona-specific settings.

Example:

Global Policy
     |
     +-- Blocked Domain
     |
     X
     |
Persona Activity

SPOT should not intentionally interact with clearly malicious infrastructure.

⸻

Abuse Prevention

SPOT is intended for privacy research, defensive privacy engineering, experimentation, and controlled synthetic activity.

SPOT should not be designed to:

* Conduct denial-of-service attacks
* Circumvent authentication
* Steal accounts
* Bypass access controls
* Automate harassment
* Send unsolicited bulk messages
* Generate fraudulent transactions
* Impersonate real individuals
* Circumvent security controls
* Attack third-party infrastructure

Activity generators should therefore use conservative defaults and explicit safety boundaries.

⸻

Dependency Security

Dependencies should be minimized.

The project should:

* Pin or constrain dependencies where appropriate.
* Regularly review dependencies.
* Monitor known vulnerabilities.
* Remove abandoned dependencies when practical.
* Verify release artifacts where possible.
* Use automated dependency scanning.
* Run security tests in CI.

GitHub Actions should include security checks before releases.

⸻

Supply-Chain Security

Official releases should be reproducible where practical.

Release artifacts should eventually support:

* Cryptographic hashes
* Signed releases
* Signed Git tags
* Reproducible builds
* SBOM generation
* Dependency provenance

Users should be able to verify that an installed release corresponds to the published source.

⸻

Plugin Security

SPOT plugins should be treated as potentially untrusted code.

Installing a plugin should not automatically grant unrestricted access to:

* The host filesystem
* Other personas
* Credentials
* Network interfaces
* Qubes management
* SPOT’s internal databases

Where possible, plugins should operate under explicit capability permissions.

Example:

Plugin
 |
 +-- browser.access
 +-- network.access
 +-- persona.read
 |
 X-- credentials.access
 X-- other_personas.write
 X-- unrestricted_filesystem

⸻

Qubes RPC Security

Qubes integrations should use explicit RPC policies.

SPOT should never require:

unrestricted dom0 access

unless absolutely necessary.

Any operation requiring dom0 interaction should be documented and independently reviewable.

Users should be able to disable optional Qubes functionality without disabling the core application.

⸻

Secure Defaults

A fresh SPOT installation should favor safety over convenience.

Recommended defaults:

Telemetry:
    OFF
Real credentials:
    NEVER IMPORT
Real browser profiles:
    NEVER IMPORT
Cross-persona access:
    DENIED
Plugin permissions:
    DENIED
Network fallback:
    DISABLED
Emergency stop:
    ENABLED
Activity limits:
    ENABLED
Persistent sensitive state:
    MINIMIZED
Debug logging:
    OFF

Users may explicitly relax individual restrictions when necessary.

⸻

Security Testing

The project should maintain automated security tests covering:

Persona isolation
Browser isolation
Network isolation
DNS leakage
Credential exposure
Filesystem permissions
Plugin permissions
Qubes RPC policies
Emergency shutdown
Scheduler failures
Configuration validation
Malformed persona files
Resource exhaustion
Dependency vulnerabilities

Fuzz testing should eventually be used for parsers and configuration interfaces.

⸻

Reporting a Vulnerability

Do not publicly disclose an undisclosed security vulnerability through a GitHub issue.

Instead, use the repository’s private security reporting mechanism if available.

A security report should include:

Affected version:
Operating system:
Installation method:
Component:
Description:
Reproduction steps:
Expected behavior:
Actual behavior:
Security impact:
Proof of concept:
Suggested mitigation:

Please avoid including real passwords, credentials, private keys, personal information, or other sensitive data in a vulnerability report.

⸻

Responsible Disclosure

SPOT follows a responsible-disclosure approach.

The maintainers will attempt to:

1. Confirm the vulnerability.
2. Determine its severity.
3. Develop and test a fix.
4. Release the fix.
5. Publish an appropriate security advisory.
6. Credit the reporter when requested and appropriate.

⸻

Security Advisories

Security advisories should document:

* Affected versions
* Fixed versions
* Severity
* Impact
* Mitigation
* Upgrade instructions
* Relevant CVE/GHSA identifiers when applicable

⸻

Important Limitations

SPOT does not guarantee anonymity, untraceability, or successful profile manipulation.

Synthetic activity can itself become observable.

Modern services may correlate information using factors including:

* IP addresses
* Browser characteristics
* Device characteristics
* Timing
* Cookies
* Account relationships
* Network metadata
* Behavioral patterns
* Application telemetry
* Third-party trackers
* Data obtained from other sources

SPOT should therefore be considered a privacy engineering and synthetic-activity framework, not an anonymity guarantee.

For high-risk applications, users should independently evaluate their entire threat model rather than relying on SPOT alone.

⸻

Security Design Goal

The long-term security goal of SPOT is:

                    REAL USER
                        |
                  ┌─────┴─────┐
                  │           │
                  v           v
              REAL WORLD    SPOT
                              |
                    ┌─────────┼─────────┐
                    │         │         │
                    v         v         v
                 Persona   Persona   Persona
                    01        02        03
                    │         │         │
                 Isolated   Isolated   Isolated
                    │         │         │
                 Network   Network   Network
                    │         │         │
                    └─────────┼─────────┘
                              |
                         Internet

The fundamental security property SPOT strives for is:

Synthetic activity should remain synthetic, isolated, controlled, and explicitly separated from the user’s real identity.

Security is considered a core architectural property of SPOT rather than an optional feature added after the activity engine is implemented.