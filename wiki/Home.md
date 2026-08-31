# Pokebot3DS-CFW Wiki

Pokebot3DS-CFW is a RAM-authoritative shiny-hunting automation project for **Pokémon Omega Ruby 1.4** and **Pokémon Alpha Sapphire 1.4** running on real Nintendo 3DS hardware.

The project combines a Windows Qt dashboard with **Pokebot-Luma**, a Luma3DS-derived firmware build that provides a read-only RAM bridge and an acknowledged controller path on UDP `4952`. Shiny decisions come from validated Gen 6 Pokémon data in RAM rather than OCR, image matching or RAM writes.

## Current ORAS status

### Working / usable

- Treecko, Torchic and Mudkip starter automation
- read-only RAM authority and PK6 checksum/shiny validation
- acknowledged controller input and soft-reset automation
- basic Wild shiny hunting
- target/filter framework
- basic automatic Poké Ball throwing
- Old 3DS support and largely unified New 3DS support

### Working but still being hardened

- Auto Capture and failed-capture retries
- Pokédex, nickname and Box continuation after capture
- Horde hunting
- Fishing
- gift/static Pokémon handling
- New 3DS hunt-specific timing consistency
- Discord integration and dashboard polish

### Current focus — Fossil Batch Hunting

The current fossil work is building a safe five-revival loop:

```text
revive 5 fossils
→ check each stable PK6 from RAM
→ shiny = immediate HOLD
→ decline nickname on non-shiny
→ continue
→ reset only after 5 confirmed non-shinies
```

Mixed batches across all 11 ORAS-revivable fossil Pokémon are supported by the current development path. The new PK6 authority requires three consecutive matching reads so transient/partially-written party data is ignored. Hardware testing established the post-revival sequence `stable PK6 → A once → nickname prompt → B once`.

The complete five-fossil loop still needs final end-to-end hardware validation before it is considered production-complete.

### Main known UI issue

The Idle Party Viewer is planned for a full rewrite. Valid party Pokémon can be decoded, but manual party changes while the bot is idle can leave stale slot/order data on the dashboard. This is isolated from shiny authority.

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
