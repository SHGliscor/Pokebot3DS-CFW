# Pokebot-Luma v0p1

Experimental Luma3DS-derived foundation build for Pokebot3DS.

v0p1 adds a Rosalina submenu named `Pokebot3DS Bridge` with two runtime flags:

- RAM Bridge: OFF by default
- Input Controller: OFF by default

The flags are intentionally not persisted. A full reboot always returns both to OFF.

v0p1 is menu/state only. It does not start networking, read game memory, or inject controller input. Those backends will be added only after the modified Luma build boots and behaves like stock Luma on real hardware.

Upstream base: LumaTeam/Luma3DS commit `d30ac8d1c665ed2a50dc30b291f7eb6b33e9890a`.

This derivative remains subject to the upstream Luma3DS GPLv3 license and notices.
