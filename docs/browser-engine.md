# SPOT Browser Engine

The browser engine manages the browser environments used by SPOT personas.

Its primary purpose is to keep synthetic browser activity separated between personas and from the user's normal browser.

## Purpose

The browser engine manages:

* Browser profiles
* Browser sessions
* Cookies
* Local storage
* Cache
* History
* Browser configuration
* Browser startup and shutdown

## Dedicated Profiles

Each persona should have a dedicated browser profile.

For example:

* Persona A → Browser Profile A
* Persona B → Browser Profile B
* Persona C → Browser Profile C

Profiles should not be shared between personas.

## Real Browser Profiles

SPOT should not automatically use the user's personal browser profile.

Personal profiles may contain:

* Passwords
* Cookies
* Authentication sessions
* Personal history
* Extensions
* Private information

Using them could break the separation between the user and synthetic personas.

## Browser Sessions

A browser session represents an active browser environment for a persona.

Sessions should be associated with the correct persona and browser profile.

The browser engine should track:

* Session state
* Start time
* Stop time
* Associated persona
* Browser process
* Network configuration

## Cookies and Local Storage

Cookies and local storage should remain associated with the correct persona.

SPOT should not copy personal cookies into synthetic profiles.

## History and Cache

History and cache should remain isolated to the appropriate persona.

Depending on configuration, SPOT may use disposable browser sessions where persistent history is unnecessary.

## Browser Configuration

Different personas can have different browser settings.

Configuration may include:

* Language
* Preferences
* Extensions
* Homepage
* Storage behavior
* Session persistence

Only safe and supported browser options should be used.

## Extensions

Extensions should be treated as potentially trusted software rather than automatically trusted.

Only required extensions should be installed.

Extensions should not receive unnecessary access to other personas or sensitive files.

## Fingerprinting

Browser fingerprinting can be used by websites to distinguish clients.

SPOT may provide configuration intended to reduce unnecessary differences or reduce unwanted correlation.

However, SPOT cannot guarantee protection against browser fingerprinting.

## Network Integration

The browser engine should use the network configuration provided by SPOT's network engine.

It should not independently create unexpected network connections.

## Browser Isolation

Depending on the platform, SPOT may use:

* Separate browser profiles
* Separate processes
* Sandboxing
* Containers
* Linux namespaces
* Qubes qubes
* Disposable qubes

The strongest available isolation should be used when appropriate.

## Session Shutdown

When a persona stops, its browser session should also stop.

SPOT should verify that browser processes started by SPOT are no longer running when practical.

## Emergency Stop

The browser engine must respond to the emergency stop.

SPOT-controlled browser sessions should be terminated as part of the emergency shutdown process.

## Security

The browser engine should never automatically expose:

* Real passwords
* Authentication tokens
* Personal browser data
* Private files
* Other persona profiles

## Summary

The browser engine provides the isolated browser environment used by each synthetic persona.

Its main principle is:

**One persona should have its own browser state.**
