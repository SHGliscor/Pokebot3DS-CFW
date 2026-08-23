# Encounter Database

The HUNTS browser is backed by ORAS encounter/terrain data so hunt selection can be organised by actual environment and method.

## Encounter categories

Depending on the location, the browser can expose:

- Grass
- Tall Grass
- Cave
- Surf / Water
- Ocean
- Rock Smash
- Old Rod
- Good Rod
- Super Rod
- Horde
- DexNav Exclusive

The three-slot encounter group sometimes labelled `Swarm` by editing/data tools is displayed as **DexNav Exclusive**, matching how those Pokémon are actually obtained in ORAS.

## Pokémon cards

Encounter cards can include:

- normal artwork
- shiny artwork
- species/name
- level range
- encounter or gift information
- persistent lifetime `Shinies Found`

The lifetime shiny total is species-based so the same Pokémon can carry its accumulated result across multiple locations/methods.

## Route 101 gift starters

Route 101 also includes Professor Birch's gift starter groups:

| Group | Pokémon | Unlock |
|---|---|---|
| Hoenn | Treecko, Torchic, Mudkip | Opening Route 101 event |
| Johto | Chikorita, Cyndaquil, Totodile | First Hall of Fame + meet Zinnia |
| Unova | Snivy, Tepig, Oshawott | Complete the Delta Episode |
| Sinnoh | Turtwig, Chimchar, Piplup | Enter the Hall of Fame a second time |

The browser containing an encounter does not automatically mean a production hunt controller exists for it. Hoenn starters are proven; postgame starter automation is still planned.

## Terrain authority

The same ORAS map/terrain work that powers the browser also supports movement containment. Wild hunts use RAM-derived position/zone/terrain information to avoid blindly walking out of the intended encounter area.

## Planned methods already represented in data

Fishing, Rock Smash and DexNav data can be browsed before their production automation is complete. This keeps the encounter database independent from the current hunt-controller implementation status.