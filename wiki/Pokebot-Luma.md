# Pokebot-Luma

Pokebot-Luma is the Luma3DS-derived firmware layer used by Pokebot3DS-CFW to provide controlled access to ORAS state and controller input on real hardware.

## Read-only RAM bridge

The bridge exposes bounded read-only access to supported game processes. The important RAM commands are:

```text
PING
GAME_INFO
QUERY
READ
```

Individual READ requests are bounded to **512 bytes (`0x200`)**. Larger desktop-side structures must be assembled from multiple bounded reads.

There is deliberately **no game-RAM write command**. The bridge cannot make a Pokémon shiny, edit PID/IVs, inject Pokémon or alter encounter generation.

## Acknowledged controller

Current development builds add an acknowledged input protocol on UDP `4952`:

```text
5   INPUT_PING
6   INPUT_PULSE
7   INPUT_STATUS
8   RELEASE_ALL
9   INPUT_TOUCH_PULSE
10  INPUT_HID_LATCH
```

The tested protocol reports:

```text
protocol:      1
capabilities:  0x000000CF
runtime:       0x00000001
neutral HID:   0xFFF
max hold:      5000 ms
max settle:    5000 ms
```

## Retained HID latch

The retained latch is used when ORAS must observe an input continuously rather than receiving a short fire-and-forget pulse.

The most important example is the soft-reset chord:

```text
L + R + START + SELECT
```

The current reset path is:

```text
pre-neutral
→ INPUT_HID_LATCH(reset chord)
→ retain chord
→ RELEASE_ALL
→ verify game/PID transition
```

This replaced the earlier short-pulse reset method after hardware testing showed that a firmware acknowledgement did not always mean the game itself had observed the chord long enough to reset.

## Native touch pulse

`INPUT_TOUCH_PULSE` provides an acknowledged touchscreen action for hunt paths that need bottom-screen input, including the current automatic Run flow.

## RELEASE_ALL

`RELEASE_ALL` is the explicit emergency neutralisation path. It is used to make sure injected input does not remain latched after a state transition, stop or safety failure.

## Separation of authority

The architecture deliberately separates two questions:

```text
RAM:        What state is the game actually in?
Controller: What normal input should be sent next?
```

A controller acknowledgement is not shiny authority. A valid PK6 read is not permission to send arbitrary inputs. The desktop state machine combines both under fail-closed safety gates.

## Legacy v0p4 transport

Older documentation describes a split design with RAM on UDP `4952` and Luma InputRedirection on UDP `4950`. That was a real stage of development and is retained in project history. Current acknowledged-controller builds use the Pokebot `4952` service for both read-only RAM requests and acknowledged controller commands while keeping those responsibilities logically separate.