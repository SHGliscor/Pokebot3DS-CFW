# Pokebot3DS Stock-Luma 3GX Bridge v0p1

Experimental first port of the Pokebot3DS-CFW bridge from the Nexus3DS-derived `boot.firm` to a normal 3GX game plugin.

## v0p1 proof goals

- Keep official Luma3DS installed.
- Load inside Omega Ruby / Alpha Sapphire as a title plugin.
- Keep normal physical 3DS buttons/touch usable while the network bridge is active.
- Preserve UDP `4952` compatibility with the existing PC bot.
- Provide bounded read-only RAM access.
- Provide acknowledged button, touch and HID-latch injection without taking ownership of the system HID service.

Implemented commands: `PING`, `GAME_INFO`, `QUERY`, bounded `READ`, `INPUT_PING`, acknowledged HID pulse/status/release, touchscreen pulse, and HID latch. Framebuffer commands are deliberately deferred until RAM/input are hardware-proven.

## First hardware test

1. Keep official Luma3DS installed and enable its Plugin Loader.
2. Place the built `Pokebot3DSBridge.3gx` at either:
   - Omega Ruby: `sd:/luma/plugins/000400000011C400/Pokebot3DSBridge.3gx`
   - Alpha Sapphire: `sd:/luma/plugins/000400000011C500/Pokebot3DSBridge.3gx`
3. Have Wi-Fi/network already active before launching ORAS.
4. Launch the game and verify normal physical A/B/D-pad/touch controls still work.
5. From the PC, test `PING`, `GAME_INFO`, and `INPUT_PING`.
6. On a harmless screen only, send one acknowledged `A` pulse.
7. Verify physical controls still work immediately afterward.

Do not use this as the main hunting bridge until the above is proven. The current Nexus bridge remains the known-good reference implementation.
