# Horde Hunts

Pokebot3DS-CFW supports ORAS Horde encounters as a five-opponent RAM-authoritative battle type rather than treating a Horde as a normal single Pokémon encounter.

Current implemented Horde work includes:

- Natural Horde handling
- Sweet Scent-triggered Hordes
- **Honey-triggered Hordes**
- reading/validating all five opponent Pokémon
- keeper/shiny safety across all five slots
- automatic continuation only when the entire Horde is safe to leave
- a one-shot RAM-driven Horde auto-attack validator used to prove safe move selection/execution

## Five-slot authority

A Horde is not authorised to continue just because one opponent slot is non-shiny. The bot inspects the Horde as a group and checks all available opponent slots before allowing normal continuation.

```text
5 validated opponents
→ any keeper shiny = HOLD
→ all validated non-keepers = continuation allowed
→ missing/invalid/uncertain slot = HOLD
```

## Sweet Scent

Sweet Scent Hordes use the same five-slot authority but need additional field/menu re-arm handling after returning from battle.

## Honey

v0p43EG includes the current hardware-developed Honey path.

The fast Honey mode requires Honey to be the first active entry in the Bag's Items pocket. The worker verifies live Items-pocket RAM before use. Current handling includes the corrected Bag shortcut, guarded A1/A2 choreography, quantity/battle-state proof and one bounded A2 retry only when the first acknowledged use did not change Honey quantity or battle state.

The important rule remains that a firmware acknowledgement alone is not enough: the game-side RAM state must confirm that Honey was actually consumed / the Horde transition began.

## Horde Auto-Attack validator

The current v0p43EG validator is designed to prove the battle-control pieces needed for a future protected-shiny Horde reducer without risking a real shiny.

On the next proven **zero-shiny** Horde, it:

1. refreshes the live lead PK6;
2. reads all four move IDs and current PP;
3. evaluates bundled ORAS move metadata;
4. chooses one authorised single-target damaging move;
5. executes exactly one attack;
6. proves target/return/resolution state;
7. returns to the normal Horde escape path.

Unsafe spread/random/all-foe choices remain rejected for this protected-shiny policy.

v0p43EE hardware-proved the complete FIGHT → MOVE → TARGET → ATTACK → RESOLUTION chain through move slot 2. v0p43EG uses calibrated ORAS MOVE-screen centres for all four slots:

```text
slot 1: (74,69)
slot 2: (246,69)  — hardware-proven end-to-end
slot 3: (74,133)
slot 4: (246,133)
```

The validator now executes the live policy-selected slot instead of forcing slot 2.

A real shiny blocks all validator attack input before execution.

## Next milestone — protected shiny Horde reducer

The one-shot validator is not the final protected-shiny Horde battle loop. The remaining production path is:

```text
identify exact shiny slot by validated RAM identity
→ select only an authorised move
→ KO one validated non-shiny opponent
→ re-read/revalidate the Horde after the turn
→ repeat while target identity remains safe
→ when the shiny is the only opponent left
→ hand off to the shared Auto Capture backend
```

Any target/move/state ambiguity must fall back to a shiny HOLD rather than risk an attack on the keeper.
