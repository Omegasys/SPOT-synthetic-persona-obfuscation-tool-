# SPOT Whonix Integration

SPOT can optionally use Whonix as a network environment for privacy-sensitive activity.

Whonix is especially useful when SPOT is running within Qubes OS.

## Purpose

Whonix can provide a Tor-based network path for SPOT activities.

The basic concept is:

**SPOT → Whonix → Tor → Internet**

SPOT should use the existing Whonix network architecture rather than attempting to bypass it.

## Requirements

A Whonix configuration should already be working before integrating it with SPOT.

The user should verify that:

* Whonix is installed correctly.
* Tor is working.
* The appropriate networking configuration is active.
* The SPOT environment can communicate with the required Whonix component.

## Qubes and Whonix

On Qubes OS, Whonix can provide a dedicated Tor-based networking environment.

A possible architecture is:

**SPOT Persona → Whonix Workstation → Whonix Gateway → Tor**

The exact configuration depends on the Qubes setup.

## Network Mode

SPOT can provide a Whonix network mode.

For example:

`network.mode: whonix`

The exact configuration may change between SPOT versions.

## Network Verification

Before starting privacy-sensitive activity, SPOT should verify that the expected network environment is available.

If the required environment is unavailable, SPOT should follow the configured failure policy.

## Fail-Closed Operation

A privacy-sensitive configuration can use fail-closed behavior.

For example:

**Whonix unavailable → Activity stops**

SPOT should not silently switch to:

**Whonix unavailable → Direct Internet**

unless the user has explicitly configured such behavior.

## DNS

DNS requests should remain within the expected network architecture.

SPOT should not intentionally bypass Whonix's networking design.

Unexpected DNS behavior should be treated as a network configuration problem.

## Browser Integration

A SPOT browser running through Whonix should remain isolated to its assigned persona.

Whonix provides a network boundary, while SPOT's browser and isolation systems provide additional application-level separation.

## Multiple Personas

Multiple personas can potentially use separate SPOT environments while sharing an appropriately configured Whonix networking layer.

The exact design should depend on the desired level of isolation.

## Network Health

SPOT should monitor the availability of the expected Whonix path.

Possible states include:

* Available
* Connecting
* Unavailable
* Failed

Activities should only run when their network requirements are satisfied.

## Limitations

Using Whonix does not guarantee complete anonymity.

Other factors can still affect privacy, including:

* Browser fingerprinting
* Account correlation
* Application behavior
* User mistakes
* Endpoint compromise
* Traffic analysis

SPOT should therefore treat Whonix as one layer of the overall privacy architecture.

## Security Considerations

SPOT should not:

* Bypass Whonix routing
* Disable Whonix security mechanisms
* Automatically fall back to an insecure network
* Require unnecessary privileged access

## Troubleshooting

If Whonix integration does not work:

1. Verify that Whonix itself works.
2. Verify the Qubes networking configuration if applicable.
3. Check the SPOT network configuration.
4. Run `spot status`.
5. Review the SPOT logs.
6. Verify that the expected network path is available.
7. Test again with a single persona.

## Summary

Whonix provides an optional Tor-based network layer for SPOT.

The intended architecture is:

**Persona → SPOT → Whonix → Tor**

Whonix strengthens the network architecture, but it should not be treated as a guarantee of anonymity.
