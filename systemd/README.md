# SPOT systemd Integration

This directory contains optional systemd units for running SPOT as a
managed Linux service.

The units are:

- `spot.service` — normal SPOT runtime.
- `spot.timer` — scheduled SPOT activation.
- `spot-emergency.service` — persistent application-level emergency stop.

## Security Model

The systemd integration follows SPOT's least-privilege model.

The normal service:

- Runs as the dedicated `spot` user.
- Does not run as root.
- Does not receive arbitrary capabilities.
- Does not use shell commands through systemd.
- Uses a private temporary directory.
- Protects the host filesystem.
- Protects `/home` and other user data.
- Cannot directly manipulate kernel modules.
- Cannot directly manipulate kernel tunables.
- Cannot directly access physical devices.
- Cannot create arbitrary Linux namespaces.
- Has access only to SPOT's designated state, log, and runtime paths.

The service should not be granted unrestricted access to the host merely
because SPOT may integrate with Qubes OS, Whonix, Tor, containers, or
other isolation systems.

Privileged operations belong in narrowly scoped integration components
with their own explicit policies.

## Installation

Create the dedicated service account.

    sudo useradd \
        --system \
        --home /var/lib/spot \
        --create-home \
        --shell /usr/sbin/nologin \
        spot

Create the required directories.

    sudo install -d \
        -o spot \
        -g spot \
        -m 0700 \
        /var/lib/spot

    sudo install -d \
        -o spot \
        -g spot \
        -m 0700 \
        /var/log/spot

    sudo install -d \
        -o spot \
        -g spot \
        -m 0755 \
        /run/spot

Copy the units into the systemd unit directory.

    sudo install -m 0644 spot.service \
        /etc/systemd/system/spot.service

    sudo install -m 0644 spot.timer \
        /etc/systemd/system/spot.timer

    sudo install -m 0644 spot-emergency.service \
        /etc/systemd/system/spot-emergency.service

Reload systemd.

    sudo systemctl daemon-reload

## Starting SPOT

Start the normal service.

    sudo systemctl start spot.service

Check its status.

    systemctl status spot.service

Enable SPOT during normal system startup.

    sudo systemctl enable spot.service

## Scheduled Operation

The timer is optional.

Enable it with:

    sudo systemctl enable --now spot.timer

Check the timer:

    systemctl status spot.timer

List scheduled timers:

    systemctl list-timers spot.timer

The timer deliberately uses a bounded randomized delay rather than
requiring a perfectly fixed schedule.

SPOT's internal scheduler remains responsible for persona and activity
decisions. systemd should primarily provide process supervision and
coarse scheduling.

## Emergency Stop

The emergency-stop unit is separate from normal SPOT operation.

Activate it with:

    sudo systemctl start spot-emergency.service

SPOT should then remain in its emergency-stop state until explicitly
reset.

The application-level emergency-stop mechanism is responsible for
preventing new SPOT activity. Integration layers are responsible for
actually terminating browser sessions, activity workers, network
connections, or other managed resources.

## Resetting the Emergency Stop

Resetting an emergency stop should be an explicit administrative action.

For the current application implementation:

    sudo systemctl stop spot-emergency.service

Then reset SPOT's application state:

    sudo -u spot /usr/bin/python3 -m spot reset-emergency-stop

Do not automatically reset emergency-stop state after a crash or reboot.

## Stopping SPOT

Stop normal operation:

    sudo systemctl stop spot.service

Disable automatic startup:

    sudo systemctl disable spot.service

Disable the scheduler:

    sudo systemctl disable --now spot.timer

## Viewing Logs

View service logs:

    journalctl -u spot.service

Follow logs:

    journalctl -u spot.service -f

View emergency-stop logs:

    journalctl -u spot-emergency.service

SPOT's application logging configuration may additionally write to the
`/var/log/spot/` directory.

Logging should remain local by default.

## Qubes OS

These units are intended primarily for a Linux environment where SPOT
runs as a normal service.

On Qubes OS, systemd inside a dedicated SPOT qube may be appropriate,
but this does not replace Qubes isolation or Qubes RPC policy.

Do not give the SPOT qube unrestricted `dom0` access.

Qubes-specific operations should go through the SPOT Qubes integration
layer and explicit Qubes policies.

A recommended architecture is:

dom0
  |
  | narrowly scoped Qubes policy
  v
SPOT qube
  |
  +-- SPOT service
  |
  +-- persona isolation
  |
  +-- browser isolation
  |
  +-- activity engine
  |
  +-- network policy
  |
  +-- Whonix/Tor integration
  |
  +-- safety system

The exact Qubes deployment should be documented separately in
`docs/qubes-integration.md`.

## Whonix

When SPOT is configured to use Whonix, systemd should not attempt to
replace the Whonix routing architecture.

The SPOT application should verify its configured network boundary
before allowing network activity.

If the configured network policy requires Whonix and Whonix is
unavailable, SPOT should fail closed rather than silently falling back
to direct networking.

See `docs/whonix-integration.md`.

## Security Hardening

These units are intentionally conservative.

Before production deployment, administrators should verify the
systemd hardening options against the target distribution and SPOT's
actual runtime requirements.

Useful checks include:

    systemd-analyze verify /etc/systemd/system/spot.service

and:

    systemd-analyze security spot.service

Do not blindly weaken sandboxing to make an integration work.

If a capability is genuinely required, document:

1. Why it is required.
2. Which component requires it.
3. Why a less privileged alternative is insufficient.
4. What the capability permits.
5. How the capability is constrained.
6. How the capability is tested.

## Fail-Closed Behavior

The systemd layer must not be treated as SPOT's only safety mechanism.

SPOT's own safety layers remain authoritative:

- Emergency stop.
- Activity limits.
- Request limits.
- Bandwidth limits.
- Resource limits.
- Domain allowlists and blocklists.
- Network fail-closed policy.
- Persona isolation.
- Browser isolation.
- Plugin capability restrictions.
- Qubes RPC policy.

A failure of systemd supervision must not cause SPOT to bypass those
controls.

## Important Implementation Note

The command paths in these units assume that SPOT is installed so that
`/usr/bin/python3 -m spot` can import the SPOT package.

A packaging-specific installation may instead provide `/usr/bin/spot`.

In that case, `ExecStart` and `ExecStop` should use the packaged
executable.

Do not modify the units to run SPOT as root simply because the package
is not installed correctly.

## Timer Design

The timer provides only coarse scheduling.

SPOT's scheduler remains responsible for:

- Persona schedules.
- Activity timing.
- Bounded randomization.
- Concurrency limits.
- Session limits.
- Runtime limits.
- Emergency-stop state.
- Safety checks.

This separation prevents systemd from becoming part of the persona
behavior model.

## Emergency-Stop Design

`spot-emergency.service` intentionally does not directly manipulate
network interfaces, kill arbitrary processes, or modify firewall rules.

Those operations require platform-specific privileges and should be
implemented by narrowly scoped SPOT integration backends.

The emergency-stop state itself is handled by SPOT's safety layer.

This separation makes the emergency mechanism easier to audit and
reduces the amount of privileged code in the project.
