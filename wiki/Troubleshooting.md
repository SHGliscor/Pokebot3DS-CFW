# Troubleshooting

Pokebot3DS-CFW is designed to stop on uncertain authority. A safety HOLD is therefore evidence to inspect, not something to automatically bypass.

## Bridge does not connect

Check:

- the 3DS and PC are on the same network
- the configured 3DS IP is correct
- ORAS is running
- the Pokebot bridge/controller services are enabled in Rosalina
- the game is a supported ORAS 1.4 profile
- local firewall/network rules are not blocking the UDP service

Use the built-in controller/connection diagnostics before starting a hunt.

## Communication-error screen during remote input

Verify that the correct game-specific `code.ips` is installed under the matching ORAS title ID.

The patch exists specifically because early Route 101 starter automation needs remote input before the player has access to the PSS menu to disable PSS communication normally.

See [ORAS code.ips](Code-IPS.md).

## Starter reset does not occur

Current builds use retained HID reset authority rather than relying on a short pulse. If a reset fails:

- export a support ZIP
- check that the acknowledged controller responds
- confirm `RELEASE_ALL` is available
- confirm the game/process transition was observed

Do not compensate by repeatedly firing blind reset chords.

## Wild hunt safety HOLD

Common causes include:

- unexpected map/terrain state
- movement outside the proven envelope
- battle/field transition not yet settled
- invalid opponent PK6/checksum
- RAM/controller timeout

Export support before restarting when possible.

## Cave safety HOLD

Cave methods use stable logical-grid authority rather than relying solely on outdoor land-style tile-centre rules. If Cave Run reports that its proven corridor is blocked, move to a wider suitable cave section or choose another supported cave method rather than weakening the safety envelope.

## Horde does not re-arm Sweet Scent

The current implementation waits for post-battle field authority before opening the menu again. If it still fails, export support so the log can show whether battle state, grid authority or menu timing failed.

## Party Pokémon order is stale

This is a known display-only issue. Valid Pokémon data can populate the cards, but manually moving Pokémon in the ORAS party menu may leave the dashboard order stale until the game is restarted.

This does **not** affect starter/wild/Horde/Cave shiny authority.

## Exporting support

For reproducible bugs, use the support ZIP workflow and export **before closing/restarting ORAS** whenever practical. The most useful evidence is often lost when the game process restarts.

Include what hunt method was running, what you expected, what happened on the 3DS and whether you manually intervened.