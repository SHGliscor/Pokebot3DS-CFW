# Cave Hunts

Cave hunting is handled separately from outdoor grass because ORAS cave movement and coordinate settling do not always behave like land tiles.

Current Alpha Sapphire development/hardware testing includes:

- Cave Walk
- Cave Run
- Cave Acro Bunny

Fiery Path has been used extensively for cave validation.

## Stable cave-grid authority

Early cave testing showed that requiring the same exact land-style `settled_tile_center` condition could false-HOLD before movement started.

Current cave authority uses the logical grid and repeated stability as the main position proof. Land-style exact tile-centre settling remains useful diagnostic information but is not the only authority.

## Cave Run

The first Cave Run implementation produced movement that was too short and could false-HOLD after returning from battle.

The newer path first proves a local corridor around the starting anchor. Once that envelope is proven, the longer Run action uses a `600 ms` B+direction hold and only accepts the result when the RAM endpoint remains inside the proven corridor.

The controller does not blindly retransmit movement if the result is uncertain.

## Post-battle re-arm

After escaping a cave encounter, the bot waits for the field to settle and re-establishes stable cave-grid authority before starting another movement action.

## Cave Acro Bunny

Cave Acro Bunny is a stationary retained-B method. The current implementation preserves the proven bunny input pattern but adds explicit initial and post-battle re-arm checks.

The re-arm requires the expected anchor/grid and battle inactivity before B is retained again.

## Safety

Cave shiny authority is still the validated opponent PK6. Cave-specific position logic only decides whether movement can safely continue; it cannot override a shiny HOLD.

## Omega Ruby

Alpha Sapphire cave behaviour is currently the main hardware-proven path. Omega Ruby-specific parity testing is the next validation step for the existing implementation.