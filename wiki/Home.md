# Pokebot3DS-CFW Wiki

Pokebot3DS-CFW is a RAM-authoritative shiny-hunting automation project for **Pokémon Omega Ruby 1.4** and **Pokémon Alpha Sapphire 1.4** running on real Nintendo 3DS hardware.

The project combines a Windows Qt dashboard with **Pokebot-Luma**, a Luma3DS-derived firmware build that provides a read-only RAM bridge and an acknowledged controller path on UDP `4952`. Shiny decisions come from validated Gen 6 Pokémon data in RAM rather than OCR, image matching or RAM writes.

## Current baseline

The current production/development build is **v0p43EG — Horde Auto-Attack Calibrated Move Buttons**.

Major implemented systems include:

- Treecko, Torchic and Mudkip starter automation
- read-only RAM authority and PK6 checksum/shiny validation
- acknowledged controller input and soft-reset automation
- Wild shiny hunting
- target/filter framework
- automatic Poké Ball throwing and capture retry handling
- **Capture Ball Override**, with Best Ball as the default
- Pokédex → nickname → Box continuation
- adaptive mixed **Fossil Batch — Any 1–5 Fossils**
- Sweet Scent and **Honey** Horde triggering
- Horde five-opponent RAM authority
- current four-slot Horde move-policy / auto-attack validator
- Old 3DS support and largely unified New 3DS support

## Current development focus

v0p43EG advances the Horde protected-shiny battle path. It reads the live lead PK6, evaluates all four move slots using bundled ORAS move metadata, selects a safe single-target damaging move and executes exactly one attack in the non-shiny validation mode.

v0p43EE hardware-proved the full attack chain through move slot 2. v0p43EG uses calibrated ORAS MOVE-screen centres for all four slots and now follows the live policy-selected move. A real shiny blocks the validator before attack input.

The next step is turning that validated one-shot attack path into the full protected-shiny Horde reducer/capture lifecycle, with RAM revalidation after every turn.

## Fossil Batch status

The fossil state machine/exhaustion authority in the current build is inherited from the hardware-proven v0p43DR baseline. The adaptive profile revives and checks the supported Devon fossils actually available in the Bag, capped at five per reset. Mixed fossil species are supported and every revived PK6 is independently shiny-checked.

## Main known UI issue

The Idle Party Viewer is planned for a full rewrite. Valid party Pokémon can be decoded, but manual party changes while the bot is idle can leave stale slot/order data on the dashboard. This is isolated from hunt shiny authority.

## Documentation

- [Getting Started](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Getting-Started)
- [Pokebot-Luma](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Pokebot-Luma)
- [ORAS code.ips](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Code-IPS)
- [Dashboard Guide](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Dashboard-Guide)
- [Shiny Detection and Safety](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Shiny-Detection)
- [Starter Hunts](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Starter-Hunts)
- [Wild Hunts](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Wild-Hunts)
- [Cave Hunts](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Cave-Hunts)
- [Horde Hunts](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Horde-Hunts)
- [Fossil Hunts](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Fossil-Hunts)
- [Surf and Ocean Hunts](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Surf-Ocean-Hunts)
- [Encounter Database](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Encounter-Database)
- [Stats and History](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Stats-History)
- [Discord](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Discord)
- [Troubleshooting](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Troubleshooting)
- [Known Issues](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Known-Issues)
- [Roadmap](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Roadmap)
- [Technical Reference](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Technical-Reference)
- [Development History](https://github.com/SHGliscor/Pokebot3DS-CFW/wiki/Development-History)

## Core safety rule

```text
RAM proves the encounter
→ validate PK6/checksum/species/state
→ calculate shiny state
→ keeper shiny = HOLD
→ validated non-shiny/non-keeper = continue
→ uncertainty = HOLD
```

The RAM bridge intentionally provides no game-memory write command. The project observes the encounter the game generated and then uses normal controller/touch input to play the game.
