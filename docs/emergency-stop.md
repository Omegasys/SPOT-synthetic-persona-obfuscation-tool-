# Emergency Stop

The emergency stop system immediately stops SPOT activity when the user needs everything to halt.

It is designed as a safety feature and should always be available.

## Purpose

The emergency stop can be used when:

* A persona is behaving unexpectedly
* A network connection is incorrect
* A browser session needs to be stopped
* A plugin behaves incorrectly
* Too many resources are being used
* A security problem is suspected
* The user simply wants SPOT to stop

The emergency stop should take priority over normal scheduling and activity execution.

## What It Stops

An emergency stop should attempt to stop:

* Active personas
* Running activities
* Browser sessions
* Scheduled activity
* Network activity
* Plugins
* Background workers
* Temporary sessions

The exact behavior depends on the isolation environment.

## Manual Emergency Stop

The primary command should be:

`spot emergency-stop`

SPOT should also provide a convenient method for triggering the emergency stop from the graphical and terminal interfaces.

## Network Safety

When possible, the emergency stop should also prevent new external network connections.

If SPOT is configured with a kill switch or firewall integration, the emergency stop may activate it.

SPOT should not silently switch to another network path after an emergency stop.

## Qubes Integration

When running under Qubes OS, the emergency stop should operate within the permissions granted to SPOT.

It should not require unrestricted access to dom0.

Depending on the configuration, SPOT may stop its own processes, request permitted qube actions, or isolate affected qubes.

## Recovery

After an emergency stop, SPOT should remain stopped until the user intentionally starts it again.

The system should not automatically resume scheduled activity.

The user can inspect the status and logs before restarting SPOT.

## Logging

The emergency stop should record:

* Time of activation
* Reason, if provided
* Personas that were active
* Activities that were running
* Network state
* Components that were successfully stopped
* Components that failed to stop

Sensitive information should not be unnecessarily recorded.

## Example

`spot emergency-stop`

Then:

`spot status`

The user can inspect the system before starting anything again.

## Principle

**When the user says stop, SPOT should stop.**
