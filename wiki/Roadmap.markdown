# ORAS Roadmap

Pokebot3DS-CFW has moved well beyond the original starter-reset scope. The roadmap now uses implementation status rather than a single completion percentage, because different hunt families have very different levels of hardware proof.

## Working / usable

- read-only RAM bridge and acknowledged controller input
- PK6 decrypt/checksum/shiny authority
- Treecko, Torchic and Mudkip starter automation
- basic Wild shiny hunting
- target/filter framework
- basic automatic Poké Ball throwing
- Old 3DS support and largely unified New 3DS support

## Working but still being hardened

- Auto Capture and failed-capture retries
- Pokédex → nickname → Box continuation
- Horde hunting
- Fishing
- gift/static Pokémon handling
- New 3DS hunt-specific timing consistency
- Discord integration and dashboard polish

## Current focus — Fossil Batch Hunting

Target lifecycle:

```text
revive fossil
→ wait for stable new PK6
→ shiny = immediate HOLD
→ non-shiny = advance received-Pokémon text
→ decline nickname
→ continue to next fossil
→ after 5 confirmed non-shinies, reset
```

Current fossil implementation/research includes:

- mixed batches across all 11 ORAS-revivable fossil Pokémon
- stable PK6 authority requiring three consecutive matching reads
- rejection of transient/partially-written party data
- trainer/species/checksum validation before shiny authority
- hardware-proven post-revival choreography: `stable PK6 → A once → nickname prompt → B once`

The complete 5-fossil loop is not yet considered production-complete until it passes end-to-end hardware validation across repeated batches.

## Needs rewrite

### Idle Party Viewer

The current Party Viewer can display valid Pokémon data but does not reliably track manual party changes while idle. It is planned for a full rewrite around live/stable PK6 sampling rather than further incremental patches.

## Still to add

1. User-selectable Poké Ball override for relevant non-starter hunts; Best Ball remains the default.
2. RAM/PK6-driven move discovery and auto-battle using any valid attacking move.
3. Sweet Scent from any move slot.
4. Honey as an alternative Horde trigger.
5. Map/terrain-aware grass movement improvements.
6. Stronger RAM state mapping for Devon fossil selection.
7. Stronger RAM state mapping for fossil nickname readiness.
8. Further capture, Horde and Fishing soak testing, especially on New 3DS.
9. Dashboard and Discord reliability/polish work.

## Development priority

```text
finish Fossil Batch Hunting
→ replace conservative fossil timing with RAM states
→ rewrite Party Viewer
→ add Poké Ball override
→ add RAM-driven move selection / auto-battle
→ Sweet Scent any slot + Honey
→ harden capture / Horde / Fishing
→ freeze stable ORAS baseline
→ begin Pokémon X/Y support
```

## Later games

After ORAS reaches the desired production baseline, planned/researched targets include:

- Pokémon X/Y
- Ultra Sun / Ultra Moon
- Gen 2 VC Gold/Silver/Crystal
- Gen 4/5 research through 3DS DS-mode tooling
- possible separate CFW Switch RAM automation project
