# Fossil Hunts

Fossil Batch Hunting is implemented in the current v0p43EG baseline and inherits the **hardware-proven v0p43DR fossil state machine/exhaustion authority**.

## Adaptive batch size

The current profile is:

**Fossil Batch — Any 1–5 Fossils**

The worker starts with one lead Pokémon and empty party slots, reads the supported Devon fossils actually available in the Bag, and revives up to five per reset.

```text
1 available fossil  → revive/check 1 → reset
2 available fossils → revive/check 2 → reset
3 available fossils → revive/check 3 → reset
4 available fossils → revive/check 4 → reset
5+ available fossils → revive/check 5 → reset
```

Mixed fossil species are supported.

## Supported fossil Pokémon

The current mixed-batch path covers all 11 ORAS-revivable fossil Pokémon:

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

## PK6 and shiny authority

Every revived Pokémon is independently validated and shiny-checked from RAM. A shiny causes an immediate Safety HOLD before post-gift input.

The fossil work also established an important general RAM rule: a newly-created party slot can be observed while ORAS is still committing the PK6. The gift/fossil path therefore uses stable/context-valid party authority rather than trusting arbitrary transient party data.

## Post-revival dialogue

Hardware tracing established the important post-gift interaction order:

```text
validated revived PK6
→ advance received-Pokémon dialogue
→ decline nickname
→ continue batch
```

Earlier experimental approaches such as DOWN+A at the nickname question and repeated blind B clearing were rejected by hardware evidence and are not the intended production logic.

## Exhaustion / reset authority

The batch does not assume that five fossils must exist. It records the actual available batch size, revived species, batches and resets in statistics/history, then resets after that adaptive batch has been exhausted and every revived Pokémon has been confirmed non-shiny.

## Safety

- shiny fossil = immediate HOLD;
- invalid/uncertain authority = fail closed;
- every revived PK6 is checked independently;
- no game RAM writes are used.
