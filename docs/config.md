SPOT Configuration

SPOT uses configuration files to control application behavior.

The main configuration is normally stored at:

~/.config/spot/config.yaml

An example configuration is provided in:

config/spot.example.yaml

Basic Configuration

A simple configuration might look like:

spot:
  enabled: true
personas:
  directory: ~/.config/spot/personas
scheduler:
  enabled: true
network:
  mode: direct
safety:
  enabled: true
logging:
  level: info

Personas

Personas are stored separately from the main configuration.

Example:

name: Morgan
interests:
  primary:
    - photography
    - hiking
  secondary:
    - camping
    - books
behavior:
  activity_level: moderate
schedule:
  enabled: true

Personas should not contain real passwords, authentication tokens, cookies, or other real credentials.

Scheduling

The scheduler controls when personas can operate.

Example:

scheduler:
  enabled: true
  max_concurrent_personas: 3

Each persona can also have its own activity schedule.

Networking

SPOT supports different network configurations depending on the installation.

Example:

network:
  mode: direct

Possible modes may include:

direct
proxy
tor
whonix

Only use modes supported by the installed SPOT version.

Safety

Safety limits can restrict resource usage and automated activity.

Example:

safety:
  enabled: true
  max_concurrent_sessions: 3
  max_bandwidth_mb: 500
  emergency_stop: true

Logging

Logging can be configured independently.

logging:
  level: info
  audit: true

Avoid enabling verbose debugging permanently because logs may contain more operational information.

Configuration Validation

Before starting SPOT, validate the configuration:

spot config validate

A configuration error should prevent SPOT from starting rather than causing it to run with unknown settings.