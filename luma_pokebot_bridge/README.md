# Pokebot-Luma v0p3

Experimental Luma3DS-derived build for Pokebot3DS.

## Hardware-proven foundation

The v0p2 menu-only foundation has now passed real-hardware testing:

- modified Luma boots normally
- HOME Menu controls and touch work
- ORAS runs normally
- `Pokebot3DS Bridge...` opens in Rosalina
- Enable Both / Disable Both / Status work without the v0p1 Rosalina crash
- a reboot returns both Pokebot states to OFF

## v0p3: additive controller proof

v0p3 connects the Pokebot `Input Controller` switch to Luma3DS's existing InputRedirection backend on UDP port 4950, but changes the HID button merge rule.

Stock InputRedirection selects remote HID whenever the remote mask is non-neutral. Pokebot instead merges the active-low masks:

`effective_raw_hid = physical_raw_hid & remote_raw_hid`

Because a cleared HID bit means pressed, this gives the intended behavior:

`effective buttons = physical OR injected`

Examples:

- physical neutral `FFF` + remote A `FFE` -> `FFE` (A)
- physical B `FFD` + remote neutral `FFF` -> `FFD` (B)
- physical B `FFD` + remote A `FFE` -> `FFC` (A+B)

Touch and circle-pad handling remain upstream Luma behavior for this proof: when the remote packet is neutral, the physical source passes through.

The `RAM Bridge` switch remains state-only in v0p3. No Pokebot RAM networking is added yet.

## v0p3 hardware gate

1. Boot normally and launch ORAS.
2. Open Rosalina -> `Pokebot3DS Bridge...`.
3. Select `Toggle Input Controller` and confirm Status shows `Input Controller: ON`, result `0x00000000`, UDP port 4950.
4. Return to ORAS and confirm physical A/B/D-pad/touch still work.
5. On the PC run:
   `python test_pokebot_luma_input.py <3DS-IP> A`
6. Confirm ORAS reacts to the synthetic A pulse.
7. Repeat with START if useful:
   `python test_pokebot_luma_input.py <3DS-IP> START`
8. Immediately confirm physical controls still work.
9. For the strongest coexistence proof, use `--hold 1.5` and press a different physical button during the synthetic hold.
10. Disable Input Controller and confirm physical controls continue normally.

Do not proceed to the RAM bridge until this additive controller path is hardware-proven.

Upstream base: LumaTeam/Luma3DS commit `d30ac8d1c665ed2a50dc30b291f7eb6b33e9890a`.

This derivative remains subject to the upstream Luma3DS GPLv3 license and notices.
