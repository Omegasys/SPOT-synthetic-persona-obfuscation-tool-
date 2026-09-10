# SPOT Behavior Engine

The behavior engine determines how a SPOT persona behaves.

It uses the persona's interests, preferences, routines, and current context to select appropriate activities.

## Purpose

The behavior engine is responsible for:

* Selecting activities
* Determining activity frequency
* Applying persona preferences
* Adding controlled variation
* Maintaining consistency
* Respecting safety limits

## Inputs

The behavior engine can use:

* Persona configuration
* Interests
* Preferences
* Routines
* Current time
* Current activity
* Previous synthetic activity
* Scheduler state
* Safety limits

It should not require the user's personal activity history.

## Activity Selection

The engine chooses activities based on the persona's characteristics.

For example, a technology-oriented persona may be more likely to select:

* Linux research
* Programming
* Hardware research
* Networking topics

An outdoors-oriented persona may be more likely to select:

* Hiking
* Camping
* Outdoor equipment
* Parks

## Probability

Activities can have different probabilities.

An important interest can have a higher probability than a secondary interest.

This allows personas to have different activity patterns without requiring completely fixed schedules.

## Randomization

SPOT can use controlled randomization to introduce natural variation.

Randomization may affect:

* Activity selection
* Start time
* Duration
* Frequency
* Order of activities

Randomization should remain within configured limits.

## Consistency

Randomization should not completely override the persona.

The behavior engine should maintain reasonable consistency between:

* Interests
* Preferences
* Activities
* Routines
* Synthetic memory

## Context

The behavior engine can consider context such as:

* Time of day
* Day of week
* Current schedule
* Previous activity
* Persona routine
* Network availability
* Safety limits

## Memory

The behavior engine can use synthetic persona memory to maintain continuity.

For example, a persona that recently developed an interest in photography may be more likely to perform related activities later.

Memory should remain synthetic and isolated to the appropriate persona.

## Scheduler Integration

The scheduler determines when the behavior engine can run.

The behavior engine determines what the persona should do.

This separation allows scheduling and behavior to remain independent.

## Safety Integration

The behavior engine must respect safety limits.

For example, it should stop selecting new activities when:

* The runtime limit is reached
* The bandwidth limit is reached
* The request limit is reached
* The persona is disabled
* The emergency stop is active

## Failure Handling

If the behavior engine cannot safely determine an activity, it should return an error or wait rather than performing an unexpected operation.

## Example Flow

The basic process is:

**Persona → Context → Activity Selection → Safety Check → Activity Engine**

Each stage should be able to reject an unsafe or invalid operation.

## Design Principles

The behavior engine should be:

* Predictable in structure
* Variable in execution
* Persona-specific
* Resource-aware
* Safety-aware
* Isolated
* Locally controlled

## Summary

The behavior engine answers the question:

**"Given this synthetic persona and its current context, what should it do next?"**
