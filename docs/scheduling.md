# SPOT Scheduling

The SPOT scheduler determines when personas and activities are allowed to run.

It works with the persona and behavior systems to create controlled activity schedules.

## Purpose

The scheduler manages:

* Start times
* Stop times
* Activity frequency
* Persona routines
* Randomized timing
* Concurrent personas
* Runtime limits

## Basic Configuration

Scheduling can be enabled in the main configuration.

For example:

`scheduler.enabled: true`

The scheduler should remain disabled until the user has verified the basic SPOT configuration.

## Persona Schedules

Each persona can have its own schedule.

For example:

* Morning activity
* Evening activity
* Weekend activity
* Occasional activity

Different personas do not need to have identical schedules.

## Time of Day

Schedules can use different periods of the day.

Examples include:

* Morning
* Afternoon
* Evening
* Night

The exact available options depend on the configuration.

## Days of the Week

Personas can have different schedules for different days.

For example, a persona may have more activity on weekends than weekdays.

## Randomized Timing

SPOT can introduce controlled variation into scheduled activity.

This can vary:

* Start time
* Activity duration
* Activity frequency
* Activity order

Randomization should remain within the limits configured by the user.

## Concurrency

The scheduler can limit how many personas run simultaneously.

For example:

`max_concurrent_personas: 3`

This helps control resource usage and prevents too many browser or network sessions from starting at once.

## Runtime Limits

A persona or activity can have a maximum runtime.

When the limit is reached, the scheduler should stop or postpone additional activity.

## Safety Limits

Scheduling must respect the SPOT safety system.

The scheduler should not start activity when:

* The persona is disabled.
* A safety limit has been reached.
* The network requirement is unavailable.
* The emergency stop is active.
* The configuration is invalid.

## Network Awareness

The scheduler can check whether the required network environment is available before starting an activity.

For example, a persona requiring a Whonix connection should wait until the required network path is available.

## Persona Routines

A persona can have a routine that influences scheduling.

For example, an outdoors persona may be more active during certain periods, while another persona may have a different synthetic routine.

Routines should be configurable rather than hard-coded.

## Manual Control

The user should always be able to override normal scheduling.

Useful commands include:

`spot start`

`spot stop`

`spot persona start Morgan`

`spot persona stop Morgan`

`spot emergency-stop`

## Scheduler State

The scheduler should track:

* Current state
* Active personas
* Pending activities
* Scheduled activities
* Runtime limits
* Safety limits

This information should be available through `spot status` where practical.

## Failure Handling

If the scheduler encounters an error, it should avoid starting unexpected activity.

A failed schedule should be logged locally and retried only according to the configured policy.

## Emergency Stop

The emergency stop takes priority over normal scheduling.

When activated, the scheduler should stop creating new activities and should not restart them automatically.

## Resource Management

Scheduling helps prevent excessive system usage by controlling how many activities run at the same time.

This is especially important when using:

* Multiple browser sessions
* Multiple personas
* Qubes qubes
* Disposable environments

## Summary

The scheduler answers the question:

**"When should a persona be allowed to perform an activity?"**

It should provide controlled variation while always respecting safety and network requirements.
