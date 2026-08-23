# Pokebot3DS-CFW Wiki

Pokebot3DS-CFW is a RAM-authoritative shiny-hunting automation project for **Pokémon Omega Ruby 1.4** and **Pokémon Alpha Sapphire 1.4** running on real Nintendo 3DS hardware.

The project combines a Windows Qt dashboard with **Pokebot-Luma**, a Luma3DS-derived firmware build that provides a read-only RAM bridge and an acknowledged controller path. Shiny decisions come from validated Gen 6 Pokémon data in RAM rather than OCR, image matching or RAM writes.

## Current ORAS status

The current development estimate is **75% complete**.

Major systems already implemented or hardware-proven include:

- Treecko, Torchic and Mudkip starter automation, including Random mode
- read-only RAM authority and PK6 checksum validation
- acknowledged controller input, retained HID latch, native touch pulse and explicit release
- normal Wild Walk/Run hunting with terrain containment and automatic escape
- Natural Horde and Sweet Scent Horde handling
- Cave Walk, Cave Run and Cave Acro Bunny
- Surf/Ocean development path
- whole-game ORAS encounter/terrain database and HUNTS browser
- persistent stats/history, Discord integration, block-list handling and support ZIP export

The main known UI issue is live Party Pokémon ordering: valid party data can be read, but manual in-game party reordering may not immediately update the dashboard until ORAS is restarted. This is isolated from shiny authority.

## Documentation

- [Getting Started](Getting-Started.md)
- [Pokebot-Luma](Pokebot-Luma.md)
- [ORAS code.ips](Code-IPS.md)
- [Dashboard Guide](Dashboard-Guide.md)
- [Shiny Detection and Safety](Shiny-Detection.md)
- [Starter Hunts](Starter-Hunts.md)
- [Wild Hunts](Wild-Hunts.md)
- [Cave Hunts](Cave-Hunts.md)
- [Horde Hunts](Horde-Hunts.md)
- [Surf and Ocean Hunts](Surf-Ocean-Hunts.md)
- [Encounter Database](Encounter-Database.md)
- [Stats and History](Stats-History.md)
- [Discord](Discord.md)
- [Troubleshooting](Troubleshooting.md)
- [Known Issues](Known-Issues.md)
- [Roadmap](Roadmap.md)
- [Technical Reference](Technical-Reference.md)
- [Development History](Development-History.md)

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