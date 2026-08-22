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
  <img src="https://img.shields.io/badge/CFW-Pokebot--Luma%20%2F%20Luma3DS-7c3aed?style=flat-square" alt="Pokebot-Luma / Luma3DS">
  <img src="https://img.shields.io/badge/RAM%20Authority-PK6-0891b2?style=flat-square" alt="RAM authority">
  <img src="https://img.shields.io/badge/Luma%20RAM%20Bridge-Hardware%20Proven-16a34a?style=flat-square" alt="Luma RAM bridge hardware proven">
  <img src="https://img.shields.io/badge/Additive%20Input-Hardware%20Proven-16a34a?style=flat-square" alt="Additive input hardware proven">
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
| CFW / RAM / input bridge | `████████████████████` **100%** | Pokebot-Luma read-only RAM bridge + additive Luma input path hardware-proven |
| Hoenn starter automation | `████████████████████` **100%** | Treecko, Torchic, Mudkip + Random mode operational |
| Grass Wild automation | `███████████████████░` **95%** | RAM-authoritative encounter loop, terrain containment and automatic Run proven; integrated Luma regression testing continues |
| Horde automation | `████████████████░░░░` **80%** | Natural and Sweet Scent Horde work implemented/hardware-tested in Alpha Sapphire; wider OR parity remains |
| Cave automation | `████████████████░░░░` **80%** | Cave hunting with Walk/Run/Acro Bunny hardware-tested in Alpha Sapphire; wider OR parity remains |
| Surf / Ocean automation | `████████████████░░░░` **80%** | Surf/Ocean hunting path implemented and hardware-tested in development; wider OR parity remains |
| Encounter / terrain DB + browser | `███████████████████░` **95%** | Whole-game ORAS encounter/terrain data and HUNTS browser are live; edge-case coverage continues |
| Dashboard / HUNTS | `██████████████████░░` **90%** | Main hunting workflow and encounter browser are live |
| STATS / history | `█████████████████░░░` **85%** | Persistent encounters, phase/lifetime analytics, extrema and history implemented; polish remains |
| TOOLS / support | `███████████████░░░░░` **75%** | Diagnostics/support design and support ZIP workflow implemented; some utilities remain unfinished |
| Discord notifications / Rich Presence | `████████████████░░░░` **80%** | Discord bot notifications and Rich Presence work implemented; further event/media wiring remains |
| Direct 3DS screenshot pipeline | `██████████░░░░░░░░░░` **50%** | PC image pipeline exists; direct framebuffer transport is not yet implemented in Pokebot-Luma v0p4 |
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

Pokebot3DS-CFW is an independent implementation built around RAM-authoritative Gen 6 shiny hunting, 3DS input automation and real-hardware safety gates.

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

Pokebot3DS-CFW is a Windows Qt application paired with **Pokebot-Luma**, a Luma3DS-derived `boot.firm` containing the Pokebot-specific Rosalina bridge.

The current split transport is:

- **UDP 4952 — read-only RAM bridge:** `PING`, `GAME_INFO`, `QUERY`, and bounded `READ` up to `0x200` bytes.
- **UDP 4950 — input controller:** Luma3DS InputRedirection with Pokebot's additive active-low button merge so physical and injected buttons can coexist.

The bot treats validated Pokémon RAM as the source of truth. OCR or image matching is **not** used as shiny authority.

There is deliberately **no game-RAM write command** in the Pokebot RAM bridge. RAM is used to observe the game and make safe automation decisions; Pokémon and encounter results are not modified.

### Current Pokebot-Luma hardware proof

The following has been proven on real Alpha Sapphire 1.4 hardware:

- Pokebot-Luma boots and returns to ORAS normally.
- Physical A/B/D-pad and touchscreen remain usable.
- Remote **A** and **START** reach ORAS through UDP `4950`.
- A different physical button remains usable during a long synthetic button hold.
- RAM `PING`, `GAME_INFO`, `QUERY`, and bounded `READ` work over UDP `4952`.
- Alpha Sapphire is correctly identified as `000400000011C500 / sango-2`.
- A real `wild/opponent0` PK6 at `0x081FFA6C` was read, decrypted and checksum-validated.
- The hardware proof PK6 was species **#293 Whismur**, non-shiny, with a matching `0xEC9C` checksum.

---

## Pokebot-Luma Rosalina menu

Pokebot-Luma adds a dedicated submenu to Rosalina.

Open Rosalina with the normal Luma3DS combo:

```text
L + D-Pad Down + Select
```

Then open:

```text
Pokebot3DS Bridge...
```

The submenu contains:

```text
Toggle RAM Bridge
Toggle Input Controller
Enable Both
Disable Both
Status
```

For normal bot use, select **Enable Both** after the game and Wi-Fi are up.

The v0p4 status screen reports:

```text
Pokebot-Luma v0p4

RAM Bridge:       ON / OFF
RAM result:       0x........
RAM UDP:          4952
Packets / Reads:  ... / ...

Input Controller: ON / OFF
Input result:     0x........
Input UDP:        4950
```

`RAM result` and `Input result` should normally be `0x00000000` after successful startup.

The two services are intentionally separate: RAM authority remains read-only on `4952`, while normal gameplay input uses Luma's HID/InputRedirection path on `4950`.

### Additive physical + remote buttons

The standard 3DS HID button mask is active-low. Pokebot-Luma merges physical and remote masks with:

```text
effective_raw_hid = physical_raw_hid & remote_raw_hid
```

This means, semantically:

```text
effective pressed buttons = physical OR injected
```

A remote press therefore does not intentionally take ownership of the entire physical button state.

---

## How is Pokebot3DS-CFW different from PKMN-NTR?

Pokebot3DS-CFW is **not a fork, replacement, or modified version of [PKMN-NTR](https://github.com/drgoku282/PKMN-NTR)**.

Both projects can communicate with a Nintendo 3DS and inspect Pokémon data in memory, but they are built for different purposes and use different architectures.

| Pokebot3DS-CFW | PKMN-NTR |
|---|---|
| Built specifically for **shiny-hunting automation** | General-purpose Pokémon memory editing/control tooling |
| Uses a **custom Luma3DS-derived Pokebot-Luma bridge** | Built around **NTR-CFW / NTRClient** |
| Game RAM access is intentionally **read-only** | Supports reading and writing game memory |
| Does **not** expose Pokémon injection or editing | Can be used to edit or inject game data/Pokémon |
| Does **not** use the NTR debugger or GDB for normal hunt authority | Uses NTR's remote memory/debugging architecture |
| RAM determines the encounter result, then normal controller/touch input plays the game | Memory access can be used for editing as well as automation |
| Invalid or uncertain authority causes a **safety HOLD** | Not designed around Pokebot3DS-CFW's fail-closed shiny-hunting state machine |

### How RAM reading works

Pokebot3DS-CFW does not attach a debugger to the game for normal hunt authority. The custom Luma3DS-derived firmware adds a small read-only Pokebot service inside Rosalina.

1. The Windows bot sends a bounded RAM request to the 3DS over **UDP port 4952**.
2. The Pokebot bridge identifies the supported running game by title ID and opens the game process internally.
3. Before reading, the bridge checks the requested memory region and its permissions.
4. The requested bytes are temporarily mapped/read through the 3DS process-memory services and returned to the PC.
5. The PC decodes the returned game structure — for example a PK6 — and validates checksum, species and the required identity/state fields.
6. Shiny state is calculated from the data that the game itself already generated.
7. If the data or game state is invalid, missing or uncertain, the bot **HOLDs instead of authorising a reset**.

The bridge protocol deliberately provides **no command that writes back into the game's RAM**. It cannot turn a Pokémon shiny, change its PID/IVs, inject a Pokémon, or alter the encounter result.

```text
Pokebot3DS-CFW on PC
        |
        |  bounded UDP 4952 read request
        v
Pokebot RAM bridge in Pokebot-Luma / Rosalina
        |
        |  read-only process-memory access
        v
Pokémon OR / AS RAM
        |
        |  requested bytes returned
        v
Validate PK6 / game state -> shiny decision -> continue or HOLD
```

### How controller inputs are sent

Controller input is separate from RAM authority.

1. The PC sends the Luma InputRedirection packet to **UDP 4950**.
2. Pokebot-Luma's HID hook merges the remote active-low button mask with the physical console mask.
3. ORAS receives the resulting normal HID state.
4. Returning the remote mask to neutral releases only the injected state; physical controls remain available.

The standalone real-hardware proof has confirmed remote A, remote START and physical/remote coexistence. Integrated hunt regression testing is still required before every older movement/touch path is re-labelled as proven under Pokebot-Luma.

This separation is intentional: **RAM tells the bot what happened; controller/touch input tells the game what to do next.** RAM is never written to in order to force a hunt result.

---

## Current validated ORAS support

| Area | Alpha Sapphire 1.4 | Omega Ruby 1.4 |
|---|---|---|
| Game detection | ✅ `...C500 / sango-2` | ✅ `...C400 / sango-1` |
| Trainer / party RAM | ✅ Proven | ✅ Proven |
| Wild PK6 / battle RAM | ✅ Proven; Pokebot-Luma real PK6 proof complete | ✅ Existing OR path proven; Luma integrated regression pending |
| Player X/Z + zone RAM | ✅ Proven | ✅ Proven |
| Birch starter chooser | ✅ Proven | ✅ Proven |
| Treecko / Torchic / Mudkip | ✅ Proven | ✅ Proven |
| Communication-error `code.ips` | ✅ Hardware proven | ✅ Hardware proven |
| Whole-game Wild terrain DB | ✅ Proven | ✅ Shared ORAS topology proven |
| Wild Walk / Run backend | ✅ Hardware proven on prior transport | ✅ Hardware proven on prior transport |
| Acro Bunny backend | ✅ 10/10 proof on prior transport | ✅ Shared backend enabled |
| Natural Hordes | ✅ Hardware-tested | ⚪ OR-specific proof pending |
| Sweet Scent Hordes | ✅ Hardware-tested | ⚪ OR-specific proof pending |
| Cave Walk / Run / Acro Bunny | ✅ Hardware-tested | ⚪ OR-specific proof pending |
| Surf / Ocean | ✅ Hardware-tested | ⚪ OR-specific proof pending |
| Discord notifications / Rich Presence | ✅ Implemented | ✅ Shared PC feature |
| Direct top-screen framebuffer capture | 🟡 PC pipeline retained; Pokebot-Luma transport pending | 🟡 Same |
| Block list | ✅ Implemented | ✅ Shared PC feature |

Omega Ruby completed the finite automated starter reset validation **6/6**, including two successful cycles for each Hoenn starter. The three locked starter modules are shared between the two ORAS profiles rather than duplicated.

---

## HUNTS — ORAS encounter browser

The **HUNTS** tab is an encounter browser rather than a settings page.

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
5. **Shiny = absolute HOLD** unless an explicitly configured block-list rule says that species is not a keeper.
6. Only validated non-shiny/non-keeper authority permits the next reset/escape action.

Unexpected state, wrong species, checksum failure, RAM failure or controller safety failure causes a HOLD rather than blind continuation.

Core principles:

- no RAM writes for shiny decisions
- no OCR/image shiny authority
- bounded RAM reads rather than continuous Pokémon polling
- validated movement/terrain containment
- new low-level paths are proven standalone before being promoted

---

## 3DS files

The current package contains:

```text
3ds_sd/
├─ boot.firm                         # Pokebot-Luma v0p4
├─ README.txt
├─ Pokebot-Luma-source/
│  ├─ LUMA3DS_LICENSE.txt
│  ├─ UPSTREAM.txt
│  ├─ apply_additive_input_redirection.py
│  ├─ apply_pokebot_menu.py         # adds Pokebot3DS Bridge... to Rosalina
│  ├─ apply_ram_bridge.py
│  └─ apply_ram_bridge_compile_fix.py
└─ luma/
   └─ titles/
      ├─ 000400000011C400/
      │  └─ code.ips                # Omega Ruby 1.4
      └─ 000400000011C500/
         └─ code.ips                # Alpha Sapphire 1.4
```

Back up your existing SD-root `boot.firm` before replacing it.

After booting the new firmware and launching ORAS, open Rosalina and choose **Pokebot3DS Bridge... → Enable Both**.

Current networking:

```text
RAM bridge:       UDP 4952
Input controller: UDP 4950
```

The `code.ips` files are separate game patches; they are not the controller.

Pokebot-Luma is a modified Luma3DS build. The package includes the relevant Luma3DS license and source patch scripts, and the upstream Luma3DS commit used for this build is recorded in the packaged source notes.

---

```text
Pokebot3DS-CFW/
├─ 3ds_sd/
├─ assets/
├─ data/
├─ pokebot/
├─ qt_ui/
├─ HOW_TO_USE.txt
├─ MANIFEST_v0p42L.json
├─ requirements.txt
└─ run_qt_live.py
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
- [x] Pokebot-Luma v0p4 menu/firmware foundation
- [x] additive Luma InputRedirection buttons on UDP 4950
- [x] physical + injected button coexistence proof
- [x] read-only RAM bridge on UDP 4952
- [x] RAM PING / GAME_INFO / QUERY / READ hardware proof
- [x] real Alpha Sapphire wild PK6 read/decrypt/checksum proof through Pokebot-Luma
- [x] Wild PK6 authority
- [x] automatic Run after validated non-shiny on the proven hunt backend
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
- [x] block-list feature
- [x] persistent stats/history and shiny phase tracking
- [x] support ZIP export
- [ ] integrated Pokebot-Luma short Wild regression
- [ ] integrated Pokebot-Luma starter endurance regression
- [ ] revalidate remote touchscreen hunt actions through Pokebot-Luma
- [ ] add Pokebot-Luma direct framebuffer transport for Discord screenshots
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
- ✅ Pokebot-Luma / Luma3DS-derived Pokebot bridge
- ✅ UDP 4952 read-only RAM bridge
- ✅ UDP 4950 additive button input
- ✅ Windows Qt dashboard

### Not claimed yet
- ❌ emulator support wont ever be supported by myself i dont have the means to port it to emulator
- ❌ non-English game languages
- ❌ full integrated-hunt regression on the new Pokebot-Luma transport
- ❌ production postgame Johto/Unova/Sinnoh starter automation
- ❌ production static hunts
- ❌ production Fishing
- ❌ XY / Gen 7 production support

---

## Disclaimer

Pokebot3DS-CFW is an independent homebrew/automation project. Use it only with real 3DS hardware. Keep backups of your SD card and important save data before testing custom firmware, patches or automation.

---

## Latest development progress — August 2026

The README sections above retain the established project history while this section records newer work.

### Pokebot-Luma low-level bridge

The active firmware is now **Pokebot-Luma v0p4**, a Luma3DS-derived build with a dedicated **Pokebot3DS Bridge** Rosalina submenu.

The controller side uses Luma's HID/InputRedirection architecture. The button hook uses additive active-low merging, which has been proven on real ORAS hardware with remote A, remote START, physical controls and simultaneous physical/remote button use.

The RAM side is a separate read-only UDP service on port `4952`. It supports only `PING`, `GAME_INFO`, `QUERY` and bounded `READ` up to `0x200`; there is no game-memory write command.

A real Alpha Sapphire wild Pokémon structure was read through this bridge from `0x081FFA6C`, decrypted as a valid Gen 6 PK6 and accepted only after its checksum matched. This proves that the Luma-based bridge reaches the authoritative game data required by the hunt backend.

### Omega Ruby Wild automation is hardware-proven

Omega Ruby completed an automated **5/5 finite Wild Run proof** using the frozen W6 causal wild state machine on real hardware.

- detected game: **Pokémon Omega Ruby 1.4** (`...C400 / sango-1`)
- exactly **5/5 encounters completed successfully**
- one authoritative PK6 read per encounter
- validated checksum/species/TID-SID before continuation
- non-shiny encounters escaped automatically
- post-escape field authority and encounter-terrain containment re-confirmed before movement resumed
- zero touch-timeout recoveries during the proof
- shiny or invalid authority causes a HOLD

That proof predates the Pokebot-Luma transport migration, so the state machine remains frozen while the new low-level transport receives targeted regression testing instead of being re-designed.

The normal Dashboard Wild hunt is **unlimited** and continues until the user stops it, a keeper shiny is found, or a safety condition causes a HOLD. The separate finite launcher remains a diagnostic/proof tool.

### Wild causal baseline and terrain-aware movement

The Alpha Sapphire Wild path reached a **30/30 complete W6 causal baseline** before being promoted into the normal unlimited Dashboard hunt.

The Wild engine uses:

- bounded terrain-aware movement
- authoritative player/zone coordinates from RAM
- encounter-terrain containment
- one authoritative PK6 logical read per encounter
- checksum/species/TID-SID validation
- RAM shiny decision
- HOLD on keeper shiny or invalid state
- native touchscreen Run input
- post-escape field/terrain authority before movement resumes

The proven escape path commonly accepts Run after roughly **12–13 touchscreen pulses**. Because it is already reliable and exits battle quickly, that sequence is intentionally not being shortened merely for timing.

### Horde encounters

Horde support has progressed beyond simply displaying Horde encounter tables in HUNTS.

Development/hardware testing includes:

- natural Horde encounter handling
- RAM inspection of all five Pokémon in a Horde
- shiny safety across the Horde slots
- Sweet Scent-triggered Horde automation
- continuation only after the Horde has been validated as safe/non-keeper

The currently proven Horde work is on Alpha Sapphire; Omega Ruby-specific Horde parity remains to be validated.

### Cave hunting

Cave hunting has been implemented and hardware-tested in Alpha Sapphire, including Fiery Path development runs.

The cave path reuses the RAM-authoritative Wild safety model and supports proven Walk/Run and Acro Bunny development paths. Cave movement is treated separately from outdoor grass so the bot does not assume every encounter area has the same terrain geometry.

### Surf and Ocean hunting

Surf/Ocean hunting has moved beyond encounter-browser data and into real automation testing.

The Surf path uses the same fundamental rule as land Wilds: the encounter result comes from validated PK6 RAM, not the screen. Movement/continuation authority is kept separate from the Pokémon shiny decision so an unexpected water/field state cannot authorise blind movement.

### Random Hoenn starters

A **Random** starter mode is present for the hardware-proven Hoenn trio.

On every reset the orchestration layer independently chooses one of:

- Treecko
- Torchic
- Mudkip

The random chooser only selects which locked starter module runs. It does **not** replace or rewrite the proven Treecko/Torchic/Mudkip selection logic.

### Long-run starter validation

The previous production input path completed long real-hardware starter runs, including one run of **415 resets in a little over four hours** without a stuck/held-input failure.

Torchic has also been observed at roughly **35–36 seconds per reset**, or around **100 resets/hour**, on the development hardware/setup. These are observed benchmarks rather than guaranteed rates.

The starter state machines and timing constants are being preserved during the Pokebot-Luma transport migration; the goal is transport replacement without disturbing their proven game choreography.

### Discord integration

Discord support includes:

- bot-account based notifications
- hunt/status information suitable for remote monitoring
- Discord Rich Presence
- shiny/event notification plumbing

Discord is not hunt authority. A Discord failure cannot decide whether a Pokémon is shiny or authorize a reset; RAM safety remains independent.

### Direct 3DS screenshot pipeline

The PC-side framebuffer/image reconstruction code is retained, but **Pokebot-Luma v0p4 does not yet expose the direct framebuffer transport commands required by that pipeline**.

Screenshot delivery is presentation-only and does not affect RAM shiny authority.

### Block list

The bot contains a **block-list** feature. It is tracked separately from RAM shiny calculation and forms part of keeper/continuation policy.

### STATS is analytics/history focused

The STATS design is separated from hunt selection and configuration. Current analytics coverage includes:

- lifetime encounters and shinies
- current phase and phase encounters
- total hunt time and encounters/hour
- current target, game, location and hunt method
- shiny-value and IV extrema
- per-species history
- method and location breakdowns
- Omega Ruby / Alpha Sapphire / combined ORAS totals
- chronological shiny history
- records such as fastest shiny and longest phase
- encounter/shiny/species/method graphs
- odds-cycle progress

### TOOLS is for diagnostics and support

TOOLS is kept separate from normal hunting and settings. The page is organised around:

**3DS Diagnostics | RAM & Game Data | Maintenance | Support**

The design includes utilities for connection/game detection, controller testing, safe read-only RAM inspection, manual PK6 inspection, terrain/position/corridor inspection, encounter-table lookup, game-patch validation, support ZIP export and local application folders.

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
