# SPOT User Guide

SPOT (Synthetic Persona Obfuscation Tool) is a Linux application for creating and managing isolated synthetic personas and generating controlled synthetic activity.

The main goal is to keep synthetic activity separate from the user's real identity, personal browser data, and credentials.

## Getting Started

After installing SPOT, start by checking the configuration:

`spot config validate`

Create a persona:

`spot persona create`

Create a persona from a template:

`spot persona create --template technology`

List your personas:

`spot persona list`

Check SPOT's current status:

`spot status`

Start SPOT:

`spot start`

Stop SPOT:

`spot stop`

## Personas

A persona is a synthetic user profile.

A persona can have:

* A synthetic name
* Interests
* Preferences
* Demographic information
* Activity preferences
* A routine or schedule
* A dedicated browser profile
* Synthetic memory
* Behavioral characteristics

Personas should contain synthetic information only.

Do not add real passwords, authentication tokens, personal browser profiles, private documents, or other sensitive information.

## Persona Templates

Templates provide a starting point for creating personas.

Example templates include:

* `blank`
* `casual-user`
* `technology`
* `outdoors`
* `creative`

A template can be modified after the persona is created.

## Persona Isolation

SPOT keeps persona information separated.

Each persona should have its own:

* Browser profile
* Cookies
* Local storage
* History
* Synthetic memory
* Activity state
* Configuration

On Qubes OS, personas can optionally be placed in separate qubes for additional isolation.

## Scheduling

SPOT can run activities according to a schedule.

Scheduling can take into account:

* Time of day
* Day of the week
* Persona routines
* Activity probability
* Randomized timing
* Runtime limits
* Resource limits

Scheduling should avoid perfectly repetitive behavior while remaining within the safety limits configured by the user.

## Activities

SPOT can support different types of synthetic activity, including:

* Search
* Browsing
* News
* Media
* Research
* Shopping
* DNS activity

Activities should be selected according to the interests and preferences of the persona.

## Browser Profiles

Each persona should use a separate browser profile.

SPOT should not automatically use the user's normal browser profile.

Real cookies, saved passwords, authentication sessions, and other personal browser information should never be imported into synthetic personas.

## Network Modes

Depending on the installation, SPOT may support:

* Direct connections
* Proxies
* Tor
* Whonix

The network mode should always be explicitly configured.

If a privacy-sensitive network such as Tor is required, SPOT should be configured to stop rather than silently falling back to a direct connection.

## Qubes OS

Qubes OS can provide additional isolation for SPOT.

A possible setup could include:

* A SPOT controller qube
* Separate persona qubes
* Disposable qubes for temporary activity
* A Whonix-based network path

SPOT should use explicit Qubes policies and should not require unrestricted access to dom0.

## Safety Controls

Safety controls limit how much activity SPOT can generate.

Examples include:

* Maximum concurrent personas
* Maximum browser sessions
* Maximum requests
* Maximum bandwidth
* Maximum runtime
* CPU limits
* Memory limits

These controls should normally remain enabled.

## Emergency Stop

SPOT provides an emergency stop command:

`spot emergency-stop`

The emergency stop should stop active SPOT activity and prevent the scheduler from immediately restarting it.

## Monitoring

Useful commands include:

`spot status`

`spot persona list`

`spot report activity`

`spot report personas`

`spot report network`

These commands provide information about the current operation of SPOT.

## Logs

SPOT keeps local logs for troubleshooting and auditing.

The normal logging level should be `info`.

Debug logging should normally remain disabled because it can contain more operational information.

Sensitive information should be redacted from logs.

## Plugins

SPOT can support plugins for additional activities, network systems, platforms, and integrations.

Plugins should receive only the permissions they require.

A plugin should not automatically receive access to all personas, files, credentials, or Qubes resources.

## Recommended First Setup

For a new installation:

1. Install SPOT.
2. Validate the configuration.
3. Create one test persona.
4. Give it a dedicated browser profile.
5. Configure conservative safety limits.
6. Test the network configuration.
7. Test the emergency stop.
8. Review the logs.
9. Create additional personas.
10. Enable scheduling.

Starting with a small number of personas makes it easier to verify that isolation is working correctly.

## Important Limitations

SPOT does not guarantee:

* Anonymity
* Unlinkability
* Successful profile manipulation
* Protection against every tracking technique
* Protection against browser fingerprinting
* Protection against account correlation
* Protection against mistakes in configuration

SPOT is an isolation and synthetic-activity framework, not a guarantee of anonymity.
