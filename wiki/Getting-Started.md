# Getting Started

This guide covers the current real-hardware ORAS setup used by Pokebot3DS-CFW.

## Requirements

- Nintendo 3DS / New Nintendo 3DS capable of running Luma3DS-derived CFW
- Pokémon Omega Ruby 1.4 or Pokémon Alpha Sapphire 1.4
- English game version is the currently hardware-verified language
- Windows PC on the same local network as the 3DS
- Pokebot3DS-CFW desktop application
- Pokebot-Luma firmware build used by the current development package
- the matching ORAS `code.ips` patch for the game being used

## Game IDs

```text
Omega Ruby 1.4:    000400000011C400
Alpha Sapphire 1.4: 000400000011C500
```

The corresponding `code.ips` belongs under that title ID in the SD card's Luma titles directory.

## Basic setup

1. Back up the current SD card and existing `boot.firm`.
2. Install the Pokebot-Luma `boot.firm` provided for the supported build.
3. Install the correct `code.ips` for Omega Ruby or Alpha Sapphire.
4. Boot the 3DS and launch ORAS.
5. Open Rosalina and enable the Pokebot3DS bridge/controller services required by the current firmware build.
6. Start Pokebot3DS-CFW on Windows.
7. Enter or confirm the 3DS IP address.
8. Verify game detection before starting a hunt.

## Before the first automated hunt

Confirm that the dashboard identifies the correct game and that the bridge/controller diagnostics pass. If game detection, RAM authority or controller authority is uncertain, do not start a hunt.

## Current networking

Current acknowledged-controller development builds use **UDP 4952** for the Pokebot service carrying read-only RAM requests and acknowledged controller commands. Older v0p4 documentation described a split `4952` RAM / `4950` InputRedirection design; that remains part of project history but should not be confused with the current acknowledged-controller path.

## Safety expectations

Pokebot3DS-CFW is designed to fail closed. A bad checksum, unexpected species, invalid game state, RAM failure, controller failure or other uncertain authority should produce a **HOLD** rather than blindly reset or continue.

See [Shiny Detection and Safety](Shiny-Detection.md) for the full model and [Troubleshooting](Troubleshooting.md) if setup validation fails.