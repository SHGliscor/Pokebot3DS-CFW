# Known Issues

This page tracks problems that are known but intentionally isolated from already-proven hunt authority.

## Idle Party Viewer

**Status:** open; full rewrite planned.

The dashboard can decode valid party Pokémon data, but manual in-game party changes while Pokebot3DS-CFW is idle can leave stale slot/order information visible until another hunt/state refresh occurs.

Incremental fixes have not solved this reliably, so the current direction is to rewrite the Party Viewer around live/stable PK6 sampling rather than continue patching the old polling path.

This display problem is isolated from the validated shiny authority used by hunt workers.

## Partially-written party PK6 during gift/capture lifecycle

**Status:** understood; stabilisation being introduced where required.

Hardware fossil testing proved that a party slot can be sampled while ORAS is still committing the new Pokémon. A transient read can occasionally look structurally/checksum valid while identity fields are not yet authoritative.

For fossil gift authority, the current development path therefore requires a plausible candidate to remain identical across **three consecutive reads** before shiny authority is granted. Candidate identity is checked against the expected context, including trainer/species/checksum information where available.

This finding is also relevant to the planned Party Viewer rewrite and any other lifecycle that reads a newly-created/captured party Pokémon.

## Fossil Batch Hunting

**Status:** active development; not yet production-complete.

The current goal is a five-fossil batch:

```text
revive → stable PK6 → shiny check → A received text → nickname prompt → B decline → next fossil
```

Mixed fossil species and the post-revival A/B choreography are understood, but the complete 1→2→3→4→5→reset loop still needs repeated end-to-end hardware proof.

The Devon fossil-selection menu and fossil nickname readiness also still need stronger RAM-defined state authority so conservative timing can eventually be reduced.

## Auto Capture lifecycle hardening

**Status:** usable/development hardened, but edge cases remain.

Automatic Poké Ball throwing, capture continuation and failed-capture retry logic have been developed and hardware-tested, including Pokédex/nickname/Box transitions. Wider soak testing is still required before every capture path should be treated as fully production-frozen.

## New 3DS hunt-specific consistency

The unified controller/bridge supports both Old and New 3DS hardware, but individual hunt methods can still expose timing/touch differences that require hardware-specific validation. Fixes should remain local to the affected method unless logs prove a shared transport problem.

## Non-English languages

English is the current hardware-verified ORAS language. Other languages are not yet claimed as supported until separately tested.

## Not yet complete / still to add

These are roadmap items rather than regressions in already-proven starter authority:

- user-selectable Poké Ball override
- RAM/PK6-driven attacking-move selection
- Sweet Scent from any move slot
- Honey Horde support
- further grass/map-aware movement improvements
- full Party Viewer rewrite
- stronger Devon fossil-selection and nickname-state mapping
- final capture/Horde/Fishing hardening
- Pokémon X/Y and later-game support

See [Roadmap](Roadmap.md) for current development order.
