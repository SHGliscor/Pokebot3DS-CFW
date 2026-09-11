# Pokebot-Luma v0p5

Experimental Luma3DS-derived firmware for Pokebot3DS.

## Why v0p5 exists

Pokebot-Luma v0p4 proved the important low-level pieces on real ORAS hardware: additive synthetic input reached the game, physical controls remained usable, and the read-only RAM bridge returned valid game RAM and a checksum-valid PK6.

The first desktop integration then exposed a transport regression: using raw Luma InputRedirection UDP `4950` with PC-side sleep timing was not equivalent to the older acknowledged Pokebot controller protocol. Previously calibrated Wild movement could overshoot and Sweet Scent choreography could fail even though the RAM side remained correct.

v0p5 fixes the architecture instead of retuning every hunt. It keeps the proven v0p4 RAM bridge and additive HID hook, but restores an acknowledged, sequence-numbered controller service with firmware-owned timing on the Pokebot UDP `4952` bridge.

## Hardware-proven foundation retained from v0p4

- modified Luma boots normally
- HOME Menu and ORAS controls remain usable
- `Pokebot3DS Bridge...` opens from Rosalina
- physical A/B/D-pad/touch remain usable with the additive HID patch
- synthetic A and START have reached ORAS through the Luma HID path
- a different physical button remains usable during a synthetic hold
- RAM `PING / GAME_INFO / QUERY / READ` pass over UDP `4952`
- Alpha Sapphire identifies as `000400000011C500 / sango-2`
- a real wild PK6 at `0x081FFA6C` was read, decrypted and checksum-validated
- no game-memory write command exists

The **new v0p5 acknowledged-controller layer is not promoted to production until its standalone hardware gate passes**.

## Unified Pokebot protocol — UDP 4952

### Read-only RAM

1. `PING`
2. `GAME_INFO`
3. `QUERY`
4. `READ`

### Acknowledged controller

5. `INPUT_PING`
6. `INPUT_PULSE`
7. `INPUT_STATUS`
8. `RELEASE_ALL`
9. `TOUCH_PULSE`
10. `HID_LATCH`

The request/response framing remains protocol version 1. Controller capability flags are `0xCF`, covering pulse, status, sequence deduplication, release, touch and latch.

## Controller model

The v0p5 controller writes only Luma's **remote/injected HID and touch state**. It does not write Pokémon or game-process RAM.

Button input retains the proven additive active-low merge:

`effective_raw_hid = physical_raw_hid & injected_raw_hid`

Because a cleared HID bit means pressed, that is equivalent to:

`effective buttons = physical OR injected`

A synthetic A press therefore does not intentionally suppress a simultaneously pressed real B/D-pad button.

### Firmware-owned timing

For `INPUT_PULSE` and `TOUCH_PULSE`, the PC sends a hold time and optional settle time. The 3DS owns the timing state machine:

`HELD -> injected neutral -> SETTLE -> COMPLETED`

The PC observes progress with `INPUT_STATUS`; it does not declare success merely because a local sleep elapsed.

### Sequence deduplication

The request ID is also the gameplay sequence ID. Re-receiving the same sequence/command reports the existing state instead of producing a second press. A completed duplicate reports `ALREADY_COMPLETED`.

### RELEASE_ALL

`RELEASE_ALL` immediately neutralises only the injected state:

- HID -> `0xFFF`
- touch -> neutral
- circle pad remains neutral

Physical controls are not intentionally released or blocked.

### HID_LATCH

`HID_LATCH` keeps the requested injected HID state active until `RELEASE_ALL`. This supports hunt paths that need a continuous button hold without depending on PC-side packet repetition.

## Native Rosalina InputRedirection on UDP 4950

v0p5 does **not** use the standard Rosalina UDP `4950` receiver as the Pokebot transport. The Pokebot controller uses the same proven Luma HID/touch injection storage and patches but owns them through the acknowledged `4952` bridge.

Do not enable `Miscellaneous options -> InputRedirection` while testing v0p5. `INPUT_PING` reports the native InputRedirection state and rejects the conflicting legacy-active condition.

## Read-only RAM bridge

The existing RAM commands remain deliberately bounded:

- Omega Ruby / Alpha Sapphire only
- maximum READ size `0x200` bytes
- requested region and read permissions are checked
- only required pages are mapped, copied and immediately unmapped
- no game-memory write command

The v0p5 controller work is intentionally separate from this proven RAM authority.

## Rosalina menu

Open Rosalina with `L + D-Pad Down + Select`, then choose:

`Pokebot3DS Bridge...`

The submenu contains:

- `Toggle RAM Bridge`
- `Toggle Input Controller`
- `Enable Both`
- `Disable Both`
- `Status`

For v0p5, Status shows the shared Pokebot UDP `4952` services and also displays whether native Rosalina InputRedirection `4950` is active.

For testing, start ORAS and Wi-Fi first, leave standard InputRedirection disabled, then choose **Enable Both**.

## v0p5 hardware proof order

Do not reconnect the full desktop hunt backend until these pass standalone:

1. `INPUT_PING` reports protocol 1 and capabilities `0xCF`.
2. Firmware-timed A pulse reaches ORAS and returns to neutral.
3. Firmware-timed START pulse reaches ORAS and returns to neutral.
4. A controlled D-pad pulse has sane timing and returns to neutral.
5. Physical buttons and touchscreen remain usable alongside synthetic HID.
6. `HID_LATCH` stays active until `RELEASE_ALL`.
7. `TOUCH_PULSE` works in the intended ORAS battle menu.
8. The v0p4 RAM PING/GAME_INFO/QUERY/READ proof still passes unchanged.

After that gate, the desktop bot can return to its original acknowledged controller API and proven hunt timings rather than the temporary raw-4950 compatibility wrapper.

## Source and licensing

Upstream base: LumaTeam/Luma3DS commit `d30ac8d1c665ed2a50dc30b291f7eb6b33e9890a`.

This derivative remains subject to the upstream Luma3DS GPLv3 license and notices.
