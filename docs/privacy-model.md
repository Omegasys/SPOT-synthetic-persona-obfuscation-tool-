# SPOT Privacy Model

SPOT is designed around local control, data minimization, persona separation, and explicit configuration.

The privacy model is based on the idea that synthetic activity should not require exposing the user's real personal information.

## Privacy Goals

SPOT aims to provide:

* Separation between real and synthetic activity
* Separation between synthetic personas
* Local-first operation
* Minimal data collection
* No mandatory cloud service
* No unnecessary telemetry
* Explicit network configuration
* Isolated browser state
* User-controlled data retention

## Data Categories

SPOT may store several types of information.

### Persona Data

Examples include:

* Synthetic names
* Interests
* Preferences
* Demographic information
* Routines
* Activity preferences
* Synthetic memory

### Runtime Data

Examples include:

* Current activity
* Scheduler state
* Browser session state
* Network state
* Process state

### Historical Data

Examples include:

* Activity history
* Synthetic memory
* Statistics
* Audit events
* Performance information

SPOT should avoid keeping historical information longer than necessary.

## Data Minimization

SPOT should only collect information necessary for its operation.

Synthetic personas should be generated from synthetic information rather than personal information belonging to the user.

## Local-First Operation

SPOT should operate locally by default.

Normal operation should not require a central SPOT account or cloud service.

Persona data, activity history, configuration, and analytics should remain local unless the user explicitly chooses otherwise.

## Telemetry

Telemetry should be disabled by default.

SPOT should not silently transmit:

* Persona information
* Activity history
* Browser information
* Network information
* Configuration
* Logs

If optional telemetry is ever implemented, it should be clearly documented and explicitly enabled by the user.

## Persona Separation

Each persona should maintain its own state.

This includes:

* Browser data
* Cookies
* History
* Synthetic memory
* Activity history
* Preferences
* Runtime state

One persona should not automatically learn information from another persona.

## Real Identity Separation

SPOT should not automatically use the user's:

* Real name
* Personal email
* Personal accounts
* Passwords
* Authentication tokens
* Personal browser profile
* Personal cookies
* Private messages
* Personal documents

The user should be warned when an operation could cross this boundary.

## Browser Privacy

Browser profiles should be dedicated to individual synthetic personas.

This helps keep cookies, history, local storage, cache, and session information separate.

The user's normal personal browser should remain separate from SPOT.

## Network Privacy

Network privacy depends heavily on configuration.

SPOT may support:

* Direct connections
* Proxies
* Tor
* Whonix

The selected network mode should be explicit.

For privacy-sensitive configurations, SPOT should be able to stop activity when the expected network path is unavailable.

## DNS Privacy

DNS requests should follow the configured network path.

Unexpected DNS fallback should be avoided.

## Location Privacy

Real physical location should not automatically become part of a synthetic persona.

When location information is required for a legitimate simulation or test, the persona should use synthetic location data unless the user explicitly chooses otherwise.

## Synthetic Memory

SPOT may maintain memory for each persona.

For example, a persona might remember its synthetic interests, previous synthetic activities, or preferences.

This memory should remain associated with the appropriate persona and should not automatically contain information about the real user.

## Analytics

SPOT can provide local analytics such as:

* Activity statistics
* Persona usage
* Scheduler statistics
* Network statistics
* Resource usage
* Consistency checks

Analytics should remain local by default.

## Audit Logs

Audit logs help users understand what SPOT has done.

Useful events include:

* Persona creation
* Persona startup
* Persona shutdown
* Activity startup
* Activity shutdown
* Network changes
* Safety-limit events
* Emergency stops
* Plugin changes
* Configuration changes

Logs should minimize sensitive information.

## Logging and Privacy

Logging creates a tradeoff between troubleshooting and privacy.

The recommended default is `info`.

Debug logging should normally be temporary because it may contain more operational information.

Sensitive values should be redacted.

## Data Retention

SPOT should avoid keeping data indefinitely.

Users should eventually be able to configure retention for:

* Activity history
* Audit logs
* Synthetic memory
* Runtime information

Shorter retention generally reduces the amount of information available if the system is later compromised.

## Encryption

Sensitive local data should be encrypted where appropriate.

Potential targets include:

* Persona memory
* Activity history
* Browser state
* Sensitive configuration
* Backups

Encryption protects stored information but does not protect information while it is actively being used.

## Backups

SPOT backups may contain persona information, activity history, browser state, configuration, and logs.

Backups should therefore be treated as sensitive.

Recommended practices include:

* Encrypting backups
* Keeping backups local when possible
* Using limited retention
* Avoiding unnecessary cloud synchronization
* Never storing real credentials in SPOT backups

## Plugins

Plugins can increase the amount of information available to SPOT.

Plugins should only receive the information and permissions necessary for their function.

For example, an activity plugin should not automatically have access to every persona's files.

## Qubes OS

Qubes OS can provide additional isolation between SPOT components.

A possible design could use:

* A controller qube
* Separate persona qubes
* Disposable qubes
* A Whonix-based network path

Correct Qubes configuration remains important. Using Qubes does not automatically make activity anonymous.

## Privacy Failure Modes

Privacy can be weakened when:

* Real credentials are imported
* Personal browser profiles are reused
* Personas share storage
* Network routing is misconfigured
* DNS bypasses the intended network
* Plugins receive excessive permissions
* Logs contain sensitive information
* Backups are exposed
* Accounts link synthetic activity
* Browser characteristics allow correlation

SPOT should make these risks visible where possible.

## Privacy vs. Realism

Synthetic activity can be internally consistent without using real personal information.

The preferred approach is:

**Realistic behavior + synthetic information + isolated execution**

rather than using real personal data to create a synthetic identity.

## Privacy vs. Anonymity

Privacy and anonymity are related but different.

Privacy concerns controlling access to information.

Anonymity concerns whether activity can be associated with a particular identity.

SPOT primarily focuses on:

* Isolation
* Data minimization
* Synthetic identity separation
* Local control

SPOT does not guarantee anonymity.

## User Control

The user should control:

* Which personas exist
* Which personas are active
* What information they contain
* Which activities are enabled
* Which network mode is used
* How long information is retained
* Which plugins are installed
* Which plugin permissions are granted
* Whether optional telemetry is enabled
* When SPOT stops

SPOT should not silently make these decisions.

## Privacy Principles

SPOT follows these basic principles:

1. Collect less.
2. Store less.
3. Share less.
4. Isolate more.
5. Make boundaries explicit.
6. Prefer local processing.
7. Never require real credentials.
8. Minimize retention.
9. Fail safely.
10. Give the user control.

## Summary

The central privacy principle of SPOT is:

**Synthetic identities should be created without requiring the user to expose their real identity.**
