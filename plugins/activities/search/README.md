# Search Activity Plugin

The Search Activity Plugin provides a provider-neutral implementation for synthetic search activity.

It is responsible for preparing bounded search requests while leaving network routing and provider-specific execution to other SPOT components.

## Purpose

The plugin can:

- Accept a synthetic search query.
- Validate the query.
- Associate the activity with a SPOT persona.
- Apply activity limits.
- Produce a bounded search request.
- Track basic local activity metadata.
- Respect SPOT safety policies.

The plugin does not:

- Create real user accounts.
- Store credentials.
- Import personal search history.
- Access personal browser profiles.
- Bypass authentication.
- Bypass CAPTCHAs.
- Perform unrestricted automated searching.
- Send bulk requests.
- Circumvent SPOT network controls.

## Network Handling

The plugin does not directly decide whether traffic should use:

- Direct networking.
- A proxy.
- Tor.
- Whonix.

Those decisions belong to SPOT's network layer.

The plugin should request network access through the SPOT plugin context and fail closed if the required capability is unavailable.

## Search Providers

This implementation is provider-neutral.

A future provider adapter may support a particular search engine, but provider-specific functionality should remain separate from the core search activity logic.

## Configuration

See:

    config.example.yaml

## Testing

Run:

    pytest plugins/activities/search/tests/

Tests should not make real external network requests.
