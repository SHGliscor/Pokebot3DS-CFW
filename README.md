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

### Inspiration

Pokebot3DS-CFW takes inspiration from excellent Pokémon automation projects including:

- [pokebot-nds](https://github.com/wyanido/pokebot-nds/)
- [pokebot-gen3](https://github.com/40cakes/pokebot-gen3)
- [PokemonAutomation](https://github.com/PokemonAutomation)

Pokebot3DS-CFW is an independent implementation built around RAM-authoritative Gen 6 shiny hunting, acknowledged 3DS input and real-hardware safety gates.

> [!IMPORTANT]
> **Pokebot3DS-CFW currently targets Pokémon Omega Ruby 1.4 and Pokémon Alpha Sapphire 1.4 on real 3DS hardware.**
>
> English is the currently hardware-verified game language. Other languages remain unverified until separately tested.

Pokebot3DS-CFW is a Windows Qt application paired with a customised Nexus3DS-based `boot.firm`. The firmware exposes a small read-only RAM bridge and an acknowledged HID/touch input bridge on UDP `4952`.

The bot treats validated Pokémon RAM as the source of truth. OCR or image matching is **not** used as shiny authority.

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
| Wild Walk / Run backend | ✅ Hardware proven | ✅ Shared backend enabled |
| Acro Bunny backend | ✅ 10/10 proof | ✅ Shared backend enabled |

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
- [x] OR + AS `code.ips` reset-route patches, this removed the annoying communication error screen when using InputReirection with ORAS
- [x] Wild PK6 authority
- [x] automatic Run after validated non-shiny
- [x] Walk/Run finite Wild proof
- [x] Acro Bunny finite Wild proof
- [x] whole-game terrain database
- [x] ORAS automatic game profiles
- [x] encounter browser
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
- ❌ production Surf/Fishing
- ❌ XY / Gen 7 production support

---

## Disclaimer

Pokebot3DS-CFW is an independent homebrew/automation project. Use it only with real 3DS hardware. Keep backups of your SD card and important save data before testing custom firmware, patches or automation.
