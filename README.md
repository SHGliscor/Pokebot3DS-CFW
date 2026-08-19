# POKEBOT3DS-CFW — Windows only unfortunately 

<p align="center">
  <img src="./POKEBOT3DS-CFW-icon.png" width="220" alt="POKEBOT3DS-CFW">
</p>

<p align="center">
  <strong>Standalone Windows build for Pokémon Alpha Sapphire</strong>
</p>

<p align="center">
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/releases/latest"><img src="https://img.shields.io/badge/DOWNLOAD%20LATEST%20EXE-16a34a?style=for-the-badge&logo=windows11&logoColor=white" alt="Download latest EXE"></a>
  <a href="#first-time-3ds-setup"><img src="https://img.shields.io/badge/SETUP%20GUIDE-2563eb?style=for-the-badge&logo=readthedocs&logoColor=white" alt="Setup guide"></a>
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/issues/new?template=bug_report.yml"><img src="https://img.shields.io/badge/REPORT%20BUG-dc2626?style=for-the-badge&logo=github&logoColor=white" alt="Report a bug"></a>
  <a href="#project-progress"><img src="https://img.shields.io/badge/PROJECT%20PROGRESS-7c3aed?style=for-the-badge&logo=githubactions&logoColor=white" alt="Project progress"></a>
</p>

<p align="center">
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/issues/new?template=feature_request.yml"><img src="https://img.shields.io/badge/REQUEST%20A%20FEATURE-f59e0b?style=flat-square&logo=github&logoColor=white" alt="Request a feature"></a>
  <a href="#building-the-windows-exe"><img src="https://img.shields.io/badge/BUILD%20EXE-0f766e?style=flat-square&logo=python&logoColor=white" alt="Build EXE"></a>
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/issues"><img src="https://img.shields.io/github/issues/SHGliscor/Pokebot3DS-CFW?style=flat-square" alt="Open issues"></a>
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/stargazers"><img src="https://img.shields.io/github/stars/SHGliscor/Pokebot3DS-CFW?style=flat-square" alt="GitHub stars"></a>
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/network/members"><img src="https://img.shields.io/github/forks/SHGliscor/Pokebot3DS-CFW?style=flat-square" alt="GitHub forks"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Game-Alpha%20Sapphire-2563eb?style=flat-square" alt="Alpha Sapphire only">
  <img src="https://img.shields.io/badge/Language-English%20Verified-16a34a?style=flat-square" alt="English verified">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows11&logoColor=white&style=flat-square" alt="Windows">
  <img src="https://img.shields.io/badge/CFW-Nexus3DS-7c3aed?style=flat-square" alt="Nexus3DS CFW">
  <img src="https://img.shields.io/badge/RAM%20Authority-PK6-0891b2?style=flat-square" alt="RAM authority">
  <img src="https://img.shields.io/badge/Torchic%20code.ips-34%2F34%20PASS-16a34a?style=flat-square" alt="34/34 Torchic code.ips validation">
</p>

### Inspiration

POKEBOT3DS-CFW takes inspiration from excellent automation projects including:

- [pokebot-nds](https://github.com/wyanido/pokebot-nds/)
- [pokebot-gen3](https://github.com/40cakes/pokebot-gen3)
- [PokemonAutomation](https://github.com/PokemonAutomation)

> [!IMPORTANT]
> **POKEBOT3DS-CFW currently supports Pokémon Alpha Sapphire only.**
>
> **English is the only in-game language currently hardware verified.** Other languages remain **UNVERIFIED** until separately tested.

---

## Project progress

### Current Alpha Sapphire starter release — **90%**

```text
██████████████████░░  90%
```

The Alpha Sapphire starter-hunting core is hardware validated. Remaining work in this release scope is mainly standalone EXE validation, release packaging, UI completion and broader stop-point testing.

### Wider POKEBOT3DS-CFW roadmap — **38%**

```text
████████░░░░░░░░░░░░  38%
```

The wider roadmap includes Omega Ruby parity, RAM-based wild hunts, static encounters, additional games and language validation.

> Percentages are roadmap estimates, not automated code-coverage metrics.

| Area | Progress | Status |
|---|---:|---|
| Nexus3DS read-only RAM bridge | **100%** | ✅ Hardware proven |
| Alpha Sapphire RAM mapping | **100%** | ✅ Proven |
| Torchic starter backend | **100%** | ✅ Proven |
| Treecko starter backend | **100%** | ✅ Proven |
| Mudkip starter backend | **100%** | ✅ Proven |
| `code.ips` ON reset route | **100%** | ✅ 34/34 Torchic validation |
| PK6 validation + shiny authority | **100%** | ✅ RAM authoritative |
| Qt dashboard core | **80%** | 🟢 Dashboard / Hunts / Settings live |
| Stats / encounter history | **80%** | 🟢 Core persistence live |
| Immediate Stop behaviour | **75%** | 🟡 Implemented; broader hardware validation pending |
| GitHub/setup documentation | **90%** | 🟢 Main setup flow documented |
| Alpha Sapphire language validation | **14%** | 🟡 English verified; others unverified |
| Omega Ruby RAM parity | **0%** | ⚪ Not started |
| RAM-based wild hunting | **10%** | ⚪ Architecture planned / early authority known |
| RAM-based static hunting | **0%** | ⚪ Deferred |
| XY / Gen 7 support | **0%** | ⚪ Future roadmap |

---

## Do I need Python?

**No — not for the finished Windows EXE release.**

End users do **not** need to install:

- Python
- pip
- PySide6
- Qt
- PyInstaller
- `RUN_REQUIREMENTS.bat`

The finished application uses a PyInstaller **onedir** bundle. Python, PySide6/Qt and the required Python modules are included inside the application folder.

### Keep the whole application folder

```text
POKEBOT3DS-CFW/
├─ POKEBOT3DS-CFW.exe
├─ _internal/
├─ assets/
├─ 3ds_sd/
│  ├─ boot.firm
│  └─ luma/
│     └─ titles/
│        └─ 000400000011C500/
│           └─ code.ips
├─ HOW_TO_USE.txt
└─ README.md
```

Do not remove `_internal` or move only the EXE elsewhere.

---

## Firmware used by POKEBOT3DS-CFW

POKEBOT3DS-CFW does **not** use a stock Luma3DS `boot.firm`.

The supplied firmware is based on **[Nexus3DS](https://github.com/2b-zipper/Nexus3DS)**, with custom POKEBOT3DS-CFW modifications that add a **read-only RAM bridge** for the game.

| Function | Port |
|---|---:|
| Read-only RAM bridge | UDP **4952** |
| Nexus3DS/Luma-derived InputRedirection | UDP **4950** |

RAM is the authority for Pokémon encounter and shiny decisions. OCR/image shiny detection is not used.

---

## First-time 3DS setup

### 1. Back up your SD card

Back up important SD-card files and save data before replacing firmware or adding patches.

### 2. Install the supplied `boot.firm`

Copy:

```text
3ds_sd\boot.firm
```

to:

```text
SD:\boot.firm
```

Back up the previous `boot.firm` first DO NOT DELETE IT RENAME IF NEEDED!.

### 3. Install the Alpha Sapphire `code.ips`

Copy:

```text
3ds_sd\luma\titles\000400000011C500\code.ips
```

to:

```text
SD:\luma\titles\000400000011C500\code.ips
```

The current patch is for **Pokémon Alpha Sapphire only**.

### 4. Enable game patching

1. Fully power off the 3DS.
2. Hold **SELECT**.
3. While holding SELECT, power on the 3DS.
4. Enable **game patching** in the Nexus3DS/Luma-derived configuration menu.
5. Save and exit.

### 5. Start InputRedirection

1. Start Pokémon Alpha Sapphire.
2. Open Rosalina with **L + D-Pad Down + Select**.
3. Open **Miscellaneous options**.
4. Start **InputRedirection**.
5. Exit Rosalina and return to the game.

---

## Starting POKEBOT3DS-CFW

For the finished EXE release, simply launch:

```text
POKEBOT3DS-CFW.exe
```

The application permanently uses the **standard native Windows frame** with native minimise, maximise/restore, close, title-bar dragging and edge/corner resizing.

---

## Configure the bot

In **Settings**, confirm:

- 3DS IP address
- RAM bridge port: `4952`
- InputRedirection port: `4950`
- whether `code.ips` is ON or OFF

### `code.ips` ON

```text
Reset
→ Title
→ Continue
→ Field / Birch Bag
```

Communication-error dismissal is disabled in this mode. An unexpected communication-error state causes a safety HOLD rather than blind dismissal inputs.

### `code.ips` OFF

```text
Reset
→ Title
→ Continue
→ Communication Error
→ RAM-confirmed dismissal
→ Field / Birch Bag
```

The bot uses bounded RAM-gated communication-error recovery.

---

## Current validated starter results

| Starter | Species | Validation | Status |
|---|---:|---:|---|
| Treecko | #252 | 10/10 baseline | ✅ |
| Torchic | #255 | 10/10 baseline | ✅ |
| Mudkip | #258 | 10/10 baseline | ✅ |

The current `code.ips` ON reset-route policy later completed a **34/34 Torchic hardware validation run** with:

- 34 completed encounters
- 34 PASS
- 0 safety HOLDs
- 0 failures
- 0 transport retries
- 35/35 `Field + PSS` Birch-bag authority probes passing
- mean encounter time around **41.88 seconds**
- approximately **86 encounters/hour**

---

## RAM shiny safety

```text
valid non-shiny  → automation may continue
shiny            → ABSOLUTE HOLD
invalid data     → HOLD
wrong species    → HOLD
checksum error   → HOLD
TID/SID mismatch → HOLD
RAM/state error  → HOLD
```

A validated RAM-authoritative shiny must never be intentionally reset over.

---

## STOP behaviour

**STOP is immediate.**

When Stop is pressed:

- cancellation is requested immediately
- controller state is forced back to neutral
- cancellable route sleeps and state waits stop
- the bot does not deliberately finish the cycle
- the bot does not deliberately return to the Birch bag first

A bounded RAM request already waiting for a network reply may still need to reach its configured timeout, but no new gameplay input should be authorized after Stop.

---

## Language support

| Language | Status |
|---|---|
| English | ✅ **VERIFIED** |
| Japanese | ⚪ Unverified |
| French | ⚪ Unverified |
| German | ⚪ Unverified |
| Italian | ⚪ Unverified |
| Spanish | ⚪ Unverified |
| Korean | ⚪ Unverified |

---

## Roadmap

### Next

- [ ] Validate immediate Stop at multiple awkward points
- [ ] Build and clean-machine test the standalone Windows EXE
- [ ] Publish the first GitHub EXE release
- [ ] Finish Statistics page
- [ ] Finish Tools page
- [ ] Finish Testing / Support page

### Omega Ruby

- [ ] Detect Omega Ruby title/process
- [ ] Prove Birch-bag anchors
- [ ] Prove TID/SID
- [ ] Prove party0
- [ ] Prove Poke3Select states/slots
- [ ] Prove battle-state mapping
- [ ] Torchic 1 → 10
- [ ] Treecko 1 → 10
- [ ] Mudkip 1 → 10

### Wild hunts

- [ ] Manual RAM authority observations
- [ ] Fresh encounter boundary
- [ ] Shiny absolute HOLD
- [ ] Automatic Run after validated non-shiny
- [ ] Movement-only module
- [ ] Grass containment / map geometry
- [ ] Finite 1 → 5 → 10 → 30–50 validation
- [ ] Unlimited mode

### Later

- [ ] XY
- [ ] Sun / Moon
- [ ] Ultra Sun / Ultra Moon
- [ ] RAM-based static encounters
- [ ] Additional language validation

---

## If the bot HOLDs

A safety HOLD is intentional. Export and retain the support ZIP so the exact failing RAM/state gate can be diagnosed.

---

## Windows SmartScreen / antivirus

Unsigned self-built applications may trigger a Windows SmartScreen or antivirus reputation warning. That is separate from whether Python is installed.

---

## Standalone EXE validation

Before publishing an EXE release, test the **exact finished distribution folder** on a clean Windows system or VM with no Python installed.

- [ ] EXE launches without Python installed
- [ ] shiny Kyogre icon appears on EXE/title bar/taskbar/Alt+Tab
- [ ] Dashboard opens
- [ ] Hunts page opens
- [ ] Settings page opens
- [ ] settings persist
- [ ] RAM bridge connection works
- [ ] InputRedirection works
- [ ] assets and shiny sound load
- [ ] support ZIP export works
- [ ] Alpha Sapphire starter hunt starts
- [ ] STOP works
- [ ] no missing-module or missing-DLL error occurs

---

## Compatibility

### Currently supported

- ✅ Pokémon Alpha Sapphire
- ✅ Title ID `000400000011C500`
- ✅ English language
- ✅ Treecko / Torchic / Mudkip starter hunts
- ✅ Custom Nexus3DS RAM bridge
- ✅ InputRedirection UDP 4950
- ✅ RAM bridge UDP 4952
- ✅ `code.ips` ON reset route
- ✅ Windows Qt dashboard

### Not yet supported / verified

- ❌ Omega Ruby
- ❌ XY
- ❌ Sun / Moon
- ❌ gen2 VC G/S/C
- ❌ Ultra Sun / Ultra Moon
- ❌ non-English language modes
- ❌ production wild-hunt automation
- ❌ production static-hunt automation

---

## Disclaimer

POKEBOT3DS-CFW is an independent homebrew/automation project. Use it only with you actual 3DS hardware this is NOT made for an EMULATOR, Keep backups of your SD card and important save data before testing custom firmware, patches or automation.
