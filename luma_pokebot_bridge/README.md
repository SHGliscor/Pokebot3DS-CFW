# Pokebot-Luma v0p4

Experimental Luma3DS-derived build for Pokebot3DS.

## Hardware-proven foundation

The v0p2 menu-only foundation passed real-hardware testing:

- modified Luma boots normally
- HOME Menu controls and touch work
- ORAS runs normally
- `Pokebot3DS Bridge...` opens in Rosalina
- Enable Both / Disable Both / Status work without the v0p1 Rosalina crash
- a reboot returns both Pokebot states to OFF

## Hardware-proven controller: v0p3

v0p3 connected the Pokebot `Input Controller` switch to Luma3DS's existing InputRedirection backend on UDP port 4950 and changed only the HID button merge rule.

Pokebot merges the active-low masks:

`effective_raw_hid = physical_raw_hid & remote_raw_hid`

Because a cleared HID bit means pressed, this gives:

`effective buttons = physical OR injected`

Real-hardware results:

- synthetic A works in ORAS
- synthetic START works in ORAS
- physical buttons remain usable
- touchscreen remains usable
- a different physical button works during a long synthetic hold
- physical controls remain normal after disabling the controller

The v0p3 controller path is therefore preserved unchanged in v0p4.

## v0p4: read-only RAM bridge

v0p4 turns the `RAM Bridge` switch into a real UDP server on port 4952. The framing is intentionally compatible with the earlier Pokebot bridge work:

- `PING`
- `GAME_INFO`
- `QUERY`
- bounded `READ`

Maximum READ size is `0x200` bytes per request.

The bridge supports ORAS title IDs:

- Omega Ruby: `000400000011C400` / `sango-1`
- Alpha Sapphire: `000400000011C500` / `sango-2`

### Read-only safety rule

v0p4 contains no game-memory write command. RAM access is limited to memory-map queries and bounded reads. The read path opens the current ORAS process, verifies the requested region/permissions, temporarily maps only the page(s) required for that request, copies the requested bytes, and immediately unmaps them.

This is deliberately not continuous polling.

## v0p4 hardware gate

1. Boot normally and launch ORAS.
2. Open Rosalina -> `Pokebot3DS Bridge...`.
3. Select `Enable Both`.
4. Open Status and confirm both are ON, both results are `0x00000000`, RAM UDP is 4952 and Input UDP is 4950.
5. Return to ORAS and confirm physical controls/touch still work.
6. From the extracted `PC_TEST` directory run:

   `python test_pokebot_luma_ram.py <3DS-IP>`

   The default smoke test reads 0x20 bytes from the game code region at `0x00100000`.
7. Expected: PING PASS, GAME_INFO PASS, QUERY PASS and READ PASS.
8. Check the Rosalina Status screen again. Packet count should have increased and Reads should be at least 1.
9. Re-test synthetic A or START with the already-proven input tester and confirm physical controls still work afterward.

Only after the generic bounded RAM read passes should the bot use the bridge for PK6 encounter reads.

Upstream base: LumaTeam/Luma3DS commit `d30ac8d1c665ed2a50dc30b291f7eb6b33e9890a`.

This derivative remains subject to the upstream Luma3DS GPLv3 license and notices.
