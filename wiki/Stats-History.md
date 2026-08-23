# Stats and History

The STATS area is intended for analytics and history rather than hunt selection or configuration.

## Current analytics coverage

The project tracks or is designed to present:

- lifetime encounters
- lifetime shinies
- current phase
- phase encounters
- total hunt time
- encounters per hour
- current target
- game, location and hunt method
- shiny-value extrema
- IV extrema
- per-species history
- method breakdowns
- location breakdowns
- Omega Ruby totals
- Alpha Sapphire totals
- combined ORAS totals
- chronological shiny history
- records such as fastest shiny and longest phase
- encounter/shiny/species/method graphs
- odds-cycle progress

## Phase vs lifetime

Phase counters represent the current hunt phase. Lifetime totals survive across phases and are intended to represent the longer-running project history.

## Persistent data

User-specific settings and stats are stored under the Pokebot3DS-CFW application data area on Windows, including `%APPDATA%\Pokebot-3DS\` for the current desktop design.

## Authority separation

Stats are observations of hunts that already happened. A stats value never authorises a reset, escape or shiny decision. Encounter authority still comes from the live RAM/state machine.

## Support and debugging

When investigating an issue, support ZIP/runtime logs should be treated as the debugging source rather than attempting to infer controller or RAM failures from the visible encounter total alone.