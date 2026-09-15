# Gen 3 v0p23 — Main Dashboard Modes

The separate Wild Encounters top-level tab has been removed from the app flow.

The existing Pokémon-themed Dashboard is now the single hunt surface.

Dashboard control flow:
- Mode = Starters
  - second selector = Starter
  - Torchic / Treecko / Mudkip / Random
- Mode = Wild Encounters
  - second selector = Method
  - Spin / Run / Walk / Acro Bike Bunny Hop / Sweet Scent / Fishing / Rock Smash / Safari / Feebas

Spin is the first implemented wild worker. The other methods are exposed through the modular registry and will be implemented one at a time.

Wild encounters now feed the same:
- Current Encounter card
- Shiny Phase stats
- Encounter Log
- Phase Records
- Lifetime stats
- Recent Shinies

The frozen v0p21 HF1 starter backend/UI/CIA are unchanged and remain SHA-256 verified.
