# Gen 2 / Pokémon Crystal VC

Initial target: **English Pokémon Crystal Version for Nintendo 3DS Virtual Console** (`0004000000172800`).

## Why this is viable

Three references line up cleanly:

- **PokeReader** provides the live Crystal GB-memory locations used for party Pokémon, wild Pokémon, generated eggs, Trainer ID and RNG-related state.
- **PKHeX** documents the Gen 2 `PK2` layout, including DVs, friendship, level, status and party stats.
- **pret/pokecrystal** provides named WRAM variables and game logic for Crystal.

The important 3DS VC discovery is that the official English Crystal emulator exposes the GB address space through a stable native mapping used by existing Crystal VC cheat codes:

```text
3DS process address = 0x08A23FAC + Game Boy address
```

This independently matches PokeReader/PKHeX data. For example:

```text
PokeReader party mon 1:       GB 0xDCDF
Mapped 3DS address:           0x08A31C8B
PK2 friendship offset:        +0x1B
Mapped friendship address:    0x08A31CA6
Known Crystal VC happiness cheat address: 0x08A31CA6
```

That exact match means the Pokebot read-only RAM bridge can read Crystal WRAM directly; we do **not** need to execute PokeReader's in-process `read_gb_mem()` function for these WRAM structures.

## First probe

`luma_pokebot_bridge/tools/test_crystal_vc_ram.py`

Reads:

- Trainer ID (`0xD47B`)
- party count (`0xDCD7`)
- six `0x30`-byte party structures starting at `0xDCDF`
- wild species/DVs (`0xD206`, `0xD20C`)
- generated egg species/DVs (`0xDF7B`, `0xDF90`)

For each PK2 it calculates:

- Attack DV
- Defense DV
- Speed DV
- Special DV
- HP DV
- shiny status

Party slots also expose level, HP and friendship as an additional mapping sanity check.

## Shiny rule

Gen 2 shiny status is DV-based. The probe checks for Speed/Defense/Special DV = 10 and Attack DV in the legal shiny set (2, 3, 6, 7, 10, 11, 14, 15).

## Hardware test

Use the boot.firm produced by the **Build Gen2 Crystal VC Probe** workflow, launch English Crystal VC, enable the Pokebot RAM bridge, then run:

```text
run_crystal_vc_ram_probe.bat
```

For a live view:

```text
python test_crystal_vc_ram.py <3DS-IP> --watch --raw
```

The first milestone is passed when party data is correct and entering a wild encounter causes the wild species/DVs to update correctly.

## Safety

The Crystal patch only adds the Crystal title ID to the existing supported-process list. It does not add a memory-write command. The bridge remains QUERY/READ-only with the existing `0x200` maximum read size.

## Next after hardware proof

1. Add battle/event-state gating so stale wild/egg buffers are never treated as fresh encounters.
2. Normalize PK2 into the common Pokebot Pokémon model.
3. Build a live Gen 2 party viewer.
4. Implement Crystal starter hunting as the first automated hunt.
5. Add wild/static/gift/egg hunt state machines.
6. Generate the Crystal world database from `pret/pokecrystal` data.
