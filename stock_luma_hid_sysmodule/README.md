# Pokebot3DS Stock-Luma HID Sysmodule v0p1

Experimental **diagnostic-only** background sysmodule for official Luma3DS.

This is the fallback path after the 3GX bridge proved stable UDP/RAM communication and physical-control passthrough, but synthetic A/START input was not consumed by ORAS.

## v0p1 scope

v0p1 intentionally does **not inject buttons or touch**.

It only proves that an external Luma sysmodule can:

- boot alongside stock Luma without replacing `boot.firm`;
- obtain the real `hid:USER` shared-memory handle without calling `hidInit()` or `irrstInit()`;
- map HID shared memory **read-only**;
- observe physical A/B/START/D-pad/X/Y/L/R state;
- answer a small UDP diagnostic protocol on port **4953**;
- leave normal physical game controls untouched.

There are no game RAM writes and no HID shared-memory writes in this build.

## Title ID / install path

CXI title ID:

`0004013000B0B702`

Install as:

`sd:/luma/sysmodules/0004013000B0B702.cxi`

Then hold **SELECT** while booting Luma and enable:

`Enable loading external FIRMs and modules`

Save the configuration and reboot.

A malformed sysmodule can interfere with boot. Keep SD-card access available so the CXI can be deleted if a test build causes a problem.

## First hardware test

For the cleanest proof, temporarily remove/disable the Pokebot 3GX plugin for this first sysmodule test.

After the 3DS boots and Wi-Fi is connected, run:

```powershell
py test_hid_sysmodule.py YOUR_3DS_IP
```

The probe uses UDP **4953** and monitors physical input for 15 seconds. During that window:

1. press/release physical **A**;
2. press/release physical **START**.

Expected output contains transitions equivalent to:

```text
PING: PASS PokebotHID-v0p1
HID=READY
UDP=READY
keys=0x001 A            ...
keys=0x000 NONE         ...
keys=0x008 START        ...
keys=0x000 NONE         ...
```

The `changes=` counter should increase on each physical press/release.

## Acceptance gate

Do not add synthetic input until all of these pass:

1. stock Luma boots normally with the CXI present;
2. HOME Menu controls remain normal;
3. ORAS controls remain normal;
4. touchscreen remains normal;
5. PC probe returns `PING: PASS`;
6. physical A is observed as `0x001`;
7. physical START is observed as `0x008`.

Only after that proof should v0p2 investigate additive input at the HID-process layer.

## Architecture target

The intended final split is:

- 3GX / game-side bridge: bounded read-only game RAM and optional OSD;
- HID sysmodule: physical + injected controller/touch path;
- separate UDP ports during development (`4952` game bridge, `4953` HID sysmodule).

This keeps official Luma's `boot.firm` untouched unless a standalone sysmodule ultimately proves insufficient.
