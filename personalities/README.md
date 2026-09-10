# SPOT Personalities

The `personalities/` directory contains reusable synthetic persona templates for SPOT.

A personality template provides a starting point for creating a synthetic persona. It does not represent a real person.

## Templates

The included templates are:

* `blank.yaml` — Minimal starting point
* `casual-user.yaml` — General everyday internet user
* `technology.yaml` — Technology-focused user
* `outdoors.yaml` — Outdoors and nature-focused user
* `creative.yaml` — Art and creative-media-focused user

## Creating a Persona

A template can be copied and modified to create a new persona.

For example, a user might start with the casual-user template and change its interests, routines, and activity preferences.

Personas should contain synthetic information only.

## Persona Information

A personality template can define:

* Name
* Interests
* Preferences
* Synthetic demographics
* Routines
* Activity preferences
* Browser preferences
* Synthetic memory
* Behavior characteristics

## Consistency

A persona should behave consistently with its configuration.

For example, a technology-focused persona should generally have a higher probability of selecting technology-related activities than an outdoors-focused persona.

Randomization can still be used to prevent every session from behaving identically.

## Isolation

Each created persona should have its own isolated state.

This includes:

* Browser profiles
* Cookies
* Local storage
* History
* Synthetic memory
* Activity history
* Runtime state

Personas should not share private state unless explicitly designed to do so.

## Synthetic Data

Names, interests, preferences, locations, demographics, and other attributes in these templates are fictional.

SPOT should not use real people's identities as persona templates.

## Extending Templates

Additional templates can be added to this directory.

Possible future templates include:

* Student
* Gamer
* Reader
* Music enthusiast
* Science enthusiast
* Traveler
* Food enthusiast
* General researcher

New templates should remain synthetic and should follow SPOT's safety and privacy model.
