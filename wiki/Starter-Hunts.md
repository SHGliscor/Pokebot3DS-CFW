# Starter Hunts

Current production starter support covers the opening Route 101 Hoenn trio:

- Treecko
- Torchic
- Mudkip
- Random mode across the three proven starter modules

## Current authority model

The starter state machines navigate the reset/title/continue/selection sequence using normal controller input, then read the resulting starter Pokémon from RAM at the proven authority boundary.

```text
reset
→ reach Birch bag / starter selection
→ select configured starter
→ battle/presentation state
→ read and validate starter PK6
→ shiny = HOLD
→ non-shiny = authorise next reset
```

## Reset chord

The current acknowledged-controller path uses a retained HID latch for:

```text
L + R + START + SELECT
```

The chord is explicitly released and the bot verifies the game/process transition rather than assuming a controller acknowledgement means the reset occurred.

## Current observed timing

Development hardware has recently produced approximately:

```text
Torchic  ~35.5 s/reset
Mudkip   ~36.7 s/reset
Treecko  ~37.3 s/reset
```

These are observed development rates, not guaranteed performance on every network/3DS/PC setup.

Treecko received a narrow early-battle timing improvement while keeping the same final RAM authority deadline.

## Birch bag safety

A false HOLD was found where ORAS was already at the proven Birch bag position but the secondary coordinate copy temporarily returned exactly `[0.0, 0.0]`.

The current validator tolerates that state only when battle is inactive, the correct zone is present, the primary coordinate exactly matches the proven bag position and the secondary coordinate is either identical or explicitly all-zero. A non-zero conflicting secondary coordinate still fails closed.

## Random mode

Random mode selects one of the three proven starter modules for each reset. It does not replace the individual Treecko/Torchic/Mudkip choreography.

## Postgame starters

Johto, Unova and Sinnoh Route 101 gift starter groups are already represented in the encounter browser, but their production automation is still planned. They require their own state/reset proof before being treated as supported hunt flows.