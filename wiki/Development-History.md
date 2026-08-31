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

This removed the need to visually classify every possible normal/shiny presentation.

## Pokebot-Luma / acknowledged controller

RAM access moved away from debugger-style polling toward a dedicated Luma3DS-derived read-only bridge. The controller path then gained acknowledgement, status, explicit release, native touch and retained HID latch.

Hardware proof established game identification, bounded process-memory reads, real ORAS PK6 decrypt/checksum validation and controller input on real hardware without game-RAM writes.

A key lesson was that a firmware acknowledgement proves the controller command executed, not necessarily that ORAS consumed the input in the intended UI state. Hunt workers therefore combine controller ACKs with RAM/state authority.

## Starter automation

Treecko, Torchic and Mudkip became the first mature RAM-authoritative hunt family. Their reset and starter-selection paths established the fail-closed pattern used throughout the project:

```text
shiny = HOLD
invalid/uncertain = HOLD
only validated non-shiny = continue/reset
```

## Wild hunting and Auto Capture

The Wild engine expanded into RAM-authoritative encounter handling and automated battle navigation. Automatic Poké Ball throwing then required reverse engineering of the Battle Bag and post-capture lifecycle.

Important mapped phases include capture/breakout handling plus Pokédex, nickname and Box continuation. Multi-ball retry and post-capture recovery are now substantially implemented, although wider soak testing is still required.

## Horde / Fishing / gift and static expansion

Horde hunting, Sweet Scent, Fishing and gift/static frameworks were added on top of the same RAM-authoritative foundation. These hunt families are at different hardware-validation levels and remain active hardening areas rather than being treated as equally mature.

## Fossil Batch Hunting

Fossil revival exposed two particularly important findings.

First, mixed fossil inventories mean the bot cannot assume that every revival produces one fixed species. The development path now covers all 11 ORAS-revivable fossil Pokémon.

Second, hardware replay proved that a newly-created party slot can be sampled while ORAS is still writing the PK6. A transient read may even appear checksum-valid while species/trainer/PID fields are not yet authoritative.

The fossil reader therefore moved toward stable identity authority:

```text
plausible new PK6
→ validate context/trainer/species/checksum
→ require same identity for 3 consecutive reads
→ only then calculate authoritative shiny state
```

Manual hardware tracing also established the correct post-revival dialogue sequence:

```text
stable PK6
→ A once to advance received-Pokémon text
→ nickname prompt
→ B once to decline nickname
```

Older approaches such as DOWN+A, immediate B after PK6 and repeated B clearing were disproved by hardware testing.

The current remaining fossil milestone is proving the complete five-revival loop through repeated 1→2→3→4→5→reset batches, then replacing conservative timing with stronger RAM-defined Devon/nickname states.

## Party Viewer lesson

The existing Idle Party Viewer has repeatedly shown stale party/order behaviour. Rather than continue patching it, the planned direction is a full rewrite using the newer live/stable PK6 principles discovered during gift/fossil work.

## Current baseline direction

Current priority is:

```text
finish Fossil Batch Hunting
→ RAM-define remaining fossil UI states
→ rewrite Party Viewer
→ add Poké Ball override
→ RAM-driven move selection / auto-battle
→ Sweet Scent any slot + Honey
→ harden capture / Horde / Fishing
→ freeze stable ORAS baseline
→ begin Pokémon X/Y support
```

The README and Wiki should preserve this history rather than presenting the current architecture as though it appeared fully formed.
