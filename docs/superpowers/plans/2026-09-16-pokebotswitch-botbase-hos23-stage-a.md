# PokebotSwitch Botbase HOS23 Stage A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce an SD-ready minimal PokebotSwitch sysmodule that starts and idles on HOS23 without initializing bot functionality.

**Architecture:** A standalone sysmodule with a narrow NPDM and no explicit Horizon service initialization. The executable enters a permanent sleep loop. GitHub Actions builds it with current devkitA64/libnx and packages one atmosphere/contents folder for hardware testing.

**Tech Stack:** C/C++, devkitA64, libnx, npdmtool, GitHub Actions

**Spec:** `docs/superpowers/specs/2026-09-16-pokebotswitch-botbase-hos23-design.md`

## Global Constraints
- Target HOS 23.0.0 + Atmosphere 1.12.0 experimental direct-Fusee baseline.
- New module must not use Koi program ID `0x430000000000000B`.
- No USB, HID, filesystem, network, capture, VI, process-debug, or game-memory initialization in Stage A.
- No `fatalThrow` path in Stage A.
- Build success is compile-only; HOME boot on the user's Switch is the hardware acceptance test.
- Keep changes off `main`.

---

### Task 1: Minimal Stage-A sysmodule

**Files:**
- Create: `switch/pokebotswitch-botbase/Makefile`
- Create: `switch/pokebotswitch-botbase/source/main.c`
- Create: `switch/pokebotswitch-botbase/pokebotswitch-botbase.json`

**Interfaces:**
- Consumes: devkitA64/libnx sysmodule build environment.
- Produces: `pokebotswitch-botbase.nsp` suitable for Atmosphere `exefs.nsp` installation.

- [ ] Create a minimal source whose only runtime behavior is an indefinite `svcSleepThread` loop.
- [ ] Define a new fixed PokebotSwitch program ID and minimal kernel capabilities needed for startup/sleep.
- [ ] Add a Makefile that builds the sysmodule and NPDM without linking legacy Koi source.
- [ ] Compile in the devkitPro environment and correct only compile/package errors; do not add runtime subsystems.
- [ ] Commit the independently buildable Stage-A source.

### Task 2: Remote build and SD overlay

**Files:**
- Create: `.github/workflows/build-pokebotswitch-botbase-hos23-stage-a.yml`

**Interfaces:**
- Consumes: Stage-A source from Task 1.
- Produces: artifact `PokebotSwitch-Botbase-HOS23-StageA` containing `atmosphere/contents/<new-program-id>/exefs.nsp`, `flags/boot2.flag`, and `BUILD_INFO.txt`.

- [ ] Add push/manual GitHub Actions triggers for the HOS23 development branch.
- [ ] Build with the devkitPro devkitA64 container.
- [ ] Fail the job if the expected NSP is absent.
- [ ] Package only the new contents folder and metadata into its own top-level directory.
- [ ] Upload the artifact.
- [ ] Verify the Actions job and artifact both complete successfully.

### Task 3: Hardware acceptance gate

**Files:**
- No source changes unless hardware testing fails.

**Interfaces:**
- Consumes: Stage-A SD overlay.
- Produces: PASS/FAIL evidence for HOS23 HOME boot with the minimal module installed.

- [ ] User copies only the new contents folder onto the known-good SD baseline.
- [ ] User boots via the currently working Hekate -> Payloads -> fusee.bin path.
- [ ] Record PASS only if HOME appears normally.
- [ ] If FAIL, capture Atmosphere error/program information and modify only Stage-A program configuration/NPDM until this gate passes.
- [ ] Do not begin USB Stage B until Stage A has a hardware PASS.