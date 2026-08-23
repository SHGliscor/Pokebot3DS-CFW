# Discord

Discord integration is a monitoring/notification feature. It is deliberately separated from shiny authority and controller safety.

## Current integration

The project includes work for:

- bot-account based notifications
- hunt/status information for remote monitoring
- Discord Rich Presence
- shiny/event notification plumbing

## Safety boundary

Discord cannot decide that a Pokémon is shiny and cannot authorise a reset or escape.

```text
ORAS RAM/state machine → hunt authority
Discord                → presentation/notification only
```

If Discord is offline, disconnected or misconfigured, the hunt should not reinterpret the encounter result.

## Screenshots

The PC-side image/framebuffer reconstruction pipeline exists, but direct top-screen framebuffer transport is not yet complete in the current Pokebot-Luma bridge. Screenshot delivery remains presentation-only and is not required for RAM shiny detection.

## Planned improvements

Further event/media wiring can expand notifications as development continues, including the eventual Auto Capture result flow, without changing the underlying RAM safety model.