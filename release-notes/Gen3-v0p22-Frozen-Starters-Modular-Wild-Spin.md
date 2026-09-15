# Gen 3 v0p22 — Frozen Starters + Modular Wild Spin

Starter development is frozen at v0p21 HF1 after hardware passes on:
- Ruby AXVE rev00 / v1.0
- Ruby AXVE rev01 / v1.1
- Sapphire AXPE rev00 / v1.0
- Sapphire AXPE rev01 / v1.1

The frozen starter backend/UI and v0p21 CIA are not modified by v0p22. Ruby v1.1 had exceeded 900 resets with no duplicate PID on the v0p19-derived generation-aware RNG path before the freeze.

v0p22 is PC-side only and adds the first modular wild encounter method:
- Spin
- shared Ruby/Sapphire v1.0-v1.1 wild RAM profile
- direct gEnemyParty PK3 decoding
- trainer-battle safety stop
- exact generation repeat tracking
- live action-cursor RUN navigation
- stationary tile drift safety
- shiny hold with fast-forward disabled
- Route 101 normal/shiny/anti-shiny sprites

New hunt logic lives under `gen3bot/`; the frozen starter files are imported unchanged.

No new CIA is required for v0p22.
