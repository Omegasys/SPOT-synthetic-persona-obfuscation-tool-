# SPOT Qubes Platform Plugin

The SPOT Qubes Platform Plugin provides controlled integration between SPOT and Qubes OS.

It is responsible for connecting SPOT's platform-independent security and networking model to Qubes-specific concepts such as:

* Qubes domains
* persistent AppVMs
* disposable qubes
* Qubes RPC
* Qubes networking
* Whonix-based networking
* persona-to-Qube assignments

## Purpose

The plugin provides:

* Qubes environment detection
* Qube assignment validation
* Persona-to-Qube mapping
* Disposable Qube support
* Persistent Qube support
* Qubes RPC policy validation
* Whonix network assignment validation
* Emergency-stop state handling
* Narrow service entry points
* Default-deny security policy

## Security Model

The Qubes plugin follows SPOT's isolation model.

The default policy is:

* deny by default
* no unrestricted dom0 access
* no arbitrary Qubes administration
* no arbitrary VM creation
* no arbitrary VM destruction
* no unrestricted file access
* no credential access
* no personal-data access
* no unrestricted device access
* no direct-network fallback when Whonix is required
* no DNS bypass
* no unrestricted RPC services

SPOT should only request the minimum Qubes operation required for the current task.

## Recommended Architecture

The recommended Qubes topology is:

```
SPOT Controller
      |
      v
Persona Qube
      |
      v
Whonix Workstation
      |
      v
   sys-whonix
      |
      v
      Tor
```

The exact Qube arrangement can vary, but SPOT should not bypass the configured network boundary.

## Persistent Persona Qubes

Persistent personas may use dedicated AppVMs.

Example:

```
persona-alex
    |
    +-- SPOT persona state
    +-- isolated browser
    +-- synthetic memory
    +-- synthetic activity state
    |
    v
sys-whonix
```

Persistent Qubes should not contain personal browser profiles, personal credentials, or unrelated user data.

## Disposable Persona Qubes

Disposable Qubes can be used when persistent state is unnecessary.

Example:

```
SPOT
  |
  v
disposable persona
  |
  v
Whonix
  |
  v
Tor
```

Disposable personas should not be used as a mechanism for preserving identity across sessions.

## Qubes RPC

SPOT uses explicit RPC services.

The included services are:

* `spot-controller`
* `spot-persona`
* `spot-network`

These services are intentionally narrow.

The plugin must not provide a generic interface such as:

```
execute arbitrary dom0 command
```

or:

```
execute arbitrary qvm command
```

Instead, requests should be represented as explicit operations.

## RPC Policy

The default policy is:

```
default deny
```

Only explicitly approved SPOT service operations should be accepted.

Examples of permitted logical operations include:

* status
* start
* stop
* emergency-stop
* network health
* persona lifecycle

The exact Qubes policy syntax can vary between Qubes releases. The policy files in the main SPOT repository therefore serve as controlled policy specifications rather than assumptions about every Qubes release.

## Network Policy

The Qubes plugin integrates with SPOT's network policy.

Recommended configuration:

* Whonix enabled
* direct networking disabled
* fail closed enabled
* DNS bypass disabled
* per-persona network assignment enabled

The plugin itself does not silently alter the network path.

## Emergency Stop

When SPOT enters emergency-stop state:

* new persona activity is denied
* new network activity is denied
* managed sessions are stopped
* the plugin reports a blocked state

Actual Qubes shutdown operations are delegated to the restricted platform integration.

## What This Plugin Does Not Do

This plugin does not:

* grant unrestricted dom0 access
* expose a shell in dom0
* execute arbitrary Qubes commands
* modify arbitrary Qubes policy files
* disable Qubes security controls
* access personal files
* import personal browser profiles
* retrieve passwords
* retrieve authentication tokens
* bypass Whonix
* silently enable direct networking

## Configuration

Start with:

```
config.example.yaml
```

The configuration intentionally uses conservative defaults.

## Testing

The tests are designed to run without requiring a live Qubes dom0 environment.

They test:

* configuration
* Qube assignment
* persistent/disposable separation
* RPC policy
* default-deny behavior
* emergency stop
* network policy
* command validation

Live Qubes integration tests should be kept separate from these unit tests.
