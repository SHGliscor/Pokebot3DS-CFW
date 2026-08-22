# Pokebot3DS-CFW

<p align="center">
  <img src="./POKEBOT3DS-CFW-icon.png" width="220" alt="Pokebot3DS-CFW">
</p>

<p align="center">
  <strong>RAM-authoritative shiny-hunting automation for Pokémon Omega Ruby and Alpha Sapphire on a real Nintendo 3DS</strong>
</p>

<p align="center">
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/releases/latest"><img src="https://img.shields.io/badge/DOWNLOAD%20LATEST%20EXE-16a34a?style=for-the-badge&logo=windows11&logoColor=white" alt="Download latest EXE"></a>
  <a href="#3ds-files"><img src="https://img.shields.io/badge/SETUP%20GUIDE-2563eb?style=for-the-badge&logo=readthedocs&logoColor=white" alt="Setup guide"></a>
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/issues/new?template=bug_report.yml"><img src="https://img.shields.io/badge/REPORT%20BUG-dc2626?style=for-the-badge&logo=github&logoColor=white" alt="Report a bug"></a>
  <a href="#current-roadmap"><img src="https://img.shields.io/badge/PROJECT%20PROGRESS-7c3aed?style=for-the-badge&logo=githubactions&logoColor=white" alt="Project progress"></a>
</p>

<p align="center">
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/issues/new?template=feature_request.yml"><img src="https://img.shields.io/badge/REQUEST%20A%20FEATURE-f59e0b?style=flat-square&logo=github&logoColor=white" alt="Request a feature"></a>
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/issues"><img src="https://img.shields.io/github/issues/SHGliscor/Pokebot3DS-CFW?style=flat-square" alt="Open issues"></a>
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/stargazers"><img src="https://img.shields.io/github/stars/SHGliscor/Pokebot3DS-CFW?style=flat-square" alt="GitHub stars"></a>
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/network/members"><img src="https://img.shields.io/github/forks/SHGliscor/Pokebot3DS-CFW?style=flat-square" alt="GitHub forks"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Games-Omega%20Ruby%20%2B%20Alpha%20Sapphire-2563eb?style=flat-square" alt="Omega Ruby and Alpha Sapphire">
  <img src="https://img.shields.io/badge/Language-English%20Verified-16a34a?style=flat-square" alt="English verified">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows11&logoColor=white&style=flat-square" alt="Windows">
  <img src="https://img.shields.io/badge/CFW-Nexus3DS-7c3aed?style=flat-square" alt="Nexus3DS CFW">
  <img src="https://img.shields.io/badge/RAM%20Authority-PK6-0891b2?style=flat-square" alt="RAM authority">
  <img src="https://img.shields.io/badge/OR%20Starter%20Reset-6%2F6%20PASS-16a34a?style=flat-square" alt="Omega Ruby starter reset 6/6 PASS">
  <img src="https://img.shields.io/badge/Wild%20Walk%20%2F%20Run-Hardware%20Proven-16a34a?style=flat-square" alt="Wild Walk Run hardware proven">
  <img src="https://img.shields.io/badge/Acro%20Bunny-10%2F10%20PASS-16a34a?style=flat-square" alt="Acro Bunny 10/10 PASS">
</p>

---

## ORAS development progress

These percentages are **development estimates, not automated code coverage**. They are intended to make the current state of the project easy to understand. The overall ORAS figure is the simple average of the 18 sections below, so no hidden weighting is being used.

### Overall ORAS roadmap

**70%**

```text
██████████████░░░░░░ 70%
```

| ORAS section | Progress | Current status |
|---|---|---|
| CFW / RAM / input bridge | `████████████████████` **100%** | Read-only RAM + acknowledged HID/touch bridge hardware-proven |
| Hoenn starter automation | `████████████████████` **100%** | Treecko, Torchic, Mudkip + Random mode operational |
| Grass Wild automation | `███████████████████░` **95%** | RAM-authoritative encounter loop, terrain containment and automatic Run proven; wider coverage continues |
| Horde automation | `████████████████░░░░` **80%** | Natural and Sweet Scent Horde work implemented/hardware-tested in Alpha Sapphire; wider OR parity remains |
| Cave automation | `████████████████░░░░` **80%** | Cave hunting with Walk/Run/Acro Bunny hardware-tested in Alpha Sapphire; wider OR parity remains |
| Surf / Ocean automation | `████████████████░░░░` **80%** | Surf/Ocean hunting path implemented and hardware-tested in development; wider OR parity remains |
| Encounter / terrain DB + browser | `███████████████████░` **95%** | Whole-game ORAS encounter/terrain data and HUNTS browser are live; edge-case coverage continues |
| Dashboard / HUNTS | `██████████████████░░` **90%** | Main hunting workflow and encounter browser are live |
| STATS / history | `█████████████████░░░` **85%** | Persistent encounters, phase/lifetime analytics, extrema and history implemented; polish remains |
| TOOLS / support | `███████████████░░░░░` **75%** | Diagnostics/support design and support ZIP workflow implemented; some utilities remain unfinished |
| Discord notifications / Rich Presence | `████████████████░░░░` **80%** | Discord bot notifications and Rich Presence work implemented; further event/media wiring remains |
| Direct 3DS screenshot pipeline | `██████████████░░░░░░` **70%** | Direct top-screen framebuffer capture to PC image pipeline built; final Discord shiny-image attachment wiring remains |
| Block list | `████████████████░░░░` **80%** | Block-list feature is present; further documentation/polish remains |
| Fishing | `████░░░░░░░░░░░░░░░░` **20%** | Encounter data/browser support exists; production automation remains |
| Static encounters | `██░░░░░░░░░░░░░░░░░░` **10%** | Planned after the currently proven starter/Wild foundations |
| Postgame starters | `███░░░░░░░░░░░░░░░░░` **15%** | Johto/Unova/Sinnoh starters are in the browser; automation is not yet wired |
| Language validation | `███░░░░░░░░░░░░░░░░░` **15%** | English hardware-verified; other game languages remain unverified |
| Release / docs | `██████████████████░░` **90%** | README/setup/release structure largely complete; documentation follows development |

The percentages should move only when a section gains real implementation, hardware proof, production integration or required parity—not simply because code was written.

---

### Inspiration

Pokebot3DS-CFW takes inspiration from excellent Pokémon automation projects including:

- [pokebot-nds](https://github.com/wyanido/pokebot-nds/)
- [pokebot-gen3](https://github.com/40cakes/pokebot-gen3)
- [PokemonAutomation](https://github.com/PokemonAutomation)

Pokebot3DS-CFW is an independent implementation built around RAM-authoritative Gen 6 shiny hunting, acknowledged 3DS input and real-hardware safety gates.

---

## 🤖 Project Transparency & Use of AI

I want to be **100% transparent** with everyone who uses or contributes to this shiny hunting bot.

This project is currently developed by **one person — me**. I also work full-time and I'm a dad to a one-year-old, so realistically I only get a few hours each day to work on the project.

Because of that, **AI-assisted development ("vibe coding") is part of the development process**.

Some parts of the project have been heavily assisted by AI, particularly the dashboard/UI and areas where I've needed help debugging, restructuring, or correcting code I've written.

The backend and core bot logic, however, are largely based on my own work, testing, research, experimentation, and implementation. I would estimate that roughly **85% of the backend logic originates from my own work**, with AI helping me debug problems, improve implementations, and develop things faster than I would be able to.

I know that some people are strongly against the use of AI in software development, and I understand many of the concerns surrounding it. I agree with quite a few of those concerns myself.

At the same time, AI assistance has made it possible for me to continue developing this project at the pace I currently can while balancing work and family life.

I don't want to hide that or pretend the entire project was written without assistance.

If the use of AI means you would rather not use this project, I completely understand. I would much rather be upfront about how the project is developed and allow people to make that decision for themselves.

Thank you to everyone who tests the bot, reports bugs, provides feedback, or simply follows the project. ❤️

---

> [!IMPORTANT]
> **Pokebot3DS-CFW currently targets Pokémon Omega Ruby 1.4 and Pokémon Alpha Sapphire 1.4 on real 3DS hardware.**
>
> English is the currently hardware-verified game language. Other languages remain unverified until separately tested.

Pokebot3DS-CFW is a Windows Qt application paired with a customised Nexus3DS-based `boot.firm`. The firmware exposes a small read-only RAM bridge and an acknowledged HID/touch input bridge on UDP `4952`.

The bot treats validated Pokémon RAM as the source of truth. OCR or image matching is **not** used as shiny authority.

There is deliberately **no game-RAM write command** in the Pokebot bridge. RAM is used to observe the game and make safe automation decisions; Pokémon and encounter results are not modified.

---

## How is Pokebot3DS-CFW different from PKMN-NTR?

Pokebot3DS-CFW is **not a fork, replacement, or modified version of [PKMN-NTR](https://github.com/drgoku282/PKMN-NTR)**.

Both projects can communicate with a Nintendo 3DS and inspect Pokémon data in memory, but they are built for different purposes and use different architectures.

| Pokebot3DS-CFW | PKMN-NTR |
|---|---|
| Built specifically for **shiny-hunting automation** | General-purpose Pokémon memory editing/control tooling |
| Uses a **custom Nexus3DS-derived Pokebot bridge** | Built around **NTR-CFW / NTRClient** |
| Game RAM access is intentionally **read-only** | Supports reading and writing game memory |
| Does **not** expose Pokémon injection or editing | Can be used to edit or inject game data/Pokémon |
| Does **not** use the NTR debugger or GDB | Uses NTR's remote memory/debugging architecture |
| RAM determines the encounter result, then normal controller/touch input plays the game | Memory access can be used for editing as well as automation |
| Invalid or uncertain authority causes a **safety HOLD** | Not designed around Pokebot3DS-CFW's fail-closed shiny-hunting state machine |

### How RAM reading works

Pokebot3DS-CFW does not attach a debugger to the game. Instead, the custom `boot.firm` adds a small read-only service inside Rosalina/Nexus3DS.

1. The Windows bot sends a bounded RAM request to the 3DS over **UDP port 4952**.
2. The Pokebot bridge identifies the supported running game by title ID and opens the game process internally.
3. Before reading, the bridge checks the requested memory region and its permissions.
4. The requested bytes are read through the 3DS process-memory services and returned to the PC.
5. The PC decodes the returned game structure — for example a PK6 — and validates the checksum, species and other required identity/state fields.
6. Shiny state is calculated from the data that the game itself already generated.
7. If the data or game state is invalid, missing or uncertain, the bot **HOLDs instead of authorising a reset**.

The bridge protocol deliberately provides **no command that writes back into the game's RAM**. It cannot turn a Pokémon shiny, change its PID/IVs, inject a Pokémon, or alter the encounter result.

```text
Pokebot3DS-CFW on PC
        |
        |  bounded UDP 4952 read request
        v
Pokebot bridge in Nexus3DS / Rosalina
        |
        |  read-only process-memory access
        v
Pokémon OR / AS RAM
        |
        |  requested bytes returned
        v
Validate PK6 / game state -> shiny decision -> continue or HOLD
```

### How controller and touchscreen inputs are sent

Inputs use the same custom Pokebot bridge rather than NTR. They are kept separate from the RAM-reading authority: an input command controls the game, but it does not modify the game's memory.

1. The PC sends an input command to the bridge over **UDP 4952** with a unique sequence ID.
2. The 3DS acknowledges the request so the PC knows whether the command was accepted.
3. The bridge applies the requested HID state through the 3DS input path, producing normal button/directional input.
4. Timed HID commands automatically release after their requested hold period and can include a settle period.
5. Native touchscreen commands can press an exact bottom-screen coordinate without requiring a capture card or mouse automation.
6. Latched HID commands can keep a button held until an explicit release is sent when a hunt requires a continuous hold.
7. `RELEASE_ALL` provides an emergency neutral state, and sequence-ID deduplication prevents a retried UDP packet from creating a second unintended gameplay press.

```text
Pokebot3DS-CFW on PC
        |
        |  sequence-numbered input request
        v
Pokebot input bridge
        |
        +--> Button / D-pad / Circle-pad style HID input
        +--> Native touchscreen pulse
        +--> Latched hold when required
        |
        v
Normal 3DS gameplay input
        |
        +--> ACK / status returned to the PC
        +--> RELEASE_ALL available as a safety path
```

This separation is intentional: **RAM tells the bot what happened; controller/touch input tells the game what to do next.** RAM is never written to in order to force a hunt result.

---

## Current validated ORAS support

| Area | Alpha Sapphire 1.4 | Omega Ruby 1.4 |
|---|---|---|
| Game detection | ✅ `...C500 / sango-2` | ✅ `...C400 / sango-1` |
| Trainer / party RAM | ✅ Proven | ✅ Proven |
| Wild PK6 / battle RAM | ✅ Proven | ✅ Proven |
| Player X/Z + zone RAM | ✅ Proven | ✅ Proven |
| Birch starter chooser | ✅ Proven | ✅ Proven |
| Treecko / Torchic / Mudkip | ✅ Proven | ✅ Proven |
| Communication-error `code.ips` | ✅ Hardware proven | ✅ Hardware proven |
| Whole-game Wild terrain DB | ✅ Proven | ✅ Shared ORAS topology proven |
| Wild Walk / Run backend | ✅ Hardware proven | ✅ Hardware proven |
| Acro Bunny backend | ✅ 10/10 proof | ✅ Shared backend enabled |
| Natural Hordes | ✅ Hardware-tested | ⚪ OR-specific proof pending |
| Sweet Scent Hordes | ✅ Hardware-tested | ⚪ OR-specific proof pending |
| Cave Walk / Run / Acro Bunny | ✅ Hardware-tested | ⚪ OR-specific proof pending |
| Surf / Ocean | ✅ Hardware-tested | ⚪ OR-specific proof pending |
| Discord notifications / Rich Presence | ✅ Implemented | ✅ Shared PC feature |
| Direct top-screen framebuffer capture | 🟡 PC image pipeline built | 🟡 Shared pipeline; Discord attachment still pending |
| Block list | ✅ Implemented | ✅ Shared PC feature |

Omega Ruby completed the finite automated starter reset validation **6/6**, including two successful cycles for each Hoenn starter. The three locked starter modules are shared between the two ORAS profiles rather than duplicated.

---

## HUNTS — ORAS encounter browser

The **HUNTS** tab is now an encounter browser rather than a settings page.

Locations are separated by encounter environment/method so different hunt types are not mixed together. Depending on the location this includes:

- Grass
- Tall Grass
- Cave
- Surf / Water
- Ocean
- Rock Smash
- Old Rod
- Good Rod
- Super Rod
- Horde
- **DexNav Exclusive**

The 3-slot ORAS encounter table that some editing tools label `Swarm` is displayed as **DexNav Exclusive**, matching how those encounters are actually obtained in ORAS.

Each Pokémon card supports:

- normal artwork
- shiny artwork
- species/name
- level range
- encounter/gift information
- persistent lifetime **Shinies Found**

### Route 101 starters

Route 101 additionally shows Professor Birch's starter choices as separate sections:

| Group | Pokémon | Unlock |
|---|---|---|
| Hoenn | Treecko, Torchic, Mudkip | Opening Route 101 event |
| Johto | Chikorita, Cyndaquil, Totodile | First Hall of Fame + meet Zinnia |
| Unova | Snivy, Tepig, Oshawott | Complete the Delta Episode |
| Sinnoh | Turtwig, Chimchar, Piplup | Enter the Hall of Fame a second time |

All are Lv. 5 gift choices.

**Automation status:** the Hoenn trio is hardware-proven. The Johto/Unova/Sinnoh entries are present in the browser, but their automated selection/reset flows remain **not yet wired** until they receive their own RAM/state proof.

---

## Safety model

For an authoritative starter or wild encounter:

1. Reach the required RAM-confirmed game-state boundary.
2. Perform a bounded PK6 read.
3. Validate structure/checksum/species and required identity fields.
4. Calculate shiny state from RAM.
5. **Shiny = absolute HOLD.**
6. Only validated non-shiny authority permits the next reset/escape action.

Unexpected state, wrong species, checksum failure, RAM failure or controller safety failure causes a HOLD rather than blind continuation.

Core principles:

- no RAM writes for shiny decisions
- no OCR/image shiny authority
- bounded RAM reads rather than continuous Pokémon polling
- validated movement/terrain containment
- new low-level paths are proven standalone before being promoted

---

## 3DS files

The release contains:

```text
3ds_sd/
├─ boot.firm
└─ luma/
   └─ titles/
      ├─ 000400000011C400/
      │  └─ code.ips        # Omega Ruby 1.4
      └─ 000400000011C500/
         └─ code.ips        # Alpha Sapphire 1.4
```

Back up your existing `boot.firm` before replacing it.

The current controller/RAM bridge uses **UDP 4952**. The `code.ips` files are separate game patches; they are not the controller.

---

```text
dist/
└─ Pokebot3DS-CFW/
   ├─ Pokebot3DS-CFW.exe
   ├─ _internal/
   ├─ assets/
   ├─ data/
   ├─ 3ds_sd/
   ├─ README.md
   ├─ README_EXE.md
   └─ HOW_TO_USE.txt
```

---

## Persistent data

User-specific settings/stats are stored under:

```text
%APPDATA%\Pokebot-3DS\
```

The encounter browser's per-species shiny totals are stored persistently, allowing the same Pokémon to show one lifetime shiny total even when it appears on multiple routes or encounter types.

---

## Current roadmap

### ORAS
- [x] Alpha Sapphire starter RAM backend
- [x] Omega Ruby RAM parity
- [x] Omega Ruby Hoenn starter one-shots
- [x] Omega Ruby finite starter reset cycle 6/6
- [x] Random Hoenn starter mode
- [x] OR + AS `code.ips` reset-route patches
- [x] acknowledged UDP 4952 input controller
- [x] native acknowledged touchscreen input
- [x] Wild PK6 authority
- [x] automatic Run after validated non-shiny
- [x] Walk/Run finite Wild proof
- [x] Acro Bunny finite Wild proof
- [x] 30/30 complete W6 causal Wild baseline
- [x] unlimited Dashboard Wild mode
- [x] whole-game terrain database
- [x] ORAS automatic game profiles
- [x] encounter browser
- [x] Alpha Sapphire Horde development path
- [x] Alpha Sapphire Sweet Scent Horde development path
- [x] Alpha Sapphire Cave Walk/Run/Acro development path
- [x] Alpha Sapphire Surf/Ocean development path
- [x] Discord notification integration
- [x] Discord Rich Presence integration
- [x] direct 3DS top-screen framebuffer-to-PC image pipeline
- [x] block-list feature
- [x] persistent stats/history and shiny phase tracking
- [x] support ZIP export
- [ ] attach direct 3DS screenshot to Discord shiny notification
- [ ] Omega Ruby-specific Horde/Cave/Surf hardware parity
- [ ] Johto postgame starter automation
- [ ] Unova postgame starter automation
- [ ] Sinnoh postgame starter automation
- [ ] Surf/Fishing production automation
- [ ] static encounter production automation

### Later games
- [ ] Pokémon X / Y
- [ ] Sun / Moon
- [ ] Ultra Sun / Ultra Moon
- [ ] Gen 2 VC Gold / Silver / Crystal integration
- [ ] additional language validation

---

## Compatibility

### Supported / hardware validated
- ✅ Real Nintendo 3DS / New Nintendo 3DS hardware
- ✅ Pokémon Omega Ruby 1.4
- ✅ Pokémon Alpha Sapphire 1.4
- ✅ English
- ✅ Custom Nexus3DS-based Pokebot3DS-CFW bridge
- ✅ UDP 4952 RAM + acknowledged input
- ✅ Windows Qt dashboard

### Not claimed yet
- ❌ emulator support wont ever be supported by myself i dont have the means to port it to emulator
- ❌ non-English game languages
- ❌ postgame Johto/Unova/Sinnoh starter automation
- ❌ production static hunts
- ❌ production Fishing
- ❌ XY / Gen 7 production support

---

## Disclaimer

Pokebot3DS-CFW is an independent homebrew/automation project. Use it only with real 3DS hardware. Keep backups of your SD card and important save data before testing custom firmware, patches or automation.

---

## Latest development progress — August 2026

The existing README above is intentionally preserved. This section records newer progress made after several of the earlier validation notes were written.

### Omega Ruby Wild automation is now hardware-proven

Omega Ruby has now completed an automated **5/5 finite Wild Run proof** using the frozen W6 causal wild state machine on real hardware.

- detected game: **Pokémon Omega Ruby 1.4** (`...C400 / sango-1`)
- exactly **5/5 encounters completed successfully**
- one authoritative PK6 read per encounter
- validated checksum/species/TID-SID before continuation
- non-shiny encounters escaped automatically
- post-escape field authority and encounter-terrain containment re-confirmed before movement resumed
- zero touch-timeout recoveries during the proof
- shiny or invalid authority still causes an **absolute HOLD**

This newer proof advances Omega Ruby beyond the earlier **“Shared backend enabled”** wording in older validation notes. The proven Run behaviour is now treated as a frozen working path rather than something to optimise unnecessarily.

The normal Dashboard Wild hunt is **unlimited** and continues until the user stops it, a shiny is found, or a safety condition causes a HOLD. The separate finite launcher remains a diagnostic/proof tool.

Early real-hardware testing has also successfully triggered and handled Wild encounters in several additional grass areas beyond the original Route 101 proof area, including tests that did not require a route-specific grass database entry for each location. Broader map-by-map coverage is still being accumulated rather than assumed complete.

### Wild causal baseline and terrain-aware movement

The Alpha Sapphire Wild path reached a **30/30 complete W6 causal baseline** before being promoted into the normal unlimited Dashboard hunt.

The Wild engine uses:

- bounded terrain-aware movement
- authoritative player/zone coordinates from RAM
- encounter-terrain containment
- one authoritative PK6 logical read per encounter
- checksum/species/TID-SID validation
- RAM shiny decision
- absolute HOLD on shiny or invalid state
- native acknowledged touchscreen Run input
- post-escape field/terrain authority before movement resumes

The proven escape path commonly accepts the Run action after roughly **12–13 native touchscreen pulses**. Because it is already reliable and exits battle quickly, that sequence is intentionally being left alone rather than shortened just for timing.

### Horde encounters

Horde support has progressed beyond simply displaying Horde encounter tables in HUNTS.

Development/hardware testing now includes:

- natural Horde encounter handling
- RAM inspection of all five Pokémon in a Horde rather than treating the encounter as one Pokémon
- shiny safety across the Horde slots
- Sweet Scent-triggered Horde automation
- continuation only after the Horde has been validated as safe/non-shiny

The currently proven Horde work is on Alpha Sapphire; Omega Ruby-specific Horde parity remains to be validated before it is marked complete for both games.

### Cave hunting

Cave hunting has been implemented and hardware-tested in Alpha Sapphire, including Fiery Path development runs.

The cave path reuses the RAM-authoritative Wild safety model and supports the movement styles that have been proven there, including Walk/Run and Acro Bunny development paths. Cave movement is treated separately from outdoor grass so the bot does not assume every encounter area has the same terrain geometry.

Omega Ruby-specific cave parity is still tracked separately rather than assumed from Alpha Sapphire.

### Surf and Ocean hunting

Surf/Ocean hunting has also moved beyond encounter-browser data and into real automation testing.

The Surf path uses the same fundamental rule as land Wilds: the encounter result comes from validated PK6 RAM, not the screen. Movement/continuation authority is kept separate from the Pokémon shiny decision so an unexpected water/field state cannot authorise blind movement.

Alpha Sapphire Surf/Ocean development has been hardware-tested; broader production coverage and Omega Ruby-specific parity remain open work.

### Random Hoenn starters

A **Random** starter mode has been added for the hardware-proven Hoenn trio.

On every reset the orchestration layer independently chooses one of:

- Treecko
- Torchic
- Mudkip

The random chooser only selects which locked starter module runs. It does **not** replace or rewrite the proven Treecko/Torchic/Mudkip selection logic, and the individual per-starter ledgers remain authoritative.

During hardware testing an orchestration regression caused Random mode to select Treecko and Torchic while omitting Mudkip, even though direct Mudkip selection still worked. That Random-mode regression has now been fixed and the current build can dispatch all three Hoenn starters through Random mode.

### Long-run starter and input validation

The custom `boot.firm` input path has now been exercised in longer real-hardware starter runs rather than only short finite proofs.

- one run completed **415 resets in a little over four hours** after moving to the new input path
- no stuck/held-input failure was observed during that run
- the same acknowledged input bridge handles buttons, directional input and native touchscreen pulses
- starter shiny authority remains RAM-based; the input bridge only performs normal gameplay controls

Torchic has also been observed at roughly **35–36 seconds per reset**, or around **100 resets/hour**, on the current hardware/setup. This is an observed development benchmark rather than a guaranteed rate on every network or 3DS.

### Discord integration

Discord support is now part of the desktop-bot work rather than a future concept.

Current Discord development includes:

- bot-account based notifications
- hunt/status information suitable for remote monitoring
- Discord Rich Presence work for current hunt/status/elapsed visibility
- shiny/event notification plumbing

Discord is not used as hunt authority. A Discord failure cannot decide whether a Pokémon is shiny or authorize a reset; RAM safety remains independent.

### Direct 3DS screenshot pipeline

A direct screenshot path is being built so shiny notifications do not have to depend on an external capture card.

The current pipeline can work from the 3DS top-screen framebuffer, transfer the image data through bounded/verified chunks, reconstruct the **400×240** top-screen image on the PC, and encode it as a normal image file. This is deliberately separate from shiny authority: the screenshot is evidence/presentation only.

The remaining step is to wire that direct 3DS image into the final Discord shiny notification attachment path. Until that wiring is hardware-proven, the README does **not** claim that Discord screenshot delivery itself is complete.

### Block list

The bot also contains a **block-list** feature. It is tracked separately from the RAM shiny decision and is part of the user-control/safety layer. The README records the feature as implemented without inventing undocumented behaviour that has not yet been recovered from the current packaged build.

### STATS is now analytics/history focused

The STATS design is separated from hunt selection and configuration. Its role is to show what the bot has achieved over time.

Current analytics coverage includes:

- lifetime encounters and shinies
- current phase and phase encounters
- total hunt time and encounters/hour
- current target, game, location and hunt method
- shiny-value and IV extrema
- per-species history
- method breakdowns
- location breakdowns
- Omega Ruby / Alpha Sapphire / combined ORAS totals
- chronological shiny history
- records such as fastest shiny and longest phase
- encounters/hour, cumulative encounter/shiny, species and method graphs
- odds-cycle progress

Shiny Charm-adjusted odds are only used when Charm status has a proven RAM authority for the active game; unknown authority is not silently guessed.

### TOOLS is for diagnostics and support

TOOLS is being kept separate from normal hunting and settings. The page is organised around:

**3DS Diagnostics | RAM & Game Data | Maintenance | Support**

The Tools design includes a top-level **System Health** view plus utilities for:

- UDP 4952 connection/game detection
- controller acknowledgement testing
- safe read-only RAM inspection
- manual PK6 inspection
- terrain/position/corridor inspection
- encounter-table lookup
- Shiny Charm authority display
- local game-patch validation
- CFW/bridge capability information
- sprite-cache maintenance
- support ZIP export
- opening Stats/Logs/Cache/Support/AppData folders
- bot/build/patch/database information
- non-destructive self-test diagnostics
- optional advanced raw/state/protocol diagnostics

Unsupported or not-yet-proven authorities are shown as **UNVERIFIED** rather than fabricated as PASS.

### Current UI responsibility split

```text
DASHBOARD = run the hunt
HUNTS     = choose what to hunt
STATS     = analyse history and results
TOOLS     = diagnose, test and inspect
SETTINGS  = configure the bot
```

The underlying safety model remains unchanged: **RAM is authoritative, no RAM writes are used for shiny decisions, and invalid state means HOLD rather than blind continuation.**
