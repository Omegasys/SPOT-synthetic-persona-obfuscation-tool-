# SPOT Qubes OS Integration

This directory contains the Qubes OS integration layer for SPOT.

The goal is to give each synthetic persona a strongly isolated execution
environment while keeping Qubes-specific privileges narrowly scoped.

## Directory Structure

- `templates/`
  - `spot-persona-template.xml`
  - `spot-disposable-template.xml`
- `services/`
  - `spot-controller`
  - `spot-persona`
  - `spot-network`
- `policies/`
  - `spot.policy`
  - `spot-firewall.policy`

## Architecture

A recommended deployment is:

dom0
  |
  | explicit Qubes policy
  v
SPOT controller qube
  |
  +-- persona qubes
  |
  +-- disposable persona qubes
  |
  +-- network policy
  |
  +-- Whonix integration
  |
  +-- safety controls

SPOT should not require unrestricted access to dom0.

The controller should communicate with other qubes only through explicit
Qubes RPC services.

## Persona Isolation

Each persistent synthetic persona should have its own qube when strong
isolation is required.

For example:

- `spot-persona-alex`
- `spot-persona-morgan`
- `spot-persona-jordan`

A persona qube should not be shared with a real personal identity.

Do not import:

- Personal browser profiles.
- Personal cookies.
- Personal credentials.
- Personal SSH keys.
- Personal GPG keys.
- Personal documents.
- Personal account sessions.
- Personal cloud-storage credentials.

## Disposable Personas

Disposable persona qubes are intended for short-lived activity.

They should:

- Start from a known template.
- Contain no persistent persona state.
- Contain no personal data.
- Be destroyed after use.
- Not receive credentials.
- Not become a fallback path around persistent persona isolation.

Persistent synthetic memory should never depend on a disposable qube
surviving.

## Network Architecture

Network access should be explicitly assigned.

Recommended modes include:

- Offline.
- Whonix.
- Explicitly approved proxy.
- Other SPOT-approved isolated network paths.

Direct networking should not be silently substituted when a configured
Whonix or proxy route is unavailable.

If the configured network boundary fails, SPOT should fail closed.

## Qubes RPC

SPOT RPC services should follow these principles:

- Default deny.
- Explicit service names.
- Explicit source qubes.
- Explicit target qubes.
- No unrestricted dom0 operations.
- No generic administrative RPC.
- No arbitrary command execution.
- No arbitrary file transfer.
- No credential access.
- No unrestricted VM management.

The service scripts should validate all received input.

## Controller

The controller is responsible for coordinating SPOT's high-level state.

It should not become a general-purpose Qubes administration daemon.

Controller responsibilities may include:

- Persona lifecycle requests.
- Activity scheduling.
- Safety state.
- Emergency-stop coordination.
- Status collection.
- Policy validation.

Privileged Qubes operations should remain in dedicated, narrowly scoped
integration code.

## Emergency Stop

Emergency stop has priority over normal activity.

When emergency stop becomes active:

1. No new persona activity should start.
2. No new browser sessions should start.
3. Scheduled activity should stop.
4. Activity workers should terminate.
5. Network activity should be blocked where supported.
6. Existing persona sessions should be stopped.
7. Disposable persona qubes should be stopped.
8. The state should remain stopped until explicitly reset.

Emergency stop should not automatically reset after reboot.

## Firewall Policy

The firewall policy should be treated as another safety boundary.

SPOT should not use the firewall to bypass Qubes or Whonix isolation.

The firewall should be used to enforce:

- Allowed destinations.
- Allowed protocols.
- Allowed ports.
- Network mode.
- Emergency-stop state.
- Optional domain/IP restrictions.

## Installation

The exact Qubes installation procedure depends on the Qubes release
and the chosen SPOT deployment.

Do not copy these files directly into dom0 and execute them without
reviewing the applicable Qubes documentation and policy syntax.

The recommended process is:

1. Create a dedicated SPOT controller qube.
2. Create the required persona templates.
3. Create persistent persona qubes from the approved template.
4. Create disposable persona qubes when needed.
5. Install only the required SPOT service endpoints.
6. Configure explicit Qubes RPC policies.
7. Configure network policies.
8. Test emergency stop.
9. Test failure and network-loss behavior.
10. Verify that no personal data crosses persona boundaries.

## Security Requirements

A production SPOT deployment should enforce:

- Dedicated service identities.
- Default-deny Qubes RPC.
- No unrestricted dom0 access.
- No unrestricted VM management.
- No unrestricted filesystem access.
- No credential access.
- No personal browser-profile import.
- No direct network fallback when fail-closed is configured.
- Persona separation.
- Disposable-state destruction.
- Resource limits.
- Activity limits.
- Bandwidth limits.
- Emergency stop.
- Local audit logging.

## Service Naming

The following RPC service names are used by the example policy:

- `org.spot.Controller`
- `org.spot.Persona`
- `org.spot.Network`

These names are intentionally SPOT-specific rather than using generic
administrative service names.

## Service Implementation

The service files in this directory are deliberately conservative.

They should not:

- Execute arbitrary shell commands received from a client.
- Accept arbitrary Qubes management commands.
- Accept arbitrary filesystem paths.
- Modify arbitrary firewall rules.
- Change arbitrary Qubes properties.
- Access credentials.
- Access personal data.

The actual Qubes integration backend should translate validated SPOT
operations into narrowly scoped Qubes operations.

## Testing

Before enabling a policy in production, verify:

- Unauthorized source qubes are denied.
- Unauthorized target qubes are denied.
- Unknown RPC arguments are rejected.
- Unknown operations are rejected.
- Emergency stop prevents new activity.
- Network loss does not cause direct-network fallback.
- Persona A cannot access Persona B's state.
- Disposable qubes do not retain persona state.
- SPOT cannot access personal credentials.
- SPOT cannot perform unrestricted dom0 administration.

## Failure Philosophy

Qubes integration should fail closed.

Examples:

- Missing RPC policy -> deny.
- Unknown persona -> deny.
- Unknown operation -> deny.
- Invalid request -> deny.
- Network policy unavailable -> deny.
- Emergency stop active -> deny.
- Required Whonix route unavailable -> deny.

A failure should never turn into unrestricted access.
