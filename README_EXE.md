# POKEBOT3DS-CFW — Windows EXE Release

<p align="center">
  <img src="./POKEBOT3DS-CFW-icon.png" width="220" alt="POKEBOT3DS-CFW">
</p>

<p align="center">
  <strong>Standalone Windows build for Pokémon Alpha Sapphire</strong>
</p>

<p align="center">
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/releases/latest"><img src="https://img.shields.io/badge/⬇%20DOWNLOAD%20LATEST%20EXE-16a34a?style=for-the-badge" alt="Download latest EXE"></a>
  <a href="#first-time-3ds-setup"><img src="https://img.shields.io/badge/📖%20SETUP%20GUIDE-2563eb?style=for-the-badge" alt="Setup guide"></a>
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/issues/new?template=bug_report.yml"><img src="https://img.shields.io/badge/🐛%20REPORT%20BUG-dc2626?style=for-the-badge" alt="Report a bug"></a>
  <a href="#project-progress"><img src="https://img.shields.io/badge/📊%20PROJECT%20PROGRESS-7c3aed?style=for-the-badge" alt="Project progress"></a>
</p>

<p align="center">
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/issues/new?template=feature_request.yml"><img src="https://img.shields.io/badge/💡%20REQUEST%20A%20FEATURE-f59e0b?style=flat-square" alt="Request a feature"></a>
  <a href="#building-the-windows-exe"><img src="https://img.shields.io/badge/🛠%20BUILD%20EXE-0f766e?style=flat-square" alt="Build EXE"></a>
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/issues"><img src="https://img.shields.io/github/issues/SHGliscor/Pokebot3DS-CFW?style=flat-square" alt="Open issues"></a>
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/stargazers"><img src="https://img.shields.io/github/stars/SHGliscor/Pokebot3DS-CFW?style=flat-square" alt="GitHub stars"></a>
  <a href="https://github.com/SHGliscor/Pokebot3DS-CFW/network/members"><img src="https://img.shields.io/github/forks/SHGliscor/Pokebot3DS-CFW?style=flat-square" alt="GitHub forks"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Game-Pokémon%20Alpha%20Sapphire-2563eb?style=flat-square" alt="Alpha Sapphire only">
  <img src="https://img.shields.io/badge/Language-English%20Verified-16a34a?style=flat-square" alt="English verified">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows11&logoColor=white&style=flat-square" alt="Windows">
  <img src="https://img.shields.io/badge/CFW-Nexus3DS-7c3aed?style=flat-square" alt="Nexus3DS CFW">
  <img src="https://img.shields.io/badge/RAM%20Authority-PK6-0891b2?style=flat-square" alt="RAM authority">
  <img src="https://img.shields.io/badge/Torchic%20code.ips-34%2F34%20PASS-16a34a?style=flat-square" alt="34/34 Torchic code.ips validation">
</p>

> [!IMPORTANT]
> **This release is currently for Pokémon Alpha Sapphire only.**
>
> **English is the only in-game language currently hardware verified.**
> Other languages are not yet claimed as supported.

---

## Do I need Python?

**No.**

If you downloaded the finished **POKEBOT3DS-CFW Windows EXE release**, you do **not** need to install:

- Python
- pip
- PySide6
- Qt
- PyInstaller
- `RUN_REQUIREMENTS.bat`
- any Python package from `requirements.txt`

The release is built with **PyInstaller in `onedir` mode**. The Python interpreter, PySide6/Qt libraries, and the Python modules used by POKEBOT3DS-CFW are bundled inside the application folder.

### Important: keep the whole folder

POKEBOT3DS-CFW is intentionally distributed as a folder-based application.

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

**Do not move `POKEBOT3DS-CFW.exe` out of this folder and do not delete `_internal`.**

---

## Project progress

### Current Alpha Sapphire starter release

**90%**

```text
██████████████████░░  90%
```

The starter-hunting core is hardware validated. Remaining work in this release scope is mainly final EXE validation, GitHub/release polish, and further UI pages.

### Wider POKEBOT3DS-CFW roadmap

**38%**

```text
████████░░░░░░░░░░░░  38%
```

The wider roadmap includes Omega Ruby parity, RAM-based wild hunts, static encounters, additional games, and broader language validation.

> Percentages are roadmap estimates, not automated code-coverage metrics.

| Area | Progress | Status |
|---|---:|---|
| Nexus3DS read-only RAM bridge | **100%** | ✅ Hardware proven |
| Alpha Sapphire RAM mapping | **100%** | ✅ Proven |
| Torchic starter backend | **100%** | ✅ 10/10 baseline proven |
| Treecko starter backend | **100%** | ✅ 10/10 baseline proven |
| Mudkip starter backend | **100%** | ✅ 10/10 baseline proven |
| `code.ips` ON reset route | **100%** | ✅ 34/34 Torchic validation |
| PK6 validation + shiny authority | **100%** | ✅ RAM authoritative |
| Qt dashboard core | **80%** | 🟢 Dashboard / Hunts / Settings live |
| Stats / encounter history | **80%** | 🟢 Core persistence live |
| Immediate Stop behaviour | **75%** | 🟡 Implemented; wider hardware stop-point validation pending |
| GitHub/setup documentation | **90%** | 🟢 Main setup flow documented |
| Alpha Sapphire language validation | **14%** | 🟡 English verified; others unverified |
| Omega Ruby RAM parity | **0%** | ⚪ Not started |
| RAM-based wild hunting | **10%** | ⚪ Architecture planned / early authority known |
| RAM-based static hunting | **0%** | ⚪ Deferred |
| XY / Gen 7 support | **0%** | ⚪ Future roadmap |

---

## What you still need

The standalone EXE removes the need for Python and PC-side dependency setup.

You still need:

- a compatible Nintendo 3DS with the required custom firmware setup
- the supplied **custom Nexus3DS-based `boot.firm`**
- the supplied Pokémon Alpha Sapphire `code.ips`
- game patching enabled
- InputRedirection enabled
- the PC and 3DS on the same local network
- Pokémon Alpha Sapphire
- the correct 3DS IP address entered in POKEBOT3DS-CFW

The EXE does **not** automatically install `boot.firm` or `code.ips`.

Those remain manual SD-card setup files.

---

## Firmware used by POKEBOT3DS-CFW

POKEBOT3DS-CFW does **not** use a stock Luma3DS `boot.firm`.

The supplied firmware is based on **Nexus3DS CFW**, with custom POKEBOT3DS-CFW modifications that add a **read-only RAM bridge** for the game.

| Function | Port |
|---|---:|
| POKEBOT3DS-CFW read-only RAM bridge | UDP **4952** |
| Nexus3DS/Luma-derived InputRedirection | UDP **4950** |

RAM is used as the authority for Pokémon encounter and shiny decisions.

The bot does not use OCR or image recognition as shiny authority.

---

## First-time 3DS setup

### 1. Back up your SD card

Before replacing firmware or adding patches, make a backup of important SD-card files and save data.

### 2. Install the supplied `boot.firm`

Copy:

```text
3ds_sd\boot.firm
```

to:

```text
SD:\boot.firm
```

Back up the previous `boot.firm` first.

### 3. Install the Alpha Sapphire patch

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
3. While still holding SELECT, power on the 3DS.
4. In the Nexus3DS/Luma-derived configuration menu, enable **game patching**.
5. Save and exit.

### 5. Start InputRedirection

1. Start Pokémon Alpha Sapphire.
2. Open Rosalina using **L + D-Pad Down + Select**.
3. Open **Miscellaneous options**.
4. Start **InputRedirection**.
5. Exit Rosalina and return to the game.

---

## Starting POKEBOT3DS-CFW

There is no dependency installer to run for the finished EXE release.

Simply double-click:

```text
POKEBOT3DS-CFW.exe
```

The application uses the standard native Windows frame with:

- minimise
- maximise / restore
- close
- normal title-bar dragging
- normal window resizing

---

## Configure the bot

In **Settings**, confirm:

- your 3DS IP address
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

Communication-error dismissal is disabled in this mode.

### `code.ips` OFF

```text
Reset
→ Title
→ Continue
→ Communication Error
→ RAM-confirmed dismissal
→ Field / Birch Bag
```

---

## Current validated starter results

| Starter | Species | Baseline validation | Status |
|---|---:|---:|---|
| Treecko | #252 | 10/10 | ✅ |
| Torchic | #255 | 10/10 | ✅ |
| Mudkip | #258 | 10/10 | ✅ |

The current `code.ips` ON reset-route policy also completed a later **34/34 Torchic hardware validation run** with:

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

POKEBOT3DS-CFW uses validated PK6 data from game RAM.

```text
valid non-shiny  → automation may continue
shiny            → absolute HOLD
invalid data     → HOLD
wrong species    → HOLD
checksum error   → HOLD
TID/SID mismatch → HOLD
RAM/state error  → HOLD
```

---

## STOP behaviour

**STOP is immediate.**

When Stop is pressed:

- cancellation is requested immediately
- controller state is forced back to neutral
- cancellable route sleeps and state waits stop
- the bot does not deliberately finish the cycle
- the bot does not deliberately return to the Birch bag first

If a bounded UDP RAM request is already waiting for a network reply, the worker may need to reach that request's configured timeout before it fully exits, but no new gameplay input should be authorized after Stop.

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

## Building the Windows EXE

For developers building from source, use:

```bat
BUILD_EXE.bat
```

The finished standalone application is created at:

```text
dist\POKEBOT3DS-CFW\POKEBOT3DS-CFW.exe
```

The public EXE release bundles Python and PySide6, so end users do **not** need to install Python or run `RUN_REQUIREMENTS.bat`.

POKEBOT3DS-CFW uses a PyInstaller **onedir** release. Distribute the complete `dist\POKEBOT3DS-CFW` folder, not the EXE by itself.

---

## Roadmap

### Next

- [ ] Validate immediate Stop at multiple awkward points in the reset/hunt cycle
- [ ] Build and clean-machine test the standalone Windows EXE
- [ ] Publish first GitHub EXE release
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

A safety HOLD is intentional. Use the support/export function and keep the generated support ZIP so the failing RAM/state gate can be diagnosed.

---

## Windows SmartScreen / antivirus

Unsigned self-built applications may trigger a Windows SmartScreen warning or antivirus reputation check. That is separate from whether Python is installed.

Future releases can add Windows code signing if desired.

---

## Release validation requirement

Before publishing a new EXE build, test the **exact finished release folder** on a clean Windows system or virtual machine that does **not have Python installed**.

Minimum smoke test:

- [ ] `POKEBOT3DS-CFW.exe` launches with no Python installed
- [ ] shiny Kyogre icon appears on the EXE
- [ ] icon appears in the native title bar
- [ ] icon appears in the taskbar / Alt+Tab
- [ ] Dashboard opens
- [ ] Hunts page opens
- [ ] Settings page opens
- [ ] settings persist
- [ ] RAM bridge connection test works
- [ ] InputRedirection works
- [ ] assets and shiny sound load
- [ ] support ZIP export works
- [ ] Alpha Sapphire starter hunt can start
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
- ❌ Ultra Sun / Ultra Moon
- ❌ non-English language modes
- ❌ production wild-hunt automation
- ❌ production static-hunt automation

---

## Disclaimer

POKEBOT3DS-CFW is an independent homebrew/automation project.

Use it only with hardware, game copies and save data you are authorised to modify or automate. Always keep backups of your SD card and important save data before testing custom firmware, patches or automation.
