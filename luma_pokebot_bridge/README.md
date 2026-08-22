# Pokebot-Luma v0p4

Experimental Luma3DS-derived firmware for Pokebot3DS.

## Hardware-proven foundation

Pokebot-Luma has now passed the low-level real-hardware gates required for the ORAS bot:

- modified Luma boots normally
- HOME Menu and ORAS controls remain usable
- `Pokebot3DS Bridge...` opens from Rosalina
- Enable Both / Disable Both / Status are stable
- reboot returns both Pokebot services OFF
- physical A/B/D-pad/touch remain usable with the controller service enabled
- synthetic A reaches ORAS over UDP 4950
- synthetic START reaches ORAS over UDP 4950
- a different physical button remains usable during a long synthetic hold
- RAM PING / GAME_INFO / QUERY / READ pass over UDP 4952
- Alpha Sapphire identifies as `000400000011C500 / sango-2`
- a real wild PK6 at `0x081FFA6C` was read, decrypted and checksum-validated

## Additive controller

The Pokebot `Input Controller` switch uses Luma3DS InputRedirection on UDP port 4950 with an additive active-low HID merge:

`effective_raw_hid = physical_raw_hid & remote_raw_hid`

Because a cleared HID bit means pressed, this implements:

`effective buttons = physical OR injected`

This prevents a remote button press from intentionally taking ownership of the complete physical button state.

Touch and circle-pad handling remain based on Luma's InputRedirection path. Physical touch has been verified to remain usable; integrated hunt actions using remote touch still require their targeted regression pass after the transport migration.

## Read-only RAM bridge

The `RAM Bridge` switch starts a separate UDP service on port 4952.

Commands:

- `PING`
- `GAME_INFO`
- `QUERY`
- `READ`

Safety properties:

- Omega Ruby / Alpha Sapphire only
- maximum READ size `0x200` bytes
- validates region and read permissions
- maps only the required page(s), copies the requested bytes, then unmaps them
- no game-memory write command

A real Alpha Sapphire `wild/opponent0` PK6 read has passed end-to-end through this service, including PK6 decryption and checksum verification.

## Rosalina menu

Open Rosalina with `L + D-Pad Down + Select`, then choose:

`Pokebot3DS Bridge...`

The submenu contains:

- `Toggle RAM Bridge`
- `Toggle Input Controller`
- `Enable Both`
- `Disable Both`
- `Status`

The v0p4 Status screen shows RAM/input ON/OFF state, result codes, RAM packet/read counters, RAM UDP 4952 and Input UDP 4950.

For normal Pokebot use, start ORAS and Wi-Fi first, then choose **Enable Both**.

## Source and licensing

Upstream base: LumaTeam/Luma3DS commit `d30ac8d1c665ed2a50dc30b291f7eb6b33e9890a`.

This derivative remains subject to the upstream Luma3DS GPLv3 license and notices.