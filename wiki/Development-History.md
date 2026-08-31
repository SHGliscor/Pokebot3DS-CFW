# Development History

Pokebot3DS-CFW has evolved through several generations of ORAS automation. This page summarises the major architectural shifts rather than listing every internal build number.

## Image/OCR-era ORAS bot

Early ORAS development used capture-card/image authority for many hunt paths. Considerable choreography was proven during this period, including starters, static encounters, Wild/Horde work and portal hunts.

That work remains useful for controller/navigation choreography, but shiny authority has been rebuilt around game RAM.

## RAM rebuild

The project moved to a stricter rule:

```text
one logical encounter decision
→ read validated game RAM
→ checksum/species/state proof
→ calculate shiny
→ continue only on an authorised non-keeper result
```

## Pokebot-Luma / acknowledged controller

RAM access moved toward a dedicated Luma3DS-derived read-only bridge. The controller path gained acknowledgement, status, explicit release, native touch and retained HID latch.

A major lesson was that firmware acknowledgement proves that an injected input command executed; it does **not** prove ORAS consumed that input in the intended UI state. Production state machines therefore combine controller ACKs with RAM/game-state authority.

## Starter automation

Treecko, Torchic and Mudkip became the first mature RAM-authoritative hunt family and established the project's fail-closed safety model.

## Wild hunting and Auto Capture

The Wild engine expanded into RAM-authoritative encounter handling, movement/escape and automated Battle Bag control.

Capture development then added:

- repeated-ball handling after failed captures;
- Pokédex/nickname/Box continuation;
- Best Ball selection;
- **Capture Ball Override** for forcing an exact supported Ball instead of automatic scoring.

## Fossil Batch

Fossil revival exposed several important state-machine and PK6-authority lessons, including mixed fossil inventories and transient newly-written party data.

The fossil work progressed to the hardware-proven **v0p43DR** state machine/exhaustion baseline. Later builds retain that authority while making the batch adaptive:

```text
available supported fossils: 1–5
→ revive/check the actual available count, capped at five
→ mixed species allowed
→ every revived PK6 independently shiny-checked
→ shiny = immediate HOLD
→ all non-shiny + batch exhausted = reset
```

v0p43DS then corrected fossil statistics so real batch sizes, species and reset counts are stored rather than inferred from encounter totals.

## Honey Horde

The Horde trigger system expanded from Natural/Sweet Scent to **Honey**.

Hardware development established:

- Honey item RAM authority;
- the corrected bottom-screen Bag shortcut;
- the slot-1/preselected fast path;
- guarded A1/A2 use choreography;
- Honey quantity and battle-state proof;
- one bounded A2 retry when an acknowledged input produced no game-side change.

## Horde Auto-Attack — v0p43ED to v0p43EG

The next step toward safe shiny Horde capture was proving that the bot can select and execute a damaging move without relying on a fixed move slot.

v0p43ED added a one-shot **non-shiny Horde auto-attack validator**. It reads the live lead PK6, all four move IDs/current PP and bundled ORAS move metadata, then selects an authorised single-target damaging move.

v0p43EE isolated the execution chain to slot 2 and hardware-proved:

```text
FIGHT → MOVE → TARGET → ATTACK → RESOLUTION
```

v0p43EF captured the real ORAS MOVE screen on hardware. v0p43EG then calibrated all four move-button centres:

```text
slot 1 = (74,69)
slot 2 = (246,69)
slot 3 = (74,133)
slot 4 = (246,133)
```

The v0p43EG validator now executes the live policy-selected safe damaging move instead of forcing slot 2. Any real shiny blocks the validator before attack input.

The remaining step is the full protected-shiny Horde reducer: KO only validated non-shiny opponents, revalidate after every turn, then hand the isolated shiny to Auto Capture.

## Party Viewer lesson

The existing Idle Party Viewer has repeatedly shown stale party/order behaviour. Rather than continue patching it, the planned direction is a full rewrite using live/stable PK6 principles learned during gift/fossil development.

## Current baseline direction

Current priority from v0p43EG is:

```text
finish protected-shiny Horde reducer/capture handoff
→ rewrite Party Viewer
→ harden capture / Horde / Fishing
→ Sweet Scent any-slot improvements
→ UI / Discord cleanup
→ freeze stable ORAS baseline
→ begin Pokémon X/Y support
```

The README and Wiki preserve the development history while the repository landing page remains intentionally minimal.
