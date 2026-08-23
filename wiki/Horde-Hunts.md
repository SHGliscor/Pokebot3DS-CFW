# Horde Hunts

Pokebot3DS-CFW supports ORAS Horde encounters as a five-opponent RAM-authoritative battle type rather than treating a Horde as a normal single Pokémon encounter.

Current Alpha Sapphire development/hardware testing includes:

- Natural Horde handling
- Sweet Scent-triggered Hordes
- reading/validating all five opponent Pokémon
- keeper/shiny safety across all five slots
- automatic continuation only when the entire Horde is safe to leave

## Five-slot authority

A Horde is not authorised to continue just because one opponent slot is non-shiny. The bot inspects the Horde as a group and checks all available opponent slots before allowing normal continuation.

```text
5 validated opponents
→ any keeper shiny = HOLD
→ all validated non-keepers = continuation allowed
→ missing/invalid/uncertain slot = HOLD
```

## Sweet Scent re-arm

Sweet Scent Hordes need an additional field/menu transition after returning from battle.

Testing exposed a case where the next Sweet Scent sequence could begin too quickly after escape. The current flow explicitly waits for field authority, lets the game settle, verifies battle inactivity and confirms the same grid before opening the menu again.

## Natural Hordes

Natural Horde encounters use the same five-slot shiny authority but do not need the Sweet Scent menu trigger.

## Planned Horde Auto Capture

Horde Auto Capture requires its own safe front-end before the shared capture engine can be used.

Planned logic:

```text
identify exact shiny slot by validated RAM identity
→ protect that slot
→ KO only validated non-shiny opponents
→ revalidate after every turn
→ when shiny is the only opponent left
→ hand it to shared Auto Capture
```

Any target ambiguity should fall back to a shiny HOLD rather than risking an attack on the keeper.

## Omega Ruby

Alpha Sapphire Horde paths are hardware-tested. Omega Ruby-specific Natural/Sweet Scent parity remains part of the planned current-controller regression pass.