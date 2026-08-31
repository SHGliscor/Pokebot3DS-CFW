# Known Issues

This page tracks problems that remain open in the current **v0p43EG** baseline.

## Idle Party Viewer

**Status:** open; full rewrite planned.

The dashboard can decode valid party Pokémon data, but manual in-game party changes while Pokebot3DS-CFW is idle can leave stale slot/order information visible until another hunt/state refresh occurs.

Incremental fixes have not solved this reliably, so the current direction is to rewrite the Party Viewer around live/stable PK6 sampling rather than continue patching the old polling path.

This display problem is isolated from validated shiny authority used by hunt workers.

## Partially-written party PK6

**Status:** understood; relevant to newly-created/captured party Pokémon.

Hardware fossil testing proved that a party slot can be sampled while ORAS is still committing a new Pokémon. A transient read can occasionally look structurally/checksum valid while identity fields are not yet authoritative.

Gift/fossil authority therefore uses stable/context-valid PK6 handling rather than trusting an arbitrary first changed read. This finding is also relevant to the Party Viewer rewrite and capture/gift lifecycle readers.

## Horde protected-shiny reducer

**Status:** current active development.

v0p43EG contains the RAM-driven one-shot Horde auto-attack validator. The move policy reads all four lead move slots and v0p43EG has calibrated MOVE-screen centres for slots 1–4. Slot 2's full attack chain is hardware-proven end-to-end.

What is **not yet production-complete** is the full real-shiny reducer that repeatedly KOs only validated non-shiny Horde members, revalidates after each turn, and then hands the isolated shiny to Auto Capture.

A real shiny blocks the current non-shiny validator before attack input.

## Auto Capture lifecycle hardening

**Status:** implemented and usable, but wider edge-case soak testing remains.

Automatic Poké Ball throwing, Capture Ball Override, capture continuation and failed-capture retry logic are present, including Pokédex/nickname/Box transitions. More hardware soak testing is still useful across different encounter/capture outcomes.

## New 3DS hunt-specific consistency

The unified controller/bridge supports both Old and New 3DS hardware, but individual hunt methods can still expose timing/touch differences that require hardware-specific validation. Fixes should remain local to the affected method unless logs prove a shared transport problem.

## Fishing / other less-soaked methods

Fishing and some gift/static/capture paths have less hardware soak time than the starter core. Their presence in the build should not be interpreted as equal maturity across every edge case.

## Non-English languages

English is the current hardware-verified ORAS language. Other languages are not yet claimed as supported until separately tested.

## Still to finish

- full protected-shiny Horde reducer/capture handoff
- Party Viewer rewrite
- Sweet Scent any-slot improvements where required
- further grass/map-aware movement work
- final capture/Horde/Fishing hardening
- dashboard/Discord polish and reliability work
- Pokémon X/Y and later-game support

Already implemented in v0p43EG and therefore **not** open roadmap items: Capture Ball Override, Honey Horde triggering, adaptive 1–5 Fossil Batch handling, and four-slot Horde move-policy selection.

See [Roadmap](Roadmap.md) for current development order.
