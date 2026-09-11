# Pokebot-Luma framebuffer extension (`v0p5-fb1`)

This extension is additive to the proven Pokebot-Luma v0p5 RAM and acknowledged-controller services on UDP `4952`.

## Compatibility invariant

Commands `1` through `10` are unchanged:

- `1-4`: read-only RAM bridge
- `5-10`: acknowledged input controller

The existing RAM `READ` maximum remains `0x200` bytes and there is still no game-process RAM write command.

## New read-only framebuffer commands

### `11 FRAMEBUFFER_INFO`

`argument` is the screen selector:

- `0`: top-left / normal top screen
- `1`: top-right eye
- `2`: bottom screen

Response payload is six little-endian `u32` values:

1. selector
2. width
3. height (`240`)
4. bytes per pixel (`3`)
5. maximum pixels per `FRAMEBUFFER_READ` (`400`)
6. flags

Returned pixels are BGR8, matching Luma3DS's built-in screenshot conversion.

### `12 FRAMEBUFFER_READ`

The request encodes a bounded horizontal framebuffer span:

- `argument bits 0..7`: screen selector
- `argument bits 8..15`: Y line (`0..239`)
- `argument bits 16..31`: X start
- `aux`: pixel count (`1..400`)

The response is `pixel_count * 3` bytes of BGR8 data. The maximum payload is therefore 1200 bytes, intentionally below normal Ethernet MTU after the Pokebot response header is added.

The implementation reuses Luma's framebuffer-format conversion and current GPU framebuffer selection. It does not change framebuffer registers, allocate a persistent screenshot buffer, or write game RAM.

## PC test

With ORAS running and `Pokebot3DS Bridge... -> Enable Both` enabled:

```text
python test_pokebot_luma_framebuffer.py <3DS-IP> top top.bmp
python test_pokebot_luma_framebuffer.py <3DS-IP> bottom bottom.bmp
```

The client reconstructs the image line-by-line and writes a standard 24-bit BMP.

Because reads are live rather than a firmware-side frozen snapshot, animated scenes can theoretically show line-to-line tearing. For the intended shiny-HOLD use case the bot stops gameplay before capture, so the display should be effectively stationary.
