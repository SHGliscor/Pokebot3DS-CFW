# Fossil Hunts

Fossil Batch Hunting is the current active ORAS development focus.

## Goal

The intended production loop revives up to five fossils into empty party slots, checks every newly-created Pokémon directly from RAM, stops immediately on a shiny, and only resets after five confirmed non-shinies.

```text
revive fossil
→ wait for stable new PK6
→ validate trainer/species/checksum/context
→ shiny = immediate HOLD
→ non-shiny = A once to advance received-Pokémon text
→ nickname prompt
→ B once to decline nickname
→ next fossil
→ after 5 confirmed non-shinies, reset
```

## Supported fossil Pokémon

The current mixed-batch development path covers all 11 ORAS-revivable fossil Pokémon:

- Omanyte
- Kabuto
- Aerodactyl
- Lileep
- Anorith
- Cranidos
- Shieldon
- Tirtouga
- Archen
- Tyrunt
- Amaura

Mixed fossil inventories are important because the bot cannot safely assume that the next revival will always be one fixed species.

## Stable PK6 authority

Hardware testing showed that ORAS can expose a party slot while the game is still committing the newly-created Pokémon. A single read can therefore be transient, and a transient read can occasionally look structurally/checksum valid while identity fields are not yet authoritative.

The current fossil authority requires:

1. a new/changed party candidate in the expected gift context;
2. valid stored PK6 structure;
3. valid checksum;
4. expected trainer identity and supported fossil species/context;
5. the same Pokémon identity across **three consecutive reads**.

Only that stable candidate is allowed to become shiny authority.

## Hardware-proven post-revival input

Manual tracing established the important dialogue order after the fossil Pokémon is created:

```text
stable PK6
→ A once
→ nickname prompt
→ B once
```

The A advances the received-Pokémon dialogue. The single B then declines the nickname prompt.

The following earlier approaches were disproved in hardware testing and should not be reintroduced without new evidence:

- DOWN + A at the nickname question
- B immediately when the PK6 first appears
- multiple/four-B clearing sequences
- treating the coarse field flow value alone as nickname readiness

## Current status

The individual pieces are substantially mapped, but Fossil Batch Hunting is still **development / hardware-validation status**, not a production-frozen hunt method.

Still to prove or improve:

- complete fossil 1 → 2 → 3 → 4 → 5 progression
- reset only after five confirmed non-shinies
- repeated full-batch soak testing
- deterministic fossil-selection authority when multiple fossil item types are in the Bag
- stronger RAM-defined Devon menu states
- stronger RAM-defined nickname readiness so conservative timing can be reduced

## Safety

A stable shiny fossil must cause an absolute HOLD before post-revival dialogue input is sent. Transient/invalid party reads must not create false shiny authority, and uncertainty must fail closed rather than blindly advance or reset.

No game RAM writes are used.
