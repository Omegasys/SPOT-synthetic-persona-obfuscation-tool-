# SPOT Qubes Policies

This directory contains the Qubes OS policy definitions and policy
documentation used by SPOT.

## Security model

SPOT uses Qubes OS primarily as an isolation mechanism.

The normal SPOT process should not have unrestricted access to `dom0`.
Qubes administration operations should therefore be exposed through
small, explicitly authorized RPC services.

The default policy is deny.

## Goals

The policy layer should provide:

- persona isolation
- disposable Qube support
- controlled network assignment
- Whonix integration
- emergency shutdown
- status reporting
- narrowly scoped RPC access

It should not provide:

- unrestricted `dom0` access
- arbitrary RPC forwarding
- arbitrary shell execution
- credential access
- unrestricted device attachment
- arbitrary filesystem access
- automatic policy modification

## RPC design

When SPOT needs an operation that requires Qubes privileges, prefer a
dedicated service.

For example:

`spot.CreateDisposable`

is preferable to granting SPOT unrestricted access to:

`admin.vm.Create`

The dedicated service can validate the complete request before
performing the privileged operation.

Validation should include:

- persona ID
- Qube name
- template
- network mode
- NetVM
- disposable status
- resource limits
- emergency-stop state

## Persona isolation

Each active persona should have its own Qubes isolation boundary.

A persona should not automatically share:

- browser profiles
- cookies
- local storage
- credentials
- filesystem state
- session history
- Qube identity
- network configuration

A persistent persona may use a persistent Qube.

A temporary activity may instead use a disposable Qube.

## Whonix

For privacy-sensitive configurations, SPOT should prefer:

`persona Qube -> sys-whonix -> sys-firewall -> Internet`

The exact Qubes/Whonix topology depends on the user's Qubes configuration.

SPOT should never assume that a Qube is anonymous merely because it
is running inside Qubes.

## Emergency stop

The SPOT emergency stop should:

1. Stop active SPOT sessions.
2. Stop managed disposable activity.
3. Disable managed network assignments.
4. Prevent new activity.
5. Prevent new disposable sessions.
6. Preserve enough local audit information to explain the shutdown.

The emergency stop must not require unrestricted `dom0` privileges.

## Policy changes

Do not grant broad Qubes administrative permissions simply to make a
feature convenient.

If a new feature requires privileged functionality:

1. Define the smallest required operation.
2. Create a dedicated RPC service.
3. Validate all parameters.
4. Reject `dom0` targets unless absolutely unavoidable.
5. Add an explicit policy entry.
6. Add tests for unauthorized requests.
7. Document the security implications.

## Important

`spot.policy` is a policy specification/template.

Qubes RPC policy syntax and available services can differ between Qubes
OS releases and local configurations. Review and adapt the policy for
the specific Qubes installation before enabling it.

SPOT should fail closed when its required Qubes policy is missing or
does not permit the requested operation.
