# Pokebot-Luma v0p2

Experimental Luma3DS-derived foundation build for Pokebot3DS.

v0p2 keeps the Rosalina submenu named `Pokebot3DS Bridge` with two runtime flags:

- RAM Bridge: OFF by default
- Input Controller: OFF by default

The flags are intentionally not persisted. A full reboot always returns both to OFF.

## v0p2 crash-safety change

The v0p1 hardware test exposed a Rosalina data-abort when enabling Pokebot state from the submenu. v0p1 dynamically rewrote the menu-item labels after each toggle. v0p2 removes that path completely:

- menu titles are constant strings
- toggle methods only flip/set the two booleans
- no Pokebot `snprintf` label refresh occurs in the toggle path
- current ON/OFF state is shown only on the dedicated `Status` screen

v0p2 is still menu/state only. It does not start networking, read game memory, or inject controller input. Those backends remain blocked until this menu-only foundation is stable on real hardware.

Upstream base: LumaTeam/Luma3DS commit `d30ac8d1c665ed2a50dc30b291f7eb6b33e9890a`.

This derivative remains subject to the upstream Luma3DS GPLv3 license and notices.
