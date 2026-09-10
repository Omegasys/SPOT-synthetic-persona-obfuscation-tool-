# Logging

SPOT uses logging to help users understand what the system is doing, diagnose problems, and investigate unexpected behavior.

Logging should provide useful information without becoming a source of unnecessary privacy risk.

## Logging Goals

SPOT logging should make it possible to determine:

* What SPOT was doing
* Which persona was active
* Which activity was running
* When an event occurred
* Whether an operation succeeded
* Whether an operation failed
* Why an operation stopped

## Log Levels

SPOT can use several log levels:

* `DEBUG` — Detailed information for development
* `INFO` — Normal system activity
* `WARNING` — Something unexpected occurred
* `ERROR` — An operation failed
* `CRITICAL` — A serious problem requiring attention

Debug logging should normally be disabled.

## Privacy

Logs should collect as little sensitive information as practical.

SPOT should avoid recording:

* Real passwords
* Authentication tokens
* Private keys
* Personal browser data
* Real account credentials
* Unnecessary personal information

URLs and network information may also need to be minimized or redacted depending on the configuration.

## Persona Logging

Logs may identify a synthetic persona using its internal identifier.

For example:

`persona=morgan`

The logging system should avoid confusing synthetic persona information with real user information.

## Activity Logging

Activity logs can record events such as:

* Activity started
* Activity completed
* Activity failed
* Activity cancelled
* Activity blocked by a safety rule

The system should record enough information to understand what happened without storing unnecessary content.

## Security Events

Security-related events should receive special attention.

Examples include:

* Network boundary failure
* Unexpected permission request
* Isolation failure
* Plugin failure
* Emergency stop
* Invalid configuration
* Blocked unsafe activity

## Log Storage

Logs should normally remain local.

Users should be able to configure:

* Log location
* Log retention
* Maximum log size
* Log level
* Rotation
* Redaction

SPOT should not send logs to a remote service unless the user explicitly configures such a feature.

## Emergency Stop

Emergency-stop events should always be logged when possible.

This helps determine what SPOT was doing immediately before it was stopped.

## Development Mode

Developers may enable more detailed logging while troubleshooting.

Development logging should still avoid exposing secrets or unnecessary sensitive information.

## Principle

**Logs should explain what SPOT did without unnecessarily revealing sensitive information.**
