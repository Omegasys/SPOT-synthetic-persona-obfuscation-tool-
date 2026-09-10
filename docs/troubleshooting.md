# Troubleshooting

This document provides basic troubleshooting steps for SPOT.

## Check Status

Start by checking the overall SPOT status:

`spot status`

This should show information such as:

* SPOT status
* Active personas
* Running activities
* Scheduler status
* Network status
* Browser status
* Plugin status
* Recent errors

## SPOT Will Not Start

Check:

* Configuration files
* File permissions
* Required dependencies
* Available system resources
* Recent logs

Try:

`spot status`

and inspect the latest log messages.

## Persona Will Not Start

Check:

* Whether the persona is enabled
* Whether its configuration is valid
* Whether another instance is already running
* Whether the scheduler allows it to start
* Whether the required network is available
* Whether its isolation environment is working

## Browser Problems

If a browser session fails:

* Check that the browser is installed
* Check the persona's browser configuration
* Check available disk space
* Check the network configuration
* Check recent logs

Do not solve browser problems by importing a personal browser profile into SPOT.

## Network Problems

Check:

* Network mode
* Proxy configuration
* Tor availability
* Whonix connectivity
* DNS configuration
* Firewall or kill-switch state

SPOT should not silently fall back to a less private network mode when fail-closed behavior is enabled.

## Qubes Problems

Check:

* Required qubes exist
* Qubes networking is working
* Required RPC permissions are configured
* The relevant qube is running
* Whonix is functioning correctly

SPOT should not require unrestricted dom0 access simply to operate.

## Plugin Problems

If a plugin fails:

* Check whether the plugin is enabled
* Check its permissions
* Check its version
* Check the plugin logs
* Try disabling the plugin

A failed plugin should not normally prevent unrelated SPOT components from operating.

## Scheduler Problems

Check:

* Whether the scheduler is enabled
* Persona schedules
* Time and date settings
* Concurrency limits
* Resource limits
* Network availability

Remember that the emergency stop takes priority over scheduled activity.

## Configuration Problems

If SPOT reports an invalid configuration:

1. Read the error message.
2. Check the relevant configuration file.
3. Compare it with the documented configuration options.
4. Correct the invalid setting.
5. Run the status check again.

## Emergency Stop

If SPOT behaves unexpectedly, use:

`spot emergency-stop`

Do not continue troubleshooting while unwanted activity is still running.

## Resetting a Persona

If a persona becomes corrupted, it should be possible to stop it and rebuild its synthetic state without affecting other personas.

This should not require deleting unrelated personas.

## Getting Help

When reporting a problem, useful information includes:

* SPOT version
* Linux distribution
* Qubes version, if applicable
* Whonix version, if applicable
* Relevant configuration
* Error message
* Relevant logs
* Steps needed to reproduce the problem

Do not include passwords, private keys, tokens, or personal browser data in bug reports.

## Principle

**Troubleshooting should identify the problem without creating a new privacy or security problem.**
