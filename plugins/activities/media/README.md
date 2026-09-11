# Media Activity Plugin

The Media Activity Plugin provides a provider-neutral interface for controlled synthetic media activity.

It can prepare bounded activity involving:

- Video
- Audio
- Music
- Podcasts
- Images
- Streams

The plugin does not directly perform unrestricted network activity. Actual media retrieval or playback should be handled by an approved SPOT provider or browser backend.

## Purpose

The plugin can:

- Prepare synthetic media activity.
- Associate activity with a SPOT persona.
- Select an approved media type.
- Apply duration limits.
- Apply item limits.
- Apply bandwidth limits.
- Maintain bounded local activity state.
- Delegate network access to SPOT's network layer.

## Media Types

Supported media types:

- `video`
- `audio`
- `music`
- `podcast`
- `image`
- `stream`

## Safety

The plugin must respect:

- SPOT emergency-stop state.
- Persona isolation.
- Network policies.
- Domain allowlists.
- Domain blocklists.
- Rate limits.
- Bandwidth limits.
- Session limits.
- Activity limits.

The plugin must not:

- Upload personal files.
- Access personal media libraries.
- Access credentials.
- Import personal browser profiles.
- Perform unrestricted crawling.
- Generate bulk requests.
- Circumvent access controls.
- Bypass authentication or CAPTCHAs.
- Perform denial-of-service activity.

## Privacy

Media activity should be synthetic.

The plugin should not import:

- Personal watch history.
- Personal playlists.
- Personal subscriptions.
- Personal accounts.
- Personal media libraries.
- Personal credentials.

## Network Handling

The plugin does not choose its own network route.

Network routing is controlled by SPOT.

Supported routing may include:

- Tor.
- Whonix.
- Approved proxies.

Direct fallback should remain disabled when SPOT is configured for fail-closed operation.

## Configuration

See:

    config.example.yaml

## Testing

Run:

    pytest plugins/activities/media/tests/

Tests must not make external network requests.
