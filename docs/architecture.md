SPOT Architecture

SPOT (Synthetic Persona Obfuscation Tool) is a modular Linux application for creating and managing isolated synthetic personas and their simulated digital activity.

Core Architecture

                         SPOT
                          |
                 ┌────────┴────────┐
                 |   Core Engine    |
                 └────────┬────────┘
                          |
        ┌─────────────────┼─────────────────┐
        |                 |                 |
        v                 v                 v
    Personas          Behavior          Scheduler
        |                 |                 |
        └─────────────────┼─────────────────┘
                          |
                          v
                    Activities
                          |
             ┌────────────┼────────────┐
             |            |            |
             v            v            v
          Browser       DNS         Network
             |            |            |
             └────────────┼────────────┘
                          |
                          v
                    Isolation Layer
                          |
                  ┌───────┴───────┐
                  |               |
                Linux           Qubes

Major Components

Core

Coordinates SPOT’s other components and manages application state.

Personas

Defines synthetic identities, interests, preferences, routines, and behavioral history.

Behavior

Determines what activity a persona should perform and helps maintain consistency between activities.

Activities

Provides individual activity generators such as browsing, searching, news, media, research, and DNS activity.

Browser

Maintains isolated browser profiles and browser sessions for individual personas.

Network

Controls network routing and optional integrations such as Tor, Whonix, proxies, and DNS services.

Isolation

Provides process, filesystem, sandbox, and other isolation mechanisms available on the host system.

Qubes

Provides optional Qubes OS integration, including per-persona qubes, disposable qubes, RPC policies, and network separation.

Scheduler

Determines when personas become active and allows multiple personas to operate concurrently.

Safety

Provides rate limits, bandwidth limits, domain controls, resource limits, anomaly detection, and emergency shutdown.

Analytics

Provides local statistics and reports about SPOT’s operation.

UI

Provides command-line and terminal interfaces for controlling SPOT.

Design Principles

SPOT follows these principles:

* Isolation by default
* Least privilege
* Local-first operation
* No real credentials
* No automatic use of real browser profiles
* Explicit network configuration
* Safe defaults
* Modular components
* Optional Qubes integration
* User-controlled persistence