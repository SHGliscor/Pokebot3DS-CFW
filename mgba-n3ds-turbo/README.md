# Pokebot3DS-CFW — mGBA N3DS Bot Turbo v0p1

This is an isolated performance test for the Nintendo New 3DS mGBA frontend. It is **not** a replacement for the hardware-passed Pokebot3DS-CFW Gen 3 bridge build yet.

## What changes

The test patch is pinned to upstream mGBA commit `25ca25612eb806ad3a70f3209ccd93890ea0c2c6`.

During mGBA fast-forward only, it:

- keeps mGBA's existing `osSetSpeedupEnable(true)` New3DS speed request;
- sets GBA frameskip to 3 (render one emulated frame out of four);
- skips the entire Citro3D/GPU presentation path for those three skipped frames;
- discards fast-forward audio before NDSP cache flush/queue work;
- raises `APT_SetAppCpuTimeLimit` from 20 to 30 for the secondary-core work;
- restores the previous frameskip immediately when fast-forward ends, the game is paused, or it unloads.

At roughly 120 emulated FPS the intended display rate is roughly 30 FPS. The performance target is **game execution speed**, not 120 separately rendered images per second.

## Why this should help

Stock 3DS mGBA removes the frame limiter during fast-forward but still calls the 3DS draw path after every emulated frame. That path flushes the GBA framebuffer, performs a synchronous display transfer and submits a Citro3D frame. mGBA's GBA frameskip already avoids scanline rendering, so aligning platform presentation skipping with frameskip removes both software-renderer and 3DS presentation work.

## Test procedure

1. Install/run the generated `mgba.3dsx` or `mgba.cia` on the New 3DS.
2. Enable mGBA's FPS counter.
3. Load the same Pokémon Ruby/Sapphire save and stand in the same scene used for the current ~120 FPS ceiling test.
4. Record normal-speed FPS.
5. Hold/toggle fast-forward for at least 60 seconds and record the stable FPS range.
6. Repeat once in a battle and once in the overworld.
7. Check that audio returns and display cadence returns to normal immediately after fast-forward is released.

The useful comparison is emulated FPS and real hunt/reset throughput before vs after. A lower visual update rate during turbo is intentional.

## Integration status

The existing Gen 3 bot source has hardware-proven state-machine and `FAST=0` safety gates. This proof build deliberately does not alter those files. Once the N3DS speed change is hardware-verified, port `patches/0001-n3ds-bot-turbo.patch` into the custom mGBA bridge source so its existing `FAST=1` command receives the same optimized fast-forward path.
