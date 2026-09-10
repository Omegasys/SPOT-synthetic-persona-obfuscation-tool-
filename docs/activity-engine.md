# SPOT Activity Engine

The activity engine is responsible for carrying out activities selected by the behavior engine.

It provides a common framework for different types of synthetic activity.

## Purpose

The activity engine manages:

* Activity selection
* Activity execution
* Activity timing
* Activity limits
* Activity results
* Activity logging
* Activity shutdown

## Activity Types

SPOT may support activities such as:

* Search
* Browsing
* News
* Media
* Research
* Shopping
* DNS

Additional activity types can be provided through plugins.

## Activity Lifecycle

An activity normally follows this process:

1. Selected
2. Validated
3. Started
4. Running
5. Completed or stopped
6. Recorded

An activity should never start if it violates the configured safety or network rules.

## Search Activities

Search activities can use topics associated with the persona's interests.

For example, a persona interested in Linux might perform searches related to:

* Linux distributions
* Open-source software
* Hardware
* Programming
* System administration

SPOT should not use searches to bypass authentication, access controls, or other security mechanisms.

## Browsing Activities

Browsing activities can visit configured or selected websites.

The browser engine is responsible for creating the appropriate browser session.

The activity engine is responsible for deciding when and why the browsing activity occurs.

## News and Media

News and media activities can be associated with persona interests.

For example, a creative persona might be more likely to interact with photography or art-related content.

## Research Activities

Research activities allow a persona to explore a topic over multiple related activities.

This can help create continuity between a persona's interests and its synthetic activity.

## Shopping Activities

Shopping-related activity should remain within safe and legitimate use.

SPOT should not automatically perform purchases, financial transactions, or other actions involving real money unless a future feature explicitly provides a safe and controlled testing environment.

## DNS Activities

DNS activity can be used for controlled synthetic network activity.

DNS operations should follow the configured network path.

## Timing

Activities can have variable timing based on:

* Persona behavior
* Scheduler settings
* Activity type
* Randomization
* Safety limits

Timing should never exceed configured limits.

## Activity Limits

The activity engine should respect limits such as:

* Maximum requests
* Maximum runtime
* Maximum bandwidth
* Maximum concurrent activities
* Maximum DNS requests

## Network Requirements

An activity should verify that the expected network configuration is available before starting.

For example, an activity configured to use a Tor-based network should not silently switch to a direct connection.

## Logging

Activities should generate useful local audit information.

Examples include:

* Activity started
* Activity completed
* Activity stopped
* Activity failed
* Safety limit reached

Sensitive information should be minimized or redacted.

## Emergency Stop

The activity engine must respond to the SPOT emergency stop.

When an emergency stop is activated, active SPOT-controlled activities should be terminated as quickly and safely as practical.

## Plugins

New activity types can be implemented as plugins.

Plugins should have limited permissions and should only access the information required for their activity.

## Safety Boundaries

SPOT activity should not be used for:

* Spam
* Denial-of-service activity
* Credential theft
* Authentication bypass
* Fraud
* Harassment
* Unsolicited bulk messaging
* Circumventing security controls

The activity engine should provide safety mechanisms that make accidental misuse less likely.

## Summary

The activity engine answers the question:

**"How should SPOT safely perform the activity selected for this persona?"**
