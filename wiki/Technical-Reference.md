# Technical Reference

This page collects stable low-level identifiers and protocol details used by current ORAS development.

## Supported ORAS profiles

```text
Omega Ruby 1.4
Title ID: 000400000011C400
Process:  sango-1

Alpha Sapphire 1.4
Title ID: 000400000011C500
Process:  sango-2
```

## Current Pokebot service

```text
UDP port: 4952
```

Read-only RAM commands:

```text
PING
GAME_INFO
QUERY
READ
```

Maximum individual RAM READ:

```text
512 bytes / 0x200
```

Acknowledged controller protocol v1:

```text
5   INPUT_PING
6   INPUT_PULSE
7   INPUT_STATUS
8   RELEASE_ALL
9   INPUT_TOUCH_PULSE
10  INPUT_HID_LATCH
```

Hardware-tested controller values:

```text
caps:        0x000000CF
runtime:     0x00000001
neutral HID: 0xFFF
max hold:    5000 ms
max settle:  5000 ms
```

## HID

3DS HID masks are active-low. The reset chord used by current starter automation is:

```text
L + R + START + SELECT
raw HID used by retained latch: 0xCF3
```

The retained latch is followed by explicit `RELEASE_ALL` and game/process-transition verification.

## Useful ORAS RAM anchors

Known development anchors include:

```text
0x081FB478  battle state
0x081FB58C  player battle-party pointer table
0x081FB92C  opponent battle-party pointer table
0x081FFA6C  wild/opponent0 PK6 runtime area
```

For the known battle-state path:

```text
active battle state: 0x00040001
```

These addresses are observation points used by the supported ORAS 1.4 profiles. The bridge remains read-only.

## Party data

The project can read valid party PK6 identity/details, but ORAS also maintains multiple stale/cached party representations. The exact live overworld party-order structure remains under investigation and is kept separate from hunt authority.

## `code.ips`

```text
000400000011C400 → Omega Ruby 1.4 patch
000400000011C500 → Alpha Sapphire 1.4 patch
```

The patch bypasses the ORAS communication-error interruption that can occur with remote/InputRedirection-style input while PSS communication is active, including the early Route 101 period before PSS can be disabled normally.

## Safety invariants

- game RAM is read-only through the Pokebot bridge
- PK6 must validate before shiny authority is accepted
- unexpected state fails closed to HOLD
- controller acknowledgement alone is not proof that the game reached the expected state
- movement must remain inside the method's proven map/grid/terrain authority
- display features such as Party cards or Discord are not hunt authority