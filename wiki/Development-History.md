# Development History

Pokebot3DS-CFW has evolved through several generations of ORAS automation. This page summarises the major architectural shifts rather than listing every internal build number.

## Image/OCR-era ORAS bot

Early ORAS development used capture-card/image authority for many hunt paths. Considerable choreography was proven during this period, including:

- Hoenn starters
- Spiritomb
- Kecleon
- Regirock
- Regice
- Registeel
- Heatran
- Reshiram
- Zekrom
- Terrakion
- Virizion
- early Wild/Horde/portal hunt work

This work remains valuable for controller/navigation choreography, but visual shiny authority is being replaced by RAM authority.

## RAM rebuild

The project was rebuilt around a stricter rule:

```text
one logical encounter decision
→ read validated game RAM
→ checksum/species/state proof
→ calculate shiny
→ continue only on authorised non-keeper result
```

This removed the need to visually validate every possible normal/shiny species presentation.

## Pokebot-Luma

RAM access was moved away from unstable debugger-style polling toward a dedicated Luma3DS-derived read-only bridge.

Hardware proof established:

- game identification
- bounded process-memory QUERY/READ
- real ORAS PK6 read/decrypt/checksum validation
- controller input on real hardware
- physical and injected control coexistence during the migration period

## Acknowledged controller

The newer controller protocol added acknowledgement, status, explicit release, native touch and retained HID latch.

A key finding was that a controller acknowledgement did not necessarily mean ORAS had observed a short reset chord long enough to reset. The starter reset path was therefore changed to a retained reset chord followed by explicit release and game/process-transition verification.

## Current starter state

Treecko, Torchic and Mudkip are current-controller proven and remain separate frozen modules. Treecko received a narrow early-battle timing improvement without moving the final RAM authority deadline.

Recent observed development timings are around 35.5 seconds for Torchic, 36.7 seconds for Mudkip and 37.3 seconds for Treecko.

## Current Wild/Horde/Cave state

The RAM-authoritative Wild engine grew into terrain-contained unlimited hunting with automatic escape. Horde handling added five-opponent authority and Sweet Scent re-arm. Cave hunting gained cave-specific stable-grid authority, longer locally-proven Cave Run movement and explicit post-battle re-arm for Cave Run/Acro Bunny.

## Current known UI work

The Party Pokémon panel can read valid identities/details but still needs the exact live runtime ordering source for immediate in-menu party reorder updates. This work is isolated from hunt authority.

## Current baseline direction

The current development strategy is to freeze proven Alpha Sapphire behaviour, complete the Omega Ruby parity pass for existing non-starter methods, then build the remaining ORAS hunt families: Fishing/Chain Fishing, RAM Static/Portal, postgame starters, DexNav, Rock Smash and shared Auto Capture.

The README and Wiki should preserve this history rather than rewriting the project as though the current architecture appeared fully formed.