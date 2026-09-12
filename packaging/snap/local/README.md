# SPOT Snap Runtime

This directory contains files used to construct the SPOT Snap.

The wrapper initializes SPOT's per-user runtime directories and then
starts SPOT through the Python module entry point.

The wrapper does not:

- modify firewall rules
- modify routing tables
- access Qubes dom0
- execute arbitrary shell commands
- access credentials
- disable host security controls
- automatically enable direct network fallback

Those operations remain outside the Snap's normal privilege boundary.

The Snap should remain strictly confined.
