# Surf and Ocean Hunts

Surf/Ocean hunting extends the RAM-authoritative Wild model to water encounter areas.

The core rule remains unchanged:

```text
movement/state authority decides whether the bot may move
PK6 authority decides whether the encounter is shiny
```

## Current implementation

The Surf/Ocean path has moved beyond encounter-table display and into real automation testing on Alpha Sapphire.

The engine uses:

- water/field state validation
- bounded movement appropriate to the current encounter area
- battle-state detection
- validated opponent PK6 authority
- automatic escape for validated non-keepers
- post-battle field authority before movement resumes

## Why water is handled separately

A water encounter route can have different movement boundaries and state transitions from normal grass. The bot therefore does not assume that a successful land movement rule is automatically valid while Surfing.

## Current status

Alpha Sapphire Surf/Ocean has been hardware-tested in development. Omega Ruby parity on the current acknowledged-controller path is still scheduled for the wider non-starter regression pass.

## Fishing is separate

Old Rod, Good Rod, Super Rod and Chain Fishing are separate production hunt families. Their encounter data is already present in the browser, but the Fishing controller/state machine is not yet production-complete.