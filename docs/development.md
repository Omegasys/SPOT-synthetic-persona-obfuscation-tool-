# Development

This document describes the basic development structure of SPOT.

SPOT is intended to be an open-source project that can be developed, reviewed, tested, and extended by the community.

## Development Goals

Development should prioritize:

* Security
* Privacy
* Isolation
* Reliability
* Simplicity
* Maintainability
* Transparency
* Reproducibility

New features should not weaken the core security model without a clear reason and documentation.

## Source Code

The main application code is located under:

`src/spot/`

Major components include:

* Core
* Personas
* Behavior
* Activities
* Browser
* Network
* Isolation
* Qubes integration
* Scheduler
* Safety
* Storage
* Analytics
* Audit
* Plugins
* User interfaces

Each component should have a clearly defined responsibility.

## Development Environment

Developers should be able to create a local development environment without modifying the user's normal SPOT installation.

Development dependencies should be separated from runtime dependencies where practical.

## Testing

SPOT should include automated tests for important functionality.

Tests should cover:

* Persona creation
* Persona isolation
* Configuration
* Activity selection
* Activity execution
* Browser management
* Network routing
* Scheduling
* Emergency stop
* Logging
* Plugin permissions
* Qubes integration
* Failure handling

Security-sensitive behavior should receive additional testing.

## Testing Safety

Tests should not unintentionally:

* Send large amounts of network traffic
* Contact unintended systems
* Use real credentials
* Modify personal browser profiles
* Access unrelated personal files
* Interact with real accounts

Network-dependent tests should use controlled environments whenever possible.

## Code Style

Code should favor:

* Clear names
* Small components
* Explicit behavior
* Minimal privileges
* Simple interfaces
* Useful error messages
* Consistent formatting

Complexity should have a reason.

## Pull Requests

Contributors should explain:

* What changed
* Why it changed
* What components are affected
* How it was tested
* Whether configuration changes are required
* Whether security or privacy behavior changed

Security-sensitive changes should receive additional review.

## Documentation

New functionality should include appropriate documentation.

This may include:

* User documentation
* Configuration documentation
* Security considerations
* API documentation
* Plugin documentation
* Examples
* Troubleshooting information

## Dependencies

Dependencies should be kept to a reasonable minimum.

New dependencies should be evaluated for:

* Security
* Maintenance
* License compatibility
* Privacy implications
* Supply-chain risk
* Project maturity

## Security Issues

Potential security vulnerabilities should be handled according to `SECURITY.md`.

Do not publicly disclose sensitive vulnerability details before an appropriate response process has been established.

## Releases

Releases should ideally include:

* Version information
* Changelog
* Source code
* Documentation
* Dependency information
* Security notes when applicable

Future development may also include signed releases, reproducible builds, and software bills of materials.

## Development Principle

**SPOT should be easy to understand, difficult to misuse accidentally, and straightforward to audit.**
