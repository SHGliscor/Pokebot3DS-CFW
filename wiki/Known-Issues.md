# Known Issues

This page tracks problems that are known but intentionally isolated from already-proven hunt authority.

## Party Pokémon live order

**Status:** open, display-only.

The dashboard can read valid party Pokémon identity/data and populate the six cards, but an in-game manual party reorder may not immediately change the displayed slot order. In current testing, closing/reopening ORAS can cause the new order to appear.

Several stale/cached party copies have been identified in RAM. The remaining work is finding the exact live runtime order structure that ORAS updates immediately when the party menu changes.

This issue does not participate in:

- starter shiny authority
- Wild shiny authority
- Horde shiny authority
- Cave shiny authority
- reset permission
- automatic Run permission

## Omega Ruby parity sweep

Several non-starter hunt paths are already Alpha Sapphire hardware-tested but still need the planned current-controller Omega Ruby parity pass, particularly Horde, Cave and Surf/Ocean.

This is validation work rather than evidence that those systems are known broken on Omega Ruby.

## Direct framebuffer transport

The PC-side screenshot/image pipeline exists, but the current Pokebot-Luma bridge does not yet provide the complete direct framebuffer transport required for capture-free Discord screenshots.

This is presentation-only and does not affect shiny authority.

## Non-English languages

English is the current hardware-verified ORAS language. Other languages are not yet claimed as supported until separately tested.

## Not yet production-complete hunt families

The following are roadmap items rather than bugs in an already-supported method:

- Fishing / Chain Fishing
- Static / Portal production engine
- Johto / Unova / Sinnoh postgame starters
- DexNav
- Rock Smash
- Auto Capture

See [Roadmap](Roadmap.md) for development order.