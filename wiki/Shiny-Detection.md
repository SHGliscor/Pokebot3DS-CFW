# Shiny Detection and Safety

Pokebot3DS-CFW uses **validated game RAM as shiny authority**. The screen is not the authority and the bot does not write to Pokémon data to determine or alter the result.

## Encounter decision

For an authoritative starter or wild encounter:

1. Reach the required RAM-confirmed state boundary.
2. Perform the bounded PK6 read(s).
3. Decrypt/parse the Pokémon structure.
4. Validate checksum, species and required identity/state fields.
5. Calculate shiny state from the data the game generated.
6. Apply keeper/block-list policy.
7. Continue only if the result is safely authorised.

```text
valid keeper shiny    → HOLD
valid blocked shiny   → policy may continue
valid non-shiny       → reset/escape may continue
invalid/unknown state → HOLD
```

## Why checksum validation matters

A memory address containing bytes is not automatically a valid Pokémon. The bot verifies the PK6 structure before trusting fields such as species, PID or shiny state. This prevents random/stale/incomplete memory from being treated as permission to reset.

## Shiny calculation

The shiny decision is derived from the Gen 6 Pokémon identity data, including the Pokémon PID and the trainer identity required for the standard Gen 6 shiny calculation.

The important design rule is not the visual sparkle or sprite colour: **the RAM structure must validate first**.

## One encounter, one logical authority decision

The hunt engine is designed around bounded reads at meaningful game-state boundaries rather than continuous high-rate Pokémon polling. Movement and battle state may be checked as required for safety, but the Pokémon encounter decision itself remains a controlled logical read/validation step.

## Fail-closed behaviour

A safety HOLD is expected behaviour when the bot cannot prove that continuing is safe. Examples include:

- checksum failure
- wrong/unexpected species state
- missing battle authority
- RAM read failure
- controller failure
- unexpected map/terrain state
- movement leaving the proven envelope

A HOLD is preferable to accidentally resetting a keeper shiny.

## Block list

The block list is policy layered on top of the shiny calculation. RAM still decides whether the Pokémon is shiny; the block list only decides whether a particular validated shiny is a keeper that must stop the hunt.

## Auto Capture

The planned Auto Capture system will begin **after** RAM has already proved a keeper shiny. It will not replace shiny detection. If capture authority becomes uncertain, it will fall back to the existing shiny HOLD behaviour.