# Debian Patches

This directory contains Debian-specific patches applied using the Debian
Quilt packaging system.

Prefer keeping this directory empty.

A patch should only be added when:

- the change is required specifically for Debian packaging;
- the change cannot reasonably be made upstream;
- the patch does not weaken SPOT's security model;
- the patch does not disable isolation or fail-closed behavior;
- the patch is documented.

Do not use Debian patches to silently change SPOT's privacy or security
defaults.

When adding a patch, use a descriptive filename and document:

- why the patch is necessary;
- which Debian versions require it;
- whether it should eventually be sent upstream.
