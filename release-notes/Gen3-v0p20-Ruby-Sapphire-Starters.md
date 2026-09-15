# Gen 3 v0p20 — Ruby + Sapphire v1.1 Starters

This build makes one functional expansion from the proven Ruby v0p19 starter path: English Pokémon Sapphire v1.1 starter support.

## Supported
- Ruby: AXVE revision 01
- Sapphire: AXPE revision 01
- Treecko / Torchic / Mudkip / Random
- Fast-forward
- Generation-aware starter RNG gate
- `STARTER_RECORD` feedback of the real decoded generation state

## Stability policy
The Ruby v0p19 generation-aware logic is preserved. Hardware testing reported 900+ Ruby resets with no duplicate PIDs before this Sapphire expansion.

## Sapphire symbol verification
The relevant Ruby/Sapphire rev1 starter and RNG symbols match, including:
- `gRngValue 0x03004818`
- `gMain 0x03001770`
- `gPlayerPartyCount 0x03004350`
- `gPlayerParty 0x03004360`
- `gSaveBlock1 0x02025734`
- `gSaveBlock2 0x02024EA4`
- `CB2_ChooseStarter 0x08109EA0`
- `Task_StarterChoose2 0x0810A198`
- `SeedRngWithRtc 0x080003E4`

The bridge now accepts both AXVE and AXPE for `STARTER_OPEN` and `STARTER_ARM`.

GitHub Actions build run: 34998246747
