# Wild Hunts

The normal Wild engine is the foundation for several ORAS encounter methods. It combines RAM-authoritative encounter decisions with terrain-aware movement and validated post-battle continuation.

## Core Wild loop

```text
prove starting field/terrain state
→ perform bounded movement
→ detect battle state
→ read/validate opponent PK6
→ shiny/keeper = HOLD
→ non-shiny = automatic Run
→ prove return to field
→ prove position/terrain again
→ resume movement
```

## Movement

Wild movement is constrained by RAM-derived position/terrain authority so the bot does not blindly drift out of the intended encounter area.

Development has included Walk/Run and Acro-style movement where the map/method permits it.

## Automatic Run

Validated non-shiny encounters use native touchscreen input to choose **Run**. The proven escape path commonly accepts Run after roughly 12–13 touch pulses. Because this is already quick and reliable, it is intentionally not shortened merely to improve timing.

The bot does not resume field movement immediately after a battle animation ends. It waits for post-escape field authority and confirms the expected terrain/position state first.

## Encounter authority

Wild shiny detection is based on the validated opponent PK6, not the battle sprite or sparkle animation.

## Unlimited mode

Normal Dashboard Wild hunting is unlimited. It continues until:

- the user stops it
- a keeper shiny is found
- a safety condition produces HOLD

Finite runs remain useful for regression/proof testing.

## Omega Ruby parity

Normal Wild has extensive prior proof, including Omega Ruby finite Wild validation. The current acknowledged-controller generation is being regression-tested across both ORAS profiles without redesigning the already-proven Wild state machine.