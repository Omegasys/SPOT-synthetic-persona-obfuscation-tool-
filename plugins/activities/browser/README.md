# Browser Activity Plugin

The Browser Activity Plugin provides a provider-neutral interface for controlled synthetic browsing activity.

It prepares bounded browser sessions and navigation requests while leaving browser isolation, networking, and actual browser execution to SPOT's core components or approved browser backends.

## Purpose

The plugin can:

- Create a synthetic browser session.
- Associate the session with a SPOT persona.
- Prepare bounded navigation requests.
- Restrict navigation to approved domains.
- Apply page and action limits.
- Track basic local session state.
- Request isolated browser execution through SPOT.

The plugin does not:

- Import personal browser profiles.
- Import personal cookies.
- Import passwords.
- Access credentials.
- Access personal browsing history.
- Disable browser isolation.
- Bypass authentication.
- Bypass CAPTCHAs.
- Circumvent security controls.
- Perform unrestricted automated browsing.
- Upload personal files.
- Send bulk requests.

## Isolation

Browser sessions should use a dedicated SPOT browser profile.

A browser session must not share:

- Cookies
- Local storage
- History
- Password stores
- Extensions
- Credentials
- Personal browser profiles

with a user's normal browser.

## Network Handling

The plugin does not independently select a network route.

Network decisions belong to SPOT's network layer.

The plugin must respect:

- SPOT network routing.
- Whonix routing.
- Tor routing.
- Proxy policies.
- Domain allowlists.
- Domain blocklists.
- DNS policies.
- Bandwidth limits.
- Rate limits.
- Emergency-stop state.

## Automation

Browser automation is intentionally bounded.

The plugin should enforce limits for:

- Pages.
- Actions.
- Session duration.
- Downloads.
- Uploads.
- Navigation targets.

Security-sensitive browser actions should remain disabled unless explicitly supported by a future, narrowly scoped capability.

## Configuration

See:

    config.example.yaml

## Testing

Run:

    pytest plugins/activities/browser/tests/

Tests must not launch a real browser or make external network requests.
