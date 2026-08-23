# ORAS Roadmap

Current ORAS development estimate: **75%**.

Percentages are development estimates rather than automated code coverage. Progress should move when a section gains real implementation, hardware proof, production integration or required game parity.

| ORAS section | Progress | Status |
|---|---:|---|
| CFW / RAM / input bridge | 100% | Hardware-proven read-only bridge + acknowledged controller |
| Hoenn starter automation | 100% | Treecko/Torchic/Mudkip + Random operational |
| Grass Wild automation | 100% | RAM-authoritative movement/encounter/escape core operational |
| Horde automation | 95% | AS proven; OR parity remains |
| Cave automation | 95% | AS proven; OR parity remains |
| Surf / Ocean automation | 90% | Implemented/development hardware-tested; OR parity remains |
| Encounter / terrain DB + browser | 100% | Whole-game ORAS data/browser live |
| Dashboard / HUNTS | 95% | Main workflow live; Party live-order issue remains |
| STATS / history | 90% | Persistent analytics/history implemented |
| TOOLS / support | 90% | Diagnostics and support ZIP workflow implemented |
| Discord / Rich Presence | 85% | Implemented; media/event polish remains |
| Direct 3DS screenshot pipeline | 50% | PC pipeline exists; direct firmware transport pending |
| Block list | 90% | Integrated; documentation/polish remains |
| Fishing | 20% | Data present; production controller remains |
| Static encounters | 30% | Previous choreography exists; RAM production engine remains |
| Postgame starters | 15% | Browser entries live; automation remains |
| Language validation | 15% | English proven; additional languages remain |
| Release / docs | 95% | README/wiki/release structure close to complete |

## Immediate validation

The next broad hardware pass is Omega Ruby parity across existing non-starter hunt methods:

- normal Wild Walk/Run
- Natural and Sweet Scent Hordes
- Cave Walk/Run/Acro Bunny
- Surf/Ocean

The objective is to validate the existing shared ORAS implementation, not redesign Alpha Sapphire-proven behaviour without evidence.

## Remaining hunt families

After OR/AS parity is frozen:

1. Fishing and Chain Fishing
2. Static encounters and Mirage Spot/portal legendaries
3. Johto / Unova / Sinnoh postgame starters
4. DexNav
5. Rock Smash
6. selected gift/fossil reset hunts
7. shared shiny Auto Capture

Previous image-era development already produced usable choreography for Spiritomb, Kecleon, Regirock, Regice, Registeel, Heatran, Reshiram, Zekrom, Terrakion and Virizion. The current goal is to reuse safe navigation choreography while replacing visual shiny authority with PK6 RAM authority.

## Auto Capture plan

Auto Capture will be a shared subsystem rather than a separate macro for every hunt method.

```text
RAM proves keeper shiny
→ normal hunt continuation disabled
→ lock target identity by species/PID/EC
→ capture only while identity/state remains valid
→ confirm catch
→ stop hunt
→ uncertainty = SHINY HOLD
```

Single-opponent capture comes first. Horde capture will add a protected-shiny-slot front-end before using the same shared capture backend.

## Later games

After ORAS reaches the desired production state, future project targets include Pokémon X/Y, Sun/Moon, Ultra Sun/Ultra Moon and Gen 2 VC Gold/Silver/Crystal integration.
