# ORAS Roadmap

This page reflects the current **v0p43EG** production/development baseline.

## Working / usable

- read-only RAM bridge and acknowledged controller input
- PK6 decrypt/checksum/shiny authority
- Treecko, Torchic and Mudkip starter automation
- Wild shiny hunting
- target/filter framework
- automatic Poké Ball throwing and capture retry path
- **Capture Ball Override** with Best Ball as the default
- Pokédex → nickname → Box continuation path
- adaptive mixed **Fossil Batch — Any 1–5 Fossils**
- Old 3DS support and largely unified New 3DS support

## Implemented / still being hardened

- Horde hunting
- Sweet Scent Horde trigger
- **Honey Horde trigger** with live RAM authority and guarded use/retry handling
- Fishing
- gift/static Pokémon handling
- New 3DS hunt-specific timing consistency
- Discord integration and dashboard polish
- capture lifecycle soak testing across more edge cases

## Fossil Batch

The fossil state machine is hardware-proven through the v0p43DR baseline retained by v0p43EG.

The current adaptive profile revives the supported Devon fossils actually available in the Bag, capped at five per reset:

```text
1 available fossil  → revive/check 1 → reset
2 available fossils → revive/check 2 → reset
3 available fossils → revive/check 3 → reset
4 available fossils → revive/check 4 → reset
5+ available fossils → revive/check 5 → reset
```

Mixed fossil species are supported. Every revived PK6 is independently validated and shiny-checked, and a shiny causes an immediate Safety HOLD before post-gift input.

## Current focus — Horde Auto-Attack

v0p43EG contains the current Horde auto-attack validator.

The validator:

- refreshes the live lead PK6;
- reads all four move IDs and current PP;
- evaluates bundled ORAS move metadata;
- rejects unsafe spread/random/all-foe choices for the protected-shiny use case;
- selects an authorised single-target damaging move;
- sends exactly one attack in the non-shiny validation mode;
- blocks all validator attack input if a real shiny is present.

v0p43EE hardware-proved the complete FIGHT → MOVE → TARGET → ATTACK → RESOLUTION chain through move slot 2. v0p43EG uses hardware-calibrated ORAS button centres for all four move slots and now executes the live policy-selected move rather than forcing slot 2.

The remaining milestone is to move from the one-shot non-shiny validator to the fully protected real-shiny Horde reducer/capture lifecycle, with revalidation after every turn.

## Needs rewrite

### Idle Party Viewer

The existing Party Viewer can decode valid party data but does not reliably track manual party changes while idle. The planned fix is a full rewrite around live/stable PK6 sampling rather than further incremental patches.

## Still to add / finish

1. Full protected-shiny Horde auto-battle reducer and handoff to capture.
2. Sweet Scent discovery/use from any move slot where the current hunt path still assumes a fixed setup.
3. Further grass/map-aware movement improvements.
4. Further capture/Horde/Fishing soak testing, especially on New 3DS.
5. Party Viewer rewrite.
6. Dashboard and Discord reliability/polish work.

## Development priority

```text
finish Horde protected-shiny auto-attack/capture path
→ rewrite Party Viewer
→ harden capture / Horde / Fishing
→ Sweet Scent any-slot improvements
→ UI / Discord cleanup
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
