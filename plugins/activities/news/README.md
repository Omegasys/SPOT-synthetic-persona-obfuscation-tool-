# News Activity Plugin

The News Activity Plugin provides a provider-neutral interface for controlled synthetic news-reading activity.

It allows SPOT personas to express interests in news topics and prepare bounded news-reading activity without requiring the plugin itself to perform unrestricted network access.

## Purpose

The plugin can:

- Prepare synthetic news-reading requests.
- Associate activity with a SPOT persona.
- Select from synthetic topic preferences.
- Apply source and article limits.
- Apply session limits.
- Maintain bounded local activity state.
- Delegate network access to SPOT's network layer.

## Topics

News topics should be represented as broad synthetic interests rather than personal or sensitive information.

Examples:

- Technology
- Science
- Environment
- Transportation
- Space
- Business
- Arts
- Culture
- Sports
- General news

A persona's topic preferences should come from its synthetic persona configuration.

## Network Handling

The plugin does not independently select networking.

All network access must remain subject to SPOT's network policy.

This includes:

- Tor.
- Whonix.
- Approved proxies.
- Domain allowlists.
- Domain blocklists.
- DNS policies.
- Rate limits.
- Bandwidth limits.
- Emergency-stop state.

## Safety

The plugin must not be used for:

- Bulk content retrieval.
- Unrestricted web crawling.
- Scraping entire websites.
- Denial-of-service activity.
- Spam.
- Harassment.
- Circumvention of access controls.

The plugin is intended for bounded synthetic activity.

## Provider Support

The initial implementation is provider-neutral.

Provider-specific news adapters can be added later without changing the core activity interface.

## Configuration

See:

    config.example.yaml

## Testing

Run:

    pytest plugins/activities/news/tests/

Tests must not make external network requests.
