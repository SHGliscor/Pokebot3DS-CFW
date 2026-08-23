# Dashboard Guide

The desktop application separates hunting, browsing, analytics and diagnostics so the normal hunt workflow does not become overloaded with setup/debug controls.

```text
DASHBOARD = run the hunt
HUNTS     = choose what to hunt
STATS     = analyse history and results
TOOLS     = diagnose, test and inspect
SETTINGS  = configure the bot
```

## DASHBOARD

The Dashboard is the operational page. It shows the current game/hunt state and provides the controls needed to start and stop supported hunt methods.

The Party Pokémon panel is display-only. Its current live-order refresh issue does not participate in shiny authority or reset/escape permission.

## HUNTS

HUNTS is the ORAS encounter browser. Locations are separated by encounter environment/method rather than mixing every encounter into one list.

Supported browser categories include Grass, Tall Grass, Cave, Surf/Water, Ocean, Rock Smash, Old Rod, Good Rod, Super Rod, Horde and DexNav Exclusive.

Pokémon cards can show artwork, species, level range, encounter/gift information and persistent lifetime shiny totals.

## STATS

STATS is intentionally analytics/history focused rather than hunt configuration. Current data includes lifetime encounters/shinies, phase data, rate, hunt time, target/game/location/method, shiny-value and IV extrema, species/method/location histories, OR/AS/combined totals and chronological shiny history.

## TOOLS

TOOLS is for diagnostics and support. It contains or is designed around connection/game detection, controller testing, safe read-only RAM inspection, PK6 inspection, terrain/position/corridor inspection, encounter-table lookup, patch validation, support ZIP export and local application folders.

Unsupported authorities should be labelled **UNVERIFIED** rather than shown as successful.

## SETTINGS

SETTINGS stores configuration that should persist between runs. Hunt authority itself remains state-driven: a saved preference never overrides an invalid RAM/controller state.

## Support ZIPs

When a hunt produces a safety HOLD or another reproducible issue, export a support ZIP before restarting the game or closing the bot whenever possible. Runtime logs are often the evidence needed to distinguish a game-state problem from a controller, RAM, movement or UI issue.