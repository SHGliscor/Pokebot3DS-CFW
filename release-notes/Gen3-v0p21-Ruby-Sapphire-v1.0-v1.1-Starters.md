# Gen 3 v0p21 — Ruby/Sapphire v1.0 + v1.1 Starters

This build adds English revision 00 / v1.0 support while preserving revision 01 / v1.1 support.

Supported:
- AXVE rev 00 — Pokémon Ruby v1.0
- AXVE rev 01 — Pokémon Ruby v1.1
- AXPE rev 00 — Pokémon Sapphire v1.0
- AXPE rev 01 — Pokémon Sapphire v1.1

Verified from pret/pokeruby symbol maps:
- The relevant RAM/RNG addresses are the same across all four profiles.
- rev 00 uses `CB2_ChooseStarter = 0x08109E80` and `Task_StarterChoose2 = 0x0810A178`.
- rev 01 uses `CB2_ChooseStarter = 0x08109EA0` and `Task_StarterChoose2 = 0x0810A198`.
- `gRngValue = 0x03004818`, `gPlayerParty = 0x03004360`, and `SeedRngWithRtc = 0x080003E4` are shared.

The v0p19 generation-aware RNG design remains unchanged in principle. The CIA now reads the ROM revision byte at `0x080000BC` and selects the correct starter callback locally.

GitHub Actions build run: 35004775997
