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

**75%**

```text
███████████████░░░░░ 75%
```

| ORAS section | Progress | Current status |
|---|---|---|
| CFW / RAM / input bridge | `████████████████████` **100%** | Pokebot-Luma read-only RAM bridge + acknowledged controller hardware-proven; retained HID latch, touch pulse and emergency release are working on real hardware |
| Hoenn starter automation | `████████████████████` **100%** | Treecko, Torchic, Mudkip + Random mode operational; current acknowledged-controller reset path is hardware-proven |
| Grass Wild automation | `████████████████████` **100%** | RAM-authoritative encounter loop, terrain containment, current controller movement and automatic Run are operational; wider OR regression sweep is still planned |
| Horde automation | `███████████████████░` **95%** | Natural and Sweet Scent Horde automation is implemented/hardware-tested in Alpha Sapphire, including post-battle re-arm; OR parity remains |
| Cave automation | `███████████████████░` **95%** | Cave Walk/Run/Acro Bunny are hardware-tested in Alpha Sapphire with stable-grid authority, longer Run bursts and post-battle re-arm; OR parity remains |
| Surf / Ocean automation | `██████████████████░░` **90%** | Surf/Ocean hunting path is implemented and hardware-tested in development; wider OR parity remains |
| Encounter / terrain DB + browser | `████████████████████` **100%** | Whole-game ORAS encounter/terrain data and HUNTS browser are live, including environment-specific encounter tables |
| Dashboard / HUNTS | `███████████████████░` **95%** | Main hunting workflow and encounter browser are live; Party Pokémon live-order refresh remains a known display issue |
| STATS / history | `██████████████████░░` **90%** | Persistent encounters, phase/lifetime analytics, extrema and history are implemented; polish remains |
| TOOLS / support | `██████████████████░░` **90%** | Diagnostics/support design, hardware controller testing and support ZIP workflow are implemented and actively used for regression evidence |
| Discord notifications / Rich Presence | `█████████████████░░░` **85%** | Discord bot notifications and Rich Presence are implemented; further event/media wiring remains |
| Direct 3DS screenshot pipeline | `██████████░░░░░░░░░░` **50%** | PC image pipeline exists; direct framebuffer transport is not yet implemented in the current Pokebot-Luma bridge |
| Block list | `██████████████████░░` **90%** | Block-list feature is present and integrated with keeper/continuation policy; documentation/polish remains |
| Fishing | `████░░░░░░░░░░░░░░░░` **20%** | Encounter data/browser support exists; production Fishing and Chain Fishing automation remain |
| Static encounters | `██████░░░░░░░░░░░░░░` **30%** | Previous ORAS choreography exists for multiple static/portal targets; current RAM-authoritative production engine is not yet wired |
| Postgame starters | `███░░░░░░░░░░░░░░░░░` **15%** | Johto/Unova/Sinnoh starters are in the browser; automation is not yet wired |
| Language validation | `███░░░░░░░░░░░░░░░░░` **15%** | English hardware-verified; other game languages remain unverified |
| Release / docs | `███████████████████░` **95%** | README/setup/release structure is largely complete and is being kept current alongside development |

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
>
> **Current controller update:** newer acknowledged-controller builds place RAM and acknowledged input commands on **UDP 4952**. The older v0p4 `4952 RAM + 4950 InputRedirection` description is retained below as project/setup history, but current development packages use the acknowledged controller path described in the August 23 update section.

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

Additional current acknowledged-controller proof:

- `INPUT_PING`, acknowledged pulse, status, emergency `RELEASE_ALL`, native touch pulse and retained HID latch are hardware-proven on UDP `4952`.
- The tested controller reports protocol v1, capability flags `0x000000CF`, runtime `0x00000001`, neutral HID `0xFFF`, and bounded hold/settle limits.
- The retained reset chord `L + R + START + SELECT` is sent as a latched active-low HID value and explicitly released, removing the unreliable short-pulse reset behaviour seen during migration.
- Current starter regression runs completed repeated first-attempt resets without the earlier reset-chord misses.

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

### Current acknowledged controller path

The newer controller path is additive to the read-only bridge protocol and is the active path in current development builds. It uses the same UDP `4952` service as RAM authority while preserving the rule that game RAM remains read-only.

Current acknowledged input commands are:

```text
5  INPUT_PING
6  INPUT_PULSE
7  INPUT_STATUS
8  RELEASE_ALL
9  INPUT_TOUCH_PULSE
10 INPUT_HID_LATCH
```

The retained HID latch is used for inputs that must remain physically present long enough for ORAS to recognise them reliably, most importantly the reset chord. `RELEASE_ALL` is always available as an explicit neutralisation path.

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
| Acknowledged controller / retained HID latch | ✅ Hardware-proven | ✅ Shared controller path proven through OR starter/reset testing |
| Native touch pulse on current controller | ✅ Hardware-proven | 🟡 Wider hunt-method parity pass pending |
| Party Pokémon live dashboard order | 🟡 Pokémon data reads correctly, but manual party reordering may not refresh until the game is restarted | 🟡 Same display-only subsystem; hunt shiny authority is unaffected |

Omega Ruby completed the finite automated starter reset validation **6/6**, including two successful cycles for each Hoenn starter. The three locked starter modules are shared between the two ORAS profiles rather than duplicated.

Current acknowledged-controller starter regression has also produced repeated first-attempt reset success on the retained reset chord. Treecko received a targeted early-battle probe timing improvement while preserving the same final RAM authority boundary.

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

> [!NOTE]
> The networking block immediately above documents the earlier v0p4 split transport. Current acknowledged-controller development builds use UDP `4952` for both read-only RAM requests and acknowledged controller commands while keeping the two responsibilities logically separate.

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
- [x] acknowledged controller protocol on UDP 4952 (`INPUT_PING`, pulse, status, release, touch, retained HID latch)
- [x] retained HID reset chord + explicit release
- [x] current-controller Hoenn starter regression across Treecko/Torchic/Mudkip
- [x] Treecko early-battle timing tune without moving the RAM authority deadline
- [x] current-controller native touch pulse used by hunt actions
- [x] Horde post-battle Sweet Scent re-arm
- [x] Cave stable-grid authority for areas where duplicate world coordinates are not land-style settled
- [x] Cave Run longer 600 ms B+direction movement with locally proven corridor envelope
- [x] Cave Run post-battle re-arm
- [x] Cave Acro Bunny initial/post-battle re-arm
- [x] Birch bag reset false-hold tolerance for an explicitly zero secondary coordinate copy
- [x] Party monitor isolated into display-only refresh/discovery work so it cannot affect hunt shiny authority
- [ ] integrated Pokebot-Luma short Wild regression
- [ ] integrated Pokebot-Luma starter endurance regression
- [ ] add Pokebot-Luma direct framebuffer transport for Discord screenshots
- [ ] Omega Ruby-specific Horde/Cave/Surf hardware parity on the current controller path
- [ ] live Party Pokémon order refresh without restarting ORAS
- [ ] Johto postgame starter automation
- [ ] Unova postgame starter automation
- [ ] Sinnoh postgame starter automation
- [ ] Surf/Fishing production automation
- [ ] Chain Fishing production automation
- [ ] static encounter / portal production automation
- [ ] DexNav hunt automation
- [ ] Rock Smash production automation
- [ ] shared shiny Auto Capture engine
- [ ] Horde shiny Auto Capture front-end that protects the shiny slot before capture

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
- ✅ UDP 4952 acknowledged controller path in current development builds
- ✅ retained HID reset chord / explicit release
- ✅ native acknowledged touchscreen pulse
- ✅ Windows Qt dashboard

### Not claimed yet
- ❌ emulator support wont ever be supported by myself i dont have the means to port it to emulator
- ❌ non-English game languages
- ❌ full integrated-hunt regression on the new Pokebot-Luma transport
- ❌ production postgame Johto/Unova/Sinnoh starter automation
- ❌ production static hunts
- ❌ production Fishing
- ❌ production DexNav automation
- ❌ production Auto Capture
- ❌ fully live Party Pokémon dashboard order after an in-game reorder
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

---

## August 23, 2026 — current hardware state and fixes

This section is additive to the development history above. It records the newer acknowledged-controller migration and the current `v0p42Z` desktop baseline without removing the earlier v0p4 history.

### Acknowledged controller migration

The desktop bot has moved from fire-and-forget input toward an acknowledged Pokebot-Luma controller on UDP `4952`.

The current protocol keeps RAM read-only while adding controller-only commands for pulse, status, emergency release, native touch and retained HID latch. The retained latch is especially important for the ORAS reset chord because the game must observe `L + R + START + SELECT` long enough to trigger a reliable reset.

The migration initially exposed a real problem: an acknowledged short reset pulse could be accepted by the firmware without producing a game-level reset. The reset path was therefore changed to:

```text
pre-neutral
→ INPUT_HID_LATCH(reset chord)
→ retain chord
→ RELEASE_ALL
→ verify game/PID transition
```

That change removed the earlier reset-chord misses in targeted starter validation.

### Current Hoenn starter reliability

The three starter modules remain intentionally frozen as separate proven pieces rather than being merged into one giant macro.

Recent acknowledged-controller hardware validation included repeated first-attempt reset cycles for all three starters. Treecko also received a narrow timing improvement that moved its early battle probe forward while preserving the original final RAM authority deadline.

Observed development timing remains approximately:

- Torchic: ~35.5 s/reset
- Mudkip: ~36.7 s/reset
- Treecko: ~37.3 s/reset after the targeted early-battle tune

These are observed development rates, not guaranteed hardware performance.

### Birch bag false-HOLD fix

A reset regression was found where the game was already at Professor Birch's bag but the secondary world-coordinate copy temporarily reported exactly `[0.0, 0.0]`.

The reset validator now accepts that narrow state only when all of the following are true:

- battle is inactive
- the correct Route 101/Birch zone is present
- the primary world coordinate is exactly the proven bag coordinate
- the secondary coordinate is either the same proven coordinate or explicitly all-zero

A non-zero conflicting secondary coordinate still fails closed.

### Horde post-battle re-arm

Sweet Scent Horde automation now performs an explicit post-battle field re-arm before opening the menu for the next Sweet Scent use.

The re-arm waits for field authority, allows the game to settle, then confirms battle inactivity and the same validated grid before continuing. This fixed the earlier tendency to act too quickly immediately after returning from a Horde battle.

### Cave stable-grid authority

Fiery Path testing showed that cave movement cannot always use the exact same land-style `settled_tile_center` rule as outdoor grass.

Cave authority now uses:

- exact zone
- duplicate-coordinate agreement where valid
- repeated logical-grid stability
- land-style tile-centre settle as diagnostic rather than mandatory authority

This removed false preflight HOLDs before cave movement had even started.

### Cave Run movement length and corridor proof

The initial Cave Run implementation was visually too short, often producing only roughly three steps at a time, and could false-HOLD after returning from battle.

The newer Cave Run path now locally proves a wider corridor around its anchor before using the longer movement burst. Once that local envelope is proven, the normal long action uses a `600 ms` B+direction hold and accepts the resulting movement only when the RAM endpoint remains inside the previously proven corridor.

A post-battle re-arm also waits for the cave field to settle before the next movement action. Blind movement retransmission is not used.

### Cave Acro Bunny re-arm

Cave Acro Bunny retains its proven stationary B-latch behaviour, but now performs explicit initial and post-battle re-arm checks before latching B again.

The re-arm requires battle inactivity and the same anchor grid. The actual retained-B input pattern remains unchanged.

### Party Pokémon panel — current known issue

The Party Pokémon dashboard has been isolated from hunt authority and rewritten several times as a display-only monitor.

What is already proven:

- the bot can read valid party PK6 data
- species/identity data is correct
- the dashboard can populate the six party cards
- multiple stale/cached party copies and candidate runtime structures have been identified

The remaining issue is **live party order**. If Pokémon are manually reordered in the ORAS party menu, the dashboard may continue showing the previous order until the game is closed/reopened. That strongly indicates the display monitor is still not following the exact runtime order structure that ORAS updates immediately in-menu.

This is deliberately treated as a **UI/display issue only**. Starter shiny authority, Wild shiny authority, Horde authority, Cave authority, Pokérus safety and the reset controller do not depend on the Party panel's visible ordering.

The rest of the current Alpha Sapphire validation is considered stable enough to freeze while Party work remains isolated.

### Omega Ruby parity pass next

The next broad hardware validation is an Omega Ruby pass across the already-implemented non-starter hunt methods, especially:

- normal Wild Walk/Run
- Hordes and Sweet Scent Hordes
- Cave Walk/Run/Acro Bunny
- Surf/Ocean

The purpose is parity validation, not redesign. Alpha Sapphire-proven behaviour should remain frozen unless Omega Ruby produces specific evidence of a game-profile difference.

### Remaining ORAS hunt families

After current OR/AS parity is frozen, the main production hunt families still to build or port are:

- Fishing and Chain Fishing
- Static encounters
- Mirage Spot / portal legendaries
- Johto / Unova / Sinnoh postgame starters
- DexNav
- Rock Smash
- selected gift/fossil reset hunts

Previous image-era ORAS work already developed successful choreography for several static/portal targets, including Spiritomb, Kecleon, Regirock, Regice, Registeel, Heatran, Reshiram, Zekrom, Terrakion and Virizion. That choreography can be reused while replacing visual shiny authority with the current RAM-authoritative PK6 decision.

### Auto Capture — planned shared subsystem

Auto Capture is planned as a shared subsystem rather than a separate macro for every hunt method.

The intended safety rule is:

```text
RAM proves keeper shiny
→ normal hunt continuation is disabled
→ capture target is locked by species/PID/EC
→ capture controller acts only while that identity remains valid
→ confirmed catch stops the hunt
→ any uncertainty falls back to SHINY HOLD
```

Single-opponent capture will be developed first. Horde capture will use a specialised front-end that protects the shiny Horde slot, removes only validated non-shiny opponents, then hands the surviving shiny to the same shared capture engine.

Auto Capture is **not yet production implemented** and is not counted as completed work in the progress table.

---

## ORAS `code.ips` communication-error patch

The per-game `code.ips` files are included because Pokémon Omega Ruby and Alpha Sapphire can show a **communication error** when remote/InputRedirection-style controller input is used while the game's PSS communication is still active.

Later in the game, this can normally be avoided by opening the **PSS** and disabling PSS communication. During the early-game Route 101 starter sequence, however, the player does **not yet have access to the PSS**, so there is no normal in-game way to turn that communication off before starter automation begins.

The ORAS `code.ips` patch removes/bypasses that communication-error interruption so Pokebot3DS-CFW can use remote controller input during those early hunts without the game stopping on the communication-error message.

There are separate update-1.4 patches for each game:

```text
000400000011C400  -> Omega Ruby 1.4
000400000011C500  -> Alpha Sapphire 1.4
```

The patch is **not** the RAM bridge and is **not** the input controller. It does not generate inputs, decide whether a Pokémon is shiny, change Pokémon data, alter shiny odds, modify encounter generation or provide a game-RAM write path. Its job is specifically to stop the ORAS communication-error path from interrupting automation when PSS communication cannot yet be disabled normally.
