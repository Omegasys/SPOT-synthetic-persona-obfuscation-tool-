# SPOT Isolation

Isolation is one of the main security principles of SPOT.

The goal is to keep the real user, individual personas, browsers, and network environments separated from one another.

## Purpose

SPOT can use several layers of isolation depending on the operating system and configuration.

These may include:

* Filesystem isolation
* Process isolation
* Browser isolation
* Network isolation
* Linux namespaces
* Sandboxing
* Containers
* Qubes OS qubes
* Disposable environments

## Persona Isolation

Each persona should have its own state.

This includes:

* Configuration
* Browser profile
* Cookies
* Local storage
* History
* Synthetic memory
* Activity history
* Runtime state

A persona should not automatically have access to another persona's information.

## Filesystem Isolation

Persona data should be stored in separate locations.

File permissions should prevent one persona from unnecessarily accessing another persona's files.

Sensitive data should be minimized and encrypted where appropriate.

## Process Isolation

SPOT-controlled processes should be associated with the correct persona.

A persona should not automatically be able to control processes belonging to another persona.

SPOT should cleanly terminate processes when a persona is stopped.

## Browser Isolation

Each persona should use a separate browser profile.

Browser state should not be shared between personas unless explicitly required.

Where appropriate, SPOT can use separate browser processes or disposable browser environments.

## Linux Isolation

On Linux, SPOT may use mechanisms such as:

* User permissions
* Linux namespaces
* Sandboxing
* Containers
* Separate processes

The exact isolation method depends on the installation and available system features.

## Qubes Isolation

Qubes OS provides stronger isolation by placing workloads into separate virtual machines.

SPOT can use separate qubes for personas when appropriate.

This provides a stronger boundary than simply using separate directories on the same Linux system.

## Disposable Environments

Disposable environments can be useful for temporary activity.

A disposable environment can be created for a task and destroyed afterward.

This reduces the amount of persistent state that remains after the activity finishes.

## Network Isolation

Network configuration should be associated with the appropriate persona or environment.

A persona using Tor should not unexpectedly use a direct connection.

Firewall rules and kill switches can provide additional protection.

## Isolation Levels

SPOT may eventually provide different isolation levels.

For example:

* Basic — separate files and browser profiles
* Sandboxed — additional process and filesystem restrictions
* Containerized — separate container environments
* Qubes — separate qubes
* Disposable — temporary environments

The strongest level is not always necessary.

## Emergency Stop

The isolation system should respond to the emergency stop.

SPOT-controlled processes and environments should be stopped as quickly and safely as practical.

## Isolation Limitations

Isolation does not protect against every threat.

A compromised operating system, hypervisor, kernel, browser, or hardware platform may weaken isolation.

Incorrect configuration can also reduce isolation.

## Design Principle

SPOT should follow this rule:

**If two components do not need to share something, they should not share it by default.**
