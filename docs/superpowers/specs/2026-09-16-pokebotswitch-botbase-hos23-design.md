# PokebotSwitch Botbase HOS23 Design

## Goal
Build a purpose-built Nintendo Switch sysmodule for PokebotSwitch targeting the user's hardware-confirmed HOS 23.0.0 + Atmosphere 1.12.0 experimental direct-Fusee environment. The eventual bridge must provide the controller and process-memory operations required by the existing FRLG bot and later ArcDelta melonDS/HeartGold integration.

## Constraints
- Do not modify the known-good Atmosphere package itself.
- Do not reuse Koi's program ID 0x430000000000000B for the new module.
- Stage A must be independently installable/removable as one atmosphere/contents folder.
- Stage A performs no USB, HID, filesystem, network, capture, VI, process-debug, or game-memory work.
- A successful GitHub build proves compilation only. Hardware compatibility requires the user's Switch to reach HOME after installation.
- Later stages add one subsystem at a time: USB/ping, HID, process discovery/RAM, then compatibility commands.
- Preserve the existing FRLG PC-side command semantics where practical so the bot requires minimal changes.

## Architecture
The botbase is split into a minimal lifecycle core and optional subsystems. The lifecycle core owns only process startup and an idle loop. Each later subsystem is introduced separately so a HOS23 regression can be attributed to a specific service/capability rather than the complete legacy sys-botbase initialization path.

Stage A uses a new PokebotSwitch-specific program ID and a deliberately narrow NPDM. It initializes no Horizon service explicitly and sleeps indefinitely. Packaging produces an SD overlay with exefs.nsp and flags/boot2.flag plus build metadata.

## Validation ladder
1. Stage A: module starts/idles; HOME must boot.
2. Stage B: USB transport plus ping/version.
3. Stage C: controller injection.
4. Stage D: application process discovery and read-only RAM access.
5. Stage E: required write/absolute/main/heap compatibility commands.
6. Stage F: existing FRLG bot validation.
7. Stage G: ArcDelta melonDS process-memory discovery and NDS RAM mapping.

## Failure handling
No Stage-A fatalThrow path is permitted. If the minimal module prevents HOME boot, investigate NPDM/resource allocation/program configuration before adding any services. Each subsequent stage must retain the previous stage's hardware pass before additional capabilities are introduced.

## Build strategy
Build remotely with GitHub Actions using current devkitA64/libnx. Keep work isolated on the existing HOS23 development branch; do not modify main. Upload an SD-ready artifact in its own top-level folder.