# SPOT Personas

A persona is a synthetic user profile managed by SPOT.

Personas allow SPOT to maintain different sets of interests, preferences, routines, and activity patterns while keeping their state separated.

## Purpose

A SPOT persona can represent a fictional user with its own:

* Name
* Interests
* Preferences
* Demographic attributes
* Routines
* Activity preferences
* Browser profile
* Synthetic memory
* Behavioral characteristics

Personas should use synthetic information.

They should not contain real passwords, authentication tokens, private documents, or personal browser data.

## Creating a Persona

Create a basic persona with:

`spot persona create`

Create one from a template:

`spot persona create --template technology`

List personas:

`spot persona list`

View a persona:

`spot persona show Morgan`

## Persona Templates

SPOT can provide templates as starting points.

Example templates include:

* `blank`
* `casual-user`
* `technology`
* `outdoors`
* `creative`

Templates should be easy to customize.

## Interests

Interests help determine what activities a persona is likely to perform.

For example:

* Linux
* Photography
* Hiking
* Books
* Programming
* Cooking
* Music

Interests can have different levels of importance.

A persona might have primary interests and secondary interests.

## Preferences

Preferences describe how a persona behaves.

Examples include:

* Preferred activity types
* Preferred times of day
* Activity frequency
* Media preferences
* Research preferences
* Browsing preferences

Preferences should influence behavior without making activity completely predictable.

## Demographics

A persona can optionally contain synthetic demographic information.

This information should be fictional and should not be based on sensitive information about a real person unless explicitly required for a controlled test.

## Routines

Personas can have routines that influence scheduling.

Examples include:

* Morning activity
* Workday activity
* Evening browsing
* Weekend activity
* Occasional research

Routines should provide structure without requiring perfectly repetitive behavior.

## Synthetic Memory

A persona can maintain synthetic memory.

Memory might include:

* Previously selected interests
* Synthetic preferences
* Previous synthetic activities
* Changes in interests
* Long-term persona characteristics

Memory should remain isolated between personas.

## Persona Evolution

Personas can gradually change over time.

For example, a persona might develop a new synthetic interest based on its existing interests.

Changes should remain controlled by the configuration.

SPOT should not use the user's real activity history as an automatic source for persona evolution.

## Persona Isolation

Each persona should have separate:

* Browser state
* Cookies
* History
* Local storage
* Memory
* Activity history
* Runtime state

Personas should not automatically access one another's information.

## Persona Lifecycle

A persona can move through several states:

1. Created
2. Configured
3. Enabled
4. Started
5. Active
6. Stopped
7. Disabled
8. Deleted

The exact lifecycle may depend on the SPOT version.

## Managing Personas

Disable a persona:

`spot persona disable Morgan`

Start a persona:

`spot persona start Morgan`

Stop a persona:

`spot persona stop Morgan`

Delete a persona:

`spot persona delete Morgan`

Destructive operations should require confirmation when appropriate.

## Multiple Personas

SPOT can manage multiple personas at the same time.

For example:

* Morgan — technology
* Alex — outdoors
* Jordan — creative

Each persona should have its own state and activity configuration.

The number of concurrent personas should be limited by the safety configuration.

## Persona Consistency

A persona should generally behave consistently with its configured characteristics.

For example, a persona interested in photography should be more likely to perform photography-related activities than unrelated activities.

Consistency should not mean perfectly predictable behavior.

## Security Considerations

Personas should never automatically receive:

* Real credentials
* Personal browser data
* Private files
* Unrestricted filesystem access
* Access to other personas
* Unrestricted network permissions

Qubes users can optionally place personas in separate qubes for additional isolation.

## Summary

SPOT personas are synthetic identities designed to provide isolated and configurable activity patterns.

The basic principle is:

**One persona = one isolated synthetic state.**
